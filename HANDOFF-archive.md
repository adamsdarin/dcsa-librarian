

# Preserved handoff before 2026-09-10 workspace improvements

# HANDOFF — dcsa-librarian

Last updated: 2026-09-07T22:30:00Z by Claude

## Current State

**The original question is answered.** DCSA published
`DCSA FCL_Orientation_Handbook_20260828.pdf` on 2026-08-28 — found live on
2026-09-07 under `/Portals/128/Documents/CTP/FC/`. The last publicly indexed
edition was 9 March 2021, and the March 2026 VOI had announced the update as
forthcoming. Nothing in this project detected it, which is what prompted all of
this work. Whether the library already holds it is still unchecked: that needs a
`discover --library` run.

Note it is a fifth naming convention for this document (`_10OCT18`,
`_05_MAR_20`, `_9_March_2021`, now `DCSA FCL_Orientation_Handbook_YYYYMMDD`),
and it is served from both `/CTP/FC/` and `/CTP/fc/` — genuinely distinct URLs
to the crawler, same inferred filename, so manifest matching by filename still
resolves both.

Integrity and discovery plane for the DCSA Library. Operates on a library passed
via `--library`; deliberately not part of the corpus.

`discover` detects revisions to documents already in the manifest (HEAD probe,
compared against the previous snapshot on ETag/Last-Modified/Content-Length/
sha256). A `changed` document becomes a review candidate.

**`--library` is now optional.** Without it every document is
`manifest_not_checked` and only source-side movement counts as a finding. This
is what lets the scan run somewhere with network access but no access to the
corpus — the change that makes hosted scheduling possible at all.

**Cadence is declared, runners are adapters.** `config/schedule.json` is the
single source of truth; `custodian.py schedule --render <runner>` emits cron,
GitHub Actions or schtasks from it. Two jobs: `monthly-scan` (1st, 09:00 ET) and
`voi-release-watch` (09:00/12:00/15:00 ET across days 28-31 and 1-3).
`scheduled-scan --job <id>` is the one entrypoint every runner calls. Exit codes
are the interface: 0 clean, 1 incomplete, 3 findings.

`state/snapshots/` and `state/watch/` are tracked in git deliberately. They are
the baseline; a runner that discards them detects nothing while still reporting
success.

**The scan runs locally, by design.** DCSA blocks GitHub's hosted runners —
user-confirmed, not a hypothesis — so the CI adapter and its workflow were
removed rather than left to fail monthly while looking like monitoring. There is
no `github-actions` renderer; asking for one raises. The scan is model-free by
construction: stdlib Python, no service, no agent in the loop.

Wrappers live in `adapters/windows/` (run-scan.cmd, install-tasks.cmd) and
`adapters/unix/run-scan.sh`. They pass `--library` because the corpus is local,
copy the report to the desktop on findings or on an incomplete scan, and
propagate the exit code so Task Scheduler's "Last Run Result" is meaningful.
Every run writes `state/reports/<job>-latest.txt` in plain English.

On the local path the DST caveat disappears: schtasks schedules in local time.
`utc_offset_hours` now only serves the cron adapter.

## Next
1. **Run the verification sequence on the target machine** (see
   `references/scheduling.md`): `selftest`, then `preflight --source
   dcsa-nisp-tools` and `--source dcsa-fcl`, then the two scratch-state
   `discover` runs plus the snapshot-perturbation check. Nothing in this project
   has ever completed a scan against a live source, so this is the first real
   proof any of it works. **Install and run it once on the target machine.** Edit `LIBRARY` and
   `ALERTS` in `adapters\windows\run-scan.cmd`, then run
   `adapters\windows\install-tasks.cmd`. Nothing in this project has ever
   executed a successful scan against a live source — every container is
   egress-blocked — so the first real run is also the first proof the crawler
   works at all.
