from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class CostRecordCreate(BaseModel):
    chat_id: int
    agent_id: int | None = None
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: Decimal = Decimal("0")


class CostRecordRead(CostRecordCreate):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
