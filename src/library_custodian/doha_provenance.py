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
# DOHA publishes two collections; the library keeps them as two groups. A listing
# page belongs to the group of the registry source whose path it sits under.
GROUPS = {"doha-iscr-hearings": "ISCR Hearing Decisions", "doha-appeals": "DOHA Appeal Board Decisions"}


def decision_group(key: str) -> str:
    """The group a decision belongs to, from the level DOHA prints: h = hearing, a = appeal.

    Not from the listing page: DOHA cross-posts some rulings on both a hearing page and
    an Appeal Board page, and the Archivist classifies by the same letter.
    """
    return GROUPS["doha-appeals"] if key.rsplit(".", 1)[1].startswith("a") else GROUPS["doha-iscr-hearings"]


def case_key(value: str, pattern: re.Pattern[str] = STEM) -> str | None:
    """The case identity DOHA prints: year, number and decision level, normalized."""
    match = pattern.match(value.strip())
    if not match:
        return None
    suffix = (match.group("suffix") or "").lower()
    return f"{match.group('year')}-{int(match.group('number')):05d}{suffix}.{match.group('level').lower()}"


def case_base(key: str) -> str:
    """Year, number and decision type: '19-00803-sd.h1' -> '19-00803.h'. A hearing and
    its appeal are different rulings, so they never stand in for each other."""
    stem, level = key.split(".", 1)
    return "-".join(stem.split("-")[:2]) + "." + level[0]


def variant_difference(missing_key: str, held_key: str) -> str:
    """How a held key of the same case differs from a missing one.

    A different decision number (h1 vs h2, a1 vs a2) is DOHA numbering a separate
    ruling -- a decision after remand, a second appeal -- so it is a missing ruling,
    not a naming mismatch. Only a suffix difference (-SD) plausibly names one file twice.
    """
    (missing_stem, missing_level), (held_stem, held_level) = missing_key.split(".", 1), held_key.split(".", 1)
    suffix = missing_stem.split("-")[2:] != held_stem.split("-")[2:]
    number = missing_level != held_level
    return "suffix_and_decision_number" if suffix and number else "suffix" if suffix else "decision_number"


def case_year(key: str) -> str:
    """The year DOHA numbered the case in -- not the year the decision issued."""
    year = int(key[:2])
    return str(1900 + year if year >= 50 else 2000 + year)


def _allowed_pages(registry: dict[str, Any]) -> list[tuple[list[str], str, str]]:
    allowed = []
    for source in registry.get("sources", []):
        if not source.get("enabled", True):
            continue
        prefix = source.get("crawl_path_prefix")
        if prefix and source.get("allowed_domains"):
            allowed.append((source["allowed_domains"], str(prefix), str(source.get("id", ""))))
    return allowed


def _page_source(url: str, allowed: list[tuple[list[str], str, str]]) -> str | None:
    parts = urllib.parse.urlsplit(url)
    if parts.scheme != "https":
        return None
    for domains, prefix, source_id in allowed:
        if domain_allowed(url, domains) and parts.path.casefold().startswith(prefix.casefold()):
            return source_id
    return None


def _page_allowed(url: str, allowed: list[tuple[list[str], str, str]]) -> bool:
    return _page_source(url, allowed) is not None


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


