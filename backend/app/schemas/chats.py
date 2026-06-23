from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ChatCreate(BaseModel):
    title: str
    section: str | None = None
    status: str = "draft"
    approval_status: str = "draft"
    active_verdict_message_id: int | None = None


class ChatRead(ChatCreate):
    id: int
    owner_user_id: int | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
