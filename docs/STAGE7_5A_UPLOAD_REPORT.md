# Stage 7.5-A Upload Report

Date: 2026-06-17

## Scope

Stage 7.5-A only: manually import and smoke-check the next four approved LEX.UZ sources from the Stage 7 registry.

- 4 sources only.
- No crawler.
- No mass import.
- No raw law texts committed.
- No local DB/storage committed.
- No backend/frontend functional changes.
- No Stage 7.5-B/C/D work.

Local smoke DB used:

```text
data/stage7_3_smoke_20260616_v2.db
```

This DB and related `data/uploads` storage are ignored local artifacts.

## Source Summary

Correction note added on 2026-06-17: Tax Code `2026-03-17 ONDATE` remains the active/current version for legal answers as of 2026-06-17. LEX.UZ also exposes future Tax Code states for `2026-06-29` and `2026-07-19`; those are preparation-only future revisions and must not be used as active law before their effective dates. `2026-04-17` and `2026-07-14` were checked as ONDATE/as-of URLs, but they were not listed by LEX.UZ as separate Tax Code revision dates.

| Source id / title | Source URL | Document number | Adoption date | Revision date / ONDATE | Language | Initial status | Final status | Chunks | Max chunk size | Warnings | Activation decision |
| --- | --- | --- | --- | --- | --- | --- | --- | ---: | ---: | --- | --- |
| 4 / Tax Code of Uzbekistan | https://lex.uz/ru/docs/4674893?ONDATE=17.03.2026 | ZRU-599 | 2019-12-30 | 2026-03-17 ONDATE | ru | draft | active | 1249 | 8970 | none | Activated after metadata, chunk, retrieval, and citation smoke |
| 5 / Customs Code of Uzbekistan | https://lex.uz/ru/docs/2876352 | ZRU-400 | 2016-01-20 | 2026-03-01 | ru | draft | active | 956 | 8526 | none | Activated after metadata, chunk, retrieval, and citation smoke |
| 6 / Labor Code of Uzbekistan | https://lex.uz/ru/docs/6257291?ONDATE=01.01.2026 | ZRU-798 | 2022-10-28 | 2026-01-01 ONDATE | ru | draft | active | 2444 | 7318 | none | Activated after metadata, chunk, retrieval, and citation smoke |
| 7 / Law of Uzbekistan on Personal Data | https://lex.uz/ru/docs/4396428?ONDATE=27.03.2026 | ZRU-547 | 2019-07-02 | 2026-03-27 ONDATE | ru | draft | active | 134 | 4402 | none | Activated after metadata, chunk, retrieval, and citation smoke |

## Per-Source Notes

### Tax Code of Uzbekistan

- Metadata captured: LEX.UZ URL, document number, adoption date, revision date, language, official status, last/next check dates.
- LEX.UZ showed future revisions after the current date 2026-06-17. The active/current source remains `ONDATE=17.03.2026`, because the next listed Tax Code revision date is `2026-06-29`.
- Additional check: `ONDATE=17.04.2026` was accessible as an as-of URL, but LEX.UZ did not list `2026-04-17` as a separate revision date. `ONDATE=14.07.2026` was also accessible as an as-of URL between future revisions, but LEX.UZ did not list `2026-07-14` as a separate revision date.
- Future Tax Code revisions found: `2026-06-29` and `2026-07-19`. These are for preparation only and must stay draft/future if loaded before their effective dates.
- Readiness warnings: none.
- Chunk inspection: 1249 chunks, max chunk size 8970, under the Stage 7.4 hard max.
- Retrieval probes: VAT/tax, tax inspection, and tax demand probes returned source hits.
- Citation smoke: correct quote confirmed; wrong quote unconfirmed and downgraded green/high to yellow/medium.
- Performance: largest imported source in this batch, about 6.7 MB HTML and about 1.97M extracted text characters. Laptop use is acceptable but close to the chunk size ceiling.
- Local smoke DB status after correction check: only the `2026-03-17` Tax Code source was present; it remained `active`. No future Tax Code source was made active.

### Customs Code of Uzbekistan

