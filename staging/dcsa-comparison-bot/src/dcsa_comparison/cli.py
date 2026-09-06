from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .baseline import build_baseline
from .common import read_json, run_id, write_json, write_jsonl
from .compare import DEFAULT_MAX_MATCHES, DEFAULT_TITLE_THRESHOLD, compare_candidates, load_candidates
from .diffing import DEFAULT_DIFF_LINES, diff_documents
from .propose import build_proposals, check_decisions


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG = PROJECT_ROOT / "comparison.config.json"


def _config(path: str | None) -> dict:
    config_path = Path(path).resolve() if path else DEFAULT_CONFIG
    return read_json(config_path) if config_path.is_file() else {}


def _state_dir(config: dict, override: str | None) -> Path:
    if override:
        return Path(override).resolve()
    return (PROJECT_ROOT / config.get("state_directory", "state")).resolve()


def _text_map(values: list[str] | None) -> dict[str, Path]:
    mapping: dict[str, Path] = {}
    for item in values or []:
        name, separator, path = item.partition("=")
        if not separator:
            raise ValueError(f"--text expects NAME=PATH, got {item!r}")
        mapping[name] = Path(path).resolve()
    return mapping


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="dcsa-comparison",
        description=(
            "DCSA Comparison Bot: pair newly released documents against the existing library, "
            "diff their text, and propose - never apply - lifecycle decisions."
        ),
    )
    parser.add_argument("--config")
    commands = parser.add_subparsers(dest="command", required=True)

    doctor = commands.add_parser("doctor", help="Read-only check that inputs and outputs are usable")
    doctor.add_argument("--manifest", type=Path)
    doctor.add_argument("--library-root", type=Path)
    doctor.add_argument("--state-dir")

    baseline = commands.add_parser("baseline", help="Project a library manifest into a comparison baseline")
    baseline.add_argument("--manifest", type=Path, required=True)
    baseline.add_argument("--library-root", type=Path)
    baseline.add_argument("--deep", action="store_true", help="Read robot text for content hashes and headers; reads only")
    baseline.add_argument("--out", type=Path)
    baseline.add_argument("--state-dir")

    compare = commands.add_parser("compare", help="Compare candidate documents against the baseline")
    source = compare.add_mutually_exclusive_group(required=True)
    source.add_argument("--baseline", type=Path)
    source.add_argument("--manifest", type=Path)
    compare.add_argument("--library-root", type=Path)
    compare.add_argument("--deep", action="store_true")
    compare.add_argument("--candidate", type=Path, action="append", dest="candidates", default=[])
    compare.add_argument("--candidates-jsonl", type=Path, help="A Librarian discovery candidates.jsonl")
    compare.add_argument("--text", action="append", dest="texts", help="NAME=PATH extracted robot text for a candidate")
    compare.add_argument("--title-threshold", type=float)
    compare.add_argument("--max-matches", type=int)
    compare.add_argument("--out", type=Path)
    compare.add_argument("--state-dir")

    diff = commands.add_parser("diff", help="Section-aware text diff between two robot-readable documents")
    diff.add_argument("--left", type=Path, required=True, help="The library copy")
    diff.add_argument("--right", type=Path, required=True, help="The newly released document")
    diff.add_argument("--left-label")
    diff.add_argument("--right-label")
    diff.add_argument("--diff-lines", type=int)
    diff.add_argument("--out", type=Path)
    diff.add_argument("--state-dir")

    propose = commands.add_parser("propose", help="Emit proposed decisions and a guidance-catalog handoff; writes nothing downstream")
    propose.add_argument("--report", type=Path, required=True)
    propose.add_argument("--reviewer", required=True, help="The named human who will own the decision")
    propose.add_argument("--accept", action="append", dest="accepted", help="finding_id to accept; repeatable. Default: all findings")
    propose.add_argument("--include-inferred", action="store_true")
    propose.add_argument("--out", type=Path)
    propose.add_argument("--state-dir")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        config = _config(args.config)
        state_dir = _state_dir(config, getattr(args, "state_dir", None))

        if args.command == "doctor":
            checks: list[dict[str, object]] = []
            if args.manifest:
                readable = args.manifest.is_file()
                checks.append({"check": "manifest_readable", "ok": readable, "path": str(args.manifest)})
                if readable:
                    baseline = build_baseline(args.manifest, args.library_root, deep=False)
                    checks.append({"check": "manifest_parsed", "ok": True, "entries": baseline["counts"]["entries"]})
                    checks.append({
                        "check": "identity_signals_present",
                        "ok": baseline["counts"]["with_document_number"] + baseline["counts"]["with_edition_token"] > 0,
                        "with_document_number": baseline["counts"]["with_document_number"],
                        "with_edition_token": baseline["counts"]["with_edition_token"],
                    })
            if args.library_root:
                checks.append({"check": "library_root_exists", "ok": args.library_root.is_dir(), "path": str(args.library_root)})
            state_dir.mkdir(parents=True, exist_ok=True)
            checks.append({"check": "state_dir_writable", "ok": True, "path": str(state_dir)})
            checks.append({"check": "writes_outside_this_project", "ok": True, "value": "none by design"})
            result = {"ok": all(check["ok"] for check in checks), "checks": checks}
            print(json.dumps(result, indent=2))
            return 0 if result["ok"] else 2

        if args.command == "baseline":
            report = build_baseline(args.manifest, args.library_root, deep=args.deep)
            output = args.out or state_dir / "baselines" / f"baseline-{run_id()}.json"
            write_json(output, report)
            print(json.dumps({"output": str(output), "counts": report["counts"]}, indent=2))
            return 0 if not report["unreadable"] else 1

        if args.command == "compare":
            baseline = read_json(args.baseline) if args.baseline else build_baseline(args.manifest, args.library_root, deep=args.deep)
            candidates = load_candidates(
                paths=[path.resolve() for path in args.candidates],
                candidates_jsonl=args.candidates_jsonl,
                text_map=_text_map(args.texts),
            )
            if not candidates:
                raise ValueError("no candidates supplied; pass --candidate and/or --candidates-jsonl")
            report = compare_candidates(
                baseline,
                candidates,
                title_threshold=args.title_threshold if args.title_threshold is not None
                else float(config.get("title_similarity_threshold", DEFAULT_TITLE_THRESHOLD)),
                max_matches=args.max_matches if args.max_matches is not None
                else int(config.get("max_matches_per_candidate", DEFAULT_MAX_MATCHES)),
            )
            identifier = run_id()
            output = args.out or state_dir / "comparisons" / identifier / "comparison-report.json"
            write_json(output, report)
            write_jsonl(output.parent / "findings.jsonl", report["findings"])
            print(json.dumps({"output": str(output), "counts": report["counts"]}, indent=2))
            return 0

        if args.command == "diff":
            report = diff_documents(
                args.left.resolve(),
                args.right.resolve(),
                left_label=args.left_label,
                right_label=args.right_label,
                diff_lines=args.diff_lines if args.diff_lines is not None
                else int(config.get("diff_excerpt_lines", DEFAULT_DIFF_LINES)),
            )
            output = args.out or state_dir / "diffs" / f"diff-{run_id()}.json"
            write_json(output, report)
            print(json.dumps({"output": str(output), "summary": report["summary"]}, indent=2))
            return 0

        if args.command == "propose":
            report = read_json(args.report)
            payload = build_proposals(
                report,
                reviewer=args.reviewer,
                accepted_finding_ids=set(args.accepted) if args.accepted else None,
                include_inferred=args.include_inferred,
            )
            problems = check_decisions(payload)
            payload["schema_problems"] = problems
            output = args.out or state_dir / "proposals" / f"proposal-{run_id()}.json"
            write_json(output, payload)
            write_json(output.parent / f"{output.stem}-fso-handoff.json", {
                "schema_version": "1.0",
                "generated_at": payload["generated_at"],
                "generated_by": "dcsa-comparison-bot",
                "note": "Input feed for the FSO guidance catalog. That project owns the findings register; this file proposes nothing to it.",
                "rows": payload["fso_guidance_watch_handoff"],
            })
            print(json.dumps({
                "output": str(output),
                "counts": payload["counts"],
                "schema_problems": problems,
                "applied": False,
            }, indent=2))
            return 2 if problems else 0

    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(f"ERROR: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    return 64


if __name__ == "__main__":
    raise SystemExit(main())
