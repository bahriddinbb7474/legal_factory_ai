# Development Setup

Stage 3 v2 creates a runnable backend/frontend foundation with core chat APIs, OpenRouter lawyer invocation, model settings, document upload, local file storage, and text extraction.

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

## Documents

Uploaded source files and extracted text are stored locally under:

```text
data/uploads/
```

The folder is ignored by git. Stage 3 supports PDF, DOCX, XLSX, TXT, JPG, PNG, and WebP. Extracted text is saved once and reused by lawyer calls so image OCR is not repeated on every chat message.

## Current Scope

Implemented: backend health endpoint, core backend models, chat/message/agent/cost APIs, OpenRouter gateway foundation, mock-tested lawyer invocation, admin model/provider endpoints, document upload APIs, local document storage, text extraction, basic role/sensitivity checks, Alembic migrations, backend tests, connected Next.js chat workspace, document chips, and model settings UI.

Not implemented: RAG/vector search, production OCR hardening, real document export, final legal source enforcement, approval workflow behavior, production admin auth, and Telegram.
