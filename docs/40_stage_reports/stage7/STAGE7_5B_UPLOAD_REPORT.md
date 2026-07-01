# Stage 7.5-B Upload Report

Date: 2026-06-17

## Scope

Stage 7.5-B only: manually import and smoke-check the next four approved LEX.UZ sources from the Stage 7 registry.

- 4 sources only.
- No crawler.
- No mass import.
- No historical LEX.UZ auto-import.
- No future versions imported or activated.
- No raw law texts committed.
- No local DB/storage committed.
- No backend/frontend functional changes.
- No Stage 7.5-C/D work.

Local smoke DB used:

```text
data/stage7_3_smoke_20260616_v2.db
```

This DB and related `data/uploads` storage are ignored local artifacts.

## Source Summary

| Source id / title | Source URL | Document number | Adoption date | Revision date / ONDATE | Language | Initial status | Final status | Chunks | Max chunk size | Warnings | Activation decision |
| --- | --- | --- | --- | --- | --- | --- | --- | ---: | ---: | --- | --- |
| 8 / Code of Uzbekistan on Administrative Responsibility | https://lex.uz/ru/docs/97664?ONDATE=13.06.2026 | 2015-XII | 1994-09-22 | 2026-06-13 ONDATE | uz | draft | active | 546 | 8665 | none | Activated after metadata, chunk, retrieval, and citation smoke |
| 9 / Law of Uzbekistan on Occupational Safety | https://lex.uz/ru/docs/3031427?ONDATE=18.05.2022 | ZRU-410 | 2016-09-22 | 2022-05-18 ONDATE | uz | draft | active | 77 | 8230 | none | Activated after metadata, chunk, retrieval, and citation smoke |
| 10 / Law of Uzbekistan on Fire Safety | https://lex.uz/ru/docs/1521663 | ZRU-226 | 2009-09-30 | 2026-03-01 | ru | draft | active | 141 | 6937 | none | Activated after metadata, chunk, retrieval, and citation smoke |
| 11 / Law of Uzbekistan on Foreign Economic Activity | https://lex.uz/ru/docs/67345?ONDATE=21.04.2021 | 77-II | 2000-05-26 | 2021-04-21 ONDATE | uz | draft | active | 46 | 4225 | none | Activated after metadata, chunk, retrieval, and citation smoke |

## Future Revision Observation

| Source | Future candidates observed on LEX.UZ | Imported/activated? |
| --- | --- | --- |
| Code of Uzbekistan on Administrative Responsibility | 2026-06-28, 2026-07-01, 2026-07-14, 2026-07-19, 2026-07-22, 2026-07-24, 2026-08-05 | No. Recorded only as future candidates. Current active import uses 2026-06-13 ONDATE. |
| Law of Uzbekistan on Occupational Safety | none observed | No future version imported. |
| Law of Uzbekistan on Fire Safety | 2026-07-22 | No. Recorded only as future candidate. Current active import uses canonical current page with revision metadata 2026-03-01 because `ONDATE=01.03.2026` returned 404. |
| Law of Uzbekistan on Foreign Economic Activity | none observed | No future version imported. |

Future versions remain preparation-only and must not be used as active law before their effective dates.

## Per-Source Notes

### Code of Uzbekistan on Administrative Responsibility

- Metadata captured: LEX.UZ URL, document number, adoption date, revision date/ONDATE, language, official status, last/next check dates.
- Current active version as of 2026-06-17: `2026-06-13 ONDATE`.
- Future LEX.UZ candidates after 2026-06-17 were recorded only; none were imported or activated.
- Readiness warnings: none.
- Chunk inspection: 546 chunks, max chunk size 8665, under the Stage 7.4 hard max.
- Retrieval probes: administrative responsibility, fine, and fire-safety related liability probes returned source hits.
- Citation smoke: correct quote confirmed; fake quote unconfirmed.
- Performance: about 5.9 MB HTML and about 1.61M extracted text characters. Laptop use is acceptable but this is a large source close to the chunk size ceiling.

### Law of Uzbekistan on Occupational Safety

- Metadata captured: LEX.UZ URL, document number, adoption date, revision date/ONDATE, language, official status, last/next check dates.
- Current active version as of 2026-06-17: `2022-05-18 ONDATE`.
- No future revisions were observed.
- Readiness warnings: none.
- Chunk inspection: 77 chunks, max chunk size 8230, under the Stage 7.4 hard max.
- Retrieval probes: occupational safety, employer rights/obligations, and employee instruction/training probes returned source hits.
- Citation smoke: correct quote confirmed; fake quote unconfirmed.
- Performance: about 437 KB HTML and about 110k extracted text characters. Safe for laptop use.

