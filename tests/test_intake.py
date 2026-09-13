from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from library_custodian.discovery import build_intake_package, discover, WebItem


PAGE_URL = "https://www.dcsa.mil/FCL/"
HANDBOOK = "https://www.dcsa.mil/Portals/128/Documents/CTP/FC/DCSA%20FCL_Orientation_Handbook_20260828.pdf"
STRATEGY = "https://www.dcsa.mil/Portals/128/Documents/about/err/DCSA%20Strategic%20Execution%20Plan.pdf"
PDF = b"%PDF-1.7 pretend handbook"


class StubFetcher:
    user_agent = "DCSA-Library-Custodian/0.1 (+local-governance-audit)"

    def __init__(self, **_kwargs: object) -> None:
        pass

    def get(self, url: str) -> tuple[bytes, dict[str, str]]:
        if url.endswith(".pdf"):
            return PDF, {
                "content_type": "application/pdf",
                "final_url": url,
                "etag": '"abc"',
                "last_modified": "Fri, 28 Aug 2026 12:00:00 GMT",
                "content_length": str(len(PDF)),
            }
        body = (
            f'<a href="{HANDBOOK}">FCL Orientation Handbook</a>'
            f'<a href="{STRATEGY}">DCSA Strategic Execution Plan</a>'
        )
        return body.encode(), {"content_type": "text/html", "final_url": url, "etag": "", "last_modified": "", "content_length": ""}

    def head(self, url: str) -> dict[str, str]:
        return {"content_type": "application/pdf", "etag": '"abc"', "last_modified": "", "content_length": "", "final_url": url}


def fixture(root: Path, with_exclusion: bool) -> tuple[Path, Path, Path]:
    library = root / "library"
    library.mkdir()
    (library / "documents.jsonl").write_text("", encoding="utf-8")
    (library / "START_HERE_FOR_ROBOTS.json").write_text(json.dumps({"documents": "documents.jsonl"}), encoding="utf-8")

    registry = root / "registry.json"
    registry.write_text(
        json.dumps(
            {
                "settings": {"delay_seconds": 0},
                "sources": [
                    {
                        "id": "dcsa-fcl",
                        "enabled": True,
                        "url": PAGE_URL,
                        "allowed_domains": ["dcsa.mil"],
                        "max_depth": 0,
                        "max_pages": 1,
                        "authority_hint": "dcsa_official_guidance_or_tool",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    exclusions = root / "exclusions.json"
    entries = [{"url": STRATEGY, "reason": "Agency strategy, not FSO practice material.", "decided_at": "2026-09-13"}] if with_exclusion else []
    exclusions.write_text(json.dumps({"exclusions": entries}), encoding="utf-8")
    return library, registry, exclusions


class ExclusionTests(unittest.TestCase):
    def test_an_excluded_document_is_recorded_not_hidden(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            library, registry, exclusions = fixture(root, with_exclusion=True)
            with mock.patch("library_custodian.discovery.Fetcher", StubFetcher):
                report = discover(library, registry, root / "state", root / "q", exclusions_path=exclusions)

            source = report["sources"][0]
            # still seen and still reported — an exclusion is a decision, not a filter
            self.assertEqual(report["counts"]["documents_seen"], 2)
            self.assertEqual(report["counts"]["excluded_from_scope"], 1)
            self.assertEqual([e["url"] for e in source["excluded"]], [STRATEGY])
            self.assertIn("not FSO practice material", source["excluded"][0]["reason"])
            # but it is not asking anyone to review it again
            self.assertNotIn(STRATEGY, source["candidates_for_review"])
            self.assertIn(HANDBOOK, source["candidates_for_review"])

    def test_without_the_exclusion_it_is_a_candidate(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            library, registry, exclusions = fixture(root, with_exclusion=False)
            with mock.patch("library_custodian.discovery.Fetcher", StubFetcher):
                report = discover(library, registry, root / "state", root / "q", exclusions_path=exclusions)
            self.assertIn(STRATEGY, report["sources"][0]["candidates_for_review"])

    def test_an_excluded_document_is_never_downloaded(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            library, registry, exclusions = fixture(root, with_exclusion=True)
            with mock.patch("library_custodian.discovery.Fetcher", StubFetcher):
                discover(library, registry, root / "state", root / "q", download=True, exclusions_path=exclusions)
            staged = [p.name for p in (root / "q").rglob("*.pdf")]
            self.assertEqual(len(staged), 1)
            self.assertNotIn("DCSA Strategic Execution Plan.pdf", staged)


class IntakePackageTests(unittest.TestCase):
    def _schema(self) -> dict:
        return json.loads(Path("schemas/intake-package.schema.json").read_text(encoding="utf-8"))

    def test_a_download_writes_a_package_matching_the_schema(self) -> None:
        schema = self._schema()
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            library, registry, exclusions = fixture(root, with_exclusion=True)
            with mock.patch("library_custodian.discovery.Fetcher", StubFetcher):
                report = discover(library, registry, root / "state", root / "q", download=True, exclusions_path=exclusions)

            packages = list((root / "q").rglob("*.intake.json"))
            self.assertEqual(len(packages), 1)
            package = json.loads(packages[0].read_text(encoding="utf-8"))

            for field in schema["required"]:
                self.assertIn(field, package, f"required field {field} missing")
            for field in package:
                self.assertIn(field, schema["properties"], f"{field} is not allowed by the schema")

            self.assertEqual(package["approval_state"], "quarantined_unreviewed")
            self.assertEqual(package["source_filename"], "DCSA FCL_Orientation_Handbook_20260828.pdf")
            self.assertEqual(package["mime_type"], "application/pdf")
            self.assertEqual(package["source_bytes"], len(PDF))
            self.assertRegex(package["source_sha256"], r"^[0-9a-f]{64}$")
            self.assertTrue(package["requested_source_uri"].startswith("https://"))
            self.assertEqual(package["publisher_claim"], "FCL Orientation Handbook")
            self.assertEqual(report["sources"][0]["intake_packages"], [package["submission_id"]])

    def test_identical_bytes_from_one_url_resubmit_under_one_id(self) -> None:
        item = WebItem(
            source_id="s", url=HANDBOOK, anchor_text="Handbook", inferred_filename="h.pdf",
            status="missing_from_manifest", discovered_at="2026-09-13T00:00:00Z",
            authority_hint="dcsa_official_guidance_or_tool", lifecycle_hint="unverified",
            sha256="a" * 64, bytes=10, content_type="application/pdf", resolved_url=HANDBOOK,
        )
        first = build_intake_package(item, {}, "agent")
        second = build_intake_package(item, {}, "agent")
        self.assertEqual(first["submission_id"], second["submission_id"])

    def test_a_package_missing_evidence_is_refused(self) -> None:
        item = WebItem(
            source_id="s", url=HANDBOOK, anchor_text="Handbook", inferred_filename="h.pdf",
            status="missing_from_manifest", discovered_at="2026-09-13T00:00:00Z",
            authority_hint="h", lifecycle_hint="unverified",
            sha256=None, bytes=None,
        )
        with self.assertRaises(ValueError) as caught:
            build_intake_package(item, {}, "agent")
        self.assertIn("source_sha256", str(caught.exception))


if __name__ == "__main__":
    unittest.main()
