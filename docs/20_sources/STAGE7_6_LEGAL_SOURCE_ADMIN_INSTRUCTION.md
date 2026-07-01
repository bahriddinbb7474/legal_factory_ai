# Stage 7.6 Legal Source Admin Instruction

## 1. Purpose

This instruction defines how Legal Factory AI legal sources must be added, checked, archived, and smoke-tested before use in ordinary RAG.

It is the operating procedure for the legal responsible person and the application administrator. It does not authorize crawling LEX.UZ, mass historical imports, or automatic activation of a source.

## 2. Core source-status policy

Ordinary RAG may use only sources where:

```text
status = active
official_status = official
```

Use the statuses as follows:

- `active/current`: the exact current official revision passed metadata, chunk, retrieval, and citation checks;
- `draft/future`: preparation-only source; never current law before its effective date;
- `outdated/historical`: repealed, expired, or superseded revision retained for audit/history and excluded from ordinary RAG;
- related candidate: useful additional act that is not a replacement for an approved source and must be separately reviewed before activation.

The application supports `draft`, `active`, `outdated`, and `archived`. Use `draft` for every new upload. The admin UI defaults to `draft`, but the backend create endpoint defaults to `active` if a caller omits status. API callers must therefore send `status=draft` explicitly.

## 3. Official-source checklist

Before adding a source, record and verify:

- official source URL, normally the exact LEX.UZ page;
- official title;
- document number/code;
- document type;
- adoption date;
- exact `revision_date` or LEX.UZ `ONDATE`;
- `official_status`;
- current, future, outdated, or historical status;
- `last_checked_at`;
- `next_check_due_at`;
- update frequency and update rule;
- responsible legal owner;
- archive/retention reason when the source is not active.

The current `LegalSource` model stores the core runtime metadata through `next_check_due_at`. Update rule, owner, and operational notes remain in the approved registry/manual record until a later metadata stage; do not invent runtime fields or put this information into raw legal text.

If the URL, revision, effective date, or legal status is unclear, stop and keep the source out of active RAG.

## 4. Revision and ONDATE rule

```text
1 legal source record = 1 exact legal revision.
```

- Capture the exact revision/as-of date shown by the official source.
- A future `ONDATE` cannot be active before the effective date.
- A future date becoming current is not automatic activation: manually re-check the official page and rerun all acceptance checks.
- When a new current revision is approved, move the old record to `outdated` or `archived`, then create the new revision as `draft`.
- Never silently replace the old text in an active record.
- Old full text and chunks must not participate in ordinary RAG.
- A historical record may remain for audit/reference, but a separate historical mode is not implemented.

For tax, customs, employment, certification, or other time-sensitive advice, re-check the effective revision before an important answer even when the scheduled monthly check is not yet due.

## 5. Upload and chunking checklist

### Before upload

1. Select `draft` explicitly.
2. Enter complete metadata.
3. Upload only the exact approved official text/revision.
4. Never commit raw texts, upload storage, or local SQLite data to Git.

### After upload or reindex

Verify in the admin UI/API:

- `chunks_count > 0`;
- the act is not one huge chunk;
- maximum chunk size is reasonable and below the current 9,000-character hard limit;
- `article_or_point` is present where the document structure permits it;
- chunk order and previews are readable;
- no mojibake, encoding corruption, navigation-only blocks, or missing sections;
- title, number, revision, source URL, status, official status, check dates, and chunk count are visible;
- readiness warnings are reviewed and resolved before activation.

PP-4348 previously became one approximately 74k-character chunk. After the Stage 7.4 fix it became 170 chunks with a maximum of 3,968 characters. Every large act must receive the same size and preview inspection.

Reindexing updates `last_checked_at` and `next_check_due_at`, but it does not by itself prove that the source is legally current or safe to activate.

## 6. Retrieval smoke checklist

Run the following probes against ordinary RAG:

```text
персональные данные
охрана труда
внешнеэкономическая деятельность
валютное регулирование
обращения физических и юридических лиц
договор поставки гражданский кодекс
налоговое обязательство
таможенный кодекс импорт сырья
трудовой договор
пожарная безопасность
техническое регулирование
сертификация продукции
```

For every intended source verify:

- it appears within `top_k=5`;
- its database status is `active`;
- `official_status` is `official`;
- returned title, number, revision, URL, article/point, and source name match the record;
- a citation can be confirmed when the returned chunk contains the cited norm.

Use at least two or three practical probes per newly activated source. A source that cannot be retrieved for its core subject must stay `draft`.

## 7. Future and outdated regression smoke

Always repeat these controls after retrieval or alias changes:

- `PP-4348`, `таможенная пошлина льгота сырье`, and `ONDATE 2026-07-01` must not expose PP-4348 as current active law before 2026-07-01. On or after that date, it still requires a new manual official-source check and smoke before activation.
- `ЗРУ-354`, `Об оценке соответствия`, and `оценка соответствия` must not expose ZRU-354 as current active law. It expired on 2023-08-29 and is historical only.
- Technical-regulation/current conformity probes should prefer current ZRU-819 and other verified current acts.
- Accreditation probes may return active related ZRU-820; it is not a replacement for ZRU-354.