2. Verify both FCL sources resolve, and whether the VOI newsletters are visible
   in the NISP Tools page HTML or sit behind a tab that needs `browser-import`.
   The `voi-release-watch` job is pointed at `dcsa-nisp-tools` and is worthless
   if that tab is invisible.
3. Confirm whether the revised FCL Orientation Handbook has actually posted. The
   March 2026 VOI announced it as forthcoming; only 2018/2020/2021 editions were
   findable.
4. Decide how manifest triage happens: the hosted scan runs without `--library`,
   so someone still has to reconcile findings against the corpus.
5. Still open: merge with `src\dcsa-library-custodian-v2`, keep both with
   distinct responsibilities, or retire one. Absorb the `OPERATIONS/` scripts
   still inside the corpus (waiting on the user).

## Open Questions
Merge with v2 or keep separate? This one has discovery and browser-import; v2
has enrichment and releases.

Answered: a declared schedule with swappable runners, executing locally.
Hosted CI is ruled out — DCSA blocks it.

Where does manifest triage happen now that the scan can run without the
library?

## Log
2026-09-07T22:30:00Z Claude — Found the revised handbook:
`DCSA FCL_Orientation_Handbook_20260828.pdf`, dated 2026-08-28, reachable from
the `dcsa-fcl` source. Both registered FCL URLs resolved, so the evidence-based
entry points were right.

That run exposed another defect the unit tests could not: the handbook was
reported four times from a two-page crawl. `_crawl_source` deduplicated links
within a page but not across the crawl, so a document linked from several pages
of a section was recorded once per page — inflating counts, probing it
repeatedly with HEAD, and listing it more than once for review. Fixed with a
crawl-wide seen set; regression test reproduces the two-page case.

The `/CTP/FC/` and `/CTP/fc/` variants are left as distinct URLs deliberately.
Path case is server-dependent and lowercasing it globally would risk false
manifest matches on case-sensitive sources; both variants share an inferred
filename, so filename matching resolves them anyway.

Pattern worth noting for whoever picks this up: three defects so far (robots
identity, VOI naming expectation, cross-page duplication) were all invisible to
a green test suite and all surfaced within minutes of running against the real
site. The tests encode my assumptions; only the live source falsifies them.

2026-09-07T22:05:00Z Claude — First successful live crawl. The robots fix
worked: `preflight --source dcsa-nisp-tools` returned Reachable: yes, 166
documents, 129 VOI issues. Two open questions closed at once — DCSA's CDN
accepts our declared user agent, and the VOI newsletters are ordinary HTML
links rather than a script-rendered tab.

The live data then falsified a design decision I had made on a guess. I had set
the release watch to expect "voi newsletter"; DCSA has renamed this publication
at least four times (`VOI_January_2016.pdf`, `Voice-of-Industry_June2023.pdf`,
`260831 VOI Newsletter.pdf`, `251031 VOI Bulletin.pdf`) and one issue is a
Bulletin, not a Newsletter. Widened `expect` to "voi", which matches all four
(`Voice` begins with it) and matched 129 of 166 documents on the page, all
genuine. A regression test pins every observed convention and asserts the
handbook is still excluded. Had October's issue been the awaited one, the old
expectation would have left the window open.

Note the failure mode was mild by construction — findings are reported
regardless of `expect`, which only governs window closing — but the expectation
was still wrong, and only real data showed it.

