# Stage 7 Legal Source Registry

## Purpose

Stage 7.2 fixes the approved first-batch registry for the first 15 legal sources that Legal Factory AI should prepare for manual upload.

This document is a user-approved registry, not an automatic legal research result. Codex must not choose extra laws by itself, download legal texts, scrape LEX.UZ, or create seed/data records from this file. Real source texts will be uploaded manually or semi-automatically later, after a separate command.

Each source must first be created as `draft`. A source can be moved to `active` only after metadata, chunks, retrieval, and citation smoke checks pass.

Every source must have:

- `revision_date_or_ONDATE`;
- `last_checked_at`;
- `next_check_due_at`;
- official source URL or approved search hint before upload;
- update policy and responsible owner/role.

LEX.UZ crawler work is explicitly forbidden at this stage.

Version handling policy is defined in:

```text
docs/LEGAL_SOURCE_VERSION_POLICY.md
```

Ordinary legal answers use only active current official revisions. Draft/future revisions are preparation-only until their effective date and must not be used as active law. Outdated/archived revisions remain metadata/history records and must not participate in ordinary RAG. Codex must not automatically download or import all historical LEX.UZ versions.

## Source revision lifecycle

One legal source record equals one concrete revision of one official document.

Example:

```text
Налоговый кодекс Республики Узбекистан — редакция / ONDATE на дату загрузки.
```

If a new official revision appears:

1. Move the old source to `outdated` or `archived`.
2. Create the new source as `draft`.
3. Fill required metadata.
4. Inspect chunks.
5. Run retrieval probes.
6. Confirm that a correct quote becomes `confirmed`.
7. Confirm that a wrong quote becomes `unconfirmed`.
8. Move the new source to `active` only after checks pass.

Forbidden:

- silently overwrite an old revision without history;
- leave an active source without `revision_date_or_ONDATE`;
- treat a source as current without `last_checked_at`;
- use a future version as `active` before its effective date.
- download/import historical LEX.UZ versions automatically.

## Required metadata for every source

For every legal source:

- `document_type`;
- `title`;
- `document_number`;
- `adoption_date`;
- `revision_date_or_ONDATE`;
- `effective_from`, if available;
- `effective_until`, if available;
- `source_name`;
- `source_url`;
- `official_status`;
- `status`;
- `language`;
- `last_checked_at`;
- `next_check_due_at`;
- `update_check_frequency`;
- `update_rule`;
- `owner_or_responsible_role`;
- `notes`.

Definitions:

- `revision_date_or_ONDATE` is the LEX.UZ revision/as-of date for the text.
- `last_checked_at` is the human manual verification date.
- `next_check_due_at` is the next manual verification date.
- `update_check_frequency` for the first version is `monthly`.
- Default upload status is `draft`.
- `active` is allowed only after acceptance checks.

## First batch — 15 approved legal sources

