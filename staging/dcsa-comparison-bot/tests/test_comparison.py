from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from dcsa_comparison.baseline import build_baseline
from dcsa_comparison.common import write_jsonl
from dcsa_comparison.compare import compare_candidates, load_candidates
from dcsa_comparison.diffing import diff_documents, split_sections
from dcsa_comparison.propose import build_proposals, check_decisions


MANIFEST = [
    {
        "document_id": "nist-sp-800-61-rev2",
        "title": "NIST SP 800-61 Rev 2 Computer Security Incident Handling Guide",
        "robot_text_path": "ROBOT_READABLE_DIRECTORY/TEXT/nist-800-61r2.txt",
        "collection_id": "nist",
        "current_status": "current",
        "authority_role": "incorporated_framework",
    },
    {
        "document_id": "sead-3-desktop-aid-2022-04",
        "title": "SEAD 3 Reporting Desktop Aid 2022-04",
        "robot_text_path": "ROBOT_READABLE_DIRECTORY/TEXT/sead3-aid.txt",
        "collection_id": "job_aids",
        "current_status": "current",
    },
    {
        "document_id": "isl-2021-02",
        "title": "ISL 2021-02 Reporting Requirements",
        "robot_text_path": "ROBOT_READABLE_DIRECTORY/TEXT/isl-2021-02.txt",
        "collection_id": "isl_current",
        "current_status": "current",
    },
    {
        "document_id": "cleared-cui-qrg-dec-2020",
        "title": "Cleared CUI Quick Reference Guide Dec 2020",
        "robot_text_path": "ROBOT_READABLE_DIRECTORY/TEXT/cleared-cui-qrg.txt",
        "collection_id": "cui",
        "current_status": "current",
    },
]

DISCOVERED = [
    {
        "url": "https://csrc.nist.gov/pubs/sp/800/61/r3/final",
        "anchor_text": "NIST SP 800-61r3 Incident Response Recommendations",
        "inferred_filename": "NIST SP 800-61r3 Incident Response Recommendations.pdf",
        "status": "missing_from_manifest",
    },
    {
        "url": "https://www.dcsa.mil/portals/SEAD-3-Reporting-Desktop-Aid-revisedMay2024.pdf",
        "anchor_text": "SEAD 3 Reporting Desktop Aid revised May 2024",
        "inferred_filename": "SEAD-3-Reporting-Desktop-Aid-revisedMay2024.pdf",
        "status": "missing_from_manifest",
    },
    {
        "url": "https://www.dcsa.mil/portals/ISL-2024-01.pdf",
        "anchor_text": "ISL 2024-01",
        "inferred_filename": "ISL 2024-01.pdf",
        "status": "missing_from_manifest",
    },
    {
        "url": "https://www.dodcui.mil/cleared-cui-qrg-october-2024.pdf",
        "anchor_text": "Cleared CUI Quick Reference Guide October 2024",
        "inferred_filename": "Cleared CUI Quick Reference Guide October 2024.pdf",
        "status": "missing_from_manifest",
    },
]


def _report(directory: Path) -> dict:
    manifest = directory / "manifest.jsonl"
    discovered = directory / "candidates.jsonl"
    write_jsonl(manifest, MANIFEST)
    write_jsonl(discovered, DISCOVERED)
    baseline = build_baseline(manifest)
    candidates = load_candidates(paths=[], candidates_jsonl=discovered)
    return compare_candidates(baseline, candidates)


class ComparisonTests(unittest.TestCase):
    def setUp(self) -> None:
        self._temp = tempfile.TemporaryDirectory()
        self.directory = Path(self._temp.name)
        self.report = _report(self.directory)
        self.by_candidate = {finding["candidate_id"]: finding for finding in self.report["findings"]}

    def tearDown(self) -> None:
        self._temp.cleanup()

    def test_shared_document_number_pairs_deterministically(self) -> None:
        finding = self.by_candidate["NIST SP 800-61r3 Incident Response Recommendations.pdf"]
        self.assertEqual(finding["incumbent_document_id"], "nist-sp-800-61-rev2")
        self.assertEqual(finding["relationship"], "newer_edition_candidate")
        self.assertEqual(finding["basis"], "deterministic")
        self.assertEqual(finding["signals"]["match_route"], "document_number")

    def test_concatenated_date_edition_pairs_deterministically(self) -> None:
        finding = self.by_candidate["SEAD-3-Reporting-Desktop-Aid-revisedMay2024.pdf"]
        self.assertEqual(finding["incumbent_document_id"], "sead-3-desktop-aid-2022-04")
        self.assertEqual(finding["basis"], "deterministic")

    def test_title_routed_pairing_is_labelled_inferred(self) -> None:
        finding = self.by_candidate["Cleared CUI Quick Reference Guide October 2024.pdf"]
        self.assertEqual(finding["incumbent_document_id"], "cleared-cui-qrg-dec-2020")
        self.assertEqual(finding["basis"], "inferred")
        self.assertEqual(finding["signals"]["match_route"], "series_key")

    def test_two_in_force_isls_are_never_paired(self) -> None:
        """ISL 2024-01 does not supersede ISL 2021-02; both remain in force."""
        unmatched = {item["candidate_id"] for item in self.report["unmatched"]}
        self.assertIn("ISL 2024-01.pdf", unmatched)
        self.assertNotIn("ISL 2024-01.pdf", self.by_candidate)

    def test_a_binary_candidate_reports_that_no_content_was_compared(self) -> None:
        for finding in self.report["findings"]:
            self.assertEqual(finding["content_comparison"], "unavailable_no_candidate_text")

    def test_report_declares_it_published_and_wrote_nothing(self) -> None:
        self.assertFalse(self.report["publication_performed"])
        self.assertFalse(self.report["decisions_written"])


