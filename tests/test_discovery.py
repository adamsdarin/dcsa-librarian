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


if __name__ == "__main__":
    unittest.main()
