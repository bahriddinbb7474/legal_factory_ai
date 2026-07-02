import asyncio
import hashlib
import sqlite3
from collections.abc import Awaitable, Callable
from datetime import datetime, timedelta
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.db.base import Base, Chat, LegalChunk, LegalSource, Message
from app.schemas.rag import CanonicalRagRequest
from app.schemas.source_packages import (
    SOURCE_PACKAGE_STATUSES,
    LegalSourcePackageCreate,
)
from app.services.legal_retriever import RetrievedLegalChunk
from app.services.source_packages import (
    SourcePackageBuildError,
    build_source_package_from_chunks,
    get_source_package_snapshot,
    persist_source_package_failure,
)


async def _run_with_db(scenario: Callable[[AsyncSession], Awaitable[None]]) -> None:
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    try:
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)
        async with session_factory() as session:
            await scenario(session)
    finally:
        await engine.dispose()


async def _seed_context(
    db: AsyncSession,
    *,
    source_status: str = "active",
    official_status: str = "official",
    next_check_due_at: datetime | None = None,
    chunks: tuple[str, ...] = ("Exact first legal chunk.", "Exact second legal chunk."),
) -> tuple[LegalSourcePackageCreate, LegalSource, Message, list[LegalChunk]]:
    chat = Chat(title="P4-C", section="legal_tax")
    db.add(chat)
    await db.flush()
    message = Message(
        chat_id=chat.id,
        role="user",
        author_type="user",
        content="Какие налоговые последствия?",
        structured_payload=None,
    )
    source = LegalSource(
        document_type="law",
        title="Tax law snapshot",
        document_number="ZRU-TEST",
        source_name="LEX.UZ",
        source_url="https://lex.uz/test",
        adoption_date="2026-01-01",
        revision_date="2026-06-01",
        last_checked_at=datetime(2026, 6, 1),
        next_check_due_at=next_check_due_at or datetime(2026, 8, 1),
        language="ru",
        status=source_status,
        official_status=official_status,
        storage_key="legal/test.txt",
    )
    db.add_all([message, source])
    await db.flush()
    legal_chunks = [
        LegalChunk(
            legal_source_id=source.id,
            article_or_point=f"Article {index}",
            section_title=None,
            chunk_index=index - 1,
            chunk_text=text,
            embedding=None,
            metadata_json=None,
        )
        for index, text in enumerate(chunks, start=1)
    ]
    db.add_all(legal_chunks)
    await db.flush()
    request = CanonicalRagRequest(
        needs_rag=True,
        reason="legal_trigger_requires_rag",
        topics=["tax"],
        question_for_retrieval="Current question: Какие налоговые последствия?",
    )
    create = LegalSourcePackageCreate(
        chat_id=chat.id,
        trigger_message_id=message.id,
        section_code="legal_tax",
        group_code="legal_questions",
        lawyer_code="lawyer_1",
        rag_request=request,
        retrieval_query=request.question_for_retrieval,
    )
    return create, source, message, legal_chunks


def _retrieved(source: LegalSource, chunk: LegalChunk, *, score: float) -> RetrievedLegalChunk:
    return RetrievedLegalChunk(
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
        needs_revision_check=False,
    )


