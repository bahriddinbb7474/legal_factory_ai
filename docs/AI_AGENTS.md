# AI Agents

Legal Factory AI uses one shared chat and three configurable legal agents. The user manually selects exactly one lawyer before sending/invoking. The backend must not call two or three lawyers in one request.

## Shared Chat Rule

Every invoked lawyer receives the full current chat context, with explicit authors:

- `Пользователь`
- `Юрист 1`
- `Юрист 2`
- `Юрист 3`
- `Система`

This prevents mixing authors and lets Lawyer 2 compare with Lawyer 1, while Lawyer 3 can act as arbiter.

## Lawyer 1

Role: primary fast practical lawyer.

- quick and practical analysis;
- reads the full chat history;
- does not present itself as an advocate;
- does not invent sources;
- asks short clarifying questions when facts are missing;
- requests targeted RAG by default in `legal_questions` unless clarification is needed first;
- returns natural human-readable text before verdict;
- cannot issue a verdict or set verdict/document-generation gates;
- defaults to Russian unless the user requests another language in the chat message.

## Lawyer 2

Role: reviewer, critic, and strong independent analyst.

If Lawyer 1 has already answered, Lawyer 2 should structure the answer as:

- agrees with Lawyer 1 on;
- disagrees with Lawyer 1 on;
- reasons.

If Lawyer 1 has not answered yet, Lawyer 2 gives an independent opinion and states that there is nothing to compare yet.

Before verdict, Lawyer 2 answers in human-readable text. Lawyer 2 may issue a structured verdict
only after explicit user permission and required source checks.

## Lawyer 3

Role: strong lawyer and arbiter.

Lawyer 3 should:

- identify disputed points;
- say whose position is stronger for each point;
- explain why;
- give a preliminary strong opinion before verdict permission;
- list unresolved or unconfirmed questions.

After explicit permission and required source checks, Lawyer 3 may issue a structured verdict.
If unresolved points lack confirmed sources, the backend must block a verified verdict or apply the
required red-risk and approval state.

## Curated Legal RAG Rule

Lawyers use controlled targeted retrieval rather than receiving every chunk by default. They first
receive a source inventory and request the source scope needed for the question.

- Official legal sources are injected as `<TRUSTED_LEGAL_SOURCE ...>`.
- Uploaded factory documents remain `<UNTRUSTED_DOCUMENT ...>`.
- `source_type=law` is confirmed only when the quote and metadata match a retrieved legal chunk.
- `source_type=law_unconfirmed` remains unconfirmed.
- If a legal quote is wrong or not retrieved, backend must block verdict/document eligibility as required.
- A verdict is bound to the concrete source package through `source_package_id` and `context_snapshot_hash`.
- Citation verification uses only that bound package, not every source previously retrieved in the chat.
- Legal and red-topic fallback triggers must support Russian and Uzbek Latin/Cyrillic roots or patterns.

The `template_documents` group does not require RAG by default and has no verdict or legal-conclusion mode. It permits only approved-template work. A missing template or legal-verification request routes to `legal_questions`; red topics override both groups. Canonical groups and sections are defined in `SECTION_GROUPS_AND_RAG_POLICY.md`.

Version rule:

- Current-law answers may rely only on active current official sources from `<TRUSTED_LEGAL_SOURCE ...>`.
- Draft/future, outdated, and archived legal sources must not be used as current law.
- If future-change context is added later, it must be separate from the current answer, carry an effective-date warning, and not confirm ordinary current-law citations.

## Response and Verdict Modes

Before verdict in `legal_questions`, lawyer answers are natural human-readable text. Allowed forms
include an opinion, clarifying question, preliminary analysis, critique, fact/document request,
or source request. Approved-template drafting in `template_documents` is a separate non-verdict
AI-Секретарь flow.

Structured legal payload is reserved for a verdict from Lawyer 2 or Lawyer 3. Explicit user
permission and required source checks are mandatory.

Model-produced values for `confirmed_in_context`, `source_check_status`,
`document_generation_allowed`, and `approval_required` are not trusted. These fields are absent
from the model schema or ignored/overwritten and computed by the backend.

## Provider Rules

- Lawyers are configured through OpenRouter model settings.
- Lawyer 1 and Lawyer 2 must use different providers.
- Providers must be enabled and allowlisted before use.
- ZDR support is stored now.
- Sensitive uploaded documents may be sent only to providers marked trusted for sensitive data.

## Costs

Each real invocation stores model, provider, input tokens, output tokens, and calculated USD cost.

Monthly budget safeguards use stored `CostRecord` rows. At the warning threshold the backend logs a warning; at 100%, non-admin calls can be blocked if `BLOCK_EXPENSIVE_CALLS=true`.

## Verified Verdict-to-Document Rule

Lawyers can produce analysis, but Lawyer 1 cannot issue a verdict. Only Lawyer 2 or Lawyer 3 may
produce a structured verdict after explicit user permission and relevant source checks.

A document draft may be generated from a verdict only after the backend confirms verdict type,
eligible author, permission, source-package binding, citation verification, red-topic approval,
and `document_generation_allowed = true`. The model does not control this gate.

Document-generation prompts include an explicit `<ACTIVE_VERDICT>` block and tell the model not to use earlier opinions or rejected/non-verdict chat messages as drafting sources. This keeps the document workflow anchored to the user-approved legal position.

Sending a generated document back to the chat is not a lawyer invocation. It creates a normal chat message/card only; the user must manually choose Lawyer 1, Lawyer 2, or Lawyer 3 in the composer for any later review.

## Planned Company Profile and Templates

CompanyProfile and approved DocumentTemplate records are the normal path for final documents.
There are two distinct paths:

- `template_documents`: select an approved form and fill CompanyProfile data without a verdict;
- `legal_questions`: use human-readable analysis and, when needed, a verified Lawyer 2/3 verdict before document generation;
- both paths require the applicable backend and approval gates.

Lawyers should not invent company data, bank details, stamp/signature information, document template versions, or approval status. Those values must come from stored project data once the stages are implemented.

There is currently no Telegram workflow. Telegram is postponed and must not be assumed in prompts or agent behavior.

The normative policy documents for P2-P6 are `PROMPT_SYSTEM_V1.md`, `RAG_WORKFLOW_V1.md`,
`LEGAL_RESPONSE_POLICY_V1.md`, `VERDICT_AND_DOCUMENT_POLICY_V1.md`, `QUALITY_GATE_V1.md`, and
`SECTION_GROUPS_AND_RAG_POLICY.md`.
