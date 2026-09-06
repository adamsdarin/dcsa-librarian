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


def render_text_summary(summary: dict[str, Any], code: int) -> str:
    """Plain text a person reads directly.

    Nothing downstream of a scheduled scan should need a model to find out what
    happened, so the verdict is stated in words, not inferred from JSON.
    """
    lines = [
        "DCSA Librarian - scheduled scan",
        "=" * 46,
        f"Job:     {summary['job_id']}",
        f"Ran:     {summary['ran_at']} (UTC)",
    ]
    if summary.get("period"):
        lines.append(f"Period:  {summary['period']}")

    if summary.get("skipped"):
        lines += [
            "Result:  SKIPPED - this period's issue was already found by an earlier poll.",
            "",
            "Nothing to do. The remaining polls in this window will also skip.",
        ]
        return "\n".join(lines) + "\n"

    findings = summary["findings"]
    total = len(set(findings["changed"]) | set(findings["new_urls"]) | set(findings["candidates"]))

    if code == EXIT_SOURCE_ERROR:
        lines.append("Result:  INCOMPLETE - a source could not be reached.")
    elif total:
        lines.append(f"Result:  {total} item(s) need review.")
    else:
        lines.append("Result:  No changes detected.")

    lines += [
        "",
        f"Sources scanned:  {', '.join(summary['sources_scanned']) or 'none'}",
        f"Manifest checked: {'yes' if summary['manifest_checked'] else 'no (source-side change only)'}",
    ]

    if summary["sources_errored"]:
        lines += [
            "",
            "!! SOURCES THAT FAILED: " + ", ".join(summary["sources_errored"]),
            "!! This scan did NOT clear those sources. Absence of findings below",
            "!! says nothing about them. The release window was left open so a",
            "!! later poll can still succeed.",
        ]

    for heading, key in (
        ("CHANGED SINCE LAST SCAN", "changed"),
        ("NEW SINCE LAST SCAN", "new_urls"),
        ("FLAGGED FOR REVIEW", "candidates"),
    ):
        urls = findings[key]
        if urls:
            lines += ["", f"{heading} ({len(urls)})"]
            lines += [f"  {url}" for url in urls]

    lines += ["", "-" * 46]
    if code == EXIT_SOURCE_ERROR:
        lines.append("Next: check network access to the failed source, then re-run.")
    elif total:
        lines.append("Next: open the URLs above and decide whether the library needs updating.")
    else:
        lines.append("Next: nothing.")
    return "\n".join(lines) + "\n"


def write_reports(state_dir: Path, summary: dict[str, Any], code: int) -> Path:
    """Write the readable report where a person will actually find it."""
    text = render_text_summary(summary, code)
    reports = state_dir / "reports"
    reports.mkdir(parents=True, exist_ok=True)
    latest = reports / f"{summary['job_id']}-latest.txt"
    latest.write_text(text, encoding="utf-8")
    with (reports / "scan-log.txt").open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(text + "\n")
    return latest


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
        skipped = {
            "job_id": job.id,
            "period": key,
            "skipped": "period_already_satisfied",
            "ran_at": moment.isoformat(),
        }
        skipped["report_path"] = str(write_reports(state_dir, skipped, EXIT_NO_FINDINGS))
        return skipped, EXIT_NO_FINDINGS

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
    code = EXIT_SOURCE_ERROR if errored else (EXIT_FINDINGS if has_findings else EXIT_NO_FINDINGS)
    summary["report_path"] = str(write_reports(state_dir, summary, code))
    return summary, code
