from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class AgentCreate(BaseModel):
    code: str
    name: str
    display_name: str = ""
    provider_code: str = ""
    model_name: str = ""
    system_prompt: str = ""
    role_type: str = ""
    is_enabled: bool = True
    input_price_per_1m: Decimal = Decimal("0")
    output_price_per_1m: Decimal = Decimal("0")
    supports_zdr: bool = False


class AgentRead(AgentCreate):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AgentUpdate(BaseModel):
    display_name: str | None = None
    provider_code: str | None = None
    model_name: str | None = None
    system_prompt: str | None = None
    role_type: str | None = None
    is_enabled: bool | None = None
    input_price_per_1m: Decimal | None = None
    output_price_per_1m: Decimal | None = None
    supports_zdr: bool | None = None
