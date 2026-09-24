# HANDOFF — dcsa-librarian

Last updated: 2026-09-24 by Claude

## Current State
2026-09-24: `doha-provenance` now also reports the reverse direction: decisions a
captured DOHA listing publishes that the library does not hold. It writes
state/provenance/doha_not_in_library.jsonl (case key, hearing/appeal, all listing
URLs and titles, formats) and adds not_in_library_count / _by_level, listed_decisions
and library_records_unkeyed to the report. The 09-22 "10,658 of 10,658 matched" figure
only ever proved library -> listing; it said nothing about missing rulings. The
check has NOT been run against real data yet: the cloud session has neither the
library nor the 09-22 capture, and DOHA is unreachable from it. 99 tests pass.

2026-09-22: New `doha-provenance` command records official DOHA source URLs for
library decisions from captured listing pages. The August crawl had stopped at
page 30 on CDP timeouts, leaving exact URLs for 2,735 files and only 322 library
decisions. DOHA's CDN refuses this project's crawler outright (403 even for
robots.txt), so the documented browser fallback was used: all 40 reachable
listing pages read in the browser pane, robots.txt confirmed to allow the
Industrial-Security-Program paths. Every page and link is re-checked against the
registry allowlist by the importer, which downloads nothing and never writes to
the library. Match is by the case number and decision level DOHA prints, PDF
labels only: 10,658 of 10,658 decisions matched. 317 are byte-verified
(`legacy_download_bytes_identical`, retained bytes equal the legacy download of
that URL); the rest carry `official_listing_label`, which is explicitly weaker
than a byte match. 334 decisions are posted twice under different FileIds; both
URLs are kept. The ledger is state/provenance/doha_source_urls.jsonl and was
handed to the Archivist, which published it on 2026-09-22. 94 tests pass
(PYTHONPATH=src;.runtime). One DOHA page is down at the source
("2016 and Prior ISCR Hearing Decisions - 2" returns the site's own error), so
its decisions carry URLs only where another listing also holds them.

2026-09-18: Back on main (the feature branch, three cloud-session commits and two
unpushed local-main commits were merged and pushed). Scans with --download now close
provenance gaps: a document the library holds without an official URL is fetched and,
only on an exact byte match, written to state/provenance/provenance.jsonl for the
Archivist's import-provenance. 88 tests pass (run with PYTHONPATH=src;.runtime).

Expected-publication polling now requires confirm-period evidence after actual
source review; filename matches and legacy markers cannot end the VOI window.
Shared public-source requests route through ../EVIDENCE-REQUESTS.md. 72 tests pass; issue periods now use the configured local date at UTC boundaries.
Structured scheduled-run records and scan-status freshness checks are implemented.
Supervisor now distinguishes source freshness from library readiness, including
registry/source coverage, library identity and timezone-aware due times. Live
status is unknown for all three jobs because earlier runs lack structured receipts;
no source success was backfilled. Windows tzdata installed under ignored .runtime.
Both month-end VOI and first-of-month maintenance were explicitly approved and
enabled September 14; older approval-pending notes were stale. See workspace
AUTOMATION-UPDATE-PROPOSAL.md. No live scan was run in this checkpoint.
Discovery/integrity plane. Scheduled wrappers now download quarantined sources and accept the rendered --job syntax. New/changed downloads emit Archivist intake packages; no-library discovery can acquire bootstrap inputs. GET redirect provenance is captured and allowlist checked. 65 offline tests pass. No live acquisition or scheduler installation was performed; no DCSA/FSO/Custodian-named Windows tasks were found on inspection.

Live Git state: run `python ../workspace_health.py status`; prior details are in `HANDOFF-archive.md`.

## Next
0. Run `doha-provenance` locally against the existing 09-22 capture and review
   doha_not_in_library.jsonl. If library_records_unkeyed is nonzero, check those
   records before treating any listed decision as missing. Anything only on the down
   archive page cannot appear.
1. Re-run `doha-provenance` when the down archive page returns, and when new
   decisions arrive; the ledger is rebuilt whole, not appended.
2. The browser capture is a manual step: the CDN blocks the crawler, so a
   scheduled job cannot refresh DOHA provenance unattended today.
3. Deploy and verify the local scheduler and agent-host cycle; config alone is not evidence of recurring operation.
2. Use ../dcsa-archivist/agents/conductor.md for package review and gated intake; do not use historical intake_voi.py as the general publication path.
3. Preserve existing untracked scripts/snapshots; see ../PROCESS-MAP.md for scope and bootstrap recommendations.

## Open Questions
No new decision needed for the authorized implementation. Prior source-acquisition
and migration questions remain scoped separately as noted above.

## Log
2026-09-24 Claude — Added the listing -> library direction to doha-provenance so
missing rulings can be found offline from the existing capture. Non-PDF postings with
a valid case number count as listed (a decision posted only as HTML is still missing)
but never become source URLs. Library records whose case stem does not parse are
counted, because they can make a held decision look missing. Not yet run on real data.
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
