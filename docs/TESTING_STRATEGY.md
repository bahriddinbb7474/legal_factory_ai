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
- `law_unconfirmed` sources remain unconfirmed until Stage 6 RAG/legal sources exist.
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

## Provider Checks

- Tests must not call real OpenRouter APIs.
- Fake providers must be used in automated tests.
- Missing API keys must produce clear disabled-provider behavior.
- OpenRouter and vision calls must be mocked in automated tests.
