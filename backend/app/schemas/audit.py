from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AuditLogCreate(BaseModel):
    user_id: int | None = None
    action: str
    entity_type: str
    entity_id: int | None = None
    details: dict | None = None


class AuditLogRead(AuditLogCreate):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
