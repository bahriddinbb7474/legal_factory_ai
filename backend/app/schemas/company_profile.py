from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


def _normalize_optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned or None


class CompanyProfileUpdate(BaseModel):
    full_name: str = Field(min_length=1)
    short_name: str = Field(min_length=1)
    legal_address: str | None = None
    actual_address: str | None = None
    tax_id: str | None = None
    oked: str | None = None
    bank_name: str | None = None
    bank_mfo: str | None = None
    bank_account: str | None = None
    director_name: str | None = None
    chief_accountant_name: str | None = None
    legal_responsible_name: str | None = None
    phone: str | None = None
    email: str | None = None
    website: str | None = None
    logo_storage_key: str | None = None
    letterhead_storage_key: str | None = None
    is_active: bool = True
    notes: str | None = None

    @field_validator(
        "legal_address",
        "actual_address",
        "tax_id",
        "oked",
        "bank_name",
        "bank_mfo",
        "bank_account",
        "director_name",
        "chief_accountant_name",
        "legal_responsible_name",
        "phone",
        "email",
        "website",
        "logo_storage_key",
        "letterhead_storage_key",
        "notes",
        mode="before",
    )
    @classmethod
    def normalize_optional_fields(cls, value: str | None) -> str | None:
        return _normalize_optional_text(value)

    @field_validator("full_name", "short_name")
    @classmethod
    def validate_required_text(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Field is required")
        return cleaned

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str | None) -> str | None:
        if value is None:
            return None
        if "@" not in value or value.startswith("@") or value.endswith("@"):
            raise ValueError("Invalid email address")
        return value


class CompanyProfileRead(BaseModel):
    id: int
    full_name: str
    short_name: str
    legal_address: str | None = None
    actual_address: str | None = None
    tax_id: str | None = None
    oked: str | None = None
    bank_name: str | None = None
    bank_mfo: str | None = None
    bank_account: str | None = None
    director_name: str | None = None
    chief_accountant_name: str | None = None
    legal_responsible_name: str | None = None
    phone: str | None = None
    email: str | None = None
    website: str | None = None
    logo_storage_key: str | None = None
    letterhead_storage_key: str | None = None
    is_active: bool
    notes: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CompanyProfileContext(BaseModel):
    full_name: str
    short_name: str
    legal_address: str | None = None
    actual_address: str | None = None
    tax_id: str | None = None
    oked: str | None = None
    bank_name: str | None = None
    bank_mfo: str | None = None
    bank_account: str | None = None
    director_name: str | None = None
    chief_accountant_name: str | None = None
    legal_responsible_name: str | None = None
    phone: str | None = None
    email: str | None = None
    website: str | None = None
    logo_storage_key: str | None = None
    letterhead_storage_key: str | None = None
