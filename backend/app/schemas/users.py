from datetime import datetime

from pydantic import BaseModel, ConfigDict


class RoleCreate(BaseModel):
    name: str
    description: str | None = None


class RoleRead(RoleCreate):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    email: str
    full_name: str
    role_id: int | None = None
    is_active: bool = True


class UserRead(UserCreate):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
