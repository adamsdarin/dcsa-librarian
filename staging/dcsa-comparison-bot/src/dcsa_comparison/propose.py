"""Turn reviewed findings into proposals for the downstream planes.

Two outputs, neither of which is applied here:

1. `proposed-metadata-decisions.json` - conforms to the DCSA Archivist's
   METADATA_DECISIONS schema, for a human to review and the Archivist's own
   approval gate to apply.
2. `variance-handoff.json` - an input feed for the FSO guidance catalog, which
   owns the findings/supersession register. This project never writes that
   register; duplicating it would create two sources of truth.

A token-derived pairing is not lifecycle evidence. Every proposal says so in
its own note, and the emitter refuses to fabricate an evidence URL it does not
have.
"""

from __future__ import annotations

from typing import Any

from .common import utc_now


# Only a *newer* edition changes the incumbent's lifecycle. An identical or
# older candidate is an intake question for the Librarian, not a lifecycle
# decision about a library record.
ELIGIBLE_RELATIONSHIPS = {"newer_edition_candidate": "superseded"}

INELIGIBLE_REASONS = {
    "identical": "candidate duplicates existing content; intake question, not a lifecycle change",
    "identical_after_normalization": "candidate duplicates existing content after normalization",
    "older_edition_candidate": "candidate is the older edition; incumbent lifecycle unchanged",
    "same_edition_candidate": "same edition markers; no lifecycle change implied",
    "edition_undetermined": "edition ordering not established; a human must read both documents",
    "title_similar": "similarity only; pairing itself is unconfirmed",
    "no_match": "no incumbent to decide about",
}

REQUIRED_DECISION_FIELDS = (
    "source_document_id", "robot_text_path", "decision", "verified_utc", "verified_by", "evidence", "note",
)


def _note_for(finding: dict[str, Any]) -> str:
    signals = finding["signals"]
    order = signals.get("edition_order", {})
    parts = [
        f"Proposed by dcsa-comparison-bot from {finding['basis']} identity signals, not from official lifecycle evidence.",
        f"Route: {signals.get('match_route')}.",
    ]
    if signals.get("shared_document_numbers"):
        parts.append(f"Shared document number(s): {', '.join(signals['shared_document_numbers'])}.")
    if order.get("kind"):
        parts.append(
            f"Edition token ({order['kind']}) moves from {order.get('left')!r} on the library copy "
            f"to {order.get('right')!r} on the candidate {finding['candidate_title']!r}."
        )
    if finding.get("content_comparison") != "available":
        parts.append("Robot text for the candidate was not available, so no content diff supports this pairing.")
    parts.append(
        "Before this decision is applied, a reviewer must attach official evidence that the library copy "
        "was withdrawn, replaced, or reissued. A filename or version token is not that evidence."
    )
    return " ".join(parts)


def _evidence_for(finding: dict[str, Any]) -> list[dict[str, str]]:
    uri = finding.get("candidate_source_uri")
    if not uri or not str(uri).startswith("https://"):
        return []
    return [{
        "url": str(uri),
        "observation": (
            f"Candidate {finding['candidate_title']!r} was located at this official source URL. "
            "This records where the candidate was found; it is not, on its own, evidence that the "
            "library copy was superseded."
        ),
        "evidence_type": "candidate_location_only",
    }]


