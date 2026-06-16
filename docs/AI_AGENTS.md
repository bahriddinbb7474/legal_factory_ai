# AI Agents

Legal Factory AI Stage 4 v2 uses one shared chat and three configurable legal agents. The user manually selects exactly one lawyer before sending/invoking. The backend must not call two or three lawyers in one request.

## Shared Chat Rule

Every invoked lawyer receives the full current chat context, with explicit authors:

- `Пользователь`
- `Юрист 1`
- `Юрист 2`
- `Юрист 3`
- `Система`

This prevents mixing authors and lets Lawyer 2 compare with Lawyer 1, while Lawyer 3 can act as arbiter.

## Lawyer 1

Role: fast practical lawyer.

- quick and practical analysis;
- reads the full chat history;
- does not present itself as an advocate;
- does not invent sources;
- returns strict structured JSON according to the legal response schema;
- may leave `agreement` as `null`;
- defaults to Russian unless the user requests another language in the chat message.

## Lawyer 2

Role: strong independent analyst.

If Lawyer 1 has already answered, Lawyer 2 should structure the answer as:

- agrees with Lawyer 1 on;
- disagrees with Lawyer 1 on;
- reasons.

If Lawyer 1 has not answered yet, Lawyer 2 gives an independent opinion and states that there is nothing to compare yet.

Backend requires Lawyer 2 to return the `agreement` object with `agreed_points`, `disagreed_points`, and `unresolved_points`.

## Lawyer 3

Role: arbiter.

Lawyer 3 should:

- identify disputed points;
- say whose position is stronger for each point;
- explain why;
- formulate the final verdict;
- list unresolved or unconfirmed questions.

Stage 4 enforces: if Lawyer 3 has unresolved points without confirmed sources, backend forces `risk=red` and `approval_required=director`.

## Structured Output

Each lawyer answer must be valid JSON with:

- `summary`;
- `risk`;
- `findings`;
- `sources`;
- `meaning_for_factory`;
- `actions`;
- `confidence`;
- `approval_required`;
- `agreement`.

Unknown fields are rejected. Invalid JSON is not displayed as a normal answer. Backend may make one safe repair attempt and then fails clearly.

## Provider Rules

- Lawyers are configured through OpenRouter model settings.
- Lawyer 1 and Lawyer 2 must use different providers.
- Providers must be enabled and allowlisted before use.
- ZDR support is stored now.
- Sensitive uploaded documents may be sent only to providers marked trusted for sensitive data.

## Costs

Each real invocation stores model, provider, input tokens, output tokens, and calculated USD cost.

Monthly budget safeguards use stored `CostRecord` rows. At the warning threshold the backend logs a warning; at 100%, non-admin calls can be blocked if `BLOCK_EXPENSIVE_CALLS=true`.

## Stage 5 Verdict-to-Document Rule

Lawyers can produce analysis, but a document draft is generated only after the user marks one lawyer message as the active verdict.

Document-generation prompts include an explicit `<ACTIVE_VERDICT>` block and tell the model not to use earlier opinions or rejected/non-verdict chat messages as drafting sources. This keeps the document workflow anchored to the user-approved legal position.

Sending a generated document back to the chat is not a lawyer invocation. It creates a normal chat message/card only; the user must manually choose Lawyer 1, Lawyer 2, or Lawyer 3 in the composer for any later review.
