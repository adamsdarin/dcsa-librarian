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


class UrlEncodingTests(unittest.TestCase):
    """DCSA publishes filenames with spaces; urllib refuses raw spaces.

    Observed live on 2026-09-07: 13 of 15 documents in the FCL section failed
    their HEAD probe with "URL can't contain control characters", including the
    FCL Orientation Handbook. Every VOI newsletter has the same shape. The
    documents were discoverable but could never be verified or downloaded.
    """

    HANDBOOK = "https://www.dcsa.mil/Portals/128/Documents/CTP/FC/DCSA FCL_Orientation_Handbook_20260828.pdf"
    ENCODED = "https://www.dcsa.mil/Portals/128/Documents/CTP/FC/DCSA%20FCL_Orientation_Handbook_20260828.pdf"

    def test_a_space_is_encoded_so_the_document_can_be_requested(self) -> None:
        self.assertEqual(canonicalize_url(self.HANDBOOK), self.ENCODED)

    def test_an_already_encoded_url_is_not_encoded_twice(self) -> None:
        self.assertEqual(canonicalize_url(self.ENCODED), self.ENCODED)
        self.assertNotIn("%2520", canonicalize_url(self.ENCODED))

    def test_both_spellings_are_one_document(self) -> None:
        self.assertEqual(canonicalize_url(self.HANDBOOK), canonicalize_url(self.ENCODED))

    def test_the_filename_still_decodes_for_manifest_matching(self) -> None:
        # the manifest records human filenames, spaces and all
        self.assertEqual(
            infer_filename(canonicalize_url(self.HANDBOOK), ""),
            "DCSA FCL_Orientation_Handbook_20260828.pdf",
        )

    def test_a_query_string_survives_intact(self) -> None:
        url = (
            "https://www.federalregister.gov/api/v1/documents.json?per_page=100"
            "&conditions%5Bagencies%5D%5B%5D=defense-counterintelligence-and-security-agency"
        )
        self.assertEqual(canonicalize_url(url), url)


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
