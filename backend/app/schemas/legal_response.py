from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


RiskLevel = Literal["green", "yellow", "red"]
ConfidenceLevel = Literal["high", "medium", "low"]
ApprovalRequirement = Literal["none", "chief_accountant", "director", "external_lawyer"]
SourceType = Literal["uploaded_document", "law_unconfirmed"]
VerificationStatus = Literal["pending", "confirmed", "unconfirmed"]
SourceCheckStatus = Literal["not_checked", "confirmed", "partially_confirmed", "unconfirmed"]


class LegalFinding(BaseModel):
    title: str = Field(min_length=1)
    description: str = Field(min_length=1)

    model_config = ConfigDict(extra="forbid")


class LegalSource(BaseModel):
    source_type: SourceType
    document_id: int | None = None
    title: str = Field(min_length=1)
    document_number: str | None = None
    revision_date: str | None = None
    article_or_point: str | None = None
    quote: str = Field(min_length=1)
    verification_status: VerificationStatus = "pending"

    model_config = ConfigDict(extra="forbid")


class LegalAgreement(BaseModel):
    agreed_points: list[str] = Field(default_factory=list)
    disagreed_points: list[str] = Field(default_factory=list)
    unresolved_points: list[str] = Field(default_factory=list)

    model_config = ConfigDict(extra="forbid")


class LegalStructuredResponse(BaseModel):
    summary: str = Field(min_length=1)
    risk: RiskLevel
    findings: list[LegalFinding] = Field(default_factory=list)
    sources: list[LegalSource] = Field(default_factory=list)
    meaning_for_factory: str = Field(min_length=1)
    actions: list[str] = Field(default_factory=list)
    confidence: ConfidenceLevel
    approval_required: ApprovalRequirement
    agreement: LegalAgreement | None = None

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def normalize_empty_lists(self) -> "LegalStructuredResponse":
        self.actions = [action for action in self.actions if action.strip()]
        return self


STRUCTURED_LEGAL_RESPONSE_INSTRUCTION = """
Верни только валидный JSON без Markdown и без пояснений вне JSON.
Схема:
{
  "summary": "краткий вывод",
  "risk": "green | yellow | red",
  "findings": [{"title": "название", "description": "описание"}],
  "sources": [{
    "source_type": "uploaded_document | law_unconfirmed",
    "document_id": 1,
    "title": "название источника",
    "document_number": null,
    "revision_date": null,
    "article_or_point": null,
    "quote": "точная цитата",
    "verification_status": "pending"
  }],
  "meaning_for_factory": "практический вывод для завода",
  "actions": ["действие"],
  "confidence": "high | medium | low",
  "approval_required": "none | chief_accountant | director | external_lawyer",
  "agreement": null
}
Для Юриста 2 и Юриста 3 поле agreement обязательно и должно содержать agreed_points, disagreed_points, unresolved_points.
До подключения RAG законы указывай только как source_type="law_unconfirmed"; не называй закон подтвержденным источником.
Для uploaded_document используй только document_id из контекста и цитату, которая есть в документе.
"""


SOURCE_NOT_FOUND_NOTICE = (
    "Точный источник не найден. Окончательный юридический вывод давать нельзя. "
    "Требуется проверка юристом или ответственным специалистом."
)
