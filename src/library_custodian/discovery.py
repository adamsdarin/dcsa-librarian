from __future__ import annotations

import hashlib
import json
import mimetypes
import re
import time
import urllib.parse
import urllib.request
import urllib.robotparser
from collections import deque
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

from .audit import iter_jsonl


DOCUMENT_EXTENSIONS = {".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".zip", ".json", ".xml"}


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[dict[str, str]] = []
        self._href: str | None = None
        self._text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.casefold() == "a":
            values = dict(attrs)
            self._href = values.get("href")
            self._text = []

    def handle_data(self, data: str) -> None:
        if self._href is not None:
            self._text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag.casefold() == "a" and self._href is not None:
            self.links.append({"href": self._href, "text": " ".join(self._text).strip()})
            self._href = None
            self._text = []


@dataclass
class WebItem:
    source_id: str
    url: str
    anchor_text: str
    inferred_filename: str
    status: str
    discovered_at: str
    authority_hint: str
    lifecycle_hint: str
    downloaded_path: str | None = None
    sha256: str | None = None
    bytes: int | None = None
    content_type: str | None = None


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def canonicalize_url(url: str) -> str:
    parts = urllib.parse.urlsplit(url)
    scheme = parts.scheme.casefold()
    hostname = (parts.hostname or "").casefold()
    port = f":{parts.port}" if parts.port and parts.port not in {80, 443} else ""
    path = re.sub(r"/{2,}", "/", parts.path or "/")
    return urllib.parse.urlunsplit((scheme, hostname + port, path, parts.query, ""))


def domain_allowed(url: str, allowed_domains: list[str]) -> bool:
    host = (urllib.parse.urlsplit(url).hostname or "").casefold()
    return any(host == domain.casefold() or host.endswith("." + domain.casefold()) for domain in allowed_domains)


def infer_filename(url: str, anchor_text: str) -> str:
    anchor = anchor_text.strip().replace("\u200b", "")
    anchor_name = Path(anchor).name
    if Path(anchor_name).suffix.casefold() in DOCUMENT_EXTENSIONS:
        return anchor_name
    url_name = Path(urllib.parse.unquote(urllib.parse.urlsplit(url).path)).name
    return url_name or "unnamed-document"


def is_document_link(url: str, anchor_text: str) -> bool:
    names = (Path(urllib.parse.urlsplit(url).path).suffix.casefold(), Path(anchor_text.strip()).suffix.casefold())
    return any(name in DOCUMENT_EXTENSIONS for name in names) or "/fileid/" in urllib.parse.urlsplit(url).path.casefold()


def extract_links(html: str, base_url: str) -> list[dict[str, str]]:
    parser = LinkParser()
    parser.feed(html)
    results: list[dict[str, str]] = []
    seen: set[str] = set()
    for item in parser.links:
        absolute = canonicalize_url(urllib.parse.urljoin(base_url, item["href"]))
        if absolute in seen:
            continue
        seen.add(absolute)
        results.append({"url": absolute, "text": item["text"]})
    return results


class Fetcher:
    def __init__(self, user_agent: str, timeout: float, max_bytes: int, delay_seconds: float, respect_robots: bool = True) -> None:
        self.user_agent = user_agent
        self.timeout = timeout
        self.max_bytes = max_bytes
        self.delay_seconds = delay_seconds
        self.respect_robots = respect_robots
        self._robots: dict[str, urllib.robotparser.RobotFileParser] = {}
        self._last_request = 0.0

    def _allowed(self, url: str) -> bool:
        if not self.respect_robots:
            return True
        parts = urllib.parse.urlsplit(url)
        origin = f"{parts.scheme}://{parts.netloc}"
        if origin not in self._robots:
            parser = urllib.robotparser.RobotFileParser(origin + "/robots.txt")
            try:
                parser.read()
            except OSError:
                parser = urllib.robotparser.RobotFileParser()
                parser.set_url(origin + "/robots.txt")
                parser.parse([])
            self._robots[origin] = parser
        return self._robots[origin].can_fetch(self.user_agent, url)

    def get(self, url: str) -> tuple[bytes, dict[str, str]]:
        if not self._allowed(url):
            raise PermissionError(f"robots policy disallows {url}")
        wait = self.delay_seconds - (time.monotonic() - self._last_request)
        if wait > 0:
            time.sleep(wait)
        request = urllib.request.Request(url, headers={"User-Agent": self.user_agent, "Accept": "text/html,application/pdf,application/octet-stream;q=0.8"})
        with urllib.request.urlopen(request, timeout=self.timeout) as response:
            content_length = response.headers.get("Content-Length")
            if content_length and int(content_length) > self.max_bytes:
                raise ValueError(f"response exceeds {self.max_bytes} bytes")
            data = response.read(self.max_bytes + 1)
            if len(data) > self.max_bytes:
                raise ValueError(f"response exceeds {self.max_bytes} bytes")
            metadata = {
                "content_type": response.headers.get_content_type(),
                "etag": response.headers.get("ETag", ""),
                "last_modified": response.headers.get("Last-Modified", ""),
                "final_url": canonicalize_url(response.geturl()),
            }
        self._last_request = time.monotonic()
        return data, metadata


def load_known_documents(library_root: Path) -> tuple[set[str], set[str]]:
    entry = json.loads((library_root / "START_HERE_FOR_ROBOTS.json").read_text(encoding="utf-8-sig"))
    manifest = library_root / entry["documents"]
    filenames: set[str] = set()
    urls: set[str] = set()
    for _, record in iter_jsonl(manifest):
        for field in ("human_source_path", "original_source_path"):
            value = record.get(field)
            if isinstance(value, str) and value:
                filenames.add(Path(value).name.casefold())
        for field in ("canonical_source_uri", "source_url", "source_uri"):
            value = record.get(field)
            if isinstance(value, str) and value.startswith("http"):
                urls.add(canonicalize_url(value))
    return filenames, urls


def _crawl_source(source: dict[str, Any], fetcher: Fetcher) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    start = canonicalize_url(source["url"])
    allowed_domains = source["allowed_domains"]
    max_depth = int(source.get("max_depth", 0))
    max_pages = int(source.get("max_pages", 25))
    prefix = source.get("crawl_path_prefix")
    queue: deque[tuple[str, int]] = deque([(start, 0)])
    visited: set[str] = set()
    documents: list[dict[str, str]] = []
    pages: list[dict[str, str]] = []

    while queue and len(visited) < max_pages:
        page_url, depth = queue.popleft()
        if page_url in visited:
            continue
        visited.add(page_url)
        data, metadata = fetcher.get(page_url)
        pages.append({"url": page_url, **metadata, "sha256": hashlib.sha256(data).hexdigest()})
        if "html" not in metadata.get("content_type", ""):
            continue
        links = extract_links(data.decode("utf-8", errors="replace"), metadata.get("final_url") or page_url)
        for link in links:
            url = link["url"]
            if urllib.parse.urlsplit(url).scheme != "https" or not domain_allowed(url, allowed_domains):
                continue
            if is_document_link(url, link["text"]):
                documents.append(link)
                continue
            path = urllib.parse.urlsplit(url).path
            if depth < max_depth and (not prefix or path.casefold().startswith(str(prefix).casefold())):
                queue.append((url, depth + 1))
    return documents, pages


def discover(
    library_root: Path,
    registry_path: Path,
    state_dir: Path,
    quarantine_dir: Path,
    selected_sources: set[str] | None = None,
    download: bool = False,
) -> dict[str, Any]:
    registry = json.loads(registry_path.read_text(encoding="utf-8-sig"))
    settings = registry.get("settings", {})
    fetcher = Fetcher(
        user_agent=settings.get("user_agent", "DCSA-Library-Custodian/0.1 (+local-governance-audit)"),
        timeout=float(settings.get("timeout_seconds", 20)),
        max_bytes=int(settings.get("max_response_bytes", 104857600)),
        delay_seconds=float(settings.get("delay_seconds", 0.5)),
        respect_robots=bool(settings.get("respect_robots", True)),
    )
    known_filenames, known_urls = load_known_documents(library_root)
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = state_dir / "scans" / run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    quarantine_run = quarantine_dir / run_id
    now = utc_now()
    items: list[WebItem] = []
    sources_report: list[dict[str, Any]] = []

    for source in registry.get("sources", []):
        source_id = source["id"]
        if not source.get("enabled", True) or (selected_sources and source_id not in selected_sources):
            continue
        try:
            documents, pages = _crawl_source(source, fetcher)
            source_items: list[WebItem] = []
            for link in documents:
                filename = infer_filename(link["url"], link["text"])
                status = "known" if link["url"] in known_urls or filename.casefold() in known_filenames else "missing_from_manifest"
                item = WebItem(
                    source_id=source_id,
                    url=link["url"],
                    anchor_text=link["text"],
                    inferred_filename=filename,
                    status=status,
                    discovered_at=now,
                    authority_hint=source.get("authority_hint", "unreviewed_official_source"),
                    lifecycle_hint="unverified",
                )
                if download and status == "missing_from_manifest":
                    data, metadata = fetcher.get(item.url)
                    source_folder = quarantine_run / source_id
                    source_folder.mkdir(parents=True, exist_ok=True)
                    safe_name = re.sub(r"[^A-Za-z0-9._-]+", "_", filename).strip("._") or hashlib.sha256(item.url.encode()).hexdigest()[:16]
                    destination = source_folder / safe_name
                    if destination.exists():
                        destination = source_folder / f"{destination.stem}-{hashlib.sha256(item.url.encode()).hexdigest()[:8]}{destination.suffix}"
                    destination.write_bytes(data)
                    item.downloaded_path = str(destination.resolve())
                    item.sha256 = hashlib.sha256(data).hexdigest()
                    item.bytes = len(data)
                    item.content_type = metadata.get("content_type") or mimetypes.guess_type(filename)[0]
                items.append(item)
                source_items.append(item)
            snapshot_path = state_dir / "snapshots" / f"{source_id}.json"
            previous_urls: set[str] = set()
            if snapshot_path.is_file():
                try:
                    previous_urls = set(json.loads(snapshot_path.read_text(encoding="utf-8")).get("document_urls", []))
                except (OSError, json.JSONDecodeError):
                    pass
            current_urls = {item.url for item in source_items}
            snapshot_path.parent.mkdir(parents=True, exist_ok=True)
            snapshot_path.write_text(json.dumps({"source_id": source_id, "scanned_at": now, "document_urls": sorted(current_urls), "pages": pages}, indent=2) + "\n", encoding="utf-8")
            sources_report.append({
                "source_id": source_id,
                "status": "ok",
                "pages_scanned": len(pages),
                "documents_seen": len(source_items),
                "new_urls_since_previous_scan": sorted(current_urls - previous_urls) if previous_urls else [],
                "removed_urls_since_previous_scan": sorted(previous_urls - current_urls),
            })
        except Exception as exc:  # a failed source must not abort or publish anything
            sources_report.append({"source_id": source_id, "status": "error", "error": f"{type(exc).__name__}: {exc}"})

    report = {
        "schema_version": "1.0",
        "run_id": run_id,
        "created_at": now,
        "library_root": str(library_root.resolve()),
        "download_enabled": download,
        "publication_performed": False,
        "sources": sources_report,
        "counts": {
            "documents_seen": len(items),
            "known": sum(item.status == "known" for item in items),
            "missing_from_manifest": sum(item.status == "missing_from_manifest" for item in items),
            "downloaded_to_quarantine": sum(item.downloaded_path is not None for item in items),
        },
        "candidates": [asdict(item) for item in items if item.status != "known"],
    }
    (run_dir / "discovery-report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    with (run_dir / "candidates.jsonl").open("w", encoding="utf-8", newline="\n") as handle:
        for item in items:
            if item.status != "known":
                handle.write(json.dumps(asdict(item), separators=(",", ":")) + "\n")
    return report


def import_browser_capture(
    library_root: Path,
    registry_path: Path,
    capture_path: Path,
    state_dir: Path,
) -> dict[str, Any]:
    """Validate and import a page-by-page browser scan without downloading or publishing."""
    registry = json.loads(registry_path.read_text(encoding="utf-8-sig"))
    capture = json.loads(capture_path.read_text(encoding="utf-8-sig"))
    source_id = capture.get("source_id")
    source = next((item for item in registry.get("sources", []) if item.get("id") == source_id and item.get("enabled", True)), None)
    if source is None:
        raise ValueError(f"capture source_id is not enabled in the registry: {source_id!r}")

    pages = capture.get("pages")
    if not isinstance(pages, list) or not pages:
        raise ValueError("browser capture must contain at least one page")

    allowed_domains = source["allowed_domains"]
    known_filenames, known_urls = load_known_documents(library_root)
    now = utc_now()
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ-browser")
    run_dir = state_dir / "browser-scans" / run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    documents: dict[str, dict[str, str]] = {}
    accepted_pages: list[dict[str, Any]] = []
    rejected_pages: list[dict[str, str]] = []
    rejected_links = 0

    for page in pages:
        if not isinstance(page, dict) or not isinstance(page.get("url"), str):
            rejected_pages.append({"url": "", "reason": "invalid_page_record"})
            continue
        page_url = canonicalize_url(page["url"])
        if urllib.parse.urlsplit(page_url).scheme != "https" or not domain_allowed(page_url, allowed_domains):
            rejected_pages.append({"url": page_url, "reason": "outside_registry_allowlist"})
            continue
        links = page.get("links", [])
        if not isinstance(links, list):
            rejected_pages.append({"url": page_url, "reason": "links_not_array"})
            continue
        accepted_page = {
            "url": page_url,
            "title": str(page.get("title", "")),
            "captured_at": str(page.get("captured_at", capture.get("captured_at", now))),
            "content_fingerprint": page.get("content_fingerprint"),
            "link_count": len(links),
        }
        accepted_pages.append(accepted_page)
        for link in links:
            if not isinstance(link, dict) or not isinstance(link.get("url"), str):
                rejected_links += 1
                continue
            url = canonicalize_url(urllib.parse.urljoin(page_url, link["url"]))
            text_value = str(link.get("text", ""))
            if urllib.parse.urlsplit(url).scheme != "https" or not domain_allowed(url, allowed_domains):
                rejected_links += 1
                continue
            if is_document_link(url, text_value):
                documents[url] = {"url": url, "text": text_value, "found_on_page": page_url}

    items: list[WebItem] = []
    for link in documents.values():
        filename = infer_filename(link["url"], link["text"])
        status = "known" if link["url"] in known_urls or filename.casefold() in known_filenames else "missing_from_manifest"
        items.append(
            WebItem(
                source_id=source_id,
                url=link["url"],
                anchor_text=link["text"],
                inferred_filename=filename,
                status=status,
                discovered_at=now,
                authority_hint=source.get("authority_hint", "unreviewed_official_source"),
                lifecycle_hint="unverified",
            )
        )

    snapshot_path = state_dir / "snapshots" / f"browser-{source_id}.json"
    previous_urls: set[str] = set()
    if snapshot_path.is_file():
        try:
            previous_urls = set(json.loads(snapshot_path.read_text(encoding="utf-8")).get("document_urls", []))
        except (OSError, json.JSONDecodeError):
            pass
    current_urls = {item.url for item in items}
    snapshot_path.parent.mkdir(parents=True, exist_ok=True)
    snapshot_path.write_text(
        json.dumps({"source_id": source_id, "scanned_at": now, "scan_mode": "browser", "document_urls": sorted(current_urls), "pages": accepted_pages}, indent=2) + "\n",
        encoding="utf-8",
    )

    report = {
        "schema_version": "1.0",
        "run_id": run_id,
        "created_at": now,
        "scan_mode": "browser_capture_import",
        "source_id": source_id,
        "library_root": str(library_root.resolve()),
        "capture_file": str(capture_path.resolve()),
        "publication_performed": False,
        "counts": {
            "pages_accepted": len(accepted_pages),
            "pages_rejected": len(rejected_pages),
            "document_links_seen": len(items),
            "known": sum(item.status == "known" for item in items),
            "missing_from_manifest": sum(item.status == "missing_from_manifest" for item in items),
            "links_rejected": rejected_links,
        },
        "new_urls_since_previous_scan": sorted(current_urls - previous_urls) if previous_urls else [],
        "removed_urls_since_previous_scan": sorted(previous_urls - current_urls),
        "rejected_pages": rejected_pages,
        "candidates": [asdict(item) for item in items if item.status != "known"],
    }
    (run_dir / "browser-import-report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    with (run_dir / "candidates.jsonl").open("w", encoding="utf-8", newline="\n") as handle:
        for item in items:
            if item.status != "known":
                handle.write(json.dumps(asdict(item), separators=(",", ":")) + "\n")
    return report
