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
