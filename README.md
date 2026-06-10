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

Current status: Stage 1 foundation.

Implemented foundation:

- minimal FastAPI backend structure;
- `GET /health` endpoint;
- backend health test;
- minimal Next.js frontend page;
- development setup documentation.

Not implemented yet: AI agents, OpenRouter, RAG, document upload, legal response logic, database models, approval workflow, and Telegram.

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
