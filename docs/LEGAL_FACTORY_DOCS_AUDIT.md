# Legal Factory AI — Documentation Structure Audit

Date: 2026-07-01
Scope: documentation audit only; no files were moved, renamed, deleted, or merged.

## Executive summary

The six `LEGAL_FACTORY_*` compact documents are suitable as the main ChatGPT Projects knowledge layer. Five should remain the main project context, specification, architecture, decisions, and status documents. `LEGAL_FACTORY_CODER_RULES.md` is useful during migration, but root `AGENTS.md` should be the single universal authority for coding agents; the compact coder-rules file should later become a short onboarding pointer.

The remaining documents fall into four distinct classes:

1. normative policy documents that must remain separate and authoritative;
2. operational guides and source registries that should be grouped but not merged into policy;
3. stage reports and the append-only decision log that are historical evidence, not current status;
4. older snapshots whose current information is already covered by the compact layer and which can be archived after unique details and links are checked.

No historical document should be deleted during the restructuring. Use `git mv`, preserve Git history, add superseded notices where useful, and update inbound links before archival.

## 1. Current documentation inventory

Freshness describes suitability as a **current source of truth**, not the historical value of a file.

| File | Type | Current role | Fresh/stale | Keep/merge/archive candidate | Notes |
|---|---|---|---|---|---|
| `AGENTS.md` | agent-rules | Stable universal project rules for Codex and agentic coders | Fresh | Keep at root; authoritative | Already explicitly separates stable rules from current status. |
| `CLAUDE.md` | agent-rules | Claude Code operating rules | Fresh, with shared-rule overlap | Keep at root; later reduce to Claude-specific deltas plus link to `AGENTS.md` | It already exists; do not create a second copy. |
| `agent.md` | archive-candidate | Older verbose Codex protocol | Stale/duplicated | Archive after checking references and preserving unique rules | Lowercase singular filename is easy to confuse with `AGENTS.md`; contains older workflow assumptions. |
| `README.md` | project-entry | Repository introduction, run commands, broad status | Mostly fresh, mixed historical detail | Keep at root; trim after restructure | Useful entry point, but duplicates status, roadmap, architecture history, and contains visible encoding corruption in some Russian text. |
| `docs/AI_AGENTS.md` | product-agent-reference | Product behavior and responsibilities of Lawyer 1/2/3 | Mixed | Keep; move to `reference/` or `policies/agents/`; link to versioned policies | This describes in-product AI lawyers, not coder-agent rules; do not merge it with `AGENTS.md`. |
| `docs/ARCHITECTURE.md` | architecture-old | Detailed chronological technical architecture and implemented stages | Mixed; current details plus old baseline | Merge unique current details into compact architecture, then move to history/archive | Valuable deep history, but not the best current architecture entry point. |
| `docs/CURRENT_STATE.md` | status-old | Detailed current implementation snapshot | Fresh but duplicate | Convert to pointer or archive after references move to compact status | `AGENTS.md` currently mentions this file, so update that reference before moving it. |
| `docs/DECISIONS_LOG.md` | decision-history | Append-only detailed decision chronology | Mixed by design | Keep as history; move to `history/` | Older statements are historical facts, not current architecture claims. Do not flatten into the compact summary. |
| `docs/DEV_SETUP.md` | setup | Local backend/frontend setup and development commands | Mixed/stale | Keep and refresh; move to `guides/` | Contains old stage/auth assumptions such as development current-user configuration. |
| `docs/FINAL_TARGET.md` | roadmap-old | Early final-product target | Stale/overlapping | Archive after unique requirements are checked | Largely superseded by compact spec/roadmap. |
| `docs/LEGAL_FACTORY_ARCHITECTURE.md` | compact-main | Current high-level architecture and code map | Fresh | Keep as main architecture source | Best architecture document for ChatGPT Projects and coder orientation. |
| `docs/LEGAL_FACTORY_CODER_RULES.md` | compact-main / agent-rules | Human-readable compact coding rules | Fresh, but duplicated | Keep temporarily; later replace content with short pointer/onboarding checklist | Root `AGENTS.md` should own universal enforceable rules. |
| `docs/LEGAL_FACTORY_CONTEXT.md` | compact-main | Project passport, purpose, users, boundaries, terminology | Fresh | Keep as main project-context source | Best source for compact project context. |
| `docs/LEGAL_FACTORY_DECISIONS_AND_CHANGES.md` | compact-main | Current decisions summary and recent change map | Fresh | Keep as main decisions summary | Should link to the detailed append-only `DECISIONS_LOG.md`. |
| `docs/LEGAL_FACTORY_SPEC_AND_ROADMAP.md` | compact-main | Current product specification and phased roadmap | Fresh | Keep as main spec/roadmap source | Best current planning source. |
| `docs/LEGAL_FACTORY_STATUS_TESTS_RISKS.md` | compact-main | Current stage, verification baseline, open risks, next work | Fresh | Keep as main status source | Current snapshot is P3-C complete, P4 next. |
| `docs/LEGAL_RESPONSE_POLICY_V1.md` | policy | Rules for ordinary legal responses, missing sources, and risk topics | Fresh/normative | Keep separate; move to `policies/` | Must not be reduced to a status or architecture summary. |
| `docs/LEGAL_SOURCE_VERSION_POLICY.md` | policy | Lifecycle of active, future, outdated, and archived law revisions | Fresh/normative | Keep separate; move to `policies/` | Separate from retrieval workflow because it governs legal validity and lifecycle. |
| `docs/LEGAL_SOURCES.md` | source-overview | Source classes, metadata, retrieval rules, and Stage 6/7 operational history | Mixed; partially duplicated | Keep in `sources/`; later split/trim historical sections | Contains encoding corruption and repeated Stage 7 material, but still has useful source-domain guidance. |
| `docs/MVP_SCOPE.md` | roadmap-old | Early MVP boundary | Stale/overlapping | Archive after unique scope checks | Superseded by compact context and spec/roadmap. |
| `docs/PROJECT_OVERVIEW.md` | project-context-old | Short early project overview | Mostly valid but duplicated | Merge any unique wording, then archive or replace with pointer | Compact context is the better source of truth. |
| `docs/PROMPT_SYSTEM_V1.md` | policy | Lawyer role, prompt, mode, and output-contract policy | Fresh/normative | Keep separate; move to `policies/` | Prompt policy must remain versioned and independently reviewable. |
| `docs/QUALITY_GATE_V1.md` | policy / acceptance | Normative P6 acceptance matrix | Fresh/normative | Keep separate; move to `policies/` | Not a substitute for an engineering test-running guide. |
| `docs/RAG_WORKFLOW_V1.md` | policy | Targeted RAG request, retrieval, source-package, and fallback workflow | Fresh/normative | Keep separate; move to `policies/` | Main RAG workflow authority; links to source-version and response policies. |
| `docs/RISKS_AND_LIMITS.md` | status-old | Historical stage risks and limitations | Stale/mixed | Merge still-current risks into compact status, then archive | Includes superseded structured-answer, auth, RAG, and manual-verdict assumptions. |
| `docs/ROADMAP_TO_FINAL.md` | roadmap-old | Long detailed roadmap and stage history | Mixed; recently synchronized in parts | Preserve as deep roadmap/history until unique detail is migrated; then archive/history | Compact spec/roadmap should remain the planning entry point. |
| `docs/SECTION_GROUPS_AND_RAG_POLICY.md` | policy | Canonical section groups/codes and routing behavior | Fresh/normative | Keep separate; move to `policies/` | Internal codes and routing semantics are implementation contracts. |
| `docs/STAGE11_AUTH_ROLES.md` | stage-report / security-reference | Stage 11 auth, admin users, viewer read-only, and audit implementation record | Historical, latest section complete | Keep; move to `reports/stage11/` | Some earlier deferred notes are superseded by later sections in the same file. |
| `docs/STAGE7_3_UPLOAD_SMOKE_REPORT.md` | stage-report | Trial legal-source upload/retrieval/citation evidence | Historical | Keep; move to `reports/stage7/` | Preserve as acceptance evidence; local data warnings are not current status. |
| `docs/STAGE7_4_CHUNKING_FIX_REPORT.md` | stage-report | Chunking root cause, fix, tests, and smoke evidence | Historical | Keep; move to `reports/stage7/` | Technical evidence, not a current chunking policy. |
| `docs/STAGE7_5A_UPLOAD_REPORT.md` | stage-report | First Stage 7.5 upload batch evidence | Historical | Keep; move to `reports/stage7/` | Preserve exact source decisions and test results. |
| `docs/STAGE7_5B_UPLOAD_REPORT.md` | stage-report | Second Stage 7.5 upload batch evidence | Historical | Keep; move to `reports/stage7/` | Preserve exact source decisions and known extraction limitations. |
| `docs/STAGE7_5C_CONFORMITY_FIX_REPORT.md` | stage-report | ZRU-354 conformity-source status correction | Historical, legally significant | Keep; move to `reports/stage7/` | Important evidence for why the source is historical/outdated. |
| `docs/STAGE7_5C_UPLOAD_REPORT.md` | stage-report | Third batch upload and conformity correction evidence | Historical | Keep; move to `reports/stage7/` | Overlaps the focused fix report but has different batch scope; keep both. |
| `docs/STAGE7_5D_FIRST_BATCH_ACCEPTANCE.md` | stage-report | First-batch acceptance, failure, remediation, and repeat results | Historical | Keep; move to `reports/stage7/` | Contains useful pass/fail chronology that should not be rewritten as current status. |
| `docs/STAGE7_6_LEGAL_SOURCE_ADMIN_INSTRUCTION.md` | source-guide | Operational legal-source admin checklist | Current operational guide with implementation caveats | Keep; move to `sources/` or `guides/legal-sources/` | Do not merge into a stage report; it is an ongoing operational instruction. |
| `docs/STAGE7_LEGAL_SOURCE_REGISTRY.md` | source-registry | Approved source slots, metadata, lifecycle, and acceptance checks | Current registry with historical decisions | Keep; move to `sources/` | Registry data must remain separate from source policy. |
| `docs/STAGE8_COMPANY_PROFILE.md` | stage-report / feature-reference | CompanyProfile implementation and security limitations | Mixed historical | Keep; move to `reports/stage8/` | Early “not implemented” notes may be superseded by later stages; retain as stage evidence. |
| `docs/STAGE9_DOCUMENT_TEMPLATES.md` | stage-report / feature-reference | Template implementation, placeholders, profile binding, limitations | Mixed historical | Keep; move to `reports/stage9/` | Useful implementation reference, but not current product status. |
| `docs/STAGES.md` | roadmap-old | Early short stage outline | Stale/overlapping | Archive after link/unique-content check | Superseded by the compact roadmap and detailed history. |
| `docs/TESTING_STRATEGY.md` | testing-old | Broad engineering testing strategy and legacy stage expectations | Stale/mixed | Refresh as technical test guide or archive old version after preserving useful guidance | Legacy “all answers structured JSON” expectations conflict with P2 policy. |
| `docs/UI_CONCEPT.md` | design-reference | UI layout, interaction concepts, and design evolution | Mixed | Keep as design reference; move to `reference/ui/` | Contains both useful current concepts and superseded model/settings assumptions. |
| `docs/USER_ROLES.md` | domain-reference | Business user-role descriptions | Stale/misaligned | Refresh and move to `guides/` or `reference/` | Role names do not fully match current runtime RBAC vocabulary. |
| `docs/VERDICT_AND_DOCUMENT_POLICY_V1.md` | policy | Verdict eligibility and backend-controlled document gates | Fresh/normative | Keep separate; move to `policies/` | Main verdict/document policy authority. |

