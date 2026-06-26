import json
import re
from dataclasses import dataclass

from pydantic import ValidationError

from app.db.base import Agent
from app.schemas.legal_response import LegalAgreement, LegalStructuredResponse, STRUCTURED_LEGAL_RESPONSE_INSTRUCTION
from app.services.audit import write_audit_log
from app.services.llm_gateway import LLMResponse, OpenRouterGateway
from sqlalchemy.ext.asyncio import AsyncSession


class StructuredResponseError(ValueError):
    pass


@dataclass
class StructuredResponseResult:
    payload: LegalStructuredResponse
    raw_response: str
    input_tokens: int
    output_tokens: int
    repair_attempted: bool = False
    is_fallback: bool = False


def structured_system_prompt(base_prompt: str) -> str:
    return f"{base_prompt.strip()}\n\n{STRUCTURED_LEGAL_RESPONSE_INSTRUCTION.strip()}"


def validate_legal_response(content: str, agent_code: str) -> LegalStructuredResponse:
    try:
        data = json.loads(_extract_json_object(content))
    except json.JSONDecodeError as exc:
        raise StructuredResponseError("LLM response is not valid JSON") from exc

    try:
        payload = LegalStructuredResponse.model_validate(data)
    except ValidationError as exc:
        raise StructuredResponseError(str(exc)) from exc

    if agent_code in {"lawyer_2", "lawyer_3"} and payload.agreement is None:
        raise StructuredResponseError("agreement is required for Lawyer 2 and Lawyer 3")
    if agent_code == "lawyer_1" and payload.agreement is None:
        payload.agreement = None
    if agent_code in {"lawyer_2", "lawyer_3"} and payload.agreement is None:
        payload.agreement = LegalAgreement()
    return payload


async def invoke_structured_with_repair(
    agent: Agent,
    chat_context: str,
    gateway: OpenRouterGateway,
    db: AsyncSession,
    user_id: int | None = None,
) -> StructuredResponseResult:
    original_prompt = agent.system_prompt
    agent.system_prompt = structured_system_prompt(original_prompt)
    try:
        first = await _invoke_gateway(gateway, agent, chat_context)
    finally:
        agent.system_prompt = original_prompt

    try:
        payload = validate_legal_response(first.content, agent.code)
        await write_audit_log(
            db,
            action="structured_response.received",
            entity_type="agent",
            entity_id=agent.id,
            user_id=user_id,
            details={"agent_code": agent.code, "repair_attempted": False},
        )
        return StructuredResponseResult(payload, first.content, first.input_tokens, first.output_tokens)
    except StructuredResponseError:
        await write_audit_log(
            db,
            action="structured_response.validation_failed",
            entity_type="agent",
            entity_id=agent.id,
            user_id=user_id,
            details={"agent_code": agent.code},
        )

    repair_context = (
        "Исправь следующий ответ в строго валидный JSON по схеме Legal Factory AI. "
        "Не добавляй Markdown и не меняй смысл. Ответ:\n\n"
        f"{first.content}"
    )
    agent.system_prompt = structured_system_prompt(original_prompt)
    try:
        second = await _invoke_gateway(gateway, agent, repair_context)
    finally:
        agent.system_prompt = original_prompt

    await write_audit_log(
        db,
        action="structured_response.repair_attempted",
        entity_type="agent",
        entity_id=agent.id,
        user_id=user_id,
        details={"agent_code": agent.code},
    )
    total_input = first.input_tokens + second.input_tokens
    total_output = first.output_tokens + second.output_tokens
    try:
        payload = validate_legal_response(second.content, agent.code)
    except StructuredResponseError:
        await write_audit_log(
            db,
            action="structured_response.validation_failed",
            entity_type="agent",
            entity_id=agent.id,
            user_id=user_id,
            details={"agent_code": agent.code, "after_repair": True},
        )
        raw_text = (first.content or second.content).strip()
        if not raw_text:
            raise
        await write_audit_log(
            db,
            action="structured_response.fallback_used",
            entity_type="agent",
            entity_id=agent.id,
            user_id=user_id,
            details={"agent_code": agent.code, "raw_length": len(raw_text)},
        )
        return _build_fallback_result(raw_text, total_input, total_output)
    return StructuredResponseResult(
        payload=payload,
        raw_response=second.content,
        input_tokens=total_input,
        output_tokens=total_output,
        repair_attempted=True,
    )


