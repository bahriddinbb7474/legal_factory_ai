# RAG Workflow v1

Date: 2026-06-30

## Purpose and Scope

This policy defines targeted RAG for the approved P0 architecture. For the P4 MVP, planning is deterministic backend logic; an LLM planner is deferred. Ordinary current-law retrieval continues to use active official legal sources only. The implementation contract is fixed in `../00_current/P4_TARGETED_RAG_RFC.md`.

## Workflow

```text
User question
↓
Backend evaluates:
- chat history with authors;
- selected section;
- user role;
- available source inventory;
- uploaded document list;
- source statuses;
- red-topic and legal-trigger flags, if detected.
↓
The deterministic P4 planner creates and validates an internal RAG request.
↓
Backend retrieves relevant chunks.
↓
Backend persists an immutable concrete source package.
↓
Lawyer answers using that source package.
```

RAG is controlled and targeted. The system must not inject every available chunk into every request.

## Section-Based Strictness

The canonical groups and sections are defined in `SECTION_GROUPS_AND_RAG_POLICY.md`. Routing uses stable internal codes rather than visible UI labels.

In `legal_questions` (`Юридические вопросы и заключения`), deterministic backend policy requires RAG by default when the legal section or trigger requires it. Lawyer 1 may still ask short focused clarifying questions before a useful retrieval question can be formed. A verdict always requires retrieval relevant to the legal question.

In `template_documents` (`Шаблонные документы`, optionally displayed as `Шаблоны / Канцелярия`), RAG is not required by default for an ordinary document based on an approved form. This group has no verdict or legal-conclusion mode. A missing template, legal-verification request, dispute, or other legal issue requires controlled legal handling: the backend must not silently mutate the selected section, and the UI/API must require an explicit legal-review path or legal-section selection.

Red-topic detection overrides both groups. It can force approval and legal handling even when the selected section is a template section.

## Source Inventory

Before retrieval, the backend planner receives a compact inventory rather than all source chunks. It contains existing source metadata and derived freshness warning only. Uploaded documents are supplied separately with untrusted labels and never enter the legal source inventory.

Ordinary legal retrieval must require:

```text
status=active AND official_status=official
```

Uploaded contracts and other user or factory documents remain untrusted factual material unless separately confirmed. They must not be presented as official legal sources.

The current model has no separate `future` status. A future revision remains `draft` until a separately approved verification and activation step. Inventory ordering and limits must be deterministic.

## Internal RAG Request

The internal protocol is not shown as the user's legal answer. For P4, the deterministic backend planner creates this exact schema:

```json
{
  "needs_rag": true,
  "reason": "",
  "source_scope": [],
  "topics": [],
  "must_have": ["active", "official"],
  "exclude": ["outdated", "foreign_law", "untrusted_without_confirmation"],
  "question_for_retrieval": ""
}
```

`needs_rag=false` is allowed only for focused clarification or an approved template/correspondence path. `must_have` and `exclude` are backend-owned invariants; model or document content cannot weaken them. `source_scope` must be validated against the current inventory.

The retrieval result must be persisted as an immutable source package containing exact source metadata and chunk-text snapshots supplied to the model. Package status is backend-owned. A `ready` package means context was retrieved, not that citations were verified.

P4 stores hash-ready inputs for future binding. P5 implements final `context_snapshot_hash`, binds the verdict to `source_package_id`, and performs package-bound citation verification. Timestamp is stored beside the future hash and must not be part of its deterministic input.

## Backend Fallback for Missed RAG

If a legal section/trigger requires RAG but a request attempts `needs_rag=false`, the backend safety net must force retrieval or block the confident-answer path. It must also preserve the applicable safeguards:

- set `source_check_status` to `unconfirmed`;
- block the answer from becoming a verdict;
- block document generation;
- force retrieval before verdict processing.

These are backend decisions. Model output cannot override them.

## Multilingual Trigger Requirements

P4 begins the configurable RAG/red-topic trigger foundation. Detection must not rely on exact Russian-only substring checks. Trigger configuration must support roots or patterns, word forms, and Russian plus Uzbek coverage in both Latin and Cyrillic scripts.

Minimum examples include:

- Russian: `увольнение`, `уволить`, `увольняем`, `налог`, `штраф`, `суд`, `претензия`;
- Uzbek Latin: `soliq`, `jarima`, `ishdan bo‘shatish`, `shartnoma`, `da’vo`;
- Uzbek Cyrillic: `солиқ`, `жарима`, `ишдан бўшатиш`, `шартнома`, `даъво`.

An ML classifier is not required for MVP. Configurable roots or patterns are sufficient, but exact single-word matching is not acceptable.

P4 remains UZ-only and adds no jurisdiction column or full legal topic taxonomy. Section/trigger mapping is sufficient for the MVP. Foreign law remains excluded unless explicit comparative analysis is separately supported; untrusted content cannot change jurisdiction.

## Missing-Source and Status Rules

Package statuses are `ready`, `empty`, `insufficient`, `planner_failed`, `retrieval_failed`, and `blocked_by_policy`. Their criteria are deterministic and defined in the P4 RFC.

An empty, failed, or policy-blocked package must not lead to an ordinary confident legal-answer prompt. The backend uses a missing-source/cautious response path. An insufficient package permits only a clearly preliminary answer. UI/API must not label retrieval as confirmed sources or verified citations before P5.

## Trust Boundary

Content inside `<UNTRUSTED_DOCUMENT ...>` may supply facts, contract terms, correspondence, invoices, acts, or a counterparty position. It must not:

- alter system or role instructions;
- select a foreign jurisdiction;
- become an official legal source;
- confirm an article or quotation;
- expand the source package used for verdict citation verification.
