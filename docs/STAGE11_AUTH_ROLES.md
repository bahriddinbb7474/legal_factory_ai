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

## Deferred work

- full user creation, editing, deactivation, and password-reset UI;
- full role/category and viewer read-only enforcement;
- full director/chief-accountant approval workflow;
- full audit log;
- sensitive stamp/signature storage and insertion policy;
- local network deployment, Telegram, and VPS.

Security warning: **Do not upload real stamp/signature assets until roles/auth and the sensitive-asset policy are fully implemented, reviewed, and accepted.** No stamp/signature endpoint or insertion flow is enabled in Stage 11-A.
