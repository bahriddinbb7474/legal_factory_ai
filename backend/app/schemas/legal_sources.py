from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator


DOCUMENT_TYPES = {
    "code",
    "law",
    "presidential_decree",
    "presidential_resolution",
    "cabinet_resolution",
    "ministerial_order",
    "technical_regulation",
    "standard",
    "sanitary_rule",
    "fire_safety_rule",
    "customs_rule",
    "tax_rule",
    "other",
}
SOURCE_STATUSES = {"active", "outdated", "draft", "archived"}
OFFICIAL_STATUSES = {"official", "non_official", "unknown"}


class LegalSourceCreate(BaseModel):
    document_type: str
    title: str = Field(min_length=1)
    document_number: str | None = None
    source_name: str = Field(min_length=1)
    source_url: str | None = None
    adoption_date: str | None = None
    revision_date: str | None = None
    language: str = "ru"
    status: str = "active"
    official_status: str = "official"
    raw_text: str | None = None

    @model_validator(mode="after")
    def validate_choices(self) -> "LegalSourceCreate":
        if self.document_type not in DOCUMENT_TYPES:
            raise ValueError("Unsupported legal document type")
        if self.status not in SOURCE_STATUSES:
            raise ValueError("Unsupported legal source status")
        if self.official_status not in OFFICIAL_STATUSES:
            raise ValueError("Unsupported official status")
        return self


class LegalSourceUpdate(BaseModel):
    document_type: str | None = None
    title: str | None = None
    document_number: str | None = None
    source_name: str | None = None
    source_url: str | None = None
    adoption_date: str | None = None
    revision_date: str | None = None
    last_checked_at: datetime | None = None
    next_check_due_at: datetime | None = None
    language: str | None = None
    status: str | None = None
    official_status: str | None = None


class LegalChunkRead(BaseModel):
    id: int
    legal_source_id: int
    article_or_point: str | None = None
    section_title: str | None = None
    chunk_index: int
    chunk_text: str
    metadata_json: dict | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LegalChunkInspectionRead(BaseModel):
    id: int
    chunk_index: int
    article_or_point: str | None = None
    section_title: str | None = None
    text_preview: str
    chunk_text: str
    char_count: int
    created_at: datetime


class LegalSourceRead(BaseModel):
    id: int
    document_type: str
    title: str
    document_number: str | None = None
    source_name: str
    source_url: str | None = None
    adoption_date: str | None = None
    revision_date: str | None = None
    last_checked_at: datetime | None = None
    next_check_due_at: datetime | None = None
    language: str
    status: str
    official_status: str
    uploaded_by_user_id: int | None = None
    storage_key: str
    chunks_count: int = 0
    needs_revision_check: bool = False
    revision_warning: str | None = None
    readiness_warnings: list[str] = Field(default_factory=list)
    readiness_warning_messages: list[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LegalSourceDetailRead(LegalSourceRead):
    chunks: list[LegalChunkRead] = Field(default_factory=list)


class LegalSourceInventoryItem(BaseModel):
    legal_source_id: int
    title: str
    document_type: str
    document_number: str | None = None
    adoption_date: str | None = None
    revision_date: str | None = None
    language: str
    status: str
    official_status: str
    source_url: str | None = None
    last_checked_at: datetime | None = None
    next_check_due_at: datetime | None = None
    freshness_warning: bool

    model_config = ConfigDict(frozen=True)
