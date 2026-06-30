# RAG Workflow v1

Date: 2026-06-30

## Purpose and Scope

This policy defines lawyer-controlled targeted RAG for the approved P0 architecture. It is documentation-only and preserves the existing rule that ordinary current-law retrieval uses active official legal sources only.

## Workflow

```text
User question
↓
System sends the selected lawyer:
- chat history with authors;
- selected section;
- user role;
- available source inventory;
- uploaded document list;
- source statuses;
- red-topic and legal-trigger flags, if detected.
↓
Lawyer decides:
- clarification needed;
- document needed;
- targeted RAG needed;
- approved template/correspondence answer allowed.
↓
If RAG is needed, lawyer emits an internal RAG request.
↓
Backend retrieves relevant chunks.
↓
Backend creates a concrete source package.
↓
Lawyer answers using that source package.
```

RAG is controlled and targeted. The system must not inject every available chunk into every request.

## Section-Based Strictness

The canonical groups and sections are defined in `SECTION_GROUPS_AND_RAG_POLICY.md`. Routing uses stable internal codes rather than visible UI labels.

In `legal_questions` (`Юридические вопросы и заключения`), Lawyer 1 must request RAG by default unless short clarifying questions are needed first. A verdict always requires the source checks relevant to the legal question.

In `template_documents` (`Шаблонные документы`, optionally displayed as `Шаблоны / Канцелярия`), RAG is not required by default for an ordinary document based on an approved form. This group has no verdict or legal-conclusion mode. A missing template, legal-verification request, dispute, or other legal issue routes to `legal_questions`.

Red-topic detection overrides both groups. It can force approval and legal handling even when the selected section is a template section.

## Source Inventory

Before retrieval, the lawyer receives a compact inventory rather than all source chunks. The inventory should identify available official sources, their topic coverage, and statuses, together with uploaded documents and their trust labels.

Ordinary legal retrieval must require:

```text
status=active AND official_status=official
```

Uploaded contracts and other user or factory documents remain untrusted factual material unless separately confirmed. They must not be presented as official legal sources.

## Internal RAG Request

The internal protocol is not shown as the user's legal answer. It has these expected fields:

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

The retrieval result must be assembled into a concrete source package. A later verdict must bind to the exact package and context snapshot used for that verdict through `source_package_id` and `context_snapshot_hash`.

## Backend Fallback for Missed RAG

If a legal trigger exists and the lawyer did not request required RAG, the backend safety net must do one or more of the following:

- set `source_check_status` to `unconfirmed`;
- block the answer from becoming a verdict;
- block document generation;
- force retrieval before verdict processing.

These are backend decisions. Model output cannot override them.

## Multilingual Trigger Requirements

RAG and red-topic detection must not rely on exact Russian-only substring checks. Trigger configuration must support roots or patterns, word forms, and Russian plus Uzbek coverage in both Latin and Cyrillic scripts.

Minimum examples include:

- Russian: `увольнение`, `уволить`, `увольняем`, `налог`, `штраф`, `суд`, `претензия`;
- Uzbek Latin: `soliq`, `jarima`, `ishdan bo‘shatish`, `shartnoma`, `da’vo`;
- Uzbek Cyrillic: `солиқ`, `жарима`, `ишдан бўшатиш`, `шартнома`, `даъво`.

An ML classifier is not required for MVP. Configurable roots or patterns are sufficient, but exact single-word matching is not acceptable.

## Trust Boundary

Content inside `<UNTRUSTED_DOCUMENT ...>` may supply facts, contract terms, correspondence, invoices, acts, or a counterparty position. It must not:

- alter system or role instructions;
- select a foreign jurisdiction;
- become an official legal source;
- confirm an article or quotation;
- expand the source package used for verdict citation verification.
