# Legal Sources

Legal Factory AI should use official and internal sources whenever possible.

## Official Sources

- LEX.UZ.
- regulation.gov.uz.
- gov.uz/adliya.
- my.gov.uz.
- license.gov.uz.
- Tax Committee sources.
- Customs Committee sources.
- Ecology authority sources.
- Labor authority sources.
- Fire safety authority sources.
- Sanitary authority sources.

## Internal Sources

- Factory contracts.
- Import contracts.
- Client debt files.
- Letters from government bodies.
- HR documents.
- Orders and internal policies.
- Occupational safety documents.
- Certificates.
- Templates.

## Citation Requirement

Legal answers should include source name, document number, revision date, article or clause, quote, and practical meaning for the factory. If these fields cannot be found, the answer must not be presented as a final legal conclusion.

## Stage 6 v2 Curated Core

Stage 6 uses a curated core of manually loaded legal sources. It is not a full LEX.UZ crawler.

Allowed document types include:

- `code` — Кодекс;
- `law` — Закон;
- `presidential_decree` — Указ Президента;
- `presidential_resolution` — ПП;
- `cabinet_resolution` — ПКМ;
- `ministerial_order` — приказ министерства;
- `technical_regulation`;
- `standard`;
- `sanitary_rule`;
- `fire_safety_rule`;
- `customs_rule`;
- `tax_rule`;
- `other`.

Admins can upload a UTF-8 text file or paste raw text. The source must store title, type, number if known, source name, URL, adoption date if known, revision date if known, language, status, and official status.

`LEX.UZ` is the primary source name for confirmed official sources. Non-official sources can be stored, but they are not used as confirmed legal authority in normal RAG.

## Revision Freshness

On upload:

- `last_checked_at` is set to the upload time;
- `next_check_due_at` is set to 30 days later.

If the due date has passed, the admin UI shows `Редакцию нужно проверить`. The source can still be used, but the warning is visible. Automatic update monitoring is not implemented in Stage 6.

## Retrieval Rules

Only `active` and `official` sources are returned by the retriever.

Old revisions should be marked `archived` or `outdated`; they remain in the database for history but do not enter normal lawyer context.

Law citations are confirmed only when the model quotes text from a chunk returned by the legal retriever. A model-invented article, ПП/ПКМ number, or quote remains unconfirmed.

## Stage 7 Legal Base Completion

Stage 7 is the next main stage after curated legal RAG. The goal is to fill the system with 15-30 real official sources needed by a cable factory in Uzbekistan.

Primary source:

- `LEX.UZ`

Required metadata for every source:

- `document_type`
- `title`
- `document_number`
- `adoption_date`
- `revision_date`
- `source_name`
- `source_url`
- `official_status`
- `status=active`
- `language`
- `last_checked_at`
- `next_check_due_at`

Required source categories:

- Contracts and obligations: Civil Code, supply contracts, late payment, claims work.
- Import and customs: Customs Code, ПП/ПКМ on customs benefits, raw material import, certificates of origin, invoices, contracts.
- Taxes: Tax Code, VAT, tax audits, electronic invoices.
- Labor and HR: Labor Code, dismissal, disciplinary penalties, employee personal data.
- Occupational safety: labor protection, accidents, fire safety, sanitary requirements.
- Production, certification, and technical regulation: technical regulations, cable product certification, metrology, O'z DSt/GOST where applicable, ecology.
- Government bodies: inspections, replies to state bodies, licenses/permits where applicable.

Revision rule:

- New active revision is loaded as `active`.
- Old revision is moved to `archived` or `outdated`.
- Normal RAG uses only `active` official revisions.
- Monthly revision checks remain mandatory through `last_checked_at` and `next_check_due_at`.

Stage 7 acceptance criteria:

1. At least 15 real sources are loaded.
2. Every source has a LEX.UZ URL.
3. Every source has a revision date.
4. Chunking succeeds for each source.
5. Retriever finds the expected clauses/points.
6. Lawyers can cite `source_type=law`.
7. Correct law quotes are confirmed.
8. Wrong law quotes are rejected/unconfirmed.
9. Outdated revisions show a freshness warning.

## Stage 7.1 Source Readiness Checklist

Before loading the first 15-30 real sources, every candidate source should be checked in the admin legal base UI.

Required metadata for manual upload:

- `document_type`;
- `title`;
- `document_number`;
- `adoption_date`;
- `revision_date`;
- `source_name`;
- `source_url`;
- `official_status`;
- `status`;
- `language`;
- `last_checked_at`;
- `next_check_due_at`.

Readiness warnings are non-blocking in Stage 7.1, but must be resolved before a source is trusted as active:

- `missing_source_url`;
- `missing_document_number`;
- `missing_adoption_date`;
- `missing_revision_date`;
- `missing_source_name`;
- `active_without_official_status`;
- `active_without_revision_date`;
- `official_source_without_url`;
- `lexuz_expected_for_official_law`;
- `lexuz_source_with_bad_url`;
- `next_check_due_or_overdue`.

Chunk inspection:

1. Upload or paste the source text as `draft` first when possible.
2. Open `Показать chunks` in the legal base UI.
3. Check that articles, points, subpoints, and appendices are separated in a useful way.
4. Use `Reindex` after metadata or source text preparation changes.
5. Run retrieval/citation smoke checks before moving the source to `active`.

A source is ready for `active` when:

- it comes from the current official revision, preferably LEX.UZ;
- URL, document number, adoption date, revision date, language, and official status are filled;
- chunks are readable and searchable;
- correct citations are confirmed and wrong citations are rejected;
- `next_check_due_at` is set for the next manual revision check.

There is still no LEX.UZ crawler in Stage 7.1. Sources are copied and verified manually.