## 2. Duplication map

| Topic | Files overlapping | Best source of truth | Proposed action |
|---|---|---|---|
| Project context | `README.md`, `PROJECT_OVERVIEW.md`, `LEGAL_FACTORY_CONTEXT.md` | `LEGAL_FACTORY_CONTEXT.md` for knowledge; `README.md` for repository entry | Keep compact context; shorten README to orientation/run links; archive or point `PROJECT_OVERVIEW.md` after unique-content check. |
| Architecture | `ARCHITECTURE.md`, `LEGAL_FACTORY_ARCHITECTURE.md`, parts of `README.md`, stage reports | `LEGAL_FACTORY_ARCHITECTURE.md` | Migrate unique current code/API details; retain old architecture in history/archive; remove architecture chronology from README. |
| Roadmap / MVP / final target | `FINAL_TARGET.md`, `MVP_SCOPE.md`, `ROADMAP_TO_FINAL.md`, `STAGES.md`, `LEGAL_FACTORY_SPEC_AND_ROADMAP.md`, parts of `README.md` | `LEGAL_FACTORY_SPEC_AND_ROADMAP.md` | Keep compact roadmap current; preserve long roadmap as history until unique later-stage details are migrated; archive small superseded plans. |
| Current status | `CURRENT_STATE.md`, `LEGAL_FACTORY_STATUS_TESTS_RISKS.md`, `README.md`, endings of stage reports | `LEGAL_FACTORY_STATUS_TESTS_RISKS.md` | Make compact status the only active snapshot; replace other current-status blocks with links; archive `CURRENT_STATE.md` only after rules/links are updated. |
| Decisions / history | `DECISIONS_LOG.md`, `LEGAL_FACTORY_DECISIONS_AND_CHANGES.md`, stage reports | Compact decisions file for current summary; `DECISIONS_LOG.md` for chronology | Keep both with explicit roles and cross-links; move the detailed log to `history/`, not archive as obsolete. |
| Coder / agent rules | `AGENTS.md`, `CLAUDE.md`, `agent.md`, `LEGAL_FACTORY_CODER_RULES.md`; name overlap with `AI_AGENTS.md` | Root `AGENTS.md` for universal rules; root `CLAUDE.md` for Claude-only notes | Consolidate shared enforceable rules in `AGENTS.md`; reduce the other active rule files to deltas/pointers; archive `agent.md`; keep `AI_AGENTS.md` separate as product-agent behavior. |
| Prompt and lawyer behavior | `AI_AGENTS.md`, `PROMPT_SYSTEM_V1.md`, response/verdict policies, compact architecture | Versioned policy documents | Keep normative policies separate; make `AI_AGENTS.md` a readable product-role overview that links to them. |
| RAG policy | `RAG_WORKFLOW_V1.md`, `LEGAL_RESPONSE_POLICY_V1.md`, `LEGAL_SOURCE_VERSION_POLICY.md`, `SECTION_GROUPS_AND_RAG_POLICY.md`, `LEGAL_SOURCES.md` | Each versioned policy for its own domain | Co-locate under `policies/`, cross-link, and remove duplicated explanatory history from `LEGAL_SOURCES.md`; do not create one monolithic RAG file. |
| Verdict / document policy | `VERDICT_AND_DOCUMENT_POLICY_V1.md`, `PROMPT_SYSTEM_V1.md`, `LEGAL_RESPONSE_POLICY_V1.md`, legacy sections in architecture/README | `VERDICT_AND_DOCUMENT_POLICY_V1.md` | Keep the policy authoritative; compact docs summarize only; label legacy Stage 4/5 workflow as historical. |
| Quality / testing | `QUALITY_GATE_V1.md`, `TESTING_STRATEGY.md`, `LEGAL_FACTORY_STATUS_TESTS_RISKS.md`, stage report test results | `QUALITY_GATE_V1.md` for normative acceptance; compact status for latest baseline | Retain separate concerns: acceptance contract, test execution guidance, and latest results. Refresh or archive stale testing strategy. |
| Legal source registry | `LEGAL_SOURCES.md`, `STAGE7_LEGAL_SOURCE_REGISTRY.md`, `LEGAL_SOURCE_VERSION_POLICY.md`, admin instruction, Stage 7 reports | Registry for approved source data; version policy for lifecycle | Group registry/admin material under `sources/`; keep policy under `policies/`; reports remain evidence. |
| Stage reports | `STAGE7_*`, `STAGE8_*`, `STAGE9_*`, `STAGE11_*`, plus fragments copied into status/README | Individual report for stage evidence; compact status for current state | Move reports into stage subfolders, add an index, and stop copying their full chronology into current docs. |
| Risks and limits | `RISKS_AND_LIMITS.md`, compact status, stage reports, policy safeguards | `LEGAL_FACTORY_STATUS_TESTS_RISKS.md` for current risks; policies for mandatory safeguards | Migrate still-open risks only; archive historical risk snapshot without deleting it. |