| id | priority | category | approved_source_title | document_type | expected_source_name | expected_source_url_or_search_hint | revision_date_or_ONDATE_policy | update_check_frequency | update_rule | why_needed_for_factory | activation_note | stage7_status |
|---:|:---:|---|---|---|---|---|---|---|---|---|---|---|
| 1 | A | civil_contracts | Гражданский кодекс Республики Узбекистан, часть первая | code | LEX.UZ | find exact current LEX.UZ source during manual upload | capture exact LEX.UZ current revision/ONDATE at upload time | monthly | if LEX.UZ has newer revision, archive old source and upload new revision as draft before activation | общие правила сделок, юрлица, обязательства, сроки, ответственность | draft until metadata/chunks/retrieval/citation checks pass | approved_for_manual_upload |
| 2 | A | civil_contracts_debt_supply | Гражданский кодекс Республики Узбекистан, часть вторая | code | LEX.UZ | find exact current LEX.UZ source during manual upload | capture exact LEX.UZ current revision/ONDATE at upload time | monthly | if LEX.UZ has newer revision, archive old source and upload new revision as draft before activation | поставка, купля-продажа, долг, пеня, возмещение, претензии | high priority for first smoke because factory debt/claims scenarios depend on it | approved_for_manual_upload |
| 3 | A | hr_labor | Трудовой кодекс Республики Узбекистан | code | LEX.UZ | find exact current LEX.UZ source during manual upload | capture exact LEX.UZ current revision/ONDATE at upload time | monthly | if LEX.UZ has newer revision, archive old source and upload new revision as draft before activation | приём, увольнение, дисциплина, отпуск, трудовой спор | draft until HR retrieval probes pass | approved_for_manual_upload |
| 4 | A | tax_accounting | Налоговый кодекс Республики Узбекистан | code | LEX.UZ | find exact current LEX.UZ source during manual upload | обязательно записать последнюю дату редакции/ONDATE с LEX.UZ при загрузке | monthly, and additionally before any important tax response | if LEX.UZ has newer revision, mark old source outdated/archived and upload new revision as draft; do not silently overwrite | НДС, налоговые проверки, требования, письма в налоговую | do not use as active without exact revision_date_or_ONDATE | approved_for_manual_upload |
| 5 | A | customs_import | Таможенный кодекс Республики Узбекистан | code | LEX.UZ | find exact current LEX.UZ source during manual upload | capture exact LEX.UZ current revision/ONDATE at upload time | monthly, and additionally before customs/import advice | if LEX.UZ has newer revision, archive old source and upload new revision as draft before activation | импорт сырья, таможенные режимы, декларации, таможенные платежи | draft until customs retrieval probes pass | approved_for_manual_upload |
| 6 | A | administrative_liability | Кодекс Республики Узбекистан об административной ответственности | code | LEX.UZ | find exact current LEX.UZ source during manual upload | capture exact LEX.UZ current revision/ONDATE at upload time | monthly | if LEX.UZ has newer revision, archive old source and upload new revision as draft before activation | риски штрафов по налогам, труду, пожарке, экологии, проверкам и госорганам | draft until penalty/risk retrieval probes pass | approved_for_manual_upload |
| 7 | A | personal_data | Закон Республики Узбекистан “О персональных данных” | law | LEX.UZ | find exact current LEX.UZ source during manual upload | capture exact LEX.UZ current revision/ONDATE at upload time | monthly | if LEX.UZ has newer revision, archive old source and upload new revision as draft before activation | HR, сотрудники, документы, доступы, хранение персональных данных | draft until personal data retrieval probes pass | approved_for_manual_upload |
| 8 | A | occupational_safety | Закон Республики Узбекистан “Об охране труда” | law | LEX.UZ | find exact current LEX.UZ source during manual upload | capture exact LEX.UZ current revision/ONDATE at upload time | monthly | if LEX.UZ has newer revision, archive old source and upload new revision as draft before activation | инструктажи, ответственность, несчастные случаи, внутренние приказы | draft until occupational safety retrieval probes pass | approved_for_manual_upload |
| 9 | A | fire_safety | Закон Республики Узбекистан “О пожарной безопасности” | law | LEX.UZ | find exact current LEX.UZ source during manual upload | capture exact LEX.UZ current revision/ONDATE at upload time | monthly | if LEX.UZ has newer revision, archive old source and upload new revision as draft before activation | проверки, пожарные требования, документы, ответственность | draft until fire safety retrieval probes pass | approved_for_manual_upload |
| 10 | A | government_requests | Закон Республики Узбекистан “Об обращениях физических и юридических лиц” | law | LEX.UZ | find exact current LEX.UZ source during manual upload | capture exact LEX.UZ current revision/ONDATE at upload time | monthly | if LEX.UZ has newer revision, archive old source and upload new revision as draft before activation | ответы госорганам, сроки, требования, официальные обращения | good candidate for first smoke because it is smaller than codes and useful for letters to state bodies | approved_for_manual_upload |
| 11 | A | electrical_industry_import_export | “О дополнительных мерах по созданию благоприятных условий для дальнейшего развития электротехнической промышленности и повышения инвестиционного и экспортного потенциала отрасли”, ПП-4348 от 30.05.2019 | presidential_resolution | LEX.UZ | https://lex.uz/uz/docs/-4360770?ONDATE=01.07.2026%2000#edi-6955857 | use ONDATE=2026-07-01 exactly as approved by the user | monthly and before any import/export/tax/customs benefit answer | because this is a future/effective-date-sensitive version, keep as draft before 2026-07-01; after 2026-07-01 manually re-check LEX.UZ, then activate only if metadata/chunks/citation checks pass | электротехническая промышленность, сырьё, импорт, экспорт, отраслевые меры, профильный акт для кабельного завода | future version; do not make active before 2026-07-01 | approved_for_manual_upload_future_version |
| 12 | A | foreign_economic_activity | Закон Республики Узбекистан “О внешнеэкономической деятельности” | law | LEX.UZ | find exact current LEX.UZ source during manual upload | capture exact LEX.UZ current revision/ONDATE at upload time | monthly | if LEX.UZ has newer revision, archive old source and upload new revision as draft before activation | импортные контракты, ВЭД, права участников внешнеэкономической деятельности | draft until import contract retrieval probes pass | approved_for_manual_upload |
| 13 | A | currency_regulation | Закон Республики Узбекистан “О валютном регулировании” | law | LEX.UZ | find exact current LEX.UZ source during manual upload | capture exact LEX.UZ current revision/ONDATE at upload time | monthly | if LEX.UZ has newer revision, archive old source and upload new revision as draft before activation | импортные платежи, валютные контракты, валютный контроль | draft until currency regulation retrieval probes pass | approved_for_manual_upload |
| 14 | A | technical_regulation | Закон Республики Узбекистан “О техническом регулировании” | law | LEX.UZ | find exact current LEX.UZ source during manual upload | capture exact LEX.UZ current revision/ONDATE at upload time | monthly | if LEX.UZ has newer revision, archive old source and upload new revision as draft before activation | техрегламенты, требования к продукции, госнадзор | draft until technical regulation retrieval probes pass | approved_for_manual_upload |
| 15 | A | conformity_assessment | Закон Республики Узбекистан “Об оценке соответствия”, ZRU-354, adopted 2013-10-04 | law | LEX.UZ | https://lex.uz/ru/docs/2248099 | exact source checked during Stage 7.5-C-fix; LEX.UZ marks it no longer in force from 2023-08-29 | monthly if retained for history | keep metadata/history only; do not use as active RAG; identify current related sources separately and ask user approval before adding substitutes | сертификация, декларация, соответствие продукции, документы качества | covered as outdated/historical; ordinary RAG excluded; role: historical/reference only | covered_as_outdated_historical |

