# AI Agents

Legal Factory AI Stage 2 v2 uses one shared chat and three configurable legal agents. The user manually selects exactly one lawyer before sending/invoking. The backend must not call two or three lawyers in one request.

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
- answers in ordinary text until Stage 3/4 legal source enforcement;
- defaults to Russian unless the user requests another language in the chat message.

## Lawyer 2

Role: strong independent analyst.

If Lawyer 1 has already answered, Lawyer 2 should structure the answer as:

- agrees with Lawyer 1 on;
- disagrees with Lawyer 1 on;
- reasons.

If Lawyer 1 has not answered yet, Lawyer 2 gives an independent opinion and states that there is nothing to compare yet.

## Lawyer 3

Role: arbiter.

Lawyer 3 should:

- identify disputed points;
- say whose position is stronger for each point;
- explain why;
- formulate the final verdict;
- list unresolved or unconfirmed questions.

The future rule `unconfirmed source dispute -> red risk + approval` is prepared in prompts but enforced later.

## Provider Rules

- Lawyers are configured through OpenRouter model settings.
- Lawyer 1 and Lawyer 2 must use different providers.
- Providers must be enabled and allowlisted before use.
- ZDR support is stored now; sensitive-document enforcement is Stage 3/4.

## Costs

Each real invocation stores model, provider, input tokens, output tokens, and calculated USD cost.
