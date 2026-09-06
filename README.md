# DCSA Librarian

This is the model-agnostic intake framework for a governed DCSA evidence library. The DCSA Librarian discovers official-source material, validates proposed acquisitions, and places candidates into quarantine for controlled intake. It is not part of the library corpus and it does not answer FSO questions.

Its two operating planes are deliberately separated:

1. **Integrity plane:** validates organization, manifest truthfulness, human/robot parity, entry-point closure, duplicate identifiers, and SQLite index integrity.
2. **Discovery plane:** checks approved public source registries for new, removed, or changed documents and creates quarantined intake candidates.

Discovery never publishes directly. Internet content remains untrusted until provenance, identity, extraction, parity, authority, lifecycle, and release gates pass.

## Commands

```powershell
python custodian.py doctor --library "C:\path\to\DCSA Library"
python custodian.py discover --library "C:\path\to\DCSA Library"
python custodian.py discover --library "C:\path\to\DCSA Library" --source dcsa-nisp-tools --download
python custodian.py browser-import --library "C:\path\to\DCSA Library" --capture "C:\path\to\browser-capture.json"
```

`doctor` and `discover` are read-only with respect to the active library. Reports, snapshots, and candidate downloads are written under this project's ignored `state/` and `quarantine/` directories unless another output directory is explicitly supplied. The legacy `dcsa-custodian` command name remains stable for compatibility; it does not define the agent's role.

When a public source rejects the direct HTTP crawler or requires rendered navigation, the Librarian may traverse the allowlisted section page by page in an approved browser. The browser produces a capture conforming to `schemas/browser-scan-page.schema.json`; `browser-import` validates its domains, rejects out-of-scope links, compares official document links with the manifest, and writes review candidates. It never downloads or publishes from the browser capture.

## Safety boundary

- Consumer and producer bots cannot publish active content.
- Discovery follows the configured domain/path allowlist, honors robots rules, limits crawl depth and response size, and uses a descriptive user agent.
- Browser fallback uses ordinary public navigation and does not disguise the client, defeat access controls, or reinterpret a failed `robots.txt` request as permission for a headless crawl.
- A missing or changed web document produces a review candidate. It is not silently added, deleted, superseded, or labeled current.
- The Librarian may inspect human-readable artifacts for parity and extraction validation; ordinary retrieval bots may not.
- Release promotion is intentionally not implemented in version 0.1. A broken library must first be recovered and a reviewed atomic-release design implemented.

## Related projects

- **DCSA Archivist** — organizes, enriches, indexes, and stages approval-gated releases from validated intake candidates.
- **DCSA Comparison Bot** — reads this project's `candidates.jsonl` and a library manifest, and reports which existing document a new release changes and what changed. It closes the gap between "this URL is new" and "this is a newer edition of that". Lives in its own repository, `adamsdarin/dcsa-comparison-bot`.
