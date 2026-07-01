# Architecture

Legal Factory AI should start with a simple, expandable architecture.

## Core Components

- Frontend: React / Next.js.
- Backend: FastAPI.
- Database: PostgreSQL.
- Vector search: pgvector.
- LLM provider: OpenRouter API.
- File storage: local server storage first.
- Telegram bot: postponed. It is not in the current core path and should return only after the legal base, templates, local launch, and real users are stable.

## Backend Data Foundation

Stage 2 adds the first backend data model layer with SQLAlchemy 2.x async sessions.

Core entities:

- `Role`
- `User`
- `Agent`
- `Chat`
- `Message`
- `Document`
- `Approval`
- `CostRecord`
- `AuditLog`

The runtime database target is PostgreSQL through `asyncpg`. Tests use SQLite in-memory through the same SQLAlchemy model metadata, so PostgreSQL is not required for automated backend checks.

Initial API surface:

- `GET /health`
- `GET /api/agents`
- `GET /api/chats`
- `POST /api/chats`
- `GET /api/chats/{chat_id}`
- `GET /api/chats/{chat_id}/messages`
- `POST /api/chats/{chat_id}/messages`
- `GET /api/chats/{chat_id}/costs`

Alembic is configured in `backend/alembic.ini`, with the first migration under `backend/alembic/versions/`.

## Post-Stage-6 Product Path

The core path is no longer Telegram-first. The originally approved sequence after Stage 6 was:

1. Stage 7 factory legal base — complete.
2. Stage 8 `CompanyProfile` — complete.
3. Stage 9 basic `DocumentTemplate` path — complete; real approved factory templates remain incomplete.
4. Stage 10 laptop pilot — pending.
5. Stage 11 local authentication and baseline role-based access — complete through Stage 11-B2.
6. Stage 12-13 final factory scenarios and mini-launch — pending.

The immediate approved work is now P2-P6 below, then P7 / Phase B. VPS, full production
deployment, and Telegram remain deferred until the core path is stable.

## First Foundation

The first implementation should avoid complex enterprise infrastructure. Redis, Celery, MinIO, Kubernetes, separate vector databases, and complex workflow engines can be added later if the product needs them.

## Approved P0 Policy Architecture

The approved target for the next implementation sequence is:

```text
section-based strictness
+ lawyer-controlled targeted RAG
+ backend safety net
+ human-readable pre-verdict answers
+ structured verdict only
+ Lawyer 1 cannot issue verdict
+ document button only after verified verdict
+ approved templates for канцелярия
+ red-topic approval everywhere
+ UNTRUSTED_DOCUMENT injection protection
```

P1 policy documentation, P2-B0 through P2-B3, and P3-A/B/B1/C are complete. The remaining required order before Phase B is:

1. P4 targeted RAG request and source-package protocol.
2. P5 verified verdict/document gates and explicit DB mapping.
3. P6 implementation of the 38-check Quality Gate.
4. P7 / Phase B OpenRouter and model settings.

P3 has two backend-owned functional groups:

- `template_documents` / `Шаблонные документы`: AI-Секретарь flow using approved templates, without RAG or verdict by default;
- `legal_questions` / `Юридические вопросы и заключения`: AI-Юрист flow using legal analysis, targeted RAG, and eligible verdicts.

Seventeen stable internal section codes now select policy. Visible names are display metadata and may change without changing routing. Unknown or legacy values normalize safely to `legal_other`, never to template flow. Template sections skip default RAG/verdict and block verdict mode; legal sections receive legal-flow context; red-topic detection applies to both groups. The canonical model and routing rules are in `SECTION_GROUPS_AND_RAG_POLICY.md`.

The Stage 4/5 sections below describe the legacy baseline rather than the final policy contract.
P2 now provides natural pre-verdict text, verdict-only structured mode, the Lawyer 1 prohibition,
and explicit-permission integration. P3 now adds canonical section routing. P4-P6 must add targeted RAG,
`source_package_id` / `context_snapshot_hash` binding, backend verification and approval gates,
and the complete Quality Gate.

