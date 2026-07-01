# Legal Factory AI — правила для coder-агентов

Актуально на: 2026-07-01

Этот файл дополняет корневой `AGENTS.md`. При конфликте active user task имеет приоритет над guidance, но не отменяет security/safety boundaries без явного решения владельца.

## Что читать

Всегда сначала:

1. [LEGAL_FACTORY_CONTEXT.md](LEGAL_FACTORY_CONTEXT.md).
2. [LEGAL_FACTORY_STATUS_TESTS_RISKS.md](LEGAL_FACTORY_STATUS_TESTS_RISKS.md).
3. Этот файл.

Для глубокой задачи:

- [LEGAL_FACTORY_ARCHITECTURE.md](LEGAL_FACTORY_ARCHITECTURE.md) — как устроен runtime.
- [LEGAL_FACTORY_SPEC_AND_ROADMAP.md](LEGAL_FACTORY_SPEC_AND_ROADMAP.md) — целевой продукт и порядок этапов.
- [LEGAL_FACTORY_DECISIONS_AND_CHANGES.md](LEGAL_FACTORY_DECISIONS_AND_CHANGES.md) — причины ограничений.
- Релевантный versioned policy: prompt, RAG, response, verdict, quality или sections.

Source of truth: текущие repo docs + code + tests + git status/log. Не полагайтесь на память предыдущего чата.

## Рабочий процесс

```text
ANALYZE → PLAN → IMPLEMENT → VERIFY → COMMIT → STOP
```

- Один task должен соответствовать одному утверждённому stage или узкому fix.
- Не переходить к следующему stage без user/architect approval.
- Не менять unrelated files «заодно».
- Если названия/пути из ТЗ устарели, найти фактическую структуру, выбрать корректное место и сообщить исправление.
- Analysis/review task не даёт разрешения менять код.

## Неприкосновенные правила

- Не менять OpenRouter models/provider settings, API keys или `.env`, если это не scope задачи.
- Не трогать DB/storage/raw legal texts без явного разрешения.
- Не ослаблять auth, ownership, admin-only или viewer read-only checks.
- Не принимать backend gate fields от пользователя или модели.
- Не разрешать final document из normal response, Lawyer 1 answer или unconfirmed verdict.
- Не считать цитату подтверждённой вне фактически переданного trusted source package.
- Не маршрутизировать unknown section в `template_documents`; fallback — `legal_other`.
- Сохранять legacy chat compatibility и canonical codes.
- Не смешивать `TRUSTED_LEGAL_SOURCE` и `UNTRUSTED_DOCUMENT`.
- Не добавлять Telegram, VPS/deployment, crawler, pgvector rollout, stamp/signature или mass import без отдельного stage.

Backend-owned fields:

```text
confirmed_in_context
source_check_status
document_generation_allowed
approval_required
```

Model output для них отсутствует, игнорируется или перезаписывается.

## Опасные зоны

Перед изменением найдите связанные tests и прочитайте специализированную policy:

- auth/sessions/roles и audit safety;
- public message creation schemas;
- `Chat.section`, legacy aliases и section policy routing;
- chat context и lawyer invoke orchestration;
- RAG active/official filtering и trust markers;
- verdict parsing, permission и active verdict state;
- generated-document creation/export/approval;
- legal-source registry/version lifecycle;
- sensitive documents и provider trust.

## Правила реализации

- Policy key — internal code, не UI label.
- Pre-verdict UI/API contract — plain text и `structured_payload=null`.
- Verdict contract — explicit mode, Lawyer 2/3, explicit permission, backend validation.
- Template group не запускает legal verdict/RAG по умолчанию и не обходит red flags.
- P4/P5 metadata добавлять только в утверждённом stage; не создавать «временный» небезопасный shortcut.
- Existing dirty worktree принадлежит пользователю; не удалять и не reset чужие изменения.
- Для локальных edits использовать минимальный diff и сохранять стиль проекта.

## Проверки

Всегда:

```powershell
git diff --check
git status --short
```

Backend change:

```powershell
cd backend
..\.venv\Scripts\python.exe -m pytest tests/<focused_tests>.py -q
..\.venv\Scripts\python.exe -m pytest tests -q  # когда затронут общий flow или риск высокий
```

Frontend change:

```powershell
cd frontend
npm.cmd run build
```

Docs-only change не требует application tests, если code не затронут. В отчёте указывать, почему тесты не запускались.

## Manual smoke format

Для каждой изменённой ветки поведения записать:

```text
Setup / role / section
User action or phrase
Expected API mode/status
Expected visible result
Forbidden result
```

Пример для legal verdict:

```text
Section: legal_hr; Lawyer 2
Action: «ок. оформи свой вердикт тогда!»
Expected: mode=verdict, unconfirmed skeleton
Visible: verdict warning, no raw JSON
Forbidden: document button or document_generation_allowed=true
```

## Task/report contract

Хорошее coder-ТЗ содержит:

- цель и текущий stage;
- authoritative docs;
- in-scope/out-of-scope;
- acceptance checks и stop conditions;
- требуемые tests/build;
- commit message и push policy.

Финальный отчёт всегда содержит:

- что сделано;
- точные изменённые файлы;
- команды и результаты проверок;
- manual smoke result или явное «не запускался»;
- ограничения/следующий stage;
- `git status --short`.

## Git

- Один логический stage = один commit.
- Commit message описывает outcome (`feat:`, `fix:`, `docs:`).
- Stage только файлы текущей задачи.
- Не использовать destructive reset/checkout для чужих изменений.
- Не push, если пользователь прямо не попросил.
- После commit снова проверить `git status --short`.

