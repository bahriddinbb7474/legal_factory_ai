# Legal Factory AI — спецификация и roadmap

## 1. Назначение документа

Этот документ объединяет продуктовую спецификацию Legal Factory AI, границы текущего MVP, этапы реализации, приоритеты до финального состояния и направления после MVP. Он предназначен для владельца проекта, AI-архитектора и разработчика.

Главный паспорт проекта и текущий snapshot находятся в [CONTEXT.md](CONTEXT.md). Нормативные правила prompt/RAG/verdict workflow остаются в профильных policy-документах и имеют приоритет над краткими формулировками здесь.

## 2. Изначальный план проекта

Legal Factory AI — внутреннее юридическое AI-пространство для кабельного завода в Узбекистане. Основной продуктовый замысел:

- веб-интерфейс в стиле ChatGPT;
- один общий чат с общей историей обсуждения;
- три AI-юриста с разными ролями;
- загрузка и анализ документов и фотографий;
- юридический RAG по официальным источникам Республики Узбекистан;
- подготовка проектов писем, претензий, заключений и других документов;
- согласование рискованных вопросов и документов ответственными пользователями;
- учёт токенов, моделей и стоимости запросов;
- Telegram и серверное развёртывание только после стабилизации безопасного основного workflow.

Система помогает готовить предварительный анализ и проекты документов, но не заменяет живого юриста, директора, главного бухгалтера или иного ответственного специалиста.

## 3. Что входит в MVP

### Практические сценарии завода

- проверка локальных договоров;
- проверка импортных договоров;
- анализ дебиторской и кредиторской задолженности;
- подготовка писем по задолженности и претензий;
- анализ писем налоговых и других государственных органов;
- ответы на кадровые и трудовые вопросы;
- подготовка писем, претензий, служебных записок и предварительных юридических заключений.

### Реализованный фундамент MVP

- рабочий веб-чат;
- три роли AI-юристов и выбор одного юриста для конкретного обращения;
- загрузка PDF, DOCX, XLSX, TXT и изображений;
- основа правой панели просмотра/редактирования документа;
- политика юридического ответа, требующая подтверждённых источников для финального вывода;
- уровни риска, red-topic detection и состояние согласования;
- базовая аутентификация, роли, admin-only управление пользователями и read-only роль `viewer`;
- учёт использования и стоимости;
- реестр и curated-база официальных юридических источников;
- профиль компании;
- базовые шаблоны документов;
- реальные чаты, sidebar и сохраняемая история;
- 17 canonical section codes и backend-controlled маршрутизация по двум функциональным группам.

## 4. Что НЕ входит в текущий MVP

- публичная регистрация и self-registration;
- сложная аналитика судебной практики;
- полностью автоматический ежедневный мониторинг законодательства;
- интеграция с ERP или 1C;
- сложный workflow engine;
- отдельное мобильное приложение;
- полная юридическая экспертиза по иностранному праву;
- Telegram, VPS и публичное развёртывание;
- crawler LEX.UZ и массовый импорт источников или исторических редакций;
- загрузка и отображение печати/подписи;
- production-grade PDF rendering;
- расширенные права по подразделениям, маршрутизация согласований и детальные export permissions.

## 5. Этапы реализации

### Завершённые этапы