def _extract_clean_answer(raw_text: str) -> str:
    """Extract a human-readable answer from raw model output that may be JSON-like.

    Returns empty string when text looks like a JSON object but no clean answer can be found,
    so the caller can substitute a safe generic message instead of exposing raw JSON.
    """
    stripped = raw_text.strip()

    # 1. Valid JSON — extract visible_answer or summary directly
    try:
        json_obj = json.loads(stripped)
        if isinstance(json_obj, dict):
            visible = json_obj.get("visible_answer")
            if visible and isinstance(visible, str) and visible.strip():
                return visible.strip()
            summary = json_obj.get("summary")
            if summary and isinstance(summary, str) and summary.strip():
                return summary.strip()
    except (json.JSONDecodeError, ValueError):
        pass

    # 2. JSON embedded in surrounding prose
    try:
        embedded = _extract_json_object(stripped)
        json_obj = json.loads(embedded)
        if isinstance(json_obj, dict):
            visible = json_obj.get("visible_answer")
            if visible and isinstance(visible, str) and visible.strip():
                return visible.strip()
            summary = json_obj.get("summary")
            if summary and isinstance(summary, str) and summary.strip():
                return summary.strip()
    except (json.JSONDecodeError, ValueError):
        pass

    # 3. "visible_answer": "..." double-quoted value
    m = re.search(r'"visible_answer"\s*:\s*"((?:[^"\\]|\\.)*)"', stripped, re.DOTALL)
    if m:
        try:
            value: str = json.loads(f'"{m.group(1)}"')
        except (json.JSONDecodeError, ValueError):
            value = m.group(1)
        if value.strip():
            return value.strip()

    # 4. 'visible_answer': '...' single-quoted value
    m = re.search(r"'visible_answer'\s*:\s*'((?:[^'\\]|\\.)*)'", stripped, re.DOTALL)
    if m and m.group(1).strip():
        return m.group(1).strip()

    # 5. "summary": "..." double-quoted fallback
    m = re.search(r'"summary"\s*:\s*"((?:[^"\\]|\\.)*)"', stripped, re.DOTALL)
    if m:
        try:
            value = json.loads(f'"{m.group(1)}"')
        except (json.JSONDecodeError, ValueError):
            value = m.group(1)
        if value.strip():
            return value.strip()

    # 6. 'summary': '...' single-quoted fallback
    m = re.search(r"'summary'\s*:\s*'((?:[^'\\]|\\.)*)'", stripped, re.DOTALL)
    if m and m.group(1).strip():
        return m.group(1).strip()

    # 7. Looks like a JSON object — don't expose raw JSON to the user
    if stripped.startswith("{") and "}" in stripped:
        return ""

    # 8. Prose — return as-is
    return stripped


def _build_fallback_result(raw_text: str, input_tokens: int, output_tokens: int) -> StructuredResponseResult:
    clean_text = _extract_clean_answer(raw_text)
    visible: str | None = clean_text if clean_text else None
    summary = clean_text if clean_text else "Ответ получен, но структура повреждена. Повторите запрос."
    payload = LegalStructuredResponse(
        answer_mode="preliminary_opinion",
        visible_answer=visible,
        summary=summary,
        risk="yellow",
        confidence="low",
        meaning_for_factory="Требуется ручная проверка юриста",
        approval_required="external_lawyer",
    )
    return StructuredResponseResult(
        payload=payload,
        raw_response=raw_text,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        repair_attempted=True,
        is_fallback=True,
    )


def _extract_json_object(content: str) -> str:
    stripped = content.strip()
    # 1. Bare JSON object
    if stripped.startswith("{") and stripped.endswith("}"):
        return stripped
    # 2. JSON inside fenced code block (```json or ```)
    fence_match = re.search(r"```(?:json)?\s*(\{.*\})\s*```", stripped, re.DOTALL)
    if fence_match:
        return fence_match.group(1)
    # 3. JSON object embedded in surrounding text
    match = re.search(r"\{.*\}", stripped, flags=re.DOTALL)
    if not match:
        raise json.JSONDecodeError("No JSON object found", content, 0)
    return match.group(0)


async def _invoke_gateway(gateway: OpenRouterGateway, agent: Agent, context: str) -> LLMResponse:
    try:
        return await gateway.invoke(agent, context, response_format={"type": "json_object"})
    except TypeError:
        return await gateway.invoke(agent, context)
