# Legal Factory AI — P4 Targeted RAG RFC

Date: 2026-07-02
Status: approved implementation direction; docs-only RFC

## 1. Purpose

P4 replaces the current broad lexical retrieval call with a controlled legal RAG protocol. It is not an embeddings, crawler, or mass-import stage.

```text
user question
→ section/group policy
→ clarification possibility
→ compact source inventory
→ deterministic backend RAG request
→ backend validation
→ persistent immutable source package
→ normal answer or unconfirmed verdict skeleton using that package
→ hash-ready metadata for P5
```

P4 preserves human-readable pre-verdict answers. Structured payload remains reserved for verdict workflow. Lawyer 1 cannot issue a verdict; Lawyer 2/3 verdict still requires explicit permission and remains unconfirmed until P5.

## 2. Approved decisions

- P4 uses a deterministic backend planner. An LLM planner and extra planning call are deferred.
- P4 persists immutable source packages and exact source/chunk snapshots used in model context.
- P4 is UZ-only MVP. No jurisdiction column or full legal topic taxonomy is added without a separate decision.
- Section code, recent relevant chat context and configurable RU/UZ triggers are sufficient for P4 targeting.
- Package status is backend-owned. Retrieval does not equal citation verification or source confirmation.
- P4 prepares deterministic hash inputs; final `context_snapshot_hash` and verdict binding belong to P5.
- Template sections are never silently changed into legal sections. Risky/legal template requests use an explicit controlled legal-review path.
- P5 must bind verdicts to persisted packages and align or close legacy Stage 4/5 shortcut paths.

## 3. Non-goals

P4 does not implement a LEX.UZ crawler, mass legal import, pgvector/embeddings rollout, OpenRouter/model settings, Telegram, VPS/deployment, verified P5 verdict/document gates, production PDF rendering, advanced approvals, or the full P6 acceptance baseline.

## 4. Source inventory

The inventory is compact metadata, never a dump of chunks. It may contain only existing or derived fields:

```text
legal_source_id
title
document_type
document_number
adoption_date
revision_date
language
status
official_status
source_url
last_checked_at
next_check_due_at
freshness_warning
```

Ordinary current-law inventory and retrieval require:

```text
status=active AND official_status=official
```

`draft`, `outdated`, `archived`, unofficial sources and uploaded documents are excluded. The current model has no separate `future` status; a future revision remains `draft` until separately verified and activated.

Inventory ordering and size limits must be deterministic. Uploaded document metadata is supplied separately as untrusted factual context and never as inventory law.

## 5. Internal RAG request

The deterministic backend planner produces the existing policy schema:

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

Rules:

- `needs_rag=false` is allowed only for focused clarification or an approved template/correspondence path.
- `must_have` and `exclude` are backend-controlled invariants.
- `source_scope` is validated against the current inventory.
- Uploaded documents cannot enter `source_scope` or become official law.
- Ordinary retrieval assumes Uzbekistan. Foreign law is blocked unless comparative analysis was explicitly requested and separately supported.
- A missed mandatory-RAG request is overridden or blocked by backend safety logic.

The planner uses the latest user message, relevant bounded chat history, selected section/group, red/legal trigger flags, uploaded-document metadata, inventory, and RU/UZ patterns. It does not attempt to replace the lawyer's focused clarification behavior with fragile heuristics.

## 6. RU/UZ trigger foundation

P4 begins configurable roots/patterns for Russian, Uzbek Latin and Uzbek Cyrillic. Minimum families include tax, fine, dismissal, contract, claim, court, government authority, HR/labor, debt and customs/import.

Examples include:

```text
налог / soliq / солиқ
штраф / jarima / жарима
увольн* / ishdan bo'shat* / ишдан бўшат*
договор / shartnoma / шартнома
претензи* / da'vo / даъво
суд
госорган
```

An ML classifier is not required. Exact Russian-only substring matching is not an acceptable final P4 implementation.

## 7. Persistent immutable SourcePackage

Implementation may use entities such as `LegalSourcePackage` and `LegalSourcePackageItem`.

Package contract:

```text
id
protocol_version
chat_id
trigger_message_id
section_code
group_code
lawyer_code
rag_request_json
retrieval_query
status
created_at
hash_ready_snapshot_json
```

Item contract:

```text
package_id
legal_source_id
legal_chunk_id
rank
score
source_title_snapshot
document_number_snapshot
revision_date_snapshot
source_url_snapshot
chunk_label_snapshot
chunk_text_snapshot
chunk_content_hash
```

The package is immutable after creation. Exact package snapshots must equal the trusted chunks sent to the model and must not change after source edit or reindex. Uploaded documents are never package items. Access and ownership must follow the parent chat.

## 8. Backend-owned package status

Allowed statuses:

```text
ready
empty
insufficient
planner_failed
retrieval_failed
blocked_by_policy
```

