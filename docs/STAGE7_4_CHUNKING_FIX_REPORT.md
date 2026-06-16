# Stage 7.4 Legal Chunking Fix Report

Date: 2026-06-16

Scope: improve legal source chunking for manually uploaded real LEX.UZ acts. No crawler, no mass download, no embeddings, no Telegram, no VPS/deployment, and no Stage 7.5 work.

## Root Cause

The Stage 7.3 PP-4348 / PQ-4348 trial source became one huge chunk because the previous chunker recognized only a narrow set of explicit headings: articles, named points, named subpoints, and simple appendices. Real LEX.UZ resolution text often contains numbered clauses, nested numbered clauses, letter subparagraphs, annex headings, Uzbek `band` / `ilova` headings, and long HTML-extracted text blocks.

The fallback path also had no hard maximum split for a single very large paragraph or HTML-extracted block, so an unrecognized source could remain as one oversized chunk.

## Added Chunking Patterns

The chunker now recognizes:

- existing article headings: `Statya`, `Modda`;
- existing named point headings: `Punkt`;
- existing named subpoint headings: `Podpunkt`;
- numbered clauses at line start: `1.`, `2.`, `10.`;
- nested numbered clauses: `1.1.`, `2.3.`;
- letter subparagraphs: Cyrillic and Latin `a)`, `b)` style labels;
- annex headings: `Prilozhenie`, uppercase annex headings, `Ilova`, numbered annexes;
- Uzbek-style annex headings: `1-ilova`;
- table/annex section headings such as passport/list/scheme/regulation headings;
- Uzbek `band`, `kichik band`, and `1-band` style headings.

The detector also filters date-like LEX.UZ lines such as `30.05.2019` so they are not treated as nested subpoints.

## Hard Max Fallback Policy

Defaults:

- target chunk size: about 3500 characters;
- hard maximum chunk size: 9000 characters.

If legal headings are found, each structured block is still split when it exceeds the hard max. If no useful headings are found, fallback chunking splits by paragraph boundaries first, then by line/sentence/word-safe size boundaries. This prevents a single 70k+ character chunk while preserving source ordering and chunk indexes.

Oversized fallback chunks are marked with `metadata_json.chunking = "fallback_size_split"`. Structured chunks include `metadata_json.pattern` with the matched heading category.

## Tests Added

Added `backend/tests/test_stage7_4_legal_chunker_real_law.py`.

Coverage:

- presidential resolution with plain numbered clauses;
- nested numbered clauses and letter subparagraphs;
- annex splitting;
- huge unstructured fallback split;
- existing article behavior preservation;
- Uzbek `band` and `ilova` support;
- LEX.UZ date-like lines are not treated as legal subpoints;
- synthetic PP/PQ-like long document regression with citation verifier checks.

Existing Stage 6/7 legal RAG tests were also run with the new chunker.

## Local PP-4348 Reindex Smoke

The ignored Stage 7.3 local smoke database was used only for local verification:

```text
data/stage7_3_smoke_20260616_v2.db
```

Result after reindexing the draft PP-4348 source with the improved chunker:

- source status remained `draft`;
- chunk count: 170;
- max chunk size: 3968 characters;
- first labels included `1-ILOVA`, `2-ILOVA`, `3-ILOVA`, `4-ILOVA`, then numbered points;
- active retrieval hits for the draft PP-4348 source: 0.

The DB/storage artifacts remain ignored local files and are not committed.

## Remaining Limitations

- HTML extraction from LEX.UZ can still include navigation/service text; admins must inspect chunks before setting a source to `active`.
- Some labels may still be generic (`Point N`) when the source has numeric clauses without explicit legal words.
- The chunker is lexical and rule-based; semantic retrieval/embeddings remain intentionally out of scope for Stage 7.4.
- Stage 7.5 citation smoke for the broader source set is not started.
