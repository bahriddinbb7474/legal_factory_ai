import re
import unicodedata
from collections.abc import Iterable, Sequence

from app.schemas.legal_sources import LegalSourceInventoryItem
from app.schemas.rag import CanonicalRagRequest, RAG_EXCLUDE, RAG_MUST_HAVE, RagPlanningResult
from app.services.legal_triggers import detect_legal_triggers
from app.services.section_policy import LEGAL_QUESTIONS, TEMPLATE_DOCUMENTS, get_section_group, normalize_section_code


RAG_HISTORY_MESSAGE_LIMIT = 3
RAG_HISTORY_MESSAGE_CHAR_LIMIT = 500
RAG_RETRIEVAL_QUESTION_CHAR_LIMIT = 2000

SECTION_TOPICS = {
    "legal_contract_review": ("contract",),
    "legal_debts": ("debt", "claim"),
    "legal_currency": ("customs_import",),
    "legal_tax": ("tax",),
    "legal_government": ("government_authority",),
    "legal_counterparties": ("claim", "contract"),
    "legal_accounting": ("debt",),
    "legal_hr": ("hr_labor",),
    "legal_court": ("court", "claim"),
}


class RagRequestValidationError(ValueError):
    pass


class DeterministicRagPlanner:
    def plan(
        self,
        *,
        latest_user_message: str,
        recent_chat_messages: Sequence[str],
        section_code: str,
        section_group: str,
        source_inventory: Sequence[LegalSourceInventoryItem],
        uploaded_document_ids: Iterable[int] = (),
    ) -> RagPlanningResult:
        normalized_section = normalize_section_code(section_code)
        resolved_group = get_section_group(normalized_section)
        if section_group != resolved_group:
            raise RagRequestValidationError("section group does not match the canonical section")

        latest_message = _compact_text(latest_user_message)
        bounded_history = _bounded_history(recent_chat_messages)
        trigger_detection = detect_legal_triggers("\n".join([*bounded_history, latest_message]))
        clarification_needed = resolved_group == LEGAL_QUESTIONS and _needs_focused_clarification(latest_message)
        requires_legal_review = resolved_group == TEMPLATE_DOCUMENTS and trigger_detection.has_legal_trigger

        if requires_legal_review:
            needs_rag = True
            reason = "controlled_legal_handling_required"
        elif resolved_group == TEMPLATE_DOCUMENTS:
            needs_rag = False
            reason = "approved_template_path"
        elif clarification_needed and not trigger_detection.has_legal_trigger:
            needs_rag = False
            reason = "focused_clarification_needed"
        elif trigger_detection.has_legal_trigger:
            needs_rag = True
            reason = "legal_trigger_requires_rag"
        else:
            needs_rag = True
            reason = "legal_section_requires_rag"

        topics = _merge_topics(trigger_detection.matched_families, SECTION_TOPICS.get(normalized_section, ()))
        request = CanonicalRagRequest(
            needs_rag=needs_rag,
            reason=reason,
            source_scope=[],
            topics=topics,
            must_have=list(RAG_MUST_HAVE),
            exclude=list(RAG_EXCLUDE),
            question_for_retrieval=(
                _build_retrieval_question(latest_message, bounded_history) if needs_rag else ""
            ),
        )
        validate_canonical_rag_request(
            request,
            source_inventory=source_inventory,
            section_group=resolved_group,
            has_legal_trigger=trigger_detection.has_legal_trigger,
            clarification_needed=clarification_needed,
            approved_template_path=resolved_group == TEMPLATE_DOCUMENTS and not requires_legal_review,
            uploaded_document_ids=uploaded_document_ids,
        )
        return RagPlanningResult(
            request=request,
            trigger_detection=trigger_detection,
            requires_legal_review=requires_legal_review,
            clarification_needed=clarification_needed,
            section_code=normalized_section,
            section_group=resolved_group,
        )


def validate_canonical_rag_request(
    request: CanonicalRagRequest,
    *,
    source_inventory: Sequence[LegalSourceInventoryItem],
    section_group: str,
    has_legal_trigger: bool,
    clarification_needed: bool = False,
    approved_template_path: bool = False,
    uploaded_document_ids: Iterable[int] = (),
) -> None:
    if tuple(request.must_have) != RAG_MUST_HAVE:
        raise RagRequestValidationError("must_have must be backend-owned active and official invariants")
    if tuple(request.exclude) != RAG_EXCLUDE:
        raise RagRequestValidationError("exclude must be backend-owned policy invariants")

    inventory_ids = {item.legal_source_id for item in source_inventory}
    scope_ids = set(request.source_scope)
    uploaded_ids = set(uploaded_document_ids)
    if scope_ids & uploaded_ids:
        raise RagRequestValidationError("uploaded documents cannot enter legal source_scope")
    if not scope_ids <= inventory_ids:
        raise RagRequestValidationError("source_scope contains an id outside the current inventory")
    if len(scope_ids) != len(request.source_scope):
        raise RagRequestValidationError("source_scope must contain unique legal source ids")

    allowed_without_rag = clarification_needed or (
        section_group == TEMPLATE_DOCUMENTS and approved_template_path and not has_legal_trigger
    )
    if not request.needs_rag and not allowed_without_rag:
        raise RagRequestValidationError("needs_rag=false is not allowed for this legal path")
    if has_legal_trigger and not request.needs_rag:
        raise RagRequestValidationError("a legal trigger cannot disable mandatory RAG")
    if request.needs_rag and not request.question_for_retrieval.strip():
        raise RagRequestValidationError("a RAG request requires question_for_retrieval")
    if not request.needs_rag and request.question_for_retrieval:
        raise RagRequestValidationError("a non-RAG path cannot carry a retrieval question")


def _bounded_history(messages: Sequence[str]) -> list[str]:
    compact = [_compact_text(message)[:RAG_HISTORY_MESSAGE_CHAR_LIMIT] for message in messages]
    return [message for message in compact if message][-RAG_HISTORY_MESSAGE_LIMIT:]


def _build_retrieval_question(latest_message: str, bounded_history: Sequence[str]) -> str:
    parts = [f"Current question: {latest_message}"]
    parts.extend(f"Previous user context: {message}" for message in bounded_history if message != latest_message)
    return "\n".join(parts)[:RAG_RETRIEVAL_QUESTION_CHAR_LIMIT]


def _merge_topics(*topic_groups: Sequence[str]) -> list[str]:
    topics: list[str] = []
    for group in topic_groups:
        for topic in group:
            if topic not in topics:
                topics.append(topic)
    return topics


def _needs_focused_clarification(message: str) -> bool:
    normalized = message.casefold().strip(" .!?,-")
    return len(normalized) < 3 or normalized in {"да", "нет", "ок", "что", "как", "понятно"}


def _compact_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKC", value)
    return re.sub(r"\s+", " ", normalized).strip()


deterministic_rag_planner = DeterministicRagPlanner()
