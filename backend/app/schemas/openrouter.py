from decimal import Decimal

from pydantic import BaseModel


class OpenRouterModelRead(BaseModel):
    model_id: str
    name: str
    provider: str
    input_price: Decimal
    output_price: Decimal
    context_length: int
    is_free: bool
    supports_zdr: bool
    supports_vision: bool
    is_available: bool


class InvokeAgentRequest(BaseModel):
    agent_code: str
