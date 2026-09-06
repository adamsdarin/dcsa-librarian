from __future__ import annotations

import hashlib
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def run_id(suffix: str = "") -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"{stamp}-{suffix}" if suffix else stamp


def norm_path(value: object) -> str:
    return str(value or "").replace("\\", "/").lstrip("./")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path, block_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while block := handle.read(block_size):
            digest.update(block)
    return digest.hexdigest()


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def normalize_text(value: str) -> str:
    """Whitespace- and case-insensitive form used only for near-identity checks."""
    return re.sub(r"\s+", " ", value.replace("\f", " ")).strip().casefold()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def iter_jsonl(path: Path) -> Iterable[tuple[int, dict[str, Any]]]:
    with path.open(encoding="utf-8-sig") as handle:
        for number, raw in enumerate(handle, 1):
            if raw.strip():
                yield number, json.loads(raw)


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8", newline="\n")
    os.replace(temp, path)


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    count = 0
    with temp.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, separators=(",", ":")) + "\n")
            count += 1
    os.replace(temp, path)
    return count


def read_text_file(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


HEADER_PATTERNS = {
    "header_tier": r"(?mi)^TIER\s*:\s*(\d+)",
    "header_status": r"(?mi)^STATUS\s*:\s*([^\r\n]+)",
    "effective_date": r"(?mi)^EFFECTIVE\s*:\s*([^\r\n]+)",
    "document_type_header": r"(?mi)^DOC TYPE\s*:\s*([^\r\n]+)",
    "metadata_basis": r"(?mi)^BASIS\s*:\s*([^\r\n]+)",
}


def parse_authority_header(text: str) -> dict[str, Any]:
    """Read the DCSA Library robot-text header block. Same field set as the Archivist."""
    header = text[:8000]
    fields: dict[str, Any] = {}
    for key, pattern in HEADER_PATTERNS.items():
        match = re.search(pattern, header)
        if match:
            value = match.group(1).strip()
            fields[key] = int(value) if key == "header_tier" else value
    return fields
