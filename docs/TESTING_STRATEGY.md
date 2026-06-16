# Testing Strategy

Testing must verify that Legal Factory AI behaves like a controlled legal assistant, not a free-form chatbot.

## Legal Response Checks

- The answer is valid structured JSON before it is displayed as a legal answer.
- Unknown fields are rejected.
- Invalid JSON is not saved as a normal legal answer.
- One safe JSON repair attempt is allowed and counted in tokens/cost.
- The answer contains a source.
- The answer contains a revision date when applicable.
- The answer contains a document number when applicable.
- The answer contains an article or clause when applicable.
- The answer contains a risk level.
- The answer does not invent legal norms.
- If no source is found, the answer blocks final legal conclusions.
- Red-risk questions go to approval.
- Uploaded-document quotes are verified by deterministic string matching against extracted text.
- `law_unconfirmed` sources always remain unconfirmed.
- `source_type=law` is confirmed only when the quote and metadata match a retrieved legal chunk.
- Archived/outdated/draft/non-official legal sources are excluded from normal retriever results.
- Trusted legal source blocks are separate from untrusted uploaded document blocks.
- Unconfirmed sources cannot produce `risk=green` or `confidence=high`.
- Lawyer 2 and Lawyer 3 must include `agreement`.
- Lawyer 3 unresolved disputes without confirmed sources force red risk and director approval.

## Application Checks

- Users can log in with assigned roles.
- Users can create chats and send messages.
- Files can be uploaded and attached to chats.
- Documents can be created in the right editor.
- Agent model settings are saved and applied.
- Token and cost records are created.
- Audit records include user, agent, sources, risk, cost, approval, and final document.
- Red flag rules move the chat to `needs_review`.
- Approval events are a journal; `Chat.approval_status` is the single current status.
- Monthly budget warnings and blocks are tested through stored cost records.
- Legal source upload works through file and raw text paths.
- ПП and ПКМ document types are stored and rendered explicitly.
- Reindex recreates chunks.
- Freshness warnings appear when revision date is missing or the next check date is overdue.

## Provider Checks

- Tests must not call real OpenRouter APIs.
- Fake providers must be used in automated tests.
- Missing API keys must produce clear disabled-provider behavior.
- OpenRouter and vision calls must be mocked in automated tests.
- Embedding calls must be mocked or disabled in automated tests.

## Stage 7-13 Test Blocks

Stage 7 legal source completion:

- at least 15 real legal sources can be loaded with required metadata;
- every source has a LEX.UZ URL and revision date;
- chunking succeeds for every source;
- retriever finds expected clauses/points;
- only active official sources enter normal lawyer context;
- correct `source_type=law` citations are confirmed;
- wrong quotes remain unconfirmed and cannot produce green/high-confidence output;
- overdue revision checks show warnings.

Stage 8 company profile:

- company data saves and updates;
- changes are audit logged;
- logo and letterhead are available for DOCX generation;
- stamp and signature are treated as sensitive;
- only director/admin can manage sensitive company assets.

Stage 9 templates:

- draft/active/archived template statuses work;
- at least five core templates can be active;
- old template versions are archived;
- generated documents can be created from an active verdict and active template;
- CompanyProfile fields are substituted;
- preview and DOCX export render the expected branded structure.

Stage 10 local laptop server:

- backend and frontend run together on the laptop;
- LAN clients can open the app through the local IP;
- 3-4 users can perform chat/upload/RAG/document-generation flows without instability;
- backup and restore commands are tested;
- logs are available for troubleshooting.

Stage 11 auth and roles:

- dev current-user stub is disabled;
- users log in with their own credentials;
- role-based access is enforced by backend endpoints;
- HR documents are hidden from supply users;
- sensitive documents and company stamp/signature are protected;
- approval cannot be bypassed by frontend-only changes.

Stage 12 final factory scenarios:

- client debt;
- claim letter;
- supplier delay;
- contract review;
- import contract;
- tax letter;
- customs letter;
- HR question;
- occupational safety;
- certification/technical regulation;
- state body reply;
- template document generation;
- director approval;
- DOCX export;
- legal source verification.

Stage 13 mini-launch:

- user and admin instructions are complete;
- legal source upload/revision rules are documented;
- approval and sensitive-document rules are documented;
- backup schedule and restore guide are verified;
- responsible owners are assigned.
