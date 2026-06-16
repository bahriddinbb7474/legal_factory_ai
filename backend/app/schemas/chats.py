from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ChatCreate(BaseModel):
    title: str
    owner_user_id: int | None = None
    status: str = "draft"
    approval_status: str = "draft"


class ChatRead(ChatCreate):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
