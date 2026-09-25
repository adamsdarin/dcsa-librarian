"""DOHA acquisition takes only listed URLs, keeps to the registry, and stops when refused.

Decisions, URLs and bytes here are synthetic; the browser is replaced by a fake.
"""
from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from library_custodian.doha_acquire import Response, acquire, load_not_held, parse_robots, plan  # noqa: E402

DOHA = "https://doha.ogc.osd.mil/Industrial-Security-Program/Industrial-Security-Clearance-Decisions"
HEARINGS, APPEALS = f"{DOHA}/ISCR-Hearing-Decisions/", f"{DOHA}/DOHA-Appeal-Board/"
REGISTRY = {"defaults": {"user_agent": "test-agent"}, "sources": [
    {"id": "doha-iscr-hearings", "enabled": True, "url": HEARINGS, "allowed_domains": ["doha.ogc.osd.mil"],
     "crawl_path_prefix": "/Industrial-Security-Program/Industrial-Security-Clearance-Decisions/ISCR-Hearing-Decisions/",
     "authority_hint": "doha_case_research_not_controlling_policy"},
    {"id": "doha-appeals", "enabled": True, "url": APPEALS, "allowed_domains": ["doha.ogc.osd.mil"],
     "crawl_path_prefix": "/Industrial-Security-Program/Industrial-Security-Clearance-Decisions/DOHA-Appeal-Board/",
     "authority_hint": "doha_case_research_not_controlling_policy"}]}
PDF = b"%PDF-1.7 synthetic decision"


def row(key: str, url: str, title: str, group: str = "ISCR Hearing Decisions", fmt: str = "pdf") -> dict:
    return {"case_key": key, "group": group, "labels": [f"{key}.{fmt}"], "formats": [fmt],
            "source_urls": [url], "listing_titles": [title]}


class FakeBrowser:
    def __init__(self, responses: dict[str, Response] | None = None, default: Response | None = None):
        self.responses, self.default, self.requested = responses or {}, default, []

    def fetch(self, url: str) -> Response:
        self.requested.append(url)
        if url in self.responses:
            return self.responses[url]
        return self.default or Response(200, url, {"content-type": "application/pdf"}, PDF)


