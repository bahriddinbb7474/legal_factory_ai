# Stage 7.3 Trial Legal Source Upload Smoke Report

Date: 2026-06-16

Scope: manual trial upload of three LEX.UZ legal sources into a local ignored SQLite smoke database. This was not a crawler, not a mass import, and not Stage 7.4/7.5 implementation. Raw legal texts, local DB files, and local storage files are not committed.

Local smoke database: `data/stage7_3_smoke_20260616_v2.db` (ignored by git).

## Summary

The Stage 7 legal source upload path is usable for a small manual upload smoke. Metadata readiness checks passed for the three trial sources, Russian law/code sources chunked into article-level chunks, lexical retrieval worked for active Russian sources, and citation verification correctly confirmed exact quotes and rejected wrong quotes.

The main blocker before loading 15-30 real sources is Uzbek/Russian mixed resolution chunking quality for some LEX.UZ pages: PP-4348 imported as one 74k-character chunk with `article_or_point=unknown`. This is acceptable for a trial smoke, but not acceptable for a larger curated factory legal base without hardening.

## Sources Uploaded

| Source | URL | Document type | Number | Adoption date | Revision / ONDATE | Language | Initial status | Final status | Chunks | Warnings | Activation decision |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | ---: | --- | --- |
| Law of Uzbekistan on Appeals of Individuals and Legal Entities | https://lex.uz/ru/docs/3336171 | law | ZRU-445 | 2017-09-11 | 2026-05-07 | ru | draft | active | 113 | none | Activated for local smoke after metadata and chunk inspection |
| Civil Code of Uzbekistan, Part Two | https://lex.uz/ru/docs/180550 | code | b/n | 1996-08-29 | 2026-05-07 | ru | draft | active | 1824 | none | Activated for local smoke after metadata and chunk inspection |
| PP-4348 / PQ-4348 future revision | https://lex.uz/uz/docs/-4360770?ONDATE=01.07.2026%2000#edi-6955857 | presidential_resolution | PP-4348 | 2019-05-30 | 2026-07-01 ONDATE | uz | draft | draft | 1 | none | Kept draft because it is a future-effective source for 2026-07-01 |

Note: LEX.UZ returned 404 for Russian URLs with `?ONDATE=16.06.2026%2000` and `?ONDATE=16.06.2026`, so the Russian trial sources used the canonical document URLs while preserving the confirmed revision date in metadata.

## Per-Source Notes

### Appeals Law, ZRU-445

- Upload worked through the existing admin legal source endpoint using `raw_text`.
- Metadata captured: source URL, document number, adoption date, revision date, source name, language, official status.
- Readiness warnings: none.
- Chunking: 113 chunks, article-level labels detected. Sample chunks included `Statya 1`, `Statya 2`, `Statya 3`.
- Retrieval smoke: query for appeals of legal entities returned active source hits, including `Statya 14`, `Statya 1`, and `Statya 2`.
- Citation smoke: exact quote confirmed; modified/wrong quote became unconfirmed and downgraded risk/confidence from green/high to yellow/medium.

### Civil Code, Part Two

- Upload worked through the existing admin legal source endpoint using `raw_text`.
- Metadata captured: source URL, document number, adoption date, revision date, source name, language, official status.
- Readiness warnings: none.
- Chunking: 1824 chunks, article-level labels detected. Sample chunks included `Statya 386`, `Statya 387`, `Statya 388`.
- Retrieval smoke: query for sale/supply contract terms returned relevant active hits, including `Statya 386`, `Statya 389`, and `Statya 418`.
- Citation smoke: exact quote confirmed; modified/wrong quote became unconfirmed and downgraded risk/confidence from green/high to yellow/medium.

### PP-4348 / PQ-4348 Future Revision

- Upload worked through the existing admin legal source endpoint using `raw_text`.
- Metadata captured: source URL with future `ONDATE=01.07.2026`, document number, adoption date, revision date, source name, language, official status.
- Readiness warnings: none.
- Status decision: kept `draft`; it must not be exposed to active legal RAG before the effective/future date is explicitly approved.
- Retrieval smoke: no active retrieval hits, as expected, because `draft` sources are excluded from the active official retriever.
- Citation smoke: direct verifier mechanics confirmed exact quote and rejected wrong quote, but this was not active RAG exposure.
- Chunking issue: only 1 chunk was produced, `article_or_point=unknown`, about 74k characters. This needs fixing before a larger Stage 7 import.

## Issues Found

- LEX.UZ `ONDATE` URL format is inconsistent. The future Uzbek PP URL worked, while Russian current-date URLs returned 404. Stage 7 needs a documented manual URL rule per source.
- PP-4348 chunking is too coarse. The current chunker did not split the Uzbek resolution into practical clauses/points.
- HTML extraction includes LEX.UZ navigation/service text inside chunks. Retrieval still works, but previews and quote selection are noisy.
- Large documents are locally manageable, but Civil Code part two produced 1824 chunks from one source. Stage 7 should watch laptop performance before loading 15-30 sources.
- Citation verification depends on exact metadata matching. Any title/number/revision normalization mismatch can make a real citation unconfirmed.

## Recommendation For Stage 7.4

Proceed to Stage 7.4 only after adding a focused chunk/retriever verification pass for the first three sources:

- Add manual acceptance checks for article/point labels, chunk size, and navigation-noise ratio.
- Harden chunking for Uzbek and mixed-language LEX.UZ pages before activating PP/PKM-style sources.
- Decide the canonical URL policy: base URL for current Russian pages, exact `ONDATE` URL for future or date-specific pages.
- Keep future-effective sources in `draft` until manually approved.
- Add regression tests for PP/PKM Uzbek clause splitting and active retriever exclusion of draft sources.

## Local Data Warning

The local development machine may now contain ignored smoke artifacts under `data/` and `data/uploads/`. These are local-only verification artifacts. No raw legal texts, SQLite smoke DB files, or storage files are committed.