## 3. Proposed clean folder structure

This is a proposal only. No path changes are part of this audit.

```text
/
  AGENTS.md
  CLAUDE.md
  README.md

docs/
  LEGAL_FACTORY_CONTEXT.md
  LEGAL_FACTORY_SPEC_AND_ROADMAP.md
  LEGAL_FACTORY_ARCHITECTURE.md
  LEGAL_FACTORY_DECISIONS_AND_CHANGES.md
  LEGAL_FACTORY_STATUS_TESTS_RISKS.md
  LEGAL_FACTORY_CODER_RULES.md          # temporary pointer/onboarding file
  LEGAL_FACTORY_DOCS_AUDIT.md

  policies/
    PROMPT_SYSTEM_V1.md
    RAG_WORKFLOW_V1.md
    LEGAL_RESPONSE_POLICY_V1.md
    VERDICT_AND_DOCUMENT_POLICY_V1.md
    QUALITY_GATE_V1.md
    SECTION_GROUPS_AND_RAG_POLICY.md
    LEGAL_SOURCE_VERSION_POLICY.md

  sources/
    LEGAL_SOURCES.md
    STAGE7_LEGAL_SOURCE_REGISTRY.md
    STAGE7_6_LEGAL_SOURCE_ADMIN_INSTRUCTION.md

  guides/
    DEV_SETUP.md
    USER_ROLES.md

  reference/
    agents/
      AI_AGENTS.md
    ui/
      UI_CONCEPT.md

  history/
    DECISIONS_LOG.md

  reports/
    stage7/
      STAGE7_3_UPLOAD_SMOKE_REPORT.md
      STAGE7_4_CHUNKING_FIX_REPORT.md
      STAGE7_5A_UPLOAD_REPORT.md
      STAGE7_5B_UPLOAD_REPORT.md
      STAGE7_5C_CONFORMITY_FIX_REPORT.md
      STAGE7_5C_UPLOAD_REPORT.md
      STAGE7_5D_FIRST_BATCH_ACCEPTANCE.md
    stage8/
      STAGE8_COMPANY_PROFILE.md
    stage9/
      STAGE9_DOCUMENT_TEMPLATES.md
    stage11/
      STAGE11_AUTH_ROLES.md

  archive/
    architecture/
      ARCHITECTURE.md
    planning/
      FINAL_TARGET.md
      MVP_SCOPE.md
      ROADMAP_TO_FINAL.md
      STAGES.md
    snapshots/
      CURRENT_STATE.md
      PROJECT_OVERVIEW.md
      RISKS_AND_LIMITS.md
      TESTING_STRATEGY.md               # only if not refreshed as a guide
    rules/
      agent.md                          # moved from repository root
```

