# Legal Factory AI — ключевые решения и изменения

Актуально на: 2026-07-01

Этот файл объясняет причины архитектурных границ. Подробная история остаётся в [DECISIONS_LOG.md](DECISIONS_LOG.md) и git log.

## Действующие решения

| Date/Stage | Решение | Причина | Статус | Влияние |
| --- | --- | --- | --- | --- |
| P0/P1 | Юрисдикция по умолчанию — Узбекистан | Завод работает в Узбекистане; foreign law без запроса создаёт риск | Принято | Current-law ответы опираются на official Uzbekistan sources |
| Stage 2 | Один shared chat и 3 юриста | Сохраняет общую историю и позволяет review/арбитраж | Реализовано | Один выбранный lawyer на invoke; все видят авторов истории |
| Stage 2/P0 | Отдельного четвёртого AI-диспетчера нет | Routing и safety должны быть детерминированы backend | Действует | Section/permission/gates не делегируются модели |
| P0/P2-B1 | Pre-verdict ответ — natural text, не giant JSON/table | Читаемость и чёткая граница между мнением и verdict | Реализовано | `structured_payload=null` для normal mode |
| P0/P2-B2 | Verdict выпускает только Lawyer 2/3 после explicit permission | Не допустить случайной финализации | Foundation реализован | Lawyer 1 блокируется; ambiguous consent уточняется |
| P0 | Lawyer 1 не выпускает final verdict | Его роль — первичный анализ и source awareness | Реализовано | Backend и frontend guards |
| P0/P2-B0 | Model gate fields недоверенные | Модель не может подтвердить собственный ответ | Реализовано | Backend игнорирует/перезаписывает gate fields |
| P0/P5 target | Document-generation button контролирует backend | Unconfirmed opinion не должен становиться документом | Частично | Сейчас новый verdict всегда `document_generation_allowed=false`; полный gate — P5 |
| Stage 6/P0 | RAG использует curated active official sources | Нужна version/freshness control, а не произвольный web context | Foundation реализован | Draft/outdated/future исключаются из ordinary current-law retrieval |
| Stage 6 | Trusted law и uploaded documents разделены | Upload может содержать факты и prompt injection, но не authority | Реализовано | `TRUSTED_LEGAL_SOURCE` vs `UNTRUSTED_DOCUMENT` |
| P3 | Две группы: `template_documents` и `legal_questions` | Разделить AI-Секретарь и AI-Юрист workflows | Реализовано | Разные default policy contexts |
| P3-C | Template group без automatic RAG/verdict | Шаблонный документ не должен симулировать legal conclusion | Реализовано | Retrieval пропускается, verdict endpoint возвращает 400 |
| P3-C | Legal group source-check aware | До final conclusion нужны официальные источники | Реализовано частично | Lawyer 1 instruction есть; targeted request/package — P4 |
| P3-A | Unknown legacy section → `legal_other`, не template | Fail-safe routing важнее удобной догадки | Реализовано | Неизвестный input всегда попадает в legal flow |
| Stage 4/P0 | Red topics работают независимо от section group | Template label не должен обходить approval | Реализовано foundation | Chat/message получает red flags и `needs_review` |
| UI/P3-B1 | Central chat остаётся главным; sidebar compact/collapsed, right panel по необходимости | Сохранить рабочее пространство и вместить 17 sections | Реализовано | Chat titles скрыты до раскрытия section |
| Roadmap | Telegram, VPS, crawler, stamp/signature и non-core integrations отложены | Сначала доказать core legal safety и local workflow | Действует | Не добавлять без отдельного stage approval |

## Существенные изменения по коммитам

| Commit/Stage | Изменение | Результат |
| --- | --- | --- |
| `768484a` / P1 | Prompt/RAG/verdict policy v1 | Нормативная база P2–P6 |
| `e095dda` / P2-B0 | Protected message creation | Пользователь не задаёт backend-owned fields |
| `2eb5c9f` / P2-B1 | Normal lawyer response mode | Pre-verdict стал plain text |
| `63df947` / P2-B2 | Verdict-only skeleton | Explicit Lawyer 2/3 structured mode, unconfirmed gate |
| `ec99f1f` / P2-B3 | Frontend/backend verdict integration | Удалён manual mark action; корректный mode invocation/rendering |
| `6758bb5` / P3 docs | Section groups policy | Утверждены groups/codes/roadmap |
| `5677737` / P3-A/B | Canonical section groups | Backend normalization и grouped UI |
| `aac76ea`, `e282d77` / P3-B1 | Sidebar polish | Collapsed chats, compact labels/spacing |
| `2d168a8` / P3-C | Runtime routing | Template/legal behavior, policy context и red-topic regressions |

## Deprecated / не считать текущим контрактом

- **Strict JSON для каждого ответа** — legacy Stage 4 baseline; normal ответы теперь prose.
- **Manual «Пометить как вердикт»** — старый UI flow удалён; legacy backend path защищён и не является новым policy workflow.
- **Раздел только как русская строка/title prefix** — заменён `Chat.section` с canonical codes и legacy normalization.
- **Один недифференцированный retrieval для всех sections** — template group его больше не запускает; legal compatibility будет заменена P4 protocol.
- **Active verdict сам по себе разрешает документ** — недостаточно; целевой P5 требует source binding, verification и backend gate.
- **Development current-user stub** — заменён database-backed sessions/auth.