The normative documents are `PROMPT_SYSTEM_V1.md`, `RAG_WORKFLOW_V1.md`,
`LEGAL_RESPONSE_POLICY_V1.md`, `VERDICT_AND_DOCUMENT_POLICY_V1.md`, `QUALITY_GATE_V1.md`,
and `SECTION_GROUPS_AND_RAG_POLICY.md`.

## Data Flow

1. User logs into the web UI.
2. User creates or opens a chat.
3. User asks a question or uploads a document.
4. Backend stores the chat, message, files, and audit information.
5. Agent layer applies the selected section and lawyer role.
6. Current P3 routing supplies template-flow or legal-flow policy context; Lawyer 1 checks/requests official sources or asks focused clarification.
7. P4 will add a concrete targeted active-official source package and backend retrieval fallbacks.
8. Before verdict, the user receives human-readable lawyer text.
9. After explicit permission, Lawyer 2 or Lawyer 3 may produce a structured verdict for backend verification.
10. P5 will enable document generation only after backend-computed source, citation, red-topic, and approval gates pass; it remains blocked for the current unconfirmed verdict skeleton.

## Stage 2 v2 OpenRouter Lawyer Flow

Stage 2 v2 adds one shared chat with manual invocation of exactly one selected lawyer:

1. User writes a message.
2. Frontend stores it in the chat.
3. User-selected lawyer is invoked through `POST /api/chats/{chat_id}/invoke`.
4. Backend builds the full chat context with explicit authors:
   - `Пользователь`
   - `Юрист 1`
   - `Юрист 2`
   - `Юрист 3`
   - `Система`
5. Backend loads the lawyer model/provider settings from DB.
6. OpenRouter gateway sends one request with `provider.only`.
7. Backend stores the answer with `author_type`, `model_id`, `provider_code`, token counts, and cost.

Automated tests mock OpenRouter. Real calls require `OPENROUTER_API_KEY`.

New data entities:

- `ProviderConfig`
- `ModelConfig`

Updated entities:

- `Agent` stores provider, model, system prompt, role type, prices, and ZDR support.
- `Message` stores `author_type`, `model_id`, `provider_code`, tokens, and cost.
- `CostRecord` stores provider/model usage.

Admin API:

- `GET /api/admin/agents`
- `PATCH /api/admin/agents/{agent_code}`
- `GET /api/admin/providers`
- `PATCH /api/admin/providers/{provider_code}`
- `GET /api/admin/openrouter/models`
- `POST /api/admin/openrouter/models/refresh`

Stage 2 v2 still does not implement RAG, document upload, final legal source enforcement, production admin auth, or Telegram.

## Stage 3 v2 Document Processing Flow

Stage 3 v2 adds secure document upload and extracted-text context:

1. The frontend uploads a file through `POST /api/documents/upload`.
2. Backend validates extension, MIME type, size, sensitivity, and path traversal.
3. `LocalStorageProvider` stores the original file once under a UUID-based storage key in `data/uploads/`.
4. Backend computes SHA-256 and reuses an existing document record when the same file content is uploaded again.
5. `DocumentExtractor` extracts text from TXT, text PDFs, DOCX, and XLSX. Images use a separate OpenRouter vision configuration only once at upload time.
6. Extracted text is saved as a separate text object in storage.
7. Documents can be linked to one or more chats through `chat_documents`.
8. When a lawyer is invoked, linked document text is appended to chat context inside marked `<UNTRUSTED_DOCUMENT>` blocks.
9. Full document text is not copied into `Message`.
10. Used documents are recorded through `message_documents`.

New API surface:

- `POST /api/documents/upload`
- `GET /api/documents`
- `GET /api/documents/{document_id}`
- `GET /api/documents/{document_id}/content`
- `GET /api/documents/{document_id}/download`
- `DELETE /api/documents/{document_id}`
- `POST /api/chats/{chat_id}/documents/{document_id}`
- `DELETE /api/chats/{chat_id}/documents/{document_id}`
- `GET /api/chats/{chat_id}/documents`