Recommended supporting indexes after the move:

- `docs/README.md`: documentation map and source-of-truth table;
- `docs/policies/README.md`: policy scope, precedence, and cross-links;
- `docs/reports/README.md`: chronological report index without treating reports as current status;
- `docs/archive/README.md`: reason and date each document was superseded.

## 4. `AGENTS.md` / `CLAUDE.md` recommendation

### Existing state

- Root `AGENTS.md` already exists and is correctly framed as stable universal working rules.
- Root `CLAUDE.md` already exists. It should not be added again.
- Root `agent.md` is an older, separate file and is the strongest rules-file archive candidate.
- `docs/LEGAL_FACTORY_CODER_RULES.md` is a useful compact human-readable checklist, but maintaining it as a third full authority will create drift.
- `docs/AI_AGENTS.md` is about Lawyer 1/2/3 inside the product and must not be classified as coder instructions.

### Recommended authority model

1. **`AGENTS.md` — universal authority.** Keep workflow, safety boundaries, repository scope, auth/RBAC invariants, legal/RAG invariants, verification requirements, documentation placement rules, and no-push rule here.
2. **`CLAUDE.md` — Claude-specific deltas only.** Keep only behavior genuinely required by Claude Code: tool/command conventions, any Claude-specific context-loading notes, and a clear instruction to follow `AGENTS.md`. Shared legal, safety, and verification rules should not be duplicated in full.
3. **`LEGAL_FACTORY_CODER_RULES.md` — short onboarding pointer.** Retain it in the compact ChatGPT Project pack, but reduce it to a readable summary and links to `AGENTS.md`, architecture, status, and policies. State that `AGENTS.md` wins on conflict.
4. **`agent.md` — archive after validation.** Check repository references and compare any unique constraints against `AGENTS.md`; then move it to `docs/archive/rules/` with a superseded notice.

