"""Section-aware text comparison between two robot-readable documents.

The diff answers "what text changed", not "what obligation changed". Reading
obligation out of a diff is a human judgement and belongs downstream, in the
FSO guidance catalog, not here.
"""

from __future__ import annotations

import difflib
import re
from pathlib import Path
from typing import Any

from .common import parse_authority_header, read_text_file, sha256_text, utc_now


HEADING_PATTERNS = (
    r"^\s*§+\s*\d+\.\d+",
    r"^\s*\d+(?:\.\d+){0,3}\.?\s+\S{3,}",
    r"^\s*(?:SECTION|PART|APPENDIX|ANNEX|ENCLOSURE|CHAPTER|ATTACHMENT|TAB)\b[^\n]{0,80}$",
)
_HEADING_RE = tuple(re.compile(pattern, re.IGNORECASE) for pattern in HEADING_PATTERNS)

# Library header fields are metadata, not sections. A changed EFFECTIVE date is a
# first-class comparison signal and is reported separately from the section diff.
_HEADER_FIELD_LINE = re.compile(r"^\s*(?:TIER|STATUS|EFFECTIVE|DOC TYPE|BASIS)\s*:", re.IGNORECASE)

DEFAULT_DIFF_LINES = 40
FUZZY_HEADING_THRESHOLD = 0.8


def is_heading(line: str) -> bool:
    stripped = line.strip()
    if not 3 <= len(stripped) <= 120:
        return False
    if _HEADER_FIELD_LINE.match(line):
        return False
    if any(pattern.match(line) for pattern in _HEADING_RE):
        return True
    letters = [character for character in stripped if character.isalpha()]
    return len(letters) >= 3 and all(character.isupper() for character in letters)


def normalize_heading(heading: str) -> str:
    return " ".join(re.split(r"[^0-9A-Za-z]+", heading.casefold())).strip()


def split_sections(text: str) -> list[dict[str, Any]]:
    """Split into (heading, body) sections; fall back to pages, then one block."""
    lines = text.splitlines()
    sections: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    for line in lines:
        if is_heading(line):
            if current is not None:
                sections.append(current)
            current = {"heading": line.strip(), "lines": []}
        elif current is None:
            current = {"heading": "", "lines": [line]}
        else:
            current["lines"].append(line)
    if current is not None:
        sections.append(current)

    if len(sections) < 2:
        pages = text.split("\f")
        if len(pages) > 1:
            sections = [{"heading": f"page {number}", "lines": page.splitlines()} for number, page in enumerate(pages, 1)]
        else:
            sections = [{"heading": "", "lines": lines}]

    for index, section in enumerate(sections, 1):
        body = "\n".join(section["lines"]).strip("\n")
        section.update({
            "ordinal": index,
            "body": body,
            "characters": len(body),
            "body_sha256": sha256_text(body),
            "key": normalize_heading(section["heading"]) or f"__ordinal_{index}",
        })
    return sections


def _fuzzy_pairs(left: list[dict[str, Any]], right: list[dict[str, Any]]) -> list[tuple[int, int]]:
    pairs: list[tuple[int, int]] = []
    taken: set[int] = set()
    for left_index, left_section in enumerate(left):
        best_index, best_score = None, 0.0
        left_tokens = set(left_section["key"].split())
        if not left_tokens:
            continue
        for right_index, right_section in enumerate(right):
            if right_index in taken:
                continue
            right_tokens = set(right_section["key"].split())
            if not right_tokens:
                continue
            score = len(left_tokens & right_tokens) / len(left_tokens | right_tokens)
            if score > best_score:
                best_index, best_score = right_index, score
        if best_index is not None and best_score >= FUZZY_HEADING_THRESHOLD:
            taken.add(best_index)
            pairs.append((left_index, best_index))
    return pairs


