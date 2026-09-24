"""Turn captured DOHA listing pages into a source-URL ledger for the Archivist.

DOHA addresses decisions by opaque FileId, so a URL can only come from the
official listing that names the file, never from the case number. This reads a
browser capture of those listing pages, keeps the links that pass the registry's
allowlist, and matches them to library decisions by case number and decision
level -- the identity DOHA itself prints on the page.

Two bases are recorded, and the weaker one says so:

- ``legacy_download_bytes_identical``: the retained PDF's bytes equal the bytes
  a recorded download of that URL produced. Identity is proven.
- ``official_listing_label``: the official listing publishes that case number
  and level under this URL. Identity is the listing's, not a byte match.

The reverse direction is reported too: every decision a captured listing
publishes that the library does not hold. It is only as complete as the capture;
a listing page that was down or not captured cannot show what is missing from it.

Nothing here downloads a document or writes into the library.
"""
from __future__ import annotations

import csv
import json
import re
import urllib.parse
from pathlib import Path
from typing import Any, Iterable

from .discovery import canonicalize_url, domain_allowed, utc_now

LIBRARY_MANIFEST = "ROBOT_READABLE_DIRECTORY/MANIFESTS/DOHA_CURRENT_PATHS.jsonl"
LEGACY_IMPORT = "ROBOT_READABLE_DIRECTORY/LEGACY_IMPORTS/doha-decisions"
FILE_LINK = re.compile(r"^(?P<page>https://[^?#]*/)FileId/(?P<file_id>\d+)/$")
# 19-02096.a1.pdf, 18.02204.h1.pdf, 19-00803-SD.h1.pdf
LABEL = re.compile(r"^(?P<year>\d{2})[-.](?P<number>\d{4,6})(?P<suffix>-[A-Za-z0-9]+)?\.(?P<level>[ha]\d)\.?(?P<extension>pdf|html?|wpd|doc)?$", re.I)
STEM = re.compile(r"^(?P<year>\d{2})-(?P<number>\d{4,6})(?P<suffix>-[A-Za-z0-9]+)?\.(?P<level>[ha]\d)", re.I)
AGGREGATE_LISTING = re.compile(r"\band\s+prior\b", re.I)


def case_key(value: str, pattern: re.Pattern[str] = STEM) -> str | None:
    """The case identity DOHA prints: year, number and decision level, normalized."""
    match = pattern.match(value.strip())
    if not match:
        return None
    suffix = (match.group("suffix") or "").lower()
    return f"{match.group('year')}-{int(match.group('number')):05d}{suffix}.{match.group('level').lower()}"


def _allowed_pages(registry: dict[str, Any]) -> list[tuple[list[str], str]]:
    allowed = []
    for source in registry.get("sources", []):
        if not source.get("enabled", True):
            continue
        prefix = source.get("crawl_path_prefix")
        if prefix and source.get("allowed_domains"):
            allowed.append((source["allowed_domains"], str(prefix)))
    return allowed


def _page_allowed(url: str, allowed: list[tuple[list[str], str]]) -> bool:
    parts = urllib.parse.urlsplit(url)
    if parts.scheme != "https":
        return False
    return any(domain_allowed(url, domains) and parts.path.casefold().startswith(prefix.casefold())
               for domains, prefix in allowed)


def read_captures(paths: Iterable[Path]) -> list[dict[str, Any]]:
    """Capture pages, newest wins when the same page was captured more than once."""
    pages: dict[str, dict[str, Any]] = {}
    for path in paths:
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            page = json.loads(line)
            if not isinstance(page, dict) or not page.get("rows") or not isinstance(page.get("u"), str):
                continue
            existing = pages.get(page["u"])
            if existing is None or str(page.get("at", "")) >= str(existing.get("at", "")):
                pages[page["u"]] = page
    return list(pages.values())


