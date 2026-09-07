from __future__ import annotations

import unittest
import urllib.error
from unittest import mock

from library_custodian.discovery import Fetcher


# The policy DCSA actually publishes, captured 2026-09-07. Neither
# /Industrial-Security/ nor /FCL/ is disallowed; only ia_archiver is banned
# outright. Any refusal of those two paths is our bug, not DCSA's policy.
DCSA_ROBOTS = b"""Sitemap: /DesktopModules/SiteData/SiteMap.ashx
User-agent: *
Allow: /Components/Administrative-Investigations/
Disallow: *captcha*
Disallow: /*Print.aspx
Disallow: /*.axd$
Disallow: /bin/
Disallow: /Error/
Disallow: /Controls/
Disallow: /Utility/
Disallow: /Admin/
Disallow: /App_Code/
Disallow: /Components/
Disallow: /Config/
Disallow: /Documentation/
Disallow: /Install/
Disallow: /Providers/
User-agent: ia_archiver
Disallow:/
"""

NISP_TOOLS = "https://www.dcsa.mil/Industrial-Security/National-Industrial-Security-Program-Oversight/NISP-Tools-Resources/"
FCL = "https://www.dcsa.mil/FCL/Maintaining-Personnel-Security-Clearances/"
UA = "DCSA-Library-Custodian/0.1 (+local-governance-audit)"


class FakeResponse:
    def __init__(self, body: bytes) -> None:
        self._body = body

    def read(self, *_args: object) -> bytes:
        return self._body

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, *_exc: object) -> bool:
        return False


def fetcher() -> Fetcher:
    return Fetcher(user_agent=UA, timeout=5, max_bytes=1_000_000, delay_seconds=0, respect_robots=True)


class RobotsTests(unittest.TestCase):
    def test_the_published_policy_permits_the_pages_we_scan(self) -> None:
        with mock.patch("library_custodian.discovery.urllib.request.urlopen", return_value=FakeResponse(DCSA_ROBOTS)):
            probe = fetcher()
            probe._check_allowed(NISP_TOOLS)
            probe._check_allowed(FCL)

    def test_a_genuinely_disallowed_path_is_still_refused(self) -> None:
        with mock.patch("library_custodian.discovery.urllib.request.urlopen", return_value=FakeResponse(DCSA_ROBOTS)):
            with self.assertRaises(PermissionError) as caught:
                fetcher()._check_allowed("https://www.dcsa.mil/Admin/secret.pdf")
        self.assertIn("disallows", str(caught.exception))

    def test_robots_is_requested_as_the_agent_we_declare(self) -> None:
        # the actual defect: the policy was fetched as Python-urllib while every
        # other request went out as this crawler, so a CDN could 403 the check
        seen: list[str] = []

        def capture(request, timeout=None):  # noqa: ANN001
            seen.append(request.get_header("User-agent"))
            return FakeResponse(DCSA_ROBOTS)

        with mock.patch("library_custodian.discovery.urllib.request.urlopen", side_effect=capture):
            fetcher()._check_allowed(NISP_TOOLS)
        self.assertEqual(seen, [UA])
        self.assertNotIn("Python-urllib", seen[0])

    def test_an_unreadable_policy_is_not_reported_as_a_policy_decision(self) -> None:
        error = urllib.error.HTTPError(NISP_TOOLS, 403, "Forbidden", {}, None)
        with mock.patch("library_custodian.discovery.urllib.request.urlopen", side_effect=error):
            with self.assertRaises(PermissionError) as caught:
                fetcher()._check_allowed(NISP_TOOLS)
        message = str(caught.exception)
        self.assertIn("could not read robots.txt (HTTP 403)", message)
        self.assertIn("policy is unknown", message)
        self.assertNotIn("disallows", message)

    def test_a_site_with_no_robots_file_is_not_treated_as_forbidden(self) -> None:
        error = urllib.error.HTTPError(NISP_TOOLS, 404, "Not Found", {}, None)
        with mock.patch("library_custodian.discovery.urllib.request.urlopen", side_effect=error):
            fetcher()._check_allowed(NISP_TOOLS)

    def test_the_policy_is_fetched_once_per_origin(self) -> None:
        with mock.patch(
            "library_custodian.discovery.urllib.request.urlopen", return_value=FakeResponse(DCSA_ROBOTS)
        ) as opener:
            probe = fetcher()
            probe._check_allowed(NISP_TOOLS)
            probe._check_allowed(FCL)
        self.assertEqual(opener.call_count, 1)


if __name__ == "__main__":
    unittest.main()
