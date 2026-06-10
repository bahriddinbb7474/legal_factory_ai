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

Stage 2 only implements the storage/API foundation. It does not call OpenRouter, generate AI answers, upload files, run RAG, or send Telegram messages.