Current `AGENTS.md` references `docs/CURRENT_STATE.md` as an example status location. If compact status becomes the sole snapshot, update that rule in the same future migration commit that moves `CURRENT_STATE.md`; do not leave a broken or misleading reference.

## 5. Proposed merge and restructuring plan

Perform this as a separate approved implementation task, preferably in small commits:

1. **Freeze the authority map.** Approve the compact-main files and policy precedence. Create `docs/README.md` with current paths before moving anything.
2. **Consolidate coder rules.** Diff `AGENTS.md`, `CLAUDE.md`, `LEGAL_FACTORY_CODER_RULES.md`, and `agent.md`; move universal unique rules into `AGENTS.md`; reduce Claude and compact files to scoped deltas/pointers; archive `agent.md` only after `rg` confirms no live dependency.
3. **Create destination folders and indexes.** Add `policies/`, `sources/`, `guides/`, `reference/`, `history/`, `reports/`, and `archive/` README files explaining purpose and authority.
4. **Move normative documents first.** Use `git mv` for the seven policy files. Update all repository links immediately and verify no old paths remain.
5. **Move source operations and reports.** Move registry/admin source docs and stage reports into their proposed folders. Keep report contents unchanged except necessary link corrections.
6. **Reconcile architecture.** Compare `ARCHITECTURE.md` against compact architecture at section level, migrate only unique current code/entity/API details, then archive the old chronological document with a superseded header.
7. **Reconcile planning documents.** Migrate unique future requirements from `FINAL_TARGET.md`, `MVP_SCOPE.md`, `ROADMAP_TO_FINAL.md`, and `STAGES.md` into the compact spec/roadmap; archive originals with links to the new authority.
8. **Unify current status.** Move still-open risks and valid verification data into compact status; replace `CURRENT_STATE.md`, `PROJECT_OVERVIEW.md`, and `RISKS_AND_LIMITS.md` with archived snapshots or short pointers. Update `AGENTS.md` and README references in the same step.
9. **Separate testing concerns.** Remove superseded structured-JSON assumptions from `TESTING_STRATEGY.md`. Either refresh it as a practical engineering test guide or archive it; keep `QUALITY_GATE_V1.md` unchanged as normative acceptance.
10. **Refresh guides/references.** Align `DEV_SETUP.md` and `USER_ROLES.md` with current auth/RBAC; trim duplicated Stage 7 history and fix encoding corruption in `LEGAL_SOURCES.md`; label historical parts of UI and product-agent references.
11. **Validate the migration.** Run Markdown link checking if available, `rg` for every old path and stale stage claim, `git diff --check`, and `git status --short`. Confirm ChatGPT Project uploads include only the five compact knowledge files plus the compact coder pointer and any specifically needed policies.

