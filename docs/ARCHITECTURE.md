# Architecture

Legal Factory AI should start with a simple, expandable architecture.

## Core Components

- Frontend: React / Next.js.
- Backend: FastAPI.
- Database: PostgreSQL.
- Vector search: pgvector.
- LLM provider: OpenRouter API.
- File storage: local server storage first.
- Telegram bot: added after the web workflow is stable.

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

## First Foundation

The first implementation should avoid complex enterprise infrastructure. Redis, Celery, MinIO, Kubernetes, separate vector databases, and complex workflow engines can be added later if the product needs them.

## Data Flow

1. User logs into the web UI.
2. User creates or opens a chat.
3. User asks a question or uploads a document.
4. Backend stores the chat, message, files, and audit information.
5. Agent layer selects the needed model and legal response mode.
6. RAG retrieves relevant sources when available.
7. The answer is returned with sources, risk level, confidence, cost, and approval requirement.

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

## Stage 4 v2 Structured Legal Safeguards

Stage 4 v2 changes lawyer answers from free text to validated structured data.

Flow:

1. Backend builds the normal chat context plus any uploaded document text in `<UNTRUSTED_DOCUMENT>` blocks.
2. The selected lawyer is asked for strict JSON according to the legal response schema.
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

## Stage 5 v2 Verdict and Generated Documents

Stage 5 introduces an explicit bridge between legal analysis and document drafting.

Core rule:

1. A lawyer answer is not automatically final.
2. The user marks exactly one lawyer message as the active verdict.
3. A generated document may be created only from that active verdict.
4. Earlier opinions, rejected drafts, and non-verdict chat messages are not document-generation sources.

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