class DohaAcquireTests(unittest.TestCase):
    def setUp(self) -> None:
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.run_dir = Path(temp.name) / "run"
        self.run_dir.mkdir()
        self.robots = parse_robots("User-agent: *\nAllow: /\n")

    def run_acquire(self, rows, browser, **kwargs):
        self.lines = []
        return acquire(rows, REGISTRY, self.run_dir, browser, kwargs.pop("robots", self.robots),
                       delay_seconds=0, sleep=lambda _: None, progress=self.lines.append, **kwargs)

    def test_newest_listings_first_and_hearings_before_appeals(self) -> None:
        rows = [row("04-00001.h1", f"{HEARINGS}Archived/2016-and-Prior-1/FileId/1/", "2016 and Prior ISCR Hearing Decisions - 4"),
                row("24-00002.a1", f"{APPEALS}2025-DOHA-Appeal-Board/FileId/2/", "2025 DOHA Appeal Board Decisions",
                    "DOHA Appeal Board Decisions"),
                row("24-00003.h1", f"{HEARINGS}2025-ISCR-Hearing-Decisions/FileId/3/", "2025 ISCR Hearing Decisions")]
        self.assertEqual([r["case_key"] for r in plan(rows)], ["24-00003.h1", "24-00002.a1", "04-00001.h1"])
        self.assertEqual([r["case_key"] for r in plan(rows, {"DOHA Appeal Board Decisions"})], ["24-00002.a1"])
        self.assertEqual(len(plan(rows, limit=2)), 2)

    def test_acquired_file_carries_a_package_the_archivist_accepts(self) -> None:
        url = f"{HEARINGS}2025-ISCR-Hearing-Decisions/FileId/3/"
        report = self.run_acquire([row("24-00003.h1", url, "2025 ISCR Hearing Decisions")], FakeBrowser())
        self.assertEqual(report["counts"]["acquired"], 1)
        self.assertFalse(report["library_written"])
        source = self.run_dir / "iscr-hearing-decisions" / "24-00003.h1.pdf"
        package = json.loads(source.with_name(source.name + ".intake.json").read_text(encoding="utf-8"))
        # The checks dcsa-archivist's stage_intake applies before it will stage a package.
        self.assertEqual(package["approval_state"], "quarantined_unreviewed")
        self.assertTrue(package["requested_source_uri"].startswith("https://"))
        self.assertTrue(package["resolved_source_uri"].startswith("https://"))
        self.assertEqual(package["source_sha256"], hashlib.sha256(PDF).hexdigest())
        self.assertEqual(package["source_bytes"], len(PDF))
        self.assertEqual(package["source_filename"], source.name)
        self.assertEqual(package["mime_type"], "application/pdf")
        self.assertEqual(package["proposed_collection"], "doha_decisions")
        self.assertIn("DOHA group: ISCR Hearing Decisions", package["producer_notes"])

    def test_a_resumed_run_does_not_request_what_it_already_has(self) -> None:
        rows = [row("24-00003.h1", f"{HEARINGS}2025-ISCR-Hearing-Decisions/FileId/3/", "2025 ISCR Hearing Decisions")]
        self.run_acquire(rows, FakeBrowser())
        browser = FakeBrowser()
        report = self.run_acquire(rows, browser)
        self.assertEqual(browser.requested, [])
        self.assertEqual(report["counts"]["already_acquired"], 1)

    def test_a_challenge_page_served_with_200_is_refused_not_saved(self) -> None:
        url = f"{HEARINGS}2025-ISCR-Hearing-Decisions/FileId/3/"
        challenge = Response(200, url, {"content-type": "text/html"}, b"<html>Access Denied</html>")
        report = self.run_acquire([row("24-00003.h1", url, "2025 ISCR Hearing Decisions")], FakeBrowser({url: challenge}))
        self.assertEqual(report["counts"], {"acquired": 0, "already_acquired": 0, "refused": 1, "skipped": 0, "non_pdf_document": 0})
        self.assertFalse((self.run_dir / "iscr-hearing-decisions").exists())

    def test_a_redirect_off_the_source_is_refused(self) -> None:
        url = f"{HEARINGS}2025-ISCR-Hearing-Decisions/FileId/3/"
        moved = Response(200, "https://example.com/decision.pdf", {"content-type": "application/pdf"}, PDF)
        report = self.run_acquire([row("24-00003.h1", url, "2025 ISCR Hearing Decisions")], FakeBrowser({url: moved}))
        self.assertEqual(report["counts"]["refused"], 1)

    def test_repeated_refusals_stop_the_run(self) -> None:
        rows = [row(f"24-{n:05d}.h1", f"{HEARINGS}2025-ISCR-Hearing-Decisions/FileId/{n}/", "2025 ISCR Hearing Decisions")
                for n in range(1, 10)]
        browser = FakeBrowser(default=Response(403, "", {}, b""))
        report = self.run_acquire(rows, browser)
        self.assertEqual(len(browser.requested), 5)
        self.assertIn("5 refusals in a row", report["stopped"])

    def test_robots_and_the_allowlist_are_checked_before_any_request(self) -> None:
        rows = [row("24-00003.h1", f"{HEARINGS}2025-ISCR-Hearing-Decisions/FileId/3/", "2025 ISCR Hearing Decisions"),
                row("24-00004.h1", "https://doha-mirror.example.com/FileId/4/", "2025 ISCR Hearing Decisions")]
        browser = FakeBrowser()
        robots = parse_robots("User-agent: *\nDisallow: /Industrial-Security-Program/\n")
        report = self.run_acquire(rows, browser, robots=robots)
        self.assertEqual(browser.requested, [])
        self.assertEqual(report["counts"]["skipped"], 2)
        reasons = [json.loads(line)["reason"] for line in (self.run_dir / "attempts.jsonl").read_text().splitlines()]
        self.assertEqual(sorted(reasons), ["outside_registry_allowlist", "robots_disallowed"])

    def test_a_not_held_file_from_before_grouping_is_refused(self) -> None:
        old = self.run_dir / "old.jsonl"
        old.write_text(json.dumps({"case_key": "24-00003.h1", "source_urls": []}) + "\n", encoding="utf-8")
        with self.assertRaises(SystemExit) as raised:
            load_not_held(old)
        self.assertIn("re-run doha-provenance", str(raised.exception))
        mixed = self.run_dir / "mixed.jsonl"
        mixed.write_text(json.dumps({"case_key": "08-01000.h1", "source_urls": [],
                                     "group": "DOHA Appeal Board Decisions + ISCR Hearing Decisions"}) + "\n", encoding="utf-8")
        with self.assertRaises(SystemExit):
            load_not_held(mixed)

    def test_progress_is_reported_for_every_decision(self) -> None:
        rows = [row(f"24-{n:05d}.h1", f"{HEARINGS}2025-ISCR-Hearing-Decisions/FileId/{n}/", "2025 ISCR Hearing Decisions")
                for n in range(1, 4)]
        self.run_acquire(rows, FakeBrowser())
        self.assertIn("3 planned, 0 already in this run", self.lines[0])
        self.assertEqual(sum("acquired" in line for line in self.lines[1:]), 3)
        self.assertTrue(self.lines[-1].startswith("[3/3] "))

    def test_a_closed_browser_stops_at_once_and_is_not_a_refusal(self) -> None:
        class ClosedBrowser(FakeBrowser):
            def fetch(self, url):
                self.requested.append(url)
                raise RuntimeError("Page.evaluate: Target page, context or browser has been closed")
        rows = [row(f"24-{n:05d}.h1", f"{HEARINGS}2025-ISCR-Hearing-Decisions/FileId/{n}/", "2025 ISCR Hearing Decisions")
                for n in range(1, 6)]
        browser = ClosedBrowser()
        report = self.run_acquire(rows, browser)
        self.assertEqual(len(browser.requested), 1)
        self.assertEqual(report["counts"]["refused"], 0)
        self.assertIn("Chrome window was closed", report["stopped"])
        # The interrupted decision is retried on resume, not treated as acquired.
        self.assertEqual(self.run_acquire(rows, FakeBrowser())["counts"]["acquired"], 5)

    def test_a_pdf_header_after_leading_bytes_is_accepted(self) -> None:
        url = f"{HEARINGS}2025-ISCR-Hearing-Decisions/FileId/3/"
        padded = Response(200, url, {"content-type": "application/octet-stream"}, b"\r\n\x00junk" + PDF)
        report = self.run_acquire([row("24-00003.h1", url, "2025 ISCR Hearing Decisions")], FakeBrowser({url: padded}))
        self.assertEqual(report["counts"]["acquired"], 1)

    def test_a_word_file_under_a_pdf_label_is_set_aside_and_does_not_stop_the_run(self) -> None:
        body = b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1rest"
        rows = [row(f"19-{n:05d}.a1", f"{APPEALS}2019-DOHA-Appeal-Board/FileId/{n}/", "2019 DOHA Appeal Board",
                    "DOHA Appeal Board Decisions") for n in range(1, 8)]
        responses = {r["source_urls"][0]: Response(200, r["source_urls"][0], {"content-type": "application/octet-stream"}, body)
                     for r in rows[:6]}
        report = self.run_acquire(rows, FakeBrowser(responses))
        self.assertIsNone(report["stopped"])
        self.assertEqual((report["counts"]["non_pdf_document"], report["counts"]["acquired"]), (6, 1))
        self.assertTrue((self.run_dir / "refused" / "19-00001.a1.word_97_2003_or_ole.bin").is_file())
        # Set-aside files are not requested again on resume.
        again = FakeBrowser()
        self.run_acquire(rows, again)
        self.assertEqual(again.requested, [])

    def test_an_unrecognised_refusal_records_what_came_back(self) -> None:
        url = f"{HEARINGS}2025-ISCR-Hearing-Decisions/FileId/3/"
        odd = Response(200, url, {"content-type": "application/octet-stream"}, b"\x01\x02\x03 not a document")
        self.run_acquire([row("24-00003.h1", url, "2025 ISCR Hearing Decisions")], FakeBrowser({url: odd}))
        reason = json.loads((self.run_dir / "attempts.jsonl").read_text().splitlines()[-1])["reason"]
        self.assertIn("content: unrecognised, first bytes 010203", reason)
        self.assertTrue((self.run_dir / "refused" / "24-00003.h1.unrecognised.bin").is_file())


if __name__ == "__main__":
    unittest.main()
