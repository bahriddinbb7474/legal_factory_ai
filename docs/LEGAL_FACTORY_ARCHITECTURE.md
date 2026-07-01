# Legal Factory AI — компактная архитектура

Актуально на: 2026-07-01

## Стек

| Слой | Реализация |
| --- | --- |
| Frontend | Next.js 15, React 19, TypeScript |
| Backend | Python 3.11+, FastAPI, Pydantic, SQLAlchemy async |
| Миграции | Alembic |
| Dev/test DB | SQLite / aiosqlite |
| Production target | PostgreSQL; pgvector остаётся целевым, но не текущим runtime requirement |
| LLM | OpenRouter gateway, configurable agents/providers, provider allowlist |
| Файлы | `StorageProvider` abstraction, локальное хранилище первой версии |
| Parsing/export | pypdf, python-docx, openpyxl; DOCX export, lightweight PDF fallback |

## Общая схема

```text
Next.js workspace
  ├─ grouped sidebar + chat history
  ├─ central shared chat + lawyer selector
  └─ upload/document panel
          ↓ authenticated HTTP API
FastAPI
  ├─ auth/RBAC and ownership
  ├─ chat/message/invoke orchestration
  ├─ section policy + red flags + approvals
  ├─ document extraction/storage
  ├─ curated legal source retrieval
  └─ verdict/generated-document workflows
          ↓
SQLAlchemy models + local files + OpenRouter
```

## Backend

Основные entry points:

- `backend/app/main.py` — FastAPI app и регистрация routers.
- `backend/app/api/chats.py` — chat/message/invoke, normal/verdict orchestration, approval и verdict-document bridge.
- `backend/app/api/auth.py`, `admin.py` — session auth, admin-created users и audit reads.
- `backend/app/api/documents.py` — upload, links, extracted content и access checks.
- `backend/app/api/legal_sources.py` — admin registry, source ingestion и chunk inspection.
- `backend/app/api/generated_documents.py` — legacy generated-document lifecycle/export/send-back.

Ключевые services:

- `section_policy.py` — 17 canonical codes, 2 groups, display labels, legacy aliases и P3-C policy context.
- `chat_context.py` — author-labelled history, section policy, trusted/untrusted context composition.
- `llm_gateway.py` — OpenRouter transport boundary.
- `legal_retriever.py`, `legal_chunker.py` — текущий curated retrieval/chunking foundation.
- `verdict_response.py` — verdict-only structured parsing/repair.
- `structured_response.py` — safe normal-response fallback и legacy structured helpers.
- `red_flags.py` — configurable red-topic detection и `needs_review` transition.
- `citation_verifier.py` — legacy deterministic quote verification.
- `document_extractor.py`, `document_access.py`, `generated_documents.py` — file/document boundaries.
- `auth.py`, `current_user.py`, `audit.py`, `budget.py`, `costs.py` — security и operational controls.

## Frontend

- `frontend/app/page.tsx` — основной workspace; auth, chat/invoke, message rendering, uploads, settings и document panel. Это крупный монолит и известная maintainability-зона.
- `frontend/app/components/Sidebar.tsx` — collapsed grouped sidebar/history.
- `frontend/app/sections.ts` — стабильные section codes, display labels и frontend legacy mapping.
- `frontend/app/globals.css` — layout и visual styles.

Frontend отправляет `section_code`, но показывает только label. Verdict mode выбирается консервативно по explicit phrases только для Lawyer 2/3; backend остаётся окончательным guard.

## Данные

Полезный уровень моделей:

- Identity/security: `Role`, `User`, `AuthSession`, `AuditLog`.
- Conversation: `Agent`, `Chat`, `Message`, `CostRecord`, `Approval`.
- Files: `Document`, `ChatDocument`, `MessageDocument`.
- LLM config: `ProviderConfig`, `ModelConfig`.
- Legal base: `LegalSource`, `LegalChunk`, `RedFlagRule`.
- Documents: `CompanyProfile`, `DocumentTemplate`, `GeneratedDocument`.

`Chat.section` хранит canonical code для новых чатов. Legacy labels нормализуются при input/read; unknown values → `legal_other`, то есть безопасно в `legal_questions`.

## Section policy

```text
section value → normalize_section_code → SectionDefinition
→ section_code + section_group + ui_label
```

- `template_documents`: plain template/drafting context, legacy auto-RAG пропускается, verdict mode backend-ом запрещён.
- `legal_questions`: legal context; Lawyer 1 получает source-check/clarification instruction. До P4 сохраняется существующий retrieval compatibility.
- Display label не участвует в policy routing.
- Red flags применяются в обеих группах на backend.

## Response modes

### Normal

Все юристы могут дать pre-verdict plain text. Public message creation принимает только user-owned content; risk/gate/structured fields контролируются backend. Raw JSON не должен показываться пользователю.

### Verdict skeleton

Только Lawyer 2/3, только explicit permission, только в `legal_questions`. Model content проходит schema validation/repair; backend принудительно сохраняет новый verdict как `source_check_status=unconfirmed` и `document_generation_allowed=false`. Это foundation, не P5 verified verdict.

## Текущее состояние RAG

Curated `LegalSource/LegalChunk`, active+official filtering, lexical fallback и trusted source blocks существуют. После P3-C template sections не запускают default retrieval; legal sections пока используют текущий retrieval. P4 должен добавить source inventory, lawyer-controlled targeted request, concrete package и missed-RAG fallback. Bound package metadata ещё нет.

## Где допустим LLM

- Анализ фактов и документов.
- Clarifying questions, preliminary opinions и review.
- Выбор topics/source scope в будущем P4 protocol.
- Legal content verdict payload после permission.
- Draft content внутри разрешённого template/document workflow.

## Где LLM не является authority

- Auth, ownership, roles и sensitive-provider access.
- Official/current source status и quote verification.
- Red-topic/approval workflow.
- Verdict eligibility и author/permission checks.
- `confirmed_in_context`, `source_check_status`, `document_generation_allowed`, `approval_required`.
- Section normalization/routing.
- Generated-document status и export permissions.

## Security summary

- HTTP-only SameSite=Lax sessions; localhost origin consistency важна в dev.
- Self-registration отсутствует; bootstrap только для первого admin, далее users создаёт admin.
- Workspace/admin routes защищены; viewer read-only.
- Password hashes/tokens/secrets запрещены в responses и audit details.
- Uploaded content помещается в `UNTRUSTED_DOCUMENT`; sensitive documents требуют trusted provider.
- Active official law и uploaded factual material разделены.

## Ограничения

- `page.tsx` слишком велик и объединяет много UI concerns.
- SQLite — только dev/test/minimal pilot, не production target.
- Targeted RAG/source package и verified P5 gate отсутствуют.
- PDF export не production-grade.
- Red-topic keywords пока ограничены и недостаточно морфологичны/multilingual.
- Legacy Stage 5 endpoints/data model существуют рядом с новой policy foundation; backend guards нельзя ослаблять.

