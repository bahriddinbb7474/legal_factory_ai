# Decisions Log

## Accepted Decisions

- Project name: Legal Factory AI.
- Main interface language for the first version: Russian.
- Primary users: director, accounting, HR, procurement, sales, and production.
- There is no full-time lawyer in the initial operating assumption.
- Red-risk approval must be handled by the director or chief accountant.
- LLM access will go through OpenRouter.
- Agent models will be selected in admin settings.
- Stage 2 v2 uses one shared chat and manual invocation of exactly one selected lawyer.
- Lawyer 1 and Lawyer 2 must use different OpenRouter providers.
- Provider allowlist is enforced before invoking a model.
- OpenRouter model list is fetched dynamically instead of hardcoding all models.
- ZDR support is stored in provider/model settings; sensitive-data enforcement is deferred.
- The first UI language remains Russian; no user language preference field is added in Stage 2 v2.
- Costs are stored per chat, lawyer, provider, model, and token usage.
- Real company documents may be sent to external LLM APIs only after the responsible business owner approves this operating model.
- Both Web UI and Telegram are needed, but Web UI comes first.

## Pending Decisions

- Exact production OpenRouter models for Lawyer 1, Lawyer 2, and Lawyer 3 after manual testing.
- Production hosting model.
- Backup policy for uploaded documents.
- Retention period for chats, files, and audit logs.
- Whether Telegram approval is allowed for all red-risk cases or only selected categories.
