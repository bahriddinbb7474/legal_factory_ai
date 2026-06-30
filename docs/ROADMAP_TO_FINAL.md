# Roadmap to Final

Current status: Stages 1–6, 7, 8, 9, 11-A, 11-B1, 11-B2, Demo-1 UI, **Stage A real chat/sidebar/history**, **P1 policy documentation**, and **P2-B0 through P2-B3** are complete.
See `CURRENT_STATE.md` for the full status snapshot.
Next priority: P3 section groups and policy routing, followed by P4-P6. OpenRouter/model settings is P7 / Phase B.

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

### Stage 4 — Structured Legal Answers (implemented legacy baseline)

- Strict JSON schema.
- Risk and confidence.
- Findings and sources.
- Citation verification.
- Red flags.
- Approval workflow.
- Monthly budget guard.

The approved P0 target supersedes strict JSON for every answer: P2-P6 must keep pre-verdict
answers human-readable and reserve the structured legal payload for verdict only.

### Stage 5 — Verdict and GeneratedDocument (implemented legacy baseline)

- One active verdict per chat.
- `GeneratedDocument`.
- Document generation only from the active verdict.
- Right editor.
- DOCX export.
- PDF fallback.
- Generated-document approval.
- Send generated document back to the shared chat without automatic LLM invocation.

P5 must replace simple active-message marking as the safety boundary with verified verdict
eligibility, explicit permission, Lawyer 2/3 authorship, bound sources, citation checks, and
backend-computed document-generation gates.

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

### Stage 11-B2 — Viewer Read-Only and Basic Audit Log (complete)

- `viewer` role is read-only: returns 403 on workspace mutations; safe GET routes available.
- Frontend: viewer write controls hidden; admin/settings hidden from non-admin.
- Basic audit log: login, logout, user created/updated/deactivated, password reset.
- Audit safety: no secrets in audit details. Admin reads entries with limit/offset.

### Demo-1 — New-Chat UI Cleanup (complete)

- Fake initial messages removed; empty new-chat state is now the default.
- ChatGPT-style start screen: centered composer block, title heading above input.
- Compact "Выбрать раздел" dropdown above the input field (placeholder until user picks).
- Selected section + first 60 chars of question generate chat title on first send.
- Lawyer selector chips below the input, visible in both empty and active chat states.
- No "Черновик" shown in empty-state topbar.
- Dead UI buttons removed. Corrupted Cyrillic fixed.
- Fake document panel data and raw model/provider display are intentionally deferred.

P1 policy commit: `768484a — docs: add prompt rag verdict policy v1` (local, not pushed).

---

## Stage A — Real Working Chat (complete)

Goal: replace all fake/static sidebar and chat data with real backend data.
No fake chats or sidebar entries in the main user flow.

### What was delivered

- Sidebar loads real chat list from `GET /api/chats`, grouped by section prefix in title.
- "New chat" button creates a real backend chat on first message send.
- Selected section + first question generate the title on first send.
- Chat appears under matching section group in sidebar after creation.
- Clicking sidebar chat loads real messages via `GET /api/chats/{id}/messages`.
- Reloading page and reopening chat restores full message history.
- All fake/static sidebar entries removed from main user flow.
- Author type visible (user/lawyer) with timestamps.
- Multiple chats can have pending AI answers simultaneously.
- AI lawyers receive full chat history before answering (universal system prompt + chat_context).
- Chat-specific history preserved in context, not system_prompt.
- Default lawyer prompts safely upgraded; custom admin prompts preserved.
- Stale AI response cannot append to wrong chat; tracking per-chat pending responses.

Acceptance: ✓ Open app, send question, see chat in sidebar under correct section, reload, reopen, see same messages with history.

---

## P0-P6 — Prompt/RAG/Verdict Safety Architecture

### P0 — Architecture (approved)

Approved target:

```text
section-based strictness
+ lawyer-controlled targeted RAG
+ backend safety net
+ human-readable pre-verdict answers
+ structured verdict only
+ Lawyer 1 cannot issue verdict
+ document button only after verified verdict
+ approved templates for канцелярия
+ red-topic approval everywhere
+ UNTRUSTED_DOCUMENT injection protection
```

### P1 — Policy Documentation (complete)

- `PROMPT_SYSTEM_V1.md`
- `RAG_WORKFLOW_V1.md`
- `LEGAL_RESPONSE_POLICY_V1.md`
- `VERDICT_AND_DOCUMENT_POLICY_V1.md`
- `QUALITY_GATE_V1.md`

### P2 — Prompt Flow Foundation (complete)

- P2-B0 protects public message creation and backend-owned fields.
- P2-B1 keeps pre-verdict lawyer responses as human-readable text.
- P2-B2 adds explicit Lawyer 2/3 verdict mode with a conservative unconfirmed skeleton.
- P2-B3 aligns frontend invocation and rendering with normal/verdict modes.

### P3 — Section Groups and RAG Policy Routing (next)

