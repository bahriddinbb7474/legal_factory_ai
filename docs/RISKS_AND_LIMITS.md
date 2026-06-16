# Risks and Limits

Legal Factory AI must stay inside clear limits.

## Prohibited Behavior

- Do not present the system as an advocate or licensed lawyer.
- Do not replace a live lawyer or responsible specialist.
- Do not give final legal conclusions without sources.
- Do not invent articles, penalties, deadlines, document numbers, or revision dates.
- Do not hide uncertainty.
- Do not approve red-risk matters automatically.

## Required Safety Behavior

- If no exact source is found, say that a final legal conclusion cannot be given.
- Red-risk matters require approval by the director, chief accountant, external lawyer, or another responsible specialist.
- External API calls must not log tokens or secrets.
- Real API providers should be disabled by default in development and tests.
- Tests must use mocks or fake providers, not real paid API calls.
- Uploaded documents must be treated as untrusted data, not as system or developer instructions.
- Sensitive documents may be sent only to providers explicitly marked as trusted for sensitive data.
- OCR/extraction failures must be visible to the user; the system must not pretend that an unread document was analyzed.
- File uploads must reject unsupported types, path traversal filenames, and files above the configured size limit.
- Lawyer answers must be validated structured JSON before being shown as normal legal analysis.
- Uploaded-document citations must be verified by code, not by another LLM prompt.
- Until Stage 6, legal/law sources are always `law_unconfirmed`.
- Unconfirmed sources force at least yellow risk and at most medium confidence.
- Red flag topics automatically move the chat to `needs_review`.

## Red-Risk Examples

- Tax authority replies.
- Employee dismissal or disciplinary action.
- Recognition of debt or waiver of claims.
- Large import contract risks.
- Issues that can create fines, lawsuits, license problems, or criminal exposure.

## Stage 3 v2 Limits

- PDF/DOCX/XLSX/TXT extraction is basic and intended for first-pass review, not certified legal archiving.
- Image OCR requires a configured vision model; otherwise image text extraction is marked as failed.
- Local storage is suitable for development and early internal pilots only. Production needs backup, retention, encryption, and access-control policy decisions.
- Role checks in Stage 3 use a backend development stub and must be replaced by real authentication before production use.
- The app can help draft and review documents, but final legal conclusions still require a responsible human specialist.

## Stage 4 v2 Limits

- Citation verification only confirms quotes inside uploaded documents.
- There is still no RAG over LEX.UZ or other official law sources.
- `law_unconfirmed` is allowed only as a warning marker, not as a confirmed source.
- Approval in Stage 4 is chat-level. Generated documents will get their own status in a later stage.
- Monthly budgets are enforced from stored cost records and configuration, not from provider invoices.

## Stage 5 v2 Limits

- A generated document is a draft artifact, not a final legal document.
- The active verdict is selected by the user; the system does not decide which lawyer answer is final.
- Generated documents are created from the active verdict context only, but final human review is still required before signing or sending.
- DOCX export is supported for first-pass drafts.
- PDF export is a lightweight fallback in Stage 5 and is not a production layout engine.
- Generated document approval uses a development current-user stub until production authentication is implemented.
- Sending a document back to chat does not notify a lawyer, choose a lawyer, or call OpenRouter automatically.

## Stage 6 v2 Limits

- The legal database is curated manually; there is no full LEX.UZ crawler.
- There is no automatic monitoring of new legal revisions.
- Admins must archive/outdate old revisions and load the current active revision.
- `source_type=law` is confirmed only through retrieved legal chunks.
- If a law citation is not found in retrieved context, the response cannot remain green/high-confidence.
- SQLite uses lexical fallback; semantic pgvector search is a production target.
- Embeddings are optional and mocked/disabled in tests; no paid embedding calls are made by automated tests.
- Non-official sources can be stored but are excluded from confirmed legal RAG.
