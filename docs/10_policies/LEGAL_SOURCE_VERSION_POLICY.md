# Legal Source Version Policy

Date: 2026-06-17

## Purpose

This policy defines how Legal Factory AI treats active, future, outdated, and archived legal source revisions.

It is a Stage 7.5-A2 policy update only. It does not authorize crawlers, historical downloads, mass imports, embeddings, Telegram, VPS deployment, or Stage 7.5-B source loading.

## Source Status Rules

One `LegalSource` record represents one concrete revision or ONDATE state of one official source.

- `active`: current official revision that passed metadata, chunk, retrieval, and citation smoke checks. Ordinary legal answers may use it.
- `draft`: not trusted for ordinary legal answers yet. Future versions stay `draft` before their effective date; the current model has no separate `future` status.
- `outdated`: no longer current. It remains visible for metadata/history but must not enter ordinary RAG.
- `archived`: retained for audit/history only. It must not enter ordinary RAG.

Normal legal retrieval must use only:

```text
status=active AND official_status=official
```

## Current Answers

For ordinary current-law answers:

- use only active current official sources;
- inject them only as `<TRUSTED_LEGAL_SOURCE ...>`;
- confirm `source_type=law` only when the quote and metadata match a retrieved active chunk;
- never mix archived, outdated, draft, or future source text into the current legal conclusion.

If the only relevant source is draft, future, outdated, or archived, the answer must not present it as current law.

## Future Versions

Future versions are allowed only for preparation and planning.

If a relevant future revision exists, it should be shown separately from the current-law answer with a clear date warning:

```text
Future-change context only. Not active law before the effective date.
```

Future source context, if implemented later, must use a separate channel such as:

```text
<FUTURE_LEGAL_SOURCE ...>
```

It must not be merged into `<TRUSTED_LEGAL_SOURCE ...>` and must not confirm ordinary current-law citations.

Current implementation note: the ordinary legal retriever is active-only. Separate future-source retrieval is postponed to a later approved Stage 7.6/8 style task.

## Historical Versions

Old source versions should remain metadata-only locally unless a separate cold-archive task is approved.

Codex must not automatically download or import all historical LEX.UZ versions. Historical source work requires a separate explicit command, a narrow scope, and a clear reason.

If an approved source is found expired during import, keep it as outdated/historical metadata and do not activate it. Identify the current related source separately and ask user approval before adding substitutes. Example: Stage 7 source No. 15, ZRU-354 `Law of Uzbekistan on Conformity Assessment`, was found no longer in force from `2023-08-29`; it is covered as historical/reference only and excluded from ordinary RAG.

## Update Workflow

When a newer official revision appears:

1. Keep the existing active source unchanged until the new revision is verified.
2. Create the new revision as `draft`.
3. Fill exact revision/ONDATE, effective date if available, source URL, and check dates.
4. Inspect chunks.
5. Run retrieval probes.
6. Confirm correct citations and reject wrong citations.
7. Move the old source to `outdated` or `archived`.
8. Move the new source to `active` only after all checks pass and only on/after its effective date.

## Forbidden Automation

Codex must not:

- crawl LEX.UZ;
- mass-download legal texts;
- import all historical revisions;
- make a future revision active before its effective date;
- commit raw legal texts, local DB files, or storage artifacts;
- use embeddings/pgvector work as part of this policy task.
