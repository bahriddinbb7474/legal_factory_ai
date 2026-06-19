# Decisions Log

## Accepted Decisions

- Project name: Legal Factory AI.
- Main interface language for the first version: Russian.
- Primary users: director, accounting, HR, procurement, sales, and production.
- There is no full-time lawyer in the initial operating assumption.
- Red-risk approval must be handled by the director or chief accountant.
- LLM access will go through OpenRouter.
- Agent models will be selected in admin settings.
- Stage 2 v2 uses one shared chat and manual invocation of exactly one selected lawyer.
- Lawyer 1 and Lawyer 2 must use different OpenRouter providers.
- Provider allowlist is enforced before invoking a model.
- OpenRouter model list is fetched dynamically instead of hardcoding all models.
- ZDR support is stored in provider/model settings; sensitive-data enforcement is deferred.
- Stage 3 v2 starts sensitive-data enforcement for uploaded documents: documents marked `sensitive` may be sent only to providers marked as trusted for sensitive data.
- The first UI language remains Russian; no user language preference field is added in Stage 2 v2.
- Costs are stored per chat, lawyer, provider, model, and token usage.
- Uploaded files are stored in local server storage for the first version.
- Extracted document text is stored separately and reused in chat context instead of re-running extraction on every lawyer call.
- Uploaded document content is wrapped as untrusted data before being sent to an LLM.
- Stage 3 v2 uses a development-only backend current-user stub from environment variables for role checks.
- Stage 4 v2 stores validated legal answers in `Message.structured_payload`; raw model output is technical evidence only.
- Backend performs at most one JSON repair attempt before rejecting the response.
- Uploaded-document quotes are verified deterministically from extracted text.
- Laws are not confirmed sources until Stage 6 RAG/legal-source ingestion exists; `law_unconfirmed` is always unconfirmed.
- `Chat.approval_status` is the single current approval status for Stage 4.
- `Approval` is an event journal, not a second source of truth.
- Red flag rules are stored as configurable `RedFlagRule` rows seeded by code.
- Monthly budget enforcement uses current-month `CostRecord` totals.
- Stage 5 uses one active verdict per chat through `Chat.active_verdict_message_id`.
- A generated document can be created only from the active verdict message.
- `GeneratedDocument.status` is the current status for document approval; `Approval` remains an event journal.
- Sending a generated document back to chat must not auto-select a lawyer or auto-call an LLM.
- Stage 5 DOCX export uses `python-docx`; PDF export is a lightweight fallback until a production renderer is chosen.
- Stage 6 implements curated legal RAG only; no full LEX.UZ crawler is built.
- Admins manually load active legal revisions, including ПП and ПКМ.
- `LegalSource.status=active` and `official_status=official` are required for normal retrieval.
- Old revisions are kept as `archived` or `outdated`.
- Legal source freshness is a manual 30-day check cycle.
- SQLite/dev/test use lexical fallback; PostgreSQL + pgvector remains the production vector-search target.
- `source_type=law` is confirmed only through chunks returned by the legal retriever.
- After Stage 6, Telegram and VPS are deferred.
- The post-Stage-6 priority is: legal source completion, company data, document templates, laptop local server, local auth/users, and factory scenario testing.
- The laptop can be used as a temporary local server only if it handles 3-4 users without instability.
- SQLite is acceptable for tests or a minimal local pilot only; PostgreSQL remains the production target.
- Telegram will be a quick entry point later, not a replacement for the Web UI.
- Real company documents may be sent to external LLM APIs only after the responsible business owner approves this operating model.
- Both Web UI and Telegram may be useful, but Web UI and local operational readiness come first.
- Stage 11-A decided: self-registration is permanently and unconditionally forbidden. User creation is admin-only. This rule must not be removed or worked around without an explicit separate approval stage.
- Stage 11-A decided: the first admin is created by `POST /api/auth/bootstrap` only; this endpoint closes permanently once an active admin with a password hash exists.
- Stage 11-B1 decided: the current dev database is SQLite (`sqlite+aiosqlite:///./legal_factory.db`). PostgreSQL restore is deferred to a separate stage before local network or production launch.
- Stage 11-B1 decided: `localhost` must be used consistently for both frontend (`localhost:3000`) and backend (`localhost:8000`) in development. Mixing `127.0.0.1` and `localhost` suppresses SameSite=Lax session cookies on POST/PATCH/DELETE requests and must be avoided.

## Pending Decisions

- Exact production OpenRouter models for Lawyer 1, Lawyer 2, and Lawyer 3 after manual testing.
- Production hosting model after the laptop pilot.
- Backup policy for uploaded documents.
- Retention period for chats, files, and audit logs.
- Whether Telegram approval is allowed for all red-risk cases or only selected categories after Telegram is reintroduced.
- Final production list of trusted providers for sensitive company documents.
- Whether image OCR should use OpenRouter vision models, a local OCR service, or a dedicated Uzbek/Russian OCR provider in production.
- Production approval roles and whether admin should be allowed to approve outside development.
- Production monthly budget value and whether blocks should be enabled by default.
- Final approved list of factory document templates and owners.
- Responsible owners for legal source revision checks, templates, and technical launch.
