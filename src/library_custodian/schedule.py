"""Runner-agnostic scheduling.

Nothing here executes on a timer. An agent framework cannot schedule itself;
something outside it has to tick. What this module does is make the cadence a
declared property of the project — one source of truth in
`config/schedule.json` — and render it for whichever runner is available, so
swapping the ticker never means rewriting the schedule.
"""

from __future__ import annotations

import json
import urllib.parse
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any


# GitHub Actions is deliberately absent. DCSA blocks GitHub's hosted runners,
# so a workflow there fails every time while looking like monitoring.
RUNNERS = ("schtasks", "cron")


ACTIONS = ("discover", "doctor")


@dataclass(frozen=True)
class Job:
    id: str
    description: str
    action: str
    local_times: tuple[str, ...]
    days_of_month: str
    sources: tuple[str, ...]
    once_per_period: str | None
    expect: str | None
    rationale: str


@dataclass(frozen=True)
class Schedule:
    timezone_name: str
    utc_offset_hours: int
    jobs: tuple[Job, ...]

    def job(self, job_id: str) -> Job:
        for candidate in self.jobs:
            if candidate.id == job_id:
                return candidate
        known = ", ".join(job.id for job in self.jobs)
        raise KeyError(f"no job {job_id!r} in the schedule; known jobs: {known}")


def load_schedule(path: Path) -> Schedule:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    jobs = []
    for raw in data.get("jobs", []):
        times = tuple(str(value) for value in raw.get("local_times", []))
        if not times:
            raise ValueError(f"job {raw.get('id')!r} declares no local_times")
        period = raw.get("once_per_period")
        if period not in (None, "month"):
            raise ValueError(f"job {raw.get('id')!r} has unsupported once_per_period {period!r}")
        action = str(raw.get("action", "discover"))
        if action not in ACTIONS:
            raise ValueError(f"job {raw.get('id')!r} has unsupported action {action!r}; expected one of {', '.join(ACTIONS)}")
        jobs.append(
            Job(
                id=str(raw["id"]),
                description=str(raw.get("description", "")),
                action=action,
                local_times=times,
                days_of_month=str(raw.get("days_of_month", "*")),
                sources=tuple(str(value) for value in raw.get("sources", [])),
                once_per_period=period,
                expect=(str(raw["expect"]) if raw.get("expect") else None),
                rationale=str(raw.get("rationale", "")),
            )
        )
    if not jobs:
        raise ValueError("schedule declares no jobs")
    return Schedule(
        timezone_name=str(data.get("timezone", "UTC")),
        utc_offset_hours=int(data.get("utc_offset_hours", 0)),
        jobs=tuple(jobs),
    )


def to_utc(local_time: str, utc_offset_hours: int) -> tuple[int, int, int]:
    """Convert HH:MM in the declared offset to UTC, returning (hour, minute, day_shift)."""
    hour_text, _, minute_text = local_time.partition(":")
    hour, minute = int(hour_text), int(minute_text)
    if not (0 <= hour <= 23 and 0 <= minute <= 59):
        raise ValueError(f"local time out of range: {local_time!r}")
    shifted = hour - utc_offset_hours
    return shifted % 24, minute, shifted // 24


def cron_expression(job: Job, utc_offset_hours: int) -> str:
    """Render one 5-field UTC cron expression covering all of a job's times.

    A conversion that rolls past midnight would move the job to a different day
    of the month, silently changing which days it runs. That is refused rather
    than emitted wrong.
    """
    minutes = set()
    hours = []
    for local_time in job.local_times:
        hour, minute, day_shift = to_utc(local_time, utc_offset_hours)
        if day_shift and job.days_of_month != "*":
            raise ValueError(
                f"job {job.id!r}: converting {local_time} to UTC crosses midnight, which would "
                f"shift its day-of-month constraint {job.days_of_month!r}. Declare the job in UTC instead."
            )
        minutes.add(minute)
        hours.append(hour)
    if len(minutes) != 1:
        raise ValueError(f"job {job.id!r}: all local_times must share a minute to render one cron expression")
    hour_field = ",".join(str(hour) for hour in sorted(set(hours)))
    return f"{minutes.pop()} {hour_field} {job.days_of_month} * *"


def period_key(job: Job, moment: datetime) -> str | None:
    """Identify the release period a run belongs to.

    A month-end window straddles the boundary: 28-31 March and 1-3 April are
    both hunting the March issue, so early-month days count toward the month
    that just ended. Without that, the April polls would re-arm and re-report an
    issue the March polls already found.
    """
    if job.once_per_period != "month":
        return None
    year, month = moment.year, moment.month
    if moment.day <= 3:
        year, month = (year - 1, 12) if month == 1 else (year, month - 1)
    return f"{year:04d}-{month:02d}"


