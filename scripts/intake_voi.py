from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from pypdf import PdfReader


DOC_ID = "dcsa-voi-2026-08-voi"
HUMAN_REL = Path("HUMAN_READABLE_DIRECTORY/INDUSTRIAL_SECURITY/VOICE_OF_INDUSTRY_(VOI)/2026-08_VOI.pdf")
ROBOT_REL = Path("ROBOT_READABLE_DIRECTORY/TEXT/INDUSTRIAL_SECURITY/VOICE_OF_INDUSTRY_(VOI)/2026-08_VOI.txt")
MANIFEST_REL = Path("ROBOT_READABLE_DIRECTORY/MANIFESTS/documents.jsonl")
RELATIONSHIPS_REL = Path("ROBOT_READABLE_DIRECTORY/MANIFESTS/relationships.jsonl")
INDEX_REL = Path("LOCAL_INDEXES/DCSA_GENERAL_FTS.sqlite")
CATALOG_REL = Path("ROBOT_READABLE_DIRECTORY/CATALOG/COLLECTIONS.json")
EXPECTED_SOURCE_SHA256 = "55d841c6812f0bfce8094071844bb8e5c80806de2671bb92ccc079ee652d90c7"
SOURCE_URL = "https://www.dcsa.mil/Portals/128/Documents/CTP/tools/260831%20VOI%20Newsletter.pdf"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl_atomic(path: Path, rows: list[dict]) -> None:
    temp = path.with_suffix(path.suffix + ".publishing")
    temp.write_text("".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in rows), encoding="utf-8", newline="\n")
    os.replace(temp, path)


def extract_robot_text(source: Path, generated_utc: str) -> tuple[str, int]:
    reader = PdfReader(source)
    pages = [page.extract_text() or "" for page in reader.pages]
    if len(pages) != 10 or "August 2026" not in pages[0]:
        raise ValueError("PDF identity check failed: expected readable 10-page August 2026 VOI")
    body = [
        "MACHINE-READABLE TEXT COPY",
        "Source PDF: 2026-08_VOI.pdf",
        "Source path: HUMAN_READABLE_DIRECTORY\\INDUSTRIAL_SECURITY\\VOICE_OF_INDUSTRY_(VOI)\\2026-08_VOI.pdf",
        f"Canonical source URL: {SOURCE_URL}",
        f"Source SHA-256: {EXPECTED_SOURCE_SHA256}",
        f"Method: embedded PDF text extraction using pypdf; generated {generated_utc}.",
        "Use: search, retrieval, and analysis aid. Consult the source PDF for authoritative visual formatting and any extraction ambiguity.",
        f"Source page count: {len(pages)}",
        "Authority: Tier 7 DCSA newsletter; operational guidance/context, never independently authoritative.",
        "",
    ]
    for number, text in enumerate(pages, 1):
        body.extend(["\f", f"===== SOURCE PAGE {number} =====", "", text.rstrip(), ""])
    result = "\n".join(body).rstrip() + "\n"
    if len(result) < 10000:
        raise ValueError("extracted robot text is unexpectedly short")
    return result, len(pages)


def paths(root: Path) -> dict[str, Path]:
    return {
        "human": root / HUMAN_REL,
        "robot": root / ROBOT_REL,
        "manifest": root / MANIFEST_REL,
        "relationships": root / RELATIONSHIPS_REL,
        "index": root / INDEX_REL,
        "catalog": root / CATALOG_REL,
    }


def preview(root: Path, source: Path) -> dict:
    target = paths(root)
    for name in ("manifest", "relationships", "index", "catalog"):
        if not target[name].is_file():
            raise FileNotFoundError(target[name])
    if sha256(source) != EXPECTED_SOURCE_SHA256:
        raise ValueError("quarantined source SHA-256 does not match the browser-verified PDF")
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d UTC")
    text, page_count = extract_robot_text(source, generated)
    documents = load_jsonl(target["manifest"])
    relationships = load_jsonl(target["relationships"])
    ids = [str(row.get("document_id")) for row in documents]
    with sqlite3.connect(f"file:{target['index'].as_posix()}?mode=ro", uri=True) as connection:
        integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
        indexed = connection.execute("SELECT count(*) FROM corpus WHERE document_id=?", (DOC_ID,)).fetchone()[0]
    return {
        "status": "already_present" if DOC_ID in ids else "ready",
        "document_id": DOC_ID,
        "source": str(source),
        "source_sha256": sha256(source),
        "source_bytes": source.stat().st_size,
        "page_count": page_count,
        "robot_text_bytes": len(text.encode("utf-8")),
        "robot_text_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "targets": {key: str(value) for key, value in target.items()},
        "preexisting": {
            "human": target["human"].exists(),
            "robot": target["robot"].exists(),
            "manifest_records": ids.count(DOC_ID),
            "relationship_records": sum(1 for row in relationships if row.get("document_id") == DOC_ID or row.get("human_readable_path") == HUMAN_REL.as_posix()),
            "index_records": indexed,
        },
        "index_integrity": integrity,
        "publication_scope": [str(HUMAN_REL), str(ROBOT_REL), str(MANIFEST_REL), str(RELATIONSHIPS_REL), str(INDEX_REL), str(CATALOG_REL)],
    }


