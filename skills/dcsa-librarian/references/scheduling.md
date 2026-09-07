# Scheduling

## What is and is not agnostic

No agent framework schedules itself. Something outside it has to tick: a cron
daemon, a CI scheduler, a hosted routine, a desktop task service. What is
portable is the *declaration*. `config/schedule.json` is the single source of
truth for cadence; runners are adapters rendered from it. Swapping the ticker
never means rewriting the schedule, and no runner holds knowledge the project
does not.

Never hand-edit a rendered adapter. Change the declaration and re-render:

```
python custodian.py schedule --render schtasks
python custodian.py schedule --render cron
```

## The scan runs locally, on an ordinary desktop

**DCSA blocks hosted CI runners.** A GitHub Actions workflow fails every time
while still looking like monitoring, which is worse than no schedule at all, so
there is deliberately no CI adapter. The scan must originate from a normal
desktop connection.

It is also model-free by construction: stdlib Python, no network service, no
agent in the loop. A scheduled run produces a plain-text report a person reads
directly. Nothing downstream needs an LLM to find out what happened.

### Prove it works before trusting the schedule

Nothing here is worth scheduling until a scan has succeeded once by hand. Run
these in order; none of them touches the library.

```
python custodian.py selftest
python custodian.py preflight --source dcsa-nisp-tools
python custodian.py preflight --source dcsa-fcl
```

`selftest` confirms the install. The two `preflight` runs confirm the machine
can reach DCSA and that the parser can see documents on those pages — including
whether the Voice of Industry newsletters are visible or hidden behind a
script-rendered tab.

Then prove change detection itself, using scratch state so the real baseline is
untouched:

```
python custodian.py discover --source dcsa-nisp-tools --state-dir %TEMP%\dcsa-probe --quarantine-dir %TEMP%\dcsa-probe\q
python custodian.py discover --source dcsa-nisp-tools --state-dir %TEMP%\dcsa-probe --quarantine-dir %TEMP%\dcsa-probe\q
```

The first run establishes a baseline; the second should report everything
`unchanged` with no candidates. Spurious `changed` results here mean the CDN
varies its validators, and the noise has to be understood before the schedule is
believable. Now edit `%TEMP%\dcsa-probe\snapshots\dcsa-nisp-tools.json`, set
any document's `etag` to a bogus value, and run the command a third time: that
document must come back under `changed_since_previous_scan`. Delete the scratch
directory afterwards.

Perturb the snapshot, never the corpus. The snapshot exists to be a comparison
baseline and is disposable; the library is the product.

### Setting it up on Windows

1. Edit `adapters/windows/run-scan.cmd` — set `LIBRARY` to the DCSA Library
   path and `ALERTS` to wherever reports should land.
2. Run `adapters/windows/install-tasks.cmd`. It renders the tasks from the
   declaration, shows them, and asks before creating anything.
3. Confirm them in Task Scheduler. "Last Run Result" carries the exit code.

### Setting it up on Linux or macOS

```
python custodian.py schedule --render cron --command "$PWD/adapters/unix/run-scan.sh"
```

Paste the output into `crontab -e`. Set `DCSA_LIBRARY` and `DCSA_ALERTS` in the
environment if the defaults do not match.

### How you find out something changed

The wrapper drops the report on the desktop when there is something to see:
`DCSA-SCAN-FINDINGS.txt` on findings, `DCSA-SCAN-INCOMPLETE.txt` when a source
could not be reached. Every run also writes
`state/reports/<job>-latest.txt` and appends to `state/reports/scan-log.txt`.

An incomplete scan gets its own alert on purpose. The failure mode that matters
is a scan that quietly reaches nothing and reads as clean.

## Running a declared job

Every runner invokes the same entrypoint with the same job id, so behaviour
does not vary with whatever started it:

```
python custodian.py scheduled-scan --job monthly-scan
```

Exit codes are the runner's interface:

