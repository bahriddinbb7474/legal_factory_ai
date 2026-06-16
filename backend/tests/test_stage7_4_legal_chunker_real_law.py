import asyncio

from app.schemas.legal_response import LegalStructuredResponse, LegalSource
from app.services.citation_verifier import citation_verifier
from app.services.legal_chunker import HARD_MAX_CHUNK_CHARS, legal_chunker
from app.services.legal_retriever import RetrievedLegalChunk


ARTICLE_1 = "\u0421\u0442\u0430\u0442\u044c\u044f 1"
ARTICLE_2 = "\u0421\u0442\u0430\u0442\u044c\u044f 2"
APPENDIX_1 = "\u041f\u0420\u0418\u041b\u041e\u0416\u0415\u041d\u0418\u0415 \u2116 1"
APPENDIX_2 = "\u041f\u0420\u0418\u041b\u041e\u0416\u0415\u041d\u0418\u0415 \u2116 2"
LETTER_A = "\u0430)"
LETTER_B = "\u0431)"
UZ_BAND = "1-\u0431\u0430\u043d\u0434"
UZ_ANNEX = "\u0418\u043b\u043e\u0432\u0430"


def _assert_ordered_indexes(chunks) -> None:
    assert [chunk.chunk_index for chunk in chunks] == list(range(len(chunks)))


def _max_chunk_size(chunks) -> int:
    return max(len(chunk.chunk_text) for chunk in chunks)


def test_presidential_resolution_plain_numbered_clauses_split_into_points() -> None:
    text = "\n\n".join(
        [
            "Presidential resolution title",
            "1. First point regulates cable export contracts.",
            "2. Second point assigns responsible factory departments.",
            "3. Third point requires monthly legal monitoring.",
        ]
    )

    chunks = legal_chunker.chunk(text)

    assert len(chunks) == 3
    _assert_ordered_indexes(chunks)
    assert [chunk.article_or_point for chunk in chunks] == ["Point 1", "Point 2", "Point 3"]
    assert _max_chunk_size(chunks) <= HARD_MAX_CHUNK_CHARS


def test_nested_numbered_clauses_and_letter_subparagraphs_are_meaningful_chunks() -> None:
    phrase = "exact phrase for later retrieval"
    text = "\n".join(
        [
            "1. Main clause introduces factory duties.",
            "1.1. Nested clause contains the exact phrase for later retrieval.",
            f"{LETTER_A} Letter subparagraph sets a reporting deadline.",
            f"{LETTER_B} Letter subparagraph requires legal approval.",
        ]
    )

    chunks = legal_chunker.chunk(text)

    assert len(chunks) == 4
    assert chunks[1].article_or_point == "Subpoint 1.1"
    assert chunks[2].article_or_point == f"Subpoint {LETTER_A}"
    assert any(phrase in chunk.chunk_text for chunk in chunks)
    assert _max_chunk_size(chunks) <= HARD_MAX_CHUNK_CHARS


def test_annex_headings_create_bounded_chunks() -> None:
    text = "\n\n".join(
        [
            f"{APPENDIX_1}\nPassport table for cable production localization.",
            f"{APPENDIX_2}\nSchedule table for investment obligations.",
        ]
    )

    chunks = legal_chunker.chunk(text)

    assert len(chunks) == 2
    assert chunks[0].article_or_point == APPENDIX_1
    assert chunks[1].article_or_point == APPENDIX_2
    assert _max_chunk_size(chunks) <= HARD_MAX_CHUNK_CHARS


def test_huge_unstructured_text_uses_size_fallback_without_losing_phrase() -> None:
    phrase = "middle exact compliance phrase"
    text = f"{'alpha ' * 1400}{phrase}. {'omega ' * 1400}"

    chunks = legal_chunker.chunk(text)

    assert len(chunks) > 1
    assert _max_chunk_size(chunks) <= HARD_MAX_CHUNK_CHARS
    assert any(phrase in chunk.chunk_text for chunk in chunks)
    assert {chunk.metadata_json["chunking"] for chunk in chunks} == {"fallback_size_split"}


