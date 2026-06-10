# AGENTS.md — Codex Working Protocol

This file defines how Codex must work in this repository.

## 1. Core behavior

Codex must work carefully, step by step, and never make broad uncontrolled changes.

Default mode:

```text
ANALYZE → PROPOSE PLAN → WAIT FOR USER APPROVAL → IMPLEMENT STEP BY STEP → VERIFY → COMMIT → REPORT
```

Codex must not jump directly into implementation unless the user explicitly gives an IMPLEMENT task.

---

## 2. General rules

Always follow these rules:

* Read this `AGENTS.md` before starting.
* Work from the project root.
* Keep changes minimal and focused.
* Do not refactor unrelated code.
* Do not change architecture unless the task requires it.
* Do not touch secrets, tokens, API keys, `.env`, credentials, production DB, or deployment files unless explicitly instructed.
* Do not run destructive commands.
* Do not push to remote unless the user explicitly says to push.
* Do not install global dependencies unless explicitly approved.
* Do not run production services unless explicitly approved.
* If something is unclear, risky, or verification fails, stop and report.

---

## 3. Git rules

Before any work:

```bash
git status --short
```

If the working tree is not clean, STOP and report.

After every completed implementation step:

1. Run verification for that step.
2. If verification passes, commit that step.
3. Continue to the next step.

Commit format should be short and specific:

```bash
git add <changed-files>
git commit -m "Add concise step description"
```

Do not push unless the user explicitly says:

```bash
git push
```

Final report must include:

```text
1. Steps completed
2. Commits created
3. Files changed
4. Behavior added
5. Tests/verification results
6. Known limitations / next steps
7. Final git status
8. Push status
9. Stop
```

---

## 4. Two-phase stage workflow

Every project stage must be handled in two separate phases.

---

# Phase A — READ-ONLY ANALYSIS

When the user gives a stage plan and asks Codex to study the project, Codex must use:

```text
Mode: READ-ONLY ANALYSIS ONLY
```

In this mode Codex must:

* Inspect the current codebase.
* Read relevant docs.
* Read tests.
* Identify existing reusable services.
* Identify risks.
* Identify missing configuration, credentials, API keys, local setup, or manual user actions.
* Propose a safe implementation plan.
* Do not modify files.
* Do not commit.
* Do not run migrations.
* Do not run production services.
* Do not touch production data.

The report must include:

```text
1. Current state
2. Existing reusable code/services
3. Recommended implementation scope
4. What should be postponed
5. Required config/API keys/manual user actions
6. Proposed implementation steps
7. Risks / open decisions
8. Tests to add
9. Stop
```

Important: if the stage needs API keys, credentials, `.env` variables, external accounts, migrations, Docker setup, cloud access, database backup, or manual approval, Codex must clearly separate:

```text
User must provide / configure:
- ...
```

and must not invent credentials or write fake real keys.

---

# Phase B — IMPLEMENT

Only after the user gives a specific implementation task, Codex may modify files.

Implementation must be step-based.

Each step must have:

```text
Step X — clear title
Goal:
Files likely changed:
Verification:
Commit:
```

Codex must complete one step at a time.

After each step:

```text
run verification → if PASS commit → continue
```

If any verification fails:

```text
STOP.
Report the exact error.
Do not continue.
Do not commit broken code.
```

If the step creates tests that cannot pass until implementation exists, Codex may combine test + implementation into one TDD slice, but must report this clearly.

---

## 5. Verification rules

Use project-appropriate verification.

Examples:

### Python

Prefer project virtual environment or documented Python path.

Possible checks:

```bash
python -m py_compile <changed-python-files>
python -m pytest <specific-tests>
```

If the project uses a custom Python command, use the documented command.

Do not install dependencies globally.

If Python environment is broken, Codex must search for a safe existing Python environment and report all attempts.

### Node / frontend

Possible checks:

```bash
npm test
npm run build
npm run lint
```

Only run commands relevant to the changed files.

### Database

For database-related changes:

* Use temp DB only.
* Do not touch production DB.
* Do not run migrations on production DB.
* If a migration is needed, create migration file and test on temp DB or copied DB only.
* Clearly report that production migration requires user backup + approval.

### External APIs

For API-related features:

* No real provider calls in tests.
* Use fake/mock provider tests.
* Do not log tokens or secrets.
* Do not add real API keys to repository.
* `.env.example` may contain variable names only, never real values.

---

## 6. Safety rules

Codex must stop and report if:

