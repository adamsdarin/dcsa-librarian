from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import ssl
import urllib.error
import urllib.parse
import urllib.request
import urllib.robotparser
from datetime import datetime, timezone
from pathlib import Path


USER_AGENT = "DCSA-Library-Custodian/0.1 (+local-governance-audit)"


def allowed_hosts(registry: Path) -> set[str]:
    payload = json.loads(registry.read_text(encoding="utf-8"))
    return {host.lower().removeprefix("www.") for source in payload["sources"] if source.get("enabled") for host in source.get("allowed_domains", [])}


def host_allowed(url: str, allowed: set[str]) -> bool:
    host = (urllib.parse.urlparse(url).hostname or "").lower().removeprefix("www.")
    return any(host == item or host.endswith("." + item) for item in allowed)


def robots_allowed(url: str, cache: dict[str, bool]) -> bool:
    parsed = urllib.parse.urlparse(url)
    origin = f"{parsed.scheme}://{parsed.netloc}"
    if origin in cache:
        return cache[origin]
    parser = urllib.robotparser.RobotFileParser(origin + "/robots.txt")
    try:
        parser.read()
        result = parser.can_fetch(USER_AGENT, url)
    except Exception:
        result = False
    cache[origin] = result
    return result


def verify(item: dict, allowed: set[str], robots_cache: dict[str, bool]) -> dict:
    url = item["url"]
    result = {**item, "checked_utc": datetime.now(timezone.utc).isoformat(), "submitted_url": url}
    if not host_allowed(url, allowed):
        return {**result, "status": "outside_registry"}
    if not robots_allowed(url, robots_cache):
        return {**result, "status": "robots_disallowed"}
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Range": "bytes=0-65535"})
    try:
        with urllib.request.urlopen(request, timeout=25, context=ssl.create_default_context()) as response:
            data = response.read(65536)
            return {
                **result,
                "status": "resolved",
                "http_status": response.status,
                "final_url": response.geturl(),
                "mime_type": response.headers.get_content_type(),
                "content_length_header": response.headers.get("Content-Length"),
                "sample_bytes": len(data),
                "sample_sha256": hashlib.sha256(data).hexdigest(),
            }
    except urllib.error.HTTPError as exc:
        return {**result, "status": "http_error", "http_status": exc.code, "final_url": exc.geturl()}
    except Exception as exc:
        return {**result, "status": "access_error", "error": f"{type(exc).__name__}: {exc}"}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--registry", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--collection", action="append", default=[])
    args = parser.parse_args()
    rows = [json.loads(line) for line in args.manifest.read_text(encoding="utf-8").splitlines() if line.strip()]
    selected = []
    for row in rows:
        url = row.get("canonical_source_url") or row.get("source_url")
        if not url or (args.collection and row.get("collection_id") not in args.collection):
            continue
        selected.append({"document_id": row["document_id"], "collection_id": row["collection_id"], "robot_text_path": row["robot_text_path"], "url": url})
    allowed = allowed_hosts(args.registry)
    robots_cache: dict[str, bool] = {}
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        futures = [pool.submit(verify, item, allowed, robots_cache) for item in selected]
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())
    results.sort(key=lambda row: (row["collection_id"], row["document_id"], row["robot_text_path"]))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in results), encoding="utf-8", newline="\n")
    counts: dict[str, int] = {}
    for row in results:
        counts[row["status"]] = counts.get(row["status"], 0) + 1
    print(json.dumps({"checked": len(results), "counts": counts, "output": str(args.output)}, indent=2))


if __name__ == "__main__":
    main()
