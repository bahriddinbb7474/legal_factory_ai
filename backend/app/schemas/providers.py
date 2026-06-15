from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ProviderRead(BaseModel):
    id: int
    provider_code: str
    display_name: str
    is_allowlisted: bool
    supports_zdr: bool
    is_trusted_for_sensitive: bool
    is_enabled: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProviderUpdate(BaseModel):
    display_name: str | None = None
    is_allowlisted: bool | None = None
    supports_zdr: bool | None = None
    is_trusted_for_sensitive: bool | None = None
    is_enabled: bool | None = None
