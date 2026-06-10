from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AgentCreate(BaseModel):
    code: str
    name: str
    model_name: str = ""
    is_enabled: bool = True


class AgentRead(AgentCreate):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
