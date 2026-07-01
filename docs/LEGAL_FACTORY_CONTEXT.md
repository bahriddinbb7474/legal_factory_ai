# Legal Factory AI — контекст проекта

Актуально на: 2026-07-01

> Это главный паспорт проекта для нового AI-чата. Сначала прочитайте этот файл, затем текущий статус и правила разработки.

## Паспорт

| Поле | Значение |
| --- | --- |
| Проект | Legal Factory AI |
| Организация | Kabel Tech Energy |
| Назначение | Внутреннее AI-пространство для юридической работы кабельного завода в Узбекистане |
| Основные пользователи | Директор/основатель, ответственный за юридические вопросы, бухгалтерия, HR, снабжение/закупки, продажи, производство и другие подразделения |
| Юрисдикция по умолчанию | Республика Узбекистан |
| Основной интерфейс | Русский |
| Языковая цель | Русский, узбекский (Latin/Cyrillic), английский, китайский и турецкий для входящих материалов и общения |
| Важная оговорка | Полная проверенная поддержка всех языков ещё не реализована: multilingual red-topic/RAG hardening для RU/UZ относится к P4/P6; UI остаётся русским |

## Идея продукта

Один общий чат хранит вопрос пользователя, документы и позиции трёх AI-юристов. Пользователь вручную выбирает одного юриста для очередного ответа; отдельного четвёртого AI-диспетчера нет. Слева находятся история и канонические разделы, в центре — чат, справа при необходимости открывается документ или preview.

- **Юрист 1** — первичный практический анализ, уточнения и awareness о необходимости официальных источников.
- **Юрист 2** — независимая проверка и сильное второе мнение.
- **Юрист 3** — сильный юрист/арбитр спорных позиций.
- До вердикта все юристы отвечают обычным читаемым текстом.
- Структурированный verdict разрешён только Юристу 2/3 после явного запроса пользователя.

## Текущее состояние

Завершены базовые этапы UI/API, загрузки документов, curated legal-source registry/retrieval, CompanyProfile, базовые шаблоны, auth/RBAC и real chat/history. Поверх legacy Stage 4/5 реализована новая policy foundation:

- **P0/P1** — утверждены и записаны prompt/RAG/response/verdict/quality policies.
- **P2-B0/B1/B2/B3** — защищён public message API, pre-verdict переведён в normal prose, добавлен консервативный verdict skeleton и согласован frontend invoke/rendering.
- **P3-A/B** — 17 стабильных `section_code`, две группы, legacy mapping и grouped UI.
- **P3-B1** — компактный collapsed sidebar и короткие display labels.
- **P3-C** — backend routing по `section_group`, template flow без default RAG/verdict, legal-flow context и общий red-topic override.

Последний application commit перед этим docs-stage: `2d168a8 feat: route behavior by section group`. P3-C локален и не отправлен; после локального commit текущей документации ветка `master` ожидаемо будет на два коммита впереди `origin/master`.

## Что готово сейчас

- Защищённый Web UI с login, admin-created users, ролями и viewer read-only.
- Реальные чаты, история, ownership/access checks и выбор одного из трёх юристов.
- Upload/извлечение PDF, DOCX, XLSX, TXT и изображений; sensitive-provider checks.
- Раздельный контекст `TRUSTED_LEGAL_SOURCE` и `UNTRUSTED_DOCUMENT`.
- Curated registry официальных источников, chunking, lexical dev/test retrieval и citation checks legacy-уровня.
- Normal pre-verdict ответы и explicit Lawyer 2/3 verdict skeleton.
- Backend-owned safety fields и запрет document generation для unconfirmed verdict skeleton.
- Две section groups: `template_documents` и `legal_questions`; неизвестный раздел безопасно становится `legal_other`.
- Red flags, approval state, cost tracking, CompanyProfile, базовый DocumentTemplate и legacy generated-document editor/export.

## Что ещё не готово

- P4 targeted RAG request protocol, source inventory и конкретный bound source package.
- `source_package_id` и `context_snapshot_hash`.
- P5 verified verdict/citation/approval gate и окончательный backend document-generation gate.
- Полный approved-template workflow для всех factory forms.
- P6: полный набор 38 quality checks и устойчивые RU/UZ morphological triggers.
- Production PostgreSQL/pgvector, production PDF rendering, backup/retention policy и laptop pilot.
- Founder-demo polishing после safety gates.
- Telegram, VPS/public deployment, crawler и другие отложенные интеграции.

## Стек

- Frontend: Next.js 15, React 19, TypeScript.
- Backend: Python 3.11+, FastAPI, Pydantic, SQLAlchemy async, Alembic.
- Текущая dev/test DB: SQLite; production target: PostgreSQL, позднее pgvector.
- LLM: OpenRouter abstraction с configurable agents/providers и mockable automated tests.
- Файлы: local storage provider; экспорт DOCX через `python-docx`, PDF пока lightweight fallback.

## Нельзя нарушать

- Не выдумывать законы, статьи, даты, названия и цитаты.
- Для current-law использовать только активные официальные источники; не смешивать их с untrusted uploads.
- Pre-verdict — обычный человеческий текст, не большой JSON.
- Юрист 1 не выпускает verdict; Юрист 2/3 — только после явного разрешения.
- Модель не управляет `confirmed_in_context`, `source_check_status`, `document_generation_allowed` и `approval_required`.
- Unconfirmed verdict не разрешает document generation.
- Template group не является обходом legal review/red-topic approval.
- Неизвестный/legacy раздел никогда не должен молча попасть в template flow.
- Self-registration запрещена; пользователей создаёт только admin.

## Следующий этап

**P4 — targeted RAG / source inventory / source package.** Нужно заменить временную legal-group retrieval compatibility на lawyer-controlled запрос, сформировать точный package перед ответом и подготовить binding для P5. Не начинать P5 gate до утверждённого результата P4.

## Порядок чтения

1. Этот файл.
2. [Текущий статус, тесты и риски](LEGAL_FACTORY_STATUS_TESTS_RISKS.md).
3. [Правила для coder-агентов](LEGAL_FACTORY_CODER_RULES.md).
4. По задаче: [спецификация и roadmap](LEGAL_FACTORY_SPEC_AND_ROADMAP.md), [архитектура](LEGAL_FACTORY_ARCHITECTURE.md), [решения и изменения](LEGAL_FACTORY_DECISIONS_AND_CHANGES.md).

Специализированные нормативные документы:

- [PROMPT_SYSTEM_V1.md](PROMPT_SYSTEM_V1.md) — prompt/role/output boundaries.
- [RAG_WORKFLOW_V1.md](RAG_WORKFLOW_V1.md) — целевой RAG/source workflow.
- [LEGAL_RESPONSE_POLICY_V1.md](LEGAL_RESPONSE_POLICY_V1.md) — виды ответов, missing-source и red-topic policy.
- [VERDICT_AND_DOCUMENT_POLICY_V1.md](VERDICT_AND_DOCUMENT_POLICY_V1.md) — verdict eligibility и document gates.
- [QUALITY_GATE_V1.md](QUALITY_GATE_V1.md) — 38 acceptance checks.
- [SECTION_GROUPS_AND_RAG_POLICY.md](SECTION_GROUPS_AND_RAG_POLICY.md) — группы, коды и routing policy.
