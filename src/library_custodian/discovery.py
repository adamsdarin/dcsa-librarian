from __future__ import annotations

import hashlib
import json
import mimetypes
import re
import time
import urllib.error
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
    etag: str | None = None
    last_modified: str | None = None
    content_length: str | None = None
    change_signal: str = "unverified"
    changed_fields: list[str] | None = None


FINGERPRINT_FIELDS = ("sha256", "etag", "last_modified", "content_length")


def response_headers(response: Any) -> dict[str, str]:
    return {
        "content_type": response.headers.get_content_type(),
        "etag": (response.headers.get("ETag") or "").strip(),
        "last_modified": (response.headers.get("Last-Modified") or "").strip(),
        "content_length": (response.headers.get("Content-Length") or "").strip(),
        "final_url": canonicalize_url(response.geturl()),
    }


def compare_fingerprints(previous: dict[str, Any] | None, current: dict[str, Any]) -> tuple[str, list[str]]:
    """Classify a document against its previous snapshot record.

    A document is called changed only on positive evidence: a field present on
    both sides holds a different value. Absent evidence is reported as
    unverified, never as unchanged, so a silent gap cannot read as a clean scan.
    """
    if previous is None:
        return "new_to_snapshot", []
    before = {field: str(previous.get(field) or "") for field in FINGERPRINT_FIELDS}
    after = {field: str(current.get(field) or "") for field in FINGERPRINT_FIELDS}
    comparable = [field for field in FINGERPRINT_FIELDS if before[field] and after[field]]
    if not comparable:
        return "unverified", []
    differing = [field for field in comparable if before[field] != after[field]]
    return ("changed", differing) if differing else ("unchanged", [])


def needs_review(item: "WebItem") -> bool:
    """A document is a review candidate when it is absent from the manifest or
    when the source's copy has changed since the last scan. A manifest hit is
    not on its own evidence that the held copy is still current.

    With no library to check against, manifest membership is unknown for every
    document, so only source-side movement counts. A run that merely established
    a source's first snapshot reports nothing: a baseline is not a finding.
    """
    if item.status == "manifest_not_checked":
        return item.change_signal in {"changed", "new_to_snapshot"}
    return item.status != "known" or item.change_signal == "changed"


