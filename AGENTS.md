# AGENTS.md - Legal Factory AI

## Purpose

This file contains stable working rules for Codex agents working on Legal Factory AI.

Do not treat this file as the detailed status snapshot. Read the active project documents below and use the active task context for branch/task scope. Do not trust memory over repository documentation.

## Project Identity

- Project: Legal Factory AI
- Organization: Kabel Tech Energy
- Role: internal legal-tech system
- Project path: `E:\Projects\Projects_5\legal_factory_ai`

## Required Reading Order

Before implementation, read only as much as the task needs, in this order:

1. Root `README.md`
2. `docs/00_current/CONTEXT.md`
3. `docs/00_current/SPEC_AND_ROADMAP.md`
4. `docs/00_current/TESTS_AND_RISKS.md`
5. `docs/00_current/ARCHITECTURE.md`
6. `docs/00_current/DECISIONS_LOG.md`
7. Relevant `docs/10_policies/*` for the task
8. Relevant `docs/20_sources/*` only for legal-source/RAG work
9. Relevant `docs/30_guides/*` only when needed
10. `docs/40_stage_reports/*` only for history or evidence, never as current truth

Documentation roles:

- `docs/00_current/` is the first source of truth for context, status, roadmap, architecture, decisions, tests, and risks.
- `docs/10_policies/` contains active prompt, RAG, response, verdict/document, section, and source-version policies.
- `docs/20_sources/` contains the legal source registry and admin/source maintenance rules.
- `docs/30_guides/` contains development, user, UI, and AI-agent guidance.
- `docs/40_stage_reports/` is historical implementation/acceptance evidence, not active policy.

Old flat `docs/<file>.md` paths are obsolete. Use the grouped paths above.

## Core Workflow

Follow this workflow:

1. ANALYZE
2. PLAN
3. IMPLEMENT
4. VERIFY
5. COMMIT
6. STOP

For analysis-only tasks, do not edit files.

Do not continue to the next stage without architect or user approval.

## Safety Rules

- No public registration and no self-registration.
- Users must be created only by admin.
- Do not touch `.env`, secrets, API keys, DB files, storage files, or raw legal texts unless explicitly requested.
- Do not add Telegram, VPS/deployment, pgvector, LEX.UZ crawler, stamp/signature features, or mass historical import unless explicitly staged and approved.
- Do not change OpenRouter/provider/model settings unless the active task explicitly requests it.
- Automated tests must use mocks/fake providers and must not call real paid OpenRouter, vision, or embedding APIs.
- Do not push unless explicitly requested.

## Auth and RBAC Rules

- Anonymous access must remain blocked for workspace and admin routes.
- Admin-only routes must stay admin-only.
- Viewer must remain read-only once Stage 11-B2 is implemented.
- Never return password hashes or session tokens in API responses, logs, or UI payloads.

## Legal and RAG Rules

- Ordinary RAG must use active official legal sources only.
- Outdated, historical, draft, or future legal sources must not be mixed into active legal answers without clear separation.
- Never mix trusted legal source context with untrusted documents without clear labeling.
- Normal pre-verdict answers are human-readable prose. Structured payload is reserved for verdict workflow.
- Lawyer 1 cannot issue a verdict. Lawyer 2/3 verdict requires explicit user permission and backend checks.
- `template_documents` does not use default legal RAG or verdict; it must not bypass red-topic/legal review.
- P3-C is complete. P4 targeted RAG/source inventory/source package is next.
- P4, P5 verified verdict/document gates, and P6 full quality acceptance are not complete.
- Do not implement P5 before P4 is approved and complete.

## Verification Rules

Run verification relevant to the change set.

- Run backend tests for backend-affecting work.
- Run frontend build when frontend code changes.
- Run `git diff --check`.
- Run `git status --short`.
- Report exact files changed and exact tests/checks run.

## Documentation Rules

`AGENTS.md` and `CLAUDE.md` are stable working-rules files, not current status snapshots.

Project context and current snapshot belong in `docs/00_current/CONTEXT.md`. Product scope, roadmap, and priorities belong in `docs/00_current/SPEC_AND_ROADMAP.md`; task-specific status may remain in task previews.
