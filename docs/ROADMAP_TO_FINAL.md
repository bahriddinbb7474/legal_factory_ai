# Roadmap to Final

Current status: Stages 1-6 are complete. Stage 6 smoke passed with curated legal RAG, ПП/ПКМ chunking, confirmed `source_type=law` citations, rejected wrong quotes, and freshness warnings.

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

### Stage 6 — Curated Legal RAG

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

## Main Path Now

### Stage 7 — Factory Legal Base

Goal: load 15-30 real official sources needed by the cable factory.

Priority categories:

- contracts and obligations;
- import and customs;
- taxes;
- labor and HR;
- occupational safety;
- production, certification, and technical regulation;
- government bodies.

Each source must include:

```text
document_type
title
document_number
adoption_date
revision_date
source_name
source_url
official_status
status=active
language
last_checked_at
next_check_due_at
```

Primary source: `LEX.UZ`.

Acceptance criteria:

- at least 15 real sources loaded;
- every source has a LEX.UZ URL and revision date;
- chunking succeeds;
- retriever finds expected clauses;
- lawyers cite `source_type=law`;
- correct quotes are confirmed;
- wrong quotes are rejected;
- stale revisions show warning.

### Stage 8 — Company Profile

Goal: store official company data and reuse it in generated letters and documents.

Planned `CompanyProfile` fields:

```text
full_name
short_name
legal_address
actual_address
tin
oked
registration_details
bank_name
mfo
settlement_account
currency_accounts
director_name
chief_accountant_name
legal_responsible_name
phone
email
website
logo_storage_key
letterhead_storage_key
stamp_storage_key
signature_storage_key
created_at
updated_at
```

UI: `Настройки -> Данные компании`.

Security: stamp/signature are sensitive; access only for director/admin; all changes go to `AuditLog`.

### Stage 9 — Document Templates

Goal: generate documents from approved factory templates, not free text.

Planned `DocumentTemplate` fields:

```text
id
name
document_type
category
language
version
status
content_template
required_fields
company_profile_fields
approval_required
created_at
updated_at
```

Statuses:

```text
draft
active
archived
```

Template categories:

- debts/claims;
- contracts;
- government bodies;
- HR;
- production/certification.

UI: `Настройки -> Шаблоны документов`.

Acceptance criteria: at least five active templates, template-based `GeneratedDocument`, CompanyProfile substitution, DOCX brand layout, archive old versions, preview, and tests.

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

### Stage 11 — Roles and Local Auth

Goal: remove the dev current-user stub.

Roles:

```text
admin
director
chief_accountant
legal_responsible
sales
supply
hr
accountant
viewer
```

Required: login/password, password change, disabled users, role assignment, current user without dev stub, backend role checks, approval restricted to director/chief_accountant where required.

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