def _legacy_downloads(library_root: Path, human_hashes: dict[str, str]
                      ) -> tuple[dict[str, tuple[str, str]], dict[str, Any]]:
    """Case key -> (URL, sha256) for files a recorded crawl actually downloaded, and
    which of the inputs byte verification needs were present."""
    base = library_root / LEGACY_IMPORT
    progress, inventory = base / "download_progress.json", base / "inventory.csv"
    inputs: dict[str, Any] = {"download_progress_found": progress.is_file(), "inventory_found": inventory.is_file(),
                              "human_hashes_supplied": len(human_hashes), "recorded_downloads": 0,
                              "inventory_rows_with_recorded_url": 0}
    if not progress.is_file() or not inventory.is_file() or not human_hashes:
        return {}, inputs
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
    inputs.update(recorded_downloads=len(urls), inventory_rows_with_recorded_url=len(output))
    return output, inputs


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
        source_id = _page_source(page_url, allowed) or ""
        group = GROUPS.get(source_id, source_id)
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
                {"url": url, "label": label, "format": extension, "listing_title": title, "captured_utc": captured,
                 "group": group})
            if extension != "pdf":
                rejected_links += 1
                continue
            by_key.setdefault(key, []).append(
                {"url": url, "listing_page": page_url, "listing_title": title, "captured_utc": captured,
                 "aggregate": bool(AGGREGATE_LISTING.search(title))})
    legacy, byte_inputs = _legacy_downloads(library_root, human_hashes or {})
    hashed_ids = 0
    rows: list[dict[str, Any]] = []
    unmatched: list[str] = []
    conflicts = 0
    held: set[str] = set()
    unkeyed = 0
    for _, record in _iter_jsonl(library_root / LIBRARY_MANIFEST):
        identity = str(record["document_id"])
        hashed_ids += identity in (human_hashes or {})
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
    held_by_base: dict[str, list[str]] = {}
    for key in held:
        held_by_base.setdefault(case_base(key), []).append(key)
    missing = [
        {"case_key": key,
         "group": decision_group(key),
         # Which collections' listing pages carry it; two means DOHA cross-posted it.
         "listed_under": sorted({item["group"] for item in items}),
         "decision_level": "appeal" if key.rsplit(".", 1)[1].startswith("a") else "hearing",
         "labels": sorted({item["label"] for item in items}),
         "formats": sorted({item["format"] for item in items}),
         "source_urls": sorted({item["url"] for item in items}),
         # Older decisions are often posted twice, as PDF and as HTML, each under its own
         # FileId. Keep which URL is which, so a fetch can ask for the PDF.
         "urls_by_format": {fmt: sorted({item["url"] for item in items if item["format"] == fmt})
                            for fmt in sorted({item["format"] for item in items})},
         "listing_titles": sorted({item["listing_title"] for item in items}),
         "captured_utc": max(item["captured_utc"] for item in items),
         # The same case held under another suffix or decision number. See
         # variant_difference: only a suffix difference may be the same ruling.
         "held_variants": [{"case_key": held_key, "differs_by": variant_difference(key, held_key)}
                           for held_key in sorted(held_by_base.get(case_base(key), []))]}
        for key, items in sorted(listed.items()) if key not in held]
    listed_by_listing: dict[str, int] = {}
    listing_groups: dict[str, str] = {}
    listed_by_group: dict[str, int] = {}
    for items in listed.values():
        for title in {item["listing_title"] for item in items}:
            listed_by_listing[title] = listed_by_listing.get(title, 0) + 1
        for item in items:
            listing_groups[item["listing_title"]] = item["group"]
    cross_posted = sum(len({item["group"] for item in items}) > 1 for items in listed.values())
    for key in listed:
        group = decision_group(key)
        listed_by_group[group] = listed_by_group.get(group, 0) + 1
    byte_inputs["human_hash_ids_in_manifest"] = hashed_ids
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
        "listed_by_listing": dict(sorted(listed_by_listing.items())),
        "listing_groups": dict(sorted(listing_groups.items())),
        "listed_by_group": dict(sorted(listed_by_group.items())),
        "listed_under_both_collections": cross_posted,
        # Why a byte-verified count is what it is: every input must be present and the
        # supplied hashes must be keyed by the manifest's current document IDs.
        "byte_verification_inputs": byte_inputs,
        "basis_counts": {basis: sum(row["source_url_basis"] == basis for row in rows)
                         for basis in ("legacy_download_bytes_identical", "official_listing_label")},
        "downloads_performed": False,
        "library_written": False,
    }
    return rows, missing, report


