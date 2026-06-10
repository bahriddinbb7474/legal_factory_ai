# Development Setup

Stage 1 creates a minimal runnable backend and frontend foundation.

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

Implemented: backend health endpoint, backend test, minimal Next.js page, and development documentation.

Not implemented: AI agents, OpenRouter, RAG, document upload, legal logic, database, approval workflow, and Telegram.
