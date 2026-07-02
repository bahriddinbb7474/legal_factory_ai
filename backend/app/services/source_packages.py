import hashlib
import math
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.base import (
    Chat,
    LegalChunk,
    LegalSource,
    LegalSourcePackage,
    LegalSourcePackageItem,
    Message,
)
from app.schemas.rag import RAG_EXCLUDE, RAG_MUST_HAVE
from app.schemas.source_packages import (
    SOURCE_PACKAGE_FAILURE_STATUSES,
    SOURCE_PACKAGE_PROTOCOL_VERSION,
    LegalSourcePackageCreate,
    LegalSourcePackageSnapshot,
    SourcePackageStatus,
)
from app.services.legal_retriever import RetrievedLegalChunk
from app.services.section_policy import get_section_group, normalize_section_code


ALLOWED_LAWYER_CODES = frozenset({"lawyer_1", "lawyer_2", "lawyer_3"})
SAFE_ERROR_CODE_PATTERN = re.compile(r"[a-z][a-z0-9_]{0,63}")


class SourcePackageBuildError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class _ItemSnapshot:
    legal_source_id: int
    legal_chunk_id: int
    rank: int
    score: float
    source_title_snapshot: str
    document_number_snapshot: str | None
    revision_date_snapshot: str | None
    source_url_snapshot: str | None
    chunk_label_snapshot: str
    chunk_text_snapshot: str
    chunk_content_hash: str


async def build_source_package_from_chunks(
    db: AsyncSession,
    *,
    create: LegalSourcePackageCreate,
    retrieved_chunks: Sequence[RetrievedLegalChunk],
    score_threshold: float = 0.05,
    minimum_chunks: int = 1,
    as_of: datetime | None = None,
) -> LegalSourcePackage:
    """Persist exact snapshots for already-retrieved legal chunks without invoking retrieval or an LLM."""
    await _validate_create_context(db, create)
    if score_threshold < 0 or not math.isfinite(score_threshold):
        raise SourcePackageBuildError("score_threshold must be a finite non-negative number")
    if minimum_chunks < 1:
        raise SourcePackageBuildError("minimum_chunks must be positive")

    if not retrieved_chunks:
        return await _persist_package(db, create=create, status="empty", snapshots=[])

    snapshots: list[_ItemSnapshot] = []
    freshness_warning = False
    seen_chunk_ids: set[int] = set()
    inventory_time = as_of or datetime.utcnow()
    for rank, retrieved in enumerate(retrieved_chunks, start=1):
        if not isinstance(retrieved, RetrievedLegalChunk):
            return await _persist_package(
                db,
                create=create,
                status="blocked_by_policy",
                snapshots=[],
                error_code="non_legal_chunk_input",
            )
        if retrieved.legal_chunk_id in seen_chunk_ids:
            return await _persist_package(
                db,
                create=create,
                status="blocked_by_policy",
                snapshots=[],
                error_code="duplicate_legal_chunk",
            )
        seen_chunk_ids.add(retrieved.legal_chunk_id)
        if create.rag_request.source_scope and retrieved.legal_source_id not in create.rag_request.source_scope:
            return await _persist_package(
                db,
                create=create,
                status="blocked_by_policy",
                snapshots=[],
                error_code="source_outside_scope",
            )

        source_and_chunk = await _load_source_and_chunk(db, retrieved)
        if source_and_chunk is None:
            return await _persist_package(
                db,
                create=create,
                status="blocked_by_policy",
                snapshots=[],
                error_code="ineligible_legal_source",
            )
        source, chunk = source_and_chunk
        _validate_retrieved_snapshot(retrieved, source, chunk)
        freshness_warning = freshness_warning or bool(
            source.next_check_due_at is not None and source.next_check_due_at < inventory_time
        )
        snapshots.append(_snapshot_item(retrieved, rank))

    complete_snapshots = all(
        snapshot.source_title_snapshot.strip() and snapshot.chunk_text_snapshot.strip()
        for snapshot in snapshots
    )
    meets_threshold = all(snapshot.score >= score_threshold for snapshot in snapshots)
    status: SourcePackageStatus = (
        "ready"
        if len(snapshots) >= minimum_chunks and meets_threshold and complete_snapshots and not freshness_warning
        else "insufficient"
    )
    return await _persist_package(db, create=create, status=status, snapshots=snapshots)


