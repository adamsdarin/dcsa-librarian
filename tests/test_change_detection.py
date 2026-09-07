from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from library_custodian.discovery import (
    compare_fingerprints,
    discover,
    load_snapshot_documents,
    needs_review,
)
from library_custodian.discovery import WebItem


PAGE_HTML = b'<html><body><a href="/docs/known.pdf">FCL Orientation Handbook</a></body></html>'
PAGE_URL = "https://www.dcsa.mil/resources/"
DOC_URL = "https://www.dcsa.mil/docs/known.pdf"


class StubFetcher:
    """Serves one HTML page and one document whose ETag the test controls."""

    etag = "v1"

    def __init__(self, **_kwargs: object) -> None:
        self.head_calls: list[str] = []

    def get(self, url: str) -> tuple[bytes, dict[str, str]]:
        return PAGE_HTML, {"content_type": "text/html", "final_url": url, "etag": "", "last_modified": "", "content_length": ""}

    def head(self, url: str) -> dict[str, str]:
        self.head_calls.append(url)
        return {"content_type": "application/pdf", "etag": type(self).etag, "last_modified": "", "content_length": "", "final_url": url}


def build_library(root: Path) -> tuple[Path, Path]:
    library = root / "library"
    library.mkdir()
    (library / "documents.jsonl").write_text(
        json.dumps(
            {
                "document_id": "known",
                "human_source_path": "HUMAN/known.pdf",
                "robot_text_path": "ROBOT/known.txt",
                "canonical_source_uri": DOC_URL,
            }
        )
        + "\n",
        encoding="utf-8",
    )
    (library / "START_HERE_FOR_ROBOTS.json").write_text(json.dumps({"documents": "documents.jsonl"}), encoding="utf-8")
    registry = root / "registry.json"
    registry.write_text(
        json.dumps(
            {
                "settings": {"delay_seconds": 0},
                "sources": [
                    {
                        "id": "dcsa-test",
                        "enabled": True,
                        "url": PAGE_URL,
                        "allowed_domains": ["dcsa.mil"],
                        "max_depth": 0,
                        "max_pages": 1,
                        "authority_hint": "dcsa_official",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    return library, registry


class FingerprintTests(unittest.TestCase):
    def test_no_baseline_is_not_unchanged(self) -> None:
        self.assertEqual(compare_fingerprints(None, {"etag": "v1"}), ("new_to_snapshot", []))

    def test_absent_evidence_reports_unverified_never_unchanged(self) -> None:
        signal, fields = compare_fingerprints({"etag": ""}, {"etag": ""})
        self.assertEqual((signal, fields), ("unverified", []))

    def test_differing_etag_is_changed_and_names_the_field(self) -> None:
        self.assertEqual(compare_fingerprints({"etag": "v1"}, {"etag": "v2"}), ("changed", ["etag"]))

    def test_matching_evidence_is_unchanged(self) -> None:
        self.assertEqual(compare_fingerprints({"sha256": "a"}, {"sha256": "a"}), ("unchanged", []))

    def test_sha256_wins_over_a_churning_etag(self) -> None:
        signal, fields = compare_fingerprints({"sha256": "a", "etag": "v1"}, {"sha256": "a", "etag": "v2"})
        self.assertEqual((signal, fields), ("changed", ["etag"]))


class ReviewPredicateTests(unittest.TestCase):
    def _item(self, status: str, signal: str) -> WebItem:
        return WebItem(
            source_id="s",
            url=DOC_URL,
            anchor_text="",
            inferred_filename="known.pdf",
            status=status,
            discovered_at="",
            authority_hint="",
            lifecycle_hint="",
            change_signal=signal,
        )

    def test_changed_known_document_is_a_candidate(self) -> None:
        self.assertTrue(needs_review(self._item("known", "changed")))

    def test_unchanged_known_document_is_not(self) -> None:
        self.assertFalse(needs_review(self._item("known", "unchanged")))

    def test_missing_document_is_still_a_candidate(self) -> None:
        self.assertTrue(needs_review(self._item("missing_from_manifest", "unchanged")))


class SnapshotCompatibilityTests(unittest.TestCase):
    def test_absent_snapshot_is_none_not_empty(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            self.assertIsNone(load_snapshot_documents(Path(temp) / "nope.json"))

    def test_schema_1_snapshot_reads_as_url_baseline(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "s.json"
            path.write_text(json.dumps({"source_id": "s", "document_urls": [DOC_URL]}), encoding="utf-8")
            self.assertEqual(load_snapshot_documents(path), {DOC_URL: {}})


class RevisionInPlaceTests(unittest.TestCase):
    def test_same_url_revision_becomes_a_review_candidate(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            library, registry = build_library(root)
            state, quarantine = root / "state", root / "quarantine"

            with mock.patch("library_custodian.discovery.Fetcher", StubFetcher):
                StubFetcher.etag = "v1"
                first = discover(library, registry, state, quarantine)

                # the manifest already holds this document, so the first scan is
                # a baseline, not a clean bill of health
                self.assertFalse(first["sources"][0]["baseline_established"])
                self.assertEqual(first["counts"]["known"], 1)
                self.assertEqual(first["candidates"], [])

                # DCSA republishes the handbook at the same URL and filename
                StubFetcher.etag = "v2"
                second = discover(library, registry, state, quarantine)

            source = second["sources"][0]
            self.assertTrue(source["baseline_established"])
            self.assertEqual(source["new_urls_since_previous_scan"], [])
            self.assertEqual([entry["url"] for entry in source["changed_since_previous_scan"]], [DOC_URL])
            self.assertEqual(source["changed_since_previous_scan"][0]["changed_fields"], ["etag"])
            self.assertEqual(second["counts"]["changed_since_previous_scan"], 1)
            self.assertEqual(second["candidates"][0]["url"], DOC_URL)
            self.assertEqual(second["candidates"][0]["status"], "known")

    def test_no_verify_known_leaves_the_document_unverified(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            library, registry = build_library(root)
            state, quarantine = root / "state", root / "quarantine"

            with mock.patch("library_custodian.discovery.Fetcher", StubFetcher):
                discover(library, registry, state, quarantine, verify_known=False)
                report = discover(library, registry, state, quarantine, verify_known=False)

            self.assertEqual(report["counts"]["unverified"], 1)
            self.assertEqual(report["sources"][0]["unverified_documents"], [DOC_URL])
            self.assertEqual(report["candidates"], [])


class ImmutableSourceTests(unittest.TestCase):
    """A source whose records never change should never be probed for changes."""

    class RefusingFetcher(StubFetcher):
        def head(self, url: str) -> dict[str, str]:
            raise AssertionError("a source opted out of verification must not be probed")

    def _registry(self, root: Path, verify_known: bool) -> Path:
        path = root / "registry.json"
        source = {
            "id": "doha-test",
            "enabled": True,
            "url": PAGE_URL,
            "allowed_domains": ["dcsa.mil"],
            "max_depth": 0,
            "max_pages": 1,
        }
        if not verify_known:
            source["verify_known"] = False
        path.write_text(json.dumps({"settings": {"delay_seconds": 0}, "sources": [source]}), encoding="utf-8")
        return path

    def test_a_source_can_opt_out_of_verification(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            library, _ = build_library(root)
            registry = self._registry(root, verify_known=False)
            with mock.patch("library_custodian.discovery.Fetcher", self.RefusingFetcher):
                report = discover(library, registry, root / "state", root / "q")
            self.assertFalse(report["sources"][0]["known_documents_verified"])

    def test_the_global_flag_can_only_narrow_a_source_that_opted_in(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            library, _ = build_library(root)
            registry = self._registry(root, verify_known=True)
            with mock.patch("library_custodian.discovery.Fetcher", self.RefusingFetcher):
                report = discover(library, registry, root / "state", root / "q", verify_known=False)
            self.assertFalse(report["sources"][0]["known_documents_verified"])


if __name__ == "__main__":
    unittest.main()
