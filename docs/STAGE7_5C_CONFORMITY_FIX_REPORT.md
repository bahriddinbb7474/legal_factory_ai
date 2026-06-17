# Stage 7.5-C Conformity Source Fix Report

Date: 2026-06-17

## Scope

Corrective step only for Stage 7.5-C source No. 15.

- No backend/frontend code changes.
- No crawler.
- No mass import.
- No historical LEX.UZ auto-import.
- No future versions imported.
- No raw legal texts committed.
- No DB/storage committed.
- No Stage 7.5-D / Stage 7.6 work.

## Exact Source Found

Exact approved source No. 15 was found on LEX.UZ:

```text
Law of Uzbekistan on Conformity Assessment
ZRU-354
Adopted: 2013-10-04
LEX.UZ: https://lex.uz/ru/docs/2248099
```

LEX.UZ marks this act as no longer in force from `2023-08-29`.

## Local Smoke Result

| Field | Result |
| --- | --- |
| Local source id | 16 |
| Initial status | draft |
| Final status | outdated |
| Revision / status date | 2023-08-29 (expired) |
| Chunks | 18 |
| Max chunk size | 3498 |
| Warnings | `lexuz_lost_force_2023_08_29` |
| Retrieval probes | passed: conformity assessment, certification, declaration of conformity, confirmation of conformity |
| Correct quote | confirmed |
| Wrong quote | unconfirmed |

ZRU-354 was not made active because it is not current law on 2026-06-17.

## ZRU-820 Role

ZRU-820, `Law of Uzbekistan on Accreditation of Conformity Assessment Bodies`, remains a related additional source/candidate in the local smoke DB.

It is not the exact first-batch source No. 15 and is not a replacement for ZRU-354.

## First-Batch Coverage After Fix

| Metric | Count | Note |
| --- | ---: | --- |
| Exact current active first-batch sources | 13 | Exact sources that are current and active. |
| Exact outdated first-batch sources | 1 | ZRU-354, exact source No. 15, no longer in force from 2023-08-29. |
| Draft/future first-batch sources | 1 | PP-4348 / PQ-4348 `ONDATE=2026-07-01`. |
| Related additional active/candidate source | 1 | ZRU-820, not a replacement for ZRU-354. |
| Total approved first-batch sources covered | 15 | Coverage now includes exact ZRU-354, but it is not current active law. |

## Final Registry Decision

Stage 7.5-C2 updates the registry so source No. 15 is no longer described as a normal activation candidate.

For ZRU-354:

- `stage7_status`: `covered_as_outdated_historical`.
- `recommended_runtime_status`: `outdated`.
- `ordinary_rag`: excluded.
- `role`: historical/reference only.

For current-law conformity-related answers:

- ZRU-819, `Law of Uzbekistan on Technical Regulation`, is the current primary first-batch source for technical regulation and related conformity-framework checks after the ZRU-354 expiry.
- ZRU-819 should not be described as fully replacing every ZRU-354 norm unless a later text check confirms that.
- ZRU-820, `Law of Uzbekistan on Accreditation of Conformity Assessment Bodies`, is a related additional candidate/current related source for accreditation of conformity assessment bodies. It is not a replacement for source No. 15 and should be treated as a second-batch/certification-expansion candidate unless separately approved.

## Policy Note

Ordinary legal answers must continue to use only active current official sources. ZRU-354 is available locally for exact coverage and historical reference, but it must not participate in ordinary `<TRUSTED_LEGAL_SOURCE>` as current law while its LEX.UZ status is no longer in force.
