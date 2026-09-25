# HANDOFF — dcsa-librarian

Last updated: 2026-09-25 by Claude

## Current State
Librarian owns official-source discovery, integrity checks and quarantine intake; it
never writes to or publishes the approved corpus.

2026-09-24 intake: the owner-authorized targeted FCL intake (FCL Orientation Handbook,
cover "July 2026"; Quick Start Guide; ten job aids; 12 packages from
quarantine/20260924T122142Z/dcsa-fcl) and the 2026-09-23 NARA ISOO Adjudicative
Guidelines package were published by the Archivist in release fcl-intake-20260924b.
The 2018 and 2021 handbook editions are marked superseded, not deleted. Byte-verified
provenance rows for SF 328, DTM 24-004 and DoDM 5220.32 V1/V2 were applied. DTM 24-004
is recorded currency_unresolved: past its 2026-07-31 expiration with no Change 2,
cancellation or incorporation posted by WHS.

2026-09-24 monthly run: the approved scan completed incompletely. All 17 enabled sources
were unavailable or could not be fully verified, so no source is cleared and the release
window stays open for retry. The integrity audit passed (11,622 manifest records, no
missing files or findings). VOI-release-watch still has no successful run record.
`doctor` no longer requires doha_topic_taxonomy / doha_topic_coverage (the Archivist
entry point has lacked them since at least 09-09) and now also checks
doha_local_indexes.