- **P3-A:** define stable internal codes, the `template_documents` and `legal_questions` groups, and safe mapping for existing free-text `Chat.section` values.
- **P3-B:** show both groups in the frontend while keeping visible labels separate from policy keys.
- **P3-C:** route Group 1 to approved-template flow and Group 2 to legal/RAG flow; red topics override either group.
- **P3-D:** test template boundaries, Lawyer 1 RAG behavior, Lawyer 2/3 verdict eligibility, and red-topic handling in both groups.

The approved group names, complete section list, proposed codes, and routing rules are normative in `SECTION_GROUPS_AND_RAG_POLICY.md`.

### P4 — Targeted RAG Protocol

- Source inventory instead of all chunks.
- Internal targeted RAG request.
- Concrete source package returned to the lawyer.
- Multilingual Russian and Uzbek Latin/Cyrillic trigger patterns.
- Backend fallback for missed RAG and unconfirmed-source blocking.

### P5 — Verified Verdict and Document Gate

- Structured payload only for verdict.
- Model content fields separated from backend-controlled gate fields.
- `source_package_id` and `context_snapshot_hash` binding.
- Citation verification only against the bound package.
- Configurable red-topic and UZS/USD large-amount rules.
- Document button only after backend verification and approval checks.
- Explicit mapping to `Message`, `RedFlagRule`, approval workflow, and `GeneratedDocument.status`.

### P6 — Quality Gate

Implement and pass all 38 checks in `QUALITY_GATE_V1.md`, including prompt behavior, RAG safety,
verdict verification, red topics, template boundaries, injection protection, and multilingual triggers.

---

## P7 / Phase B — OpenRouter and Model Settings

Goal: complete minimal working OpenRouter integration with admin model settings and clean
user-facing model UX. Must be done before RAG quality verification so test answers use real models.

Scope:

- OpenRouter API key via `.env` (not hardcoded, not committed).
- Admin model settings: assign model per lawyer (Lawyer 1, 2, 3).
- Display prices as `$ / 1M input tokens` and `$ / 1M output tokens`.
- User-facing modes: `Экономно`, `Быстро`, `Качественно` (map to model presets).
- Hide raw `model_id` strings from the normal chat UI; keep technical IDs in admin/logs only.
- Replace `$0.000000` cost display with either real cost or hidden when zero.

---

## Phase C — Company Details and Document Templates

Goal: replace fake document panel data with real generated documents based on real company data
and approved templates.

Scope:

- Enter real company requisites into `CompanyProfile` via admin settings.
- Approve and finalize document templates (at minimum: debt/claim letter, supply contract notice).
- Remove fake demo document data from the document panel.
- Generate real letters/claims/legal conclusions from the active verdict.
- Document statuses: draft / review / approved.
- Word export (DOCX already supported); PDF export as a follow-up if not already working.

---

## Phase D — Legal Base and RAG Verification

Goal: ensure the legal knowledge base is correct, current, and covers the main factory use cases.

Scope:

- Audit current legal sources: confirm active status, official status, freshness.
- Add missing key laws, ПКМ, and codes relevant to the factory's legal topics.
- Verify chunking quality, retrieval ranking, and source cards in real answers.
- Run 20–30 control legal questions across all main categories.
- Confirm that answers include source citations with correct quotes.
- Confirm uncertainty warnings appear for missing or outdated sources.

---

## Phase E — Real Factory Scenarios

Goal: end-to-end test of all main business workflows with real data and real AI answers.

Scenarios:

1. Debt / client claim — chat, RAG, claim letter generation, director approval.
2. Supply contract check — upload contract, human-readable analysis, verified verdict when requested, risk state, and sources.
3. Procurement risk question — procurement department user, supplier document upload.
4. HR question — HR user, labor code source, answer with citations.
5. Accounting/finance legal document question — accountant user, tax source, document generation.

Each scenario must cover: chat flow, RAG sources, generated document, saved history, sidebar,
UI clarity. No fake data must appear in any step.

---

## Phase F — Founder Presentation Polish

Goal: prepare a clean, coherent demo for the company founder with no visible rough edges.

Criteria:

- No fake data in any visible demo path.
- No raw technical errors on screen.
- No raw `model_id` strings in normal chat UI.
- Clean page load, clean new-chat start, clean source cards, clean generated document.
- Sidebar shows only real chats.
- At least one complete end-to-end scenario works without manual workarounds.

---

## After Presentation — Extended Permissions

Keep current baseline through the presentation:

- Admin-created users only, no self-registration.
- `viewer` role is read-only.
- Basic audit log covers auth and user management.

Improvements to consider after a successful presentation:

- Department-level visibility: users see only their section's chats.
- Approval routing: send to specific approver role based on risk level.
- Export rights: control who can export DOCX/PDF.
- Model settings rights: allow a "senior user" to switch modes without admin access.

---

## Later

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

SQLite is acceptable only for tests/minimal local launch. Local PostgreSQL is preferred if
practical. PostgreSQL remains the production target.

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
