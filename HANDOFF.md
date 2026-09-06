# HANDOFF — dcsa-librarian

Last updated: 2026-09-06T22:25:00Z by Claude

## Current State
Integrity and discovery plane for the DCSA Library. Operates on a library passed
via `--library`; deliberately not part of the corpus.

`discover` now detects **revisions to documents already in the manifest**, which
it previously could not. Status was decided by URL-or-filename match alone, so a
document republished at the same URL came back `known` and never reached the
candidate list. Documents are now probed with HEAD and compared against the
previous snapshot on `ETag`/`Last-Modified`/`Content-Length`/`sha256`; a
`changed` document becomes a review candidate. Snapshots are schema 2
(`documents` map); schema 1 snapshots still load and re-baseline as `unverified`.

Nothing in this project was ever watching on a schedule. `discover` is a manual
command; there is no cron, Routine, or hook that runs it. **That, not the code,
is why a DCSA change can pass unnoticed.** Unresolved.

Registry coverage was the larger gap for the FCL Orientation Handbook
specifically: no FCL source was registered at all, and DCSA date-stamps that
filename, so a revision arrives as a new URL rather than an in-place edit.
Added `dcsa-fcl`. Its URL could not be verified from the session container —
dcsa.mil is blocked by the egress proxy — so the first real scan must confirm
that source does not report `status: error`.

## Next
1. **Decide how scanning gets triggered.** Detection code without a scheduler
   changes nothing. Options: a scheduled Routine, a local cron, or an explicit
   accepted-manual-cadence decision.
2. Verify `dcsa-fcl` resolves, and whether VOI newsletters are reachable from
   the NISP Tools page HTML or need the browser-import fallback (they sit behind
   an in-page tab).
3. Confirm whether the revised FCL Orientation Handbook has actually been posted.
   The March 2026 VOI announced it as forthcoming; only 2018/2020/2021 editions
   were findable.
4. Still open from before: merge with `src\dcsa-library-custodian-v2`, keep both
   with distinct responsibilities, or retire one. Absorb the `OPERATIONS/`
   scripts still inside the corpus (waiting on the user).

## Open Questions
Merge with v2 or keep separate? This one has discovery and browser-import; v2
has enrichment and releases.

What is the intended trigger for `discover`? Everything else is moot until that
is answered.

## Log
2026-08-31T16:47:01Z Claude — Committed the first baseline — the repo had been
initialised with zero commits.

2026-09-06T22:25:00Z Claude — User asked why a DCSA documentation change was not
detected. Nothing had changed in the repo since the previous watermark (three
commits total, all baseline; no Codex session files present). Diagnosis: three
independent gaps, ranked. (1) No scheduler — `discover` only runs when a human
runs it. (2) No FCL source in the registry, so the handbook's section was never
crawled; DCSA date-stamps the filename, so revisions surface as new URLs, and
the VOI newsletter — DCSA's own change-announcement channel — sits behind a tab
the plain HTML parser likely cannot see. (3) No content-change detection.

Implemented (3) and part of (2): HEAD-based revision probing, evidence-based
change signals, schema 2 snapshots with backward compatibility, and the
`dcsa-fcl` source. Design choice: a document is called `changed` only on
positive evidence, and absent evidence reports `unverified` rather than
`unchanged` — a governance tool must not let a gap read as a clean scan.
`verify_known` defaults on, since a detector nobody opts into repeats the
original failure; cost is one HEAD per known document per scan, escapable with
`--no-verify-known`. Also fixed a latent bug: second-granular run ids with
`mkdir(exist_ok=False)` crashed two scans in the same second.

(1) is deliberately left undone — it is a decision about cadence and hosting,
not a code change, and it is the gap that actually caused the miss.
