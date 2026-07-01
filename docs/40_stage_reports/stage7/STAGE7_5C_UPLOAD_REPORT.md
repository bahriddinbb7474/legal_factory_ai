# Stage 7.5-C Upload Report

Date: 2026-06-17

## Scope

Stage 7.5-C only: manually import and smoke-check the remaining four approved first-batch LEX.UZ sources from the Stage 7 registry.

- 4 sources only.
- No crawler.
- No mass import.
- No historical LEX.UZ auto-import.
- No future versions imported or activated.
- No raw law texts committed.
- No local DB/storage committed.
- No backend/frontend functional changes.
- No Stage 7.5-D / Stage 7.6 work.

Local smoke DB used:

```text
data/stage7_3_smoke_20260616_v2.db
```

This DB and related `data/uploads` storage are ignored local artifacts.

## Correction Note 2026-06-17

Stage 7.5-C originally imported ZRU-820, `Law of Uzbekistan on Accreditation of Conformity Assessment Bodies`, as the conformity assessment source.

Corrective check found the exact approved source No. 15:

```text
Law of Uzbekistan on Conformity Assessment
ZRU-354, adopted 2013-10-04
LEX.UZ: https://lex.uz/ru/docs/2248099
```

LEX.UZ marks ZRU-354 as no longer in force from `2023-08-29`. It was imported locally for exact first-batch coverage and smoke-checked, but it must not be used as active current law in ordinary RAG under `../../10_policies/LEGAL_SOURCE_VERSION_POLICY.md`.

ZRU-820 remains a related additional source/candidate. It is not a replacement for first-batch source No. 15.

## Stage 7.5-C2 Registry Update

The Stage 7 registry has been updated after the ZRU-354 expiry finding.

For source No. 15:

- `stage7_status`: `covered_as_outdated_historical`.
- `recommended_runtime_status`: `outdated`.
- `ordinary_rag`: excluded.
- `role`: historical/reference only.

`Covered` means the approved source slot was investigated and resolved. It does not mean the source is active current law.

For conformity-related current-law answers after the ZRU-354 expiry:

- ZRU-354 must stay out of ordinary active `<TRUSTED_LEGAL_SOURCE>` retrieval.
- ZRU-819, `Law of Uzbekistan on Technical Regulation`, is the current primary first-batch source for technical regulation and related conformity-framework checks, together with other current related acts.
- ZRU-819 must not be described as fully replacing every ZRU-354 norm unless that is confirmed by the text.
- ZRU-820 is a related additional candidate/current related source for accreditation of conformity assessment bodies, not a replacement for source No. 15.

## Source Summary

| Source id / title | Source URL | Document number | Adoption date | Revision date / ONDATE | Language | Initial status | Final status | Chunks | Max chunk size | Warnings | Activation decision |
| --- | --- | --- | --- | --- | --- | --- | --- | ---: | ---: | --- | --- |
| 12 / Civil Code of Uzbekistan, Part One | https://lex.uz/ru/docs/111189?ONDATE=30.12.2025 | b/n | 1995-12-21 | 2025-12-30 ONDATE | uz | draft | active | 336 | 8948 | none | Activated after metadata, chunk, retrieval, and citation smoke |
| 13 / Law of Uzbekistan on Currency Regulation | https://lex.uz/ru/docs/4562834 | ZRU-573 | 2019-10-22 | 2025-04-18 | uz | draft | active | 72 | 5589 | none | Activated after metadata, chunk, retrieval, and citation smoke |
| 14 / Law of Uzbekistan on Technical Regulation | https://lex.uz/ru/docs/6392314?ONDATE=19.01.2026 | ZRU-819 | 2023-02-27 | 2026-01-19 ONDATE | ru | draft | active | 204 | 7841 | none | Activated after metadata, chunk, retrieval, and citation smoke |
| 15 / Law of Uzbekistan on Accreditation of Conformity Assessment Bodies | https://lex.uz/ru/docs/6392307?ONDATE=29.08.2023 | ZRU-820 | 2023-02-27 | 2023-08-29 ONDATE | ru | draft | active | 86 | 3772 | none | Activated after metadata, chunk, retrieval, and citation smoke |
| 16 / Law of Uzbekistan on Conformity Assessment | https://lex.uz/ru/docs/2248099 | ZRU-354 | 2013-10-04 | 2023-08-29 (expired) | uz | draft | outdated | 18 | 3498 | `lexuz_lost_force_2023_08_29` | Exact approved source No. 15 imported and smoke-checked, but not activated because LEX.UZ marks it as no longer in force |

## Future Revision Observation

