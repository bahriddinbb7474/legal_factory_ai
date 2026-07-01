# Legal Factory AI — тесты и риски

## 1. Назначение документа

Это основной активный документ по verification, открытым рискам и обязательным safety limits Legal Factory AI. Он отвечает на вопросы:

- какие проверки уже пройдены;
- какие проверки обязательны для docs, backend, frontend и cross-cutting изменений;
- какие тесты ещё нужны для P4/P5/P6;
- какие риски остаются открытыми;
- какие ограничения нельзя ослаблять.

Документ консолидирует ранее раздельные quality gate, testing strategy и risks/limits материалы и является единой активной точкой контроля.

## 2. Текущий verification snapshot

- Последний завершённый этап: **P3-C**.
- Следующий этап: **P4 targeted RAG/source inventory/source package**.
- P3-C focused backend tests: **113 passed**.
- Полный backend suite после P3-C: **249 passed**.
- Frontend production build после P3-B1: **passed**.
- P3-C не менял frontend.
- Последующие docs-only commits не запускали application tests, поскольку не меняли код или конфигурацию.

Этот snapshot нужно обновлять после каждого значимого implementation stage или изменения verification baseline.

## 3. Базовые правила тестирования

### Docs-only change

Обязательно:

```powershell
git diff --check
git status --short
```

Backend/frontend tests не требуются, если не менялись код, runtime config или executable tooling.

### Backend change

Сначала focused tests:

```powershell
cd backend
..\.venv\Scripts\python.exe -m pytest tests/<focused_tests>.py -q
```

При изменении cross-cutting flow, общих schemas/services, auth, invoke, RAG, verdict или document gates запускать полный suite:

```powershell
cd backend
..\.venv\Scripts\python.exe -m pytest tests -q
```

### Frontend change

Обязательно:

```powershell
cd frontend
npm.cmd run build
```

Для изменённого пользовательского flow также выполнить focused manual browser smoke.

### Full flow / risky change

Запустить:

1. focused backend tests;
2. полный backend suite, если затронут cross-cutting контракт;
3. frontend build, если менялся frontend;
4. manual browser smoke для реального пользовательского пути;
5. `git diff --check` и `git status --short`.

Автоматические тесты не должны вызывать реальные платные OpenRouter, vision или embedding API; используются mocks/fake providers.

## 4. Опасные зоны, где нужны усиленные тесты

- auth, sessions, roles и read-only ограничения `viewer`;
- public message creation schemas и backend-owned fields;
- ownership/access для chats, messages и documents;
- orchestration вызова выбранного юриста и история чата;
- normal mode против verdict mode;
- canonical section normalization и policy routing;
- `template_documents` flow и approved-template boundary;
- `legal_questions` flow и source-check requirement;
- фильтрация legal sources по status/official status;
- разделение `TRUSTED_LEGAL_SOURCE` и `UNTRUSTED_DOCUMENT`;
- deterministic citation verification;
- red flags, large amounts и approval state;
- generated documents, lifecycle, DOCX/PDF export;
- provider/model/cost и monthly budget logic;
- file upload, extraction, OCR, size/type/path validation;
- admin legal source registry, reindex и freshness warnings.

## 5. Что уже проверено

### P2-B0/B1/B2/B3

- public message fields защищены, model/backend gate fields не принимаются как пользовательские;
- обычные pre-verdict ответы сохраняются и отображаются как human-readable prose;
- structured payload не требуется для normal answer;
- Lawyer 2/3 поддерживают explicit verdict mode с консервативным unconfirmed skeleton;
- Lawyer 1 и normal messages защищены от использования как verdict/document source;
- frontend/API invocation и безопасный rendering normal/verdict modes согласованы;
- unconfirmed verdict сохраняет `document_generation_allowed=false`.

### P3-A/B/B1/C

- реализованы 17 canonical section codes и две backend-owned группы;
- grouped UI использует display labels, а не policy keys;
- sidebar compact/collapsed, chats раскрываются по section;
- legacy/unknown sections безопасно нормализуются в `legal_other`;
- template и legal flows маршрутизируются раздельно;
- verdict mode блокируется в template sections;
- legal-flow context требует от Lawyer 1 проверить/запросить официальные источники либо уточнить факты;
- red-topic detection продолжает действовать в обеих группах.

Последний подтверждённый baseline: **113 focused backend tests**, **249 full backend tests**, frontend build после P3-B1 — **passed**. Browser smoke после P3-C не зафиксирован и не заявляется как выполненный.

