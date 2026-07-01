# Current State

Last updated after P3-C completion on 2026-07-01.

P2-B0 through P2-B3 are complete: safe public message fields, normal pre-verdict text, explicit Lawyer 2/3 verdict skeleton, and frontend/API mode integration. P3-A/B/B1/C are also complete: canonical sections, grouped/collapsed UI, compact sidebar polish, and backend section-policy routing.

Latest recorded verification: P3-C passed **113 focused backend tests** and the full backend suite passed **249 tests**. The frontend production build passed after P3-B1; P3-C did not change frontend code.

## Completed stages

- **Stages 1–6**: Web UI skeleton, OpenRouter lawyers, documents and photos, structured legal answers,
  verdict and generated document, curated legal RAG foundation.
- **Stage 7**: Factory legal source foundation. Real official Uzbek legal sources loaded; chunking,
  retrieval, citation confirmation, and freshness checks working.
- **Stage 8**: Company Profile. `CompanyProfile` model, admin CRUD API, and settings UI
  (`Настройки → Профиль компании`) implemented.
- **Stage 9**: Basic document templates. Debt/claim template with `CompanyProfile` substitution,
  DOCX export, and tests.
- **Stage 11-A**: Auth and roles foundation. Database-backed users, salted `scrypt` passwords,
  HTTP-only SameSite=Lax session cookies, `POST /api/auth/login`, `POST /api/auth/logout`,
  `GET /api/auth/me`, `POST /api/auth/bootstrap`. All workspace and admin routes require
  authentication. Admin-only enforcement on settings/admin routes and CompanyProfile writes.
- **Stage 11-B1**: Admin user management. `GET/POST /api/admin/users`,
  `PATCH /api/admin/users/{id}`, `POST /api/admin/users/{id}/reset-password`. Last-active-admin
  protection. Session invalidation on deactivate and password-reset. Frontend settings modal:
  section navigation, users list, inline user creation, inline edit, inline password reset.
  Admin UI is visible only to the `admin` role; non-admin users (including viewer) cannot see
  the Settings button or the admin user list.
- **Stage 11-B2**: Viewer read-only and basic audit log. `viewer` role enforced read-only:
  returns 403 on workspace mutations (chat/message/document/generated-document create/update/delete);
  safe GET/read routes remain available. Frontend: viewer write controls hidden; admin/settings
  hidden from non-admin. Role-name policy fixed for `supply`/`accountant`. Audit log added for
  `auth.login`, `auth.logout`, `user.created`, `user.updated`, `user.deactivated`,
  `user.password_reset`. Audit safety: no password/password_hash/token/cookie/session/secret in
  audit details; endpoint has `limit`/`offset`. Admin audit UI section shows recent audit entries;
  frontend filters sensitive detail keys defensively.
- **Demo-1 new-chat UI**: ChatGPT-style new-chat start screen. Fake initial messages removed;
  empty state is the default when opening a new chat. Compact "Выбрать раздел" dropdown selector
  above the input (no auto-selected section on load; placeholder shown until user picks).
  Selected section + first question generate the chat title on first send. Lawyer selector chips
  remain below the input in both empty and active chat states. No "Черновик" shown in empty-state
  topbar. Dead UI buttons removed. Corrupted Cyrillic strings fixed.
- **Stage A real chat/sidebar/history** (complete): Real chat backend and frontend with AI history integration.
  - **Backend**: Chat ownership and per-chat access control. `Chat.section` column added.
    `ChatCreate` no longer accepts `owner_user_id`; backend sets owner from authenticated user.
    `GET /api/chats`: admin sees all chats; non-admin sees only their own. Per-chat access:
    admin can read/write/invoke all chats; owner can read/write/invoke own chats; non-owner
    non-admin cannot access other users' chats; viewer can read only own chats, cannot create/write/invoke.
  - **Frontend**: Sidebar loads real chats from `GET /api/chats` grouped by section; click loads messages;
    reload-safe; who-wrote-what visible by `author_type`; multiple pending AI answers supported.
  - **AI history**: Lawyers receive chat history before answering; history includes sender labels and timestamps;
    each lawyer has universal system prompt; chat-specific history in `chat_context` not `system_prompt`;
    default prompts safely upgraded, custom admin prompts preserved; stale AI response cannot append to wrong chat.
