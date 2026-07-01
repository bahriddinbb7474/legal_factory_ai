# CLAUDE.md — Legal Factory AI

## Purpose

This file contains stable working rules for Claude Code when working on Legal Factory AI.

Do not treat this file as a full project status snapshot. Current stage status, current branch, and current task scope must be provided separately in each task.

## Project

Legal Factory AI is an internal AI legal workspace for Kabel Tech Energy, a cable manufacturing company.

Main stack:

- FastAPI / Python backend
- SQLAlchemy / Alembic
- SQLite dev database
- Next.js frontend
- local storage
- OpenRouter
- legal RAG
- document templates
- CompanyProfile
- auth / roles

## Read first

Use repository docs rather than memory:

1. `docs/README.md`
2. `docs/00_current/CONTEXT.md`
3. `docs/00_current/SPEC_AND_ROADMAP.md`
4. `docs/00_current/TESTS_AND_RISKS.md`
5. `docs/00_current/ARCHITECTURE.md`
6. Relevant `docs/10_policies/*`

Use `docs/20_sources/*` only for source/RAG tasks, `docs/30_guides/*` when needed, and `docs/40_stage_reports/*` only as historical evidence. Old flat docs paths are obsolete.

## Mandatory workflow

Always work step by step:

1. ANALYZE
2. PLAN
3. IMPLEMENT
4. VERIFY
5. COMMIT
6. STOP

Do not skip verification.

Do not start a new stage without explicit instruction.

Do not push unless the user explicitly asks.

## Safety rules

Never touch or commit:

- `.env`
- secrets
- API keys
- real credentials
- SQLite database files
- storage files
- raw legal texts
- real stamp/signature assets

Do not enable these unless a separate approved stage explicitly requires it:

- Telegram
- VPS/deployment
- pgvector
- LEX.UZ crawler
- mass historical legal text import
- stamp/signature upload or rendering

Do not change OpenRouter/provider/model settings unless explicitly requested. Automated tests must use mocks/fake providers and must never call real paid OpenRouter, vision, or embedding APIs.

## Dev URL rule

Always use `localhost` for both frontend and backend in development.

- Frontend: `localhost:3000`
- Backend: `localhost:8000`

Do not mix `localhost` and `127.0.0.1`. Session cookies use `SameSite=Lax`. Cross-origin requests
from `localhost:3000` to `127.0.0.1:8000` are treated as cross-site; the browser suppresses the
cookie on POST/PATCH/DELETE, causing 401 authentication errors.

## Auth and user rules

Users must not self-register.

Only an admin can create users.

The first admin is created only through bootstrap / initial setup.

After that, all users are managed only by admin.

Do not add public registration, invite links, email sending, or self-service signup unless explicitly approved later.

## Legal source rules

Ordinary legal RAG must use only active/official legal sources.

Future/draft/outdated/historical sources must not be mixed into ordinary active-law answers.

Do not mix trusted legal sources with untrusted uploaded documents without clear separation.

Normal pre-verdict answers are human-readable prose; structured payload is reserved for verdict workflow. Lawyer 1 cannot issue a verdict. Lawyer 2/3 verdict requires explicit permission and backend checks. `template_documents` has no default legal RAG or verdict flow.

## Stage discipline

Implement only the requested stage or substage.

P3-C is complete. P4 targeted RAG/source inventory/source package is next. P4/P5/P6 are not complete, and P5 must not start before P4 is approved and complete.

Keep changes minimal.

Prefer small focused commits.

If there is ambiguity, stop and report.

## Verification commands

Backend:

```bat
cd E:\Projects\Projects_5\legal_factory_ai\backend
..\.venv\Scripts\python.exe -m pytest
```

Frontend:

```bat
cd E:\Projects\Projects_5\legal_factory_ai\frontend
npm.cmd run build
```

Repo checks:

```bat
cd E:\Projects\Projects_5\legal_factory_ai
git diff --check
git status --short
git diff --stat
```

## Final report format

After every task, report:

1. Result: PASS / PASS WITH NOTES / FAIL
2. What changed
3. Tests/checks run
4. Files changed
5. Commit hash
6. Push status
7. Notes / risks
8. Recommendation