DOHA provenance: the 09-22 ledger (state/provenance/doha_source_urls.jsonl, published by
the Archivist) records official listing URLs for 10,658 of 10,658 library decisions; 317
byte-verified, the rest official_listing_label. That only proves library -> listing.
`doha-provenance` now also reports decisions a listing publishes that the library lacks
(state/provenance/doha_not_in_library.jsonl), and `--summary` triages them by case year,
hearing/appeal, listing (>= 50% missing flagged as a suspected capture/import gap), cases
held under another suffix or level number, and non-PDF-only postings. NOT yet run on
real data. The 09-22 report and capture are not in this checkout's state/, so their
location must be found first. One archived DOHA listing page ("2016 and Prior ISCR
Hearing Decisions - 2") is inaccessible with no recovery date.

## Next
1. Find the 09-22 DOHA capture and report, back up state/provenance, then run
   `python custodian.py doha-provenance --library <root> --capture <file>...
   --human-hashes <PRODUCTION_AUDIT.json> --summary`. Confirm matched = 10,658 and
   legacy_download_bytes_identical = 317 before trusting the output; without
   --human-hashes the rebuilt ledger downgrades the 317 byte-verified rows.
2. Retry the unresolved sources from the incomplete 2026-09-24 monthly scan when access
   is available; no further full sweep outside the authorized window.
3. Re-check the WHS DTM and DoDM listings for DTM 24-004 and lifecycle-review its record.
4. Rebuild the DOHA provenance ledger when the inaccessible listing page returns.
5. Save future DOHA browser captures to a fixed, recorded path; the 09-22 one was not.

## Open Questions
- gsa.gov (the SF forms library, linked from DCSA's FOCI page) is not in the source
  registry, so SF 328 was verified against DCSA's official copy only. Add gsa.gov to
  official-reference-verification? Owner decision.
- The inaccessible DOHA listing page has no recovery date.

## Log
2026-09-25 Claude — Reconciled two local stashes with main. Today's uncommitted work
(Codex scan, Claude FCL/NARA intake and Archivist publication, doctor contract fix) is merged
here with the doha-provenance changes. A 2026-09-03 stashed HANDOFF (end-to-end pipeline
confirmation, manual VOI rollback, ISOO Notice 2026-06 in quarantine) was never recorded on
main; it is preserved in HANDOFF-archive.md, not restored as current state.
2026-09-24 Claude — Retired branch claude/dcsa-comparison-bot-k0ttop. Its two commits
staged the Comparison Bot and then removed it again, so its only net change was a
HANDOFF/README edit based on the 09-02 tree. Byte comparison against the bot's own
repo showed nothing unique: 21 files identical, 7 later revisions, 5 added there.
Kept only its purpose: README now names the related projects.
2026-09-24 Claude — Merged PR #3 (--summary) into main after PR #2. Both were merged
without CI (the repo has none) or human review, on the user's instruction; the only
validation is the offline suite and a synthetic end-to-end run.
2026-09-24 Claude — Added --summary. A hearing and its appeal never count as variants
of each other; only a different suffix or level number (h1/h2) does, since those are
plausible naming mismatches. The 50% capture-gap threshold is a heuristic constant
(CAPTURE_GAP_SHARE), chosen so a mostly-missing listing reads as a capture problem.
2026-09-24 Claude — Added the listing -> library direction to doha-provenance so
missing rulings can be found offline from the existing capture. Non-PDF postings with
a valid case number count as listed (a decision posted only as HTML is still missing)
but never become source URLs. Library records whose case stem does not parse are
counted, because they can make a held decision look missing. Not yet run on real data.
2026-09-24 Claude (as Archivist) — Consumed quarantine/20260924T122142Z/dcsa-fcl: all 12 packages published
in Archivist release fcl-intake-20260924b (INDUSTRIAL_SECURITY/TOOLS/DCSA_ISSUED_JOB_AIDS); 2018/2021
handbooks marked superseded, not deleted. The 4 verified provenance rows were applied (SF 328, DoDM 5220.32
V1/V2, DTM 24-004). The 2026-09-23 NARA Adjudicative Guidelines package was published in the same release.
DTM 24-004 recorded currency_unresolved (past stated expiration, unconfirmed by WHS). Doctor's
doha_topic_taxonomy/doha_topic_coverage requirement was stale (Archivist entry has lacked them since at least
09-09); removed from ENTRY_PATH_KEYS, doha_local_indexes now checked too, 2 tests added; doctor now ready with
no findings. Uncommitted. 7 unrelated test_schedule/test_status errors need the missing tzdata package.
2026-09-24 Codex — Ran the owner-approved monthly scan and integrity audit. All 17 registered sources failed availability/verification, so the scan remains incomplete and makes no clean-source claim; the release window remains open for later retry. Integrity passed across 11,622 records with no missing files or findings. No library publication occurred.
2026-09-24 Claude — Owner-authorized targeted FCL acquisition. Ran doctor first (0 missing files; 2 entry-point contract errors unrelated to intake). The Librarian Fetcher reached DCSA and WHS normally; nothing was blocked. Fetched the 12 FCL documents from the Facility-Clearances listing and packaged them with the existing writer. None is byte-identical to any library file. Edition dates come from the document text and metadata, not filenames; the handbook's cover says July 2026 although its URL says 20260828. The /CTP/FC/ and /CTP/fc/ handbook URLs return the same bytes, so there is one package. SF 328, DTM 24-004 and DoDM 5220.32 V1/V2 are byte-identical to the official copies, so they were recorded as provenance rows, not re-quarantined. WHS still lists DTM 24-004 as CH 1 expiring 2026-07-31, with incorporation into DoDM 5220.32 V1 pending. No code changes; nothing committed.
2026-09-23 Codex — Read-only scan-status confirmed no valid structured receipts for monthly-scan, monthly-integrity or VOI-release-watch. Status remains unknown, not successful; no out-of-cycle sweep was started.
2026-09-23 Claude — Operator handed in a retyped 2017 PDF of the 2005 Adjudicative
Guidelines with no official URL. It matches no official file byte-for-byte, so the
operator chose to ingest the NARA ISOO copy (archives.gov, allowlisted under
official-reference-verification) instead; the retyped copy's hash is noted in the
package only for reference. Fetched with the Librarian's own Fetcher and package
writer; marked superseded/historical, not current policy.
2026-09-22 Claude — Added doha-provenance. DOHA addresses decisions by opaque
FileId, so a URL can only come from the listing that names the file; a case number
can never produce one. The basis is recorded per row because a listing label is
weaker evidence than matching bytes, and a decision posted on two listings keeps
both URLs and withholds the year, which the Archivist reads as a date bound. No
document was downloaded and the library was not written.
2026-09-18 Claude — Added byte-verified provenance to discovery. A name match alone is
never provenance; bytes_differ rows go to the Evidence Reviewer. This is how the
Rebuilder's 749 retained-bytes-only records can gain official URLs over time.
2026-09-18 Claude — Merged three cloud-session commits (Sept 7-13, pushed only to the
feature branch) into the local line: URL percent-encoding, pinned failing URLs, and
config/catalog_exclusions.json scope decisions (excluded documents are still crawled
and reported, never re-offered or downloaded). Both sides had built intake packages;
kept Codex's writer and adopted the cloud builder's stable url+hash submission_id and
required-field check. That session's FCL intake (12 in-scope documents) still needs a
library doctor and a handbook-edition check before acquisition.
2026-09-16 Codex — Fixed local-calendar period selection; boundary regression and
all 72 Librarian tests pass. No acquisition or publication run.
2026-09-15 Codex — Closed filename-based period suppression; added retained,
hash-bound issue-period review and source-request handoff instructions. No live
issue confirmed, source downloaded or library publication performed.
