from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from app.services.section_policy import build_section_policy_context

if TYPE_CHECKING:
    from app.db.base import Chat, Message


AUTHOR_LABELS = {
    "user": "Пользователь",
    "agent1": "Юрист 1",
    "agent2": "Юрист 2",
    "agent3": "Юрист 3",
    "system": "Система",
}

HISTORY_LIMIT = 30


def build_rich_lawyer_block(message) -> str:
    """Return a compact readable block from an agent message's structured_payload for cross-lawyer context."""
    payload = getattr(message, "structured_payload", None)
    if not payload or not isinstance(payload, dict):
        return message.content

    lines: list[str] = []

    if summary := payload.get("summary"):
        lines.append(summary)

    meta: list[str] = []
    if risk := payload.get("risk"):
        meta.append(f"риск={risk}")
    if conf := payload.get("confidence"):
        meta.append(f"уверенность={conf}")
    if meta:
        lines.append("[" + " | ".join(meta) + "]")

    findings = payload.get("findings", [])
    if findings:
        items = "; ".join(
            f"{f.get('title', '')}: {f.get('description', '')}"
            for f in findings
            if isinstance(f, dict) and f.get("title")
        )
        if items:
            lines.append(f"Выводы: {items}")

    if meaning := payload.get("meaning_for_factory"):
        lines.append(f"Для завода: {meaning}")

    actions = [a for a in payload.get("actions", []) if a and str(a).strip()]
    if actions:
        lines.append(f"Действия: {'; '.join(actions)}")

    sources = payload.get("sources", [])
    if sources:
        src_parts = [
            f"{s.get('title', '')} ({s.get('verification_status', 'pending')})"
            for s in sources
            if isinstance(s, dict) and s.get("title")
        ]
        if src_parts:
            lines.append(f"Источники: {'; '.join(src_parts)}")

    agreement = payload.get("agreement")
    if isinstance(agreement, dict):
        agreed = agreement.get("agreed_points", [])
        disagreed = agreement.get("disagreed_points", [])
        unresolved = agreement.get("unresolved_points", [])
        if agreed:
            lines.append(f"Согласен: {'; '.join(agreed)}")
        if disagreed:
            lines.append(f"Не согласен: {'; '.join(disagreed)}")
        if unresolved:
            lines.append(f"Нерешено: {'; '.join(unresolved)}")

    return "\n".join(lines) if lines else message.content


def build_chat_history_context(messages: list[Message], limit: int = HISTORY_LIMIT) -> str:
    """Format the last `limit` non-empty messages as sender-labelled, optionally timestamped lines."""
    relevant = [m for m in messages if m.content.strip()][-limit:]
    lines: list[str] = []
    for message in relevant:
        author = AUTHOR_LABELS.get(message.author_type, message.author_type)
        model_suffix = f" (модель: {message.model_id})" if message.model_id else ""
        ts = ""
        created_at = getattr(message, "created_at", None)
        if isinstance(created_at, datetime):
            ts = f"[{created_at.strftime('%Y-%m-%d %H:%M')}] "
        structured_payload = getattr(message, "structured_payload", None)
        if message.author_type.startswith("agent") and structured_payload:
            content = build_rich_lawyer_block(message)
        else:
            content = message.content
        lines.append(f"{ts}{author}{model_suffix}: {content}")
    return "\n".join(lines)


def build_chat_context(
    messages: list[Message],
    chat: Chat | None = None,
    document_context: str = "",
    legal_context: str = "",
    limit: int = HISTORY_LIMIT,
    agent_code: str | None = None,
) -> str:
    parts: list[str] = []

    if chat:
        meta_lines = [f"- Название: {chat.title}"]
        parts.append("Контекст чата:\n" + "\n".join(meta_lines))
        parts.append(build_section_policy_context(getattr(chat, "section", None), agent_code))

    history = build_chat_history_context(messages, limit=limit)
    if history:
        parts.append("История текущего чата:\n" + history)

    if document_context:
        parts.append("Документы, связанные с текущим чатом:\n" + document_context)

    if legal_context:
        parts.append("Курируемые подтвержденные правовые источники:\n" + legal_context)

    last_user = next(
        (m for m in reversed(messages) if m.author_type == "user" and m.content.strip()),
        None,
    )
    if last_user:
        parts.append(f"Текущий вопрос пользователя:\n{last_user.content}")

    parts.append(
        "Используй историю чата. Не повторяй уже данный ответ без необходимости. "
        "Если вопрос является продолжением, отвечай как продолжение."
    )

    return "\n\n".join(parts)


def author_type_for_agent(agent_code: str) -> str:
    return {
        "lawyer_1": "agent1",
        "lawyer_2": "agent2",
        "lawyer_3": "agent3",
    }[agent_code]