def load_snapshot_documents(snapshot_path: Path) -> dict[str, dict[str, Any]] | None:
    """Read a snapshot, or None when no usable baseline exists.

    None and {} are different answers: None means nothing to compare against,
    which is why an empty change list on a first scan must not read as "clean".
    """
    if not snapshot_path.is_file():
        return None
    try:
        data = json.loads(snapshot_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    documents = data.get("documents")
    if isinstance(documents, dict):
        return {url: record for url, record in documents.items() if isinstance(record, dict)}
    urls = data.get("document_urls")
    if isinstance(urls, list):
        # schema 1 snapshots recorded URLs only: a URL baseline with no fingerprints
        return {url: {} for url in urls if isinstance(url, str)}
    return None


def make_run_dir(parent: Path, run_id: str) -> Path:
    """Create a fresh run directory, disambiguating runs inside the same second.

    Run ids are second-granular, so back-to-back scans would otherwise collide
    and abort the second one.
    """
    candidate = parent / run_id
    attempt = 1
    while candidate.exists():
        attempt += 1
        candidate = parent / f"{run_id}-{attempt}"
    candidate.mkdir(parents=True, exist_ok=False)
    return candidate


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


# Characters that may stand unescaped in a path or query. "%" is listed safe so
# an already-encoded URL is left alone rather than double-encoded: "%20" must
# stay "%20" and not become "%2520".
URL_SAFE = "/%:@&=+$,;~-._!*'()"


def canonicalize_url(url: str) -> str:
    parts = urllib.parse.urlsplit(url)
    scheme = parts.scheme.casefold()
    hostname = (parts.hostname or "").casefold()
    port = f":{parts.port}" if parts.port and parts.port not in {80, 443} else ""
    path = re.sub(r"/{2,}", "/", parts.path or "/")
    # DCSA publishes filenames containing spaces, and urllib refuses to request
    # a URL with a raw space. Unencoded, such a document could be discovered but
    # never probed for revision and never downloaded — the failure would land on
    # exactly the documents that matter, including every VOI newsletter.
    # Encoding here also collapses the encoded and unencoded spellings of one
    # document into a single identity.
    path = urllib.parse.quote(path, safe=URL_SAFE)
    query = urllib.parse.quote(parts.query, safe=URL_SAFE + "?")
    return urllib.parse.urlunsplit((scheme, hostname + port, path, query, ""))


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
        self._robots: dict[str, tuple[urllib.robotparser.RobotFileParser | None, str]] = {}
        self._last_request = 0.0

    def _load_robots(self, origin: str) -> tuple[urllib.robotparser.RobotFileParser | None, str]:
        """Fetch and parse robots.txt under this crawler's own declared identity.

        RobotFileParser.read() issues its own request as Python-urllib, not as
        the user agent this crawler declares for every other request. A site
        that rejects that default then yields 403, which the parser records as
        "disallow everything" — a refusal indistinguishable from a real policy.
        Asking under the identity we actually crawl with is the consistent
        thing to do, and it keeps a transport failure from being reported as a
        policy decision.
        """
        parser = urllib.robotparser.RobotFileParser()
        url = origin + "/robots.txt"
        parser.set_url(url)
        request = urllib.request.Request(url, headers={"User-Agent": self.user_agent, "Accept": "text/plain,*/*"})
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                text = response.read(self.max_bytes).decode("utf-8", errors="replace")
        except urllib.error.HTTPError as exc:
            if exc.code in (404, 410):
                # no policy published is not the same as a policy of silence
                parser.parse([])
                return parser, f"no robots.txt (HTTP {exc.code})"
            return None, f"could not read robots.txt (HTTP {exc.code})"
        except Exception as exc:
            return None, f"could not read robots.txt ({type(exc).__name__}: {exc})"
        parser.parse(text.splitlines())
        return parser, "ok"

    def _check_allowed(self, url: str) -> None:
        """Raise PermissionError unless robots policy permits this URL.

        The message distinguishes a policy that forbids the path from a policy
        that could not be retrieved. They call for different responses, and
        collapsing them hides which one happened.
        """
        if not self.respect_robots:
            return
        parts = urllib.parse.urlsplit(url)
        origin = f"{parts.scheme}://{parts.netloc}"
        if origin not in self._robots:
            self._robots[origin] = self._load_robots(origin)
        parser, status = self._robots[origin]
        if parser is None:
            raise PermissionError(
                f"{status} for {origin}, so its crawling policy is unknown and {url} was not requested"
            )
        if not parser.can_fetch(self.user_agent, url):
            raise PermissionError(f"robots.txt at {origin} disallows {url} for {self.user_agent}")

    def _throttle(self) -> None:
        wait = self.delay_seconds - (time.monotonic() - self._last_request)
        if wait > 0:
            time.sleep(wait)

    def head(self, url: str) -> dict[str, str]:
        """Freshness probe for a document already held in the manifest.

        Headers only: a revision check must not cost a full re-download of every
        known document on every scan.
        """
        self._check_allowed(url)
        self._throttle()
        request = urllib.request.Request(url, method="HEAD", headers={"User-Agent": self.user_agent, "Accept": "*/*"})
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                return response_headers(response)
        finally:
            self._last_request = time.monotonic()

    def get(self, url: str) -> tuple[bytes, dict[str, str]]:
        self._check_allowed(url)
        self._throttle()
        request = urllib.request.Request(url, headers={"User-Agent": self.user_agent, "Accept": "text/html,application/pdf,application/octet-stream;q=0.8"})
        with urllib.request.urlopen(request, timeout=self.timeout) as response:
            content_length = response.headers.get("Content-Length")
            if content_length and int(content_length) > self.max_bytes:
                raise ValueError(f"response exceeds {self.max_bytes} bytes")
            data = response.read(self.max_bytes + 1)
            if len(data) > self.max_bytes:
                raise ValueError(f"response exceeds {self.max_bytes} bytes")
            metadata = response_headers(response)
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
    # Links are deduplicated within a page by extract_links, but a document
    # linked from several pages of the same section would otherwise be recorded
    # once per page: inflating counts, probing it repeatedly, and listing it
    # more than once for review.
    seen_documents: set[str] = set()
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
                if url not in seen_documents:
                    seen_documents.add(url)
                    documents.append(link)
                continue
            path = urllib.parse.urlsplit(url).path
            if depth < max_depth and (not prefix or path.casefold().startswith(str(prefix).casefold())):
                queue.append((url, depth + 1))
    return documents, pages


def discover(
    library_root: Path | None,
    registry_path: Path,
    state_dir: Path,
    quarantine_dir: Path,
    selected_sources: set[str] | None = None,
    download: bool = False,
    verify_known: bool = True,
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
    # Without a library the scan still detects source-side movement; it just
    # cannot say whether the corpus already holds what it finds.
    known_filenames, known_urls = load_known_documents(library_root) if library_root is not None else (set(), set())
    run_dir = make_run_dir(state_dir / "scans", datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"))
    run_id = run_dir.name
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
            # Some sources publish immutable records. Probing those for in-place
            # revision is cost with no possible finding, so the registry can opt
            # a source out; the global flag can only ever narrow it further.
            source_verify = verify_known and bool(source.get("verify_known", True))
            source_items: list[WebItem] = []
            snapshot_path = state_dir / "snapshots" / f"{source_id}.json"
            previous_documents = load_snapshot_documents(snapshot_path)
            current_documents: dict[str, dict[str, Any]] = {}
            verification_errors: list[dict[str, str]] = []
            changed: list[dict[str, Any]] = []
            for link in documents:
                filename = infer_filename(link["url"], link["text"])
                if library_root is None:
                    status = "manifest_not_checked"
                elif link["url"] in known_urls or filename.casefold() in known_filenames:
                    status = "known"
                else:
                    status = "missing_from_manifest"
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
                    item.etag = metadata.get("etag") or None
                    item.last_modified = metadata.get("last_modified") or None
                    item.content_length = metadata.get("content_length") or None
                elif source_verify:
                    # A document already in the manifest can still be revised in
                    # place. Probe its headers so a same-URL revision is visible.
                    try:
                        headers = fetcher.head(item.url)
                    except Exception as exc:
                        verification_errors.append({"url": item.url, "error": f"{type(exc).__name__}: {exc}"})
                    else:
                        item.etag = headers.get("etag") or None
                        item.last_modified = headers.get("last_modified") or None
                        item.content_length = headers.get("content_length") or None
                        item.content_type = item.content_type or headers.get("content_type")
                record = {
                    "inferred_filename": filename,
                    "sha256": item.sha256,
                    "etag": item.etag,
                    "last_modified": item.last_modified,
                    "content_length": item.content_length,
                }
                if previous_documents is None:
                    # nothing to compare against yet; do not report the whole
                    # source as newly discovered on its first scan
                    item.change_signal, differing = "baseline", []
                else:
                    item.change_signal, differing = compare_fingerprints(previous_documents.get(item.url), record)
                item.changed_fields = differing or None
                if item.change_signal == "changed":
                    changed.append({"url": item.url, "inferred_filename": filename, "status": status, "changed_fields": differing})
                current_documents[item.url] = record
                items.append(item)
                source_items.append(item)
            baseline_established = previous_documents is not None
            previous_urls = set(previous_documents) if previous_documents is not None else set()
            current_urls = {item.url for item in source_items}
            snapshot_path.parent.mkdir(parents=True, exist_ok=True)
            snapshot_path.write_text(
                json.dumps(
                    {
                        "schema_version": 2,
                        "source_id": source_id,
                        "scanned_at": now,
                        "documents": current_documents,
                        "document_urls": sorted(current_urls),
                        "pages": pages,
                    },
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
            sources_report.append({
                "source_id": source_id,
                "status": "ok",
                "pages_scanned": len(pages),
                "documents_seen": len(source_items),
                "baseline_established": baseline_established,
                "known_documents_verified": source_verify,
                "new_urls_since_previous_scan": sorted(current_urls - previous_urls) if baseline_established else [],
                "removed_urls_since_previous_scan": sorted(previous_urls - current_urls),
                "changed_since_previous_scan": sorted(changed, key=lambda entry: entry["url"]),
                "candidates_for_review": sorted(item.url for item in source_items if needs_review(item)),
                "unverified_documents": sorted(item.url for item in source_items if item.change_signal == "unverified"),
                "verification_errors": verification_errors,
            })
        except Exception as exc:  # a failed source must not abort or publish anything
            sources_report.append({"source_id": source_id, "status": "error", "error": f"{type(exc).__name__}: {exc}"})

    report = {
        "schema_version": "1.0",
        "run_id": run_id,
        "created_at": now,
        "library_root": str(library_root.resolve()) if library_root is not None else None,
        "manifest_checked": library_root is not None,
        "download_enabled": download,
        "verify_known_enabled": verify_known,
        "publication_performed": False,
        "sources": sources_report,
        "counts": {
            "documents_seen": len(items),
            "known": sum(item.status == "known" for item in items),
            "missing_from_manifest": sum(item.status == "missing_from_manifest" for item in items),
            "manifest_not_checked": sum(item.status == "manifest_not_checked" for item in items),
            "changed_since_previous_scan": sum(item.change_signal == "changed" for item in items),
            "new_to_snapshot": sum(item.change_signal == "new_to_snapshot" for item in items),
            "unverified": sum(item.change_signal == "unverified" for item in items),
            "downloaded_to_quarantine": sum(item.downloaded_path is not None for item in items),
        },
        "candidates": [asdict(item) for item in items if needs_review(item)],
    }
    (run_dir / "discovery-report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    with (run_dir / "candidates.jsonl").open("w", encoding="utf-8", newline="\n") as handle:
        for item in items:
            if needs_review(item):
                handle.write(json.dumps(asdict(item), separators=(",", ":")) + "\n")
    return report


def preflight(registry_path: Path, source_id: str, match: str | None = None) -> dict[str, Any]:
    """Fetch one source and report what the parser can actually see.

    Writes nothing — no snapshot, no report, no baseline. This exists so that
    "is this source working" can be answered without perturbing the state that
    change detection depends on, and without touching the library.
    """
    registry = json.loads(registry_path.read_text(encoding="utf-8-sig"))
    source = next((item for item in registry.get("sources", []) if item.get("id") == source_id), None)
    if source is None:
        known = ", ".join(str(item.get("id")) for item in registry.get("sources", []))
        raise KeyError(f"no source {source_id!r} in the registry. Known sources: {known}")

    settings = registry.get("settings", {})
    fetcher = Fetcher(
        user_agent=settings.get("user_agent", "DCSA-Library-Custodian/0.1 (+local-governance-audit)"),
        timeout=float(settings.get("timeout_seconds", 20)),
        max_bytes=int(settings.get("max_response_bytes", 104857600)),
        delay_seconds=float(settings.get("delay_seconds", 0.5)),
        respect_robots=bool(settings.get("respect_robots", True)),
    )

    result: dict[str, Any] = {
        "source_id": source_id,
        "url": source.get("url"),
        "enabled": bool(source.get("enabled", True)),
        "checked_at": utc_now(),
        "match": match,
        "wrote_anything": False,
    }
    try:
        documents, pages = _crawl_source(source, fetcher)
    except Exception as exc:
        result.update({"reachable": False, "error": f"{type(exc).__name__}: {exc}", "pages_read": 0, "documents": []})
        return result

    found = []
    for link in documents:
        filename = infer_filename(link["url"], link["text"])
        found.append({"url": link["url"], "anchor_text": link["text"], "inferred_filename": filename})

    listed = found
    if match:
        needle = match.casefold()
        listed = [item for item in found if needle in (item["url"] + item["anchor_text"] + item["inferred_filename"]).casefold()]

    result.update(
        {
            "reachable": True,
            "pages_read": len(pages),
            "documents_seen": len(found),
            "documents_listed": len(listed),
            "documents": listed,
        }
    )
    return result


def render_preflight_text(result: dict[str, Any]) -> str:
    lines = [
        f"Preflight - {result['source_id']}",
        "=" * 46,
        f"Source URL: {result['url']}",
        f"Enabled:    {'yes' if result['enabled'] else 'no (a scan would skip it)'}",
    ]

    if not result.get("reachable"):
        lines += [
            "Reachable:  NO",
            f"Error:      {result['error']}",
            "",
            "This tells you nothing about whether the source changed. Check network",
            "access from this machine and re-run. If the page loads in a browser but",
            "not here, the site is rejecting the crawler: use the browser fallback in",
            "references/discovery.md. Do not spoof a user agent or disable robots handling.",
            "",
            "Nothing was written.",
        ]
        return "\n".join(lines) + "\n"

    lines += [
        "Reachable:  yes",
        f"Pages read: {result['pages_read']}",
        f"Documents:  {result['documents_seen']} found",
    ]
    if result["match"]:
        lines.append(f"Filter:     {result['match']!r} -> {result['documents_listed']} shown")

    if result["documents_seen"] == 0:
        lines += [
            "",
            "No document links were found on that page.",
            "If you can see documents on it in a browser, they are rendered by script",
            "and the plain parser cannot see them. Capture the page with the browser",
            "fallback and import it with browser-import. A scheduled scan pointed at",
            "this source would report nothing, forever, and look healthy doing it.",
        ]
    elif not result["documents"]:
        lines += ["", f"No document matched {result['match']!r}, though {result['documents_seen']} were found."]
    else:
        lines.append("")
        for item in result["documents"]:
            lines.append(f"  {item['inferred_filename']}")
            lines.append(f"    {item['url']}")

    lines += ["", "Nothing was written. No snapshot, report or baseline changed."]
    return "\n".join(lines) + "\n"


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
    run_dir = make_run_dir(state_dir / "browser-scans", datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ-browser"))
    run_id = run_dir.name
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
    previous_documents = load_snapshot_documents(snapshot_path)
    baseline_established = previous_documents is not None
    previous_urls = set(previous_documents) if previous_documents is not None else set()
    current_documents: dict[str, dict[str, Any]] = {}
    for item in items:
        record = {"inferred_filename": item.inferred_filename, "sha256": None, "etag": None, "last_modified": None, "content_length": None}
        previous_record = previous_documents.get(item.url) if previous_documents is not None else None
        item.change_signal, differing = compare_fingerprints(previous_record, record)
        item.changed_fields = differing or None
        current_documents[item.url] = record
    current_urls = {item.url for item in items}
    snapshot_path.parent.mkdir(parents=True, exist_ok=True)
    snapshot_path.write_text(
        json.dumps(
            {
                "schema_version": 2,
                "source_id": source_id,
                "scanned_at": now,
                "scan_mode": "browser",
                "documents": current_documents,
                "document_urls": sorted(current_urls),
                "pages": accepted_pages,
            },
            indent=2,
        )
        + "\n",
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
        "baseline_established": baseline_established,
        "known_documents_verified": False,
        "new_urls_since_previous_scan": sorted(current_urls - previous_urls) if baseline_established else [],
        "removed_urls_since_previous_scan": sorted(previous_urls - current_urls),
        "rejected_pages": rejected_pages,
        "candidates": [asdict(item) for item in items if needs_review(item)],
    }
    (run_dir / "browser-import-report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    with (run_dir / "candidates.jsonl").open("w", encoding="utf-8", newline="\n") as handle:
        for item in items:
            if needs_review(item):
                handle.write(json.dumps(asdict(item), separators=(",", ":")) + "\n")
    return report
