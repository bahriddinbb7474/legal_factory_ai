# Stage 11-A Auth and Roles Foundation

## Scope

Stage 11-A replaces the development current-user assumption with database-backed users and authenticated sessions. It adds password hashing, login/logout/current-user endpoints, one-time admin bootstrap, role dependencies, protected settings writes, and a minimal frontend login/session indicator.

This stage does not implement the full approval workflow, audit-log expansion, user-management UI, sensitive stamp/signature access, local network deployment, Telegram, or VPS deployment.

## User model and roles

Users contain email, full name, role, password hash, active state, timestamps, and nullable last-login time. Email is unique. Password hashes are never included in API schemas.

Supported roles:

- `admin`
- `director`
- `chief_accountant`
- `legal_responsible`
- `sales`
- `supply`
- `hr`
- `accountant`
- `viewer`

Stage 11-A requires an active authenticated user for all legal workspace API routes. It enforces `admin` on admin/settings API routes and on CompanyProfile create/update and asset upload/delete. Other roles can authenticate and use the existing legal workspace; finer document-category and read-only enforcement is deferred.

## Passwords and sessions

Passwords are hashed with salted `scrypt`; plaintext passwords are never stored. Login creates a random opaque session token. Only its SHA-256 hash is stored in `auth_sessions`. The browser receives the token in an HTTP-only, SameSite=Lax cookie. Sessions expire after seven days by default.

Endpoints:

```text
POST /api/auth/bootstrap
POST /api/auth/login
POST /api/auth/logout
GET  /api/auth/me
```

For HTTPS deployment, set `AUTH_COOKIE_SECURE=true`. CORS must list the exact frontend origin and continue to allow credentials.

## Initial admin bootstrap

Create the first usable administrator once:

```powershell
$body = @{ email = "your-admin@example.com"; full_name = "Local Administrator"; password = Read-Host "Strong password" } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/api/auth/bootstrap -ContentType application/json -Body $body -SessionVariable session
```

Use a unique password of at least 12 characters. Do not place credentials in source files, `.env`, shell history, documentation, or screenshots.

Bootstrap is available only while there is no active administrator with a non-empty password hash. This permits a database migrated from an earlier stage to initialize its first usable administrator even if legacy user rows already exist. If the submitted email belongs to a legacy user, that row is initialized as the administrator instead of creating a duplicate. Bootstrap is serialized by an application-level lock and re-checks the usable-admin condition inside the lock; after a usable administrator exists, it returns `409`.

## Frontend behavior

Unauthenticated visitors see the login form. Authenticated users see their name/email and role in the sidebar and can log out. The settings entry and settings modal are available only to admins. API requests include the HTTP-only session cookie.

## Deferred work (after Stage 11-A)

- full user creation, editing, deactivation, and password-reset UI → **implemented in Stage 11-B1**
- full role/category and viewer read-only enforcement;
- full director/chief-accountant approval workflow;
- full audit log;
- sensitive stamp/signature storage and insertion policy;
- local network deployment, Telegram, and VPS.

Security warning: **Do not upload real stamp/signature assets until roles/auth and the sensitive-asset policy are fully implemented, reviewed, and accepted.** No stamp/signature endpoint or insertion flow is enabled in Stage 11-A.

---

# Stage 11-B1 Admin User Management

## Scope

Stage 11-B1 adds admin-only user management. Admin can list, create, edit, deactivate, and reset passwords for users. No self-registration, no invite links, no email sending.

## User creation rules

- Admin-only: `POST /api/admin/users`
- Email is normalized (lowercase, trimmed) and must be unique; duplicate returns 409
- Password is hashed with salted scrypt; plaintext is never stored or logged
- `password_hash` is never included in any API response
- `is_active` defaults to true

## Supported roles

`admin`, `director`, `chief_accountant`, `legal_responsible`, `sales`, `supply`, `hr`, `accountant`, `viewer`

## User update rules

