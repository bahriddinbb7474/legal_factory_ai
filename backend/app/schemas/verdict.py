from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class VerdictLegalSource(BaseModel):
    source_id: str = ""
    title: str = ""
    number: str = ""
    date: str = ""
    article_or_clause: str = ""
    quote: str = ""

    model_config = ConfigDict(extra="ignore")


class VerdictPayload(BaseModel):
    type: Literal["verdict"]
    lawyer_id: Literal["lawyer_2", "lawyer_3"]
    jurisdiction: Literal["UZ"] = "UZ"
    short_conclusion: str = Field(min_length=1)
    facts_established: list[str] = Field(default_factory=list)
    facts_missing: list[str] = Field(default_factory=list)
    legal_sources: list[VerdictLegalSource] = Field(default_factory=list)
    analysis: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    recommended_actions: list[str] = Field(default_factory=list)
    confidence: Literal["low", "medium", "high"]

    model_config = ConfigDict(extra="ignore")


VERDICT_RESPONSE_INSTRUCTION = """
Это отдельный, явно разрешенный backend verdict-режим.
Верни только валидный JSON без Markdown и текста вне JSON:
{
  "type": "verdict",
  "lawyer_id": "lawyer_2 | lawyer_3",
  "jurisdiction": "UZ",
  "short_conclusion": "",
  "facts_established": [],
  "facts_missing": [],
  "legal_sources": [{
    "source_id": "",
    "title": "",
    "number": "",
    "date": "",
    "article_or_clause": "",
    "quote": ""
  }],
  "analysis": [],
  "risks": [],
  "recommended_actions": [],
  "confidence": "low | medium | high"
}
Не добавляй confirmed_in_context, source_check_status, document_generation_allowed или approval_required:
эти поля вычисляет только backend.
Не выдумывай источники, статьи, даты или цитаты.
"""