async def persist_source_package_failure(
    db: AsyncSession,
    *,
    create: LegalSourcePackageCreate,
    status: SourcePackageStatus,
    error_code: str,
) -> LegalSourcePackage:
    await _validate_create_context(db, create)
    if status not in SOURCE_PACKAGE_FAILURE_STATUSES:
        raise SourcePackageBuildError("failure package status is not allowed")
    if not SAFE_ERROR_CODE_PATTERN.fullmatch(error_code):
        raise SourcePackageBuildError("error_code must be a non-sensitive normalized code")
    return await _persist_package(
        db,
        create=create,
        status=status,
        snapshots=[],
        error_code=error_code,
    )


async def get_source_package_snapshot(
    db: AsyncSession,
    package_id: int,
) -> LegalSourcePackageSnapshot | None:
    result = await db.execute(
        select(LegalSourcePackage)
        .where(LegalSourcePackage.id == package_id)
        .options(selectinload(LegalSourcePackage.items))
    )
    package = result.scalar_one_or_none()
    if package is None:
        return None
    return LegalSourcePackageSnapshot.model_validate(package)


async def _validate_create_context(db: AsyncSession, create: LegalSourcePackageCreate) -> None:
    if create.protocol_version != SOURCE_PACKAGE_PROTOCOL_VERSION:
        raise SourcePackageBuildError("unsupported source package protocol version")
    normalized_section = normalize_section_code(create.section_code)
    if normalized_section != create.section_code or get_section_group(normalized_section) != create.group_code:
        raise SourcePackageBuildError("section and group must be canonical and consistent")
    if create.lawyer_code not in ALLOWED_LAWYER_CODES:
        raise SourcePackageBuildError("unsupported lawyer code")
    if tuple(create.rag_request.must_have) != RAG_MUST_HAVE or tuple(create.rag_request.exclude) != RAG_EXCLUDE:
        raise SourcePackageBuildError("RAG request invariants are not canonical")
    if not create.rag_request.needs_rag or not create.retrieval_query.strip():
        raise SourcePackageBuildError("source packages require an active canonical RAG request")
    if create.retrieval_query != create.rag_request.question_for_retrieval:
        raise SourcePackageBuildError("retrieval query must match the canonical RAG request")

    chat = await db.get(Chat, create.chat_id)
    if chat is None:
        raise SourcePackageBuildError("parent chat does not exist")
    if create.trigger_message_id is not None:
        message = await db.get(Message, create.trigger_message_id)
        if message is None or message.chat_id != create.chat_id or message.author_type != "user":
            raise SourcePackageBuildError("trigger message must be a user message in the parent chat")


async def _load_source_and_chunk(
    db: AsyncSession,
    retrieved: RetrievedLegalChunk,
) -> tuple[LegalSource, LegalChunk] | None:
    result = await db.execute(
        select(LegalSource, LegalChunk)
        .join(LegalChunk, LegalChunk.legal_source_id == LegalSource.id)
        .where(
            LegalSource.id == retrieved.legal_source_id,
            LegalChunk.id == retrieved.legal_chunk_id,
            LegalSource.status == "active",
            LegalSource.official_status == "official",
        )
    )
    return result.one_or_none()


def _validate_retrieved_snapshot(
    retrieved: RetrievedLegalChunk,
    source: LegalSource,
    chunk: LegalChunk,
) -> None:
    expected = (
        source.title,
        source.document_type,
        source.document_number,
        source.revision_date,
        source.source_url,
        source.source_name,
        chunk.article_or_point,
        chunk.chunk_text,
    )
    actual = (
        retrieved.title,
        retrieved.document_type,
        retrieved.document_number,
        retrieved.revision_date,
        retrieved.source_url,
        retrieved.source_name,
        retrieved.article_or_point,
        retrieved.chunk_text,
    )
    if expected != actual:
        raise SourcePackageBuildError("retrieved chunk no longer matches current legal source data")
    if not math.isfinite(retrieved.score) or retrieved.score < 0:
        raise SourcePackageBuildError("retrieved chunk score must be finite and non-negative")


