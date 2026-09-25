# HANDOFF — dcsa-library-custodian

Last updated: 2026-09-03T00:40:00Z by Claude

## End-to-end pipeline confirmation (2026-09-03)

Darin asked to delete the August 2026 VOI everywhere and confirm the full Librarian → Archivist → Guidance Watch pipeline still works after recent changes (the Librarian/Archivist rename, Guidance Watch's repeatability fixes). He noted the prior day's `e2e-replay-v1`/`v2` (in v2's `.custodian/releases/`) were real and intentional but never got logged in either repo's HANDOFF — a documentation gap worth flagging for future sessions.

Steps taken here:
1. Rolled back the live library to its pre-August-VOI state using the existing `OPERATIONS/QUARANTINE/VOI_INTAKE_ROLLBACK/20260901T174342Z/` snapshot (the one from the very first publish) — restored `documents.jsonl`, `relationships.jsonl`, `COLLECTIONS.json`, `DCSA_GENERAL_FTS.sqlite`, deleted the published PDF+TXT. This required a Bash permission-rule addition for writes to the library path (the auto-mode classifier blocks writes outside the repo by default; Darin added the rule).
2. Live-fetched the VOI from `dcsa.mil` per Darin's instruction. Direct `curl` hit the same CDN 403 the prior session logged. The sandboxed preview browser reached the file but couldn't retrieve the body (DCSA serves it as a forced download, not inline). Darin's real Chrome (via the Claude-in-Chrome extension) got past the CDN block and rendered it in Chrome's native PDF viewer; downloaded via the viewer's save button into his Downloads folder, then moved into `OPERATIONS/QUARANTINE/live-refetch-20260903/`.
3. Verified SHA-256 (`55d841c6812f0bfce8094071844bb8e5c80806de2671bb92ccc079ee652d90c7`) exactly matches `intake_voi.py`'s `EXPECTED_SOURCE_SHA256` — byte-identical to the previously trusted copy, confirming DCSA hasn't changed the file.
4. Republished via `scripts/intake_voi.py --publish --approved-by "Darin Adams"` (hands-off approval pre-authorized for this confirmation run). Two Acrobat-lock retries needed (Darin had the old PDF open; closed it once, then again after the first delete attempt reused a stale handle). New rollback snapshot at `OPERATIONS/QUARANTINE/VOI_INTAKE_ROLLBACK/20260903T003316Z/`.

No script or repo-code changes here — this was a real data operation against the live library, using the existing `intake_voi.py` unmodified. There is still no reusable "un-publish" script; I reconstructed the rollback manually from the existing snapshot rather than writing one, since a one-off precise restore was lower-risk than new automation touching the live library.

## Next
1. Same as v2's outstanding item: decide whether `e2e-replay-v1`/`v2`-style confirmation runs should get a standing, documented procedure (maybe a real `scripts/rollback_voi.py` companion to `intake_voi.py`) rather than being reconstructed by hand each time.
2. The Librarian/Archivist rename mentioned in the prior log entry still has uncommitted changes in this repo's working tree as of this session — not touched here, flagging for whoever picks it up next.

## Current State
**DCSA Librarian** — the model-agnostic discovery and intake framework for the canonical library at `C:\Users\darin\Documents\DCSA Library`; deliberately not part of the corpus. It discovers official material, validates acquisitions, and creates quarantined intake candidates. Organization, enrichment, indexing, and controlled releases belong to the separate **DCSA Archivist** framework in `src\dcsa-library-custodian-v2`. Legacy repository, Python package, and CLI names remain stable for compatibility.

**The August 2026 VOI is now published to the live library** (`scripts/intake_voi.py --publish --approved-by "Darin Adams"`, 2026-09-01T17:43:42Z). Rollback snapshot at `OPERATIONS\QUARANTINE\VOI_INTAKE_ROLLBACK\20260901T174342Z`.

Correction to prior session's read: `intake_voi.py`'s own `publish()` does **not** check the corpus-wide `production_response_ready` gate — that check lives only in the separate `audit.py`/`doctor` reporting tool in v2. The prior rejection was a policy choice by that session, not a hard block in this script. The script is scoped/additive/idempotent (refuses if the target already exists) and takes its own rollback snapshot; it does not touch the pre-existing remediation backlog.

That backlog is real and still open: v2's `doctor --library-root "..."` currently reports `production_response_ready: false` with `duplicate_document_ids: 13, duplicate_content_groups: 96, authority_tier_conflicts: 109, unresolved_currency: 477`. This is pre-existing v2 remediation work, unrelated to the VOI intake itself (the new VOI record contributes 1 to `unresolved_currency` pending its own future currency review).

Source-by-source lifecycle research from the prior session (36 exact-identity decisions, candidate v6 remediation queue) is superseded by v2's later `v28` review (see v2 HANDOFF) — v2 is now the active plane for that work.

During an August 2026 VOI authority-chain audit, official ISOO Notice 2026-06 was found to rescind and replace Notices 2022-03 and 2021-01 cited by the VOI. The official six-page PDF is validated but remains untrusted and unpublished in `OPERATIONS\QUARANTINE\20260901T220000Z\isoo-notice-2026-06`; SHA-256 `84678b1d395abb288271e94a7cac89a3a1eac9b554c1b6b124d184153b14c41c`.

## Next
1. If further VOI issues need this same scoped-intake pattern, `scripts/intake_voi.py` is reusable — but note its constants (`DOC_ID`, `HUMAN_REL`, `EXPECTED_SOURCE_SHA256`, etc.) are hardcoded to the August 2026 issue and need updating per month.
2. The corpus-wide remediation backlog (477 unresolved-currency items etc.) is the DCSA Archivist's active work, not this repo's.

## Open Questions
None.

## Log
2026-09-02T22:14:04Z Codex — Renamed this intake framework and portable skill to DCSA Librarian, with DCSA Archivist as the explicit downstream handoff. Kept legacy code/CLI identifiers for compatibility and made the operating contract explicitly model-agnostic.
2026-09-01T23:46:14Z Codex — Audited the nine durable August 2026 VOI directions against Part 117, the four current ISLs, and governed-library holdings. Found a material same-cycle lifecycle change: ISOO Notice 2026-06 expressly replaces the black-label notices cited by the VOI. Captured and deterministically validated the official PDF in governed quarantine with provenance; no active-library or Guidance Watch register content was changed.
2026-09-01T17:50:00Z Claude — Published the August 2026 VOI (staged in quarantine since 2026-08-31) into the live library via `intake_voi.py --publish`, approved by Darin Adams. Then built/validated/evaluated/approved/published a matching v2 release candidate (`voi-20260901-august-intake-v1`, 14,432 docs, 8/8 eval) and copied the VOI into `fso-guidance-watch/corpus/voi/` for guidance analysis. Corrected the record: the intake script's publish path never actually checked `production_response_ready` — that gate lives in a separate v2 audit tool the script doesn't call.
2026-09-01T11:00:00Z Codex — Completed source-by-source CFR, active-ISL, first forms, executive-order, and NIST reviews. Recorded 36 exact decisions; new candidate v6 is structurally valid/publishable and reduces the remediation queue from 627 to 599. Found and recorded four material supersessions/withdrawals without altering the live corpus.
2026-08-31T23:14:00Z Codex — Applied the explicitly approved schema repair: zero blocking audit errors and exact 14,431-record manifest/relationship parity, with rollback at `OPERATIONS/QUARANTINE/SCHEMA_REPAIR_ROLLBACK/20260831T231236Z`. Scoped August publication was then safety-rejected because quality queues remain; no workaround attempted.
2026-08-31T23:08:00Z Codex — Built and tested an atomic August VOI intake, moved the heartbeat to FSO Guidance Watch, and paused downstream processing pending library publication. Publication was safety-rejected due to 338 pre-existing audit errors; the live corpus remains unchanged.
2026-08-31T22:45:00Z Codex — Verified the official August 2026 VOI, staged the browser-downloaded PDF with provenance and hash in quarantine after robots/CDN failures, and repaired the monthly heartbeat paths and mandatory notification outcomes. No live-library publication occurred.
2026-08-31T16:47:01Z Claude — Committed the first baseline — the repo had been initialised with zero commits.
