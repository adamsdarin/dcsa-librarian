from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .audit import audit_library
from .discovery import discover, import_browser_capture, preflight, render_preflight_text
from .runner import run_scheduled_job
from .schedule import RUNNERS, load_schedule, render


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="dcsa-custodian", description="DCSA Librarian: audit intake integrity and discover missing official documents without publishing them.")
    commands = parser.add_subparsers(dest="command", required=True)
    confirm = commands.add_parser('confirm-period', help='Record reviewed issue-period evidence before ending publication polling')
    confirm.add_argument('--job', required=True)
    confirm.add_argument('--period', required=True)
    confirm.add_argument('--receipt', type=Path, required=True)
    confirm.add_argument('--library', type=Path, required=True)
    confirm.add_argument('--schedule', type=Path, default=PROJECT_ROOT / 'config/schedule.json')
    confirm.add_argument('--registry', type=Path, default=PROJECT_ROOT / 'config/source_registry.json')
    confirm.add_argument('--state-dir', type=Path, default=PROJECT_ROOT / 'state')
    status = commands.add_parser('scan-status', help='Read scheduled acquisition freshness without network access')
    status.add_argument('--library', type=Path, required=True)
    status.add_argument('--schedule', type=Path, default=PROJECT_ROOT / 'config/schedule.json')
    status.add_argument('--registry', type=Path, default=PROJECT_ROOT / 'config/source_registry.json')
    status.add_argument('--state-dir', type=Path, default=PROJECT_ROOT / 'state')

    doctor = commands.add_parser("doctor", help="Run a read-only integrity and parity audit")
    doctor.add_argument("--library", type=Path, required=True)
    doctor.add_argument("--strict-hashes", action="store_true")
    doctor.add_argument("--json-out", type=Path)

    scan = commands.add_parser("discover", help="Scan allowlisted official sources and create review candidates")
    scan.add_argument("--library", type=Path, help="Classify findings against this library's manifest; omit to detect source-side change only")
    scan.add_argument("--registry", type=Path, default=PROJECT_ROOT / "config" / "source_registry.json")
    scan.add_argument("--exclusions", type=Path, default=PROJECT_ROOT / "config" / "catalog_exclusions.json")
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

    check = commands.add_parser("preflight", help="Show what one source serves, without writing anything")
    check.add_argument("--source", required=True, help="Source id from config/source_registry.json")
    check.add_argument("--registry", type=Path, default=PROJECT_ROOT / "config" / "source_registry.json")
    check.add_argument("--match", help="Only list documents whose URL, link text or filename contains this")
    check.add_argument("--json", action="store_true", help="Emit the raw result instead of the readable report")

    commands.add_parser("selftest", help="Run the project's own tests to confirm this install works")

    scheduled = commands.add_parser("scheduled-scan", help="Run one job declared in config/schedule.json")
    scheduled.add_argument("--job", required=True, help="Job id from the schedule declaration")
    scheduled.add_argument("--schedule", type=Path, default=PROJECT_ROOT / "config" / "schedule.json")
    scheduled.add_argument("--library", type=Path, help="Optional; omit when the runner has no access to the library")
    scheduled.add_argument("--registry", type=Path, default=PROJECT_ROOT / "config" / "source_registry.json")
    scheduled.add_argument("--exclusions", type=Path, default=PROJECT_ROOT / "config" / "catalog_exclusions.json")
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

    doha = commands.add_parser("doha-provenance", help="Record official DOHA source URLs for library decisions from captured listing pages, and list listed decisions the library lacks")
    doha.add_argument("--library", type=Path, required=True)
    doha.add_argument("--capture", type=Path, action="append", required=True, help="Listing capture file; repeatable")
    doha.add_argument("--registry", type=Path, default=PROJECT_ROOT / "config" / "source_registry.json")
    doha.add_argument("--state-dir", type=Path, default=PROJECT_ROOT / "state")
    doha.add_argument("--summary", action="store_true", help="Triage the listed-but-not-held decisions per group (ISCR hearings, Appeal Board) by case year and listing; print it as text instead of the report JSON")
    doha.add_argument("--human-hashes", type=Path, help="Deep-audit hashes (Archivist PRODUCTION_AUDIT.json) that let a recorded download prove identity by bytes")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == 'confirm-period':
        from .schedule import confirm_period
        path = confirm_period(args.state_dir, load_schedule(args.schedule).job(args.job), args.period,
                              args.receipt, args.registry, args.library)
        print(json.dumps({'marker': str(path), 'period': args.period, 'status': 'reviewed_issue_confirmed'}))
        return 0
    if args.command == 'scan-status':
        from .status import scan_status
        print(json.dumps(scan_status(args.schedule, args.registry, args.state_dir, args.library), indent=2))
        return 0
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
            exclusions_path=args.exclusions.resolve() if args.exclusions else None,
        )
        print(json.dumps(report, indent=2))
        return 1 if any(source["status"] == "error" for source in report["sources"]) else 0
    if args.command == "preflight":
        try:
            result = preflight(args.registry.resolve(), args.source, args.match)
        except KeyError as exc:
            print(exc.args[0], file=sys.stderr)
            return 64
        print(json.dumps(result, indent=2) if args.json else render_preflight_text(result), end="" if not args.json else "\n")
        return 0 if result.get("reachable") else 1
    if args.command == "selftest":
        import unittest

        tests_dir = PROJECT_ROOT / "tests"
        if not tests_dir.is_dir():
            print(f"No tests directory at {tests_dir}", file=sys.stderr)
            return 64
        suite = unittest.TestLoader().discover(str(tests_dir), top_level_dir=str(tests_dir))
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        return 0 if result.wasSuccessful() else 1
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
            exclusions_path=args.exclusions.resolve() if args.exclusions else None,
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
    if args.command == "doha-provenance":
        from .doha_provenance import build_ledger, format_summary, summarize_missing
        hashes = {}
        if args.human_hashes:
            hashes = json.loads(args.human_hashes.read_text(encoding="utf-8")).get("human_hashes", {})
        rows, missing, report = build_ledger(args.library.resolve(), [path.resolve() for path in args.capture],
                                    args.registry.resolve(), hashes)
        ledger = args.state_dir.resolve() / "provenance" / "doha_source_urls.jsonl"
        ledger.parent.mkdir(parents=True, exist_ok=True)
        with ledger.open("w", encoding="utf-8", newline="\n") as handle:
            for row in rows:
                handle.write(json.dumps(row, separators=(",", ":")) + "\n")
        report["ledger"] = str(ledger)
        not_held = ledger.parent / "doha_not_in_library.jsonl"
        with not_held.open("w", encoding="utf-8", newline="\n") as handle:
            for item in missing:
                handle.write(json.dumps(item, separators=(",", ":")) + "\n")
        report["not_in_library"] = str(not_held)
        if args.summary:
            report["not_in_library_summary"] = summarize_missing(missing, report)
        (ledger.parent / "doha_source_urls_report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        if args.summary:
            print(format_summary(report["not_in_library_summary"], report))
        else:
            print(json.dumps(report, indent=2))
        return 0 if report["matched"] else 2
    return 64


if __name__ == "__main__":
    sys.exit(main())
