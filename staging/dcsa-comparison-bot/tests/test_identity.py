from __future__ import annotations

import unittest

from dcsa_comparison.identity import (
    compare_editions,
    document_numbers,
    edition_tokens,
    jaccard,
    series_key,
    series_tokens,
    split_runs,
)


class DocumentNumberTests(unittest.TestCase):
    def test_reads_mixed_case_and_concatenated_dod_numbers(self) -> None:
        self.assertIn("dod:i-5205.16", document_numbers("DoDI 5205.16 Insider Threat Program"))
        self.assertIn("dod:i-5205.16", document_numbers("DoDI5205.16_InsiderThreat.pdf"))

    def test_reads_hyphenated_and_spaced_series(self) -> None:
        self.assertIn("sead:3", document_numbers("SEAD-3-Reporting-Desktop-Aid-revisedMay2024"))
        self.assertIn("sead:3", document_numbers("SEAD 3 Reporting Desktop Aid"))

    def test_nist_suffix_does_not_leak_into_the_number(self) -> None:
        self.assertIn("nist-sp:800-61", document_numbers("NIST SP 800-61r3 Incident Response"))
        self.assertIn("nist-sp:800-61", document_numbers("NIST SP 800-61 Rev 2 Guide"))

    def test_cfr_and_isl_numbers(self) -> None:
        self.assertIn("cfr:32-117", document_numbers("32 CFR Part 117 (up to date as of 7-24-2026)"))
        self.assertEqual(document_numbers("ISL 2024-01"), ["isl:2024-01"])

    def test_unparseable_text_yields_no_number_rather_than_a_guess(self) -> None:
        self.assertEqual(document_numbers("workplaceviolence"), [])


class EditionOrderingTests(unittest.TestCase):
    def order(self, left: str, right: str) -> dict:
        return compare_editions(edition_tokens(left), edition_tokens(right))

    def test_dotted_version_suffix_is_newer(self) -> None:
        result = self.order("IC Tech Spec ICD-ICS 705 v1.5", "IC Tech Spec ICD-ICS 705 v1.5.1")
        self.assertEqual((result["order"], result["kind"]), (1, "version"))

    def test_compact_nist_revision_outranks_spelled_revision(self) -> None:
        result = self.order("NIST SP 800-61 Rev 2 Guide", "NIST SP 800-61r3 Recommendations")
        self.assertEqual((result["order"], result["kind"]), (1, "revision"))

    def test_month_name_edition_beats_iso_edition_date(self) -> None:
        result = self.order("SEAD 3 Reporting Desktop Aid 2022-04", "SEAD-3-Aid-revisedMay2024")
        self.assertEqual((result["order"], result["kind"]), (1, "edition_date"))

    def test_reverse_direction_is_reported_as_older(self) -> None:
        self.assertEqual(self.order("Guide October 2024", "Guide Dec 2020")["order"], -1)

    def test_no_shared_token_kind_is_undetermined_not_a_guess(self) -> None:
        result = self.order("Physical Security Job Aid", "Physical Security Job Aid v2")
        self.assertIsNone(result["order"])

    def test_equal_editions_report_zero(self) -> None:
        self.assertEqual(self.order("Aid v2.0", "Aid v2.0")["order"], 0)


class SeriesKeyTests(unittest.TestCase):
    def test_edition_markers_and_publication_artifacts_are_stripped(self) -> None:
        self.assertEqual(
            series_key("Cleared CUI Quick Reference Guide Dec 2020"),
            series_key("Cleared CUI Quick Reference Guide October 2024"),
        )
        self.assertNotIn("508", series_key("Insider Threat Trifold_Final_508"))

    def test_run_splitting_exposes_concatenated_editions(self) -> None:
        self.assertEqual(split_runs("revisedMay2024"), "revised May 2024")

    def test_jaccard_is_zero_against_an_empty_side(self) -> None:
        self.assertEqual(jaccard(series_tokens("Guide"), frozenset()), 0.0)


if __name__ == "__main__":
    unittest.main()
