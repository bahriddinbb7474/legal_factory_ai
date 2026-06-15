from app.db.base import Message


AUTHOR_LABELS = {
    "user": "Пользователь",
    "agent1": "Юрист 1",
    "agent2": "Юрист 2",
    "agent3": "Юрист 3",
    "system": "Система",
}


def build_chat_context(messages: list[Message]) -> str:
    lines: list[str] = []
    for message in messages:
        author = AUTHOR_LABELS.get(message.author_type, message.author_type)
        model_suffix = f" (модель: {message.model_id})" if message.model_id else ""
        lines.append(f"{author}{model_suffix}: {message.content}")
    return "\n".join(lines)


def author_type_for_agent(agent_code: str) -> str:
    return {
        "lawyer_1": "agent1",
        "lawyer_2": "agent2",
        "lawyer_3": "agent3",
    }[agent_code]
