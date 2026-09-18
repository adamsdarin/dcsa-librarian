# Intake handoff

This role stops at quarantine. Validated candidates are handed to the DCSA
Archivist; nothing here organises the corpus, rebuilds manifests or prepares a
release. The gates in [governance.md](governance.md) apply to promotion, and
promotion is not this role's to perform.

## Order of operations

1. **Audit first.** `python custodian.py doctor --library <path>`. Adding
   documents to a library that already fails its own gates compounds the
   problem rather than fixing it.
2. **Discover and triage.** Decide which candidates are in scope before
   acquiring anything.
3. **Acquire with authorisation.** `discover --download` stages originals in
   the quarantine directory, outside the active corpus, and writes an intake
   package beside each file.
4. **Hand off.** The quarantine run directory is the deliverable.

## What an intake package asserts, and what it does not

Each downloaded document gets `<filename>.intake.json`, shaped to
[intake-package.schema.json](../../../schemas/intake-package.schema.json). It
records what was retrieved and proves what was received: requested and resolved
URL, retrieval time, filename, MIME type, SHA-256, byte count, and the HTTP
validators.

`approval_state` is fixed at `quarantined_unreviewed`. Nothing this role
produces is approved, and the package cannot claim otherwise.

The package asserts **no** lifecycle, authority or applicability. A source's
`authority_hint` is a property of where the document was found, not a finding
about the document. Currency is not inferred from a live link. Those
determinations need official evidence and belong to review.

`submission_id` is derived from the resolved URL and the content hash, so
re-downloading identical bytes from the same URL yields the same id. A
resubmission is recognisable as one rather than arriving as a new document.

## Supersession

A revised edition arriving under a new filename does not delete the edition it
replaces. Mark the older record superseded, with evidence of the replacement;
official source documents are preserved. Deleting a superseded edition destroys
the record of what guidance was in force at a past date, which is exactly what a
governed evidence library exists to answer.

## Scope exclusions

`config/catalog_exclusions.json` records documents deliberately kept out of the
corpus, each with a reason and a date. An exclusion is a decision, not a filter:
excluded documents are still crawled, still counted, still snapshotted, and
still listed under `excluded` in every report. They are simply not re-offered
for review and are never downloaded. Remove an entry to put a document back in
scope.

This exists because document links are collected from anywhere on an allowed
domain, not only under a source's `crawl_path_prefix` — a page may legitimately
link a PDF stored elsewhere in `/Portals/`. The cost is that site-wide
navigation links are swept in too, and without a record of the decision they
would be re-triaged on every scan.