def _snapshot_item(retrieved: RetrievedLegalChunk, rank: int) -> _ItemSnapshot:
    chunk_text = retrieved.chunk_text
    return _ItemSnapshot(
        legal_source_id=retrieved.legal_source_id,
        legal_chunk_id=retrieved.legal_chunk_id,
        rank=rank,
        score=retrieved.score,
        source_title_snapshot=retrieved.title,
        document_number_snapshot=retrieved.document_number,
        revision_date_snapshot=retrieved.revision_date,
        source_url_snapshot=retrieved.source_url,
        chunk_label_snapshot=retrieved.article_or_point or "unknown",
        chunk_text_snapshot=chunk_text,
        chunk_content_hash=hashlib.sha256(chunk_text.encode("utf-8")).hexdigest(),
    )


async def _persist_package(
    db: AsyncSession,
    *,
    create: LegalSourcePackageCreate,
    status: SourcePackageStatus,
    snapshots: Sequence[_ItemSnapshot],
    error_code: str | None = None,
) -> LegalSourcePackage:
    rag_request_json = create.rag_request.model_dump(mode="json")
    hash_ready_snapshot = _build_hash_ready_snapshot(
        create=create,
        status=status,
        rag_request_json=rag_request_json,
        snapshots=snapshots,
    )
    package = LegalSourcePackage(
        protocol_version=create.protocol_version,
        chat_id=create.chat_id,
        trigger_message_id=create.trigger_message_id,
        section_code=create.section_code,
        group_code=create.group_code,
        lawyer_code=create.lawyer_code,
        rag_request_json=rag_request_json,
        retrieval_query=create.retrieval_query,
        status=status,
        error_code=error_code,
        hash_ready_snapshot_json=hash_ready_snapshot,
        items=[
            LegalSourcePackageItem(
                legal_source_id=snapshot.legal_source_id,
                legal_chunk_id=snapshot.legal_chunk_id,
                rank=snapshot.rank,
                score=snapshot.score,
                source_title_snapshot=snapshot.source_title_snapshot,
                document_number_snapshot=snapshot.document_number_snapshot,
                revision_date_snapshot=snapshot.revision_date_snapshot,
                source_url_snapshot=snapshot.source_url_snapshot,
                chunk_label_snapshot=snapshot.chunk_label_snapshot,
                chunk_text_snapshot=snapshot.chunk_text_snapshot,
                chunk_content_hash=snapshot.chunk_content_hash,
            )
            for snapshot in snapshots
        ],
    )
    db.add(package)
    await db.flush()
    return package


def _build_hash_ready_snapshot(
    *,
    create: LegalSourcePackageCreate,
    status: SourcePackageStatus,
    rag_request_json: dict,
    snapshots: Sequence[_ItemSnapshot],
) -> dict:
    return {
        "protocol_version": create.protocol_version,
        "rag_request": rag_request_json,
        "section_code": create.section_code,
        "group_code": create.group_code,
        "lawyer_code": create.lawyer_code,
        "retrieval_query": create.retrieval_query,
        "status": status,
        "package_items": [
            {
                "legal_source_id": snapshot.legal_source_id,
                "legal_chunk_id": snapshot.legal_chunk_id,
                "rank": snapshot.rank,
                "source_title_snapshot": snapshot.source_title_snapshot,
                "document_number_snapshot": snapshot.document_number_snapshot,
                "revision_date_snapshot": snapshot.revision_date_snapshot,
                "source_url_snapshot": snapshot.source_url_snapshot,
                "chunk_label_snapshot": snapshot.chunk_label_snapshot,
                "chunk_text_snapshot": snapshot.chunk_text_snapshot,
                "chunk_content_hash": snapshot.chunk_content_hash,
            }
            for snapshot in snapshots
        ],
    }