def satisfies_expectation(url: str, expect: str | None) -> bool:
    """Whether a finding is the thing this job was waiting for.

    Case-insensitive substring match against the percent-decoded URL, so a
    declaration can say "voi newsletter" and still match
    ".../260331%20VOI%20Newsletter.pdf".

    A job with no expectation is satisfied by any finding. That is the right
    default for a job that is simply looking for movement, and the wrong one for
    a job waiting on a specific publication — which is why the release watch
    declares what it is waiting for.
    """
    if not expect:
        return True
    return expect.casefold() in urllib.parse.unquote(url).casefold()


def marker_path(state_dir: Path, job: Job, key: str) -> Path:
    return state_dir / "watch" / job.id / f"{key}.json"


def period_satisfied(state_dir: Path, job: Job, key: str | None) -> bool:
    return key is not None and marker_path(state_dir, job, key).is_file()


def record_period_satisfied(state_dir: Path, job: Job, key: str | None, evidence: dict[str, Any]) -> Path | None:
    if key is None:
        return None
    path = marker_path(state_dir, job, key)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({"job_id": job.id, "period": key, "satisfied_at": datetime.now(timezone.utc).isoformat(), "evidence": evidence}, indent=2) + "\n",
        encoding="utf-8",
    )
    return path


def render_cron(schedule: Schedule, command: str) -> str:
    lines = [f"# Rendered from config/schedule.json ({schedule.timezone_name}, cron is UTC)."]
    for job in schedule.jobs:
        lines.append(f"# {job.id}: {job.description}")
        lines.append(f"{cron_expression(job, schedule.utc_offset_hours)} {command} --job {job.id}")
    return "\n".join(lines) + "\n"


def expand_days(days_of_month: str) -> str:
    """Expand a cron-style day field into the explicit list schtasks requires.

    Windows Task Scheduler takes a comma-separated list of day numbers and does
    not understand ranges, so "28-31,1-3" has to become "28,29,30,31,1,2,3".
    Days that do not exist in a given month simply do not fire, which is why the
    window also covers the first days of the following month.
    """
    if days_of_month == "*":
        return "*"
    days: list[int] = []
    for part in days_of_month.split(","):
        part = part.strip()
        if "-" in part:
            start, _, end = part.partition("-")
            days.extend(range(int(start), int(end) + 1))
        else:
            days.append(int(part))
    for day in days:
        if not 1 <= day <= 31:
            raise ValueError(f"day of month out of range in {days_of_month!r}: {day}")
    return ",".join(str(day) for day in days)


def render_schtasks(schedule: Schedule, command: str) -> str:
    """Windows Task Scheduler commands.

    schtasks schedules in the machine's local time, so the declared times are
    emitted unconverted — and unlike the UTC crons, they track DST correctly.
    One task per time of day: a monthly task cannot repeat within a day.
    """
    lines = [
        f":: Rendered from config/schedule.json by: python custodian.py schedule --render schtasks",
        f":: Times are local ({schedule.timezone_name}). schtasks uses local time, so these follow DST.",
        ":: Run this from the project directory in an elevated Command Prompt.",
    ]
    for job in schedule.jobs:
        lines.append("")
        lines.append(f":: {job.id}: {job.description}")
        for local_time in job.local_times:
            name = f"DCSA Librarian - {job.id} - {local_time.replace(':', '')}"
            lines.append(
                f'schtasks /create /tn "{name}" /tr "{command} --job {job.id}" '
                f'/sc monthly /d {expand_days(job.days_of_month)} /st {local_time} /rl limited /f'
            )
    return "\n".join(lines) + "\n"


def render(runner: str, schedule: Schedule, command: str) -> str:
    if runner == "cron":
        return render_cron(schedule, command)
    if runner == "schtasks":
        return render_schtasks(schedule, command)
    raise ValueError(f"unknown runner {runner!r}; expected one of {', '.join(RUNNERS)}")


def due_today(job: Job, day: date) -> bool:
    """Whether a job's day-of-month field admits this date."""
    if job.days_of_month == "*":
        return True
    for part in job.days_of_month.split(","):
        part = part.strip()
        if "-" in part:
            start, _, end = part.partition("-")
            if int(start) <= day.day <= int(end):
                return True
        elif int(part) == day.day:
            return True
    return False