def summarize_missing(missing: list[dict[str, Any]], report: dict[str, Any]) -> dict[str, Any]:
    """Triage the listed-but-not-held decisions per group, by case year and listing."""
    groups: dict[str, dict[str, Any]] = {}
    for group, listed in report.get("listed_by_group", {}).items():
        groups[group] = {"listed": listed, "not_held": 0, "by_case_year": {}}
    by_listing: dict[str, int] = {}
    for item in missing:
        entry = groups.setdefault(item["group"], {"listed": 0, "not_held": 0, "by_case_year": {}})
        entry["not_held"] += 1
        year = case_year(item["case_key"])
        entry["by_case_year"][year] = entry["by_case_year"].get(year, 0) + 1
        for title in item["listing_titles"]:
            by_listing[title] = by_listing.get(title, 0) + 1
    listing_groups = report.get("listing_groups", {})
    listings = []
    for title, listed in report.get("listed_by_listing", {}).items():
        count = by_listing.get(title, 0)
        listings.append({"listing_title": title, "collection": listing_groups.get(title, ""), "not_held": count,
                         "listed": listed, "share_not_held": round(count / listed, 3) if listed else 0.0})
    listings.sort(key=lambda row: (row["collection"], -row["share_not_held"], row["listing_title"]))
    for entry in groups.values():
        entry["by_case_year"] = dict(sorted(entry["by_case_year"].items()))
    variants = [item for item in missing if item.get("held_variants")]
    non_pdf = [item for item in missing if "pdf" not in item["formats"]]
    kinds: dict[str, int] = {}
    for item in variants:
        for variant in item["held_variants"]:
            kinds[variant["differs_by"]] = kinds.get(variant["differs_by"], 0) + 1
    return {
        "not_held": len(missing),
        "groups": dict(sorted(groups.items())),
        "by_listing": listings,
        "listed_under_both_collections": report.get("listed_under_both_collections", 0),
        "held_variant_count": len(variants),
        "held_variant_kinds": dict(sorted(kinds.items())),
        "held_variant_sample": [{"case_key": item["case_key"], "held_variants": item["held_variants"]}
                                for item in variants[:25]],
        "non_pdf_only_count": len(non_pdf),
        "non_pdf_only_sample": [item["case_key"] for item in non_pdf[:25]],
    }


def format_summary(summary: dict[str, Any], report: dict[str, Any]) -> str:
    """Plain-text rendering of summarize_missing for a terminal."""
    lines = [f"Listed by DOHA, not in library: {summary['not_held']}"]
    if report.get("library_records_unkeyed"):
        lines.append(f"WARNING: {report['library_records_unkeyed']} library records have unparseable case stems; "
                     "some of these may be held under another name.")
    inputs = report.get("byte_verification_inputs", {})
    if inputs.get("human_hashes_supplied") and not report.get("basis_counts", {}).get("legacy_download_bytes_identical"):
        lines.append("WARNING: hashes were supplied but no decision is byte-verified; this ledger would downgrade "
                     "published provenance. Inputs: " + ", ".join(f"{k}={v}" for k, v in inputs.items()))
    for group, entry in summary["groups"].items():
        lines += ["", f"== {group}: {entry['not_held']} of {entry['listed']} listed not held", "",
                  "  Case year   Not held"]
        lines += [f"  {year:<11}{count:>9}" for year, count in entry["by_case_year"].items()]
    lines += ["", "Listing pages (not held / listed). Group is by decision level (h/a), not page;",
              f"{summary['listed_under_both_collections']} decisions are posted on both a hearing and an Appeal Board page."]
    collection = None
    for row in summary["by_listing"]:
        if row["collection"] != collection:
            collection = row["collection"]
            lines += ["", f"  {collection} pages"]
        lines.append(f"  {row['not_held']:>6} / {row['listed']:<6}{row['share_not_held']:>7.1%}  {row['listing_title']}")
    kinds = ", ".join(f"{kind}: {count}" for kind, count in summary["held_variant_kinds"].items()) or "none"
    lines += ["", f"Same case held under another number or suffix: {summary['held_variant_count']} ({kinds})",
              "  A different decision number (h1/h2, a1/a2) is a separate ruling and is still missing;",
              "  only a suffix difference may be the same file under another name."]
    lines += [f"  {row['case_key']}  held: " + ", ".join(f"{v['case_key']} ({v['differs_by']})" for v in row["held_variants"])
              for row in summary["held_variant_sample"]]
    lines += ["", f"Posted only in a non-PDF format: {summary['non_pdf_only_count']}"]
    lines += [f"  {key}" for key in summary["non_pdf_only_sample"]]
    return "\n".join(lines)


def _iter_jsonl(path: Path):
    with path.open(encoding="utf-8") as handle:
        for number, line in enumerate(handle, start=1):
            line = line.strip()
            if line:
                yield number, json.loads(line)
