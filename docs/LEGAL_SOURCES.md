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