Document categories:

- `local_contract`
- `import_contract`
- `client_debt`
- `tax_letter`
- `government_letter`
- `hr_document`
- `order`
- `occupational_safety`
- `certificate`
- `template`
- `other`

Sensitivity values:

- `normal`
- `internal`
- `sensitive`

If a chat contains a `sensitive` document, the selected provider must be enabled, allowlisted, and trusted for sensitive documents. This check is enforced on the backend before any OpenRouter request.

SQLite remains for local development and tests only. PostgreSQL remains the production database target.

## Stage 4 v2 Structured Legal Safeguards (Legacy Baseline)

Stage 4 v2 historically changed lawyer answers from free text to validated structured data. P2 supersedes this for ordinary replies: pre-verdict answers are normal text, while structured payload is reserved for explicit eligible verdict mode.

Flow:

1. Backend builds the normal chat context plus any uploaded document text in `<UNTRUSTED_DOCUMENT>` blocks.
2. In the legacy Stage 4 flow, the selected lawyer was asked for strict JSON according to the legal response schema.
3. OpenRouter may receive `response_format={"type": "json_object"}` when supported, but backend validation is still mandatory.
4. If the first response is invalid JSON, backend performs one safe repair attempt.
5. If validation still fails, no normal legal answer is saved.
6. Citation verification runs in code:
   - `uploaded_document` sources must reference a document from the current context;
   - the quote must exist in extracted text after Unicode/whitespace normalization;
   - `law_unconfirmed` is always unconfirmed until Stage 6.
7. Unconfirmed sources force at least yellow risk and at most medium confidence.
8. Red flag rules scan user text, uploaded document text, and structured response text.
9. Chat approval status is updated on the `Chat` row; `Approval` records are an event journal.
10. Monthly budget checks run before model invocation and use current-month `CostRecord` totals.

New message fields:

- `structured_payload`;
- `raw_response`;
- `risk`;
- `confidence`;
- `approval_required`;
- `source_check_status`;
- `red_flag_codes`.

New approval API:

- `POST /api/chats/{chat_id}/request-approval`
- `POST /api/chats/{chat_id}/approve`
- `POST /api/chats/{chat_id}/reject`
- `GET /api/chats/{chat_id}/approvals`

New safety services:

- `structured_response.py`;
- `citation_verifier.py`;
- `red_flags.py`;
- `budget.py`.

## Stage 5 v2 Verdict and Generated Documents (Legacy Baseline)

Stage 5 introduces an explicit bridge between legal analysis and document drafting.

Core rule:

1. A lawyer answer is not automatically final.
2. The legacy storage/API can mark exactly one lawyer message as the active verdict, but the old manual mark action is not the normal current UI workflow and backend protections reject invalid sources.
3. The legacy document endpoint is tied to that active verdict, but new unconfirmed verdict skeletons keep `document_generation_allowed=false`; P5 must provide the verified target gate.
4. Earlier opinions, rejected drafts, and non-verdict chat messages are not document-generation sources.

P5 must harden this baseline: only an eligible structured verdict from Lawyer 2 or Lawyer 3 after
explicit permission may be active; relevant sources must be bound and verified; model-provided
gate fields must be ignored; and document generation must remain blocked until backend checks pass.

Updated entities:

- `Chat.active_verdict_message_id` stores the current verdict message.
- `Message.is_verdict` marks the active verdict message in message lists.
- `GeneratedDocument` stores the generated draft, document type, current status, storage keys, and the verdict message it came from.
- `Approval` remains an event journal; for generated documents, the current status lives on `GeneratedDocument.status`.

New chat API:

- `POST /api/chats/{chat_id}/messages/{message_id}/mark-verdict`
- `DELETE /api/chats/{chat_id}/verdict`
- `GET /api/chats/{chat_id}/verdict`
- `POST /api/chats/{chat_id}/documents/generate-from-verdict`

New generated document API:

