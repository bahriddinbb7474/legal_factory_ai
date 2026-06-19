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

## Stage discipline

Implement only the requested stage or substage.

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