def _legacy_downloads(library_root: Path, human_hashes: dict[str, str]) -> dict[str, tuple[str, str]]:
    """Case key -> (URL, sha256) for files a recorded crawl actually downloaded."""
    base = library_root / LEGACY_IMPORT
    progress, inventory = base / "download_progress.json", base / "inventory.csv"
    if not progress.is_file() or not inventory.is_file() or not human_hashes:
        return {}
    urls: dict[str, str] = {}
    for item in json.loads(progress.read_text(encoding="utf-8-sig")).get("browserManifest", []):
        key = case_key(str(item.get("label", "")), LABEL)
        if key and isinstance(item.get("url"), str):
            urls.setdefault(key, canonicalize_url(item["url"]))
    output: dict[str, tuple[str, str]] = {}
    with inventory.open(encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            key = case_key(str(row.get("case", "")), STEM)
            digest = str(row.get("sha256", "")).strip().lower()
            if key and key in urls and len(digest) == 64:
                output[key] = (urls[key], digest)
    return output


def build_ledger(library_root: Path, capture_paths: list[Path], registry_path: Path,
                 human_hashes: dict[str, str] | None = None
                 ) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    """Match captured listing links to library decisions, and list the listed
    decisions the library lacks. Writes nothing."""
    registry = json.loads(registry_path.read_text(encoding="utf-8-sig"))
    allowed = _allowed_pages(registry)
    pages = read_captures(capture_paths)
    rejected_pages: list[dict[str, str]] = []
    rejected_links = 0
    by_key: dict[str, list[dict[str, Any]]] = {}
    # Every decision a listing publishes, in any format: an HTML-only posting is
    # still a decision the library may lack, though it cannot be a PDF source URL.
    listed: dict[str, list[dict[str, Any]]] = {}
    for page in pages:
        page_url = canonicalize_url(page["u"])
        if not _page_allowed(page_url, allowed):
            rejected_pages.append({"url": page_url, "reason": "outside_registry_allowlist"})
            continue
        title = str(page.get("t", ""))
        captured = str(page.get("at", ""))
        for row in page["rows"]:
            if not isinstance(row, list) or len(row) < 2:
                rejected_links += 1
                continue
            label, file_id = str(row[0]).strip(), str(row[1])
            url = f"{page_url}FileId/{file_id}/"
            parsed = LABEL.match(label)
            key = case_key(label, LABEL)
            if not FILE_LINK.match(url) or not _page_allowed(url, allowed) or not key:
                rejected_links += 1
                continue
            extension = (parsed.group("extension") or "pdf").lower()
            listed.setdefault(key, []).append(
                {"url": url, "label": label, "format": extension, "listing_title": title, "captured_utc": captured})
            if extension != "pdf":
                rejected_links += 1
                continue
            by_key.setdefault(key, []).append(
                {"url": url, "listing_page": page_url, "listing_title": title, "captured_utc": captured,
                 "aggregate": bool(AGGREGATE_LISTING.search(title))})
    legacy = _legacy_downloads(library_root, human_hashes or {})
    rows: list[dict[str, Any]] = []
    unmatched: list[str] = []
    conflicts = 0
    held: set[str] = set()
    unkeyed = 0
    for _, record in _iter_jsonl(library_root / LIBRARY_MANIFEST):
        identity = str(record["document_id"])
        key = case_key(str(record.get("case_stem", "")))
        if key:
            held.add(key)
        else:
            unkeyed += 1
        found = by_key.get(key or "")
        if not found:
            unmatched.append(identity)
            continue
        # A decision posted on a dated listing and again on an "and prior" archive page
        # has two official URLs. The dated page is the narrower evidence of when it issued.
        dated = [item for item in found if not item["aggregate"]]
        preferred = sorted(dated or found, key=lambda item: item["url"])
        primary = preferred[0]
        conflicting = len({item["listing_title"] for item in preferred}) > 1
        conflicts += conflicting
        basis, verified = "official_listing_label", None
        recorded = legacy.get(key or "")
        if recorded and (human_hashes or {}).get(identity) == recorded[1]:
            basis, verified = "legacy_download_bytes_identical", recorded[1]
            primary = next((item for item in found if item["url"] == recorded[0]), primary)
        rows.append({
            "document_id": identity,
            "case_key": key,
            "source_url": primary["url"],
            "source_url_basis": basis,
            "source_bytes_sha256": verified,
            "source_listing_page": primary["listing_page"],
            # Withheld when copies of one decision sit on listings for different years:
            # the era classifier reads this title as a date bound.
            "source_listing_title": None if conflicting else primary["listing_title"],
            "source_listing_captured_utc": primary["captured_utc"],
            "source_url_alternates": sorted({item["url"] for item in found} - {primary["url"]}),
            "listing_conflict": conflicting,
        })
    missing = [
        {"case_key": key,
         "decision_level": "appeal" if key.rsplit(".", 1)[1].startswith("a") else "hearing",
         "labels": sorted({item["label"] for item in items}),
         "formats": sorted({item["format"] for item in items}),
         "source_urls": sorted({item["url"] for item in items}),
         "listing_titles": sorted({item["listing_title"] for item in items}),
         "captured_utc": max(item["captured_utc"] for item in items)}
        for key, items in sorted(listed.items()) if key not in held]
    report = {
        "schema_version": "1.0",
        "created_utc": utc_now(),
        "library_root": str(library_root.resolve()),
        "captures": [str(path.resolve()) for path in capture_paths],
        "pages_accepted": len(pages) - len(rejected_pages),
        "pages_rejected": rejected_pages,
        "links_rejected": rejected_links,
        "listing_case_keys": len(by_key),
        "decisions": len(rows) + len(unmatched),
        "matched": len(rows),
        "unmatched_documents": unmatched[:50],
        "unmatched_count": len(unmatched),
        "listing_conflicts": conflicts,
        "listed_decisions": len(listed),
        "not_in_library_count": len(missing),
        "not_in_library_by_level": {level: sum(item["decision_level"] == level for item in missing)
                                    for level in ("hearing", "appeal")},
        "not_in_library_sample": [item["case_key"] for item in missing[:50]],
        # A library record whose case stem does not parse cannot match a listing, so a
        # decision it holds may be reported missing. Nonzero means review before acting.
        "library_records_unkeyed": unkeyed,
        "basis_counts": {basis: sum(row["source_url_basis"] == basis for row in rows)
                         for basis in ("legacy_download_bytes_identical", "official_listing_label")},
        "downloads_performed": False,
        "library_written": False,
    }
    return rows, missing, report


def _iter_jsonl(path: Path):
    with path.open(encoding="utf-8") as handle:
        for number, line in enumerate(handle, start=1):
            line = line.strip()
            if line:
                yield number, json.loads(line)
