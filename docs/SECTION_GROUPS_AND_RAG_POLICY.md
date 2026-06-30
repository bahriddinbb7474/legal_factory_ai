# Section Groups and RAG Policy

Date: 2026-06-30

## Purpose and Status

This document fixes the approved section structure for Legal Factory AI and is the normative section-routing specification for P3. It documents policy only; it does not describe already implemented runtime behavior.

Visible names may be adjusted later without changing policy. Runtime routing must use stable internal group and section codes, never raw UI labels.

## Approved Functional Groups

| Internal group code | UI group name | Product role | Default workflow |
| --- | --- | --- | --- |
| `template_documents` | `Шаблонные документы` | AI-Секретарь / шаблонный документооборот | Approved template or form; no RAG or verdict by default |
| `legal_questions` | `Юридические вопросы и заключения` | AI-Юрист / юридический анализ | Legal analysis, targeted RAG, multi-lawyer review, and eligible verdict |

The alternative visible label `Шаблоны / Канцелярия` is acceptable for `template_documents`. It is not a policy key.

## Group 1 — Шаблонные документы

This group is for ordinary document drafting from approved company templates and forms.

### Approved sections and proposed stable codes

| Internal section code | UI section name | Scope |
| --- | --- | --- |
| `template_letters` | `Письма` | Ordinary bank, supplier, buyer, cover, details-request, and other business letters that do not require legal verification |
| `template_contracts` | `Договоры по утверждённым шаблонам` | Only approved forms, including cable, raw-material, inventory, fixed-asset, vehicle-sale, and approved loan agreements |
| `template_certificates` | `Справки` | Approved employee, notary, place-of-demand, residual-value, and similar certificates |
| `template_powers_of_attorney` | `Доверенности` | Approved annual, one-time, vehicle, goods-receipt, customs, and representation powers of attorney |
| `template_orders` | `Приказы` | Approved or simple internal order forms, including approved HR and organizational forms |
| `template_other` | `Прочие шаблонные документы` | Other documents strictly covered by an approved template |

The codes above are the recommended P3-A canonical codes. P3-A must confirm them in one backend-owned mapping before runtime use.

### Group 1 policy

- RAG is not required by default.
- Verdict mode and legal conclusions are not available.
- Source citations are not required for an ordinary approved-template operation.
- Documents are not generated from a verdict; they are created only from approved templates or forms.
- If no approved template exists, the system must not create a final document.
- A contract without an approved template routes to `legal_contract_review`.
- A request for legal or normative verification routes to `legal_questions`.
- A risky order involving dismissal, disciplinary action, financial liability, a dispute, or another red topic cannot remain a simple template operation.
- Red-topic detection and approval policy apply in every section and override the group default.

## Group 2 — Юридические вопросы и заключения

This group is for legal analysis, legal opinions, targeted RAG, criticism or review by multiple lawyers, and eligible verdicts.

### Approved sections and proposed stable codes

| Internal section code | UI section name | Scope |
| --- | --- | --- |
| `legal_contract_review` | `Договоры и экспертиза контрактов` | Contract review, risks, amendments, disputed clauses, legal opinions, and contracts without an approved form |
| `legal_debts` | `Долги (дебиторы / кредиторы)` | Receivables, payables, overdue payment, claims, collection, and acknowledgement of debt |
| `legal_currency` | `Валютное регулирование` | Currency operations, foreign-trade payments, repatriation periods, currency control, and international settlements |
| `legal_tax` | `Налоговые вопросы` | Taxes, audits, tax consequences, VAT, profit tax, withholding, and tax authorities |
| `legal_government` | `Государственные органы` | Letters and replies to authorities, inspections, demands, prescriptions, and administrative risks |
| `legal_counterparties` | `Контрагенты и переписка` | Counterparty demands and claims, disputed correspondence, legal replies, and negotiation positions |
| `legal_accounting` | `Бухгалтерия` | Legal issues involving primary documents, acts, invoices, settlements, write-offs, and financial-legal consequences |
| `legal_hr` | `HR / Трудовое право` | Dismissal, discipline, financial liability, explanations, labor disputes, and risky HR documents |
| `legal_departments` | `Прочие подразделения предприятия` | Legal questions from production, warehouse, supply, sales, or technical teams that fit no narrower section |
| `legal_court` | `Судебные и досудебные дела` | Court, pre-trial claims, enforcement, settlement agreements, court documents, and post-judgment actions |
| `legal_other` | `Прочие юридические вопросы` | Safe fallback for legal questions that fit no other legal section |

### Group 2 policy

- Lawyer 1 requests targeted RAG by default unless focused clarification is needed first.
- Pre-verdict answers are normal human-readable text.
- Only Lawyer 2 or Lawyer 3 may issue a verdict, after explicit user permission and required checks.
- Structured legal payload is reserved for verdict mode.
- `confirmed_in_context`, `source_check_status`, `document_generation_allowed`, and `approval_required` remain backend-controlled.
- Red topics force approval in every legal section.
- If a required official source is missing, no final proven legal conclusion may be presented.
- Document generation from verdict remains blocked until source verification and the P5 gate are implemented and pass.

## Routing and Override Rules

1. The backend resolves `section_code` to `section_group`; the frontend label is display-only.
2. Existing free-text `Chat.section` values must be mapped through an explicit alias/migration table. Unknown or ambiguous legal values must fall back safely to `legal_other`; they must not silently enter the template path.
3. An ordinary approved-template request stays in `template_documents`.
4. A missing template, legal-verification request, legal dispute, or unapproved contract routes to `legal_questions`.
5. Red-topic detection overrides both group defaults and forces the applicable approval workflow.
6. Group routing must not weaken user-role, source-trust, verdict, or document-generation gates.

## P3 Implementation Plan — Section Groups and RAG Policy Routing

### P3-A — Canonical section model

- Define stable internal section codes and a backend-owned mapping to `template_documents` or `legal_questions`.
- Keep visible UI names separate from internal codes.
- Map existing free-text `Chat.section` values safely through explicit aliases or migration logic.
- Define a safe fallback for unknown values and preserve existing chat history.

### P3-B — Frontend section UI

- Show sections under the two approved visible groups.
- Send stable section codes to the backend rather than using labels as policy keys.
- Allow future visible-name changes without breaking routing or stored history.

### P3-C — Section policy routing

- Route `template_documents` to the approved-template/document flow.
- Route `legal_questions` to the legal-answer flow.
- Do not require RAG by default for ordinary Group 1 work.
- Require Lawyer 1 to request RAG by default for Group 2 unless clarification is needed first.
- Let red-topic detection override either group and force approval.

### P3-D — Safety tests

- An ordinary Group 1 letter does not require RAG.
- Group 1 cannot create a final document without an approved template.
- A Group 1 HR dismissal request cannot bypass legal policy.
- In Group 2, Lawyer 1 requests RAG or asks necessary clarifying questions.
- A Group 2 verdict requires Lawyer 2 or Lawyer 3 and explicit permission.
- Red-topic handling works in both groups.
- UI-label changes do not change policy routing for a stable section code.
