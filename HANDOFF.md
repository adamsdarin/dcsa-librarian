# HANDOFF — dcsa-librarian

Last updated: 2026-09-06T23:10:00Z by Claude

## Current State
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

**Not yet proven: whether a hosted runner can actually reach DCSA.** The
committed GitHub Actions workflow is unexercised. This container is blocked at
the proxy for every registry domain (dcsa.mil, ecfr.gov, federalregister.gov,
archives.gov, doha, esd.whs.mil all 403 at CONNECT), so it could not be tested
here. DCSA's CDN commonly rejects datacenter IPs. If the workflow 403s, the
declaration is unchanged — point a different runner at it.

## Next
1. **Run the workflow manually and see whether GitHub's runners can reach
   dcsa.mil.** Everything else about the hosted path depends on this one
   empirical answer. If blocked: use the browser fallback, or a runner whose
   egress is accepted. Do not respond by spoofing a user agent.
2. Verify `dcsa-fcl` resolves (its URL was never reachable from a container) and
   whether the VOI newsletters are visible in the NISP Tools page HTML or sit
   behind a tab that needs `browser-import`. The `voi-release-watch` job is
   pointed at `dcsa-nisp-tools` and is worthless if that tab is invisible.
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

Answered: a declared schedule with swappable runners, GitHub Actions first.
Still open is whether that runner's egress is accepted by DCSA.

Where does manifest triage happen now that the scan can run without the
library?

## Log
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