2026-09-07T15:10:00Z Claude — First execution outside a sandbox. User ran the
verification sequence on Windows: 54 tests OK, then both preflights failed with
`robots policy disallows`. Investigated rather than accepting it: DCSA's actual
robots.txt (retrieved via the user's browser) permits every path we scan and
bans only ia_archiver, while a direct Python fetch of robots.txt from the same
machine returned HTTP 403. So the refusal was self-inflicted —
`RobotFileParser.read()` asks as `Python-urllib`, and its 403 handling records
"disallow everything", which we surfaced as a policy refusal.

Rewrote the robots handling: fetch under the user agent we declare for every
other request (consistency, not evasion — we still identify honestly as
DCSA-Library-Custodian), treat 404/410 as no published policy, and report an
unreadable policy as "policy unknown ... not requested" rather than as a
disallow. The two failure modes call for opposite responses and collapsing them
hid which had occurred. DCSA's real robots.txt is now a test fixture proving our
scanned paths are permitted.

Open: whether the CDN also rejects our declared agent. If so the browser
fallback is the route; spoofing a browser is not.

2026-09-07T01:05:00Z Claude — Worked the three options the user had not
selected. (a) Replaced the guessed `/FCL/` root: search confirmed
`/Industrial-Security/Entity-Vetting-Facility-Clearances-FOCI/` exists and
follows the same path pattern as every other DCSA source, so it is registered as
`dcsa-entity-vetting-fcl`; `dcsa-fcl` now enters at
`/FCL/Maintaining-Personnel-Security-Clearances/`, a page search confirms
exists, and reaches its siblings via `crawl_path_prefix` at depth 2. Entering at
a confirmed page rather than an assumed root removes the most likely first-run
failure. (b) `verify_known` is now per-source and off for the two DOHA
collections: published decisions are immutable, so probing each one every scan
was cost with no possible finding, and those two sources carry `max_pages` 80
and 40. The global flag can only narrow a source further, never widen it.
(c) Jobs now declare an `action`, and a new `monthly-integrity` job runs
`doctor` at 09:30 on the 1st — nothing was watching the corpus itself, so parity
breaks and hash drift would have sat unnoticed. Library problems get their own
exit code (4) and their own desktop alert, because the remediation is nothing
like a source finding; a doctor job with no library reports that it could not
run rather than passing.

54 tests pass. Still nothing has run against a live source — see Next #1.

2026-09-07T00:30:00Z Claude — Found and fixed a defect in my own scheduling
work. `once_per_period` closed the release window on *any* finding, so an
unrelated document posted mid-window would have satisfied the period and the
awaited VOI would never have been polled for — precisely the miss the watch was
built to prevent. Jobs now declare `expect` (a case-insensitive substring
matched against the percent-decoded URL; the watch declares "voi newsletter"),
and reporting is separated from satisfying: every finding is still reported,
only a matching one closes the window. Regression test covers the sequence —
unrelated document on the 30th leaves the window open, awaited issue on the 31st
closes it. 48 tests pass.

2026-09-07T00:05:00Z Claude — User proposed deleting the August VOI from the
corpus and re-scanning as a test. Pushed back and it was accepted: that test
exercises manifest comparison, which was never broken, while the mechanism
actually at issue is change detection; and it is a destructive write to the
governed product to test a read-only tool, which breaks `doctor` parity and
loses an official document for nothing if the source turns out to be
script-rendered. The right object to perturb is the snapshot — disposable
comparison state — not the library.

Built the two commands that make diagnosis possible without touching anything.
`preflight --source <id>` fetches one source and prints every document link the
parser can see, writing no snapshot, report or baseline; a test asserts it
writes nothing and that it never probes documents. Its most valuable output is
the reachable-but-zero-documents case, which names the script-rendered-tab
problem explicitly — the failure that would leave `voi-release-watch` reporting
nothing forever while looking healthy. `selftest` runs the suite, so confirming
an install is one command rather than a unittest incantation.

Documented the safe verification sequence in scheduling.md and the
never-diagnose-by-deleting rule in discovery.md and SKILL.md.

44 tests pass. Still nothing has run against a live source — see Next #1.

2026-09-06T23:22:00Z Claude — User confirmed DCSA blocks GitHub Actions runners
and directed that the scan run locally, without a model. Removed the workflow
and the `github-actions` renderer outright rather than leaving them to fail
monthly: a scheduled job that always fails is worse than no schedule, because it
still reads as monitoring. A test now asserts that runner is unavailable.

Added local wrappers for Windows and Unix and a plain-text report
(`state/reports/<job>-latest.txt`), so a scheduled run is legible without an
LLM: the verdict is stated in words, and an unreachable source is called
INCOMPLETE rather than clean. The wrapper copies the report to the desktop on
findings or on failure and propagates the exit code, so Task Scheduler's "Last
Run Result" carries it.

Fixed a real defect in the schtasks renderer: Task Scheduler takes an explicit
list of day numbers and cannot parse ranges, so `28-31,1-3` was invalid and
would have failed at registration. It now expands to `28,29,30,31,1,2,3`.

Note the local path is strictly better on time: schtasks schedules in local
time and therefore follows DST, so the fixed-offset caveat only applies to the
cron adapter now.

38 tests pass. Still nothing has run against a live source — see Next #1.

2026-09-06T23:10:00Z Claude — Built the scheduling layer. User rejected a
Windows-Task-Scheduler-shaped answer and asked for automation "built into the
structure of the agent so it's agnostic". Told them plainly that no agent
framework schedules itself — something outside it must tick — and that the
achievable version is a declared cadence with rendered adapters. Built that:
`config/schedule.json` as the single declaration, `schedule --render` for
cron/GitHub Actions/schtasks, `scheduled-scan --job` as the one entrypoint,
exit codes as the runner interface.

Made `--library` optional, which is the load-bearing change: it decouples the
scan from the machine holding the corpus. Without a library the scan reports
`manifest_not_checked` rather than falsely flagging the whole corpus as missing.
Also split `baseline` from `new_to_snapshot` — a source's first-ever scan is not
a discovery, and conflating them would have dumped every document as a finding
on first run.

User asked for VOI polling "at 9:00, noon and 3:00 on the date of release".
Pushed back: the release date is not knowable in advance (observed 260130,
260227, 260331; March issue surfaced ~2 April). Implemented a polled window
(days 28-31 and 1-3) that closes on success via a period marker. The period
spans the month boundary so early-April polls do not re-arm on the March issue.
A scan with a failed source never closes a window — an incomplete run must not
suppress polls that might still succeed.

Snapshots and watch markers left `.gitignore`; they are the baseline and must
survive an ephemeral runner. Caught two of my own defects while wiring the CLI:
a leftover debug line, and `--command` colliding with the subparser's
`dest="command"`, which would have broken dispatch entirely.

30 tests pass. The hosted runner remains unproven — see Next #1.

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

## Trimmed from HANDOFF log 2026-09-24
2026-09-10 Codex — Implementing the five authorized workspace improvements and accepted-answer wiki. Preserved the entire prior handoff in the archive, including pre-existing edits. Validation is in progress; do not interpret implementation as a live library release.

## Recovered 2026-09-25: HANDOFF stashed locally on 2026-09-03, never committed
Preserved verbatim from a local stash (base f560a7a). Historical; superseded by later state.

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

### Its log
2026-09-02T22:14:04Z Codex — Renamed this intake framework and portable skill to DCSA Librarian, with DCSA Archivist as the explicit downstream handoff. Kept legacy code/CLI identifiers for compatibility and made the operating contract explicitly model-agnostic.
2026-09-01T23:46:14Z Codex — Audited the nine durable August 2026 VOI directions against Part 117, the four current ISLs, and governed-library holdings. Found a material same-cycle lifecycle change: ISOO Notice 2026-06 expressly replaces the black-label notices cited by the VOI. Captured and deterministically validated the official PDF in governed quarantine with provenance; no active-library or Guidance Watch register content was changed.
2026-09-01T17:50:00Z Claude — Published the August 2026 VOI (staged in quarantine since 2026-08-31) into the live library via `intake_voi.py --publish`, approved by Darin Adams. Then built/validated/evaluated/approved/published a matching v2 release candidate (`voi-20260901-august-intake-v1`, 14,432 docs, 8/8 eval) and copied the VOI into `fso-guidance-watch/corpus/voi/` for guidance analysis. Corrected the record: the intake script's publish path never actually checked `production_response_ready` — that gate lives in a separate v2 audit tool the script doesn't call.
2026-09-01T11:00:00Z Codex — Completed source-by-source CFR, active-ISL, first forms, executive-order, and NIST reviews. Recorded 36 exact decisions; new candidate v6 is structurally valid/publishable and reduces the remediation queue from 627 to 599. Found and recorded four material supersessions/withdrawals without altering the live corpus.
2026-08-31T23:14:00Z Codex — Applied the explicitly approved schema repair: zero blocking audit errors and exact 14,431-record manifest/relationship parity, with rollback at `OPERATIONS/QUARANTINE/SCHEMA_REPAIR_ROLLBACK/20260831T231236Z`. Scoped August publication was then safety-rejected because quality queues remain; no workaround attempted.
2026-08-31T23:08:00Z Codex — Built and tested an atomic August VOI intake, moved the heartbeat to FSO Guidance Watch, and paused downstream processing pending library publication. Publication was safety-rejected due to 338 pre-existing audit errors; the live corpus remains unchanged.
2026-08-31T22:45:00Z Codex — Verified the official August 2026 VOI, staged the browser-downloaded PDF with provenance and hash in quarantine after robots/CDN failures, and repaired the monthly heartbeat paths and mandatory notification outcomes. No live-library publication occurred.
2026-08-31T16:47:01Z Claude — Committed the first baseline — the repo had been initialised with zero commits.

## Trimmed from HANDOFF log 2026-09-25
2026-09-15 Codex — Added structured scan receipts, read-only freshness CLI and
supervisor integration; corrected stale scheduler approval state. Unknown prior
runs remain unknown. 70 Librarian tests pass. Period satisfaction and source
requests need further audit; no source acquisition or publication was run.
2026-09-14 Codex — Verified monthly maintenance coverage gap; recorded concrete
first-of-month schedule addition. No acquisition or library writes performed.
2026-09-11 Codex — Completed cross-system role/handoff implementation and process map. Tests: 65 Librarian, 52 Archivist; three cross-system acceptance cases and shared-policy checks pass. No live publication, acquisition, scheduling, or guidance product changes. Portable regenerator assessed as a proposed recipe-driven CLI, not implemented.
2026-09-11 Codex — Cross-system workflow audit in progress. User selected Librarian -> Archivist -> approved release -> comparison and Guidance Watch. Implementing staged source intake, published navigation graph, and durable release packets with completion receipts. Existing dirty files preserved. No live library changes; installed Windows task inspection found no DCSA/FSO/Custodian-named tasks.
2026-09-10 Codex — Completed authorized implementation. Offline discovery/quarantine is exercised by the cross-system acceptance suite. Shared-policy check passes. Pre-existing untracked files remain untouched; no live source scan or scheduler change was made. Changes remain uncommitted, including preserved prior edits.
2026-09-15 Codex — Closed filename-based period suppression; added retained,
hash-bound issue-period review and source-request handoff instructions. No live
issue confirmed, source downloaded or library publication performed.
2026-09-16 Codex — Fixed local-calendar period selection; boundary regression and
all 72 Librarian tests pass. No acquisition or publication run.
2026-09-18 Claude — Merged three cloud-session commits (Sept 7-13, pushed only to the
feature branch) into the local line: URL percent-encoding, pinned failing URLs, and
config/catalog_exclusions.json scope decisions (excluded documents are still crawled
and reported, never re-offered or downloaded). Both sides had built intake packages;
kept Codex's writer and adopted the cloud builder's stable url+hash submission_id and
required-field check. That session's FCL intake (12 in-scope documents) still needs a
library doctor and a handbook-edition check before acquisition.
2026-09-18 Claude — Added byte-verified provenance to discovery. A name match alone is
never provenance; bytes_differ rows go to the Evidence Reviewer. This is how the
Rebuilder's 749 retained-bytes-only records can gain official URLs over time.