def test_existing_article_chunking_is_preserved() -> None:
    text = "\n\n".join(
        [
            f"{ARTICLE_1}. Cable supply is regulated by contract.",
            f"{ARTICLE_2}. Delivery terms are fixed in writing.",
        ]
    )

    chunks = legal_chunker.chunk(text)

    assert len(chunks) == 2
    assert chunks[0].article_or_point == ARTICLE_1
    assert chunks[1].article_or_point == ARTICLE_2


def test_uzbek_heading_support_for_band_and_annex() -> None:
    text = "\n\n".join(
        [
            f"{UZ_BAND}. Korxona eksport shartnomasini tekshiradi.",
            f"{UZ_ANNEX} 1\nInvestitsiya majburiyatlari ro'yxati.",
        ]
    )

    chunks = legal_chunker.chunk(text)

    assert len(chunks) == 2
    assert chunks[0].article_or_point == UZ_BAND
    assert chunks[1].article_or_point == f"{UZ_ANNEX} 1"


def test_lexuz_date_lines_are_not_treated_as_nested_subpoints() -> None:
    text = "\n".join(
        [
            "30.05.2019 yildagi PQ-4348-son",
            "01.07.2026 sanasi holatiga",
            "1. Real clause starts here.",
            "2. Another real clause starts here.",
        ]
    )

    chunks = legal_chunker.chunk(text)

    assert [chunk.article_or_point for chunk in chunks] == ["Point 1", "Point 2"]


def test_pp_like_long_document_no_huge_chunk_and_citation_rules_still_work() -> None:
    exact_quote = "Factory legal team must verify export insurance terms before approval."
    sections = ["PQ-like synthetic title"]
    for index in range(1, 9):
        body = " ".join([f"section {index} operational text"] * 120)
        if index == 7:
            body = f"{body} {exact_quote}"
        sections.append(f"{index}. {body}")
    text = "\n\n".join(sections)

    chunks = legal_chunker.chunk(text)

    assert len(chunks) > 5
    assert _max_chunk_size(chunks) <= HARD_MAX_CHUNK_CHARS
    assert any(exact_quote in chunk.chunk_text for chunk in chunks)
    target = next(chunk for chunk in chunks if exact_quote in chunk.chunk_text)
    assert target.article_or_point == "Point 7"

    retrieved = RetrievedLegalChunk(
        legal_source_id=77,
        legal_chunk_id=target.chunk_index + 1,
        chunk_text=target.chunk_text,
        title="Synthetic PP/PQ source",
        document_type="presidential_resolution",
        document_number="PP-TEST",
        revision_date="2026-07-01",
        article_or_point=target.article_or_point,
        source_url="https://lex.uz/synthetic",
        source_name="LEX.UZ",
        score=1.0,
        needs_revision_check=False,
    )
    payload = _payload(retrieved, exact_quote)
    verified = asyncio.run(citation_verifier.verify(payload, [], [retrieved]))
    wrong = asyncio.run(citation_verifier.verify(_payload(retrieved, f"{exact_quote} wrong tail"), [], [retrieved]))

    assert verified.source_check_status == "confirmed"
    assert verified.confirmed_count == 1
    assert wrong.source_check_status == "unconfirmed"
    assert wrong.payload.risk == "yellow"
    assert wrong.payload.confidence == "medium"


def _payload(chunk: RetrievedLegalChunk, quote: str) -> LegalStructuredResponse:
    return LegalStructuredResponse(
        summary="Synthetic check",
        risk="green",
        findings=[],
        sources=[
            LegalSource(
                source_type="law",
                legal_source_id=chunk.legal_source_id,
                title=chunk.title,
                document_type=chunk.document_type,
                document_number=chunk.document_number,
                revision_date=chunk.revision_date,
                article_or_point=chunk.article_or_point,
                source_name=chunk.source_name,
                source_url=chunk.source_url,
                quote=quote,
            )
        ],
        meaning_for_factory="Synthetic smoke only",
        actions=[],
        confidence="high",
        approval_required="none",
    )
