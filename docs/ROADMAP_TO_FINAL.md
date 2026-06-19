# Roadmap to Final

Current status: Stages 1–6, 7, 8, 9, 11-A, and 11-B1 are complete. See `CURRENT_STATE.md` for the full status snapshot. Next recommended stage: 11-B2.

## Completed

### Stage 1 — UI Skeleton

- Web workspace foundation.
- Left project sections.
- Center chat.
- Right document/preview area.

### Stage 2 — OpenRouter Lawyers

- Three lawyers: Lawyer 1, Lawyer 2, Lawyer 3 / arbiter.
- One shared chat.
- Manual invocation of exactly one selected lawyer.
- Model/provider settings.
- Token and cost tracking.

### Stage 3 — Documents and Photos

- Upload: PDF, DOCX, XLSX, TXT, JPG/JPEG, PNG, WEBP.
- `StorageProvider`.
- Extraction/OCR path.
- Sensitivity metadata.
- `UNTRUSTED_DOCUMENT` prompt boundary.
- Role/sensitivity/trusted-provider enforcement.

### Stage 4 — Structured Legal Answers

- Strict JSON schema.
- Risk and confidence.
- Findings and sources.
- Citation verification.
- Red flags.
- Approval workflow.
- Monthly budget guard.

### Stage 5 — Verdict and GeneratedDocument

- One active verdict per chat.
- `GeneratedDocument`.
- Document generation only from the active verdict.
- Right editor.
- DOCX export.
- PDF fallback.
- Generated-document approval.
- Send generated document back to the shared chat without automatic LLM invocation.

### Stage 6 — Curated Legal RAG (complete)

- `LegalSource`.
- `LegalChunk`.
- ПП/ПКМ support.
- Law source verification.
- `TRUSTED_LEGAL_SOURCE`.
- `law_unconfirmed`.
- Freshness warning.
- SQLite lexical fallback for tests/dev.
- PostgreSQL + pgvector production target.

Smoke PASS:

```text
ПКМ №999
Пункт 3. Документы проверяются один раз в месяц.
correct quote -> confirmed
wrong quote -> unconfirmed, risk yellow, confidence medium
```

### Stage 7 — Factory Legal Base (complete)

Real official Uzbek legal sources loaded (contracts/obligations, customs, taxes, labor/HR,
occupational safety, production/certification, government bodies). Chunking, retrieval, citation
confirmation, freshness checks implemented and tested.

### Stage 8 — Company Profile (complete)

`CompanyProfile` model, admin CRUD API, and settings UI (`Настройки → Профиль компании`).
Stamp/signature fields are reserved in the model but upload/rendering is not implemented.

### Stage 9 — Document Templates (complete)

Basic debt/claim template with `CompanyProfile` substitution, DOCX export, and tests.

### Stage 11-A — Auth and Roles Foundation (complete)

Database-backed users, salted `scrypt` passwords, HTTP-only SameSite=Lax session cookies.
Login/logout/me/bootstrap endpoints. All workspace and admin routes protected.
Admin-only enforcement on settings/admin routes and CompanyProfile writes.

### Stage 11-B1 — Admin User Management (complete)

Admin can list, create, edit (name/role/active), deactivate, and reset passwords for users.
Last-active-admin protection. Session invalidation on deactivate/reset. Frontend settings modal
with section navigation, inline user creation, inline edit, inline password reset. Admin UI
is hidden from non-admin users including viewer. Self-registration is forbidden.

## Main Path Now

### Stage 11-B2 — Viewer Read-Only and Basic Audit Log

Do not implement until explicitly instructed. Scope is planned only.

Goal: enforce role-based read-only access and add a basic audit log.

Planned scope:

- `viewer` role can read allowed workspace areas but cannot create, update, or delete anything.
- `sales`, `supply`, `hr`, `accountant` roles get basic safe restrictions matching their category.
- Basic audit log for important actions:
  - login and logout;
  - user created, updated, and deactivated;
  - password reset;
  - CompanyProfile update;
  - template applied;
  - legal-source admin changes.

Acceptance criteria: viewer confirmed read-only in UI and API; audit entries appear for all listed
actions; admin can view recent audit log in settings.

### Stage 10 — Laptop Local Server

Goal: test and configure the user's laptop as a temporary local server for 3-4 users.

Check:

```text
backend
frontend
OpenRouter latency
upload documents
RAG
GeneratedDocument
3-4 users in local network
database size
uploads size
stability
```

Configure:

```text
start script
local IP
LAN access
firewall rule
backup
restore
restart script
logs
```

SQLite is acceptable only for tests/minimal local launch. Local PostgreSQL is preferred if practical. PostgreSQL remains the production target.

### Stage 11 — Roles and Local Auth (in progress)

Stage 11-A and 11-B1 are complete. Stage 11-B2 (viewer read-only and audit log) is next.
Remaining after 11-B2: HTTPS hardening, approval workflow, granular category permissions,
and multi-worker bootstrap lock hardening.

### Stage 12 — Final Factory Scenarios

Run end-to-end:

1. Client owes money.
2. Claim letter.
3. Supplier missed deadline.
4. Contract review.
5. Import contract.
6. Tax letter.
7. Customs letter.
8. HR question.
9. Occupational safety.
10. Certification/technical regulation.
11. State body reply.
12. Template document generation.
13. Director approval.
14. DOCX export.
15. Legal source verification.

### Stage 13 — Mini Launch

Prepare:

```text
user instruction
admin instruction
rules for legal source upload
rules for revision checks
rules for approval
rules for sensitive documents
backup schedule
restore guide
known limitations
```

Acceptance criteria: 3-4 users trained, instructions exist, backup exists, and responsible owners are assigned for legal base, templates, and technical launch.

## Later

### Stage 14 — Telegram

Telegram is postponed until:

- legal base is filled;
- templates are approved;
- local launch is stable;
- real users are working.

Telegram should be a quick entry point, not a replacement for the Web UI.

### Stage 15 — VPS / Full Server

VPS or a separate server is needed only if:

- the laptop cannot handle the load;
- 24/7 operation is required;
- there are more than 3-4 users;
- external access is required;
- stronger backups are required;
- production security is required.
