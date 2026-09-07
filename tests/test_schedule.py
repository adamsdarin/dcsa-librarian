from __future__ import annotations

import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock

from library_custodian.runner import (
    EXIT_FINDINGS,
    EXIT_NO_FINDINGS,
    EXIT_SOURCE_ERROR,
    render_text_summary,
    run_scheduled_job,
)
from library_custodian.schedule import (
    Job,
    cron_expression,
    due_today,
    expand_days,
    load_schedule,
    period_key,
    render,
    satisfies_expectation,
    to_utc,
)


PAGE_URL = "https://www.dcsa.mil/resources/"


def job(**overrides: object) -> Job:
    base = {
        "id": "j",
        "description": "",
        "local_times": ("09:00",),
        "days_of_month": "1",
        "sources": (),
        "once_per_period": None,
        "expect": None,
        "rationale": "",
    }
    base.update(overrides)
    return Job(**base)  # type: ignore[arg-type]


class ConversionTests(unittest.TestCase):
    def test_eastern_morning_converts_to_utc_afternoon(self) -> None:
        self.assertEqual(to_utc("09:00", -5), (14, 0, 0))
        self.assertEqual(to_utc("12:00", -5), (17, 0, 0))
        self.assertEqual(to_utc("15:00", -5), (20, 0, 0))

    def test_conversion_reports_a_day_shift(self) -> None:
        self.assertEqual(to_utc("21:00", -5), (2, 0, 1))

    def test_declared_jobs_render_the_expected_crons(self) -> None:
        schedule = load_schedule(Path("config/schedule.json"))
        rendered = {j.id: cron_expression(j, schedule.utc_offset_hours) for j in schedule.jobs}
        self.assertEqual(rendered["monthly-scan"], "0 14 1 * *")
        self.assertEqual(rendered["voi-release-watch"], "0 14,17,20 28-31,1-3 * *")

    def test_day_crossing_conversion_is_refused_not_silently_wrong(self) -> None:
        with self.assertRaises(ValueError) as caught:
            cron_expression(job(local_times=("21:00",), days_of_month="1"), -5)
        self.assertIn("crosses midnight", str(caught.exception))

    def test_mixed_minutes_cannot_share_one_expression(self) -> None:
        with self.assertRaises(ValueError):
            cron_expression(job(local_times=("09:00", "09:30")), -5)


class SchtasksRenderingTests(unittest.TestCase):
    def test_ranges_expand_because_schtasks_cannot_read_them(self) -> None:
        self.assertEqual(expand_days("28-31,1-3"), "28,29,30,31,1,2,3")

    def test_single_day_passes_through(self) -> None:
        self.assertEqual(expand_days("1"), "1")

    def test_out_of_range_day_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            expand_days("30-33")

    def test_rendered_tasks_carry_expanded_days(self) -> None:
        schedule = load_schedule(Path("config/schedule.json"))
        output = render("schtasks", schedule, "run-scan.cmd")
        self.assertIn("/d 28,29,30,31,1,2,3", output)
        self.assertNotIn("28-31", output)

    def test_github_actions_is_not_an_available_runner(self) -> None:
        # DCSA blocks hosted CI runners; a CI adapter would fail every run
        # while still looking like monitoring
        schedule = load_schedule(Path("config/schedule.json"))
        with self.assertRaises(ValueError):
            render("github-actions", schedule, "x")


class TextReportTests(unittest.TestCase):
    def _summary(self, **overrides: object) -> dict:
        base = {
            "job_id": "watch",
            "period": "2026-03",
            "ran_at": "2026-03-31T14:00:00+00:00",
            "sources_scanned": ["dcsa-nisp-tools"],
            "sources_errored": [],
            "manifest_checked": True,
            "findings": {"changed": [], "new_urls": [], "candidates": []},
        }
        base.update(overrides)
        return base

    def test_an_unreachable_source_is_never_reported_as_clean(self) -> None:
        text = render_text_summary(self._summary(sources_errored=["dcsa-nisp-tools"]), EXIT_SOURCE_ERROR)
        self.assertIn("INCOMPLETE", text)
        self.assertIn("did NOT clear those sources", text)
        self.assertNotIn("No changes detected", text)

    def test_findings_are_listed_with_their_urls(self) -> None:
        text = render_text_summary(
            self._summary(findings={"changed": ["https://x/a.pdf"], "new_urls": [], "candidates": ["https://x/a.pdf"]}),
            EXIT_FINDINGS,
        )
        self.assertIn("1 item(s) need review", text)
        self.assertIn("https://x/a.pdf", text)

    def test_a_clean_scan_says_so_plainly(self) -> None:
        self.assertIn("No changes detected", render_text_summary(self._summary(), EXIT_NO_FINDINGS))


