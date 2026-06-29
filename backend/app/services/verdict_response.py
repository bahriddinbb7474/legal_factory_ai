import json
import re
from dataclasses import dataclass

from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import Agent
from app.schemas.verdict import VERDICT_RESPONSE_INSTRUCTION, VerdictPayload
from app.services.audit import write_audit_log
from app.services.llm_gateway import LLMResponse, OpenRouterGateway


class VerdictResponseError(ValueError):
    pass


@dataclass
class VerdictResponseResult:
    payload: VerdictPayload
    raw_response: str
    input_tokens: int
    output_tokens: int
    repair_attempted: bool = False


def validate_verdict_response(content: str, agent_code: str) -> VerdictPayload:
    try:
        data = json.loads(_extract_json_object(content))
        payload = VerdictPayload.model_validate(data)
    except (json.JSONDecodeError, ValidationError) as exc:
        raise VerdictResponseError("LLM verdict response is invalid") from exc

    if agent_code not in {"lawyer_2", "lawyer_3"}:
        raise VerdictResponseError("Selected lawyer cannot issue verdict")
    payload.lawyer_id = agent_code  # type: ignore[assignment]
    return payload


async def invoke_verdict_with_repair(
    agent: Agent,
    chat_context: str,
    gateway: OpenRouterGateway,
    db: AsyncSession,
    user_id: int | None = None,
) -> VerdictResponseResult:
    first = await _invoke_with_verdict_prompt(agent, chat_context, gateway)
    try:
        payload = validate_verdict_response(first.content, agent.code)
        return VerdictResponseResult(payload, first.content, first.input_tokens, first.output_tokens)
    except VerdictResponseError:
        await write_audit_log(
            db,
            action="verdict_response.validation_failed",
            entity_type="agent",
            entity_id=agent.id,
            user_id=user_id,
            details={"agent_code": agent.code},
        )

    repair_context = (
        "Исправь ответ в валидный JSON verdict-схемы. Не добавляй backend gate fields и не меняй смысл:\n\n"
        f"{first.content}"
    )
    second = await _invoke_with_verdict_prompt(agent, repair_context, gateway)
    await write_audit_log(
        db,
        action="verdict_response.repair_attempted",
        entity_type="agent",
        entity_id=agent.id,
        user_id=user_id,
        details={"agent_code": agent.code},
    )
    try:
        payload = validate_verdict_response(second.content, agent.code)
    except VerdictResponseError:
        await write_audit_log(
            db,
            action="verdict_response.validation_failed",
            entity_type="agent",
            entity_id=agent.id,
            user_id=user_id,
            details={"agent_code": agent.code, "after_repair": True},
        )
        raise

    return VerdictResponseResult(
        payload=payload,
        raw_response=second.content,
        input_tokens=first.input_tokens + second.input_tokens,
        output_tokens=first.output_tokens + second.output_tokens,
        repair_attempted=True,
    )


async def _invoke_with_verdict_prompt(agent: Agent, context: str, gateway: OpenRouterGateway) -> LLMResponse:
    original_prompt = agent.system_prompt
    agent.system_prompt = f"{original_prompt.strip()}\n\n{VERDICT_RESPONSE_INSTRUCTION.strip()}"
    try:
        try:
            return await gateway.invoke(agent, context, response_format={"type": "json_object"})
        except TypeError:
            return await gateway.invoke(agent, context)
    finally:
        agent.system_prompt = original_prompt


def _extract_json_object(content: str) -> str:
    stripped = content.strip()
    if stripped.startswith("{") and stripped.endswith("}"):
        return stripped
    fence_match = re.search(r"```(?:json)?\s*(\{.*\})\s*```", stripped, re.DOTALL)
    if fence_match:
        return fence_match.group(1)
    match = re.search(r"\{.*\}", stripped, flags=re.DOTALL)
    if not match:
        raise json.JSONDecodeError("No JSON object found", content, 0)
    return match.group(0)