## 6. Manual smoke checklist

### После sidebar/section UI изменений

- [ ] Новый чат открывается без fake messages.
- [ ] Отображаются две группы и все ожидаемые section labels.
- [ ] Internal section codes не показываются пользователю.
- [ ] Старые chats находятся под правильной normalized section.
- [ ] Chat titles корректно раскрываются и сворачиваются.
- [ ] Создание, открытие и reload chat history работают.

### После изменений normal answer

- [ ] User message сохраняется.
- [ ] Отвечает выбранный юрист.
- [ ] Ответ — обычный читаемый текст без raw JSON.
- [ ] Для normal answer не требуется `structured_payload`.
- [ ] Под normal answer нет verdict/document action, нарушающего policy.

### После изменений verdict flow

- [ ] Lawyer 1 не может выпустить verdict.
- [ ] Explicit phrase для Lawyer 2/3 включает verdict mode.
- [ ] Неоднозначные `ок`, `понятно`, `согласен` запрашивают уточнение.
- [ ] Текущий verdict skeleton остаётся unconfirmed.
- [ ] Для unconfirmed verdict не показывается document-generation button.

### После изменений section routing

- [ ] Простое письмо в template section не требует RAG или verdict.
- [ ] Рискованный HR/tax/government/court запрос в template section не обходит red/legal warning.
- [ ] Legal HR вопрос заставляет Lawyer 1 проверить/запросить official sources либо уточнить факты.
- [ ] Red-topic detection действует в обеих группах.
- [ ] Unknown section уходит в `legal_other`, не в template flow.

### После изменений documents/upload

- [ ] PDF, DOCX, XLSX, TXT и поддерживаемое изображение загружаются.
- [ ] Unsupported type отклоняется.
- [ ] Oversized file отклоняется.
- [ ] Path-traversal filename не принимается.
- [ ] Extraction/OCR failure явно виден пользователю.
- [ ] Uploaded document передаётся только как `UNTRUSTED_DOCUMENT`.

## 7. P4 required tests — targeted RAG

**Статус: NOT DONE. P4 ещё не реализован.**

После реализации P4 тесты должны подтвердить:

- юрист получает compact source inventory, а не dump всех chunks;
- legal section может сформировать внутренний targeted RAG request;
- template section не запускает legal RAG по умолчанию;
- current-law source package содержит только `active + official` sources;
- `outdated`, `future`, `draft`, `archived` и неподтверждённые источники исключены из ordinary RAG;
- отсутствие источника вызывает uncertainty/missing-source behavior, а не fake certainty;
- user upload не становится official source;
- backend fallback ловит legal answer, пропустивший обязательный RAG;
- source package metadata достаточно для будущей P5 binding;
- RU/UZ trigger patterns добавлены либо подготовлены для полного P6 coverage;
- prompt injection в uploaded document не может выбрать юрисдикцию или legal source;
- trusted и untrusted context остаются раздельными на всех шагах.

## 8. P5 required tests — verified verdict/document gate

**Статус: NOT DONE. P5 ещё не реализован.**

После реализации P5 тесты должны подтвердить:

- Lawyer 1 verdict заблокирован;
- Lawyer 2/3 verdict требует explicit permission;
- ambiguous permission вызывает clarification;
- verdict привязан к `source_package_id`;
- verdict привязан к `context_snapshot_hash`;
- citation verification проверяет только bound package;
- модель не может установить или переопределить:
  - `confirmed_in_context`;
  - `source_check_status`;
  - `document_generation_allowed`;
  - `approval_required`;
- unconfirmed verdict не создаёт документ;
- normal answer и Lawyer 1 answer не создают документ;
- red-topic approval блокирует generation, пока требование не выполнено;
- template path создаёт документ только из approved template, когда policy это разрешает;
- eligibility для document generation и `GeneratedDocument.status` вычисляются/управляются backend независимо;
- generated document lifecycle остаётся `draft/review/approved/rejected` и не контролируется моделью.

## 9. P6 required tests — Quality Gate

**Статус: NOT DONE. Полный P6 Quality Gate не пройден.**

Нужно покрыть:

- prompt behavior и роль каждого юриста;
- normal-answer/verdict boundary;
- RAG/source safety и legal source freshness;
- canonical section routing;
- approved-template boundaries;
- red-topic detection, large amounts и approval behavior;
- prompt injection protection;
- uploaded-document trust boundary;
- deterministic citation verification;
- multilingual RU, Uzbek Latin и Uzbek Cyrillic triggers;
- frontend visibility warnings, source state и backend gates;
- отсутствие raw JSON и необработанных technical errors в normal UI.

