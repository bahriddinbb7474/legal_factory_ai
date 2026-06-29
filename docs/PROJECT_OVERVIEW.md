# Project Overview

Legal Factory AI is an internal AI legal assistant for a cable factory in Uzbekistan.

The project is for the director, accounting, HR, procurement, sales, and production teams. It helps prepare preliminary legal analysis, document drafts, replies to government bodies, debt-related letters, and contract reviews.

Main tasks:

- answer legal questions with sources and risk level;
- review local and import contracts;
- analyze client debt situations;
- draft letters, claims, memos, and legal opinions;
- help with HR and labor questions;
- keep chat history, uploaded documents, costs, and approval status.

The approved target uses natural, human-readable preliminary answers. Structured output is
reserved for a verified verdict from Lawyer 2 or Lawyer 3; Lawyer 1 cannot issue a verdict.
Legal sections use targeted RAG over active official Uzbekistan sources, while uploaded documents
remain untrusted factual material. Backend verification controls verdict, approval, citation, and
document-generation gates.

The program does not replace a live lawyer. It helps prepare work materials and flags when a director, chief accountant, external lawyer, or responsible specialist must approve the conclusion.