## 6. What should not be merged

- **`LEGAL_SOURCE_VERSION_POLICY.md` and `RAG_WORKFLOW_V1.md`:** source legal validity/lifecycle and retrieval orchestration are different controls.
- **`STAGE7_LEGAL_SOURCE_REGISTRY.md` and source policy:** the registry is mutable approved-source data; policy defines rules that govern it.
- **`STAGE7_6_LEGAL_SOURCE_ADMIN_INSTRUCTION.md` and Stage 7 reports:** one is an ongoing operational guide, the others are historical evidence.
- **`QUALITY_GATE_V1.md` and `TESTING_STRATEGY.md`:** one is normative product acceptance, the other should explain engineering test execution and layers.
- **`LEGAL_FACTORY_STATUS_TESTS_RISKS.md` and stage reports:** current status must remain concise; reports preserve exact historical pass/fail evidence.
- **`LEGAL_FACTORY_DECISIONS_AND_CHANGES.md` and `DECISIONS_LOG.md`:** the compact file is a current summary; the log is append-only chronology.
- **`AI_AGENTS.md` and coder rules:** product lawyers and repository coding agents are unrelated despite the shared word “agents”.
- **Prompt, response, verdict, section-routing, and source-version policies:** co-locate and cross-link them, but keep independent versioned review boundaries.
- **`DEV_SETUP.md` and architecture:** setup commands change at a different rate from architectural contracts.
- **`UI_CONCEPT.md` and product specification:** design exploration and normative product scope should remain distinguishable.
- **Conformity fix report and the broader Stage 7.5-C upload report:** they overlap intentionally but record different scopes; preserve both.

## Audit conclusion

The main cleanup is not deletion; it is assigning one role to each document:

- compact documents answer “what the project is, how it works, what was decided, and what is next”;
- policies answer “what behavior is mandatory”;
- guides and registries answer “how operators work and what data is approved”;
- reports and logs answer “what happened and what evidence exists”;
- archive preserves superseded snapshots without presenting them as current truth.

The safest first implementation is rules consolidation plus documentation indexes, followed by path-only moves with link updates. Content merging should occur afterward in separate, reviewable commits.