- **Stage 1 — UI skeleton:** основа web workspace, sidebar, центральный чат и правая панель.
- **Stage 2 — OpenRouter lawyers:** фундамент трёх AI-юристов, общий чат, выбор юриста, модели и учёт стоимости.
- **Stage 3 — Documents and photos:** загрузка, извлечение текста/OCR, storage abstraction, sensitivity metadata и граница `UNTRUSTED_DOCUMENT`.
- **Stage 4 — Legacy structured legal answers:** базовые structured responses, risk/confidence, citations, red flags, approval и budget guard.
- **Stage 5 — Legacy verdict and `GeneratedDocument`:** active-verdict storage/API, редактор, export, approval lifecycle и отправка результата обратно в чат.
- **Stage 6 — Curated legal RAG:** `LegalSource`, `LegalChunk`, active/official filtering, citation verification и lexical fallback.
- **Stage 7 — Factory legal source base:** реальные официальные источники, chunking, retrieval, freshness и citation smoke checks.
- **Stage 8 — Company profile:** модель, admin CRUD и UI профиля компании.
- **Stage 9 — Basic document templates:** базовый debt/claim template, подстановка данных компании и DOCX export.
- **Stage 11-A/B1/B2 — Auth and roles:** login/session, admin-created users, admin management, read-only `viewer` и базовый audit log.
- **Demo-1 — New-chat UI cleanup:** чистое состояние нового чата, реальный composer и удаление fake chat data из основного chat flow.
- **Stage A — Real chat/sidebar/history:** реальные чаты и сообщения, reload-safe история, ownership/access control и передача истории юристам.
- **P0/P1 — Policy architecture:** утверждены и документированы prompt, RAG, legal response, verdict/document и Quality Gate правила.
- **P2-B0/B1/B2/B3 — Prompt flow foundation:** безопасное создание сообщений, обычный pre-verdict текст, консервативный verdict skeleton и согласованная frontend/API интеграция.
- **P3-A/B/B1/C — Section behavior:** canonical section model, grouped UI, compact/collapsed sidebar и backend section-policy routing.

Stage 4 и Stage 5 являются **legacy foundation**, а не финальной политикой. P2 заменил обязательный JSON для обычных ответов на human-readable pre-verdict текст. P4 и P5 должны заменить общий retrieval и простой active-verdict baseline на targeted RAG, привязку источников и проверяемые backend-controlled gates.

## 6. Текущее состояние

Последний завершённый этап — **P3-C**.

Реализовано:

- 17 canonical section codes;
- две backend-owned группы:
  - `template_documents`;
  - `legal_questions`;
- `template_documents` не запускает RAG или verdict по умолчанию;
- verdict mode заблокирован в template sections;
- `legal_questions` получает legal-flow policy context;
- Lawyer 1 в legal sections обязан проверить/запросить официальные источники либо задать уточняющий вопрос до финального вывода;
- red-topic detection применяется в обеих группах;
- неизвестные и legacy section values безопасно нормализуются в `legal_other` и не могут случайно попасть в template flow;
- видимые русские названия разделов не являются policy keys.

Последняя проверка:

- P3-C focused backend tests: **113 passed**;
- полный backend suite после P3-C: **249 passed**;
- frontend production build после P3-B1: **passed**;
- P3-C не менял frontend.

Не реализованы:

- P4 targeted RAG/source inventory/source package;
- `source_package_id` и `context_snapshot_hash`;
- P5 verified verdict/document gate;
- полная проверка 38 пунктов P6 Quality Gate.

## 7. План до финала

### P4 — Targeted RAG / source inventory / source package

**Статус: не реализован; следующий этап.**

Нужно:

- передавать юристу компактный source inventory вместо всех chunks;
- добавить внутренний targeted RAG request;
- возвращать юристу конкретный source package;
- использовать только допустимые active/official источники для обычного current-law flow;
- добавить backend fallback, если legal flow пропустил обязательный RAG;
- подготовить метаданные для будущих `source_package_id` и `context_snapshot_hash`;
- начать усиление RU/UZ trigger patterns либо подготовить основу для полного покрытия в P6.

### P5 — Verified verdict and document gate

**Статус: не реализован.**

Нужно:

- разрешать verdict только Lawyer 2 или Lawyer 3;
- требовать явное разрешение пользователя;
- привязать verdict к конкретному source package;
- привязать verdict к context snapshot;
- детерминированно проверять citations и источники только в привязанном package;
- вычислять `confirmed_in_context`, `source_check_status`, `document_generation_allowed` и `approval_required` только на backend;
- показывать кнопку создания документа только после backend verification и выполнения approval requirements;
- не считать обычный ответ, Lawyer 1 response или простой legacy active-verdict marker достаточным основанием для документа.

### P6 — Quality Gate

**Статус: не реализован полностью.**

Нужно реализовать и пройти все 38 проверок из `QUALITY_GATE_V1.md`, включая:

