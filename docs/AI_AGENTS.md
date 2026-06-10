# AI Agents

Legal Factory AI uses three legal agents. The user interface may show all three, but the system should prefer automatic risk-based escalation so ordinary users do not need to understand model complexity.

## Agent 1: Fast Low-Cost Lawyer

Purpose:

- answer simple questions;
- draft simple letters;
- summarize documents;
- identify whether a question may require deeper review.

## Agent 2: Strong Legal Analyst

Purpose:

- analyze contracts and serious legal questions;
- compare facts with sources;
- produce structured legal conclusions;
- handle yellow-risk and selected red-risk matters.

## Agent 3: Reviewer / Critic

Purpose:

- review Agent 2 answers;
- search for weak assumptions;
- flag missing sources;
- challenge risky conclusions before approval.

## Risk-Based Escalation

- Green risk: Agent 1 can answer.
- Yellow risk: Agent 1 answers and recommends Agent 2 review.
- Red risk: Agent 2 and Agent 3 must review, and approval is required from the director, chief accountant, external lawyer, or responsible specialist.

Every agent must follow the legal response format with source, document number, revision date, article or clause, quote, practical conclusion, confidence, and approval requirement.