class PeriodTests(unittest.TestCase):
    def _key(self, iso: str) -> str | None:
        return period_key(job(once_per_period="month"), datetime.fromisoformat(iso).replace(tzinfo=timezone.utc))

    def test_month_end_and_early_next_month_share_a_period(self) -> None:
        # 28-31 March and 1-3 April are both hunting the March issue
        self.assertEqual(self._key("2026-03-31T14:00:00"), "2026-03")
        self.assertEqual(self._key("2026-04-02T14:00:00"), "2026-03")

    def test_mid_month_belongs_to_its_own_period(self) -> None:
        self.assertEqual(self._key("2026-04-15T14:00:00"), "2026-04")

    def test_period_rolls_back_across_the_year_boundary(self) -> None:
        self.assertEqual(self._key("2026-01-02T14:00:00"), "2025-12")

    def test_jobs_without_a_period_have_no_key(self) -> None:
        self.assertIsNone(period_key(job(), datetime.now(timezone.utc)))


class DueTodayTests(unittest.TestCase):
    def test_ranges_and_lists(self) -> None:
        watch = job(days_of_month="28-31,1-3")
        self.assertTrue(due_today(watch, datetime(2026, 3, 30).date()))
        self.assertTrue(due_today(watch, datetime(2026, 4, 2).date()))
        self.assertFalse(due_today(watch, datetime(2026, 4, 15).date()))


class ExpectationTests(unittest.TestCase):
    def test_percent_encoding_does_not_defeat_the_match(self) -> None:
        self.assertTrue(
            satisfies_expectation("https://x/Portals/128/260331%20VOI%20Newsletter.pdf", "voi newsletter")
        )

    def test_an_unrelated_document_does_not_satisfy(self) -> None:
        self.assertFalse(satisfies_expectation("https://x/docs/new-job-aid.pdf", "voi newsletter"))

    def test_no_expectation_means_any_finding_satisfies(self) -> None:
        self.assertTrue(satisfies_expectation("https://x/anything.pdf", None))


class StubFetcher:
    links: list[str] = ["/docs/known.pdf"]
    fail = False

    def __init__(self, **_kwargs: object) -> None:
        pass

    def get(self, url: str) -> tuple[bytes, dict[str, str]]:
        if type(self).fail:
            raise OSError("source unreachable")
        anchors = "".join(f'<a href="{href}">doc</a>' for href in type(self).links)
        return anchors.encode(), {"content_type": "text/html", "final_url": url, "etag": "", "last_modified": "", "content_length": ""}

    def head(self, url: str) -> dict[str, str]:
        return {"content_type": "application/pdf", "etag": "v1", "last_modified": "", "content_length": "", "final_url": url}


