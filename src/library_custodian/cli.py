from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .audit import audit_library
from .discovery import discover, import_browser_capture


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="dcsa-custodian", description="Audit a DCSA Library and discover missing official documents without publishing them.")
    commands = parser.add_subparsers(dest="command", required=True)

    doctor = commands.add_parser("doctor", help="Run a read-only integrity and parity audit")
    doctor.add_argument("--library", type=Path, required=True)
    doctor.add_argument("--strict-hashes", action="store_true")
    doctor.add_argument("--json-out", type=Path)

    scan = commands.add_parser("discover", help="Scan allowlisted official sources and create review candidates")
    scan.add_argument("--library", type=Path, required=True)
    scan.add_argument("--registry", type=Path, default=PROJECT_ROOT / "config" / "source_registry.json")
    scan.add_argument("--state-dir", type=Path, default=PROJECT_ROOT / "state")
    scan.add_argument("--quarantine-dir", type=Path, default=PROJECT_ROOT / "quarantine")
    scan.add_argument("--source", action="append", dest="sources")
    scan.add_argument("--download", action="store_true", help="Download missing candidates into quarantine; never publishes")

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
            library_root=args.library.resolve(),
            registry_path=args.registry.resolve(),
            state_dir=args.state_dir.resolve(),
            quarantine_dir=args.quarantine_dir.resolve(),
            selected_sources=set(args.sources) if args.sources else None,
            download=args.download,
        )
        print(json.dumps(report, indent=2))
        return 1 if any(source["status"] == "error" for source in report["sources"]) else 0
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
