from datetime import datetime

import pytest

from app.schemas.legal_sources import LegalSourceInventoryItem
from app.schemas.rag import CanonicalRagRequest, RAG_EXCLUDE, RAG_MUST_HAVE
from app.services.legal_triggers import LegalTriggerPattern, detect_legal_triggers
from app.services.rag_planner import (
    RagRequestValidationError,
    deterministic_rag_planner,
    validate_canonical_rag_request,
)
from app.services.section_policy import LEGAL_QUESTIONS, TEMPLATE_DOCUMENTS


def _inventory_item(source_id: int = 1) -> LegalSourceInventoryItem:
    return LegalSourceInventoryItem(
        legal_source_id=source_id,
        title=f"Official source {source_id}",
        document_type="law",
        document_number=f"NO-{source_id}",
        adoption_date="2026-01-01",
        revision_date="2026-06-01",
        language="ru",
        status="active",
        official_status="official",
        source_url=f"https://lex.uz/{source_id}",
        last_checked_at=datetime(2026, 6, 1),
        next_check_due_at=datetime(2026, 7, 15),
        freshness_warning=False,
    )


@pytest.mark.parametrize(
    ("text", "families"),
    [
        ("Налоговый штраф при увольнении и претензия", {"tax", "fine", "dismissal", "claim"}),
        ("Soliq, jarima, ishdan bo'shatish, shartnoma va da'vo", {"tax", "fine", "dismissal", "contract", "claim"}),
        ("Солиқ, жарима, ишдан бўшатиш, шартнома ва даъво", {"tax", "fine", "dismissal", "contract", "claim"}),
    ],
)
def test_multilingual_trigger_families_are_detected(text: str, families: set[str]) -> None:
    detection = detect_legal_triggers(text)

    assert detection.has_legal_trigger is True
    assert families <= set(detection.matched_families)
    assert detection.matched_patterns


def test_trigger_foundation_accepts_configured_patterns() -> None:
    detection = detect_legal_triggers(
        "special legal marker",
        patterns=(LegalTriggerPattern("custom_family", "test:marker", r"\blegal marker\b"),),
    )

    assert detection.matched_families == ["custom_family"]
    assert detection.matched_patterns == ["test:marker"]


@pytest.mark.parametrize(
    ("text", "family"),
    [
        ("Обращение в суд и государственный орган", "court"),
        ("Qarz bo'yicha bojxona va import masalasi", "debt"),
        ("Қарз ва божхона масаласи", "customs_import"),
        ("Проверить трудовые права", "hr_labor"),
    ],
)
def test_remaining_required_trigger_families_are_covered(text: str, family: str) -> None:
    assert family in detect_legal_triggers(text).matched_families


def test_legal_trigger_builds_canonical_deterministic_request_with_bounded_history() -> None:
    inputs = {
        "latest_user_message": "Какие налоговые последствия у договора?",
        "recent_chat_messages": [
            "old-1 must be excluded",
            "old-2 must be excluded",
            "Поставка оборудования",
            "Контрагент просит изменить цену",
            "Оплата после приемки",
        ],
        "section_code": "legal_tax",
        "section_group": LEGAL_QUESTIONS,
        "source_inventory": [_inventory_item()],
    }

    first = deterministic_rag_planner.plan(**inputs)
    second = deterministic_rag_planner.plan(**inputs)

    assert first.model_dump() == second.model_dump()
    assert first.request.needs_rag is True
    assert first.request.reason == "legal_trigger_requires_rag"
    assert first.request.must_have == ["active", "official"]
    assert first.request.exclude == ["outdated", "foreign_law", "untrusted_without_confirmation"]
    assert first.request.source_scope == []
    assert "tax" in first.request.topics
    assert "Поставка оборудования" in first.request.question_for_retrieval
    assert "old-1" not in first.request.question_for_retrieval
    assert first.trigger_detection.has_legal_trigger is True


def test_legal_section_without_trigger_still_requires_rag_from_section_policy() -> None:
    result = deterministic_rag_planner.plan(
        latest_user_message="Проверьте возможные риски этой ситуации",
        recent_chat_messages=[],
        section_code="legal_court",
        section_group=LEGAL_QUESTIONS,
        source_inventory=[_inventory_item()],
    )

    assert result.request.needs_rag is True
    assert result.request.reason == "legal_section_requires_rag"
    assert result.request.topics == ["court", "claim"]


def test_simple_template_path_skips_default_rag() -> None:
    result = deterministic_rag_planner.plan(
        latest_user_message="Подготовь обычное сопроводительное письмо поставщику",
        recent_chat_messages=[],
        section_code="template_letters",
        section_group=TEMPLATE_DOCUMENTS,
        source_inventory=[_inventory_item()],
    )

    assert result.request.needs_rag is False
    assert result.request.reason == "approved_template_path"
    assert result.request.question_for_retrieval == ""
    assert result.requires_legal_review is False
    assert result.section_code == "template_letters"


