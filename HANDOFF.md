# HANDOFF — dcsa-librarian

Last updated: 2026-09-15 by Codex

## Current State
Expected-publication polling now requires confirm-period evidence after actual
source review; filename matches and legacy markers cannot end the VOI window.
Shared public-source requests route through ../EVIDENCE-REQUESTS.md. 72 tests pass; issue periods now use the configured local date at UTC boundaries.
Structured scheduled-run records and scan-status freshness checks are implemented.
Supervisor now distinguishes source freshness from library readiness, including
registry/source coverage, library identity and timezone-aware due times. Live
status is unknown for all three jobs because earlier runs lack structured receipts;
no source success was backfilled. Windows tzdata installed under ignored .runtime.
Both month-end VOI and first-of-month maintenance were explicitly approved and
enabled September 14; older approval-pending notes were stale. See workspace
AUTOMATION-UPDATE-PROPOSAL.md. No live scan was run in this checkpoint.
Discovery/integrity plane. Scheduled wrappers now download quarantined sources and accept the rendered --job syntax. New/changed downloads emit Archivist intake packages; no-library discovery can acquire bootstrap inputs. GET redirect provenance is captured and allowlist checked. 65 offline tests pass. No live acquisition or scheduler installation was performed; no DCSA/FSO/Custodian-named Windows tasks were found on inspection.

Live Git state: run `python ../workspace_health.py status`; prior details are in `HANDOFF-archive.md`.

## Next
1. Deploy and verify the local scheduler and agent-host cycle; config alone is not evidence of recurring operation.
2. Use ../dcsa-archivist/agents/conductor.md for package review and gated intake; do not use historical intake_voi.py as the general publication path.
3. Preserve existing untracked scripts/snapshots; see ../PROCESS-MAP.md for scope and bootstrap recommendations.

## Open Questions
No new decision needed for the authorized implementation. Prior source-acquisition
and migration questions remain scoped separately as noted above.

## Log
2026-09-16 Codex — Fixed local-calendar period selection; boundary regression and
all 72 Librarian tests pass. No acquisition or publication run.
2026-09-15 Codex — Closed filename-based period suppression; added retained,
hash-bound issue-period review and source-request handoff instructions. No live
issue confirmed, source downloaded or library publication performed.
2026-09-15 Codex — Added structured scan receipts, read-only freshness CLI and
supervisor integration; corrected stale scheduler approval state. Unknown prior
runs remain unknown. 70 Librarian tests pass. Period satisfaction and source
requests need further audit; no source acquisition or publication was run.
2026-09-14 Codex — Verified monthly maintenance coverage gap; recorded concrete
first-of-month schedule addition. No acquisition or library writes performed.
2026-09-11 Codex — Completed cross-system role/handoff implementation and process map. Tests: 65 Librarian, 52 Archivist; three cross-system acceptance cases and shared-policy checks pass. No live publication, acquisition, scheduling, or guidance product changes. Portable regenerator assessed as a proposed recipe-driven CLI, not implemented.
2026-09-11 Codex — Cross-system workflow audit in progress. User selected Librarian -> Archivist -> approved release -> comparison and Guidance Watch. Implementing staged source intake, published navigation graph, and durable release packets with completion receipts. Existing dirty files preserved. No live library changes; installed Windows task inspection found no DCSA/FSO/Custodian-named tasks.
2026-09-10 Codex — Completed authorized implementation. Offline discovery/quarantine is exercised by the cross-system acceptance suite. Shared-policy check passes. Pre-existing untracked files remain untouched; no live source scan or scheduler change was made. Changes remain uncommitted, including preserved prior edits.
2026-09-10 Codex — Implementing the five authorized workspace improvements and accepted-answer wiki. Preserved the entire prior handoff in the archive, including pre-existing edits. Validation is in progress; do not interpret implementation as a live library release.