class ScheduledRunTests(unittest.TestCase):
    def _fixture(self, root: Path, expect: str | None = None) -> tuple[Path, Path]:
        registry = root / "registry.json"
        registry.write_text(
            json.dumps(
                {
                    "settings": {"delay_seconds": 0},
                    "sources": [{"id": "dcsa-test", "enabled": True, "url": PAGE_URL, "allowed_domains": ["dcsa.mil"], "max_depth": 0, "max_pages": 1}],
                }
            ),
            encoding="utf-8",
        )
        schedule = root / "schedule.json"
        schedule.write_text(
            json.dumps(
                {
                    "timezone": "America/New_York",
                    "utc_offset_hours": -5,
                    "jobs": [
                        {
                            "id": "watch",
                            "description": "",
                            "local_times": ["09:00", "12:00", "15:00"],
                            "days_of_month": "28-31,1-3",
                            "sources": ["dcsa-test"],
                            "once_per_period": "month",
                            "expect": expect,
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        return registry, schedule

    def _run(self, root: Path, registry: Path, schedule: Path, when: str) -> tuple[dict, int]:
        return run_scheduled_job(
            job_id="watch",
            schedule_path=schedule,
            library_root=None,
            registry_path=registry,
            state_dir=root / "state",
            quarantine_dir=root / "quarantine",
            now=datetime.fromisoformat(when).replace(tzinfo=timezone.utc),
        )

    def test_window_closes_once_the_issue_is_found_and_reopens_next_period(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            registry, schedule = self._fixture(root)
            with mock.patch("library_custodian.discovery.Fetcher", StubFetcher):
                StubFetcher.links = ["/docs/known.pdf"]
                StubFetcher.fail = False

                # first poll of the window only establishes a baseline
                first, code = self._run(root, registry, schedule, "2026-03-30T14:00:00")
                self.assertEqual(code, EXIT_NO_FINDINGS)
                self.assertIsNone(first["period_marker"])
                self.assertEqual(first["period"], "2026-03")

                # the issue lands: a new URL appears on the page
                StubFetcher.links = ["/docs/known.pdf", "/docs/260331-voi.pdf"]
                second, code = self._run(root, registry, schedule, "2026-03-31T14:00:00")
                self.assertEqual(code, EXIT_FINDINGS)
                self.assertIn("https://www.dcsa.mil/docs/260331-voi.pdf", second["findings"]["new_urls"])
                self.assertIsNotNone(second["period_marker"])

                # remaining polls in the window have nothing left to do,
                # including the ones that fall in early April
                third, code = self._run(root, registry, schedule, "2026-04-02T14:00:00")
                self.assertEqual(code, EXIT_NO_FINDINGS)
                self.assertEqual(third["skipped"], "period_already_satisfied")

                # the next month's window is a fresh period and polls again
                fourth, code = self._run(root, registry, schedule, "2026-04-29T14:00:00")
                self.assertNotIn("skipped", fourth)
                self.assertEqual(fourth["period"], "2026-04")

    def test_an_unrelated_document_does_not_close_the_window(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            registry, schedule = self._fixture(root, expect="voi newsletter")
            with mock.patch("library_custodian.discovery.Fetcher", StubFetcher):
                StubFetcher.fail = False
                StubFetcher.links = ["/docs/known.pdf"]
                self._run(root, registry, schedule, "2026-03-29T14:00:00")

                # DCSA posts something unrelated mid-window
                StubFetcher.links = ["/docs/known.pdf", "/docs/new-job-aid.pdf"]
                unrelated, code = self._run(root, registry, schedule, "2026-03-30T14:00:00")
                self.assertEqual(code, EXIT_FINDINGS)
                self.assertEqual(unrelated["satisfying_findings"], [])
                self.assertIsNone(unrelated["period_marker"], "an unrelated document must not end the polling")

                # the awaited issue lands on the 31st and is still caught
                StubFetcher.links = ["/docs/known.pdf", "/docs/new-job-aid.pdf", "/docs/260331%20VOI%20Newsletter.pdf"]
                awaited, code = self._run(root, registry, schedule, "2026-03-31T14:00:00")
                self.assertEqual(code, EXIT_FINDINGS)
                self.assertEqual(len(awaited["satisfying_findings"]), 1)
                self.assertIsNotNone(awaited["period_marker"])

    def test_a_failed_source_leaves_the_window_open(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            registry, schedule = self._fixture(root)
            with mock.patch("library_custodian.discovery.Fetcher", StubFetcher):
                StubFetcher.links = ["/docs/known.pdf"]
                StubFetcher.fail = True
                summary, code = self._run(root, registry, schedule, "2026-03-30T14:00:00")

            self.assertEqual(code, EXIT_SOURCE_ERROR)
            self.assertEqual(summary["sources_errored"], ["dcsa-test"])
            # an incomplete scan must not suppress the remaining polls
            self.assertIsNone(summary["period_marker"])


if __name__ == "__main__":
    unittest.main()