def test_ready_package_persists_exact_ordered_immutable_snapshots() -> None:
    async def scenario(db: AsyncSession) -> None:
        create, source, message, chunks = await _seed_context(db)
        intended_context = [
            _retrieved(source, chunks[1], score=0.9),
            _retrieved(source, chunks[0], score=0.8),
        ]

        package = await build_source_package_from_chunks(
            db,
            create=create,
            retrieved_chunks=intended_context,
            as_of=datetime(2026, 7, 2),
        )
        await db.commit()
        snapshot = await get_source_package_snapshot(db, package.id)

        assert snapshot is not None
        assert snapshot.status == "ready"
        assert snapshot.chat_id == create.chat_id
        assert snapshot.trigger_message_id == message.id
        assert [item.rank for item in snapshot.items] == [1, 2]
        assert [item.legal_chunk_id for item in snapshot.items] == [chunks[1].id, chunks[0].id]
        assert [item.chunk_text_snapshot for item in snapshot.items] == [
            intended_context[0].chunk_text,
            intended_context[1].chunk_text,
        ]
        assert snapshot.items[0].source_title_snapshot == source.title
        assert snapshot.items[0].chunk_content_hash == hashlib.sha256(
            intended_context[0].chunk_text.encode("utf-8")
        ).hexdigest()
        assert "created_at" not in str(snapshot.hash_ready_snapshot_json)
        assert "timestamp" not in str(snapshot.hash_ready_snapshot_json)
        assert message.structured_payload is None

        old_title = snapshot.items[0].source_title_snapshot
        old_text = snapshot.items[0].chunk_text_snapshot
        source.title = "Edited source title"
        chunks[1].chunk_text = "Edited current chunk text."
        await db.commit()

        unchanged = await get_source_package_snapshot(db, package.id)
        assert unchanged is not None
        assert unchanged.items[0].source_title_snapshot == old_title
        assert unchanged.items[0].chunk_text_snapshot == old_text

    asyncio.run(_run_with_db(scenario))


def test_hash_ready_snapshot_is_deterministic_for_same_inputs() -> None:
    async def scenario(db: AsyncSession) -> None:
        create, source, _, chunks = await _seed_context(db)
        retrieved = [_retrieved(source, chunks[0], score=0.75)]

        first = await build_source_package_from_chunks(db, create=create, retrieved_chunks=retrieved)
        second = await build_source_package_from_chunks(db, create=create, retrieved_chunks=retrieved)
        await db.commit()

        assert first.id != second.id
        assert first.hash_ready_snapshot_json == second.hash_ready_snapshot_json
        assert first.hash_ready_snapshot_json["package_items"][0]["chunk_text_snapshot"] == chunks[0].chunk_text
        assert "created_at" not in first.hash_ready_snapshot_json

    asyncio.run(_run_with_db(scenario))


def test_empty_and_insufficient_statuses_are_derived_by_backend() -> None:
    async def scenario(db: AsyncSession) -> None:
        create, source, _, chunks = await _seed_context(db)

        empty = await build_source_package_from_chunks(db, create=create, retrieved_chunks=[])
        below_threshold = await build_source_package_from_chunks(
            db,
            create=create,
            retrieved_chunks=[_retrieved(source, chunks[0], score=0.01)],
            score_threshold=0.05,
        )
        await db.commit()

        assert empty.status == "empty"
        assert empty.items == []
        assert below_threshold.status == "insufficient"
        assert len(below_threshold.items) == 1

    asyncio.run(_run_with_db(scenario))


def test_freshness_review_makes_package_insufficient() -> None:
    async def scenario(db: AsyncSession) -> None:
        as_of = datetime(2026, 7, 2)
        create, source, _, chunks = await _seed_context(
            db,
            next_check_due_at=as_of - timedelta(seconds=1),
        )

        package = await build_source_package_from_chunks(
            db,
            create=create,
            retrieved_chunks=[_retrieved(source, chunks[0], score=0.8)],
            as_of=as_of,
        )

        assert package.status == "insufficient"

    asyncio.run(_run_with_db(scenario))


@pytest.mark.parametrize(
    ("source_status", "official_status"),
    [
        ("draft", "official"),
        ("outdated", "official"),
        ("archived", "official"),
        ("active", "non_official"),
        ("active", "unknown"),
    ],
)
def test_ineligible_source_chunks_are_blocked(
    source_status: str,
    official_status: str,
) -> None:
    async def scenario(db: AsyncSession) -> None:
        create, source, _, chunks = await _seed_context(
            db,
            source_status=source_status,
            official_status=official_status,
        )

        package = await build_source_package_from_chunks(
            db,
            create=create,
            retrieved_chunks=[_retrieved(source, chunks[0], score=0.8)],
        )

        assert package.status == "blocked_by_policy"
        assert package.error_code == "ineligible_legal_source"
        assert package.items == []

    asyncio.run(_run_with_db(scenario))