- `GET /api/generated-documents/{document_id}`
- `PATCH /api/generated-documents/{document_id}`
- `GET /api/generated-documents/{document_id}/download.docx`
- `GET /api/generated-documents/{document_id}/download.pdf`
- `POST /api/generated-documents/{document_id}/send-to-chat`
- `POST /api/generated-documents/{document_id}/request-approval`
- `POST /api/generated-documents/{document_id}/approve`
- `POST /api/generated-documents/{document_id}/reject`
- `GET /api/generated-documents/{document_id}/approvals`

The send-back-to-chat action only adds a normal chat message/card. It does not choose a lawyer and does not invoke an LLM. The user must still select Lawyer 1, Lawyer 2, or Lawyer 3 from the composer before asking for another review.

DOCX export uses `python-docx`. PDF export is a lightweight Stage 5 fallback so the endpoint is stable; production PDF layout is postponed.

## Stage 6 v2 Curated Legal RAG

Stage 6 adds a curated legal source database, not a crawler.

Admins manually upload or paste active revisions of sources that the factory actually needs: codes, laws, ПП, ПКМ, ministerial orders, technical regulations, standards, tax/customs/fire/sanitary rules, and similar official acts.

New entities:

- `LegalSource`: metadata for one legal act/revision.
- `LegalChunk`: searchable chunks linked to a legal source.

Source lifecycle:

- `active` sources are eligible for RAG.
- `outdated`, `archived`, and `draft` sources remain visible in admin UI but are excluded from normal retrieval.
- Old revisions are archived or marked outdated instead of deleted.
- Future revisions remain draft/future before their effective date and are excluded from ordinary current-law retrieval.
- `last_checked_at` and `next_check_due_at` support manual monthly freshness review.

Retrieval:

- Production target is PostgreSQL + pgvector.
- Dev/test path uses lexical fallback in SQLite and does not require embeddings.
- If `EMBEDDING_MODEL`, `EMBEDDING_PROVIDER`, and `EMBEDDING_DIMENSIONS` are empty, uploads and retrieval still work.
- Only `status=active` and `official_status=official` sources are returned to the lawyer context.

Context separation:

- Curated laws are injected as `<TRUSTED_LEGAL_SOURCE ...>`.
- Uploaded contracts/letters stay inside `<UNTRUSTED_DOCUMENT ...>`.
- These two source types must not be mixed.
- Future legal-source context, if later approved, must use a separate marker such as `<FUTURE_LEGAL_SOURCE ...>` with an effective-date warning.

Citation validation:

- `source_type=law` is confirmed only if the source came from the legal retriever and the quote exists in the retrieved chunk with matching metadata.
- `source_type=law_unconfirmed` is always unconfirmed.
- Uploaded document citations continue to be verified against extracted uploaded document text.

## Stage 7-11 Architecture Status

Stage 7 completed the existing `LegalSource` and `LegalChunk` flow through data completion rather than a new crawler. Every source should include document type, title, number, adoption date, revision date, source name, source URL, official status, status, language, last check date, and next check date. Normal RAG must keep using only `active` official sources. Draft/future sources are preparation-only unless a later approved task adds separate future-context retrieval. Outdated/historical sources, including an approved source later found expired, remain metadata/history records and are excluded from ordinary current-law RAG.

Stage 8 added `CompanyProfile` for company details. Stamp/signature upload and rendering remain intentionally unimplemented; these files are sensitive and require a separate approved secure stage with director/admin access and audit logging.

Stage 9 added the basic `DocumentTemplate` path and one debt/claim template. The approved P0 target requires future real templates to follow the verified-verdict path or the separately approved template/correspondence path.

Stage 10 keeps the laptop pilot as an operational check: backend, frontend, local IP, LAN access, backups, restore, restart script, logs, database size, uploads size, and stability under 3-4 local users. SQLite is acceptable only for tests or minimal local launch; PostgreSQL remains the production target and should be prepared locally if practical.

Stage 11-A through 11-B2 removed the development current-user stub, added login/password users,
admin-only user creation, disabled users, backend-enforced role access, viewer read-only behavior,
and basic auth/user-management audit logging. Advanced approval routing remains deferred.
