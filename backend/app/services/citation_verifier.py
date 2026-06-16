import re
import unicodedata
from dataclasses import dataclass

from app.db.base import Document
from app.schemas.legal_response import LegalFinding, LegalStructuredResponse, SOURCE_NOT_FOUND_NOTICE
from app.services.legal_retriever import RetrievedLegalChunk
from app.storage.local import local_storage


@dataclass
class CitationVerificationResult:
    payload: LegalStructuredResponse
    source_check_status: str
    unconfirmed_count: int
    confirmed_count: int


class CitationVerifier:
    async def verify(
        self,
        payload: LegalStructuredResponse,
        context_documents: list[Document],
        legal_chunks: list[RetrievedLegalChunk] | None = None,
    ) -> CitationVerificationResult:
        document_map = {document.id: document for document in context_documents}
        legal_chunk_map: dict[int, list[RetrievedLegalChunk]] = {}
        for chunk in legal_chunks or []:
            legal_chunk_map.setdefault(chunk.legal_source_id, []).append(chunk)
        confirmed = 0
        unconfirmed = 0
        text_cache: dict[int, str] = {}

        for source in payload.sources:
            source.verification_status = "unconfirmed"
            if source.source_type == "law_unconfirmed":
                unconfirmed += 1
                continue
            if source.source_type == "law":
                legal_source_id = source.legal_source_id
                if legal_source_id is None or legal_source_id not in legal_chunk_map:
                    unconfirmed += 1
                    continue
                matching_chunks = legal_chunk_map[legal_source_id]
                if any(_law_metadata_matches(source, chunk) and _contains_quote(chunk.chunk_text, source.quote) for chunk in matching_chunks):
                    source.verification_status = "confirmed"
                    confirmed += 1
                else:
                    unconfirmed += 1
                continue
            if source.document_id is None or source.document_id not in document_map:
                unconfirmed += 1
                continue
            document = document_map[source.document_id]
            if not document.extracted_text_storage_key:
                unconfirmed += 1
                continue
            if document.id not in text_cache:
                text_cache[document.id] = await local_storage.read_text(document.extracted_text_storage_key)
            if _contains_quote(text_cache[document.id], source.quote):
                source.verification_status = "confirmed"
                confirmed += 1
            else:
                unconfirmed += 1

        if not payload.sources or confirmed == 0:
            status = "unconfirmed"
        elif unconfirmed == 0:
            status = "confirmed"
        else:
            status = "partially_confirmed"

        if status != "confirmed":
            if payload.risk == "green":
                payload.risk = "yellow"
            if payload.confidence == "high":
                payload.confidence = "medium"
            if not any(source.title == SOURCE_NOT_FOUND_NOTICE for source in payload.sources):
                payload.findings.append(LegalFinding(title="Источник не подтвержден", description=SOURCE_NOT_FOUND_NOTICE))

        return CitationVerificationResult(payload, status, unconfirmed, confirmed)


def _contains_quote(document_text: str, quote: str) -> bool:
    normalized_document = _normalize(document_text)
    normalized_quote = _normalize(quote)
    return bool(normalized_quote) and normalized_quote in normalized_document


def _law_metadata_matches(source, chunk: RetrievedLegalChunk) -> bool:
    return (
        source.title == chunk.title
        and (source.document_type or chunk.document_type) == chunk.document_type
        and (source.document_number or None) == chunk.document_number
        and (source.revision_date or None) == chunk.revision_date
        and (source.article_or_point or None) == chunk.article_or_point
    )


def _normalize(value: str) -> str:
    normalized = unicodedata.normalize("NFKC", value)
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized.strip().casefold()


citation_verifier = CitationVerifier()
