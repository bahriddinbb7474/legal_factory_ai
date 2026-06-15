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
- Legal response mode with source, document number, revision date, article or clause, quote, risk level, confidence, and approval flag.
- RAG over uploaded factory documents and official legal sources.
- Cost tracking by chat, model, and agent.
- Approval workflow for red-risk answers and final documents.
- Telegram bot as a quick entry point in later stages.

## Future Stack

- Frontend: React / Next.js.
- Backend: FastAPI.
- Database: PostgreSQL.
- Vector search: pgvector.
- LLM provider: OpenRouter API.
- Files: local server storage first.
- Telegram: added after the web foundation is stable.

## Launch Stages

1. Project foundation and documentation.
2. Web UI skeleton.
3. Chat and agents.
4. OpenRouter integration.
5. File upload and document analysis.
6. Right document editor.
7. RAG and legal sources.
8. Roles and approval.
9. Cost tracking.
10. Telegram bot.
11. Testing and first launch.

## Legal Warning

The system must not provide final legal conclusions without reliable sources. If a source is not found, the answer must clearly say that a final legal conclusion cannot be given and must be checked by a lawyer or responsible specialist.

## Project Status

Current status: Stage 3 v2 document upload and secure processing foundation.

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

Not implemented yet: RAG over laws, final legal source enforcement, approval workflow behavior, real document export, production auth/admin permissions, and Telegram.

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
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000
```

OpenRouter real calls require:

```env
OPENROUTER_API_KEY=
DOCUMENT_VISION_MODEL=
DOCUMENT_VISION_PROVIDER=
MAX_UPLOAD_SIZE_MB=25
```

Without the key, automated tests still pass through mocks, and the UI shows a clear backend/OpenRouter error instead of calling a real provider.
