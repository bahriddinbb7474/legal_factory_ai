from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

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
        lines.append(f"{ts}{author}{model_suffix}: {message.content}")
    return "\n".join(lines)


def build_chat_context(
    messages: list[Message],
    chat: Chat | None = None,
    document_context: str = "",
    legal_context: str = "",
    limit: int = HISTORY_LIMIT,
) -> str:
    parts: list[str] = []

    if chat:
        meta_lines: list[str] = []
        if getattr(chat, "section", None):
            meta_lines.append(f"- Раздел: {chat.section}")
        meta_lines.append(f"- Название: {chat.title}")
        parts.append("Контекст чата:\n" + "\n".join(meta_lines))

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
