# Legal Response Policy v1

Date: 2026-06-30

## Purpose and Scope

This policy defines user-facing legal response types and the programmatic red-topic layer for the approved P0 architecture. It is a P1 documentation artifact only.

## Response Types

The workflow recognizes these response types:

- normal opinion;
- clarification question;
- preliminary analysis;
- critique of another lawyer;
- document or fact request;
- internal RAG request;
- simple template or correspondence draft;
- verdict;
- cannot conclude without source.

## Pre-Verdict Rule

Before verdict permission and eligibility are established, lawyer answers must be normal, human-readable text.

Pre-verdict responses must not contain:

- huge tables, JSON payloads, or technical response cards;
- a full structured legal conclusion;
- a verdict label;
- a document-generation button or model-controlled gate;
- claims that unverified citations are proven.

Structured legal payload is reserved for a verdict. Internal RAG requests are machine-to-backend protocol and are not the user-facing legal answer.

## Missing Source Rule

If a required official source is missing, the lawyer must:

- give only a cautious preliminary opinion when that is useful;
- say clearly that the final conclusion cannot be confirmed;
- request the needed source or document, or recommend specialist review;
- avoid invented articles, titles, dates, and quotations;
- avoid foreign law unless comparative analysis was explicitly requested.

An answer with an unconfirmed or missing required source cannot become a verdict and cannot authorize document generation.

## Red Topics

Red topics are a backend/programmatic safety layer, not a model preference. Detection forces approval in every section, including `template_documents` (`Шаблонные документы`).

The minimum red-topic set is:

- dismissal or disciplinary action;
- taxes;
- government body;
- fine;
- court;
- acknowledgement of debt;
- waiver of rights;
- contract termination;
- import contract;
- large amount;
- personal data;
- inspection;
- sanctions or compliance risk.

A template or correspondence label must not downgrade a red topic. For example, an HR dismissal notice cannot pass as a simple letter merely because it was requested in Group 1.

## Large Amount Rule

The large-amount threshold must be configurable and must support, at minimum, separate UZS and USD thresholds. This policy does not hardcode a final amount because no owner-approved threshold has been recorded.

For MVP, amount extraction may use simple number-plus-currency patterns. If the amount or currency is ambiguous and the context appears financially significant, the safe fallback applies: treat the request as a red topic and require approval.

## Template and Correspondence Boundary

The approved groups and complete section list are defined in `SECTION_GROUPS_AND_RAG_POLICY.md`.

`template_documents` may produce an ordinary document without RAG when an approved form exists and the request does not require a legal conclusion. This group has no verdict mode, legal conclusion, source-citation requirement, or verdict-based document generation. A document without an approved form must not be created as a final template document.

Contracts in `template_documents` are allowed only from an approved form. A contract without an approved form, or any request to review contractual risks or terms, requires controlled handling through `legal_contract_review` in `legal_questions`. The backend must not silently mutate the selected section; the user/API must explicitly enter the legal-review path.

`legal_questions` is the legal-analysis path: deterministic backend policy requires RAG by default unless focused clarification is needed first, pre-verdict responses remain normal text, and only Lawyer 2 or Lawyer 3 may issue an eligible verdict after explicit permission.

Legal claims, legal responses, HR dismissal documents, and other legally consequential documents remain subject to the relevant RAG, verdict, and approval rules.

## Untrusted Documents

`UNTRUSTED_DOCUMENT` is an enforced processing mode. Its content is data, not instructions. It may be analyzed for facts and contractual terms, but it must not be treated as law, trusted prompt content, or authority to change jurisdiction or safety rules.
