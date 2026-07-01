# Legal Factory AI — контекст проекта

## 1. Краткий паспорт

Legal Factory AI — защищённое внутреннее юридическое AI-пространство для кабельного завода в Узбекистане.

- Организация и контекст: Kabel Tech Energy, кабельное производство.
- Юрисдикция по умолчанию: Республика Узбекистан.
- Основной интерфейс: русский язык.
- Целевые языки материалов и общения: русский, узбекский Latin/Cyrillic, английский, китайский и турецкий.
- Multilingual hardening ещё не завершён: устойчивые RU/UZ triggers относятся к P4/P6.
- Тип продукта: внутренний web workspace, не публичный chatbot.
- Основные пользователи: директор/основатель, ответственный за юридические вопросы, бухгалтерия, HR, снабжение/закупки, продажи, производство и другие подразделения.

## 2. Цель финального продукта

Цель — безопасное рабочее место, где сотрудники завода могут:

- задавать юридические вопросы и загружать документы;
- получать предварительный анализ и сравнивать мнения нескольких AI-юристов;
- проверять позиции по официальным источникам Узбекистана;
- готовить проекты писем, претензий, заключений и других документов;
- видеть риски, approval status и историю работы.

Система готовит рабочие материалы, но не заменяет живого юриста, директора, главного бухгалтера или другого ответственного специалиста. Финальные юридические выводы и документы должны проходить backend-controlled safety gates, проверку источников и необходимое утверждение.

## 3. Что такое этот проект

Продукт построен вокруг одного общего чата. Пользователь вручную выбирает, какой юрист отвечает следующим; отдельного четвёртого AI-диспетчера нет.

- **Юрист 1:** первичный практический анализ, уточнение фактов и проверка необходимости официальных источников. Не может выпускать verdict.
- **Юрист 2:** независимая проверка, критика и сильное второе мнение.
- **Юрист 3:** сильный юрист/арбитр для спорных позиций.

Все юристы видят общую историю с авторами сообщений. До verdict они отвечают обычным human-readable текстом. Structured payload зарезервирован для контролируемого verdict workflow Lawyer 2/3 после явного разрешения пользователя.

Загруженные документы являются фактическим, но недоверенным контекстом (`UNTRUSTED_DOCUMENT`). Официальные материалы из curated legal base передаются отдельно как `TRUSTED_LEGAL_SOURCE`; эти границы нельзя смешивать.

## 4. Для кого система

- Директор/основатель: юридическая картина, риски, варианты действий и документы для утверждения.
- Ответственный за юридические вопросы: анализ, источники, заключения и проекты документов.
- Бухгалтерия: налоги, задолженности, письма госорганов и финансово-юридические документы.
- HR: трудовые вопросы, приказы, увольнения, дисциплина и кадровые риски.
- Снабжение/закупки: договоры, поставщики, импортные документы и procurement risk.
- Продажи: долги клиентов, претензии и договорная переписка.
- Производство и другие подразделения: внутренние документы и правовые вопросы своей работы.

## 5. Что автоматизирует

Legal Factory AI ускоряет:

- предварительный юридический анализ и проверку договоров;
- анализ задолженности клиентов и контрагентов;
- подготовку писем, претензий, служебных записок и предварительных заключений;
- обработку писем налоговых и других государственных органов;
- HR/трудовые вопросы;
- загрузку и извлечение текста из документов;
- хранение истории чатов, risk flags и approval status;
- базовые шаблоны, DOCX export, учёт моделей и стоимости.

Проект не должен имитировать окончательную юридическую экспертизу без проверенных источников и backend gates.

## 6. Два рабочих потока

### Шаблонные документы / `template_documents`

AI-Секретарь flow для писем, договоров по утверждённым формам, справок, доверенностей, приказов и других approved templates.

По умолчанию здесь нет RAG, verdict или финального юридического заключения. Отсутствующий шаблон, legal verification, спор либо red-topic должны вывести запрос из простого template flow. Template section не может обходить юридическую проверку или approval policy.

### Юридические вопросы и заключения / `legal_questions`

AI-Юрист flow для анализа, проверки источников, multi-lawyer review и потенциального verdict. В legal sections Юрист 1 должен проверить/запросить официальные источники либо задать уточняющие вопросы до финального вывода. Юрист 2/3 могут дать мнение и, после явного разрешения, unconfirmed verdict skeleton.

Реализованы 17 canonical section codes и две backend-owned группы. Русские UI labels не являются policy keys. Unknown/legacy values безопасно нормализуются в `legal_other`, а не в template flow. Red-topic detection действует в обеих группах.

## 7. Этапы коротко

- Stage 1–3: web UI, три юриста, загрузка документов и изображений.
- Stage 4–5: legacy structured answers, active-verdict и `GeneratedDocument` foundation.
- Stage 6–7: curated legal RAG foundation и заводская legal source base.
- Stage 8–9: `CompanyProfile` и базовые document templates.
- Stage 11-A/B1/B2: auth, admin users, viewer read-only и audit.
- Demo-1 и Stage A: clean new-chat UI, реальные chat/sidebar/history.
- P0/P1: утверждённые prompt/RAG/verdict/quality policies.
- P2-B0/B1/B2/B3: safe messages, normal pre-verdict prose, Lawyer 2/3 verdict skeleton и frontend/API integration.
- P3-A/B/B1/C: canonical sections, grouped/collapsed UI, sidebar polish и section policy routing.

