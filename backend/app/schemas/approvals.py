from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ApprovalCreate(BaseModel):
    chat_id: int
    requested_by_user_id: int
    approved_by_user_id: int | None = None
    status: str = "draft"
    comment: str | None = None


class ApprovalRead(ApprovalCreate):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
