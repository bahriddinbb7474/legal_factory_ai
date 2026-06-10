# Development Setup

Stage 1 creates a minimal runnable backend and frontend foundation.

## Backend

Install dependencies in a local Python environment:

```bash
cd backend
python -m pip install -e ".[dev]"
```

Run the API:

```bash
cd backend
python -m uvicorn app.main:app --reload
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
python -m pytest
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

Implemented: backend health endpoint, backend test, minimal Next.js page, and development documentation.

Not implemented: AI agents, OpenRouter, RAG, document upload, legal logic, database, approval workflow, and Telegram.
