# Current State

Last updated after Stage 11-B1 Admin User Management.
Master commit: `c30ea53 — merge: stage 11-b1 user menu UI fixes`.

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

## Next stage

**Stage 11-B2 — Viewer read-only and basic audit log.**
See `STAGE11_AUTH_ROLES.md` for planned scope. Do not implement until explicitly instructed.
