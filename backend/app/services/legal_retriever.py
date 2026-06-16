import re
import unicodedata
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import LegalChunk, LegalSource


@dataclass(frozen=True)
class RetrievedLegalChunk:
    legal_source_id: int
    legal_chunk_id: int
    chunk_text: str
    title: str
    document_type: str
    document_number: str | None
    revision_date: str | None
    article_or_point: str | None
    source_url: str | None
    source_name: str
    score: float
    needs_revision_check: bool


class LegalRetriever:
    async def retrieve(self, db: AsyncSession, query: str, top_k: int = 5, score_threshold: float = 0.05) -> list[RetrievedLegalChunk]:
        terms = _terms(query)
        if not terms:
            return []
        result = await db.execute(
            select(LegalChunk, LegalSource)
            .join(LegalSource, LegalSource.id == LegalChunk.legal_source_id)
            .where(LegalSource.status == "active", LegalSource.official_status == "official")
            .order_by(LegalSource.id, LegalChunk.chunk_index)
        )
        scored: list[RetrievedLegalChunk] = []
        for chunk, source in result.all():
            score = _lexical_score(terms, chunk.chunk_text)
            if score < score_threshold:
                continue
            scored.append(
                RetrievedLegalChunk(
                    legal_source_id=source.id,
                    legal_chunk_id=chunk.id,
                    chunk_text=chunk.chunk_text,
                    title=source.title,
                    document_type=source.document_type,
                    document_number=source.document_number,
                    revision_date=source.revision_date,
                    article_or_point=chunk.article_or_point,
                    source_url=source.source_url,
                    source_name=source.source_name,
                    score=score,
                    needs_revision_check=bool(source.next_check_due_at and source.next_check_due_at < datetime.utcnow()),
                )
            )
        return sorted(scored, key=lambda item: item.score, reverse=True)[:top_k]


def build_trusted_legal_context(chunks: list[RetrievedLegalChunk]) -> str:
    blocks: list[str] = []
    for chunk in chunks:
        attrs = {
            "legal_source_id": str(chunk.legal_source_id),
            "legal_chunk_id": str(chunk.legal_chunk_id),
            "document_type": chunk.document_type,
            "title": chunk.title,
            "document_number": chunk.document_number or "",
            "revision_date": chunk.revision_date or "",
            "article_or_point": chunk.article_or_point or "",
            "source_name": chunk.source_name,
            "source_url": chunk.source_url or "",
        }
        attr_text = " ".join(f'{key}="{_escape_attr(value)}"' for key, value in attrs.items())
        warning = "\nВНИМАНИЕ: редакцию нужно проверить." if chunk.needs_revision_check else ""
        blocks.append(f"<TRUSTED_LEGAL_SOURCE {attr_text}>\n{chunk.chunk_text}{warning}\n</TRUSTED_LEGAL_SOURCE>")
    return "\n\n".join(blocks)


def _terms(value: str) -> set[str]:
    normalized = _normalize(value)
    return {term for term in re.findall(r"[\w№-]{3,}", normalized) if term not in STOP_TERMS}


def _lexical_score(query_terms: set[str], text: str) -> float:
    text_terms = _terms(text)
    if not text_terms:
        return 0.0
    overlap = query_terms & text_terms
    return len(overlap) / max(len(query_terms), 1)


def _normalize(value: str) -> str:
    value = unicodedata.normalize("NFKC", value)
    value = value.casefold()
    return re.sub(r"\s+", " ", value)


def _escape_attr(value: str) -> str:
    return value.replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;").replace(">", "&gt;")


STOP_TERMS = {
    "что",
    "как",
    "для",
    "или",
    "при",
    "надо",
    "нужно",
    "если",
    "это",
    "the",
    "and",
}


legal_retriever = LegalRetriever()
