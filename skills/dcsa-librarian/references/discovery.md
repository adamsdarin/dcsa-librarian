# Official-source discovery

Use `config/source_registry.json` as the allowlist. A search engine may help identify a potential official registry, but a result becomes eligible only after validating the canonical government source and adding that registry deliberately.

## Discovery rules

- Stay within configured HTTPS domains and path scopes.
- Honor robots rules, request delays, maximum pages, timeouts, and response-size caps.
- Record requested and resolved URLs, retrieval time, HTTP metadata, source bytes, and SHA-256 when downloading.
- Compare canonical URLs and filenames to the manifest, then use content hashes during intake review.
- Label newly found, disappeared, renamed, or changed items for review. Do not interpret disappearance as rescission.
- Do not assign `current`, `rescinded`, `superseded`, controlling authority, or applicability without explicit official evidence.
- DOHA decisions are case-research evidence, not controlling policy. Preserve hearing/appeal relationships and stable case IDs.
- Do not download authentication-gated, access-controlled, personal, export-controlled, or non-public material.

The `--download` option writes only to the independent project's quarantine directory. Publication requires a separate reviewed release workflow.

## Revision detection

A manifest hit proves the library once held that URL. It is not evidence that
the held copy is still what the source publishes today, so `discover` probes
every already-known document with a HEAD request and compares `ETag`,
`Last-Modified`, `Content-Length`, and — for anything downloaded — SHA-256
against the previous scan's snapshot. Each document carries a `change_signal`:

- `changed` — a field present in both scans holds a different value. The
  document becomes a review candidate even though it is already in the manifest.
- `unchanged` — compared on real evidence and identical.
- `unverified` — no field was comparable (the server returned no validators, the
  probe failed, or the snapshot predates this check). Never read this as clean.
- `new_to_snapshot` — no previous record; this scan is its baseline.

A source can opt out with `"verify_known": false` in the registry. That is for
sources whose records are immutable once published — the DOHA decision
collections — where probing each document every scan is cost with no possible
finding. New decisions still surface as new URLs. The command-line flag can
only narrow this further, never widen it: a source that opted out is never
probed.

`baseline_established: false` on a source means there was nothing to compare
against, so an empty change list says nothing about the source. Read
`verification_errors` and `unverified_documents` before concluding a scan was
clean. `--no-verify-known` skips the probes and leaves every known document
`unverified`.

Two source shapes defeat URL-only comparison, and both occur at DCSA:

- **Date-stamped republication.** The FCL Orientation Handbook ships as
  `FCL_Orientation_Handbook_<date>.pdf`, so a revision arrives as a *new URL*.
  Only registered coverage of the hosting section catches it; hashing does not.
- **Announcement-first change.** The Voice of Industry newsletter announces
  guidance updates before or instead of the document moving. Monitoring the
  document alone will lag the announcement.

## Checking a source

```
python custodian.py preflight --source dcsa-nisp-tools
python custodian.py preflight --source dcsa-nisp-tools --match voi
```

`preflight` fetches one source and prints every document link the parser can
see. It writes nothing — no snapshot, no report, no baseline — so it never
perturbs the state change detection depends on, and it is the correct way to
answer "is this source working" and "can the parser see these documents".

Two results matter:

- **Unreachable.** Says nothing about whether the source changed. Check network
  access first. If the page loads in a browser but not here, the site is
  rejecting the crawler: use the browser fallback below.
- **Policy unknown.** `could not read robots.txt (HTTP 403)` means the site
  refused the policy file itself, so whether crawling is permitted is unknown
  and nothing was requested. That is not a refusal by the site's policy and must
  not be reported as one. robots.txt is fetched under the user agent this
  project declares, not Python's default, so that a CDN rejecting scripted
  clients cannot masquerade as a policy decision — but a site may still refuse
  every non-browser client, and then the browser fallback is the way in.
- **Reachable, zero documents.** The links are rendered by script and the plain
  parser cannot see them. A scheduled scan pointed at that source would report
  nothing forever and look healthy doing it. Use the browser fallback.

Never diagnose a source by deleting a document from the corpus. That mutates
the governed product to test a read-only tool, breaks `doctor` parity, and
exercises manifest comparison rather than change detection. To test manifest
classification, point `--library` at a copy.

## Browser fallback

If the direct crawler cannot retrieve `robots.txt`, is rejected by a CDN, or cannot see links rendered by the public page, do not spoof a different client or disable safeguards. Use the available approved browser-control capability to navigate the configured public section normally, page by page.

1. Start only from a URL in `config/source_registry.json`.
2. Traverse breadth-first within that source's configured official domains and relevant section. Keep a visited-URL set, deduplicate canonical URLs, and honor the registry's maximum-page scope.
3. Capture each page URL, title, capture time, optional content fingerprint, and its visible document links. Do not open authentication-gated areas.
4. Save the capture using `schemas/browser-scan-page.schema.json`.
5. Run `python custodian.py browser-import --library <path> --capture <capture.json>`.
6. Review its rejected pages/links and missing-manifest candidates. Do not publish them.

A failed or inaccessible `robots.txt` response is not proof that ordinary browser review is forbidden, and it is not permission to bypass the site's controls. The browser fallback uses the public site as presented to a normal user; the deterministic importer enforces the registry boundary afterward.
