# Stage 7.5-D First-Batch Acceptance

Date: 2026-06-18

## Result

- Stage 7.5-D result: **FAIL**.
- Stage 7 MVP first batch can be closed: **NO**.
- Runtime safety filters work, but the prescribed first-batch retrieval matrix is not reliable enough for acceptance.

No runtime code, legal source text, SQLite data, or upload storage was changed during this smoke.

## Scope and evidence

The smoke reviewed:

- the Stage 7 registry, upload reports, conformity correction, version policy, legal source guide, architecture, roadmap, and testing strategy;
- `LegalSource` / `LegalChunk`, upload and reindex API, chunker, lexical retriever, citation verifier, structured answer schema, trusted/untrusted context builders, admin source cards, and answer source cards;
- the ignored local smoke database `data/stage7_3_smoke_20260616_v2.db` in SQLite read-only mode;
- all backend automated tests and the production frontend build.

The local database contains 16 source records and 8,416 chunks:

- 13 active/current approved first-batch sources;
- 1 active related additional source: ZRU-820;
- 1 draft/future source: PP-4348, ONDATE `2026-07-01`;
- 1 outdated/historical source: ZRU-354.

## Source status

### Active/current approved first batch

1. Law on Appeals of Individuals and Legal Entities — ZRU-445.
2. Civil Code, Part Two.
3. Tax Code — ZRU-599.
4. Customs Code — ZRU-400.
5. Labor Code — ZRU-798.
6. Law on Personal Data — ZRU-547.
7. Code on Administrative Responsibility — 2015-XII.
8. Law on Occupational Safety — ZRU-410.
9. Law on Fire Safety — ZRU-226.
10. Law on Foreign Economic Activity — 77-II.
11. Civil Code, Part One.
12. Law on Currency Regulation — ZRU-573.
13. Law on Technical Regulation — ZRU-819.

### Future/draft

- PP-4348 — status `draft`, official status `official`, revision/ONDATE `2026-07-01`, 170 chunks, maximum chunk size 3,968 characters.
- It is excluded from ordinary retrieval.

### Outdated/historical

- ZRU-354, Law on Conformity Assessment — status `outdated`, official status `official`, 18 chunks, maximum chunk size 3,498 characters.
- It is excluded from ordinary retrieval.

### Related candidate

- ZRU-820, Law on Accreditation of Conformity Assessment Bodies — active related additional source.
- It is not a replacement for ZRU-354 and is not counted among the 13 active approved first-batch sources.

## Smoke results

### Status and trust safeguards — PASS

- `LegalRetriever` selects only sources with `status=active` and `official_status=official`.
- PP-4348 never appeared in ordinary retrieval results.
- ZRU-354 never appeared in ordinary retrieval results.
- A ZRU-354 probe returned current ZRU-819 context, not historical ZRU-354 chunks.
- Laws can be confirmed only against retrieved `TRUSTED_LEGAL_SOURCE` chunks with matching metadata and quote text.
- Missing or false law quotes remain unconfirmed and downgrade green/high output.
- Uploaded documents are wrapped in `UNTRUSTED_DOCUMENT`; the prompt permits `source_type=law` only for `TRUSTED_LEGAL_SOURCE` context.
- Automated tests cover confirmed/unconfirmed citations and trusted/untrusted separation.

### Source metadata — PASS WITH NOTE

The admin legal source API and admin cards expose:

- title and document number;
- adoption and revision dates;
- source name and URL;
- status and official status;
- last and next check timestamps;
- chunk count and readiness warnings.

The legal answer source card is intentionally smaller and shows title/number, revision, article or point, source name, quote, and verification result. It does not show status, official status, check timestamps, chunk count, or a clickable source URL. This is non-blocking for the admin acceptance check but should be considered in a later UI improvement.

### Chunking and performance — PASS WITH NOTE

- PP-4348 is no longer a single oversized chunk: 170 chunks, maximum 3,968 characters.
- Maximum chunk size across the database is 8,970 characters; no 74k-character chunk remains.
- A read-only lexical smoke over all 8,416 chunks completed without timeout. Individual in-memory scoring probes took approximately 0.56-0.78 seconds on this workstation.
- The current retriever scans and tokenizes all active chunks for every request. This is acceptable for the current local smoke size, but it is a known scaling limitation.

### Prescribed active retrieval matrix — FAIL

Using the same normalization, score threshold, source ordering, stable score sort, and `top_k=5` behavior as `LegalRetriever`:

| Probe | Expected source | First expected rank | Result |
|---|---|---:|---|
| обращения физических и юридических лиц | ZRU-445 | 1 | PASS |
| договор поставки гражданский кодекс | Civil Code, Part Two | 1 | PASS |
| налоговый кодекс налоговое обязательство | Tax Code | 1 | PASS |
| таможенный кодекс импорт сырья | Customs Code | 1 | PASS |
| трудовой договор | Labor Code | 3 | PASS |
| персональные данные работника | ZRU-547 | 17 | **FAIL: outside top 5** |
| охрана труда на предприятии | ZRU-410 | not found | **FAIL** |
| пожарная безопасность | ZRU-226 | 1 | PASS |
| внешнеэкономическая деятельность | Law on Foreign Economic Activity | not found | **FAIL** |
| техническое регулирование | ZRU-819 | 1 | PASS |
| валютное регулирование | ZRU-573 | not found | **FAIL** |

The failure is caused by the current lexical ranking design:

- score uses chunk text only, not source title or document metadata;
- repeated generic matches from large earlier sources can occupy all five results;
- results have no per-source diversity or exact title/document-number boost;
- several source texts are in a language/transliteration that does not match the Russian probe wording.

This is blocking because ordinary chat receives at most five chunks. A source at rank 17 or absent from the scored set cannot be supplied as trusted context for that request.

## Verification

- Backend: `50 passed`, 2 deprecation warnings.
- Frontend: `npm.cmd run build` passed.
- No external provider calls were made.
- No crawler, download, migration, reindex, or database mutation was performed.

## Recommendation

Do not close Stage 7 first batch yet.

Before repeating Stage 7.5-D, implement and test a narrowly scoped lexical retrieval quality fix. At minimum, the fix should consider source title/document number during ranking and prevent one broad source from consuming all `top_k` positions. Add deterministic acceptance tests for the failed probes using local fixture text; do not use network downloads or real provider calls.

Do not start Stage 7.6 until the failed retrieval probes pass.