Any future or outdated source appearing as current `<TRUSTED_LEGAL_SOURCE>` is a blocking failure.

## 8. Citation verification checklist

For each source activation:

1. **Confirmed case:** cite an exact norm present in a retrieved chunk. Verify `verification_status=confirmed` and the source card metadata.
2. **Unconfirmed case:** use a false, changed, or absent quote. Verify `verification_status=unconfirmed`.
3. Verify an unconfirmed law cannot remain `risk=green` or `confidence=high`; it must receive a warning/downgrade.
4. Verify missing/overdue revision checks produce the freshness warning.
5. Review title, document number, revision, article/point, source name, URL where exposed, and quoted text.

Metadata and quote matching are deterministic. A title, number, revision, or article mismatch can make a real quotation unconfirmed and must be investigated rather than bypassed.

## 9. TRUSTED versus UNTRUSTED

User-uploaded contracts, letters, spreadsheets, PDFs, DOCX files, and JPG/PNG images are `UNTRUSTED_DOCUMENT`.

- They may provide case facts or evidence.
- Their exact quotations may be verified against their extracted file text.
- They cannot confirm a legal norm or become a curated law merely because the file mentions legislation.

Only approved `LegalSource` and `LegalChunk` records that pass ordinary RAG filters can produce `TRUSTED_LEGAL_SOURCE`. If an act is absent from trusted context, the structured answer must use `law_unconfirmed` and avoid a final confirmed legal conclusion.

## 10. Search-alias policy

Curated source aliases live outside `legal_retriever.py` in:

```text
backend/app/services/legal_source_search_metadata.py
```

`get_source_search_aliases(source)` helps Russian queries match approved sources whose imported titles may be English or transliterated. Unknown document numbers return an empty alias list. The provider affects ranking only; it cannot bypass `active + official` filtering or change a source status.

Do not place first-batch alias dictionaries directly in `legal_retriever.py`. Add or change a curated alias only with a deterministic retrieval regression test and repeat the future/outdated smoke. Admin-managed aliases may move to `LegalSource` metadata/admin UI in a later approved stage.

## 11. Accepted first-batch state

Stage 7 acceptance history:

- initial Stage 7.5-D result: **FAIL**, because ranking ignored source metadata and aliases;
- R1 added metadata-aware ranking and deterministic regression tests;
- R1a moved curated aliases out of the retriever into the search metadata provider;
- repeat Stage 7.5-D result: **PASS WITH NOTES**;
- Stage 7 MVP first batch can be closed: **YES**.

Accepted registry state:

- 13 active/current approved first-batch sources;
- 1 future/draft source: PP-4348, ONDATE 2026-07-01;
- 1 outdated/historical source: ZRU-354;
- ZRU-820: active related additional source/candidate outside the original approved first-batch list, not a replacement for ZRU-354.

## 12. Known limitations after Stage 7

- Lexical/linear retrieval is acceptable for the local MVP, not final enterprise search.
- Repeat-smoke retrieval took approximately 0.93-3.55 seconds per call on the current workstation.
- The retriever scans all active chunks for every request.
- Answer source cards expose less metadata than admin source cards.
- Admin-managed aliases in the database/UI are not implemented.
- pgvector/embeddings are deferred.
- Telegram and VPS/deployment are deferred.
- No LEX.UZ crawler exists.
- No automatic historical mass import or historical/future answer mode exists.

These are non-blocking for Stage 7 MVP and must be handled only in separately approved later work.

## 13. When activation must be blocked

Do not activate a source when:

- official URL is missing or not verified;
- `revision_date` / `ONDATE` is missing or unclear;
- its future effective date has not arrived;
- it is outdated, repealed, expired, or superseded;
- metadata is incomplete or inconsistent;
- text/chunks are unreadable, corrupted, empty, or dominated by navigation noise;
- chunks are too large or not searchable;
- the intended source does not appear within `top_k=5` for basic probes;
- a correct basic citation cannot be confirmed;
- a wrong citation is incorrectly confirmed;
- future/outdated regression smoke fails;
- the responsible legal person cannot determine whether the revision is current.

Record the blocker, keep the record `draft` or mark it `outdated`, and do not work around the safeguard.

## 14. Admin workflow summary

1. Identify the official source.
2. Confirm exact revision/ONDATE and effective status.
3. Register complete metadata with `status=draft`.
4. Upload/import the exact official text.
5. Inspect chunk count, size, labels, previews, and encoding.
6. Run source-specific retrieval smoke.
7. Run confirmed and unconfirmed citation smoke.
8. Confirm future/outdated exclusion and trusted/untrusted separation.
9. Mark `active` only when all checks pass and the source is current/official.
10. Record `last_checked_at`, `next_check_due_at`, update rule, owner, and any notes/blockers.

For a new revision: archive/outdate the old record first, create the new record as draft, and repeat the full workflow. Never activate by date alone.
