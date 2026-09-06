"""Deterministic identity signals for DCSA documents.

Nothing here decides that a document is superseded. It extracts observable,
reproducible signals - official document numbers, edition tokens, and a
normalized series key - so that a human reviewer can see exactly why two
records were paired. Every function is pure and total: unparseable input
yields an empty signal, never a guess.
"""

from __future__ import annotations

import re
from typing import Any


# ---------------------------------------------------------------------------
# Official document numbers
# ---------------------------------------------------------------------------

# Each entry is (kind, pattern). The pattern must expose the identifying parts
# as groups; they are joined with "-" to form the normalized number.
DOCUMENT_NUMBER_PATTERNS: list[tuple[str, str]] = [
    ("cfr", r"\b(\d{1,2})\s*C\.?\s?F\.?\s?R\.?\s*(?:part\s*)?(\d{3,4})\b"),
    ("dod", r"\bD\s?o\s?D\s?([IDM])\s*-?\s*(\d{4}\.\d{1,2}(?:\s?-\s?[A-Z])?)"),
    ("sead", r"\bSEAD\s*-?\s*(\d{1,2})\b"),
    ("isl", r"\bISL\s*-?\s*(\d{4})\s*-\s*(\d{2})\b"),
    ("nist-sp", r"\bSP\s*-?\s*(\d{3})\s*-\s*(\d{1,3}[A-Za-z]?)(?![0-9])"),
    ("icd", r"\bICD\s*-?\s*(\d{3})\b"),
    ("ics", r"\bICS\s*-?\s*(\d{3})\b"),
    ("eo", r"\bE\.?\s?O\.?\s*(\d{5})\b"),
    ("cnssi", r"\bCNSSI\s*-?\s*(\d{4})\b"),
    ("dfars", r"\bDFARS\s*(\d{3}\.\d{3}\s*-\s*\d{4})\b"),
    ("far", r"\bFAR\s*(\d{2}\.\d{3}\s*-\s*\d{1,2})\b"),
]


# ---------------------------------------------------------------------------
# Edition tokens, in descending authority. A pair is only ordered by tokens of
# the SAME kind; mixing a version against a date is not an ordering.
# ---------------------------------------------------------------------------

EDITION_KIND_PRIORITY = ("version", "revision", "edition_date", "year")

MONTHS = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}

_VERSION = re.compile(r"\bv(?:er|ersion)?\.?\s*(\d+(?:\.\d+){1,3})\b", re.IGNORECASE)
_REVISION = re.compile(r"\b(?:rev(?:ision)?|change|chg)\.?\s*(\d{1,2})\b", re.IGNORECASE)
# NIST-style compact revision suffix: "SP 800-61r3" survives run-splitting as "61 r 3".
_REVISION_SUFFIX = re.compile(r"(?<=\d)\s*r\.?\s*(\d{1,2})\b", re.IGNORECASE)
_DATE_ISO = re.compile(r"\b(20\d{2})\s*[-_]\s*(\d{1,2})(?:\s*[-_]\s*(\d{1,2}))?\b")
_DATE_US = re.compile(r"\b(\d{1,2})\s*[-/]\s*(\d{1,2})\s*[-/]\s*(20\d{2})\b")
_DATE_COMPACT = re.compile(r"\b(20\d{2})(0\d|1[0-2])([0-2]\d|3[01])\b")
_DATE_MONTH = re.compile(
    r"\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s*,?\s*(\d{1,2})?\s*,?\s*((?:19|20)\d{2})\b",
    re.IGNORECASE,
)
_YEAR = re.compile(r"\b((?:19|20)\d{2})\b")

# Publication artifacts that carry no identity.
NOISE_TOKENS = frozenset(
    {"final", "draft", "clean", "signed", "copy", "508", "compliant", "accessible", "pdf", "txt", "docx", "ocr"}
)


def split_runs(text: str) -> str:
    """Insert separators at case and letter/digit boundaries.

    'revisedMay2024' -> 'revised May 2024', 'DoDI5205.16' -> 'DoDI 5205.16'.
    Filenames in this corpus routinely concatenate an edition onto a title;
    without this step those editions are invisible to every pattern below.
    """
    text = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", text)
    text = re.sub(r"(?<=[A-Za-z])(?=\d)", " ", text)
    text = re.sub(r"(?<=\d)(?=[A-Za-z])", " ", text)
    return re.sub(r"[_]+", " ", text)


def document_numbers(text: str) -> list[str]:
    """Normalized official document numbers found in the text, sorted and deduped."""
    found: set[str] = set()
    # Scan the raw text and the run-split text. Mixed-case acronyms ("DoDI") read
    # correctly raw; concatenated ones ("DoDI5205.16") only read once split.
    for source in (text, split_runs(text)):
        for kind, pattern in DOCUMENT_NUMBER_PATTERNS:
            for match in re.finditer(pattern, source, re.IGNORECASE):
                parts = [re.sub(r"[\s-]+", "", group) for group in match.groups() if group]
                if parts:
                    found.add(f"{kind}:{'-'.join(parts).casefold()}")
    return sorted(found)


def _as_date(year: int, month: int | None, day: int | None) -> tuple[int, int, int]:
    return (year, month or 0, day or 0)


