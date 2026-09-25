"""Acquire DOHA decisions the library does not hold into quarantine, through a browser.

DOHA's CDN refuses this project's HTTP fetcher (403, even for robots.txt), so the
bytes are fetched by a real Chrome: the page is opened on an official listing and
each decision is requested with the page's own fetch(), on Chrome's network stack.

What is fetched comes only from doha_not_in_library.jsonl, which holds URLs the
official listings published. Nothing is guessed from a case number. Every URL,
and the URL each response finally came from, must sit under a registry source's
path. Each file lands in quarantine with the same .intake.json package the
scheduled scans write, so the Archivist's intake plan can take it as it is.

Runs are resumable: every attempt is appended to the run's attempts.jsonl, and a
decision already acquired in that run is not requested again. A run stops after
a few consecutive refusals rather than keep asking a site that is saying no.

Nothing here writes to the library.
"""
from __future__ import annotations

import base64
import hashlib
import json
import re
import time
import urllib.parse
import urllib.robotparser
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterable, Protocol

from .discovery import WebItem, canonicalize_url, utc_now, write_intake_package
from .doha_provenance import GROUPS, _allowed_pages, _page_source, case_year

GROUP_FOLDERS = {"ISCR Hearing Decisions": "iscr-hearing-decisions",
                 "DOHA Appeal Board Decisions": "doha-appeal-board-decisions"}
LISTING_YEAR = re.compile(r"\b(19|20)\d{2}\b")
# Refusals in a row before the run stops: a CDN challenge page or a block looks
# the same for every request, and hammering it would only make that worse.
MAX_CONSECUTIVE_FAILURES = 5


@dataclass
class Response:
    status: int
    url: str
    headers: dict[str, str]
    body: bytes


class Transport(Protocol):
    def fetch(self, url: str) -> Response: ...


def listing_year(titles: Iterable[str]) -> int:
    """Newest year a decision's listings name: '2025 ISCR Hearing Decisions' -> 2025."""
    years = [int(match.group(0)) for title in titles for match in LISTING_YEAR.finditer(title)]
    return max(years, default=0)


def plan(not_held: Iterable[dict[str, Any]], groups: set[str] | None = None, limit: int | None = None
         ) -> list[dict[str, Any]]:
    """Order decisions newest listing first; within a year, hearings before appeals."""
    order = {group: index for index, group in enumerate(GROUPS.values())}
    chosen = [row for row in not_held if not groups or row.get("group") in groups]
    chosen.sort(key=lambda row: (-listing_year(row.get("listing_titles", [])),
                                 order.get(row.get("group"), len(order)), row["case_key"]))
    return chosen[:limit] if limit else chosen


def choose_url(row: dict[str, Any]) -> str:
    """Prefer a dated listing's URL over an 'and Prior' archive page's."""
    urls = sorted(row["source_urls"])
    return next((url for url in urls if "and-prior" not in url.casefold()), urls[0])


def read_attempts(path: Path) -> dict[str, dict[str, Any]]:
    done: dict[str, dict[str, Any]] = {}
    if path.is_file():
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                row = json.loads(line)
                if row.get("status") == "acquired":
                    done[row["case_key"]] = row
    return done


def _looks_like(body: bytes, fmt: str) -> bool:
    if fmt == "pdf":
        return body[:5] == b"%PDF-"
    return bool(body.strip())


