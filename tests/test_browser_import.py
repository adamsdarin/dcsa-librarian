from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from library_custodian.discovery import import_browser_capture


class BrowserImportTests(unittest.TestCase):
    def test_import_is_allowlisted_and_finds_missing_document(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            library = root / "library"
            state = root / "state"
            library.mkdir()
            manifest = library / "documents.jsonl"
            manifest.write_text(json.dumps({
                "document_id": "known",
                "human_source_path": "HUMAN/known.pdf",
                "robot_text_path": "ROBOT/known.txt",
                "canonical_source_uri": "https://www.dcsa.mil/docs/known.pdf"
            }) + "\n", encoding="utf-8")
            (library / "START_HERE_FOR_ROBOTS.json").write_text(json.dumps({"documents": "documents.jsonl"}), encoding="utf-8")
            registry = root / "registry.json"
            registry.write_text(json.dumps({"sources": [{
                "id": "dcsa-test",
                "enabled": True,
                "url": "https://www.dcsa.mil/resources/",
                "allowed_domains": ["dcsa.mil"],
                "authority_hint": "dcsa_official"
            }]}), encoding="utf-8")
            capture = root / "capture.json"
            capture.write_text(json.dumps({
                "schema_version": "1.0",
                "source_id": "dcsa-test",
                "captured_at": "2026-08-31T00:00:00Z",
                "pages": [{
                    "url": "https://www.dcsa.mil/resources/",
                    "title": "Resources",
                    "links": [
                        {"url": "/docs/known.pdf", "text": "Known"},
                        {"url": "/docs/new-job-aid.pdf", "text": "New job aid"},
                        {"url": "https://evil.example/not-allowed.pdf", "text": "Reject"}
                    ]
                }]
            }), encoding="utf-8")

            report = import_browser_capture(library, registry, capture, state)

            self.assertFalse(report["publication_performed"])
            self.assertEqual(report["counts"]["known"], 1)
            self.assertEqual(report["counts"]["missing_from_manifest"], 1)
            self.assertEqual(report["counts"]["links_rejected"], 1)
            self.assertEqual(report["candidates"][0]["inferred_filename"], "new-job-aid.pdf")


if __name__ == "__main__":
    unittest.main()
