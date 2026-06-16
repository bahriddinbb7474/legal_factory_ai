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
    try:
        payload = validate_legal_response(second.content, agent.code)
    except StructuredResponseError as exc:
        await write_audit_log(
            db,
            action="structured_response.validation_failed",
            entity_type="agent",
            entity_id=agent.id,
            user_id=user_id,
            details={"agent_code": agent.code, "after_repair": True},
        )
        raise
    return StructuredResponseResult(
        payload=payload,
        raw_response=second.content,
        input_tokens=first.input_tokens + second.input_tokens,
        output_tokens=first.output_tokens + second.output_tokens,
        repair_attempted=True,
    )


def _extract_json_object(content: str) -> str:
    stripped = content.strip()
    if stripped.startswith("{") and stripped.endswith("}"):
        return stripped
    match = re.search(r"\{.*\}", stripped, flags=re.DOTALL)
    if not match:
        raise json.JSONDecodeError("No JSON object found", content, 0)
    return match.group(0)


async def _invoke_gateway(gateway: OpenRouterGateway, agent: Agent, context: str) -> LLMResponse:
    try:
        return await gateway.invoke(agent, context, response_format={"type": "json_object"})
    except TypeError:
        return await gateway.invoke(agent, context)