* working tree is dirty before starting;
* production DB may be touched;
* migration may affect real data;
* API key or secret is required but missing;
* task requires external account setup;
* tests fail;
* code behavior is unclear;
* implementation requires broad refactor;
* user approval is needed;
* command may be destructive.

Codex must never hide failures.

---

## 7. API keys and secrets

Never commit real secrets.

Allowed:

```env
OPENAI_API_KEY=
GOOGLE_CLIENT_SECRET_PATH=
STT_PROVIDER=disabled
AI_PROVIDER=disabled
```

Not allowed:

```env
OPENAI_API_KEY=real_key_here
```

When a stage needs API access, Codex must say:

```text
User must configure:
- variable name
- where to put it
- how to test it safely
- whether it is optional or required
```

Default provider behavior should be disabled unless explicitly enabled.

---

## 8. External provider policy

Any integration with AI, STT, Google, payment systems, cloud, email, storage, or other external services must follow:

* provider disabled by default;
* fake provider for tests;
* no network calls in tests;
* timeout and failure fallback;
* no tokens in logs;
* no secrets in commits;
* user confirmation before enabling real provider;
* clear cost/rate-limit notes if relevant.

---

## 9. User-confirmation policy

For actions that create, update, delete, send, sync, deploy, migrate, or call paid APIs:

Codex must require explicit user approval unless the current task explicitly authorizes that action.

Examples requiring approval:

* database migration on real DB;
* push to remote;
* deploy;
* production restart;
* deleting files/data;
* enabling real API provider;
* sending emails/messages;
* writing to Google Calendar;
* changing `.env` with real secrets.

---

## 10. Implementation step template

When user gives a stage implementation task, Codex should follow this internal template:

```text
Before starting:
1. Read AGENTS.md.
2. Run git status --short.
3. If dirty, STOP and report.
4. Inspect relevant files.

For each step:
1. Implement minimal change.
2. Run targeted verification.
3. If PASS, commit.
4. If FAIL, STOP and report.

No push.

Final report:
1. Steps completed
2. Commits created
3. Files changed
4. Behavior added
5. Tests/verification results
6. Known limitations / next steps
7. Final git status
8. Push status: not pushed unless user requested
9. Stop
```

---

## 11. Markdown stage analysis prompt template

Use this when the user gives a new stage and asks for analysis:

```text
Mode: READ-ONLY ANALYSIS ONLY — Stage <N> Planning.

Goal:
Study the current project and propose the safest implementation plan for Stage <N>: <stage name>.

Rules:
- Do not modify files.
- Do not refactor.
- Do not change DB/schema.
- Do not run migrations.
- Do not run production services.
- Do not touch production data.
- Do not call real external providers.
- Use safe inspection commands only.

Analyze:
1. Current state
2. Existing reusable code/services
3. Recommended scope
4. What should be postponed
5. Required config/API keys/manual user actions
6. Proposed implementation steps
7. Risks / open decisions
8. Tests to add
9. Stop

Do not implement anything.
```

---

## 12. Markdown implementation prompt template

Use this when the user approves implementation:

```text
Mode: IMPLEMENT — Stage <N> <stage name>.

Goal:
<clear goal>

Rules:
- Minimal changes only.
- One step at a time.
- After each successful step: verify, then git commit.
- Do NOT push.
- If verification fails or behavior is unclear: STOP and report.
- Do not touch production data.
- Tests must use temp DB/mocks/fakes where relevant.
- Do not call real external providers unless explicitly approved.
- Do not add real API keys.

Before starting:
1. Read AGENTS.md.
2. Run git status --short.
3. If dirty, STOP and report.

Step <N>.1 — <title>
- Implement ...
- Verify ...
- Commit:
  `<commit message>`

Step <N>.2 — <title>
- Implement ...
- Verify ...
- Commit:
  `<commit message>`

Final:
- Do NOT push.
- Final report:
  1. Steps completed
  2. Commits created
  3. Files changed
  4. Behavior added
  5. Tests/verification results
  6. Known limitations / next steps
  7. Final git status
  8. Push status
  9. Stop
```

---

## 13. Response style

Be concise, factual, and practical.

Do not write long theory unless needed.

When reporting an issue, include:

```text
Problem:
Cause:
Files involved:
What I tried:
Recommended next action:
Stop.
```

When successful, include exact commits and exact verification results.

---

## 14. Final rule

Codex is not allowed to “continue creatively” beyond the approved stage scope.

If a better architecture is discovered, Codex must report it as a recommendation, not implement it without approval.
