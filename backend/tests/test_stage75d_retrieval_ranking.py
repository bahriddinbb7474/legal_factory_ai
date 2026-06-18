import asyncio
from dataclasses import dataclass

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.db.base import Base, LegalChunk, LegalSource
from app.services.legal_retriever import legal_retriever
from app.services.legal_source_search_metadata import get_source_search_aliases


@dataclass(frozen=True)
class SourceFixture:
    title: str
    document_number: str
    status: str = "active"
    official_status: str = "official"


def test_curated_search_metadata_returns_known_alias_and_empty_for_unknown_source() -> None:
    assert get_source_search_aliases(SourceFixture(title="Personal data", document_number="  ZRU-547  ")) == (
        "персональные данные",
    )
    assert get_source_search_aliases(SourceFixture(title="Unknown", document_number="UNKNOWN")) == ()


async def _retrieve(query: str, sources: list[SourceFixture]):
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    try:
        async with session_factory() as session:
            for source_index, fixture in enumerate(sources):
                source = LegalSource(
                    document_type="law",
                    title=fixture.title,
                    document_number=fixture.document_number,
                    source_name="LEX.UZ",
                    source_url=f"https://lex.uz/docs/{source_index}",
                    revision_date="2026-06-01",
                    language="ru",
                    status=fixture.status,
                    official_status=fixture.official_status,
                    storage_key=f"unused/{source_index}.txt",
                )
                session.add(source)
                await session.flush()
                chunk_texts = ["Профильная норма без слов поискового запроса."]
                if fixture.document_number == "GENERIC":
                    chunk_texts = [f"{query}. Общая норма {chunk_index}." for chunk_index in range(6)]
                for chunk_index, chunk_text in enumerate(chunk_texts):
                    session.add(
                        LegalChunk(
                            legal_source_id=source.id,
                            article_or_point=f"Статья {chunk_index + 1}",
                            chunk_index=chunk_index,
                            chunk_text=chunk_text,
                        )
                    )
            await session.commit()
            return await legal_retriever.retrieve(session, query, top_k=5)
    finally:
        await engine.dispose()


@pytest.mark.parametrize(
    ("query", "title", "document_number"),
    [
        ("персональные данные работника", "Law of Uzbekistan on Personal Data", "ZRU-547"),
        ("охрана труда на предприятии", "Law of Uzbekistan on Occupational Safety", "ZRU-410"),
        ("внешнеэкономическая деятельность", "Law of Uzbekistan on Foreign Economic Activity", "77-II"),
        ("валютное регулирование", "Law of Uzbekistan on Currency Regulation", "ZRU-573"),
        ("техническое регулирование", "Law of Uzbekistan on Technical Regulation", "ZRU-819"),
        ("сертификация продукции", "Law of Uzbekistan on Technical Regulation", "ZRU-819"),
    ],
)
def test_first_batch_metadata_aliases_rank_target_source_in_top_five(query: str, title: str, document_number: str) -> None:
    results = asyncio.run(
        _retrieve(
            query,
            [
                SourceFixture(title="Generic active code", document_number="GENERIC"),
                SourceFixture(title=title, document_number=document_number),
            ],
        )
    )

    target_rank = next(index for index, result in enumerate(results, start=1) if result.document_number == document_number)

    assert target_rank <= 5
    assert all(result.document_number != "GENERIC" for result in results[:target_rank])


def test_future_pp4348_stays_excluded_despite_number_and_metadata_match() -> None:
    results = asyncio.run(
        _retrieve(
            "ПП-4348 таможенная пошлина сырье",
            [
                SourceFixture(
                    title="PQ-4348 future electrical industry resolution",
                    document_number="ПП-4348",
                    status="draft",
                )
            ],
        )
    )

    assert results == []


def test_outdated_zru354_stays_excluded_despite_number_and_metadata_match() -> None:
    results = asyncio.run(
        _retrieve(
            "ЗРУ-354 оценка соответствия",
            [
                SourceFixture(
                    title="Закон Республики Узбекистан Об оценке соответствия",
                    document_number="ЗРУ-354",
                    status="outdated",
                )
            ],
        )
    )

    assert results == []
