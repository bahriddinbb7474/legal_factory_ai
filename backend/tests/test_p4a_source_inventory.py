import asyncio
from datetime import datetime, timedelta

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.db.base import Base, LegalSource
from app.services.legal_source_inventory import build_legal_source_inventory


def _source(
    title: str,
    *,
    status: str = "active",
    official_status: str = "official",
    next_check_due_at: datetime | None = None,
) -> LegalSource:
    return LegalSource(
        document_type="law",
        title=title,
        document_number=f"NO-{title}",
        source_name="LEX.UZ",
        source_url=f"https://lex.uz/{title}",
        adoption_date="2026-01-01",
        revision_date="2026-06-01",
        last_checked_at=datetime(2026, 6, 1),
        next_check_due_at=next_check_due_at,
        language="ru",
        status=status,
        official_status=official_status,
        storage_key=f"legal/{title}.txt",
    )


async def _inventory_for(sources: list[LegalSource], **kwargs):
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
            session.add_all(sources)
            await session.commit()
            return await build_legal_source_inventory(session, **kwargs)
    finally:
        await engine.dispose()


def test_inventory_contains_only_active_official_source_metadata() -> None:
    as_of = datetime(2026, 7, 2)
    items = asyncio.run(
        _inventory_for(
            [
                _source("active-official", next_check_due_at=as_of + timedelta(days=1)),
                _source("draft", status="draft", next_check_due_at=as_of + timedelta(days=1)),
                _source("outdated", status="outdated", next_check_due_at=as_of + timedelta(days=1)),
                _source("archived", status="archived", next_check_due_at=as_of + timedelta(days=1)),
                _source("unofficial", official_status="non_official", next_check_due_at=as_of + timedelta(days=1)),
                _source("unknown", official_status="unknown", next_check_due_at=as_of + timedelta(days=1)),
            ],
            as_of=as_of,
        )
    )

    assert [item.title for item in items] == ["active-official"]
    assert set(items[0].model_dump()) == {
        "legal_source_id",
        "title",
        "document_type",
        "document_number",
        "adoption_date",
        "revision_date",
        "language",
        "status",
        "official_status",
        "source_url",
        "last_checked_at",
        "next_check_due_at",
        "freshness_warning",
    }
    assert "storage_key" not in items[0].model_dump()
    assert "chunks" not in items[0].model_dump()


def test_inventory_order_limit_and_freshness_are_deterministic() -> None:
    as_of = datetime(2026, 7, 2, 12)
    items = asyncio.run(
        _inventory_for(
            [
                _source("first", next_check_due_at=as_of + timedelta(seconds=1)),
                _source("second", next_check_due_at=as_of),
                _source("third", next_check_due_at=None),
                _source("fourth", next_check_due_at=as_of - timedelta(seconds=1)),
            ],
            limit=4,
            as_of=as_of,
        )
    )

    assert [item.title for item in items] == ["first", "second", "third", "fourth"]
    assert [item.freshness_warning for item in items] == [False, False, False, True]


def test_inventory_clamps_explicit_limit_to_200() -> None:
    as_of = datetime(2026, 7, 2)
    items = asyncio.run(
        _inventory_for(
            [
                _source(f"source-{index:03d}", next_check_due_at=as_of + timedelta(days=1))
                for index in range(201)
            ],
            limit=500,
            as_of=as_of,
        )
    )

    assert len(items) == 200
    assert items[0].legal_source_id == 1
    assert items[-1].legal_source_id == 200


def test_inventory_uses_configured_default_limit(monkeypatch) -> None:
    monkeypatch.setattr(settings, "legal_source_inventory_limit", 1)

    items = asyncio.run(
        _inventory_for(
            [
                _source("first", next_check_due_at=datetime(2026, 8, 1)),
                _source("second", next_check_due_at=datetime(2026, 8, 1)),
            ],
            as_of=datetime(2026, 7, 2),
        )
    )

    assert [item.title for item in items] == ["first"]


def test_inventory_rejects_non_positive_limit() -> None:
    with pytest.raises(ValueError, match="must be positive"):
        asyncio.run(_inventory_for([], limit=0))
