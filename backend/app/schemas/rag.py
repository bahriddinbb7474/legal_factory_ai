from pydantic import BaseModel, ConfigDict, Field


RAG_MUST_HAVE = ("active", "official")
RAG_EXCLUDE = ("outdated", "foreign_law", "untrusted_without_confirmation")


class LegalTriggerDetection(BaseModel):
    has_legal_trigger: bool
    matched_families: list[str] = Field(default_factory=list)
    matched_patterns: list[str] = Field(default_factory=list)

    model_config = ConfigDict(extra="forbid", frozen=True)


class CanonicalRagRequest(BaseModel):
    needs_rag: bool
    reason: str
    source_scope: list[int] = Field(default_factory=list)
    topics: list[str] = Field(default_factory=list)
    must_have: list[str] = Field(default_factory=lambda: list(RAG_MUST_HAVE))
    exclude: list[str] = Field(default_factory=lambda: list(RAG_EXCLUDE))
    question_for_retrieval: str

    model_config = ConfigDict(extra="forbid", frozen=True)


class RagPlanningResult(BaseModel):
    request: CanonicalRagRequest
    trigger_detection: LegalTriggerDetection
    requires_legal_review: bool
    clarification_needed: bool
    section_code: str
    section_group: str

    model_config = ConfigDict(extra="forbid", frozen=True)