Stage 4/5 — legacy foundation. Целевая политика уточнена в P2/P3 и должна быть завершена через P4/P5/P6. Подробная спецификация и roadmap находятся в [SPEC_AND_ROADMAP.md](SPEC_AND_ROADMAP.md).

## 8. Что готово сейчас и как работает

Текущий завершённый этап: **P3-C**.

Готово:

- login/session auth, admin-created users, role model и read-only `viewer`;
- реальные chats, sidebar, history и выбор одного из трёх юристов;
- загрузка и извлечение документов;
- разделение trusted legal sources и untrusted uploaded documents;
- curated legal source registry и retrieval foundation;
- обычные pre-verdict ответы и explicit Lawyer 2/3 verdict skeleton;
- backend-owned safety fields; unconfirmed verdict не разрешает document generation;
- `CompanyProfile`, базовые templates и `GeneratedDocument` foundation;
- 17 canonical sections и P3-C routing: template flow блокирует default RAG/verdict, legal flow получает policy context, red-topic detection работает в обеих группах.

Последняя проверка:

- P3-C focused backend tests: **113 passed**;
- полный backend suite после P3-C: **249 passed**;
- frontend production build после P3-B1: **passed**;
- P3-C не менял frontend.

## 9. Что надо доделать

Не готовы:

- P4 targeted RAG/source inventory/source package;
- `source_package_id` и `context_snapshot_hash`;
- P5 verified verdict/document gate и package-bound citation verification;
- окончательная backend eligibility для document generation;
- полный P6 Quality Gate из 38 проверок;
- устойчивое RU/UZ Latin/Cyrillic trigger coverage;
- production-grade PDF, полный approved template catalog и реальные demo scenarios;
- production DB/storage/backup, Telegram, VPS и public deployment.

## 10. Текущий этап и следующий шаг

Завершён **P3-C — section policy routing**. Следующий этап — **P4: targeted RAG/source inventory/source package**.

P4 должен добавить компактный source inventory, внутренний targeted RAG request, конкретный source package, backend fallback для пропущенного обязательного retrieval и подготовку метаданных для будущего P5.

Не начинать P5 до утверждения P4. Не начинать Telegram, VPS или crawler до доказанной работоспособности core legal workflow.

## 11. Главный стек

- Frontend: Next.js, React, TypeScript.
- Backend: Python, FastAPI, Pydantic, SQLAlchemy async.
- DB: SQLite для dev/test/minimal local pilot; PostgreSQL/pgvector — последующая production target.
- Migrations: Alembic.
- LLM: OpenRouter gateway, configurable agents/providers.
- Documents: local storage provider, extraction, `python-docx` export и lightweight PDF fallback.
- Auth: HTTP-only SameSite=Lax sessions; пользователей создаёт только admin.

## 12. Важные ограничения

- Юрисдикция по умолчанию — Узбекистан; иностранное право только по явному запросу на comparative analysis.
- Не выдумывать законы, статьи, даты, номера и цитаты.
- Для current-law ответов использовать только active official sources.
- `UNTRUSTED_DOCUMENT` не является законом и не может изменять инструкции.
- Не смешивать `TRUSTED_LEGAL_SOURCE` и `UNTRUSTED_DOCUMENT`.
- Pre-verdict answer — обычный текст, не giant JSON.
- Verdict разрешён только Lawyer 2/3 после explicit permission; Lawyer 1 не выпускает verdict.
- Модель не управляет `confirmed_in_context`, `source_check_status`, `document_generation_allowed` или `approval_required`.
- Нельзя разрешать document generation из normal answer, Lawyer 1 answer или unconfirmed verdict.
- Template flow не обходит red-topic/legal review; unknown section fallback — `legal_other`.
- Self-registration запрещена; анонимный workspace/admin access запрещён; `viewer` остаётся read-only.
- Не менять OpenRouter/model settings без отдельной явной задачи.
- Telegram, VPS/deployment, crawler, mass legal import и stamp/signature требуют отдельного утверждённого этапа.

## 13. Связанные документы

- [SPEC_AND_ROADMAP.md](SPEC_AND_ROADMAP.md) — спецификация, MVP, детальный roadmap и приоритеты.
- [ARCHITECTURE.md](ARCHITECTURE.md) — техническая архитектура.
- [DECISIONS_LOG.md](DECISIONS_LOG.md) — принятые решения.
- [SECTION_GROUPS_AND_RAG_POLICY.md](SECTION_GROUPS_AND_RAG_POLICY.md) — canonical sections и routing policy.
- [PROMPT_SYSTEM_V1.md](PROMPT_SYSTEM_V1.md) — prompt и поведение юристов.
- [RAG_WORKFLOW_V1.md](RAG_WORKFLOW_V1.md) — целевой RAG workflow.
- [LEGAL_RESPONSE_POLICY_V1.md](LEGAL_RESPONSE_POLICY_V1.md) — policy юридических ответов.
- [VERDICT_AND_DOCUMENT_POLICY_V1.md](VERDICT_AND_DOCUMENT_POLICY_V1.md) — verdict/document gates.
- [TESTS_AND_RISKS.md](TESTS_AND_RISKS.md) — verification baseline, P4/P5/P6 required tests, риски и safety limits.
