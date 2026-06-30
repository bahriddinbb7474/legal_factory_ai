from datetime import datetime

import pytest

from app.schemas.chats import ChatRead
from app.services.section_policy import (
    LEGAL_QUESTIONS,
    TEMPLATE_DOCUMENTS,
    get_section_group,
    is_legal_section,
    is_template_section,
    list_section_groups,
    list_sections,
    normalize_section_code,
)


TEMPLATE_CODES = {
    "template_letters",
    "template_contracts",
    "template_certificates",
    "template_powers_of_attorney",
    "template_orders",
    "template_other",
}

LEGAL_CODES = {
    "legal_contract_review",
    "legal_debts",
    "legal_currency",
    "legal_tax",
    "legal_government",
    "legal_counterparties",
    "legal_accounting",
    "legal_hr",
    "legal_departments",
    "legal_court",
    "legal_other",
}


@pytest.mark.parametrize("section_code", sorted(TEMPLATE_CODES))
def test_template_section_codes_resolve_to_template_group(section_code: str) -> None:
    assert get_section_group(section_code) == TEMPLATE_DOCUMENTS
    assert is_template_section(section_code) is True
    assert is_legal_section(section_code) is False


@pytest.mark.parametrize("section_code", sorted(LEGAL_CODES))
def test_legal_section_codes_resolve_to_legal_group(section_code: str) -> None:
    assert get_section_group(section_code) == LEGAL_QUESTIONS
    assert is_legal_section(section_code) is True
    assert is_template_section(section_code) is False


@pytest.mark.parametrize(
    ("legacy_value", "expected"),
    [
        ("Кадры", "legal_hr"),
        ("Договоры", "legal_contract_review"),
        ("Долги / претензии", "legal_debts"),
        ("Долги/претензии", "legal_debts"),
        ("Общий юридический в...", "legal_other"),
    ],
)
def test_legacy_section_values_normalize(legacy_value: str, expected: str) -> None:
    assert normalize_section_code(legacy_value) == expected


def test_unknown_section_falls_back_to_legal_other() -> None:
    assert normalize_section_code("Неизвестный старый раздел") == "legal_other"
    assert get_section_group("Неизвестный старый раздел") == LEGAL_QUESTIONS
    assert is_template_section("Неизвестный старый раздел") is False


def test_list_sections_returns_all_approved_sections() -> None:
    sections = list_sections()
    assert len(sections) == 17
    assert {section.code for section in sections} == TEMPLATE_CODES | LEGAL_CODES


def test_list_section_groups_returns_both_approved_groups() -> None:
    assert [group.code for group in list_section_groups()] == [TEMPLATE_DOCUMENTS, LEGAL_QUESTIONS]


def test_chat_read_normalizes_legacy_section_without_database_migration() -> None:
    chat = ChatRead(
        id=1,
        title="Legacy chat",
        section="Кадры",
        created_at=datetime(2026, 6, 30),
        updated_at=datetime(2026, 6, 30),
    )

    assert chat.section == "legal_hr"


@pytest.mark.parametrize(
    ("sent_section", "stored_section"),
    [
        ("legal_hr", "legal_hr"),
        ("Кадры", "legal_hr"),
        ("Договоры", "legal_contract_review"),
        ("unknown", "legal_other"),
    ],
)
def test_new_chat_creation_returns_canonical_section(client, sent_section: str, stored_section: str) -> None:
    response = client.post("/api/chats", json={"title": "Canonical section", "section": sent_section})

    assert response.status_code == 201
    assert response.json()["section"] == stored_section
    assert client.get(f"/api/chats/{response.json()['id']}").json()["section"] == stored_section