| Source | Future candidates observed on LEX.UZ | Imported/activated? |
| --- | --- | --- |
| Civil Code of Uzbekistan, Part One | 2026-06-29 | No. Recorded only as future candidate. Current active import uses 2025-12-30 ONDATE. |
| Law of Uzbekistan on Currency Regulation | none observed after 2026-06-17 | No future version imported. |
| Law of Uzbekistan on Technical Regulation | none observed after 2026-06-17 | No future version imported. |
| Law of Uzbekistan on Accreditation of Conformity Assessment Bodies | none observed after 2026-06-17 | No future version imported. |
| Law of Uzbekistan on Conformity Assessment, ZRU-354 | no future version imported | Exact source imported for coverage; LEX.UZ marks it as no longer in force from 2023-08-29, so it is not active current law. |

Future versions remain preparation-only and must not be used as active law before their effective dates.

## Per-Source Notes

### Civil Code of Uzbekistan, Part One

- Metadata captured: LEX.UZ URL, document number placeholder `b/n`, adoption date, revision date/ONDATE, language, official status, last/next check dates.
- Current active version as of 2026-06-17: `2025-12-30 ONDATE`.
- LEX.UZ showed future candidate `2026-06-29`; it was recorded only and not imported or activated.
- Readiness warnings: none.
- Chunk inspection: 336 chunks, max chunk size 8948, under the Stage 7.4 hard max but close to the ceiling.
- Retrieval probes: legal entity, transaction, obligation, and term/deadline probes returned source hits.
- Citation smoke: correct quote confirmed; fake quote unconfirmed.
- Performance: about 1.93 MB HTML and about 711k extracted text characters. Laptop use is acceptable, but chunk size is close to the hard max.

### Law of Uzbekistan on Currency Regulation

- Metadata captured: LEX.UZ URL, document number, adoption date, revision date, language, official status, last/next check dates.
- Current active version as of 2026-06-17: `2025-04-18`.
- `ONDATE=18.04.2025` returned 404, so the canonical LEX.UZ URL was used while recording revision metadata from the page.
- No future revisions were observed after 2026-06-17.
- Readiness warnings: none.
- Chunk inspection: 72 chunks, max chunk size 5589, under the Stage 7.4 hard max.
- Retrieval probes: currency operations, residents, non-residents, and currency control probes returned source hits.
- Citation smoke: correct quote confirmed; fake quote unconfirmed.
- Performance: about 318 KB HTML and about 78k extracted text characters. Safe for laptop use.

### Law of Uzbekistan on Technical Regulation

- Metadata captured: LEX.UZ URL, document number, adoption date, revision date/ONDATE, language, official status, last/next check dates.
- Current active version as of 2026-06-17: `2026-01-19 ONDATE`.
- No future revisions were observed after 2026-06-17.
- Readiness warnings: none.
- Chunk inspection: 204 chunks, max chunk size 7841, under the Stage 7.4 hard max.
- Retrieval probes: technical regulation, mandatory requirements, state control, and conformity assessment probes returned source hits.
- Citation smoke: correct quote confirmed; fake quote unconfirmed.
- Performance: about 522 KB HTML and about 141k extracted text characters. Safe for laptop use.

### Law of Uzbekistan on Accreditation of Conformity Assessment Bodies

- Metadata captured: LEX.UZ URL, document number, adoption date, revision date/ONDATE, language, official status, last/next check dates.
- Current active version as of 2026-06-17: `2023-08-29 ONDATE`.
- Correction: this source is related to conformity assessment, but it is not the exact approved source No. 15 and must not be treated as a replacement for ZRU-354.
- No future revisions were observed after 2026-06-17.
- Readiness warnings: none.
- Chunk inspection: 86 chunks, max chunk size 3772, under the Stage 7.4 hard max.
- Retrieval probes: conformity assessment, accreditation, conformity assessment bodies, and accreditation certificate probes returned source hits.
- Citation smoke: correct quote confirmed; fake quote unconfirmed.
- Performance: about 241 KB HTML and about 50k extracted text characters. Safe for laptop use.

### Law of Uzbekistan on Conformity Assessment

- Corrective source: exact approved first-batch source No. 15, ZRU-354, adopted 2013-10-04.
- LEX.UZ URL: `https://lex.uz/ru/docs/2248099`.
- LEX.UZ status: no longer in force from `2023-08-29`.
- Local final status: `outdated`, not `active`, to keep ordinary RAG aligned with current-law policy.
- Readiness warnings: `lexuz_lost_force_2023_08_29`.
- Chunk inspection: 18 chunks, max chunk size 3498, under the Stage 7.4 hard max.
- Retrieval probes: conformity assessment, certification, declaration of conformity, and confirmation of conformity probes returned source hits.
- Citation smoke: correct quote confirmed; fake quote unconfirmed.
- Performance: about 226 KB HTML and a small extracted text set. Safe for laptop use.

