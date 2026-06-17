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

## Source Summary

| Source id / title | Source URL | Document number | Adoption date | Revision date / ONDATE | Language | Initial status | Final status | Chunks | Max chunk size | Warnings | Activation decision |
| --- | --- | --- | --- | --- | --- | --- | --- | ---: | ---: | --- | --- |
| 12 / Civil Code of Uzbekistan, Part One | https://lex.uz/ru/docs/111189?ONDATE=30.12.2025 | b/n | 1995-12-21 | 2025-12-30 ONDATE | uz | draft | active | 336 | 8948 | none | Activated after metadata, chunk, retrieval, and citation smoke |
| 13 / Law of Uzbekistan on Currency Regulation | https://lex.uz/ru/docs/4562834 | ZRU-573 | 2019-10-22 | 2025-04-18 | uz | draft | active | 72 | 5589 | none | Activated after metadata, chunk, retrieval, and citation smoke |
| 14 / Law of Uzbekistan on Technical Regulation | https://lex.uz/ru/docs/6392314?ONDATE=19.01.2026 | ZRU-819 | 2023-02-27 | 2026-01-19 ONDATE | ru | draft | active | 204 | 7841 | none | Activated after metadata, chunk, retrieval, and citation smoke |
| 15 / Law of Uzbekistan on Accreditation of Conformity Assessment Bodies | https://lex.uz/ru/docs/6392307?ONDATE=29.08.2023 | ZRU-820 | 2023-02-27 | 2023-08-29 ONDATE | ru | draft | active | 86 | 3772 | none | Activated after metadata, chunk, retrieval, and citation smoke |

## Future Revision Observation

| Source | Future candidates observed on LEX.UZ | Imported/activated? |
| --- | --- | --- |
| Civil Code of Uzbekistan, Part One | 2026-06-29 | No. Recorded only as future candidate. Current active import uses 2025-12-30 ONDATE. |
| Law of Uzbekistan on Currency Regulation | none observed after 2026-06-17 | No future version imported. |
| Law of Uzbekistan on Technical Regulation | none observed after 2026-06-17 | No future version imported. |
| Law of Uzbekistan on Accreditation of Conformity Assessment Bodies | none observed after 2026-06-17 | No future version imported. |

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
- Source title note: the Stage 7 registry names this category as `Law on Conformity Assessment`; LEX.UZ search did not show a separate exact-title law. The official source found and imported for this category is `Law on Accreditation of Conformity Assessment Bodies`, ZRU-820.
- No future revisions were observed after 2026-06-17.
- Readiness warnings: none.
- Chunk inspection: 86 chunks, max chunk size 3772, under the Stage 7.4 hard max.
- Retrieval probes: conformity assessment, accreditation, conformity assessment bodies, and accreditation certificate probes returned source hits.
- Citation smoke: correct quote confirmed; fake quote unconfirmed.
- Performance: about 241 KB HTML and about 50k extracted text characters. Safe for laptop use.

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

This confirms the PP-4348 future source remains draft and excluded from active retrieval, while prior active sources remain available.

## First Batch Completion Status

| Metric | Count | Note |
| --- | ---: | --- |
| Active current sources | 14 | All current first-batch sources imported so far passed smoke and are active. |
| Draft/future sources | 1 | PP-4348 / PQ-4348 `ONDATE=2026-07-01` remains draft/future before its effective date. |
| Total first-batch sources covered | 15 | Includes 14 current active sources plus 1 future draft source. |

Ordinary RAG should continue to use only active official sources. PP-4348 remains excluded from ordinary active retrieval until its effective date and a later approved activation check.

## Issues Found

- LEX.UZ search ranks newer modifying acts above base laws, so direct source verification required exact doc IDs and revision checks.
- Civil Code Part One has a future LEX.UZ candidate `2026-06-29`. It was not imported or activated.
- Currency Regulation `ONDATE=18.04.2025` returned 404; the canonical URL was used with explicit revision metadata.
- The conformity-assessment registry title is ambiguous: LEX.UZ did not show a separate exact-title `Law on Conformity Assessment`. The imported official law is `Law on Accreditation of Conformity Assessment Bodies`, ZRU-820, which matches the conformity assessment category and smoke probes.
- HTML extraction still includes some LEX.UZ navigation/service text. Chunking and citation smoke passed, but manual chunk inspection remains necessary before production reliance.
- Civil Code Part One and Tax Code are close to the Stage 7.4 chunk-size ceiling. Laptop use remains acceptable, but final acceptance smoke should watch performance.

## Recommendation For Stage 7.5-D / Stage 7.6

Proceed next to first-batch final acceptance smoke only after user approval.

Recommended:

- verify final 14-active + 1-draft status through UI/API;
- run cross-source retrieval probes for common factory scenarios;
- explicitly verify PP-4348 future remains excluded from ordinary `<TRUSTED_LEGAL_SOURCE>`;
- review the conformity-assessment source-title ambiguity with the user before treating it as final production coverage;
- avoid adding more sources until final acceptance smoke confirms laptop performance.

## Local Data Warning

The local development DB/storage contains the imported Stage 7.5-C legal sources and extracted legal texts. These are local ignored artifacts only.

Raw legal texts, SQLite DB files, and storage files are not committed. Only this report is intended to be committed.
