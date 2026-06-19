# Current State

Last updated after Stage 11-B2 Viewer Read-Only and Basic Audit Log.
Master commit: `711a271 — feat: audit auth and admin user actions`.

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

After Stage 11-B2, remaining priorities before final launch:

1. UI/page cleanup and polish.
2. Chat functionality cleanup and comprehensive testing.
3. Correct CompanyProfile data and ensure admin setup workflow.
4. Document templates quality and completeness.
5. Approval workflow clarity and enforcement.
6. Legal source expansion and RAG testing with real factory scenarios.
7. AI testing by demo topics (debt claim, contract review, tax letter, HR, customs, etc.).
8. Founder demo preparation with realistic end-to-end scenarios.
