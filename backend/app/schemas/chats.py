from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator

from app.services.section_policy import DEFAULT_SECTION_CODE, normalize_section_code


class ChatCreate(BaseModel):
    title: str
    section: str = DEFAULT_SECTION_CODE
    status: str = "draft"
    approval_status: str = "draft"
    active_verdict_message_id: int | None = None

    @field_validator("section", mode="before")
    @classmethod
    def normalize_section(cls, value: object) -> str:
        return normalize_section_code(value if isinstance(value, str) else None)


class ChatRead(ChatCreate):
    id: int
    owner_user_id: int | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