def diff_documents(
    left_path: Path,
    right_path: Path,
    left_label: str | None = None,
    right_label: str | None = None,
    diff_lines: int = DEFAULT_DIFF_LINES,
) -> dict[str, Any]:
    left_text, right_text = read_text_file(left_path), read_text_file(right_path)
    left_sections, right_sections = split_sections(left_text), split_sections(right_text)

    left_by_key: dict[str, list[int]] = {}
    for index, section in enumerate(left_sections):
        left_by_key.setdefault(section["key"], []).append(index)
    matched: dict[int, int] = {}
    used_left: set[int] = set()
    for right_index, section in enumerate(right_sections):
        for left_index in left_by_key.get(section["key"], []):
            if left_index not in used_left:
                matched[right_index] = left_index
                used_left.add(left_index)
                break

    remaining_left = [section for index, section in enumerate(left_sections) if index not in used_left]
    remaining_right = [(index, section) for index, section in enumerate(right_sections) if index not in matched]
    for left_offset, right_offset in _fuzzy_pairs(remaining_left, [section for _, section in remaining_right]):
        left_index = left_sections.index(remaining_left[left_offset])
        right_index = remaining_right[right_offset][0]
        if left_index not in used_left and right_index not in matched:
            matched[right_index] = left_index
            used_left.add(left_index)

    results: list[dict[str, Any]] = []
    lines_added = lines_removed = 0

    for right_index, right_section in enumerate(right_sections):
        left_index = matched.get(right_index)
        if left_index is None:
            results.append({
                "status": "added",
                "heading": right_section["heading"],
                "right_ordinal": right_section["ordinal"],
                "right_characters": right_section["characters"],
            })
            lines_added += len(right_section["body"].splitlines())
            continue
        left_section = left_sections[left_index]
        if left_section["body_sha256"] == right_section["body_sha256"]:
            results.append({
                "status": "unchanged",
                "heading": right_section["heading"],
                "left_ordinal": left_section["ordinal"],
                "right_ordinal": right_section["ordinal"],
            })
            continue
        raw = list(difflib.unified_diff(
            left_section["body"].splitlines(),
            right_section["body"].splitlines(),
            fromfile=left_label or left_path.name,
            tofile=right_label or right_path.name,
            lineterm="",
            n=1,
        ))
        added = sum(1 for line in raw if line.startswith("+") and not line.startswith("+++"))
        removed = sum(1 for line in raw if line.startswith("-") and not line.startswith("---"))
        lines_added += added
        lines_removed += removed
        results.append({
            "status": "changed",
            "heading": right_section["heading"],
            "left_heading": left_section["heading"],
            "left_ordinal": left_section["ordinal"],
            "right_ordinal": right_section["ordinal"],
            "left_characters": left_section["characters"],
            "right_characters": right_section["characters"],
            "lines_added": added,
            "lines_removed": removed,
            "diff_excerpt": raw[:diff_lines],
            "diff_truncated": len(raw) > diff_lines,
        })

    for left_index, left_section in enumerate(left_sections):
        if left_index in used_left:
            continue
        results.append({
            "status": "removed",
            "heading": left_section["heading"],
            "left_ordinal": left_section["ordinal"],
            "left_characters": left_section["characters"],
        })
        lines_removed += len(left_section["body"].splitlines())

    left_header, right_header = parse_authority_header(left_text), parse_authority_header(right_text)
    header_changes = {
        field: {"left": left_header.get(field), "right": right_header.get(field)}
        for field in sorted(set(left_header) | set(right_header))
        if left_header.get(field) != right_header.get(field)
    }

    summary = {
        "sections_left": len(left_sections),
        "sections_right": len(right_sections),
        "unchanged": sum(1 for item in results if item["status"] == "unchanged"),
        "changed": sum(1 for item in results if item["status"] == "changed"),
        "added": sum(1 for item in results if item["status"] == "added"),
        "removed": sum(1 for item in results if item["status"] == "removed"),
        "lines_added": lines_added,
        "lines_removed": lines_removed,
    }
    summary["header_fields_changed"] = len(header_changes)
    summary["substantively_identical"] = (
        summary["changed"] == summary["added"] == summary["removed"] == 0 and not header_changes
    )

    return {
        "schema_version": "1.0",
        "generated_at": utc_now(),
        "left": {
            "label": left_label or left_path.name,
            "path": str(left_path.resolve()),
            "text_sha256": sha256_text(left_text),
            "characters": len(left_text),
        },
        "right": {
            "label": right_label or right_path.name,
            "path": str(right_path.resolve()),
            "text_sha256": sha256_text(right_text),
            "characters": len(right_text),
        },
        "header_changes": header_changes,
        "summary": summary,
        "sections": results,
    }
