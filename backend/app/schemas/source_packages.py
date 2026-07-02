from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.rag import CanonicalRagRequest


SOURCE_PACKAGE_PROTOCOL_VERSION = "p4_rag_v1"
SOURCE_PACKAGE_STATUSES = frozenset(
    {
        "ready",
        "empty",
        "insufficient",
        "planner_failed",
        "retrieval_failed",
        "blocked_by_policy",
    }
)
SOURCE_PACKAGE_FAILURE_STATUSES = frozenset({"planner_failed", "retrieval_failed", "blocked_by_policy"})
SourcePackageStatus = Literal[
    "ready",
    "empty",
    "insufficient",
    "planner_failed",
    "retrieval_failed",
    "blocked_by_policy",
]


class LegalSourcePackageCreate(BaseModel):
    protocol_version: str = SOURCE_PACKAGE_PROTOCOL_VERSION
    chat_id: int
    trigger_message_id: int | None = None
    section_code: str
    group_code: str
    lawyer_code: str
    rag_request: CanonicalRagRequest
    retrieval_query: str

    model_config = ConfigDict(extra="forbid", frozen=True)


class LegalSourcePackageItemSnapshot(BaseModel):
    id: int
    package_id: int
    legal_source_id: int | None = None
    legal_chunk_id: int | None = None
    rank: int
    score: float
    source_title_snapshot: str
    document_number_snapshot: str | None = None
    revision_date_snapshot: str | None = None
    source_url_snapshot: str | None = None
    chunk_label_snapshot: str
    chunk_text_snapshot: str
    chunk_content_hash: str

    model_config = ConfigDict(from_attributes=True, frozen=True)


class LegalSourcePackageSnapshot(BaseModel):
    id: int
    protocol_version: str
    chat_id: int
    trigger_message_id: int | None = None
    section_code: str
    group_code: str
    lawyer_code: str
    rag_request_json: dict
    retrieval_query: str
    status: SourcePackageStatus
    error_code: str | None = None
    created_at: datetime
    hash_ready_snapshot_json: dict
    items: list[LegalSourcePackageItemSnapshot] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True, frozen=True)
