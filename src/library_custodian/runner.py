"""Execute one declared schedule job.

This is the single entrypoint every runner calls. A cron daemon, a CI
scheduler and Windows Task Scheduler all invoke the same command with the same
job id, so the behaviour of a scheduled scan does not vary with the ticker that
happened to start it.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .discovery import discover
from .schedule import Job, Schedule, load_schedule, period_key, period_satisfied, record_period_satisfied


EXIT_NO_FINDINGS = 0
EXIT_SOURCE_ERROR = 1
EXIT_FINDINGS = 3


def _findings(report: dict[str, Any]) -> dict[str, list[str]]:
    """Everything a human needs to look at, keyed by why it surfaced."""
    changed: list[str] = []
    new_urls: list[str] = []
    candidates: list[str] = []
    for source in report["sources"]:
        if source.get("status") != "ok":
            continue
        changed.extend(entry["url"] for entry in source.get("changed_since_previous_scan", []))
        new_urls.extend(source.get("new_urls_since_previous_scan", []))
        candidates.extend(source.get("candidates_for_review", []))
    return {
        "changed": sorted(set(changed)),
        "new_urls": sorted(set(new_urls)),
        "candidates": sorted(set(candidates)),
    }


def run_scheduled_job(
    job_id: str,
    schedule_path: Path,
    library_root: Path | None,
    registry_path: Path,
    state_dir: Path,
    quarantine_dir: Path,
    download: bool = False,
    skip_if_satisfied: bool = True,
    now: datetime | None = None,
) -> tuple[dict[str, Any], int]:
    schedule: Schedule = load_schedule(schedule_path)
    job: Job = schedule.job(job_id)
    moment = now or datetime.now(timezone.utc)
    key = period_key(job, moment)

    if skip_if_satisfied and period_satisfied(state_dir, job, key):
        # the issue this window was hunting has already been found; the
        # remaining polls in the period have nothing left to do
        return (
            {
                "job_id": job.id,
                "period": key,
                "skipped": "period_already_satisfied",
                "ran_at": moment.isoformat(),
            },
            EXIT_NO_FINDINGS,
        )

    report = discover(
        library_root=library_root,
        registry_path=registry_path,
        state_dir=state_dir,
        quarantine_dir=quarantine_dir,
        selected_sources=set(job.sources) if job.sources else None,
        download=download,
        verify_known=True,
    )

    findings = _findings(report)
    errored = [source["source_id"] for source in report["sources"] if source.get("status") != "ok"]
    has_findings = any(findings.values())

    marker = None
    if has_findings and not errored:
        # only close the window on a clean scan; a partial scan that happened to
        # find something must not suppress the remaining polls
        marker = record_period_satisfied(state_dir, job, key, {"run_id": report["run_id"], **findings})

    summary = {
        "job_id": job.id,
        "period": key,
        "ran_at": moment.isoformat(),
        "run_id": report["run_id"],
        "sources_scanned": [source["source_id"] for source in report["sources"]],
        "sources_errored": errored,
        "manifest_checked": report["manifest_checked"],
        "findings": findings,
        "period_marker": str(marker) if marker else None,
        "counts": report["counts"],
    }
    if errored:
        return summary, EXIT_SOURCE_ERROR
    return summary, EXIT_FINDINGS if has_findings else EXIT_NO_FINDINGS
