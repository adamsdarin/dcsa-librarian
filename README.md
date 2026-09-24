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

## Scheduled acquisition and handoff

For watches with an expected publication, URL matching only identifies a lead.
Use `confirm-period --job <job> --period YYYY-MM --library <root> --receipt <review.json>`
after actual source review. Receipt fields: source_uri, source_artifact (relative
to the receipt directory), source_sha256, reviewed_by, reviewed_utc, issue_locator,
review_basis, issue_period_verified (true), and source_period (YYYY-MM). It retains
source evidence locally and binds the marker to that library and registry. An old
matching filename or legacy marker cannot suppress future polls. No source is
published by this confirmation.

In the shared workspace, EVIDENCE-REQUESTS.md and workflow_requests.py own the
public-source inbox. Missing sources route here; do not treat a request as approval
to bypass registry controls. Acquisition does not close the request: approved
release availability must be verified after Archivist review/publication.

`python custodian.py scan-status --library <root>` reads acquisition freshness
without network access. Scheduled jobs now write structured latest-run JSON beside
their readable reports, binding discovery to the library and source registry.
Missing records are unknown; partial coverage, verification failures, zero-document
results, changed registries and overdue runs are not clean checks. Skipped polls
require review of the original period evidence. Windows installs require tzdata
for daylight-saving-aware due times (declared in pyproject.toml); a repository-local
installation under ignored .runtime is supported by custodian.py.

The Windows/Unix wrappers download new or positively changed sources into quarantine and emit `.intake.json` packages. They accept both a bare job ID and `--job <id>`. `config/schedule.json` declares cadence; it does not install tasks. Archivist reviews packages and uses `build-candidate --intake-plan` before gated publication. See `../dcsa-archivist/agents/conductor.md` for the complete agent cycle. The historical `scripts/intake_voi.py` helper is not the general intake path.

## Related projects

- **DCSA Archivist** (`adamsdarin/dcsa-archivist`) — reviews this project's intake packages, organizes, enriches and indexes the library, and stages approval-gated releases.
- **DCSA Comparison Bot** (`adamsdarin/dcsa-comparison-bot`) — reads this project's `candidates.jsonl` and a library manifest, and reports which document already held a new release changes and what changed, as proposals for human review. It closes the gap between "this URL is new" and "this is a newer edition of that". Nothing here imports from it.
- **DCSA Library Rebuilder** (`adamsdarin/dcsa-library-rebuilder`) — a standalone agent that rebuilds a DCSA Library into an empty destination and proves the result; the rebuilt copy is a one-time snapshot that only stays current through this project and the Archivist. Its census reads the official URLs this project's byte-verified provenance publishes, which is how a document classed `retained_bytes_only` becomes reacquirable from an official source.
