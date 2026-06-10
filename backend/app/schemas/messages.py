from datetime import datetime

from pydantic import BaseModel, ConfigDict


class MessageCreate(BaseModel):
    role: str
    content: str
    agent_id: int | None = None


class MessageRead(MessageCreate):
    id: int
    chat_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
