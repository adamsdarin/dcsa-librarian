from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .audit import audit_library
from .discovery import discover, import_browser_capture
from .runner import run_scheduled_job
from .schedule import RUNNERS, load_schedule, render


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="dcsa-custodian", description="DCSA Librarian: audit intake integrity and discover missing official documents without publishing them.")
    commands = parser.add_subparsers(dest="command", required=True)

    doctor = commands.add_parser("doctor", help="Run a read-only integrity and parity audit")
    doctor.add_argument("--library", type=Path, required=True)
    doctor.add_argument("--strict-hashes", action="store_true")
    doctor.add_argument("--json-out", type=Path)

    scan = commands.add_parser("discover", help="Scan allowlisted official sources and create review candidates")
    scan.add_argument("--library", type=Path, help="Classify findings against this library's manifest; omit to detect source-side change only")
    scan.add_argument("--registry", type=Path, default=PROJECT_ROOT / "config" / "source_registry.json")
    scan.add_argument("--state-dir", type=Path, default=PROJECT_ROOT / "state")
    scan.add_argument("--quarantine-dir", type=Path, default=PROJECT_ROOT / "quarantine")
    scan.add_argument("--source", action="append", dest="sources")
    scan.add_argument("--download", action="store_true", help="Download missing candidates into quarantine; never publishes")
    scan.add_argument(
        "--verify-known",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Probe documents already in the manifest for in-place revisions (default: on)",
    )

    scheduled = commands.add_parser("scheduled-scan", help="Run one job declared in config/schedule.json")
    scheduled.add_argument("--job", required=True, help="Job id from the schedule declaration")
    scheduled.add_argument("--schedule", type=Path, default=PROJECT_ROOT / "config" / "schedule.json")
    scheduled.add_argument("--library", type=Path, help="Optional; omit when the runner has no access to the library")
    scheduled.add_argument("--registry", type=Path, default=PROJECT_ROOT / "config" / "source_registry.json")
    scheduled.add_argument("--state-dir", type=Path, default=PROJECT_ROOT / "state")
    scheduled.add_argument("--quarantine-dir", type=Path, default=PROJECT_ROOT / "quarantine")
    scheduled.add_argument("--download", action="store_true")
    scheduled.add_argument(
        "--skip-if-satisfied",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Skip when this period's issue was already found by an earlier poll (default: on)",
    )

    render_schedule = commands.add_parser("schedule", help="Render the declared schedule for a specific runner")
    render_schedule.add_argument("--render", choices=RUNNERS, required=True)
    render_schedule.add_argument("--schedule", type=Path, default=PROJECT_ROOT / "config" / "schedule.json")
    render_schedule.add_argument(
        "--command",
        dest="command_template",
        default="python custodian.py scheduled-scan",
        help="Command the rendered adapter should invoke",
    )

    browser_import = commands.add_parser("browser-import", help="Validate a browser page-by-page capture and create review candidates")
    browser_import.add_argument("--library", type=Path, required=True)
    browser_import.add_argument("--capture", type=Path, required=True)
    browser_import.add_argument("--registry", type=Path, default=PROJECT_ROOT / "config" / "source_registry.json")
    browser_import.add_argument("--state-dir", type=Path, default=PROJECT_ROOT / "state")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "doctor":
        report = audit_library(args.library, strict_hashes=args.strict_hashes)
        payload = report.to_dict()
        encoded = json.dumps(payload, indent=2)
        if args.json_out:
            args.json_out.parent.mkdir(parents=True, exist_ok=True)
            args.json_out.write_text(encoded + "\n", encoding="utf-8")
        print(encoded)
        return 0 if report.ready else 2
    if args.command == "discover":
        report = discover(
            library_root=args.library.resolve() if args.library else None,
            registry_path=args.registry.resolve(),
            state_dir=args.state_dir.resolve(),
            quarantine_dir=args.quarantine_dir.resolve(),
            selected_sources=set(args.sources) if args.sources else None,
            download=args.download,
            verify_known=args.verify_known,
        )
        print(json.dumps(report, indent=2))
        return 1 if any(source["status"] == "error" for source in report["sources"]) else 0
    if args.command == "schedule":
        print(render(args.render, load_schedule(args.schedule.resolve()), args.command_template), end="")
        return 0
    if args.command == "scheduled-scan":
        summary, code = run_scheduled_job(
            job_id=args.job,
            schedule_path=args.schedule.resolve(),
            library_root=args.library.resolve() if args.library else None,
            registry_path=args.registry.resolve(),
            state_dir=args.state_dir.resolve(),
            quarantine_dir=args.quarantine_dir.resolve(),
            download=args.download,
            skip_if_satisfied=args.skip_if_satisfied,
        )
        print(json.dumps(summary, indent=2))
        return code
    if args.command == "browser-import":
        report = import_browser_capture(
            library_root=args.library.resolve(),
            registry_path=args.registry.resolve(),
            capture_path=args.capture.resolve(),
            state_dir=args.state_dir.resolve(),
        )
        print(json.dumps(report, indent=2))
        return 0
    return 64


if __name__ == "__main__":
    sys.exit(main())
