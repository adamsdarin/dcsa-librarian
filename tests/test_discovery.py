from __future__ import annotations

import unittest

from library_custodian.discovery import canonicalize_url, domain_allowed, extract_links, infer_filename, is_document_link


class DiscoveryTests(unittest.TestCase):
    def test_extracts_and_normalizes_links(self) -> None:
        html = '<a href="/docs/Aid.pdf">Aid PDF</a><a href="https://evil.example/bad.pdf">bad</a>'
        links = extract_links(html, "https://www.dcsa.mil/resources/")
        self.assertEqual(links[0]["url"], "https://www.dcsa.mil/docs/Aid.pdf")
        self.assertTrue(domain_allowed(links[0]["url"], ["dcsa.mil"]))
        self.assertFalse(domain_allowed(links[1]["url"], ["dcsa.mil"]))

    def test_doha_fileid_uses_anchor_filename(self) -> None:
        url = "https://doha.ogc.osd.mil/path/FileId/254155/"
        self.assertTrue(is_document_link(url, "25-00138.h1.pdf"))
        self.assertEqual(infer_filename(url, "25-00138.h1.pdf"), "25-00138.h1.pdf")

    def test_canonicalize_drops_fragment(self) -> None:
        self.assertEqual(canonicalize_url("HTTPS://WWW.DCSA.MIL//a///b#top"), "https://www.dcsa.mil/a/b")


class CrossPageDeduplicationTests(unittest.TestCase):
    """A document linked from several pages is one document, not several.

    Observed live on 2026-09-07: the FCL handbook was reported four times from a
    two-page crawl, because links were deduplicated within a page but not across
    the crawl.
    """

    HANDBOOK = "https://www.dcsa.mil/Portals/128/Documents/CTP/FC/handbook.pdf"

    class TwoPageFetcher:
        def __init__(self, **_kwargs: object) -> None:
            pass

        def get(self, url: str) -> tuple[bytes, dict[str, str]]:
            body = (
                '<a href="/FCL/second/">Second page</a>'
                '<a href="/Portals/128/Documents/CTP/FC/handbook.pdf">Handbook</a>'
            )
            return body.encode(), {"content_type": "text/html", "final_url": url, "etag": "", "last_modified": "", "content_length": ""}

        def head(self, url: str) -> dict[str, str]:
            return {"content_type": "application/pdf", "etag": "v1", "last_modified": "", "content_length": "", "final_url": url}

    def test_a_document_linked_from_two_pages_is_recorded_once(self) -> None:
        from library_custodian.discovery import _crawl_source

        source = {
            "id": "dcsa-fcl",
            "url": "https://www.dcsa.mil/FCL/first/",
            "allowed_domains": ["dcsa.mil"],
            "crawl_path_prefix": "/FCL/",
            "max_depth": 1,
            "max_pages": 5,
        }
        documents, pages = _crawl_source(source, self.TwoPageFetcher())
        self.assertEqual(len(pages), 2, "the fixture must actually crawl two pages")
        self.assertEqual([doc["url"] for doc in documents], [self.HANDBOOK])


if __name__ == "__main__":
    unittest.main()
