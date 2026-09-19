from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from library_custodian.discovery import discover

from test_intake import HANDBOOK, PDF, StubFetcher, fixture


def hold_without_url(library: Path, data: bytes) -> None:
    """The library already has the handbook's bytes but no official URL on record."""
    human = library / "HUMAN/DCSA FCL_Orientation_Handbook_20260828.pdf"
    human.parent.mkdir(parents=True)
    human.write_bytes(data)
    record = {"document_id": "fcl-handbook", "human_source_path": "HUMAN/DCSA FCL_Orientation_Handbook_20260828.pdf"}
    (library / "documents.jsonl").write_text(json.dumps(record) + "\n", encoding="utf-8")


class ProvenanceTests(unittest.TestCase):
    def scan(self, retained: bytes) -> tuple[dict, Path]:
        root = Path(self._dir.name)
        library, registry, exclusions = fixture(root, with_exclusion=True)
        hold_without_url(library, retained)
        with mock.patch("library_custodian.discovery.Fetcher", StubFetcher):
            report = discover(library, registry, root / "state", root / "q", download=True, exclusions_path=exclusions)
        return report, root

    def setUp(self) -> None:
        self._dir = tempfile.TemporaryDirectory()

    def tearDown(self) -> None:
        self._dir.cleanup()

    def test_identical_bytes_record_the_official_url(self) -> None:
        report, root = self.scan(PDF)
        self.assertEqual(report["counts"]["provenance_verified"], 1)
        row = report["provenance"][0]
        self.assertEqual((row["document_id"], row["status"], row["requested_url"]), ("fcl-handbook", "verified", HANDBOOK))
        ledger = (root / "state/provenance/provenance.jsonl").read_text(encoding="utf-8").splitlines()
        self.assertEqual(json.loads(ledger[0])["run_id"], report["run_id"])
        # nothing is quarantined: the library already holds these exact bytes
        self.assertEqual(report["counts"]["downloaded_to_quarantine"], 0)

    def test_a_matching_name_with_different_bytes_is_not_provenance(self) -> None:
        report, _ = self.scan(b"%PDF-1.7 an older printing")
        self.assertEqual(report["counts"]["provenance_verified"], 0)
        self.assertEqual(report["provenance"][0]["status"], "bytes_differ")

    def test_without_download_nothing_is_fetched_for_provenance(self) -> None:
        root = Path(self._dir.name)
        library, registry, exclusions = fixture(root, with_exclusion=True)
        hold_without_url(library, PDF)
        with mock.patch("library_custodian.discovery.Fetcher", StubFetcher):
            report = discover(library, registry, root / "state", root / "q", exclusions_path=exclusions)
        self.assertEqual(report["provenance"], [])
        self.assertFalse((root / "state/provenance").exists())


if __name__ == "__main__":
    unittest.main()
