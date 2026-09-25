# HANDOFF — dcsa-librarian

Last updated: 2026-09-24 by Codex

## Current State
2026-09-24: owner-authorized targeted FCL intake (not a sweep) is in quarantine/20260924T122142Z/dcsa-fcl: the FCL Orientation Handbook (cover "July 2026", URL-dated 20260828), the Quick Start Guide for the FCL Process and ten FCL job aids, each with an .intake.json package (quarantined_unreviewed) and intake-report.json beside the run. This closes the 2026-09-13/18 cloud-session intake of the same 12 documents, which had been triaged but never downloaded. The handbook package proposes marking both held editions (March 2021 "AID FCL Orientation Handbook" and October 2018) superseded, not deleted. SF 328 (REV. 7/2026), DTM 24-004 (Change 1) and DoDM 5220.32 V1/V2 (Change 2, 2021-12-10) are byte-identical to the official copies; verified provenance rows were appended to state/provenance/provenance.jsonl. Nothing was written to the library.

A pre-SEAD 4 Adjudicative Guidelines memo from the NARA ISOO source is quarantined for Archivist review; it is marked historical and has not been published. The DOHA provenance ledger published September 22 records official listing URLs for 10,658 decisions; 317 have byte-verified provenance and the remainder are explicitly weaker official-listing matches. One archived DOHA listing page is inaccessible, so unresolved entries remain gaps.

Librarian owns official-source discovery, integrity checks and quarantine intake; it never writes to or publishes the approved corpus. The approved September 24 monthly scan completed incompletely: all 17 enabled sources were unavailable or could not be fully verified, with zero sources cleared. Preserve its open release window and retry the unresolved sources when access is available; no further full sweep is due today. The monthly integrity audit passed (11,622 manifest records and matching human/robot files, no missing files/findings). VOI-release-watch remains without a current successful run record.

## Next
1. Archivist Evidence Reviewer: review quarantine/20260924T122142Z/dcsa-fcl (12 packages) and the four verified provenance rows, then build-candidate --intake-plan and hand to the gated Release Manager. Includes the proposed supersession of the 2018 and 2021 handbook editions.
2. Route quarantined packages from 2026-09-23 (NARA adjudicative guidelines) the same way.
3. DTM 24-004 passed its 2026-07-31 expiration with no Change 2, cancellation or incorporation posted by WHS; re-check the WHS DTM and DoDM listings and lifecycle-review the library record (currently "active").
4. Rebuild the DOHA provenance ledger when the inaccessible listing page returns; do not start another full-source sweep outside its authorized window.

## Open Questions
- gsa.gov (the SF forms library, linked from DCSA's FOCI page) is not in the source registry, so SF 328 was verified against DCSA's official copy only. Add gsa.gov to official-reference-verification? Owner decision.
- `doctor` reports two errors because the library entry point no longer carries doha_topic_taxonomy / doha_topic_coverage. Update the doctor contract or restore the keys? No document files are missing.
- The inaccessible DOHA listing page has no recovery date.

## Log
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
2026-09-15 Codex — Added structured scan receipts, read-only freshness CLI and
supervisor integration; corrected stale scheduler approval state. Unknown prior
runs remain unknown. 70 Librarian tests pass. Period satisfaction and source
requests need further audit; no source acquisition or publication was run.
2026-09-14 Codex — Verified monthly maintenance coverage gap; recorded concrete
first-of-month schedule addition. No acquisition or library writes performed.
2026-09-11 Codex — Completed cross-system role/handoff implementation and process map. Tests: 65 Librarian, 52 Archivist; three cross-system acceptance cases and shared-policy checks pass. No live publication, acquisition, scheduling, or guidance product changes. Portable regenerator assessed as a proposed recipe-driven CLI, not implemented.
2026-09-11 Codex — Cross-system workflow audit in progress. User selected Librarian -> Archivist -> approved release -> comparison and Guidance Watch. Implementing staged source intake, published navigation graph, and durable release packets with completion receipts. Existing dirty files preserved. No live library changes; installed Windows task inspection found no DCSA/FSO/Custodian-named tasks.
2026-09-10 Codex — Completed authorized implementation. Offline discovery/quarantine is exercised by the cross-system acceptance suite. Shared-policy check passes. Pre-existing untracked files remain untouched; no live source scan or scheduler change was made. Changes remain uncommitted, including preserved prior edits.
2026-09-10 Codex — Implementing the five authorized workspace improvements and accepted-answer wiki. Preserved the entire prior handoff in the archive, including pre-existing edits. Validation is in progress; do not interpret implementation as a live library release.

