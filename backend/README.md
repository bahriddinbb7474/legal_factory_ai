# Legal Factory AI Backend

Minimal FastAPI backend foundation for Stage 1.

## Run

```bash
cd backend
python -m uvicorn app.main:app --reload
```

Health check:

```bash
GET /health
```

Expected response:

```json
{
  "status": "ok",
  "app": "Legal Factory AI"
}
```

## Test

```bash
cd backend
python -m pytest
```

No database, AI provider, OpenRouter integration, RAG, document upload, or Telegram logic is implemented in this stage.
