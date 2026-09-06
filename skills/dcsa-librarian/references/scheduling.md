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
python custodian.py schedule --render github-actions
python custodian.py schedule --render cron
python custodian.py schedule --render schtasks
```

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
| 1 | A source failed. The scan is incomplete; do not read it as "no changes" |
| 3 | Findings to triage |

## The declared jobs

- **`monthly-scan`** — every enabled source, the 1st at 09:00 America/New_York.
- **`voi-release-watch`** — the VOI home at 09:00, 12:00 and 15:00 across the
  month-end window (days 28-31 and 1-3).

The window exists because the release date is not knowable in advance. Observed
issues are dated `260130`, `260227`, `260331` — DCSA targets month-end and
slips; the March 2026 issue surfaced around 2 April. Polling a window and
stopping on success is the only schedule that actually catches it.

`once_per_period` closes the window: when a poll finds something, it writes
`state/watch/<job>/<period>.json` and the remaining polls in that period no-op.
A period spans the boundary — 28-31 March and 1-3 April both belong to
`2026-03` — so the early-April polls do not re-arm and re-report the issue the
March polls already found. **A scan with a failed source never closes a
window**: an incomplete run must not suppress the polls that might still
succeed.

## Cron is UTC; the declaration is not

`utc_offset_hours` is a fixed standard-time offset (EST, -5). Rendered crons
are UTC, so during EDT each job fires an hour later in local terms. Three polls
a day absorb that; the monthly sweep does not care. A conversion that would
cross midnight and silently shift a job's day-of-month is refused rather than
emitted wrong.

`schtasks` is the exception: it schedules in local time, so that adapter
renders the declared local times unconverted.

## Running without the library

`--library` is optional. Given one, findings are classified against the
manifest (`known` / `missing_from_manifest`). Without one, every document is
`manifest_not_checked` and only source-side movement counts as a finding —
which is what lets the scan run somewhere that has network access but no access
to the corpus. Manifest triage then happens where the library lives.

## State is the baseline, so state must survive

`state/snapshots/` and `state/watch/` are tracked in git on purpose. Change
detection compares against the previous scan; a runner that discards them
detects nothing, ever, while still reporting success. Any hosted runner must
commit them back. A useful side effect: `git log -p state/snapshots/` is a
durable history of exactly what each source changed and when.

## Choosing a runner

The requirements are network egress to the configured sources, a durable place
for `state/`, and optionally the library. A runner missing the first two cannot
do this job regardless of how it is configured.

Datacenter IPs are a live risk: DCSA sits behind a CDN that often rejects them
and non-browser user agents, so a hosted runner may see 403s where an ordinary
desktop succeeds. Do not respond by spoofing a user agent or disabling
safeguards. Either move the job to a runner whose egress is accepted, or use
the browser fallback in [discovery.md](discovery.md).