| Code | Meaning |
| --- | --- |
| 0 | Ran clean, nothing to review — or the period was already satisfied |
| 1 | Incomplete. A source failed, or an audit could not run. Never read as "no changes" |
| 3 | Findings to triage |
| 4 | The library itself has integrity problems |

## The declared jobs

Each job declares an `action`: `discover` scans sources, `doctor` audits the
library.

- **`monthly-scan`** (`discover`) — every enabled source, the 1st at 09:00
  America/New_York.
- **`monthly-integrity`** (`doctor`) — the library itself, the 1st at 09:30.
  The scans watch sources; without this nothing watches the corpus, and parity
  breaks, hash drift and index rot would sit unnoticed between manual runs. It
  runs half an hour after the sweep so the two do not contend for the same
  minute. A `doctor` job with no `--library` reports that it could not run — an
  audit that examined nothing is never a clean result.
- **`voi-release-watch`** (`discover`) — the VOI home at 09:00, 12:00 and 15:00
  across the month-end window (days 28-31 and 1-3).

The window exists because the release date is not knowable in advance. Observed
issues are dated `260130`, `260227`, `260331` — DCSA targets month-end and
slips; the March 2026 issue surfaced around 2 April. Polling a window and
stopping on success is the only schedule that actually catches it.

`once_per_period` closes the window, but only on the finding the job is waiting
for. `expect` declares that: a case-insensitive substring matched against the
percent-decoded URL, so `"voi newsletter"` matches
`.../260331%20VOI%20Newsletter.pdf`. When a matching document appears the job
writes `state/watch/<job>/<period>.json` and the remaining polls in that period
no-op.

Reporting and satisfying are separate. Every finding is reported; only a
matching one closes the window. Without that split, an unrelated job aid posted
on the 29th would end the March polling before the issue was ever published —
the exact miss the watch exists to prevent. A job with no `expect` is satisfied
by any finding, which suits a job merely looking for movement and not one
waiting on a specific publication.
A period spans the boundary — 28-31 March and 1-3 April both belong to
`2026-03` — so the early-April polls do not re-arm and re-report the issue the
March polls already found. **A scan with a failed source never closes a
window**: an incomplete run must not suppress the polls that might still
succeed.

## Time zones

`schtasks` schedules in the machine's local time, so the declared times are
emitted unconverted and **follow DST correctly**. On the local path the offset
question does not arise.

`utc_offset_hours` (EST, -5) exists for the cron adapter, whose expressions are
UTC. There, during EDT each job fires an hour later in local terms; three polls
a day absorb that and the monthly sweep does not care. A conversion that would
cross midnight and silently shift a job's day-of-month is refused rather than
emitted wrong.

schtasks takes an explicit list of day numbers and does not understand ranges,
so the renderer expands `28-31,1-3` to `28,29,30,31,1,2,3`. Days that do not
exist in a given month simply do not fire — which is the other reason the
window covers the first days of the following month.

## Running without the library

`--library` is optional. Given one, findings are classified against the
manifest (`known` / `missing_from_manifest`). Without one, every document is
`manifest_not_checked` and only source-side movement counts as a finding —
which is what lets the scan run somewhere that has network access but no access
to the corpus. Manifest triage then happens where the library lives.

## State is the baseline, so state must survive

`state/snapshots/` and `state/watch/` are tracked in git on purpose. Change
detection compares against the previous scan; a runner that discards them
detects nothing, ever, while still reporting success. On the local path they
persist on disk anyway, but committing them gives a durable history:
`git log -p state/snapshots/` shows exactly what each source changed and when.

`state/reports/` is not tracked. Reports are local output, not baseline.

## If a source starts failing

A run that cannot reach a source has not cleared it. Do not respond by spoofing
a user agent or disabling robots handling. If the direct crawler is rejected by
a CDN, use the browser fallback in [discovery.md](discovery.md) — it navigates
the public site as an ordinary user and hands the capture back to the
deterministic importer.