## Existing Source Status Check

The previous Stage 7.3, Stage 7.5-A, and Stage 7.5-B sources were available in the same ignored local smoke DB:

| Source | Status | Revision | Chunks | Max chunk size | Active retrieval sample |
| --- | --- | --- | ---: | ---: | --- |
| Law on Appeals of Individuals and Legal Entities | active | 2026-05-07 | 113 | 2991 | active sample hits available |
| Civil Code of Uzbekistan, Part Two | active | 2026-05-07 | 1824 | 2474 | active sample hits available |
| PP-4348 / PQ-4348 future source | draft | 2026-07-01 | 170 | 3968 | active hits: 0; still excluded |
| Tax Code of Uzbekistan | active | 2026-03-17 | 1249 | 8970 | active sample hits available |
| Customs Code of Uzbekistan | active | 2026-03-01 | 956 | 8526 | active sample hits available |
| Labor Code of Uzbekistan | active | 2026-01-01 | 2444 | 7318 | active sample hits available |
| Law of Uzbekistan on Personal Data | active | 2026-03-27 | 134 | 4402 | active sample hits available |
| Code of Uzbekistan on Administrative Responsibility | active | 2026-06-13 ONDATE | 546 | 8665 | active sample hits available |
| Law of Uzbekistan on Occupational Safety | active | 2022-05-18 ONDATE | 77 | 8230 | active sample hits available |
| Law of Uzbekistan on Fire Safety | active | 2026-03-01 | 141 | 6937 | active sample hits available |
| Law of Uzbekistan on Foreign Economic Activity | active | 2021-04-21 ONDATE | 46 | 4225 | active sample hits available |
| Law of Uzbekistan on Conformity Assessment, ZRU-354 | outdated | 2023-08-29 (expired) | 18 | 3498 | exact source imported, excluded from active current retrieval |

This confirms the PP-4348 future source remains draft and excluded from active retrieval, while prior active sources remain available.

## First Batch Completion Status

| Metric | Count | Note |
| --- | ---: | --- |
| Active current sources | 14 | Includes 13 exact current first-batch active sources plus ZRU-820 as a related additional active source/candidate; this is not the same as 15 active first-batch sources. |
| Draft/future sources | 1 | PP-4348 / PQ-4348 `ONDATE=2026-07-01` remains draft/future before its effective date. |
| Outdated exact first-batch sources | 1 | Exact source No. 15, ZRU-354, is covered but not active because LEX.UZ marks it as no longer in force from 2023-08-29. |
| Total first-batch sources covered | 15 | Includes 13 exact current active sources, 1 future draft source, and 1 exact outdated source. |

Ordinary RAG should continue to use only active official sources. PP-4348 remains excluded from ordinary active retrieval until its effective date and a later approved activation check. ZRU-354 remains excluded because it is outdated/historical.

## Issues Found

- LEX.UZ search ranks newer modifying acts above base laws, so direct source verification required exact doc IDs and revision checks.
- Civil Code Part One has a future LEX.UZ candidate `2026-06-29`. It was not imported or activated.
- Currency Regulation `ONDATE=18.04.2025` returned 404; the canonical URL was used with explicit revision metadata.
- Corrective check found exact source No. 15, ZRU-354 `Law on Conformity Assessment`, but LEX.UZ marks it as no longer in force from 2023-08-29.
- ZRU-820 is a related additional source/candidate, not a replacement for ZRU-354.
- HTML extraction still includes some LEX.UZ navigation/service text. Chunking and citation smoke passed, but manual chunk inspection remains necessary before production reliance.
- Civil Code Part One and Tax Code are close to the Stage 7.4 chunk-size ceiling. Laptop use remains acceptable, but final acceptance smoke should watch performance.

## Recommendation For Stage 7.5-D / Stage 7.6

Proceed next to first-batch final acceptance smoke only after user approval.

Recommended:

- verify final active-current status through UI/API using active current only;
- run cross-source retrieval probes for common factory scenarios;
- explicitly verify PP-4348 future remains excluded from ordinary `<TRUSTED_LEGAL_SOURCE>`;
- explicitly verify outdated ZRU-354 remains excluded from ordinary `<TRUSTED_LEGAL_SOURCE>`;
- decide whether ZRU-820 should remain active as an additional current source or be moved to draft until a separate second-batch approval;
- keep ZRU-354 out of ordinary active RAG unless a user explicitly requests historical/outdated-law analysis;
- avoid adding more sources until final acceptance smoke confirms laptop performance.

## Local Data Warning

The local development DB/storage contains the imported Stage 7.5-C legal sources and extracted legal texts. These are local ignored artifacts only.

Raw legal texts, SQLite DB files, and storage files are not committed. Only this report is intended to be committed.
