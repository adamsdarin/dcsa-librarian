"""Build the comparison baseline from a DCSA Library manifest.

The baseline is a read-only projection. It never writes into the library and it
carries no judgement: for each existing document it records the manifest facts
plus the deterministic identity signals derived from them.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .common import (
    iter_jsonl,
    normalize_text,
    norm_path,
    parse_authority_header,
    read_text_file,
    sha256_text,
    utc_now,
)
from .identity import signals_for


CARRIED_FIELDS = (
    "collection_id",
    "domain",
    "current_status",
    "authority_role",
    "authority_priority",
    "contractor_binding",
    "answer_eligibility",
    "effective_date",
    "canonical_document_id",
    "duplicate_of",
    "robot_content_sha256",
    "human_source_path",
)


def title_for(record: dict[str, Any]) -> str:
    title = str(record.get("title") or "").strip()
    if title:
        return title
    robot = norm_path(record.get("robot_text_path"))
    if robot:
        return Path(robot).stem
    return str(record.get("document_id") or "")


def build_baseline(
    manifest_path: Path,
    library_root: Path | None = None,
    deep: bool = False,
) -> dict[str, Any]:
    """Project a manifest into baseline entries.

    `deep` additionally reads each robot text file to record a normalized-content
    hash and the document's own header fields. It is the only mode that touches
    library bytes, and it reads them - never writes.
    """
    if deep and library_root is None:
        raise ValueError("deep baseline requires --library-root")

    entries: list[dict[str, Any]] = []
    unreadable: list[dict[str, str]] = []

    for line_number, record in iter_jsonl(manifest_path):
        document_id = record.get("document_id")
        if not document_id:
            unreadable.append({"line": str(line_number), "reason": "missing_document_id"})
            continue
        robot_rel = norm_path(record.get("robot_text_path"))
        title = title_for(record)
        entry: dict[str, Any] = {
            "document_id": str(document_id),
            "title": title,
            "robot_text_path": robot_rel,
            "manifest_line": line_number,
        }
        for field in CARRIED_FIELDS:
            if record.get(field) is not None:
                entry[field] = record[field]

        header_text = ""
        if deep and robot_rel:
            robot_path = (library_root / robot_rel) if library_root else None
            if robot_path is not None and robot_path.is_file():
                text = read_text_file(robot_path)
                entry["normalized_text_sha256"] = sha256_text(normalize_text(text))
                entry["exact_text_sha256"] = sha256_text(text)
                header = parse_authority_header(text)
                if header:
                    entry["header_fields"] = header
                    entry.setdefault("effective_date", header.get("effective_date"))
                header_text = " ".join(str(value) for value in header.values())
            else:
                unreadable.append({"line": str(line_number), "reason": "robot_text_unreadable", "path": robot_rel})

        entry["signals"] = signals_for(title, header_text)
        entries.append(entry)

    return {
        "schema_version": "1.0",
        "generated_at": utc_now(),
        "manifest_path": str(manifest_path.resolve()),
        "library_root": str(library_root.resolve()) if library_root else None,
        "deep": deep,
        "counts": {
            "entries": len(entries),
            "with_document_number": sum(1 for entry in entries if entry["signals"]["document_numbers"]),
            "with_edition_token": sum(1 for entry in entries if entry["signals"]["edition_tokens"]),
            "unreadable": len(unreadable),
        },
        "unreadable": unreadable,
        "entries": entries,
    }


def index_by_document_number(baseline: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    index: dict[str, list[dict[str, Any]]] = {}
    for entry in baseline["entries"]:
        for number in entry["signals"]["document_numbers"]:
            index.setdefault(number, []).append(entry)
    return index


def index_by_series_key(baseline: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    index: dict[str, list[dict[str, Any]]] = {}
    for entry in baseline["entries"]:
        key = entry["signals"]["series_key"]
        if key:
            index.setdefault(key, []).append(entry)
    return index
