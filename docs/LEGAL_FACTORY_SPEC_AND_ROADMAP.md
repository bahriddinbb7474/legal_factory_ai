# Legal Factory AI — спецификация и roadmap

Актуально на: 2026-07-01

## Видение

Legal Factory AI должен стать безопасным внутренним рабочим местом, где подразделения завода получают предварительный юридический анализ, проверяют документы по официальным источникам, сопоставляют позиции нескольких AI-юристов и готовят документы через контролируемые backend workflows. Система помогает людям, но не заменяет ответственного специалиста или утверждение руководителя.

## MVP

В текущий MVP входят:

- защищённый Web UI, admin-created users, роли и история чатов;
- один shared chat и ручной выбор одного из трёх AI-юристов;
- upload/preview документов и передача их как untrusted factual context;
- curated active official Uzbekistan sources;
- normal pre-verdict analysis, explicit verdict workflow и red-topic approval state;
- две канонические группы разделов;
- CompanyProfile, approved templates foundation, generated-document editor и export foundation;
- cost/provider controls и audit foundation.

MVP считается безопасно завершённым только после P4 targeted RAG, P5 verified verdict/document gate и P6 quality acceptance.

## После MVP

- Расширение утверждённых factory templates и реальных legal sources.
- Улучшение multilingual retrieval/triggers и OCR.
- Production PostgreSQL/pgvector, backup/restore, retention и наблюдаемость.
- Laptop/LAN pilot, реальные factory scenarios и mini-launch.
- Production-grade document/PDF rendering и расширенный audit/approval routing.
- Telegram или внешнее размещение — только отдельным утверждённым этапом.

## Не входит в текущий MVP

- Public/self-registration.
- Полный LEX.UZ crawler или массовый historical import.
- Автоматическое смешивание outdated/future law с current law.
- Stamp/signature upload/rendering.
- Telegram, VPS/public deployment и 24/7 external access.
- Сложные department-level permissions и enterprise workflow engine.
- Автономный четвёртый AI-диспетчер.

## Пользователи и права

- **admin** — создаёт пользователей, управляет настройками и видит административные разделы.
- **director / chief_accountant / legal_responsible** — рабочие и approval-роли в пределах реализованных endpoint checks.
- **sales / supply / hr / accountant** — рабочие роли; non-admin видит только свои чаты.
- **viewer** — read-only для собственных доступных данных; workspace mutations возвращают 403.
- Anonymous workspace/admin access запрещён. Runtime role names и точные checks определяются backend, а не текстом модели.

## Три юриста

| Роль | До verdict | Verdict |
| --- | --- | --- |
| Юрист 1 | Первичный практический анализ, уточнения, запрос/проверка источников | Запрещён |
| Юрист 2 | Review, критика и сильное второе мнение | Разрешён после explicit permission и backend checks |
| Юрист 3 | Арбитраж спорных позиций и сильное мнение | Разрешён после explicit permission и backend checks |

Юристы работают в одном контексте и видят авторов сообщений. Backend вызывает только выбранного юриста; multi-agent fan-out автоматически не выполняется.

## Группы разделов

### `template_documents` — «Шаблонные документы»

AI-Секретарь flow: письма, договоры по утверждённым формам, справки, доверенности, приказы и прочие approved templates. Default RAG/verdict/legal conclusion отсутствуют. Риск, спор, legal verification или red topic требуют legal review; отсутствие утверждённой формы запрещает финальный документ.

### `legal_questions` — «Юридические вопросы и заключения»

AI-Юрист flow: legal analysis, source checks, review и eligible verdict. Юрист 1 должен запросить/проверить официальные источники либо сначала задать точные уточнения. Юрист 2/3 может дать обычное мнение; verdict требует явного разрешения.

UI labels являются display-only. Backend routing использует стабильные `section_code`; unknown/ambiguous input безопасно нормализуется в `legal_other`.

## Два продуктовых потока

### Template/document flow

```text
section_code → approved template lookup → CompanyProfile/data fields → draft/review → export
```

На текущем этапе присутствует только foundation и один базовый template path. P3-C блокирует verdict shortcut и default RAG в template group; полный набор форм и финальная проверка template eligibility ещё не реализованы.

### Legal/RAG/verdict flow

```text
question + history + trusted/untrusted inventory
→ clarification or targeted RAG request (P4)
→ exact source package
→ normal lawyer analysis/review
→ explicit user permission
→ Lawyer 2/3 structured verdict
→ backend citation/approval/document gate (P5)
→ generated document
```

Сейчас normal/verdict mode и section routing работают, но targeted package и verified gate ещё не завершены.

## Roadmap до founder demo

1. **P4 — Targeted RAG**: source inventory, internal request protocol, точный source package, missed-RAG fallback и подготовка package binding.
2. **P5 — Verified verdict/document gate**: `source_package_id`, `context_snapshot_hash`, deterministic citation checks, backend-owned eligibility и document button.
3. **P6 — Quality/multilingual hardening**: реализовать/пройти 38 checks, усилить RU/UZ Latin/Cyrillic triggers, injection и boundary regressions.
4. **Founder demo polish**: browser smoke реальных сценариев, убрать fake/right-panel remnants, выровнять UX и подготовить демонстрационные данные без ослабления gates.

## После founder demo

1. P7/OpenRouter UX и production model selection после ручного тестирования.
2. Расширение legal base/templates и владельцев актуальности.
3. Production data/storage/audit hardening.
4. Laptop/LAN pilot на 3–4 пользователя, backup/restore и mini-launch.
5. Отдельное решение о PostgreSQL/pgvector rollout, Telegram и deployment.

## Приоритет

Safety dependencies важнее визуального polish:

```text
P4 source package → P5 verified gate → P6 acceptance → founder demo polish → pilot/production work
```

Нельзя перепрыгивать к final document generation, если source verification и backend gate ещё не доказаны.

