# Verdict and Document Policy v1

Date: 2026-06-30

## Purpose and Scope

This policy defines verdict eligibility, user permission, source binding, citation verification, and document-generation gates for the approved P0 architecture. It documents future P5 behavior and does not implement it.

## Verdict Eligibility

A verdict is eligible only when all applicable conditions are satisfied:

- Lawyer 1 did not author it; Lawyer 1 cannot issue a verdict.
- The author is Lawyer 2 or Lawyer 3.
- The user gave explicit verdict permission.
- Relevant active official sources are available for legal sections.
- The verdict uses a structured payload.
- The verdict is bound to its concrete source package and context snapshot.
- Citation verification passes against that bound source package.
- Required red-topic approval is satisfied or represented by the correct pending state.

Pre-verdict opinions, including strong opinions from Lawyer 2 or Lawyer 3, remain natural human-readable text and are not verdicts.

## User Permission

Examples of explicit verdict permission include:

- `оформи вердикт`;
- `оформи свой вердикт`;
- `дай финальное заключение`;
- `готовь итог`;
- `сделай юридический вывод`;
- `подготовь финальный вывод`;
- UI action `Разрешить вердикт`.

The following phrases are ambiguous and do not permit a verdict by themselves:

- `понятно`;
- `согласен`;
- `ок`;
- `ну да`;
- `в принципе ясно`.

Ambiguous consent must produce a clarification such as: `Подготовить финальный вердикт?`

## Model-Generated Verdict Content

The model may provide legal content fields in this form:

```json
{
  "type": "verdict",
  "lawyer_id": "lawyer_2",
  "jurisdiction": "UZ",
  "short_conclusion": "",
  "facts_established": [],
  "facts_missing": [],
  "legal_sources": [
    {
      "source_id": "",
      "title": "",
      "number": "",
      "date": "",
      "article_or_clause": "",
      "quote": ""
    }
  ],
  "analysis": [],
  "risks": [],
  "recommended_actions": [],
  "confidence": "low|medium|high"
}
```

This model payload is untrusted input to backend verification. It does not establish gate status.

## Backend-Controlled Fields

The following fields must be absent from the model schema or ignored and overwritten if a model emits them:

```text
confirmed_in_context
source_check_status
document_generation_allowed
approval_required
```

Only the backend sets these fields after deterministic checks and workflow evaluation. A model cannot approve its own citations, verdict, approval state, or document-generation gate.

## Source Package Binding

Every verdict must be bound to the exact retrieval and context used to generate it:

```text
source_package_id
context_snapshot_hash
```

Citation verification must use only the sources actually supplied to the model for that verdict. It must not search across every source ever retrieved in the chat. User-uploaded or other untrusted documents do not become official legal sources through this binding.

## Document Generation Button

The backend may set `document_generation_allowed = true` and show the document-generation button only when it confirms all applicable requirements:

- message type is `verdict`;
- verdict author is Lawyer 2 or Lawyer 3;
- explicit user permission exists;
- the source package and context snapshot are bound;
- citation verification passed, or an approved-template path applies;
- red-topic approval is satisfied, or the correct pending status is shown and generation remains blocked as required;
- the backend-computed gate is true.

The model must not control this button. The button must not appear under a normal opinion, Lawyer 1 response, preliminary analysis, unconfirmed answer, or non-verdict message.

## Approved Template Path

The `template_documents` group (`Шаблонные документы`, optionally displayed as `Шаблоны / Канцелярия`) is separate from verdict-based document generation. It may create a document only from an approved template or form without a verdict when policy permits. It has no verdict or legal-conclusion mode and must not bypass red-topic approval or create a final document from an unapproved form.

Verdicts belong only to `legal_questions` and remain subject to Lawyer 2/3 eligibility, explicit permission, source checks, backend verification, and approval gates. The canonical groups and section codes are defined in `SECTION_GROUPS_AND_RAG_POLICY.md`.

## P5 Implementation Mapping

P5 must explicitly map this policy to database and backend models so policy and implementation do not drift:

- `source_check_status` → `Message` or equivalent message metadata;
- `source_package_id` and `context_snapshot_hash` → message/verdict metadata;
- red-topic rules → `RedFlagRule` or equivalent configuration table;
- `document_generation_allowed` → backend-computed gate, never model output;
- `GeneratedDocument.status` → `draft` / `review` / `approved` / `rejected` lifecycle;
- `approval_required` → backend-computed approval workflow field.

P5 design must distinguish eligibility to generate a document from the lifecycle status of a generated document. The mapping above is mandatory, but exact schema changes require their own approved implementation stage.