- Admin-only: `PATCH /api/admin/users/{user_id}`
- Admin can update `full_name`, `role`, `is_active`
- **Last-admin protection**: deactivating or demoting the last active admin returns 409
- Sessions for a deactivated user are invalidated immediately

## Password reset

- Admin-only: `POST /api/admin/users/{user_id}/reset-password`
- Sets a new hashed password; old password stops working immediately
- All existing sessions for that user are invalidated after reset

## Admin user endpoints

```text
GET    /api/admin/users
POST   /api/admin/users
PATCH  /api/admin/users/{user_id}
POST   /api/admin/users/{user_id}/reset-password
```

All routes require `role == "admin"`.

## Frontend

Users section appears at the top of the admin settings modal, visible only to admins. Non-admins cannot see it. The section allows listing users, creating a new user (inline form), editing full_name/role/is_active, and resetting a user's password.

## Deferred after Stage 11-B1

- viewer read-only enforcement for legal workspace → **planned in Stage 11-B2**
- audit log for user management actions → **planned in Stage 11-B2**
- approval workflow
- granular workspace permissions by document category
- HTTPS deployment hardening
- multi-worker bootstrap lock (race-condition hardening)
- Telegram / VPS
- stamp/signature sensitive storage and insertion policy

Security warning: **Do not upload real stamp/signature assets until roles/auth and the sensitive-asset policy are fully implemented, reviewed, and accepted.**

---

# Stage 11-B2 — Viewer Read-Only and Basic Audit Log

## Status

**COMPLETE** as of commit `711a271 — feat: audit auth and admin user actions`.

## Implementation Summary

### Role enforcement (COMPLETE)

- `viewer` role is now read-only across the legal workspace. Returns 403 on workspace mutations:
  - Chat create/update/delete
  - Message create/update/delete
  - Document create/update/delete
  - GeneratedDocument create/update/delete
  - CompanyProfile mutations (already admin-only in 11-A)
  - Legal source mutations (already admin-only)
- Safe GET/read routes remain available; viewer can view chats, messages, documents, generated documents, and audit log.
- Role-name policy fixed for `supply` and `accountant` roles to match role enum correctly.
- Frontend: write controls (buttons, inputs) hidden for viewer role; admin settings and user list hidden from non-admin users.
- Enforcement is both backend (403 API responses) and frontend (UI hiding and defensive detail filtering).

### Audit log (COMPLETE)

Append-only `AuditLog` table with entries for:

- `auth.login` — user login
- `auth.logout` — user logout
- `user.created` — admin creates new user
- `user.updated` — admin updates user (role/name/active)
- `user.deactivated` — user deactivated by admin
- `user.password_reset` — admin resets user password

Each entry records: `action` (string), `actor_user_id` (who performed it), `target_id` (user being acted upon, nullable),
`detail` (JSON), `created_at` (timestamp).

**Audit safety enforced:**
- No `password`, `password_hash`, `token`, `cookie`, `session`, `secret`, or `new_password` in audit details.
- `GET /api/admin/audit` endpoint requires `admin` role and supports `limit` and `offset` pagination.
- Frontend audit log section in admin settings filters sensitive detail keys defensively before display.

Admin can view recent audit entries in the settings modal with pagination.

## Deferred after Stage 11-B2

- Full director/chief-accountant approval workflow (approval role enforcement).
- Granular workspace permissions by document category (`sales`, `supply`, `hr`, `accountant` category-based restrictions).
- Audit log expansion (document/template/legal-source mutations; approval workflow events).
- HTTPS deployment hardening.
- Multi-worker bootstrap lock (race-condition hardening for bootstrap endpoint).
- Telegram / VPS.
- Stamp/signature sensitive storage and insertion policy.

## Commits in Stage 11-B2

- `606eb29 — feat: enforce viewer read-only access` (backend 403 enforcement)
- `b775422 — feat: hide read-only viewer workspace controls` (frontend UI hiding)
- `711a271 — feat: audit auth and admin user actions` (audit log implementation)
- `f395c4b` (audit UI frontend part 1)
- `7f4b07c` (audit UI frontend part 2)