- `ready`: at least one eligible active+official chunk, complete source/chunk snapshot, and configured score or strong lexical-match criterion passes.
- `empty`: retrieval completed successfully with no eligible chunks.
- `insufficient`: chunks exist but fail a configured threshold/minimum or require freshness review.
- `planner_failed`: no valid deterministic request can be created and safe fallback cannot recover.
- `retrieval_failed`: DB/search execution failed or timed out.
- `blocked_by_policy`: the request attempts disallowed source status, foreign law without an explicit supported comparison, or an uploaded document as law.

Thresholds and limits must be configured and testable. Package status is not a verdict state. Clarification is not a package status. `ready` means retrieved context is available, not that citations are verified.

## 9. Hash-ready boundary

P4 stores the stable inputs needed by P5 but does not implement final `context_snapshot_hash`.

Hash-ready data includes retrieval protocol and prompt/policy versions, canonical RAG request JSON, chat/context digest inputs, selected section and lawyer, uploaded document IDs and content hashes, package item snapshots and chunk content hashes.

P5 will define canonical serialization and compute the final deterministic hash. Timestamp must not enter that hash; `created_at` is stored beside it.

## 10. Invoke integration

Normal legal mode:

```text
Lawyer 1/2/3
→ source package when mandatory RAG applies
→ human-readable answer
→ structured_payload=null
→ no document-generation eligibility
```

Verdict skeleton mode:

```text
Lawyer 2/3 + explicit permission
→ source package included
→ structured verdict skeleton
→ source_check_status remains unconfirmed/not confirmed
→ document_generation_allowed=false
```

Lawyer 1 remains blocked from verdict. Template sections remain blocked from verdict.

If package is `empty`, `retrieval_failed`, `planner_failed`, or policy-blocked, the backend must not run an ordinary confident legal-answer prompt. It uses a missing-source/cautious path. `insufficient` permits only a clearly preliminary answer.

Suggested missing-source wording:

```text
По этому вопросу в текущей базе не найден достаточный официальный источник.
Я могу дать только предварительную рабочую оценку или задать уточняющие вопросы.
Финальный юридический вывод без проверки официального источника невозможен.
```

## 11. Template legal handling

An ordinary approved-template request stays in `template_documents` without default RAG. A missing template, legal verification, dispute, or red-topic cannot remain a simple template operation.

The backend must not silently mutate the selected section. UI/API must require an explicit legal-review path or legal-section selection while preserving red-topic and approval gates.

## 12. API/UI wording

P4 may expose package state and source metadata, but must not describe retrieval as confirmation.

Allowed:

```text
Официальные источники найдены и использованы.
Проверка цитат и финальное подтверждение ещё не выполнены.
```

For missing sources:

```text
Официальный источник не найден в текущей базе.
Финальный юридический вывод невозможен без дополнительной проверки.
```

Forbidden before P5 verification: `sources confirmed`, `citations verified`, or `source_check_status=confirmed` based only on retrieval.

## 13. Implementation roadmap

1. **P4-A — Source inventory:** active+official filtering, stable ordering/limits, metadata/freshness, tests.
2. **P4-B — RU/UZ triggers and deterministic planner:** configurable patterns, canonical request, bounded chat context, validation and fallback, tests.
3. **P4-C — Persistent SourcePackage:** migration/models, immutable snapshots, item hashes/status, exact-context equality, tests.
4. **P4-D — Invoke integration:** normal and verdict-skeleton paths use packages while current verdict/document gates remain blocked, tests.
5. **P4-E — Missing-source behavior:** distinguish empty, insufficient and failures; no confident unsupported answer, tests.
6. **P4-F — Minimal API/UI visibility:** accurate package/warning language; frontend build if UI changes.
7. **P4-G — Final verification/docs:** focused and full backend tests, applicable frontend build, manual smoke, final PASS/PARTIAL/FAIL.

## 14. Blocking acceptance tests

P4 tests must cover section/path rules, backend-controlled request invariants, active+official inventory, exclusion of draft/outdated/archived/unofficial/untrusted sources, RU/UZ triggers, prompt-injection resistance, missed-RAG fallback, empty versus failed retrieval, cautious insufficient behavior, immutable exact package snapshots, deterministic inventory/hash-ready data, chat-context targeting, concurrency isolation, normal/verdict integration, and non-misleading UI wording.

The complete blocking list is maintained in [TESTS_AND_RISKS.md](TESTS_AND_RISKS.md).

## 15. P4/P5 boundary

P4 ends when a legal invoke can deterministically build, validate, persist and use an immutable package, handle missing sources safely, and expose accurate unconfirmed status.

P5 begins with final `context_snapshot_hash`, verdict-to-package binding, package-bound citation verification, backend-computed gate fields and closure/alignment of legacy Stage 4/5 active-verdict, citation-verifier and structured-response shortcuts. P4 must not enable document generation from an unconfirmed verdict.

Related policy: [RAG_WORKFLOW_V1.md](../10_policies/RAG_WORKFLOW_V1.md), [VERDICT_AND_DOCUMENT_POLICY_V1.md](../10_policies/VERDICT_AND_DOCUMENT_POLICY_V1.md), [SECTION_GROUPS_AND_RAG_POLICY.md](../10_policies/SECTION_GROUPS_AND_RAG_POLICY.md).