def edition_tokens(text: str) -> list[dict[str, Any]]:
    """Every edition marker in the text, with the span it occupied.

    Spans are returned against the run-split form so callers can subtract them
    from the title when deriving a series key.
    """
    prepared = split_runs(text)
    tokens: list[dict[str, Any]] = []

    for match in _VERSION.finditer(prepared):
        value = tuple(int(part) for part in match.group(1).split("."))
        tokens.append({"kind": "version", "raw": match.group(0).strip(), "value": list(value), "span": list(match.span())})
    for pattern in (_REVISION, _REVISION_SUFFIX):
        for match in pattern.finditer(prepared):
            tokens.append({"kind": "revision", "raw": match.group(0).strip(), "value": int(match.group(1)), "span": list(match.span())})
    for match in _DATE_COMPACT.finditer(prepared):
        value = _as_date(int(match.group(1)), int(match.group(2)), int(match.group(3)))
        tokens.append({"kind": "edition_date", "raw": match.group(0), "value": list(value), "span": list(match.span())})
    for match in _DATE_ISO.finditer(prepared):
        month = int(match.group(2))
        if not 1 <= month <= 12:
            continue
        day = int(match.group(3)) if match.group(3) else None
        tokens.append({
            "kind": "edition_date", "raw": match.group(0),
            "value": list(_as_date(int(match.group(1)), month, day)), "span": list(match.span()),
        })
    for match in _DATE_US.finditer(prepared):
        month, day = int(match.group(1)), int(match.group(2))
        if not 1 <= month <= 12 or not 1 <= day <= 31:
            continue
        tokens.append({
            "kind": "edition_date", "raw": match.group(0),
            "value": list(_as_date(int(match.group(3)), month, day)), "span": list(match.span()),
        })
    for match in _DATE_MONTH.finditer(prepared):
        month = MONTHS[match.group(1).casefold()[:3]]
        day = int(match.group(2)) if match.group(2) else None
        tokens.append({
            "kind": "edition_date", "raw": match.group(0).strip(),
            "value": list(_as_date(int(match.group(3)), month, day)), "span": list(match.span()),
        })

    covered = [tuple(token["span"]) for token in tokens]
    for match in _YEAR.finditer(prepared):
        if any(start <= match.start() and match.end() <= end for start, end in covered):
            continue
        tokens.append({"kind": "year", "raw": match.group(0), "value": int(match.group(1)), "span": list(match.span())})

    tokens.sort(key=lambda token: (EDITION_KIND_PRIORITY.index(token["kind"]), token["span"][0]))
    return tokens


def strongest_tokens(tokens: list[dict[str, Any]]) -> dict[str, Any]:
    """The highest-value token of each kind, keyed by kind."""
    best: dict[str, Any] = {}
    for token in tokens:
        current = best.get(token["kind"])
        if current is None or _token_value(token) > _token_value(current):
            best[token["kind"]] = token
    return best


def _token_value(token: dict[str, Any]) -> Any:
    value = token["value"]
    return tuple(value) if isinstance(value, list) else (value,)


def compare_editions(left: list[dict[str, Any]], right: list[dict[str, Any]]) -> dict[str, Any]:
    """Order two documents by edition, or report that they cannot be ordered.

    Returns {'order': -1|0|1|None, 'kind': str|None, 'left': raw, 'right': raw}.
    `order` is 1 when `right` is the later edition. None means the pair shares
    no comparable token kind - an absence of evidence, reported as such.
    """
    left_best, right_best = strongest_tokens(left), strongest_tokens(right)
    for kind in EDITION_KIND_PRIORITY:
        if kind not in left_best or kind not in right_best:
            continue
        left_value, right_value = _token_value(left_best[kind]), _token_value(right_best[kind])
        if left_value == right_value:
            continue
        return {
            "order": 1 if right_value > left_value else -1,
            "kind": kind,
            "left": left_best[kind]["raw"],
            "right": right_best[kind]["raw"],
        }
    shared = [kind for kind in EDITION_KIND_PRIORITY if kind in left_best and kind in right_best]
    if shared:
        kind = shared[0]
        return {"order": 0, "kind": kind, "left": left_best[kind]["raw"], "right": right_best[kind]["raw"]}
    return {"order": None, "kind": None, "left": None, "right": None}


def series_key(text: str) -> str:
    """The title with edition markers and publication artifacts removed."""
    prepared = split_runs(text)
    spans = sorted((tuple(token["span"]) for token in edition_tokens(text)), reverse=True)
    for start, end in spans:
        prepared = prepared[:start] + " " + prepared[end:]
    words = re.split(r"[^0-9A-Za-z]+", prepared.casefold())
    kept = [word for word in words if word and word not in NOISE_TOKENS]
    return " ".join(kept)


def series_tokens(text: str) -> frozenset[str]:
    return frozenset(series_key(text).split())


def jaccard(left: frozenset[str], right: frozenset[str]) -> float:
    if not left or not right:
        return 0.0
    return len(left & right) / len(left | right)


def signals_for(title: str, extra_text: str = "") -> dict[str, Any]:
    """The full deterministic signal set for one document."""
    basis = f"{title} {extra_text}".strip()
    tokens = edition_tokens(basis)
    return {
        "title": title,
        "document_numbers": document_numbers(basis),
        "edition_tokens": tokens,
        "series_key": series_key(title),
        "series_token_count": len(series_tokens(title)),
    }