- **P0 architecture** (approved): section-based strictness, lawyer-controlled targeted RAG, backend
  safety net, human-readable pre-verdict answers, structured verdict only, Lawyer 1 verdict ban,
  verified-verdict document gate, approved-template path, red-topic approval, and
  `UNTRUSTED_DOCUMENT` injection protection.
- **P1 policy documentation** (complete): `PROMPT_SYSTEM_V1.md`, `RAG_WORKFLOW_V1.md`,
  `LEGAL_RESPONSE_POLICY_V1.md`, `VERDICT_AND_DOCUMENT_POLICY_V1.md`, and `QUALITY_GATE_V1.md`.
- **P2-B0/B1/B2/B3** (complete): backend-owned public message fields, human-readable normal mode,
  conservative explicit verdict mode for Lawyer 2/3, and matching frontend invocation/rendering.
- **P3-A/B/B1/C** (complete): 17 canonical section codes belong to backend-owned groups
  `template_documents` and `legal_questions`; visible labels are display-only. The grouped sidebar
  is compact and collapsed by default, preserving legacy chats through normalization. Unknown or
  legacy values safely normalize to `legal_other` and never enter template flow accidentally.
  Template sections do not run default RAG or verdict and block verdict mode. Legal sections receive
  legal-flow policy context; Lawyer 1 must check/request official sources or ask focused clarification
  before a final conclusion. Red-topic detection still applies in both groups.

## What is intentionally NOT done yet

- **Fake document panel data**: still present in the document/right panel. Must be replaced
  during the real document generation and templates stage — not before.
- **Model/provider display**: raw `model_id` strings (e.g. `inclusionai/ling-2.6-flash`) and
  `$0.000000` cost display still visible in message toolbar. Cleanup deferred to the
  OpenRouter/model settings stage.
- **Advanced department permissions**: current baseline (admin-created users, viewer read-only,
  audit log) is sufficient before the founder presentation. Department-level visibility, approval
  routing, and export rights are deferred to post-presentation.
- **P4-P6 are not implemented yet**: targeted RAG/source inventory/source-package protocol,
  verified verdict/document gates, and the complete Quality Gate remain before Phase B.
- **P4 identifiers are not implemented**: `source_package_id` and `context_snapshot_hash` do not
  yet exist in the runtime flow.
- **P5 gate is not implemented**: an active verdict alone must not be treated as sufficient for
  document generation in the target workflow.

## Active database

SQLite via `DATABASE_URL=sqlite+aiosqlite:///./legal_factory.db` in `.env`.
PostgreSQL restore is deferred to a separate stage before local network or production launch.

## URL conventions (dev)

Backend must start on `localhost:8000`.
Frontend must run at `localhost:3000`.

Do **not** mix `127.0.0.1` and `localhost` between frontend and backend. Session cookies use
`SameSite=Lax`; cross-origin requests from `localhost:3000` to `127.0.0.1:8000` are treated as
cross-site and the cookie is suppressed on POST/PATCH/DELETE requests.

`NEXT_PUBLIC_API_BASE_URL` in the frontend defaults to `http://localhost:8000` when not set.

## Permanent invariants

- Self-registration is permanently forbidden. Only admin can create users.
- The first admin is created by bootstrap (`POST /api/auth/bootstrap`) only while no active admin
  exists; subsequent calls return 409.
- Admin settings and user management UI are visible only to role `admin`.
- `password_hash` is never included in any API response.
- Stamp/signature upload and rendering are not implemented and must not be enabled until a
  separate secure stage is explicitly approved.
- Deferred: Telegram, VPS/deployment, pgvector, LEX.UZ crawler, mass historical legal import.

## Next major direction

The approved immediate sequence is:

1. **P4 — Targeted RAG protocol**: source inventory, internal request, bound source package, multilingual backend fallback.
2. **P5 — Verdict/document gate**: structured verdict only, explicit permission, backend verification fields, `source_package_id` / `context_snapshot_hash`, approval and document button gates, DB mapping.
3. **P6 — Quality tests**: implement and pass all 38 checks from `QUALITY_GATE_V1.md`.
4. **P7 / Phase B — OpenRouter and model settings**: API key via `.env`, admin settings, user-facing modes, and clean model/cost UX.

After P7: company details/templates, legal-base and RAG verification, real factory scenarios,
founder presentation polish, laptop pilot/mini-launch, and only then separately approved deferred work.