def publish(root: Path, source: Path, approved_by: str) -> dict:
    report = preview(root, source)
    if report["status"] == "already_present" or any(report["preexisting"].values()):
        raise RuntimeError(f"refusing non-idempotent intake; target already exists: {report['preexisting']}")
    if report["index_integrity"] != "ok":
        raise RuntimeError("general FTS index failed integrity check")

    target = paths(root)
    now = datetime.now(timezone.utc)
    timestamp = now.strftime("%Y%m%dT%H%M%SZ")
    generated = now.strftime("%Y-%m-%d UTC")
    robot_text, page_count = extract_robot_text(source, generated)
    rollback = root / "OPERATIONS" / "QUARANTINE" / "VOI_INTAKE_ROLLBACK" / timestamp
    rollback.mkdir(parents=True, exist_ok=False)
    for name in ("manifest", "relationships", "index", "catalog"):
        relative = target[name].relative_to(root)
        destination = rollback / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(target[name], destination)

    target["human"].parent.mkdir(parents=True, exist_ok=True)
    target["robot"].parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target["human"])
    target["robot"].write_text(robot_text, encoding="utf-8", newline="\n")

    record = {
        "document_id": DOC_ID,
        "collection_id": "voi",
        "domain": "industrial_security",
        "human_source_path": HUMAN_REL.as_posix(),
        "robot_text_path": ROBOT_REL.as_posix(),
        "source_extension": ".pdf",
        "authority_tier": 7,
        "current_status": "current_or_verify",
        "representation_action": "newly_acquired_from_verified_official_source",
        "text_quality": "embedded_text_extracted",
        "source_exists": True,
        "machine_text_exists": True,
        "source_bytes": target["human"].stat().st_size,
        "machine_text_bytes": target["robot"].stat().st_size,
        "page_count": page_count,
        "mime_type": "application/pdf",
        "canonical_source_url": SOURCE_URL,
        "retrieved_utc": "2026-08-31T22:37:44Z",
        "published_utc": now.isoformat(),
        "approved_by": approved_by,
        "source_sha256": sha256(target["human"]),
        "robot_sha256": sha256(target["robot"]),
        "original_source_path": HUMAN_REL.as_posix(),
    }
    documents = load_jsonl(target["manifest"])
    insert_at = next((i + 1 for i, row in enumerate(documents) if row.get("document_id") == "dcsa-voi-2026-07-voi"), len(documents))
    documents.insert(insert_at, record)
    write_jsonl_atomic(target["manifest"], documents)

    relationship = {
        "document_id": DOC_ID,
        "human_readable_path": HUMAN_REL.as_posix(),
        "human_source_path": HUMAN_REL.as_posix(),
        "robot_text_path": ROBOT_REL.as_posix(),
        "exists_in_both": True,
        "relationship": "machine_readable_representation_of",
        "pair_status": "validated_official_source_intake",
        "source_url": SOURCE_URL,
        "source_sha256": record["source_sha256"],
        "robot_sha256": record["robot_sha256"],
    }
    relationships = load_jsonl(target["relationships"])
    rel_insert_at = next((i + 1 for i, row in enumerate(relationships) if row.get("human_readable_path") == "HUMAN_READABLE_DIRECTORY/INDUSTRIAL_SECURITY/VOICE_OF_INDUSTRY_(VOI)/2026-07_VOI.pdf"), len(relationships))
    relationships.insert(rel_insert_at, relationship)
    write_jsonl_atomic(target["relationships"], relationships)

    with sqlite3.connect(target["index"]) as connection:
        connection.execute("BEGIN IMMEDIATE")
        connection.execute(
            "INSERT INTO corpus(document_id,collection_id,domain,current_status,authority_tier,human_source_path,robot_text_path,content) VALUES(?,?,?,?,?,?,?,?)",
            (DOC_ID, "voi", "industrial_security", "current_or_verify", "7", HUMAN_REL.as_posix(), ROBOT_REL.as_posix(), robot_text),
        )
        if connection.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
            raise RuntimeError("FTS integrity failed after insertion")
        connection.commit()

    catalog = json.loads(target["catalog"].read_text(encoding="utf-8"))
    collection_rows = catalog if isinstance(catalog, list) else catalog.get("collections", [])
    voi = next(row for row in collection_rows if row.get("collection_id") == "voi")
    voi["document_count"] = sum(1 for row in documents if row.get("collection_id") == "voi")
    catalog_temp = target["catalog"].with_suffix(".json.publishing")
    catalog_temp.write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    os.replace(catalog_temp, target["catalog"])

    final = preview(root, source)
    expected = {"human": True, "robot": True, "manifest_records": 1, "relationship_records": 1, "index_records": 1}
    if final["preexisting"] != expected or final["index_integrity"] != "ok":
        raise RuntimeError(f"post-publication validation failed: {final}")
    receipt = {
        "schema_version": "1.0",
        "status": "published",
        "published_utc": now.isoformat(),
        "approved_by": approved_by,
        "document_id": DOC_ID,
        "source_url": SOURCE_URL,
        "source_sha256": record["source_sha256"],
        "robot_sha256": record["robot_sha256"],
        "human_path": HUMAN_REL.as_posix(),
        "robot_path": ROBOT_REL.as_posix(),
        "rollback_snapshot": str(rollback),
        "post_validation": final,
    }
    (rollback / "PUBLICATION_RECEIPT.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8", newline="\n")
    return receipt


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--library", type=Path, required=True)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--publish", action="store_true")
    parser.add_argument("--approved-by", default="")
    args = parser.parse_args()
    if args.publish and not args.approved_by:
        parser.error("--approved-by is required with --publish")
    result = publish(args.library.resolve(), args.source.resolve(), args.approved_by) if args.publish else preview(args.library.resolve(), args.source.resolve())
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
