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
- Stage 11-B2 decided: `viewer` role is read-only across the entire legal workspace. Returns 403 on all mutations (chat, message, document, generated document). Safe GET/read routes remain available.
- Stage 11-B2 decided: Audit log covers authentication and user management actions only (`auth.login`, `auth.logout`, `user.created`, `user.updated`, `user.deactivated`, `user.password_reset`). CompanyProfile, document templates, and legal source mutations are deferred to future audit expansion.
- Stage 11-B2 decided: Audit entries must never contain password, password_hash, token, cookie, session, secret, or new_password. Frontend audit section filters sensitive detail keys defensively as secondary protection.
- Stage 11-B2 decided: Admin audit UI section is read-only and shows recent audit entries with `limit`/`offset` pagination.

- Demo-1 decided: fake initial chat messages are permanently removed. The new-chat state defaults
  to an empty message list. Any initial content must come from the real backend, not hardcoded
  frontend state.
- Demo-1 historical decision, **superseded by P3-A**: `Chat` originally had no dedicated `section`
  field and encoded the selected section in the title. Current code has `Chat.section` and uses
  canonical backend-owned section codes; the title prefix is not a current routing contract.
- Demo-1 decided: `selectedSection` defaults to `null` on page load (no auto-selection). The
  section selector shows "Выбрать раздел" until the user picks a section. If no section is
  selected when the first message is sent, the chat title is just the first 60 chars of the
  question without a section prefix.
- Demo-1 decided: fake document panel data is intentionally left in place. It must be replaced
  during Phase C (real document generation and templates), not before.
- Demo-1 decided: raw `model_id` display and `$0.000000` cost formatting are deferred to Phase B
  (OpenRouter and model settings). They are known issues, not regressions.
- Demo-1 decided: advanced department-level permissions (section visibility, approval routing,
  export rights) are deferred until after the founder presentation. The current baseline of
  admin-created users, viewer read-only, and basic audit log is sufficient.
- P0 approved: pre-verdict lawyer answers are natural human-readable text. Structured legal payload is reserved for verdict only.
- P0 approved, refined by P4-RFC: Lawyer 1 provides preliminary analysis, identifies source needs and may ask clarification, but cannot issue a verdict or control retrieval/verdict/document gates. P4 creates the internal RAG request deterministically in backend.
- P0 approved: only Lawyer 2 or Lawyer 3 may issue a verdict, after explicit user permission and required source checks.
- P0 approved: legal sections require targeted RAG by default; approved template/correspondence work may use a separate path that cannot bypass legal or red-topic controls.
- P0 approved: RAG receives source inventory first, retrieves a targeted source package, and binds verdict verification to `source_package_id` and `context_snapshot_hash`.
- P0 approved: `confirmed_in_context`, `source_check_status`, `document_generation_allowed`, and `approval_required` are backend-controlled fields. Model values for them are absent, ignored, or overwritten.
- P0 approved: red topics force approval in every section. Large-amount thresholds are configurable for at least UZS and USD, with ambiguous financially significant amounts treated as red.
- P0 approved: RAG and red-topic triggers use configurable Russian and Uzbek Latin/Cyrillic roots or patterns, not exact Russian-only words.
- P0 approved: `<UNTRUSTED_DOCUMENT ...>` content is analysis data, not instructions or official law.
- P1 complete: the versioned policy files under `docs/10_policies/` are the normative specification for P2-P6.
- Approved implementation order: P2 prompts → P3 section behavior → P4 targeted RAG → P5 verdict/document gates and DB mapping → P6 Quality Gate → P7/Phase B model settings.
- P2-B0 through P2-B3 are complete. At that decision point P3 was next; this status is superseded by the P3 completion entries below.
- P3 approved: the two functional groups are `template_documents` (`Шаблонные документы`) and `legal_questions` (`Юридические вопросы и заключения`).
- P3 approved: Group 1 is an AI-Секретарь approved-template flow with no RAG, verdict, or legal conclusion by default; Group 2 is the AI-Юрист legal/RAG/verdict flow.
- P3 approved: policy routing uses stable internal group and section codes. Visible UI names are not policy keys and may change independently.
- P3 approved: missing templates and legal-verification requests route from Group 1 to Group 2; red topics override both group defaults and force the applicable approval workflow.
- P3-A/B/B1/C complete: runtime policy uses 17 canonical section codes in the `template_documents` and `legal_questions` groups; visible Russian labels remain display-only.
- P3 complete: legacy and unknown section values normalize safely to `legal_other` and cannot silently enter template flow.
- P3 complete: template sections do not run default RAG or verdict and verdict mode is blocked; legal sections receive legal-flow context; Lawyer 1 must check/request official sources or ask focused clarification before a final conclusion.
- P3 complete: red-topic detection still applies in both groups. P3-C verification passed 113 focused tests and the full backend suite passed 249 tests; P3-B1 frontend build passed and P3-C had no frontend changes.
- P4-RFC approved: P4 uses a deterministic backend planner; an LLM planner and extra planning call are not part of P4.
- P4-RFC approved: P4 persists immutable SourcePackage records with exact source metadata and chunk-text snapshots used in model context.
- P4-RFC approved: P4 prepares hash-ready snapshot fields; final `context_snapshot_hash`, verdict binding and package-bound citation verification belong to P5.
- P4-RFC approved: P4 is UZ-only MVP. No jurisdiction column or full topic taxonomy is added without a separate approval; section/trigger mapping is sufficient.
- P4-RFC approved: P4 begins configurable Russian, Uzbek Latin and Uzbek Cyrillic trigger patterns.
- P4-RFC approved: package statuses are backend-owned: `ready`, `empty`, `insufficient`, `planner_failed`, `retrieval_failed`, and `blocked_by_policy`.
- P4-RFC approved: retrieval/package readiness must not be labelled citation verification, confirmed source check, or `source_check_status=confirmed`.
- P4-RFC approved: template legal/red-topic handling is controlled and must not silently mutate the selected section.
- P4-RFC approved: the current source model has no separate `future` status; future revisions remain `draft` until verified and activated.
- P4-RFC approved: P5 must align or close legacy Stage 4/5 active-verdict, `citation_verifier`, and `structured_response` shortcut paths.
- Next implementation stage: P4-A source inventory, followed by P4-B triggers/planner, P4-C persistent package, P4-D invoke integration, P4-E missing-source behavior, P4-F minimal visibility and P4-G final verification. The verified P5 verdict/document gate is not implemented yet.

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