def build_proposals(
    report: dict[str, Any],
    reviewer: str,
    accepted_finding_ids: set[str] | None = None,
    include_inferred: bool = False,
) -> dict[str, Any]:
    if not reviewer or not reviewer.strip():
        raise ValueError("a named human reviewer is required; the bot must not sign a decision as itself")

    decisions: list[dict[str, Any]] = []
    blocked: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    handoff: list[dict[str, Any]] = []
    now = utc_now()

    for finding in report.get("findings", []):
        if accepted_finding_ids is not None and finding["finding_id"] not in accepted_finding_ids:
            continue
        relationship = finding["relationship"]

        handoff.append({
            "finding_id": finding["finding_id"],
            "incumbent_document_id": finding["incumbent_document_id"],
            "incumbent_title": finding["incumbent_title"],
            "incumbent_authority_role": finding.get("incumbent_authority_role"),
            "candidate_title": finding["candidate_title"],
            "candidate_source_uri": finding.get("candidate_source_uri"),
            "relationship": relationship,
            "basis": finding["basis"],
            "edition_order": finding["signals"].get("edition_order"),
            "content_comparison": finding.get("content_comparison"),
        })

        decision_value = ELIGIBLE_RELATIONSHIPS.get(relationship)
        if decision_value is None:
            skipped.append({
                "finding_id": finding["finding_id"],
                "relationship": relationship,
                "reason": INELIGIBLE_REASONS.get(relationship, "relationship carries no lifecycle consequence"),
            })
            continue
        if finding["basis"] != "deterministic" and not include_inferred:
            skipped.append({
                "finding_id": finding["finding_id"],
                "relationship": relationship,
                "reason": "inferred pairing withheld; re-run with --include-inferred to propose it explicitly",
            })
            continue
        if not finding.get("incumbent_robot_text_path"):
            blocked.append({"finding_id": finding["finding_id"], "reason": "incumbent has no robot_text_path"})
            continue

        evidence = _evidence_for(finding)
        decision = {
            "source_document_id": finding["incumbent_document_id"],
            "robot_text_path": finding["incumbent_robot_text_path"],
            "decision": decision_value,
            "verified_utc": now,
            "verified_by": reviewer.strip(),
            "evidence": evidence,
            "note": _note_for(finding),
            "proposed_by": "dcsa-comparison-bot",
            "proposal_basis": finding["basis"],
            "proposal_finding_id": finding["finding_id"],
            "requires_official_lifecycle_evidence": True,
        }
        if not evidence:
            blocked.append({
                "finding_id": finding["finding_id"],
                "reason": "no https candidate source URL; the Archivist schema requires at least one evidence URL",
                "draft_decision": decision,
            })
            continue
        decisions.append(decision)

    return {
        "schema_version": "1.0",
        "proposal_state": "proposed_not_applied",
        "generated_at": now,
        "generated_by": "dcsa-comparison-bot",
        "reviewer": reviewer.strip(),
        "include_inferred": include_inferred,
        "counts": {
            "proposed_decisions": len(decisions),
            "blocked": len(blocked),
            "skipped": len(skipped),
            "handoff_rows": len(handoff),
        },
        "archivist_metadata_decisions": {"schema_version": "1.0", "decisions": decisions},
        "blocked": blocked,
        "skipped": skipped,
        "fso_guidance_watch_handoff": handoff,
    }


def check_decisions(payload: dict[str, Any]) -> list[str]:
    """Minimal structural check against the Archivist METADATA_DECISIONS contract."""
    problems: list[str] = []
    allowed = {"verified_current", "superseded", "historical", "exclude"}
    for index, decision in enumerate(payload.get("archivist_metadata_decisions", {}).get("decisions", [])):
        for field in REQUIRED_DECISION_FIELDS:
            if field not in decision:
                problems.append(f"decision[{index}]: missing {field}")
        if decision.get("decision") not in allowed:
            problems.append(f"decision[{index}]: decision must be one of {sorted(allowed)}")
        if not str(decision.get("robot_text_path", "")).startswith("ROBOT_READABLE_DIRECTORY/"):
            problems.append(f"decision[{index}]: robot_text_path must stay under ROBOT_READABLE_DIRECTORY/")
        evidence = decision.get("evidence") or []
        if not evidence:
            problems.append(f"decision[{index}]: at least one evidence entry is required")
        for entry in evidence:
            if not str(entry.get("url", "")).startswith("https://"):
                problems.append(f"decision[{index}]: evidence url must be https")
    return problems
