from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from library_custodian.discovery import preflight, render_preflight_text


PAGE_URL = "https://www.dcsa.mil/resources/"


class StubFetcher:
    html = b'<a href="/docs/260831 VOI Newsletter.pdf">August VOI</a><a href="/docs/handbook.pdf">Handbook</a>'
    error: Exception | None = None

    def __init__(self, **_kwargs: object) -> None:
        pass

    def get(self, url: str) -> tuple[bytes, dict[str, str]]:
        if type(self).error is not None:
            raise type(self).error
        return type(self).html, {"content_type": "text/html", "final_url": url, "etag": "", "last_modified": "", "content_length": ""}

    def head(self, url: str) -> dict[str, str]:
        raise AssertionError("preflight must not probe documents")


def registry(root: Path) -> Path:
    path = root / "registry.json"
    path.write_text(
        json.dumps(
            {
                "settings": {"delay_seconds": 0},
                "sources": [{"id": "dcsa-test", "enabled": True, "url": PAGE_URL, "allowed_domains": ["dcsa.mil"], "max_depth": 0, "max_pages": 1}],
            }
        ),
        encoding="utf-8",
    )
    return path


class PreflightTests(unittest.TestCase):
    def setUp(self) -> None:
        StubFetcher.error = None
        StubFetcher.html = b'<a href="/docs/260831 VOI Newsletter.pdf">August VOI</a><a href="/docs/handbook.pdf">Handbook</a>'

    def test_lists_what_the_parser_can_see(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            with mock.patch("library_custodian.discovery.Fetcher", StubFetcher):
                result = preflight(registry(Path(temp)), "dcsa-test")
        self.assertTrue(result["reachable"])
        self.assertEqual(result["documents_seen"], 2)
        self.assertFalse(result["wrote_anything"])
        self.assertIn("260831 VOI Newsletter.pdf", render_preflight_text(result))

    def test_match_filters_without_hiding_the_true_total(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            with mock.patch("library_custodian.discovery.Fetcher", StubFetcher):
                result = preflight(registry(Path(temp)), "dcsa-test", match="voi")
        self.assertEqual(result["documents_seen"], 2)
        self.assertEqual(result["documents_listed"], 1)
        self.assertIn("VOI", result["documents"][0]["inferred_filename"])

    def test_a_page_with_no_visible_documents_names_the_tab_problem(self) -> None:
        # the failure that would make voi-release-watch silently useless
        StubFetcher.html = b"<html><body><div>tabs rendered by script</div></body></html>"
        with tempfile.TemporaryDirectory() as temp:
            with mock.patch("library_custodian.discovery.Fetcher", StubFetcher):
                result = preflight(registry(Path(temp)), "dcsa-test")
        text = render_preflight_text(result)
        self.assertEqual(result["documents_seen"], 0)
        self.assertIn("rendered by script", text)
        self.assertIn("browser-import", text)
        self.assertIn("look healthy doing it", text)

    def test_an_unreachable_source_refuses_to_imply_anything(self) -> None:
        StubFetcher.error = OSError("boom")
        with tempfile.TemporaryDirectory() as temp:
            with mock.patch("library_custodian.discovery.Fetcher", StubFetcher):
                result = preflight(registry(Path(temp)), "dcsa-test")
        text = render_preflight_text(result)
        self.assertFalse(result["reachable"])
        self.assertIn("tells you nothing about whether the source changed", text)
        self.assertIn("Do not spoof a user agent", text)

    def test_unknown_source_names_the_ones_that_exist(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(KeyError) as caught:
                preflight(registry(Path(temp)), "nope")
        self.assertIn("dcsa-test", caught.exception.args[0])

    def test_preflight_writes_no_state(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            path = registry(root)
            before = sorted(p.name for p in root.iterdir())
            with mock.patch("library_custodian.discovery.Fetcher", StubFetcher):
                preflight(path, "dcsa-test")
            self.assertEqual(sorted(p.name for p in root.iterdir()), before)


if __name__ == "__main__":
    unittest.main()