def test_uploaded_or_non_legal_input_cannot_become_package_item() -> None:
    async def scenario(db: AsyncSession) -> None:
        create, _, _, _ = await _seed_context(db)

        package = await build_source_package_from_chunks(
            db,
            create=create,
            retrieved_chunks=[{"document_id": 123, "chunk_text": "uploaded raw text"}],  # type: ignore[list-item]
        )

        assert package.status == "blocked_by_policy"
        assert package.error_code == "non_legal_chunk_input"
        assert package.items == []
        assert "uploaded raw text" not in str(package.hash_ready_snapshot_json)

    asyncio.run(_run_with_db(scenario))


def test_source_outside_canonical_scope_is_blocked() -> None:
    async def scenario(db: AsyncSession) -> None:
        create, source, _, chunks = await _seed_context(db)
        scoped_request = create.rag_request.model_copy(update={"source_scope": [source.id + 100]})
        scoped_create = create.model_copy(update={"rag_request": scoped_request})

        package = await build_source_package_from_chunks(
            db,
            create=scoped_create,
            retrieved_chunks=[_retrieved(source, chunks[0], score=0.8)],
        )

        assert package.status == "blocked_by_policy"
        assert package.error_code == "source_outside_scope"
        assert package.items == []

    asyncio.run(_run_with_db(scenario))


@pytest.mark.parametrize("status", ["planner_failed", "retrieval_failed", "blocked_by_policy"])
def test_failure_statuses_are_explicit_backend_owned_codes(status: str) -> None:
    async def scenario(db: AsyncSession) -> None:
        create, _, _, _ = await _seed_context(db)

        package = await persist_source_package_failure(
            db,
            create=create,
            status=status,  # type: ignore[arg-type]
            error_code="safe_failure_code",
        )

        assert package.status == status
        assert package.error_code == "safe_failure_code"
        assert not hasattr(package, "error_message")
        assert package.items == []

    asyncio.run(_run_with_db(scenario))


def test_failure_service_rejects_non_failure_status_and_sensitive_error_text() -> None:
    async def scenario(db: AsyncSession) -> None:
        create, _, _, _ = await _seed_context(db)

        with pytest.raises(SourcePackageBuildError, match="status"):
            await persist_source_package_failure(
                db,
                create=create,
                status="ready",
                error_code="not_a_failure",
            )
        with pytest.raises(SourcePackageBuildError, match="non-sensitive"):
            await persist_source_package_failure(
                db,
                create=create,
                status="retrieval_failed",
                error_code="raw uploaded contract text must not leak",
            )

    asyncio.run(_run_with_db(scenario))


def test_package_status_contract_contains_only_backend_owned_values() -> None:
    assert SOURCE_PACKAGE_STATUSES == {
        "ready",
        "empty",
        "insufficient",
        "planner_failed",
        "retrieval_failed",
        "blocked_by_policy",
    }


def test_migration_creates_source_package_tables_on_sqlite(tmp_path, monkeypatch) -> None:
    backend_dir = Path(__file__).resolve().parents[1]
    database_path = tmp_path / "p4c_migration.sqlite3"
    monkeypatch.setattr(settings, "database_url", f"sqlite+aiosqlite:///{database_path.as_posix()}")
    config = Config(str(backend_dir / "alembic.ini"))
    config.set_main_option("script_location", str(backend_dir / "alembic"))

    command.upgrade(config, "head")

    with sqlite3.connect(database_path) as connection:
        tables = {
            row[0]
            for row in connection.execute("SELECT name FROM sqlite_master WHERE type = 'table'").fetchall()
        }
        package_indexes = {
            row[1]
            for row in connection.execute("PRAGMA index_list('legal_source_packages')").fetchall()
        }
        item_indexes = {
            row[1]
            for row in connection.execute("PRAGMA index_list('legal_source_package_items')").fetchall()
        }

    assert {"legal_source_packages", "legal_source_package_items"} <= tables
    assert "ix_legal_source_packages_chat_id" in package_indexes
    assert "ix_legal_source_packages_trigger_message_id" in package_indexes
    assert "ix_legal_source_packages_status" in package_indexes
    assert "ix_legal_source_package_items_package_id" in item_indexes
    assert "ix_legal_source_package_items_legal_source_id" in item_indexes
    assert "ix_legal_source_package_items_legal_chunk_id" in item_indexes