### Law of Uzbekistan on Fire Safety

- Metadata captured: LEX.UZ URL, document number, adoption date, revision date, language, official status, last/next check dates.
- Current active version as of 2026-06-17: `2026-03-01`.
- `ONDATE=01.03.2026` returned 404, so the canonical Russian LEX.UZ URL was used while recording revision metadata from the page.
- Future LEX.UZ candidate `2026-07-22` was recorded only; it was not imported or activated.
- Readiness warnings: none.
- Chunk inspection: 141 chunks, max chunk size 6937, under the Stage 7.4 hard max.
- Retrieval probes: organization duties, fire safety requirements, and state fire supervision probes returned source hits.
- Citation smoke: correct quote confirmed; fake quote unconfirmed.
- Performance: about 354 KB HTML and about 82k extracted text characters. Safe for laptop use.

### Law of Uzbekistan on Foreign Economic Activity

- Metadata captured: LEX.UZ URL, document number, adoption date, revision date/ONDATE, language, official status, last/next check dates.
- Current active version as of 2026-06-17: `2021-04-21 ONDATE`.
- No future revisions were observed.
- Readiness warnings: none.
- Chunk inspection: 46 chunks, max chunk size 4225, under the Stage 7.4 hard max.
- Retrieval probes: foreign economic activity, export/import, and foreign economic activity subjects probes returned source hits.
- Citation smoke: correct quote confirmed; fake quote unconfirmed.
- Performance: about 281 KB HTML and about 61k extracted text characters. Safe for laptop use.

## Existing Source Status Check

The previous Stage 7.3 and Stage 7.5-A sources were available in the same ignored local smoke DB:

| Source | Status | Revision | Chunks | Max chunk size | Active retrieval sample |
| --- | --- | --- | ---: | ---: | --- |
| Law on Appeals of Individuals and Legal Entities | active | 2026-05-07 | 113 | 2991 | sample active hits: 82 |
| Civil Code of Uzbekistan, Part Two | active | 2026-05-07 | 1824 | 2474 | sample active hits: 1661 |
| PP-4348 / PQ-4348 future source | draft | 2026-07-01 | 170 | 3968 | active hits: 0; still excluded |
| Tax Code of Uzbekistan | active | 2026-03-17 | 1249 | 8970 | sample active hits: 563 |
| Customs Code of Uzbekistan | active | 2026-03-01 | 956 | 8526 | sample active hits: 475 |
| Labor Code of Uzbekistan | active | 2026-01-01 | 2444 | 7318 | sample active hits: 537 |
| Law of Uzbekistan on Personal Data | active | 2026-03-27 | 134 | 4402 | sample active hits: 83 |

This confirms the PP-4348 future source remains draft and excluded from active retrieval, while prior active sources remain available.

## Issues Found

- LEX.UZ search ranks newer modifying acts above base laws, so direct source verification required following referenced acts and exact doc IDs.
- Code of Administrative Responsibility has multiple future LEX.UZ revision candidates after 2026-06-17. They were not imported or activated.
- Fire Safety Law shows a future candidate `2026-07-22`. It was not imported or activated.
- Fire Safety Law `ONDATE=01.03.2026` returned 404; the canonical URL was used with explicit revision metadata.
- HTML extraction still includes some LEX.UZ navigation/service text. Chunking and citation smoke passed, but manual chunk inspection remains necessary before production reliance.
- Large sources remain manageable locally, but the Administrative Responsibility Code is heavy and close to the max chunk-size ceiling.

## Recommendation For Stage 7.5-C

Proceed to the next small batch only after user approval.

Recommended:

- continue with 3-4 sources per batch;
- keep every new source as `draft` until metadata, chunk, retrieval, and citation smoke passes;
- record future revisions only as future candidates unless the user explicitly approves future/draft import;
- prefer exact ONDATE URLs when LEX.UZ accepts them;
- document any ONDATE 404 and use canonical URL only with explicit revision metadata;
- watch laptop performance for large codes.

## Local Data Warning

The local development DB/storage contains the imported Stage 7.5-B legal sources and extracted legal texts. These are local ignored artifacts only.

Raw legal texts, SQLite DB files, and storage files are not committed. Only this report is intended to be committed.