def acquire(not_held: Iterable[dict[str, Any]], registry: dict[str, Any], run_dir: Path, transport: Transport,
            robots: urllib.robotparser.RobotFileParser, groups: set[str] | None = None, limit: int | None = None,
            delay_seconds: float = 4.0, max_bytes: int = 50_000_000,
            sleep: Callable[[float], None] = time.sleep) -> dict[str, Any]:
    """Fetch each planned decision into run_dir and write its intake package."""
    allowed = _allowed_pages(registry)
    sources = {source["id"]: source for source in registry.get("sources", [])}
    user_agent = str(registry.get("defaults", {}).get("user_agent", "*"))
    attempts_path = run_dir / "attempts.jsonl"
    done = read_attempts(attempts_path)
    counts = {"acquired": 0, "already_acquired": 0, "refused": 0, "skipped": 0}
    consecutive = 0
    stopped = None
    todo = plan(not_held, groups, limit)
    with attempts_path.open("a", encoding="utf-8", newline="\n") as log:
        def record(row: dict[str, Any]) -> None:
            log.write(json.dumps(row, separators=(",", ":")) + "\n")
            log.flush()

        for index, row in enumerate(todo):
            key = row["case_key"]
            if key in done:
                counts["already_acquired"] += 1
                continue
            url = canonicalize_url(choose_url(row))
            source_id = _page_source(url, allowed)
            attempt = {"case_key": key, "group": row.get("group"), "url": url, "at": utc_now()}
            if not source_id:
                counts["skipped"] += 1
                record(dict(attempt, status="skipped", reason="outside_registry_allowlist"))
                continue
            if not robots.can_fetch(user_agent, url):
                counts["skipped"] += 1
                record(dict(attempt, status="skipped", reason="robots_disallowed"))
                continue
            if index and delay_seconds:
                sleep(delay_seconds)
            fmt = row.get("formats", ["pdf"])[0] if "pdf" not in row.get("formats", ["pdf"]) else "pdf"
            try:
                response = transport.fetch(url)
                final = canonicalize_url(response.url or url)
                problem = None
                if response.status != 200:
                    problem = f"http_{response.status}"
                elif _page_source(final, allowed) != source_id:
                    problem = f"resolved_outside_source: {final}"
                elif len(response.body) > max_bytes:
                    problem = "too_large"
                elif not _looks_like(response.body, fmt):
                    # A challenge or error page served with 200 must not become a "decision".
                    problem = f"not_a_{fmt}: {response.headers.get('content-type', '')}"
            except Exception as exc:  # the browser can fail in many ways; all are refusals here
                response, final, problem = None, url, f"{type(exc).__name__}: {exc}"
            if problem:
                counts["refused"] += 1
                consecutive += 1
                record(dict(attempt, status="refused", reason=problem))
                if consecutive >= MAX_CONSECUTIVE_FAILURES:
                    stopped = f"{consecutive} refusals in a row; last: {problem}"
                    break
                continue
            consecutive = 0
            folder = run_dir / GROUP_FOLDERS.get(row.get("group", ""), "other")
            folder.mkdir(parents=True, exist_ok=True)
            destination = folder / f"{key}.{fmt}"
            destination.write_bytes(response.body)
            digest = hashlib.sha256(response.body).hexdigest()
            headers = {name.casefold(): value for name, value in response.headers.items()}
            label = (row.get("labels") or [destination.name])[0]
            item = WebItem(
                source_id=source_id, url=url, anchor_text=label, inferred_filename=destination.name,
                status="acquired_from_official_listing", discovered_at=utc_now(),
                authority_hint=str(sources.get(source_id, {}).get("authority_hint", "")),
                lifecycle_hint="unknown", downloaded_path=str(destination.resolve()), sha256=digest,
                bytes=len(response.body), content_type=headers.get("content-type", "").split(";")[0] or
                ("application/pdf" if fmt == "pdf" else "text/html"),
                etag=headers.get("etag") or None, last_modified=headers.get("last-modified") or None,
                content_length=headers.get("content-length") or None)
            metadata = {"content_type": item.content_type, "etag": item.etag or "",
                        "last_modified": item.last_modified or "", "content_length": item.content_length or "",
                        "final_url": final, "fetched_via": "browser_page_fetch"}
            source = dict(sources.get(source_id, {}), proposed_collection="doha_decisions")
            submission = write_intake_package(destination, item, metadata, source)
            package_path = Path(item.intake_package_path)
            package = json.loads(package_path.read_text(encoding="utf-8"))
            package["producer_notes"] += (
                f" DOHA group: {row.get('group')}. Listed as {label!r} on "
                f"{', '.join(row.get('listing_titles', []))}; identity rests on that listing label until "
                f"the Archivist reviews the text. Case year {case_year(key)} (the year DOHA numbered "
                "the case, not the decision date).")
            package_path.write_text(json.dumps(package, indent=2) + "\n", encoding="utf-8")
            counts["acquired"] += 1
            record(dict(attempt, status="acquired", resolved_url=final, sha256=digest, bytes=len(response.body),
                        path=str(destination.resolve()), submission_id=submission))
    report = {"schema_version": "1.0", "finished_utc": utc_now(), "run_dir": str(run_dir.resolve()),
              "planned": len(todo), "counts": counts, "stopped": stopped,
              "library_written": False}
    (run_dir / "acquire-report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


def parse_robots(text: str) -> urllib.robotparser.RobotFileParser:
    parser = urllib.robotparser.RobotFileParser()
    parser.parse(text.splitlines())
    return parser


class BrowserTransport:
    """Fetch through a real Chrome with the page's own fetch().

    Either launches Chrome (a separate profile under state/) or attaches to one the
    operator started with --remote-debugging-port, which is how the August crawl
    got past the CDN.
    """

    FETCH = """async (url) => {
      const r = await fetch(url, {credentials: "include", redirect: "follow"});
      const bytes = new Uint8Array(await r.arrayBuffer());
      let text = "";
      for (let i = 0; i < bytes.length; i += 0x8000) text += String.fromCharCode.apply(null, bytes.subarray(i, i + 0x8000));
      return {status: r.status, url: r.url, headers: Object.fromEntries(r.headers.entries()), body: btoa(text)};
    }"""

    def __init__(self, start_url: str, profile_dir: Path, cdp_url: str | None = None, timeout_ms: int = 60_000):
        try:
            from playwright.sync_api import sync_playwright
        except ImportError as exc:  # optional: only this command needs it
            raise SystemExit("doha-acquire needs Playwright: pip install playwright "
                             "(it drives your installed Chrome; no browser download is needed)") from exc
        self._playwright = sync_playwright().start()
        if cdp_url:
            self._browser = self._playwright.chromium.connect_over_cdp(cdp_url)
            self._context = self._browser.contexts[0] if self._browser.contexts else self._browser.new_context()
        else:
            self._browser = None
            self._context = self._playwright.chromium.launch_persistent_context(
                str(profile_dir), channel="chrome", headless=False)
        self._page = self._context.new_page()
        self._page.set_default_timeout(timeout_ms)
        self._page.goto(start_url, wait_until="domcontentloaded")

    def robots_text(self, origin: str) -> str:
        result = self._page.evaluate(self.FETCH, origin + "/robots.txt")
        if result["status"] != 200:
            raise SystemExit(f"robots.txt returned HTTP {result['status']} in the browser; not proceeding")
        return base64.b64decode(result["body"]).decode("utf-8", errors="replace")

    def fetch(self, url: str) -> Response:
        result = self._page.evaluate(self.FETCH, url)
        return Response(int(result["status"]), str(result["url"]), dict(result["headers"]),
                        base64.b64decode(result["body"]))

    def close(self) -> None:
        try:
            self._page.close()
            if self._browser is None:
                self._context.close()
        finally:
            self._playwright.stop()


def load_not_held(path: Path) -> list[dict[str, Any]]:
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if any(row.get("group") not in GROUPS.values() for row in rows):
        # Written before decisions were grouped by level; the group decides the quarantine folder.
        raise SystemExit(f"{path} predates grouping by decision level; re-run doha-provenance to regenerate it")
    return rows