def test_template_legal_trigger_requires_controlled_review_without_section_mutation() -> None:
    result = deterministic_rag_planner.plan(
        latest_user_message="Подготовь письмо об увольнении и штрафе",
        recent_chat_messages=[],
        section_code="template_letters",
        section_group=TEMPLATE_DOCUMENTS,
        source_inventory=[_inventory_item()],
    )

    assert result.request.needs_rag is True
    assert result.request.reason == "controlled_legal_handling_required"
    assert result.requires_legal_review is True
    assert result.section_code == "template_letters"
    assert result.section_group == TEMPLATE_DOCUMENTS
    assert {"dismissal", "fine"} <= set(result.request.topics)


def test_short_legal_message_uses_focused_clarification_path() -> None:
    result = deterministic_rag_planner.plan(
        latest_user_message="ок",
        recent_chat_messages=[],
        section_code="legal_other",
        section_group=LEGAL_QUESTIONS,
        source_inventory=[_inventory_item()],
    )

    assert result.request.needs_rag is False
    assert result.request.reason == "focused_clarification_needed"
    assert result.clarification_needed is True


def test_validation_rejects_weakened_backend_invariants() -> None:
    inventory = [_inventory_item()]
    missing_official = CanonicalRagRequest(
        needs_rag=True,
        reason="unsafe",
        must_have=["active"],
        exclude=list(RAG_EXCLUDE),
        question_for_retrieval="tax",
    )
    missing_foreign_exclusion = CanonicalRagRequest(
        needs_rag=True,
        reason="unsafe",
        must_have=list(RAG_MUST_HAVE),
        exclude=["outdated", "untrusted_without_confirmation"],
        question_for_retrieval="tax",
    )

    with pytest.raises(RagRequestValidationError, match="must_have"):
        _validate(missing_official, inventory)
    with pytest.raises(RagRequestValidationError, match="exclude"):
        _validate(missing_foreign_exclusion, inventory)


def test_validation_rejects_source_ids_outside_inventory_and_uploaded_documents() -> None:
    inventory = [_inventory_item(1)]
    outside_inventory = _request(source_scope=[999])
    uploaded_as_law = _request(source_scope=[1])

    with pytest.raises(RagRequestValidationError, match="outside the current inventory"):
        _validate(outside_inventory, inventory)
    with pytest.raises(RagRequestValidationError, match="uploaded documents"):
        _validate(uploaded_as_law, inventory, uploaded_document_ids=[1])


def test_validation_rejects_needs_rag_false_for_legal_trigger() -> None:
    request = CanonicalRagRequest(
        needs_rag=False,
        reason="user_requested_no_rag",
        question_for_retrieval="",
    )

    with pytest.raises(RagRequestValidationError, match="not allowed|cannot disable"):
        validate_canonical_rag_request(
            request,
            source_inventory=[_inventory_item()],
            section_group=LEGAL_QUESTIONS,
            has_legal_trigger=True,
        )


def test_section_group_mismatch_is_rejected() -> None:
    with pytest.raises(RagRequestValidationError, match="section group"):
        deterministic_rag_planner.plan(
            latest_user_message="Налоговый вопрос",
            recent_chat_messages=[],
            section_code="legal_tax",
            section_group=TEMPLATE_DOCUMENTS,
            source_inventory=[_inventory_item()],
        )


def test_canonical_request_does_not_add_deferred_taxonomy_fields() -> None:
    assert set(CanonicalRagRequest.model_fields) == {
        "needs_rag",
        "reason",
        "source_scope",
        "topics",
        "must_have",
        "exclude",
        "question_for_retrieval",
    }
    assert {"jurisdiction", "category", "topic_hints", "future"}.isdisjoint(CanonicalRagRequest.model_fields)


def _request(*, source_scope: list[int]) -> CanonicalRagRequest:
    return CanonicalRagRequest(
        needs_rag=True,
        reason="legal_trigger_requires_rag",
        source_scope=source_scope,
        question_for_retrieval="tax",
    )


def _validate(
    request: CanonicalRagRequest,
    inventory: list[LegalSourceInventoryItem],
    *,
    uploaded_document_ids: list[int] | None = None,
) -> None:
    validate_canonical_rag_request(
        request,
        source_inventory=inventory,
        section_group=LEGAL_QUESTIONS,
        has_legal_trigger=True,
        uploaded_document_ids=uploaded_document_ids or [],
    )
