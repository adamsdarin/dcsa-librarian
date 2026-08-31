from __future__ import annotations

import json
import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path

from library_custodian.audit import audit_library


class AuditTests(unittest.TestCase):
    def make_library(self, root: Path, missing_human: bool = False) -> Path:
        (root / "ROBOT_READABLE_DIRECTORY" / "TEXT").mkdir(parents=True)
        (root / "HUMAN_READABLE_DIRECTORY").mkdir()
        (root / "LOCAL_INDEXES").mkdir()
        robot = root / "ROBOT_READABLE_DIRECTORY" / "TEXT" / "doc.txt"
        human = root / "HUMAN_READABLE_DIRECTORY" / "doc.pdf"
        robot.write_text("robot text", encoding="utf-8")
        if not missing_human:
            human.write_bytes(b"%PDF-test")
        for name in ("policy.json", "catalog.json", "aliases.json", "relationships.jsonl", "retrieval.json", "state.json", "router.json", "taxonomy.json", "coverage.json"):
            (root / name).write_text("{}\n", encoding="utf-8")
        database = root / "LOCAL_INDEXES" / "general.sqlite"
        with closing(sqlite3.connect(database)) as connection:
            connection.execute("create table documents(id text)")
            connection.commit()
        manifest = root / "documents.jsonl"
        record = {
            "document_id": "doc-1",
            "human_source_path": "HUMAN_READABLE_DIRECTORY/doc.pdf",
            "robot_text_path": "ROBOT_READABLE_DIRECTORY/TEXT/doc.txt",
            "source_exists": not missing_human,
            "current_status": "current",
            "authority_tier": 1,
        }
        manifest.write_text(json.dumps(record) + "\n", encoding="utf-8")
        entry = {
            "access_policy": "policy.json",
            "catalog": "catalog.json",
            "aliases": "aliases.json",
            "documents": "documents.jsonl",
            "relationships": "relationships.jsonl",
            "retrieval": "retrieval.json",
            "library_state": "state.json",
            "doha_router": "router.json",
            "doha_topic_taxonomy": "taxonomy.json",
            "doha_topic_coverage": "coverage.json",
            "local_indexes": ["LOCAL_INDEXES/general.sqlite"],
        }
        (root / "START_HERE_FOR_ROBOTS.json").write_text(json.dumps(entry), encoding="utf-8")
        return root

    def test_healthy_fixture_is_ready(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            report = audit_library(self.make_library(Path(temp)))
            self.assertTrue(report.ready)
            self.assertEqual(report.counters["manifest_records"], 1)

    def test_missing_human_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            report = audit_library(self.make_library(Path(temp), missing_human=True))
            self.assertFalse(report.ready)
            self.assertEqual(report.finding_totals["missing_human_file"], 1)


if __name__ == "__main__":
    unittest.main()
