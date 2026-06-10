# Testing Strategy

Testing must verify that Legal Factory AI behaves like a controlled legal assistant, not a free-form chatbot.

## Legal Response Checks

- The answer contains a source.
- The answer contains a revision date when applicable.
- The answer contains a document number when applicable.
- The answer contains an article or clause when applicable.
- The answer contains a risk level.
- The answer does not invent legal norms.
- If no source is found, the answer blocks final legal conclusions.
- Red-risk questions go to approval.

## Application Checks

- Users can log in with assigned roles.
- Users can create chats and send messages.
- Files can be uploaded and attached to chats.
- Documents can be created in the right editor.
- Agent model settings are saved and applied.
- Token and cost records are created.
- Audit records include user, agent, sources, risk, cost, approval, and final document.

## Provider Checks

- Tests must not call real OpenRouter APIs.
- Fake providers must be used in automated tests.
- Missing API keys must produce clear disabled-provider behavior.
