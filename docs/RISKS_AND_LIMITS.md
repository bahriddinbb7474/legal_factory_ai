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

## Red-Risk Examples

- Tax authority replies.
- Employee dismissal or disciplinary action.
- Recognition of debt or waiver of claims.
- Large import contract risks.
- Issues that can create fines, lawsuits, license problems, or criminal exposure.
