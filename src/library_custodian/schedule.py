"""Runner-agnostic scheduling.

Nothing here executes on a timer. An agent framework cannot schedule itself;
something outside it has to tick. What this module does is make the cadence a
declared property of the project — one source of truth in
`config/schedule.json` — and render it for whichever runner is available, so
swapping the ticker never means rewriting the schedule.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any


RUNNERS = ("cron", "github-actions", "schtasks")


@dataclass(frozen=True)
class Job:
    id: str
    description: str
    local_times: tuple[str, ...]
    days_of_month: str
    sources: tuple[str, ...]
    once_per_period: str | None
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
        jobs.append(
            Job(
                id=str(raw["id"]),
                description=str(raw.get("description", "")),
                local_times=times,
                days_of_month=str(raw.get("days_of_month", "*")),
                sources=tuple(str(value) for value in raw.get("sources", [])),
                once_per_period=period,
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


def render_github_actions(schedule: Schedule) -> str:
    lines = [
        "# Rendered from config/schedule.json. GitHub Actions cron is UTC.",
        "on:",
        "  workflow_dispatch:",
        "    inputs:",
        "      job:",
        "        description: Schedule job id to run",
        "        required: false",
        "  schedule:",
    ]
    for job in schedule.jobs:
        lines.append(f"    # {job.id}: {job.description}")
        lines.append(f"    - cron: '{cron_expression(job, schedule.utc_offset_hours)}'")
    return "\n".join(lines) + "\n"


def render_schtasks(schedule: Schedule, command: str) -> str:
    """Windows Task Scheduler commands, in local time — schtasks does not use UTC."""
    lines = [f":: Rendered from config/schedule.json. Times are local ({schedule.timezone_name}); schtasks schedules in local time."]
    for job in schedule.jobs:
        for local_time in job.local_times:
            name = f"dcsa-librarian-{job.id}-{local_time.replace(':', '')}"
            lines.append(f":: {job.id}: {job.description}")
            lines.append(
                f'schtasks /create /tn "{name}" /tr "{command} --job {job.id}" '
                f'/sc monthly /d {job.days_of_month} /st {local_time} /f'
            )
    return "\n".join(lines) + "\n"


def render(runner: str, schedule: Schedule, command: str) -> str:
    if runner == "cron":
        return render_cron(schedule, command)
    if runner == "github-actions":
        return render_github_actions(schedule)
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
