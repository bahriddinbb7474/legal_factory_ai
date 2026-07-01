# Legal Factory AI — статус, тесты и риски

Актуально на: 2026-07-01

> Обновляйте этот файл после каждого завершённого stage. Stable working rules находятся в `AGENTS.md` и `LEGAL_FACTORY_CODER_RULES.md`.

## Текущая точка

- Текущий завершённый этап: **P3-C — section policy routing**.
- Следующая задача: **P4 — targeted RAG / source inventory / source package**.
- Branch: `master`.
- Git sync перед этим docs commit: `master...origin/master [ahead 1]`.
- Локальный непушенный application commit: `2d168a8 feat: route behavior by section group`.
- После локального commit этого docs-stage без push ожидаемый статус — `ahead 2`.
- Working tree перед созданием этого docs-stage был чистым.

## Последние этапы

| Stage | Commit | Статус |
| --- | --- | --- |
| P2-B0 | `e095dda` | Public message fields защищены |
| P2-B1 | `2eb5c9f` | Normal pre-verdict prose |
| P2-B2 | `63df947` | Explicit Lawyer 2/3 verdict skeleton |
| P2-B3 | `ec99f1f` | Frontend/API normal-verdict integration |
| P3 policy docs | `6758bb5` | Groups/codes/routing policy |
| P3-A/B | `5677737` | Canonical section model + grouped UI |
| P3-B1 | `aac76ea`, `e282d77` | Collapsed/compact sidebar и spacing |
| P3-C | `2d168a8` | Runtime behavior by section group |

## Работает сейчас

- Login/session auth, admin-created users, ownership и viewer read-only.
- Real chats/history, selected lawyer invocation и per-chat cost metadata.
- Upload/extraction/preview документов, sensitivity/provider enforcement.
- Curated legal sources, chunking, active+official filtering и retrieval foundation.
- Plain-text pre-verdict ответы всех трёх юристов.
- Lawyer 1 verdict ban; explicit Lawyer 2/3 verdict skeleton; ambiguous consent clarification.
- Backend-owned gates; unconfirmed verdict имеет `document_generation_allowed=false`.
- 17 canonical sections, 2 groups, legacy aliases, unknown → `legal_other`.
- Template group без default retrieval/verdict; legal group с source-check-aware context.
- Red-topic detection/approval warning независимо от group.
- CompanyProfile, один базовый DocumentTemplate path, legacy GeneratedDocument editor/export.

## Частично реализовано

- **RAG:** curated retrieval есть, но legal group пока использует compatibility retrieval; lawyer-controlled targeted protocol отсутствует.
- **Verdict:** schema/permission/author guards есть, но нет source package binding и verified status.
- **Documents:** legacy workflow/editor/export есть, но новый policy-safe generation gate ещё не подключён.
- **Red topics:** backend foundation работает, но keyword morphology и multilingual coverage ограничены.
- **Templates:** infrastructure и базовый debt/claim template есть; полный approved factory catalog отсутствует.
- **PDF:** endpoint/format fallback есть, production layout нет.

## Не реализовано

- P4 source inventory, internal targeted request, concrete package и missed-RAG safety net.
- `source_package_id`, `context_snapshot_hash` и package-bound citation verification.
- P5 final verdict/document-generation eligibility gate.
- Полное прохождение 38 Quality Gate checks.
- Устойчивая RU/UZ Latin/Cyrillic trigger coverage; другие языки не подтверждены end-to-end tests.
- Production PostgreSQL/pgvector rollout, backup/retention и laptop/LAN pilot.
- Production-grade templates/PDF, advanced approval routing и расширенный audit.
- Telegram, VPS/public deployment, crawler, stamp/signature и mass import.

## Последние проверки

| Проверка | Результат | Когда/контекст |
| --- | --- | --- |
| Полный backend suite | **249 passed**, 4 deprecation warnings | После P3-C (`2d168a8`) |
| P3-C focused routing/verdict/red-topic | **113 passed**, 1 warning | Перед P3-C commit |
| P3-A/B full backend suite | **234 passed** на том этапе | До дополнительных P3-C tests |
| Frontend production build | PASS | После P3-B1 spacing commit `e282d77`; P3-C frontend не менял |
| `git diff --check` | PASS | После каждого последнего stage |

Warnings относятся к Starlette/FastAPI deprecated interfaces/status aliases и не были причиной test failure.

## Manual smoke

Подтверждено владельцем в browser smoke после P3-A/B:

- две группы и 17 sections отображаются;
- выявленные проблемы высоты/sidebar были исправлены P3-B1;
- normal lawyer answers отображались без raw JSON;
- P2-B3 verdict invocation issue был исправлен.

Не подтверждено финальным browser smoke после P3-C:

- template letter → normal drafting без verdict/retrieval expectation;
- template red-topic → visible review warning;
- legal HR + Lawyer 1 → source-check caution/clarification;
- Lawyer 2 explicit verdict → unconfirmed skeleton без document button;
- окончательная оценка sidebar spacing после `e282d77`.

## Риски

- Модель может звучать слишком уверенно до завершения official source check; P4/P5 должны дать deterministic boundary.
- Без source package невозможно доказать, какие chunks использовались для verdict.
- Legacy generated-document code существует рядом с новым policy; новые обходные UI/API paths запрещены.
- Template sections могут стать unsafe shortcut, если routing/red flags будут ослаблены.
- Exact-keyword red flags пропускают словоформы и часть RU/UZ вариантов.
- Frontend `page.tsx` монолитен и повышает риск unrelated regression.
- Реальные OpenRouter models/providers и multilingual quality не покрываются mocked test suite.
- Browser smoke отстаёт от automated checks.
- Current status docs до этого отставали от P3; этот compact file должен стать частым snapshot, но git/code остаются окончательной проверкой.

## Следующая задача: P4

Минимальный ожидаемый результат:

1. Source inventory без отправки всех chunks.
2. Internal targeted RAG request, невидимый как user answer.
3. Concrete source package из active official sources.
4. Backend fallback, если legal flow пропустил обязательный RAG.
5. Metadata, достаточная для последующего P5 binding, без преждевременной реализации P5.
6. Focused tests для template bypass, legal source request, missing source и trust boundary.

## Не делать следующим

- Не включать final document generation для unconfirmed verdict.
- Не начинать Telegram/VPS/deployment или crawler.
- Не менять OpenRouter models/settings без отдельного задания.
- Не смешивать P4 с большим UI redesign или schema-wide refactor.
- Не расширять template flow так, чтобы он обходил legal/red-topic checks.
- Не объявлять P5/P6 завершёнными только по model output или demo appearance.
