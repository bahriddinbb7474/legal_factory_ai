export type SectionCode =
  | "template_letters"
  | "template_contracts"
  | "template_certificates"
  | "template_powers_of_attorney"
  | "template_orders"
  | "template_other"
  | "legal_contract_review"
  | "legal_debts"
  | "legal_currency"
  | "legal_tax"
  | "legal_government"
  | "legal_counterparties"
  | "legal_accounting"
  | "legal_hr"
  | "legal_departments"
  | "legal_court"
  | "legal_other";

export type SectionDefinition = {
  code: SectionCode;
  label: string;
};

export type SectionGroup = {
  code: "template_documents" | "legal_questions";
  label: string;
  sections: readonly SectionDefinition[];
};

export const SECTION_GROUPS: readonly SectionGroup[] = [
  {
    code: "template_documents",
    label: "Шаблонные документы",
    sections: [
      { code: "template_letters", label: "Письма" },
      { code: "template_contracts", label: "Договоры" },
      { code: "template_certificates", label: "Справки" },
      { code: "template_powers_of_attorney", label: "Доверенности" },
      { code: "template_orders", label: "Приказы" },
      { code: "template_other", label: "Прочие документы" },
    ],
  },
  {
    code: "legal_questions",
    label: "Юридические вопросы и заключения",
    sections: [
      { code: "legal_contract_review", label: "Экспертиза контрактов" },
      { code: "legal_debts", label: "Долги (дебиторы / кредиторы)" },
      { code: "legal_currency", label: "Валютное регулирование" },
      { code: "legal_tax", label: "Налоговые вопросы" },
      { code: "legal_government", label: "Государственные органы" },
      { code: "legal_counterparties", label: "Контрагенты и переписка" },
      { code: "legal_accounting", label: "Бухгалтерия" },
      { code: "legal_hr", label: "HR / Трудовое право" },
      { code: "legal_departments", label: "Прочие внут.подразделения" },
      { code: "legal_court", label: "Судебные и досудебные дела" },
      { code: "legal_other", label: "Прочие юридические вопросы" },
    ],
  },
];

const SECTION_BY_CODE = new Map(
  SECTION_GROUPS.flatMap((group) => group.sections).map((section) => [section.code, section]),
);

function aliasKey(value: string): string {
  return value.toLocaleLowerCase("ru-RU").replace(/ё/g, "е").replace(/\s+/g, " ").trim();
}

const LEGACY_SECTION_ALIASES = new Map<string, SectionCode>([
  ...SECTION_GROUPS.flatMap((group) =>
    group.sections.map((section) => [aliasKey(section.label), section.code] as [string, SectionCode]),
  ),
  [aliasKey("Долги / претензии"), "legal_debts"],
  [aliasKey("Долги/претензии"), "legal_debts"],
  [aliasKey("Договоры"), "legal_contract_review"],
  [aliasKey("Контракты"), "legal_contract_review"],
  [aliasKey("Кадры"), "legal_hr"],
  [aliasKey("HR"), "legal_hr"],
  [aliasKey("HR / кадры"), "legal_hr"],
  [aliasKey("Снабжение"), "legal_departments"],
  [aliasKey("Общий юридический вопрос"), "legal_other"],
  [aliasKey("Прочие"), "legal_other"],
  [aliasKey("Судебные вопросы"), "legal_court"],
  [aliasKey("ГНИ"), "legal_tax"],
  [aliasKey("Прочие Гос"), "legal_government"],
  [aliasKey("Договоры по утверждённым шаблонам"), "template_contracts"],
  [aliasKey("Прочие шаблонные документы"), "template_other"],
  [aliasKey("Договоры и экспертиза контрактов"), "legal_contract_review"],
  [aliasKey("Прочие подразделения предприятия"), "legal_departments"],
]);

export function normalizeSectionCode(value?: string | null): SectionCode {
  if (value && SECTION_BY_CODE.has(value as SectionCode)) {
    return value as SectionCode;
  }
  const key = aliasKey(value ?? "");
  if (key.startsWith("общий юридический в")) {
    return "legal_other";
  }
  return LEGACY_SECTION_ALIASES.get(key) ?? "legal_other";
}

export function sectionLabel(value?: string | null): string {
  return SECTION_BY_CODE.get(normalizeSectionCode(value))?.label ?? "Прочие юридические вопросы";
}
