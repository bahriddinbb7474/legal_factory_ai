# Development Setup

Stage 2 creates a minimal runnable backend and frontend foundation, plus core backend models and chat API endpoints.

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

Build production assets:

```bash
cd frontend
npm run build
```

## Current Scope

Implemented: backend health endpoint, core backend models, chat/message/agent/cost APIs, Alembic initial migration, backend tests, minimal Next.js page, and development documentation.

Not implemented: AI agent execution, OpenRouter, RAG, document upload, legal response logic, approval workflow behavior, and Telegram.