class ProposalTests(unittest.TestCase):
    def setUp(self) -> None:
        self._temp = tempfile.TemporaryDirectory()
        self.report = _report(Path(self._temp.name))

    def tearDown(self) -> None:
        self._temp.cleanup()

    def test_only_deterministic_newer_editions_become_decisions(self) -> None:
        payload = build_proposals(self.report, reviewer="Darin Adams")
        ids = {decision["source_document_id"] for decision in payload["archivist_metadata_decisions"]["decisions"]}
        self.assertEqual(ids, {"nist-sp-800-61-rev2", "sead-3-desktop-aid-2022-04"})
        self.assertTrue(any("inferred pairing withheld" in item["reason"] for item in payload["skipped"]))

    def test_inferred_pairings_require_an_explicit_opt_in(self) -> None:
        payload = build_proposals(self.report, reviewer="Darin Adams", include_inferred=True)
        ids = {decision["source_document_id"] for decision in payload["archivist_metadata_decisions"]["decisions"]}
        self.assertIn("cleared-cui-qrg-dec-2020", ids)

    def test_every_proposal_says_it_is_not_lifecycle_evidence(self) -> None:
        payload = build_proposals(self.report, reviewer="Darin Adams")
        for decision in payload["archivist_metadata_decisions"]["decisions"]:
            self.assertTrue(decision["requires_official_lifecycle_evidence"])
            self.assertIn("not from official lifecycle evidence", decision["note"])
            self.assertEqual(decision["evidence"][0]["evidence_type"], "candidate_location_only")

    def test_output_conforms_to_the_archivist_decision_contract(self) -> None:
        payload = build_proposals(self.report, reviewer="Darin Adams")
        self.assertEqual(check_decisions(payload), [])
        self.assertEqual(payload["proposal_state"], "proposed_not_applied")

    def test_an_unnamed_reviewer_is_refused(self) -> None:
        with self.assertRaises(ValueError):
            build_proposals(self.report, reviewer="   ")

    def test_accepting_a_subset_limits_the_output(self) -> None:
        accepted = {"NIST SP 800-61r3 Incident Response Recommendations.pdf::nist-sp-800-61-rev2"}
        payload = build_proposals(self.report, reviewer="Darin Adams", accepted_finding_ids=accepted)
        self.assertEqual(payload["counts"]["proposed_decisions"], 1)
        self.assertEqual(payload["counts"]["handoff_rows"], 1)


LEFT = """TIER: 3
STATUS: current
EFFECTIVE: 2020-09-01

1. PURPOSE
Construction standards for SCIFs.

2. ACOUSTIC PROTECTION
Amplified sound requires Sound Group 4.
"""

RIGHT = """TIER: 3
STATUS: current
EFFECTIVE: 2023-05-15

1. PURPOSE
Construction standards for SCIFs.

2. ACOUSTIC PROTECTION
Amplified sound requires Sound Group 4 with supplemental treatment.

3. INTRUSION DETECTION
An IDS shall be monitored continuously.
"""


class DiffTests(unittest.TestCase):
    def setUp(self) -> None:
        self._temp = tempfile.TemporaryDirectory()
        self.directory = Path(self._temp.name)
        self.left = self.directory / "left.txt"
        self.right = self.directory / "right.txt"
        self.left.write_text(LEFT, encoding="utf-8")
        self.right.write_text(RIGHT, encoding="utf-8")

    def tearDown(self) -> None:
        self._temp.cleanup()

    def test_header_fields_are_reported_separately_from_sections(self) -> None:
        report = diff_documents(self.left, self.right)
        self.assertEqual(report["header_changes"]["effective_date"], {"left": "2020-09-01", "right": "2023-05-15"})

    def test_changed_and_added_sections_are_distinguished(self) -> None:
        report = diff_documents(self.left, self.right)
        statuses = {section["heading"]: section["status"] for section in report["sections"]}
        self.assertEqual(statuses["2. ACOUSTIC PROTECTION"], "changed")
        self.assertEqual(statuses["3. INTRUSION DETECTION"], "added")
        self.assertEqual(statuses["1. PURPOSE"], "unchanged")

    def test_an_identical_document_reports_no_change(self) -> None:
        report = diff_documents(self.left, self.left)
        self.assertTrue(report["summary"]["substantively_identical"])

    def test_documents_without_headings_fall_back_to_form_feed_pages(self) -> None:
        sections = split_sections("plain text page one\fplain text page two")
        self.assertEqual([section["heading"] for section in sections], ["page 1", "page 2"])


if __name__ == "__main__":
    unittest.main()