## Stage 7.5-C2 conformity registry decision

Stage 7.5-C-fix found and smoke-checked the exact approved source No. 15, ZRU-354 `Law of Uzbekistan on Conformity Assessment`, at `https://lex.uz/ru/docs/2248099`. LEX.UZ marks this act as no longer in force from `2023-08-29`.

Registry decision:

- `stage7_status`: `covered_as_outdated_historical`.
- `recommended_runtime_status`: `outdated`.
- `ordinary_rag`: excluded.
- `role`: historical/reference only.

Original approved source No. 15 was checked and found expired; keep metadata/history, do not use it as active RAG. See `docs/STAGE7_5C_CONFORMITY_FIX_REPORT.md`.

ZRU-819, `Law of Uzbekistan on Technical Regulation`, is already in the first batch as a current active source. After ZRU-354 expiry, current regulation for technical regulation and related conformity-framework questions should be checked through ZRU-819 and other current related acts. Do not state that ZRU-819 fully replaces every ZRU-354 norm unless that is confirmed by the text.

ZRU-820, `Law of Uzbekistan on Accreditation of Conformity Assessment Bodies`, is a related additional candidate/current related source for accreditation of conformity assessment bodies. It is not a replacement for source No. 15 and is not part of the original first-batch required source list unless the user later approves it for a second batch or certification expansion.

First-batch coverage wording:

- `covered` means the approved source slot was investigated and its status was resolved; it does not mean every covered source is active.
- `active current sources` must exclude outdated ZRU-354 and future PP-4348.
- ordinary `<TRUSTED_LEGAL_SOURCE>` retrieval must exclude outdated/future sources unless a separate future or historical mode is explicitly implemented later.

## Stage 7.3 suggested upload order

Start Stage 7.3 with three trial sources:

1. Закон “Об обращениях физических и юридических лиц”
   - Reason: useful for letters to government bodies, usually smaller than codes, and convenient for metadata/chunking checks.
2. Гражданский кодекс Республики Узбекистан, часть вторая
   - Reason: critical for contracts, debt, supply, and claims.
3. ПП-4348 `ONDATE=2026-07-01`
   - Reason: profile source for electrical/cable industry, but keep as `draft` / future version before 2026-07-01.

After these pass smoke checks, upload the remaining sources.

## Per-source acceptance checks

Before moving a source to `active`, verify:

- metadata complete;
- `source_url` points to official source;
- `revision_date_or_ONDATE` captured;
- `last_checked_at` filled;
- `next_check_due_at` filled;
- `update_rule` understood;
- future/effective date handled;
- chunks inspected in UI;
- reindex done if needed;
- 2-3 retrieval probe questions passed;
- correct quote confirmed;
- wrong quote unconfirmed;
- stale/future source warning understood;
- source card shows metadata in UI.

## Registry is not the law database

This document is only the approved loading plan. The legal texts themselves are not loaded by this document.

Stage 7.3 starts only after a separate command. Codex must not independently download, select, scrape, or upload sources from this registry.