- Metadata captured: LEX.UZ URL, document number, adoption date, revision date, language, official status, last/next check dates.
- LEX.UZ `ONDATE=01.03.2026` returned 404, so the canonical Russian URL was used while recording revision date `2026-03-01` from the page.
- Readiness warnings: none.
- Chunk inspection: 956 chunks, max chunk size 8526, under the Stage 7.4 hard max.
- Retrieval probes: customs declaration, customs payments, and customs value/import probes returned source hits.
- Citation smoke: correct quote confirmed; wrong quote unconfirmed and downgraded green/high to yellow/medium.
- Performance: about 3.2 MB HTML and about 914k extracted text characters. Usable locally.

### Labor Code of Uzbekistan

- Metadata captured: LEX.UZ URL, document number, adoption date, revision date, language, official status, last/next check dates.
- Used accessible `ONDATE=01.01.2026`.
- Readiness warnings: none.
- Chunk inspection: 2444 chunks, max chunk size 7318, under the Stage 7.4 hard max.
- Retrieval probes: employment contract, dismissal, and disciplinary penalty probes returned source hits.
- Citation smoke: correct quote confirmed; wrong quote unconfirmed and downgraded green/high to yellow/medium.
- Performance: about 4.2 MB HTML and about 1.29M extracted text characters. Chunk count is high but still manageable.

### Law of Uzbekistan on Personal Data

- Metadata captured: LEX.UZ URL, document number, adoption date, revision date, language, official status, last/next check dates.
- Used accessible `ONDATE=27.03.2026`.
- Readiness warnings: none.
- Chunk inspection: 134 chunks, max chunk size 4402, under the Stage 7.4 hard max.
- Retrieval probes: consent of personal data subject and processing/storage style probes returned source hits. The very generic `personal data` probe returned 0 source hits in top-k because active-source competition and lexical scoring favored other chunks.
- Citation smoke: correct quote confirmed; wrong quote unconfirmed and downgraded green/high to yellow/medium.
- Performance: small/medium source, about 329 KB HTML and about 75k extracted text characters.

## Existing Trial Sources Status Check

The previous Stage 7.3 sources were available in the same ignored local smoke DB:

| Source | Status | Chunks | Max chunk size | Note |
| --- | --- | ---: | ---: | --- |
| Law on Appeals of Individuals and Legal Entities | active | 113 | 2991 | Still active |
| Civil Code of Uzbekistan, Part Two | active | 1824 | 2474 | Still active |
| PP-4348 / PQ-4348 future source | draft | 170 | 3968 | Still draft; active retrieval hits: 0 |

This confirms the future PP-4348 source remains excluded from active retrieval.

## Issues Found

- Tax Code has future LEX.UZ revisions visible after 2026-06-17. The smoke used `ONDATE=17.03.2026`, which remains the current active version as of 2026-06-17. Future `2026-06-29` and `2026-07-19` versions must not become active before their effective dates.
- Customs Code `ONDATE=01.03.2026` returned 404. The canonical URL was used with revision metadata from LEX.UZ.
- LEX.UZ HTML extraction still includes navigation, OKOZ/TSZ and service text in some chunks. Citation verification still works, but admins should inspect chunks before relying on them.
- Personal Data generic probe `personal data` had 0 source hits in top-k; more specific probes passed. This is a lexical retriever limitation, not a source upload failure.
- Large codes are usable locally but heavy: Tax and Labor produced high chunk counts. Batch size should remain conservative.

## Recommendation For Stage 7.5-B

Proceed to the next batch, but keep it small and manual. Recommended:

- continue with 3-4 sources per batch;
- keep all new sources as `draft` until metadata/chunk/retrieval/citation smoke passes;
- prefer exact `ONDATE` URLs when LEX.UZ accepts them;
- document any LEX.UZ `ONDATE` 404 and use canonical URL only with explicit revision metadata;
- use the active current source for current legal answers; use draft/future sources only for future planning with an explicit date warning;
- add stricter retrieval probes for short/generic terms only if lexical ranking becomes a real blocker.

## Local Data Warning

The local development DB/storage may contain the imported Stage 7.5-A legal sources and raw extracted legal texts. These are local ignored artifacts only. Raw legal texts, SQLite DB files, and storage files are not committed. Only this report is intended to be committed.
