# Legal Factory AI

Legal Factory AI is an internal AI legal assistant for a cable factory in Uzbekistan.

The project is planned as a web workspace in a ChatGPT/Claude style: chat in the center, chat history on the left, a document editor on the right, and legal answers with sources, risk level, confidence, and approval requirements.

## Purpose

The system should help factory teams prepare legal drafts and preliminary analysis for:

- local and import contracts;
- client debts;
- letters from tax and other government bodies;
- HR and labor questions;
- claims, replies, memos, and legal opinions.

Legal Factory AI is an assistant only. It does not replace a live lawyer, director, chief accountant, or other responsible specialist.

## Planned Features

- Web UI with login, roles, chat history, and document editor.
- Three AI legal agents through OpenRouter.
- File upload for PDF, DOCX, XLSX, TXT, and images.
- Human-readable pre-verdict legal analysis, with structured payload reserved for verified verdicts.
- RAG over uploaded factory documents and official legal sources.
- Cost tracking by chat, model, and agent.
- Approval workflow for red-risk answers and final documents.
- Company profile data for official letters and generated documents.
- Approved document templates for factory letters, claims, replies, and HR/production documents.
- Local laptop server pilot for 3-4 users before any VPS or production deployment.
- Telegram bot as a postponed quick entry point after the Web UI, legal base, templates, and local launch are stable.

## Future Stack

- Frontend: React / Next.js.
- Backend: FastAPI.
- Database: PostgreSQL.
- Vector search: pgvector.
- LLM provider: OpenRouter API.
- Files: local server storage first.
- Telegram: postponed until after the factory legal base, templates, local launch, and real users are stable.

## Launch Stages

Completed:

1. Stage 1: UI skeleton and project foundation.
2. Stage 2: OpenRouter and three lawyers in one shared chat, including manual lawyer selection and token/cost tracking.
3. Stage 3: PDF/DOCX/XLSX/TXT/JPG/JPEG/PNG/WEBP upload, extraction/OCR path, sensitivity, `UNTRUSTED_DOCUMENT`, storage, and provider enforcement.
4. Stage 4: legacy structured legal-answer baseline, risk, confidence, sources, citation verification, red flags, approval, and monthly budget guard.
5. Stage 5: legacy active-verdict baseline, `GeneratedDocument`, right editor, DOCX export, approval, and send-back-to-chat without an automatic LLM call.
6. Stage 6: curated legal RAG with `LegalSource`, `LegalChunk`, ПП/ПКМ support, `TRUSTED_LEGAL_SOURCE`, `source_type=law` verification, freshness warnings, SQLite lexical fallback, and PostgreSQL + pgvector production target.

Also complete: Stages 7-9, local auth/RBAC through Stage 11-B2, Demo-1 UI, Stage A real chat/history,
approved P0 prompt/RAG/verdict architecture, and P1 policy documentation.

Immediate roadmap:

1. P2: implement universal and role prompts plus verdict/template/source-missing modes.
2. P3: implement section-based strictness and lawyer verdict eligibility.
3. P4: implement lawyer-controlled targeted RAG and multilingual backend fallback.
4. P5: implement verified verdict/document gates, bound source packages, and DB mapping.
5. P6: pass all 34 checks in `docs/QUALITY_GATE_V1.md`.
6. P7 / Phase B: finish OpenRouter/model settings UX.
7. Continue with real templates/data, RAG verification, factory scenarios, presentation polish, laptop pilot, and mini-launch.
8. Telegram and VPS remain separately approved later work.

## Legal Warning

The system must not provide final legal conclusions without reliable sources. If a source is not found, the answer must clearly say that a final legal conclusion cannot be given and must be checked by a lawyer or responsible specialist.

## Project Status

Current status: P1 policy documentation is complete. The next approved stage is P2 prompt implementation; P3-P6 follow before P7 / Phase B.

Implemented foundation:

