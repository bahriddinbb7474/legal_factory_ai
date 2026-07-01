# AGENTS.md - Legal Factory AI

## Purpose

This file contains stable working rules for Codex agents working on Legal Factory AI.

Do not treat this file as a current status snapshot. Current stage status, current branch, and current task scope must be provided separately in the active task context.

## Project Identity

- Project: Legal Factory AI
- Organization: Kabel Tech Energy
- Role: internal legal-tech system
- Project path: `E:\Projects\Projects_5\legal_factory_ai`

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

## Verification Rules

Run verification relevant to the change set.

- Run backend tests for backend-affecting work.
- Run frontend build when frontend code changes.
- Run `git diff --check`.
- Run `git status --short`.
- Report exact files changed and exact tests/checks run.

## Documentation Rules

`AGENTS.md` and `CLAUDE.md` are stable working-rules files, not current status snapshots.

Project context and current snapshot belong in `docs/CONTEXT.md`. Product scope, roadmap, and priorities belong in `docs/SPEC_AND_ROADMAP.md`; task-specific status may remain in task previews.
