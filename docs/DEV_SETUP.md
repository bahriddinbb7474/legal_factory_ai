# Development Setup

Stage 6 v2 has a runnable backend/frontend foundation with core chat APIs, OpenRouter lawyer invocation, model settings, document upload, local file storage, text extraction, structured legal answers, generated documents, and curated legal RAG.

## Backend

Use the project virtual environment for backend commands.

Create `.venv` from the installed Python:

```bash
C:\Users\user\AppData\Local\Programs\Python\Python311\python.exe -m venv .venv
```

Install dependencies:

```bash
cd backend
..\.venv\Scripts\python.exe -m pip install -e ".[dev]"
```

Run the API:

```bash
cd backend
..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Check health:

```bash
GET http://127.0.0.1:8000/health
```

Expected response:

```json
{
  "status": "ok",
  "app": "Legal Factory AI"
}
```

OpenRouter configuration in `.env`:

```env
OPENROUTER_API_KEY=
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_TIMEOUT_SECONDS=30
OPENROUTER_APP_REFERER=
OPENROUTER_APP_TITLE=Legal Factory AI
OPENROUTER_MAX_OUTPUT_TOKENS=1200
CORS_ORIGINS=http://127.0.0.1:3000,http://localhost:3000
```

Do not commit real API keys. If `OPENROUTER_API_KEY` is empty, real lawyer invocation returns a clear service error; tests use a fake gateway.

Document processing configuration in `.env`:

```env
DOCUMENT_VISION_MODEL=
DOCUMENT_VISION_PROVIDER=
MAX_UPLOAD_SIZE_MB=25
XLSX_MAX_ROWS=1000
DEV_CURRENT_USER_ROLE=admin
DEV_CURRENT_USER_ID=1
```

`DOCUMENT_VISION_MODEL` and `DOCUMENT_VISION_PROVIDER` are optional. If they are empty, image uploads are accepted only as stored files and OCR extraction is marked as failed until a vision model is configured.

Run tests:

```bash
cd backend
..\.venv\Scripts\python.exe -m pytest
```

If a new PowerShell window can find Python in PATH, `python` may also work. The stable project command is still `.venv\Scripts\python.exe`.

## Database

Runtime database target:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/legal_factory_ai
```

The backend normalizes `postgresql://` to the async SQLAlchemy driver form internally. PostgreSQL is not required for tests; tests override the DB session with SQLite in-memory.

Run Alembic migrations when PostgreSQL is available:

```bash
cd backend
..\.venv\Scripts\python.exe -m alembic upgrade head
```

For local migration checks without PostgreSQL, a temporary SQLite database can be used:

```powershell
cd backend
$env:DATABASE_URL="sqlite+aiosqlite:///E:/Projects/Projects_5/legal_factory_ai/data/local_migration_check.db"
..\.venv\Scripts\python.exe -m alembic upgrade head
Remove-Item Env:\DATABASE_URL
```

Create a future migration after model changes:

```bash
cd backend
..\.venv\Scripts\python.exe -m alembic revision --autogenerate -m "describe change"
```

## Frontend

Install dependencies:

```bash
cd frontend
npm install
```

Run the development server:

```bash
cd frontend
npm run dev
```

The frontend calls the backend through:

```env
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000
```

Build production assets:

```bash
cd frontend
npm run build
```

## Future Laptop Local Server Plan

Stage 10 will test the user's laptop as a temporary local server for 3-4 users in the office LAN.

Planned local setup checks:

- backend runs on the laptop;
- frontend runs on the laptop;
- LAN users can reach the app through the laptop local IP;
- firewall rules allow local network access only as needed;
- OpenRouter latency is acceptable;
- document upload, RAG, generated documents, and DOCX export work under 3-4 users;
- database size, upload size, logs, CPU, RAM, and disk usage are monitored;
- restart, backup, and restore commands are documented.

Database guidance:

- SQLite is acceptable for automated tests and a minimal local pilot only.
- Local PostgreSQL should be prepared for the laptop pilot if practical.
- PostgreSQL remains the production target.

Do not treat the laptop pilot as production deployment. VPS/full server work is postponed until the laptop cannot meet the factory's needs or the factory needs 24/7, external access, stronger backups, or production security.

## Documents

Uploaded source files and extracted text are stored locally under:

```text
data/uploads/
```

The folder is ignored by git. Stage 3 supports PDF, DOCX, XLSX, TXT, JPG, PNG, and WebP. Extracted text is saved once and reused by lawyer calls so image OCR is not repeated on every chat message.

## Current Scope

Implemented: backend health endpoint, core backend models, chat/message/agent/cost APIs, OpenRouter gateway foundation, mock-tested lawyer invocation, admin model/provider endpoints, document upload APIs, local document storage, text extraction, basic role/sensitivity checks, structured legal JSON, citation verification, red flags, approval, generated documents, DOCX/PDF endpoints, curated legal RAG, Alembic migrations, backend tests, connected Next.js chat workspace, document chips, right editor, legal source settings UI, and model settings UI.

Not implemented: Stage 7 real legal base population, CompanyProfile, document templates, local laptop server hardening, production auth, production OCR hardening, production-grade PDF rendering, Telegram, and VPS/production deployment.
