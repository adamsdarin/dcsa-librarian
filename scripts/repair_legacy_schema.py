from __future__ import annotations

import argparse
import collections
import json
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path


REQUIRED = {"document_id", "collection_id", "authority_tier", "current_status", "human_source_path", "robot_text_path"}
MANIFEST_REL = Path("ROBOT_READABLE_DIRECTORY/MANIFESTS/documents.jsonl")
RELATIONSHIPS_REL = Path("ROBOT_READABLE_DIRECTORY/MANIFESTS/relationships.jsonl")


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl_atomic(path: Path, rows: list[dict]) -> None:
    temporary = path.with_suffix(path.suffix + ".publishing")
    temporary.write_text("".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in rows), encoding="utf-8", newline="\n")
    os.replace(temporary, path)


def normalize_manifest(records: list[dict]) -> tuple[list[dict], collections.Counter]:
    output: list[dict] = []
    changes: collections.Counter[str] = collections.Counter()
    for source in records:
        row = dict(source)
        if "document_id" not in row and row.get("id"):
            row["document_id"] = row["id"]
            changes["id_to_document_id"] += 1
        if "collection_id" not in row:
            row["collection_id"] = "cdse_resources" if str(row.get("document_id", "")).startswith("CDSE_") else "legacy_unclassified"
            changes["collection_id_added"] += 1
        if "authority_tier" not in row and row.get("tier") is not None:
            row["authority_tier"] = row["tier"]
            changes["tier_to_authority_tier"] += 1
        if "human_source_path" not in row and row.get("human_path"):
            row["human_source_path"] = row["human_path"]
            changes["human_path_to_human_source_path"] += 1
        if "robot_text_path" not in row and row.get("robot_path"):
            row["robot_text_path"] = row["robot_path"]
            changes["robot_path_to_robot_text_path"] += 1
        if "current_status" not in row:
            row["current_status"] = "current_or_verify"
            row["current_status_basis"] = "legacy_record_normalized_without_lifecycle_inference"
            changes["current_status_added_unresolved"] += 1
        missing = REQUIRED - row.keys()
        if missing:
            raise ValueError(f"record cannot be normalized without inference: {row.get('document_id') or row.get('id')}: {sorted(missing)}")
        output.append(row)
    return output, changes


def normalize_relationships(records: list[dict], documents: list[dict]) -> tuple[list[dict], collections.Counter]:
    old_pairs = {
        (
            str(row.get("human_source_path") or row.get("human_readable_path") or "").replace("\\", "/"),
            str(row.get("robot_text_path") or row.get("robot_path") or "").replace("\\", "/"),
        )
        for row in records
    }
    output: list[dict] = []
    new_pairs: set[tuple[str, str]] = set()
    for row in documents:
        human = str(row["human_source_path"]).replace("\\", "/")
        robot = str(row["robot_text_path"]).replace("\\", "/")
        pair = (human, robot)
        relationship = {
            "document_id": str(row["document_id"]),
            "human_readable_path": human,
            "human_source_path": human,
            "robot_text_path": robot,
            "exists_in_both": True,
            "relationship": "machine_readable_representation_of",
            "pair_status": "regenerated_from_validated_document_manifest",
        }
        source_url = row.get("canonical_source_url") or row.get("source_url")
        if source_url:
            relationship["source_url"] = source_url
        output.append(relationship)
        new_pairs.add(pair)
    changes: collections.Counter[str] = collections.Counter()
    changes["old_relationship_rows"] = len(records)
    changes["new_relationship_rows"] = len(output)
    changes["old_orphan_pairs_removed_from_active_metadata"] = len(old_pairs - new_pairs)
    changes["manifest_pairs_added_to_relationship_metadata"] = len(new_pairs - old_pairs)
    return output, changes


def validate(documents: list[dict], relationships: list[dict], root: Path) -> dict:
    errors: list[dict] = []
    pairs = {(str(row["document_id"]), str(row["human_source_path"]).replace("\\", "/"), str(row["robot_text_path"]).replace("\\", "/")) for row in documents}
    for line, row in enumerate(documents, 1):
        missing = REQUIRED - row.keys()
        if missing:
            errors.append({"type": "manifest_missing_fields", "line": line, "fields": sorted(missing)})
            continue
        for field in ("human_source_path", "robot_text_path"):
            path = root / str(row[field]).replace("/", os.sep)
            if not path.is_file():
                errors.append({"type": "missing_pair_file", "line": line, "field": field, "path": str(path)})
    for line, row in enumerate(relationships, 1):
        pair = (str(row.get("document_id")), str(row.get("human_source_path", "")).replace("\\", "/"), str(row.get("robot_text_path", "")).replace("\\", "/"))
        if pair not in pairs:
            errors.append({"type": "broken_relationship", "line": line, "document_id": row.get("document_id")})
    return {"valid": not errors, "errors": errors[:100], "error_count": len(errors), "manifest_records": len(documents), "relationships": len(relationships)}


def prepare(root: Path) -> tuple[list[dict], list[dict], dict]:
    documents, manifest_changes = normalize_manifest(load_jsonl(root / MANIFEST_REL))
    relationships, relationship_changes = normalize_relationships(load_jsonl(root / RELATIONSHIPS_REL), documents)
    validation = validate(documents, relationships, root)
    report = {
        "status": "ready" if validation["valid"] else "blocked",
        "manifest_changes": dict(manifest_changes),
        "relationship_changes": dict(relationship_changes),
        "validation": validation,
        "semantic_policy": "Missing lifecycle values become current_or_verify; no current, superseded, or historical status is inferred.",
        "source_artifacts_modified": False,
    }
    return documents, relationships, report


def publish(root: Path, approved_by: str) -> dict:
    documents, relationships, report = prepare(root)
    if not report["validation"]["valid"]:
        raise RuntimeError(report)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    rollback = root / "OPERATIONS" / "QUARANTINE" / "SCHEMA_REPAIR_ROLLBACK" / timestamp
    rollback.mkdir(parents=True, exist_ok=False)
    for relative in (MANIFEST_REL, RELATIONSHIPS_REL):
        source = root / relative
        target = rollback / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    write_jsonl_atomic(root / MANIFEST_REL, documents)
    write_jsonl_atomic(root / RELATIONSHIPS_REL, relationships)
    post_documents = load_jsonl(root / MANIFEST_REL)
    post_relationships = load_jsonl(root / RELATIONSHIPS_REL)
    post = validate(post_documents, post_relationships, root)
    if not post["valid"]:
        shutil.copy2(rollback / MANIFEST_REL, root / MANIFEST_REL)
        shutil.copy2(rollback / RELATIONSHIPS_REL, root / RELATIONSHIPS_REL)
        raise RuntimeError(f"post-repair validation failed and rollback was restored: {post}")
    receipt = {
        "schema_version": "1.0",
        "status": "published",
        "published_utc": datetime.now(timezone.utc).isoformat(),
        "approved_by": approved_by,
        "rollback_snapshot": str(rollback),
        "preview": report,
        "post_validation": post,
    }
    (rollback / "REPAIR_RECEIPT.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8", newline="\n")
    return receipt


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--library", type=Path, required=True)
    parser.add_argument("--publish", action="store_true")
    parser.add_argument("--approved-by", default="")
    args = parser.parse_args()
    if args.publish and not args.approved_by:
        parser.error("--approved-by is required with --publish")
    root = args.library.resolve()
    result = publish(root, args.approved_by) if args.publish else prepare(root)[2]
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