- prompt behavior;
- RAG и source safety;
- verdict verification;
- red-topic behavior и approval;
- границы `template_documents`;
- защиту от prompt injection через `UNTRUSTED_DOCUMENT`;
- multilingual triggers для русского, узбекского Latin и узбекского Cyrillic.

### P7 / Phase B — OpenRouter and model settings

**Статус: позже.**

Нужно:

- хранить API key только в `.env`;
- завершить admin model settings;
- добавить понятные пользователю режимы качества/скорости/стоимости;
- скрыть raw `model_id` из обычного UI;
- показывать стоимость в понятном формате или скрывать нулевое значение.

### Phase C — Company details and templates

**Статус: позже.**

Нужно:

- внести реальные реквизиты компании;
- утвердить заводские шаблоны и их владельцев;
- убрать fake/demo data из правой панели;
- создавать реальные письма, претензии и юридические заключения только через соответствующий безопасный путь: approved template gate или verified P5 verdict gate;
- довести статусы и редактирование документов до рабочего процесса.

### Phase D — Legal base and RAG verification

**Статус: позже.**

Нужно:

- провести аудит юридических источников, их статусов и актуальности;
- добавить недостающие законы, кодексы, ПП и ПКМ;
- проверить chunking и retrieval на контрольных вопросах;
- проверить корректность цитат, source cards и warnings для отсутствующих/устаревших источников.

### Phase E — Real factory scenarios

**Статус: позже.**

Нужно провести end-to-end тестирование как минимум для:

1. задолженности клиента и претензии;
2. проверки договора поставки;
3. procurement risk;
4. кадрового/трудового вопроса;
5. бухгалтерского, налогового или юридического документа.

Каждый сценарий должен проверять chat flow, источники, approvals, документ, историю и понятность UI без fake data.

### Phase F — Founder presentation polish

**Статус: позже.**

Критерии:

- в demo path нет fake data;
- normal UI не показывает raw technical model IDs;
- sidebar, чат, sources и документы выглядят согласованно;
- нет необработанных технических ошибок;
- минимум один end-to-end сценарий проходит без ручных обходов.

## 8. Что будет после MVP / после founder demo

- hardening production storage и базы данных;
- окончательное решение по PostgreSQL/pgvector;
- backup/restore и проверка восстановления;
- LAN/laptop pilot для 3–4 пользователей;
- расширенные permissions и section visibility;
- approval routing по ролям и рискам;
- улучшенный document/PDF rendering;
- Telegram только после стабилизации web workflow;
- VPS/отдельный сервер только при необходимости 24/7, внешнего доступа, большей нагрузки или усиленных production controls.

## 9. Приоритеты

1. Сначала безопасность и юридическая корректность.
2. P4 выполняется до P5.
3. P5 обязателен до финальной генерации юридических документов из verdict.
4. P6 должен быть пройден до серьёзной founder demo.
5. UI polish выполняется после ключевых safety gates, кроме точечных исправлений, необходимых для корректного workflow.
6. Telegram, VPS и crawler не начинаются до доказанной работоспособности основного пути.
7. Нельзя ослаблять auth, RAG, verdict, document или section gates ради скорости демонстрации.

## 10. Связанные документы

- [CONTEXT.md](CONTEXT.md) — главный паспорт проекта и текущий snapshot.
- [ARCHITECTURE.md](ARCHITECTURE.md) — архитектура и технический flow.
- [DECISIONS_LOG.md](DECISIONS_LOG.md) — принятые и ожидающие решения.
- [SECTION_GROUPS_AND_RAG_POLICY.md](SECTION_GROUPS_AND_RAG_POLICY.md) — canonical sections и правила маршрутизации.
- [PROMPT_SYSTEM_V1.md](PROMPT_SYSTEM_V1.md) — роли юристов и prompt/output policy.
- [RAG_WORKFLOW_V1.md](RAG_WORKFLOW_V1.md) — целевой targeted RAG workflow.
- [VERDICT_AND_DOCUMENT_POLICY_V1.md](VERDICT_AND_DOCUMENT_POLICY_V1.md) — eligibility verdict и document gates.
- [QUALITY_GATE_V1.md](QUALITY_GATE_V1.md) — обязательные 38 проверок P2–P6.
