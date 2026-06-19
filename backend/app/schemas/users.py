from datetime import datetime

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class UserRole(StrEnum):
    admin = "admin"
    director = "director"
    chief_accountant = "chief_accountant"
    legal_responsible = "legal_responsible"
    sales = "sales"
    supply = "supply"
    hr = "hr"
    accountant = "accountant"
    viewer = "viewer"


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
    role: UserRole = UserRole.viewer
    password: str = Field(min_length=12, max_length=256)
    is_active: bool = True


class UserRead(BaseModel):
    id: int
    email: str
    full_name: str
    role: UserRole
    is_active: bool
    last_login_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    full_name: str | None = None
    role: UserRole | None = None
    is_active: bool | None = None


class UserPasswordReset(BaseModel):
    new_password: str = Field(min_length=12, max_length=256)


class BootstrapAdminRequest(BaseModel):
    email: str
    full_name: str
    password: str = Field(min_length=12, max_length=256)


class LoginRequest(BaseModel):
    email: str
    password: str
