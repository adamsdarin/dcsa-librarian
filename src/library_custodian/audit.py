from __future__ import annotations

import hashlib
import json
import sqlite3
from collections import Counter
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterable


ENTRY_PATH_KEYS = (
    "access_policy",
    "catalog",
    "aliases",
    "documents",
    "relationships",
    "retrieval",
    "library_state",
    "doha_router",
    "doha_topic_taxonomy",
    "doha_topic_coverage",
)


@dataclass
class Finding:
    severity: str
    code: str
    message: str
    path: str | None = None


@dataclass
class AuditReport:
    library_root: str
    ready: bool = True
    counters: dict[str, int] = field(default_factory=dict)
    findings: list[Finding] = field(default_factory=list)
    finding_totals: dict[str, int] = field(default_factory=dict)
    finding_sample_limit: int = 250

    def add(self, severity: str, code: str, message: str, path: Path | str | None = None) -> None:
        self.finding_totals[code] = self.finding_totals.get(code, 0) + 1
        if severity == "error":
            self.ready = False
        if len(self.findings) < self.finding_sample_limit:
            self.findings.append(Finding(severity, code, message, str(path) if path else None))

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["summary"] = dict(Counter(f.severity for f in self.findings))
        return result


def sha256_file(path: Path, block_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(block_size), b""):
            digest.update(block)
    return digest.hexdigest()


def iter_jsonl(path: Path) -> Iterable[tuple[int, dict[str, Any]]]:
    with path.open("r", encoding="utf-8-sig") as handle:
        for line_no, raw in enumerate(handle, 1):
            if raw.strip():
                yield line_no, json.loads(raw)


def _library_path(root: Path, value: str) -> Path:
    candidate = Path(value)
    return candidate if candidate.is_absolute() else root / candidate


def _check_sqlite(path: Path, report: AuditReport) -> None:
    connection: sqlite3.Connection | None = None
    try:
        uri = f"file:{path.as_posix()}?mode=ro"
        connection = sqlite3.connect(uri, uri=True)
        value = connection.execute("PRAGMA integrity_check").fetchone()[0]
        if value != "ok":
            report.add("error", "sqlite_integrity", f"SQLite integrity check returned {value!r}", path)
    except (sqlite3.Error, OSError) as exc:
        report.add("error", "sqlite_unreadable", str(exc), path)
    finally:
        if connection is not None:
            connection.close()


def audit_library(library_root: Path, strict_hashes: bool = False) -> AuditReport:
    root = library_root.resolve()
    report = AuditReport(str(root))
    entry_path = root / "START_HERE_FOR_ROBOTS.json"
    if not entry_path.is_file():
        report.add("error", "missing_entry_point", "START_HERE_FOR_ROBOTS.json is required", entry_path)
        return report

    try:
        entry = json.loads(entry_path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        report.add("error", "invalid_entry_point", str(exc), entry_path)
        return report

    required_paths: list[Path] = []
    for key in ENTRY_PATH_KEYS:
        value = entry.get(key)
        if not isinstance(value, str):
            report.add("error", "missing_entry_reference", f"Entry point has no string value for {key}", entry_path)
            continue
        required_paths.append(_library_path(root, value))
    for value in entry.get("local_indexes", []):
        if isinstance(value, str):
            required_paths.append(_library_path(root, value))

    for path in required_paths:
        if not path.is_file():
            report.add("error", "missing_entry_target", "Required entry-point target is missing", path)
        elif path.suffix.casefold() in {".sqlite", ".db"}:
            _check_sqlite(path, report)

    manifest_value = entry.get("documents")
    if not isinstance(manifest_value, str):
        return report
    manifest_path = _library_path(root, manifest_value)
    if not manifest_path.is_file():
        return report

    ids: set[str] = set()
    records = 0
    humans = robots = missing_humans = missing_robots = 0
    lifecycle = Counter()
    authority = Counter()

    try:
        for line_no, record in iter_jsonl(manifest_path):
            records += 1
            document_id = record.get("document_id")
            if not isinstance(document_id, str) or not document_id:
                report.add("error", "missing_document_id", f"Manifest line {line_no} has no document_id", manifest_path)
            elif document_id in ids:
                report.add("error", "duplicate_document_id", f"Duplicate document_id: {document_id}", manifest_path)
            else:
                ids.add(document_id)

            lifecycle[str(record.get("current_status", "missing"))] += 1
            authority[str(record.get("authority_tier", "missing"))] += 1

            for field_name, kind in (("human_source_path", "human"), ("robot_text_path", "robot")):
                value = record.get(field_name)
                if not isinstance(value, str) or not value:
                    report.add("error", f"missing_{kind}_path", f"{document_id or line_no} has no {field_name}", manifest_path)
                    continue
                resolved = _library_path(root, value)
                exists = resolved.is_file()
                if kind == "human":
                    humans += int(exists)
                    missing_humans += int(not exists)
                else:
                    robots += int(exists)
                    missing_robots += int(not exists)
                if not exists:
                    report.add("error", f"missing_{kind}_file", f"{document_id or line_no} references a missing {kind} file", resolved)

            declared_source = record.get("source_exists")
            human_value = record.get("human_source_path")
            if isinstance(human_value, str) and isinstance(declared_source, bool):
                actual_source = _library_path(root, human_value).is_file()
                if declared_source != actual_source:
                    report.add("error", "source_exists_mismatch", f"{document_id or line_no} declares source_exists={declared_source} but disk state is {actual_source}", manifest_path)

            if strict_hashes:
                for field_name, hash_field in (("human_source_path", "human_sha256"), ("robot_text_path", "robot_sha256")):
                    value = record.get(field_name)
                    expected = record.get(hash_field)
                    if isinstance(value, str) and _library_path(root, value).is_file():
                        if not isinstance(expected, str):
                            report.add("error", "missing_hash", f"{document_id or line_no} has no {hash_field}", manifest_path)
                        elif sha256_file(_library_path(root, value)) != expected.casefold():
                            report.add("error", "hash_mismatch", f"{document_id or line_no} failed {hash_field}", _library_path(root, value))
    except (OSError, json.JSONDecodeError) as exc:
        report.add("error", "invalid_manifest", str(exc), manifest_path)

    report.counters.update(
        manifest_records=records,
        unique_document_ids=len(ids),
        existing_human_files=humans,
        existing_robot_files=robots,
        missing_human_files=missing_humans,
        missing_robot_files=missing_robots,
    )
    for key, value in lifecycle.items():
        report.counters[f"lifecycle:{key}"] = value
    for key, value in authority.items():
        report.counters[f"authority_tier:{key}"] = value

    return report
