from __future__ import annotations

from dataclasses import dataclass


TEMPLATE_DOCUMENTS = "template_documents"
LEGAL_QUESTIONS = "legal_questions"
DEFAULT_SECTION_CODE = "legal_other"


@dataclass(frozen=True, slots=True)
class SectionGroupDefinition:
    code: str
    ui_label: str


@dataclass(frozen=True, slots=True)
class SectionDefinition:
    code: str
    group: str
    ui_label: str
    description: str

    @property
    def is_template_group(self) -> bool:
        return self.group == TEMPLATE_DOCUMENTS

    @property
    def is_legal_group(self) -> bool:
        return self.group == LEGAL_QUESTIONS


SECTION_GROUPS = (
    SectionGroupDefinition(TEMPLATE_DOCUMENTS, "Шаблонные документы"),
    SectionGroupDefinition(LEGAL_QUESTIONS, "Юридические вопросы и заключения"),
)

SECTIONS = (
    SectionDefinition("template_letters", TEMPLATE_DOCUMENTS, "Письма", "Ordinary approved-template business letters."),
    SectionDefinition("template_contracts", TEMPLATE_DOCUMENTS, "Договоры по утверждённым шаблонам", "Contracts based on approved company forms."),
    SectionDefinition("template_certificates", TEMPLATE_DOCUMENTS, "Справки", "Approved certificate forms."),
    SectionDefinition("template_powers_of_attorney", TEMPLATE_DOCUMENTS, "Доверенности", "Approved power-of-attorney forms."),
    SectionDefinition("template_orders", TEMPLATE_DOCUMENTS, "Приказы", "Approved or simple internal order forms."),
    SectionDefinition("template_other", TEMPLATE_DOCUMENTS, "Прочие шаблонные документы", "Other documents covered by an approved template."),
    SectionDefinition("legal_contract_review", LEGAL_QUESTIONS, "Договоры и экспертиза контрактов", "Contract review, risks, amendments, and unapproved forms."),
    SectionDefinition("legal_debts", LEGAL_QUESTIONS, "Долги (дебиторы / кредиторы)", "Receivables, payables, claims, and collection."),
    SectionDefinition("legal_currency", LEGAL_QUESTIONS, "Валютное регулирование", "Currency operations and international settlements."),
    SectionDefinition("legal_tax", LEGAL_QUESTIONS, "Налоговые вопросы", "Taxes, audits, and tax consequences."),
    SectionDefinition("legal_government", LEGAL_QUESTIONS, "Государственные органы", "Government correspondence, inspections, and administrative risks."),
    SectionDefinition("legal_counterparties", LEGAL_QUESTIONS, "Контрагенты и переписка", "Counterparty claims, disputes, and legal correspondence."),
    SectionDefinition("legal_accounting", LEGAL_QUESTIONS, "Бухгалтерия", "Legal issues involving accounting documents and settlements."),
    SectionDefinition("legal_hr", LEGAL_QUESTIONS, "HR / Трудовое право", "Labor, discipline, liability, and risky HR documents."),
    SectionDefinition("legal_departments", LEGAL_QUESTIONS, "Прочие подразделения предприятия", "Legal questions from factory departments."),
    SectionDefinition("legal_court", LEGAL_QUESTIONS, "Судебные и досудебные дела", "Court, pre-trial, enforcement, and settlement matters."),
    SectionDefinition("legal_other", LEGAL_QUESTIONS, "Прочие юридические вопросы", "Fallback for other legal questions."),
)

_SECTIONS_BY_CODE = {section.code: section for section in SECTIONS}


def _alias_key(value: str) -> str:
    return " ".join(value.casefold().replace("ё", "е").split())


_ALIASES = {_alias_key(section.ui_label): section.code for section in SECTIONS}
_ALIASES.update(
    {
        _alias_key("Долги / претензии"): "legal_debts",
        _alias_key("Долги/претензии"): "legal_debts",
        _alias_key("Договоры"): "legal_contract_review",
        _alias_key("Контракты"): "legal_contract_review",
        _alias_key("Кадры"): "legal_hr",
        _alias_key("HR"): "legal_hr",
        _alias_key("HR / кадры"): "legal_hr",
        _alias_key("Снабжение"): "legal_departments",
        _alias_key("Общий юридический вопрос"): "legal_other",
        _alias_key("Прочие"): "legal_other",
        _alias_key("Судебные вопросы"): "legal_court",
        _alias_key("ГНИ"): "legal_tax",
        _alias_key("Прочие Гос"): "legal_government",
    }
)


def normalize_section_code(value: str | None) -> str:
    if value is None:
        return DEFAULT_SECTION_CODE
    stripped = value.strip()
    if stripped in _SECTIONS_BY_CODE:
        return stripped
    key = _alias_key(stripped)
    if key.startswith("общий юридический в"):
        return DEFAULT_SECTION_CODE
    return _ALIASES.get(key, DEFAULT_SECTION_CODE)


def get_section_definition(section_code_or_legacy_label: str | None) -> SectionDefinition:
    return _SECTIONS_BY_CODE[normalize_section_code(section_code_or_legacy_label)]


def get_section_group(section_code_or_legacy_label: str | None) -> str:
    return get_section_definition(section_code_or_legacy_label).group


def list_section_groups() -> tuple[SectionGroupDefinition, ...]:
    return SECTION_GROUPS


def list_sections() -> tuple[SectionDefinition, ...]:
    return SECTIONS


def is_template_section(section_code_or_legacy_label: str | None) -> bool:
    return get_section_definition(section_code_or_legacy_label).is_template_group


def is_legal_section(section_code_or_legacy_label: str | None) -> bool:
    return get_section_definition(section_code_or_legacy_label).is_legal_group
