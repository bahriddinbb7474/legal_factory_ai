from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, model_validator

from app.schemas.legal_response import SourceCheckStatus


class MessageCreate(BaseModel):
    author_type: str | None = None
    role: str | None = None
    content: str
    agent_id: int | None = None
    model_id: str | None = None
    provider_code: str | None = None
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: Decimal = Decimal("0")
    structured_payload: dict | None = None
    raw_response: str | None = None
    risk: str | None = None
    confidence: str | None = None
    approval_required: str | None = None
    source_check_status: SourceCheckStatus = "not_checked"
    red_flag_codes: list[str] = []
    is_verdict: bool = False

    @model_validator(mode="after")
    def normalize_author_type(self) -> "MessageCreate":
        if self.author_type is None and self.role is not None:
            self.author_type = "agent1" if self.role == "assistant" else self.role
        if self.role is None and self.author_type is not None:
            self.role = "assistant" if self.author_type.startswith("agent") else self.author_type
        if self.author_type is None or self.role is None:
            raise ValueError("author_type is required")
        return self


class MessageRead(MessageCreate):
    id: int
    chat_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
