"""A DOHA source URL comes from the official listing, or from matching bytes, or not at all.

Captures and cases here are synthetic.
"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from library_custodian.doha_provenance import (  # noqa: E402
    LABEL, build_ledger, case_key, case_year, format_summary, summarize_missing)

DOHA = "https://doha.ogc.osd.mil/Industrial-Security-Program/Industrial-Security-Clearance-Decisions"
HEARINGS = f"{DOHA}/ISCR-Hearing-Decisions/"
ARCHIVE = f"{DOHA}/ISCR-Hearing-Decisions/Archived-ISCR-Hearing-Decisions/"
APPEALS = f"{DOHA}/DOHA-Appeal-Board/"
REGISTRY = {"sources": [{"id": "doha-iscr-hearings", "enabled": True, "url": HEARINGS,
                         "allowed_domains": ["doha.ogc.osd.mil"],
                         "crawl_path_prefix": "/Industrial-Security-Program/Industrial-Security-Clearance-Decisions/ISCR-Hearing-Decisions/"},
                        {"id": "doha-appeals", "enabled": True, "url": APPEALS,
                         "allowed_domains": ["doha.ogc.osd.mil"],
                         "crawl_path_prefix": "/Industrial-Security-Program/Industrial-Security-Clearance-Decisions/DOHA-Appeal-Board/"}]}


class DohaProvenanceTests(unittest.TestCase):
    def setUp(self) -> None:
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.base = Path(temp.name)
        self.library = self.base / "library"
        (self.library / "ROBOT_READABLE_DIRECTORY/MANIFESTS").mkdir(parents=True)
        self.registry = self.base / "registry.json"
        self.registry.write_text(json.dumps(REGISTRY), encoding="utf-8")
        self.captures = 0

    def decisions(self, *stems: str) -> None:
        rows = [{"document_id": f"doc-{stem}", "case_stem": stem} for stem in stems]
        (self.library / "ROBOT_READABLE_DIRECTORY/MANIFESTS/DOHA_CURRENT_PATHS.jsonl").write_text(
            "".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")

    def capture(self, *pages: dict) -> Path:
        self.captures += 1
        path = self.base / f"capture-{self.captures}.jsonl"
        path.write_text("".join(json.dumps(page) + "\n" for page in pages), encoding="utf-8")
        return path

    def page(self, url: str, title: str, rows: list[list], at: str = "2026-09-22T00:00:00.000Z") -> dict:
        return {"u": url, "t": title, "at": at, "rows": rows}

    def build(self, capture: Path, hashes: dict | None = None):
        rows, _, report = build_ledger(self.library, [capture], self.registry, hashes or {})
        return rows, report

    def missing(self, capture: Path):
        _, missing, report = build_ledger(self.library, [capture], self.registry, {})
        return missing, report

    def test_case_key_normalizes_what_doha_prints(self) -> None:
        self.assertEqual(case_key("18.02204.h1.pdf", LABEL), "18-02204.h1")
        self.assertEqual(case_key("19-00803-SD.h1.pdf", LABEL), "19-00803-sd.h1")
        self.assertEqual(case_key("15-01381.h1_approved_F"), "15-01381.h1")
        self.assertIsNone(case_key("ISCR+Case+No+08-07664.pdf", LABEL))

    def test_listing_label_records_the_url_and_its_weaker_basis(self) -> None:
        self.decisions("19-02096.a1_denied_f")
        capture = self.capture(self.page(f"{HEARINGS}2019-ISCR-Hearing-Decisions/", "2019 ISCR Hearing Decisions",
                                         [["19-02096.a1.pdf", "219192", 1]]))
        rows, report = self.build(capture)
        self.assertEqual(rows[0]["source_url"], f"{HEARINGS}2019-ISCR-Hearing-Decisions/FileId/219192/")
        self.assertEqual(rows[0]["source_url_basis"], "official_listing_label")
        self.assertEqual(rows[0]["source_listing_title"], "2019 ISCR Hearing Decisions")
        self.assertEqual(report["basis_counts"]["official_listing_label"], 1)
        self.assertFalse(report["downloads_performed"] or report["library_written"])

    def test_matching_bytes_from_a_recorded_download_upgrade_the_basis(self) -> None:
        self.decisions("19-02096.a1_denied_f")
        legacy = self.library / "ROBOT_READABLE_DIRECTORY/LEGACY_IMPORTS/doha-decisions"
        legacy.mkdir(parents=True)
        url = f"{HEARINGS}2019-ISCR-Hearing-Decisions/FileId/219192/"
        digest = "a" * 64
        (legacy / "download_progress.json").write_text(
            json.dumps({"browserManifest": [{"label": "19-02096.a1.pdf", "url": url}]}), encoding="utf-8")
        (legacy / "inventory.csv").write_text(
            f"case,level,disposition,file,bytes,sha256\n19-02096.a1,appeal,denied,x.pdf,1,{digest}\n", encoding="utf-8")
        capture = self.capture(self.page(f"{HEARINGS}2019-ISCR-Hearing-Decisions/", "2019 ISCR Hearing Decisions",
                                         [["19-02096.a1.pdf", "219192", 1]]))
        rows, _ = self.build(capture, {"doc-19-02096.a1_denied_f": digest})
        self.assertEqual(rows[0]["source_url_basis"], "legacy_download_bytes_identical")
        self.assertEqual(rows[0]["source_bytes_sha256"], digest)
        # Different retained bytes leave the listing basis in place.
        rows, _ = self.build(capture, {"doc-19-02096.a1_denied_f": "b" * 64})
        self.assertEqual(rows[0]["source_url_basis"], "official_listing_label")
        self.assertIsNone(rows[0]["source_bytes_sha256"])

    def test_copies_on_two_listings_keep_alternates_and_withhold_the_year(self) -> None:
        self.decisions("04-08547.h1_denied_f")
        capture = self.capture(
            self.page(f"{ARCHIVE}2016-and-Prior-ISCR-Hearing-Decisions-1/", "2016 and Prior ISCR Hearing Decisions - 1",
                      [["04-08547.h1.pdf", "126891", 1]]),
            self.page(f"{ARCHIVE}2016-and-Prior-ISCR-Hearing-Decisions-16/", "2016 and Prior ISCR Hearing Decisions - 16",
                      [["04-08547.h1.pdf", "150442", 1]]))
        rows, report = self.build(capture)
        self.assertEqual(len(rows[0]["source_url_alternates"]), 1)
        self.assertIsNone(rows[0]["source_listing_title"], "a contested year must not bound the era")
        self.assertTrue(rows[0]["listing_conflict"])
        self.assertEqual(report["listing_conflicts"], 1)

    def test_a_dated_listing_is_preferred_over_an_archive_page(self) -> None:
        self.decisions("12-02471.h1_denied_f")
        capture = self.capture(
            self.page(f"{ARCHIVE}2016-and-Prior-ISCR-Hearing-Decisions-1/", "2016 and Prior ISCR Hearing Decisions - 1",
                      [["12-02471.h1.pdf", "126000", 1]]),
            self.page(f"{HEARINGS}2019-ISCR-Hearing-Decisions/", "2019 ISCR Hearing Decisions",
                      [["12-02471.h1.pdf", "113184", 1]]))
        rows, _ = self.build(capture)
        self.assertEqual(rows[0]["source_listing_title"], "2019 ISCR Hearing Decisions")
        self.assertFalse(rows[0]["listing_conflict"])

    def test_pages_and_links_outside_the_allowlist_are_refused(self) -> None:
        self.decisions("19-02096.a1_denied_f", "19-02097.h1_denied_f")
        capture = self.capture(
            self.page("https://doha-mirror.example.com/decisions/", "Mirror", [["19-02096.a1.pdf", "1", 1]]),
            self.page(f"{DOHA}/Some-Other-Section/", "Other", [["19-02096.a1.pdf", "2", 1]]),
            self.page(f"{HEARINGS}2019-ISCR-Hearing-Decisions/", "2019 ISCR Hearing Decisions",
                      [["19-02097.h1.html", "3", 1], ["not a case.pdf", "4", 1], ["19-02096.a1.pdf", "219192", 1]]))
        rows, report = self.build(capture)
        self.assertEqual([row["document_id"] for row in rows], ["doc-19-02096.a1_denied_f"])
        self.assertEqual(rows[0]["source_url"], f"{HEARINGS}2019-ISCR-Hearing-Decisions/FileId/219192/")
        self.assertEqual(len(report["pages_rejected"]), 2)
        self.assertEqual(report["links_rejected"], 2)
        self.assertEqual(report["unmatched_count"], 1)

    def test_listed_decisions_the_library_lacks_are_reported(self) -> None:
        self.decisions("19-02096.a1_denied_f")
        capture = self.capture(
            self.page(f"{HEARINGS}2019-ISCR-Hearing-Decisions/", "2019 ISCR Hearing Decisions",
                      [["19-02096.a1.pdf", "219192", 1], ["19-02100.h1.pdf", "219200", 1],
                       ["19-02101.a1.pdf", "219201", 1]]),
            self.page(f"{ARCHIVE}2016-and-Prior-ISCR-Hearing-Decisions-1/", "2016 and Prior ISCR Hearing Decisions - 1",
                      [["19-02100.h1.pdf", "126000", 1]]))
        missing, report = self.missing(capture)
        self.assertEqual([item["case_key"] for item in missing], ["19-02100.h1", "19-02101.a1"])
        self.assertEqual(missing[0]["decision_level"], "hearing")
        self.assertEqual(missing[1]["decision_level"], "appeal")
        # One decision on two listings is one missing decision with both URLs.
        self.assertEqual(len(missing[0]["source_urls"]), 2)
        self.assertEqual(report["listed_decisions"], 3)
        self.assertEqual(report["not_in_library_count"], 2)
        self.assertEqual(report["not_in_library_by_level"], {"hearing": 1, "appeal": 1})

    def test_the_same_decision_at_another_level_is_still_missing(self) -> None:
        self.decisions("19-02096.h1_denied_f")
        capture = self.capture(self.page(f"{HEARINGS}2019-ISCR-Hearing-Decisions/", "2019 ISCR Hearing Decisions",
                                         [["19-02096.h1.pdf", "1", 1], ["19-02096.a1.pdf", "2", 1]]))
        missing, _ = self.missing(capture)
        self.assertEqual([item["case_key"] for item in missing], ["19-02096.a1"])

    def test_a_non_pdf_posting_counts_as_listed_but_never_as_a_source_url(self) -> None:
        self.decisions()
        capture = self.capture(self.page(f"{HEARINGS}2019-ISCR-Hearing-Decisions/", "2019 ISCR Hearing Decisions",
                                         [["19-02097.h1.html", "3", 1]]))
        rows, missing, report = build_ledger(self.library, [capture], self.registry, {})
        self.assertEqual(rows, [])
        self.assertEqual(missing[0]["formats"], ["html"])
        self.assertEqual(report["links_rejected"], 1)

    def test_links_outside_the_allowlist_never_count_as_missing(self) -> None:
        self.decisions()
        capture = self.capture(self.page("https://doha-mirror.example.com/decisions/", "Mirror",
                                         [["19-02096.a1.pdf", "1", 1]]))
        missing, report = self.missing(capture)
        self.assertEqual(missing, [])
        self.assertEqual(report["listed_decisions"], 0)

    def test_unparseable_library_stems_are_counted_so_missing_can_be_doubted(self) -> None:
        self.decisions("ISCR Case No 08-07664", "19-02096.a1_denied_f")
        capture = self.capture(self.page(f"{HEARINGS}2019-ISCR-Hearing-Decisions/", "2019 ISCR Hearing Decisions",
                                         [["19-02096.a1.pdf", "1", 1]]))
        _, report = self.missing(capture)
        self.assertEqual(report["library_records_unkeyed"], 1)
        self.assertEqual(report["not_in_library_count"], 0)

    def test_case_year_reads_the_two_digit_case_prefix(self) -> None:
        self.assertEqual(case_year("19-02096.a1"), "2019")
        self.assertEqual(case_year("98-00123.h1"), "1998")
        self.assertEqual(case_year("04-08547-sd.h1"), "2004")

    def test_summary_groups_by_collection_and_case_year(self) -> None:
        self.decisions("19-02096.h1_denied_f")
        capture = self.capture(
            self.page(f"{HEARINGS}2019-ISCR-Hearing-Decisions/", "2019 ISCR Hearing Decisions",
                      [["19-02096.h1.pdf", "1", 1], ["19-02100.h1.pdf", "2", 1]]),
            self.page(f"{APPEALS}2019-DOHA-Appeal-Board/", "2019 DOHA Appeal Board",
                      [["18-01000.a1.pdf", "3", 1], ["19-02101.a1.pdf", "4", 1]]))
        missing, report = self.missing(capture)
        self.assertEqual({item["case_key"]: item["group"] for item in missing},
                         {"18-01000.a1": "DOHA Appeal Board Decisions", "19-02100.h1": "ISCR Hearing Decisions",
                          "19-02101.a1": "DOHA Appeal Board Decisions"})
        groups = summarize_missing(missing, report)["groups"]
        self.assertEqual((groups["ISCR Hearing Decisions"]["not_held"], groups["ISCR Hearing Decisions"]["listed"]), (1, 2))
        self.assertEqual(groups["DOHA Appeal Board Decisions"]["by_case_year"], {"2018": 1, "2019": 1})

    def test_listings_report_what_is_not_held_including_fully_held_pages(self) -> None:
        self.decisions("19-02096.h1_x", "19-02097.h1_x", "19-02098.h1_x", "20-00001.h1_x")
        capture = self.capture(
            self.page(f"{HEARINGS}2019-ISCR-Hearing-Decisions/", "2019 ISCR Hearing Decisions",
                      [["19-02096.h1.pdf", "1", 1], ["19-02097.h1.pdf", "2", 1],
                       ["19-02098.h1.pdf", "3", 1], ["19-02099.h1.pdf", "4", 1]]),
            self.page(f"{HEARINGS}2020-ISCR-Hearing-Decisions/", "2020 ISCR Hearing Decisions",
                      [["20-00001.h1.pdf", "5", 1]]))
        missing, report = self.missing(capture)
        rows = {row["listing_title"]: row for row in summarize_missing(missing, report)["by_listing"]}
        self.assertEqual(rows["2019 ISCR Hearing Decisions"]["share_not_held"], 0.25)
        self.assertEqual(rows["2020 ISCR Hearing Decisions"]["not_held"], 0)
        self.assertNotIn("suspect_capture_gap", rows["2019 ISCR Hearing Decisions"])

    def test_variants_say_whether_a_suffix_or_the_decision_number_differs(self) -> None:
        self.decisions("19-00803-SD.h1_x", "19-00900.h1_x", "19-00960.a1_x")
        capture = self.capture(self.page(f"{HEARINGS}2019-ISCR-Hearing-Decisions/", "2019 ISCR Hearing Decisions",
                                         [["19-00803.h1.pdf", "1", 1], ["19-00900.h2.pdf", "2", 1],
                                          ["19-00950.h1.htm", "3", 1], ["19-00960.h1.pdf", "4", 1]]))
        missing, report = self.missing(capture)
        by_key = {item["case_key"]: item for item in missing}
        self.assertEqual(by_key["19-00803.h1"]["held_variants"], [{"case_key": "19-00803-sd.h1", "differs_by": "suffix"}])
        # A remand decision (h2) is a separate ruling from h1, not a naming mismatch.
        self.assertEqual(by_key["19-00900.h2"]["held_variants"], [{"case_key": "19-00900.h1", "differs_by": "decision_number"}])
        # Holding the appeal does not stand in for the hearing decision.
        self.assertEqual(by_key["19-00960.h1"]["held_variants"], [])
        summary = summarize_missing(missing, report)
        self.assertEqual(summary["held_variant_kinds"], {"decision_number": 1, "suffix": 1})
        self.assertEqual(summary["non_pdf_only_sample"], ["19-00950.h1"])
        text = format_summary(summary, dict(report, library_records_unkeyed=3))
        self.assertIn("WARNING: 3 library records", text)
        self.assertIn("19-00803.h1  held: 19-00803-sd.h1 (suffix)", text)
        self.assertIn("== ISCR Hearing Decisions:", text)

    def test_byte_verification_inputs_explain_a_zero_count(self) -> None:
        self.decisions("19-02096.a1_denied_f")
        capture = self.capture(self.page(f"{APPEALS}2019-DOHA-Appeal-Board/", "2019 DOHA Appeal Board",
                                         [["19-02096.a1.pdf", "1", 1]]))
        _, missing, report = build_ledger(self.library, [capture], self.registry, {"some-other-id": "a" * 64})
        inputs = report["byte_verification_inputs"]
        self.assertFalse(inputs["download_progress_found"])
        self.assertEqual((inputs["human_hashes_supplied"], inputs["human_hash_ids_in_manifest"]), (1, 0))
        text = format_summary(summarize_missing(missing, report), report)
        self.assertIn("WARNING: hashes were supplied but no decision is byte-verified", text)
    def test_a_cross_posted_decision_is_grouped_by_its_level_not_its_page(self) -> None:
        self.decisions()
        capture = self.capture(
            self.page(f"{HEARINGS}Archived/2016-and-Prior-4/", "2016 and Prior ISCR Hearing Decisions - 4",
                      [["08-01000.h1.pdf", "1", 1]]),
            self.page(f"{APPEALS}2016-and-Prior-DOHA-Appeal-Board/", "2016 and Prior DOHA Appeal Board",
                      [["08-01000.h1.pdf", "2", 1], ["08-01000.a1.pdf", "3", 1]]))
        missing, report = self.missing(capture)
        by_key = {item["case_key"]: item for item in missing}
        self.assertEqual(by_key["08-01000.h1"]["group"], "ISCR Hearing Decisions")
        self.assertEqual(by_key["08-01000.h1"]["listed_under"], ["DOHA Appeal Board Decisions", "ISCR Hearing Decisions"])
        self.assertEqual(by_key["08-01000.a1"]["group"], "DOHA Appeal Board Decisions")
        self.assertEqual(report["listed_under_both_collections"], 1)
        summary = summarize_missing(missing, report)
        self.assertEqual(set(summary["groups"]), {"ISCR Hearing Decisions", "DOHA Appeal Board Decisions"})
        self.assertEqual(summary["groups"]["ISCR Hearing Decisions"]["listed"], 1)


if __name__ == "__main__":
    unittest.main()