- minimal FastAPI backend structure;
- `GET /health` endpoint;
- SQLAlchemy async DB foundation;
- core backend models for users, roles, chats, messages, agents, documents, approvals, cost records, and audit logs;
- Alembic initial migration;
- simple agents, chats, messages, and chat costs API endpoints;
- OpenRouter gateway foundation with mockable tests and no real provider calls in automated checks;
- three configurable lawyers: fast lawyer, independent analyst, and arbiter;
- one shared chat where the user manually invokes only one selected lawyer per request;
- provider allowlist and the rule that Lawyer 1 and Lawyer 2 must use different providers;
- dynamic OpenRouter model list endpoint for admin settings;
- model settings UI from the user profile area;
- backend tests using SQLite in-memory;
- Next.js chat workspace connected to backend chat/invoke endpoints;
- development setup documentation.
- StorageProvider abstraction with local `data/uploads/` storage;
- upload API for PDF, DOCX, XLSX, TXT, JPG/JPEG, PNG, and WEBP;
- extracted text storage for documents, with image OCR routed through a separate configurable vision model;
- chat-document and message-document linking;
- prompt-injection protection through explicit untrusted document context blocks;
- backend role checks for document access;
- sensitive-document provider enforcement;
- audit logs for upload/open/download/link/use/denial events;
- upload UI from the chat composer plus right-side extracted-text preview.
- strict structured JSON response schema for lawyer answers (implemented legacy baseline; P2-P6 will reserve structured payload for verdict only);
- backend validation and one safe JSON repair attempt;
- deterministic citation verification against uploaded document text;
- unconfirmed-source safeguards that prevent green/high-confidence answers;
- red flag detection with automatic `needs_review` chat status;
- arbiter forced-red rule for unresolved disputes without confirmed sources;
- approval API where `Chat.approval_status` is the single source of truth;
- monthly budget warning/block guard based on stored `CostRecord` rows;
- frontend structured legal answer card, red-flag banner, and approval controls.
- active verdict workflow: only one lawyer message can be marked as the current verdict per chat;
- `GeneratedDocument` backend entity for drafts created strictly from the active verdict;
- generated document editor flow with save/cancel, DOCX/PDF export endpoints, and send-back-to-chat action;
- generated document approval status with an `Approval` event journal;
- audit logs for verdict, generated document, export, send-back, and approval events.
- curated legal source database for manually loaded laws, codes, ПП, ПКМ, standards, and other official acts;
- `LegalSource` and `LegalChunk` models with Alembic migration;
- admin API and minimal settings UI for legal source upload, raw-text entry, listing, freshness warnings, and reindex;
- legal chunking by articles, points, subpoints, applications, with safe fallback chunking;
- legal retriever with SQLite lexical fallback for dev/tests and PostgreSQL + pgvector as the production target;
- trusted legal source blocks in lawyer context, separate from untrusted uploaded documents;
- `source_type=law` citation validation only against retrieved legal chunks.

Stage 6 smoke status: PASS.

- ПКМ №999 chunking produced Пункт 1/2/3.
- Retriever found Пункт 3: `Документы проверяются один раз в месяц.`
- Correct quote was confirmed.
- Wrong quote was unconfirmed, prevented green/high-confidence output, and kept risk at yellow with medium confidence.
- Freshness warning works.

Not implemented yet: Stage 7 real legal base population, CompanyProfile, document templates, local laptop pilot, production auth/admin permissions, production-grade PDF rendering, Telegram, and VPS/production deployment.

## Run Backend

Create and use the project Python environment:

```bash
C:\Users\user\AppData\Local\Programs\Python\Python311\python.exe -m venv .venv
```

Install backend dependencies:

```bash
cd backend
..\.venv\Scripts\python.exe -m pip install -e ".[dev]"
```

Start the API:

```bash
cd backend
..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Health check:

```bash
GET http://127.0.0.1:8000/health
```

## Run Backend Tests

```bash
cd backend
..\.venv\Scripts\python.exe -m pytest
```

## Run Database Migrations

When PostgreSQL is available and `DATABASE_URL` is configured:

```bash
cd backend
..\.venv\Scripts\python.exe -m alembic upgrade head
```

Backend tests do not require PostgreSQL; they use SQLite in-memory.

## Run Frontend

Install frontend dependencies:

```bash
cd frontend
npm install
```

Start the frontend:

```bash
cd frontend
npm run dev
```

Build the frontend:

```bash
cd frontend
npm run build
```

Frontend expects the backend at:

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

OpenRouter real calls require:

```env
OPENROUTER_API_KEY=
DOCUMENT_VISION_MODEL=
DOCUMENT_VISION_PROVIDER=
MAX_UPLOAD_SIZE_MB=25
MONTHLY_BUDGET_USD=100
BUDGET_WARNING_PERCENT=80
BLOCK_EXPENSIVE_CALLS=false
EMBEDDING_MODEL=
EMBEDDING_PROVIDER=
EMBEDDING_DIMENSIONS=
```

Without the key, automated tests still pass through mocks, and the UI shows a clear backend/OpenRouter error instead of calling a real provider.
