"""Pair newly released documents against the library baseline.

A finding is a *proposal for human review*, never a decision. Each one records
the route that produced the pair, the signals behind it, and whether the
relationship is deterministic (reproducible from observable tokens) or inferred
(a similarity judgement). No confidence score is emitted: a score invites a
threshold, a threshold invites automation, and automating this step is exactly
what the Librarian and Archivist contracts forbid.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .baseline import index_by_document_number, index_by_series_key
from .common import (
    iter_jsonl,
    normalize_text,
    read_text_file,
    sha256_file,
    sha256_text,
    utc_now,
)
from .identity import compare_editions, jaccard, series_tokens, signals_for


# A series-key pairing on a one- or two-word key ("isl", "job aid") is noise.
MIN_SERIES_TOKENS = 3
# Title similarity needs enough words to mean anything.
MIN_TITLE_TOKENS = 4
DEFAULT_TITLE_THRESHOLD = 0.6
DEFAULT_MAX_MATCHES = 5

DETERMINISTIC = "deterministic"
INFERRED = "inferred"

NEXT_ACTIONS = {
    "identical": "Confirm whether the library already holds this exact content; if so no intake is needed.",
    "identical_after_normalization": "Compare formatting only; content is byte-equal after whitespace and case folding.",
    "newer_edition_candidate": "Obtain official evidence that the incumbent was withdrawn or replaced, then record a lifecycle decision.",
    "older_edition_candidate": "Candidate appears older than the library copy; verify before any intake.",
    "same_edition_candidate": "Same edition markers as the incumbent; check for a silent content revision.",
    "edition_undetermined": "Edition ordering could not be established from tokens; a human must read both documents.",
    "title_similar": "Similarity only. Confirm or reject the pairing by reading both documents.",
    "no_match": "No incumbent matched. Treat as a possible new document for Librarian intake review.",
}


def load_candidates(
    paths: list[Path],
    candidates_jsonl: Path | None = None,
    text_map: dict[str, Path] | None = None,
) -> list[dict[str, Any]]:
    """Build candidate records from local files and/or a Librarian candidates.jsonl."""
    text_map = text_map or {}
    candidates: list[dict[str, Any]] = []

    for path in paths:
        candidate: dict[str, Any] = {
            "candidate_id": path.name,
            "title": path.stem,
            "source_path": str(path.resolve()),
            "source_uri": None,
            "source_sha256": sha256_file(path) if path.is_file() else None,
        }
        _attach_text(candidate, text_map.get(path.name) or (path if path.suffix.casefold() == ".txt" else None))
        candidate["signals"] = signals_for(candidate["title"], candidate.get("text_header", ""))
        candidates.append(candidate)

    if candidates_jsonl is not None:
        for _, record in iter_jsonl(candidates_jsonl):
            name = str(record.get("inferred_filename") or record.get("url") or "unnamed")
            title = Path(name).stem or name
            candidate = {
                "candidate_id": name,
                "title": title,
                "source_path": record.get("downloaded_path"),
                "source_uri": record.get("url"),
                "source_sha256": record.get("sha256"),
                "librarian_status": record.get("status"),
                "authority_hint": record.get("authority_hint"),
                "anchor_text": record.get("anchor_text"),
            }
            _attach_text(candidate, text_map.get(name))
            basis_text = " ".join(filter(None, [candidate.get("anchor_text"), candidate.get("text_header", "")]))
            candidate["signals"] = signals_for(title, basis_text)
            candidates.append(candidate)

    return candidates


def _attach_text(candidate: dict[str, Any], text_path: Path | None) -> None:
    """Record extracted-text hashes when text is available, and say so when it is not.

    This project does not extract text from binary formats. Extraction is the
    Librarian/Archivist path; comparing a PDF's bytes against a robot text hash
    would be a false equivalence, so the absence is reported rather than papered over.
    """
    if text_path is None or not Path(text_path).is_file():
        candidate["text_available"] = False
        candidate["content_comparison"] = "unavailable_no_candidate_text"
        return
    text = read_text_file(Path(text_path))
    candidate["text_available"] = True
    candidate["text_path"] = str(Path(text_path).resolve())
    candidate["exact_text_sha256"] = sha256_text(text)
    candidate["normalized_text_sha256"] = sha256_text(normalize_text(text))
    candidate["text_header"] = text[:400].replace("\n", " ")
    candidate["content_comparison"] = "available"


def _pair(candidate: dict[str, Any], entry: dict[str, Any], route: str, extra: dict[str, Any]) -> dict[str, Any]:
    candidate_signals, entry_signals = candidate["signals"], entry["signals"]
    shared_numbers = sorted(set(candidate_signals["document_numbers"]) & set(entry_signals["document_numbers"]))
    edition = compare_editions(entry_signals["edition_tokens"], candidate_signals["edition_tokens"])

    if candidate.get("exact_text_sha256") and candidate["exact_text_sha256"] == entry.get("exact_text_sha256"):
        relationship, basis = "identical", DETERMINISTIC
    elif candidate.get("normalized_text_sha256") and candidate["normalized_text_sha256"] == entry.get("normalized_text_sha256"):
        relationship, basis = "identical_after_normalization", DETERMINISTIC
    elif edition["order"] == 1:
        relationship = "newer_edition_candidate"
        basis = DETERMINISTIC if route == "document_number" else INFERRED
    elif edition["order"] == -1:
        relationship = "older_edition_candidate"
        basis = DETERMINISTIC if route == "document_number" else INFERRED
    elif edition["order"] == 0:
        relationship = "same_edition_candidate"
        basis = DETERMINISTIC if route == "document_number" else INFERRED
    elif route == "title_similarity":
        relationship, basis = "title_similar", INFERRED
    else:
        relationship, basis = "edition_undetermined", INFERRED

    signals = {
        "match_route": route,
        "shared_document_numbers": shared_numbers,
        "candidate_document_numbers": candidate_signals["document_numbers"],
        "incumbent_document_numbers": entry_signals["document_numbers"],
        "candidate_series_key": candidate_signals["series_key"],
        "incumbent_series_key": entry_signals["series_key"],
        "edition_order": edition,
        "candidate_edition_tokens": [token["raw"] for token in candidate_signals["edition_tokens"]],
        "incumbent_edition_tokens": [token["raw"] for token in entry_signals["edition_tokens"]],
    }
    signals.update(extra)

    return {
        "finding_id": f"{candidate['candidate_id']}::{entry['document_id']}",
        "candidate_id": candidate["candidate_id"],
        "candidate_title": candidate["title"],
        "candidate_source_uri": candidate.get("source_uri"),
        "candidate_source_sha256": candidate.get("source_sha256"),
        "incumbent_document_id": entry["document_id"],
        "incumbent_title": entry["title"],
        "incumbent_robot_text_path": entry.get("robot_text_path"),
        "incumbent_current_status": entry.get("current_status"),
        "incumbent_authority_role": entry.get("authority_role"),
        "incumbent_answer_eligibility": entry.get("answer_eligibility"),
        "relationship": relationship,
        "basis": basis,
        "signals": signals,
        "content_comparison": candidate.get("content_comparison", "unavailable_no_candidate_text"),
        "disposition": "proposed_for_human_review",
        "recommended_next_action": NEXT_ACTIONS[relationship],
    }


def _rank(finding: dict[str, Any]) -> tuple[Any, ...]:
    relationship_order = [
        "identical", "identical_after_normalization", "newer_edition_candidate",
        "same_edition_candidate", "older_edition_candidate", "edition_undetermined", "title_similar",
    ]
    return (
        finding["basis"] != DETERMINISTIC,
        relationship_order.index(finding["relationship"]),
        -finding["signals"].get("title_similarity", 0.0),
        finding["incumbent_document_id"],
    )


def compare_candidates(
    baseline: dict[str, Any],
    candidates: list[dict[str, Any]],
    title_threshold: float = DEFAULT_TITLE_THRESHOLD,
    max_matches: int = DEFAULT_MAX_MATCHES,
) -> dict[str, Any]:
    by_number = index_by_document_number(baseline)
    by_series = index_by_series_key(baseline)
    entries = baseline["entries"]

    findings: list[dict[str, Any]] = []
    unmatched: list[dict[str, Any]] = []
    suppressed: list[dict[str, Any]] = []

    for candidate in candidates:
        signals = candidate["signals"]
        numbers = set(signals["document_numbers"])
        seen: dict[str, dict[str, Any]] = {}

        for number in sorted(numbers):
            for entry in by_number.get(number, []):
                seen.setdefault(entry["document_id"], _pair(candidate, entry, "document_number", {}))

        if numbers:
            # A candidate that carries an official number is identified by it.
            # Pairing it with a differently-numbered document by title similarity
            # would manufacture a supersession between two documents that both
            # remain in force - the ISL series is the standing example.
            suppressed.append({
                "candidate_id": candidate["candidate_id"],
                "reason": "document_number_present_title_routes_suppressed",
                "document_numbers": sorted(numbers),
            })
        else:
            series = signals["series_key"]
            if series and len(series.split()) >= MIN_SERIES_TOKENS:
                for entry in by_series.get(series, []):
                    seen.setdefault(entry["document_id"], _pair(candidate, entry, "series_key", {"series_key_exact": True}))

            candidate_tokens = series_tokens(candidate["title"])
            if len(candidate_tokens) >= MIN_TITLE_TOKENS:
                for entry in entries:
                    if entry["document_id"] in seen or entry["signals"]["document_numbers"]:
                        continue
                    entry_tokens = series_tokens(entry["title"])
                    if len(entry_tokens) < MIN_TITLE_TOKENS:
                        continue
                    score = jaccard(candidate_tokens, entry_tokens)
                    if score >= title_threshold:
                        seen[entry["document_id"]] = _pair(
                            candidate, entry, "title_similarity", {"title_similarity": round(score, 3)}
                        )

        matches = sorted(seen.values(), key=_rank)[:max_matches]
        if matches:
            findings.extend(matches)
        else:
            unmatched.append({
                "candidate_id": candidate["candidate_id"],
                "candidate_title": candidate["title"],
                "candidate_source_uri": candidate.get("source_uri"),
                "relationship": "no_match",
                "basis": DETERMINISTIC,
                "signals": {
                    "candidate_document_numbers": signals["document_numbers"],
                    "candidate_series_key": signals["series_key"],
                },
                "content_comparison": candidate.get("content_comparison", "unavailable_no_candidate_text"),
                "disposition": "proposed_for_human_review",
                "recommended_next_action": NEXT_ACTIONS["no_match"],
            })

    counts: dict[str, int] = {}
    for finding in findings:
        counts[finding["relationship"]] = counts.get(finding["relationship"], 0) + 1

    return {
        "schema_version": "1.0",
        "generated_at": utc_now(),
        "publication_performed": False,
        "decisions_written": False,
        "baseline": {
            "manifest_path": baseline.get("manifest_path"),
            "generated_at": baseline.get("generated_at"),
            "entries": baseline["counts"]["entries"],
            "deep": baseline.get("deep", False),
        },
        "settings": {"title_threshold": title_threshold, "max_matches": max_matches},
        "counts": {
            "candidates": len(candidates),
            "candidates_with_matches": len({finding["candidate_id"] for finding in findings}),
            "candidates_without_matches": len(unmatched),
            "findings": len(findings),
            "deterministic_findings": sum(1 for finding in findings if finding["basis"] == DETERMINISTIC),
            "inferred_findings": sum(1 for finding in findings if finding["basis"] == INFERRED),
            "content_comparison_unavailable": sum(
                1 for finding in findings if finding["content_comparison"] != "available"
            ),
            "by_relationship": counts,
        },
        "findings": findings,
        "unmatched": unmatched,
        "suppressed_routes": suppressed,
    }
