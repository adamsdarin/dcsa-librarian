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

## Browser fallback

If the direct crawler cannot retrieve `robots.txt`, is rejected by a CDN, or cannot see links rendered by the public page, do not spoof a different client or disable safeguards. Use the available approved browser-control capability to navigate the configured public section normally, page by page.

1. Start only from a URL in `config/source_registry.json`.
2. Traverse breadth-first within that source's configured official domains and relevant section. Keep a visited-URL set, deduplicate canonical URLs, and honor the registry's maximum-page scope.
3. Capture each page URL, title, capture time, optional content fingerprint, and its visible document links. Do not open authentication-gated areas.
4. Save the capture using `schemas/browser-scan-page.schema.json`.
5. Run `python custodian.py browser-import --library <path> --capture <capture.json>`.
6. Review its rejected pages/links and missing-manifest candidates. Do not publish them.

A failed or inaccessible `robots.txt` response is not proof that ordinary browser review is forbidden, and it is not permission to bypass the site's controls. The browser fallback uses the public site as presented to a normal user; the deterministic importer enforces the registry boundary afterward.