Все P6 quality checks, перечисленные в этом разделе и в текущем acceptance checklist проекта, должны быть покрыты автоматическими тестами либо явным manual acceptance checklist до серьёзной founder demo. Наличие отдельных P2/P3 regressions не означает, что P6 завершён.

## 10. Current open risks

- P4 targeted RAG/source inventory/source package не реализован.
- `source_package_id` и `context_snapshot_hash` отсутствуют.
- P5 verified verdict/document gate отсутствует.
- Текущий retrieval foundation совместим с legal RAG, но не является финальным P4 protocol.
- Модель может звучать слишком уверенно до проверки official sources; backend и UI должны явно сохранять uncertainty.
- Legacy generated-document/active-verdict foundation существует рядом с новой policy и не должен стать shortcut.
- Morphology и multilingual coverage red-topic/RAG triggers неполны.
- Browser smoke может отставать от automated tests; после P3-C он не зафиксирован.
- Frontend `page.tsx` остаётся крупным/монолитным и повышает regression risk.
- Mocked tests не полностью отражают реальное поведение выбранных OpenRouter models/providers.
- Production DB, storage, encryption/retention и backup/restore не готовы.
- PDF export — lightweight fallback, не production layout engine.
- Telegram, VPS и crawler отложены и в будущем не должны обходить web safety gates.

## 11. Permanent safety limits

- Система не является лицензированным адвокатом/юристом и не заменяет ответственного специалиста.
- Нельзя давать final legal conclusion без поддержки официальных источников.
- Нельзя выдумывать статьи, штрафы, сроки, номера документов, revision dates или quotes.
- Нельзя скрывать uncertainty или автоматически утверждать red-risk matters.
- Uploaded documents всегда считаются untrusted data, не инструкциями или official law.
- Sensitive documents можно отправлять только providers, явно разрешённым и trusted для sensitive data, если такой provider policy активен.
- Extraction/OCR failure должен быть виден; нельзя утверждать, что нечитаемый документ проанализирован.
- Unsupported, path-traversal и oversized files должны отклоняться.
- Ordinary current-law answers используют только active official sources.
- Outdated, future, draft и archived sources исключаются из ordinary RAG.
- Model-generated citations остаются unconfirmed до deterministic checks.
- `TRUSTED_LEGAL_SOURCE` нельзя смешивать с `UNTRUSTED_DOCUMENT`.
- Normal answer — human-readable text; structured payload зарезервирован для verdict workflow.
- Lawyer 1 не выпускает verdict; Lawyer 2/3 требуют explicit permission.
- Unconfirmed verdict, normal answer и Lawyer 1 answer не разрешают document generation.
- Model output не управляет backend gate fields или approval state.
- Template sections не обходят red-topic/legal review.
- Auth/RBAC, viewer read-only и admin-only user creation нельзя ослаблять.
- Automated tests не вызывают real paid provider APIs и не раскрывают secrets.
- OpenRouter/model settings нельзя менять без отдельной явной задачи.

## 12. История консолидации

Этот документ заменил прежние отдельные документы по quality gate, testing strategy и risks/limits. Их актуальное содержание перенесено сюда; устаревшие strict-JSON, legacy auth и legacy verdict assumptions удалены или исправлены.

## 13. Related docs

- [CONTEXT.md](CONTEXT.md) — паспорт проекта и current snapshot.
- [SPEC_AND_ROADMAP.md](SPEC_AND_ROADMAP.md) — MVP, roadmap и приоритеты.
- [ARCHITECTURE.md](ARCHITECTURE.md) — техническая архитектура и legacy/current boundaries.
- [SECTION_GROUPS_AND_RAG_POLICY.md](SECTION_GROUPS_AND_RAG_POLICY.md) — canonical sections и routing policy.
- [RAG_WORKFLOW_V1.md](RAG_WORKFLOW_V1.md) — целевой P4 targeted RAG workflow.
- [VERDICT_AND_DOCUMENT_POLICY_V1.md](VERDICT_AND_DOCUMENT_POLICY_V1.md) — целевой P5 verdict/document gate.
- [LEGAL_RESPONSE_POLICY_V1.md](LEGAL_RESPONSE_POLICY_V1.md) — response types, missing-source и red-topic policy.
