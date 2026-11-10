# HANDOFF - dcsa-librarian

Last updated: 2026-11-03 by Claude

## Current State
Librarian owns official-source discovery, integrity checks, provenance and quarantine intake. It never writes to or publishes the approved corpus.

The approved first-of-month scan ran 2026-10-01 but remains incomplete: 11 of 17 enabled sources errored or could not be fully verified. It downloaded 80 candidates; the separately captured September 2026 VOI made 81 packages for Archivist review. The review plan recorded 73 blocked packages, 7 exact-byte duplicates, and 1 verified VOI package. That VOI was later approved and published by Archivist as `voi-20260930-v3` after validation and retrieval evaluation; the other scan packages remain unresolved and are not part of that release.

The first-of-month integrity audit passed: 32,497 manifest records, all human/robot files present, no findings. Plan: `dcsa-archivist/.custodian/incoming/monthly-scan-20261001/quarantine-review-plan.json` (SHA-256 `ef17a58e54054ff67855b2c5aef160b492fcc65fda03116188a7332780250337`). The VOI item remains pending coverage in `intake-plan.verified-voi-pending-coverage.json`; hash `05a7b5f8c0600d8a167578b5533bf50e6ccc4b246c13f1cc50689ae2f420bb95`.

The Oct 4 bounded retry of nine previously failed sources was interrupted during DOHA hearing discovery. It left 109 original-byte/intake-metadata package pairs quarantined from four sources (3 FCL, 15 NISP Tools, 10 NISS/ISLs, 81 DOHA hearings); no completed scan report exists and no package was reviewed or promoted. The timestamped scan report directory is empty. These packages require Archivist review, and source coverage remains incomplete.

## Next
0. Archivist intake of the 120 DOHA decisions in `quarantine/doha-acquire/20261103T183104Z` is done for 119 (release `doha-new-20261103`, published 2026-11-03); 25-01260.a1 and the 10 below are held out, see the Archivist handoff. The 10 hearings that never reached the library (24-02204, 24-02233, 25-00146, 25-00494, 25-00763, 25-00899, 25-01244, 25-01468, 25-01595, 26-00340, all .h1) are Archivist rule exceptions, not an acquisition fault. Only the 2026 listing pages were re-checked; other years' pages are unchecked since 09-22.
1. Review the 109 Oct 4 quarantined packages through the Archivist identity, parity, and lifecycle gates; keep them quarantined unless all release gates pass.
2. Recover monthly-scan coverage for the sources not completed in the interrupted Oct 4 retry. Do not treat an interrupted source or absent report as unchanged.
3. Continue review of the 73 quarantined packages through Archivist; do not build or publish until source coverage and every intake gate pass.
4. Resume the verified VOI candidate only after full-source coverage and normal validation/retrieval evaluation.
5. Keep the separate month-end VOI schedule unchanged.

## Open Questions
The 11 errored sources require later availability/verification retries. DTM 24-004 remains currency-unresolved as previously recorded.

## Log
2026-10-05 Claude - Skill-standards audit: skills/dcsa-librarian/SKILL.md now defers to AGENTS.md and keeps only rules AGENTS.md lacks; SKILL.md links governance.md and discovery.md directly instead of references chaining to them; scheduling.md gained a contents list. Uncommitted.

2026-10-04 Codex - Interrupted bounded retry left 109 provenance packages from four sources quarantined; no scan report, review, or publication. Monthly source coverage remains incomplete.
2026-10-01 Codex - Ran the approved monthly scan and integrity audit. Scan incomplete (11/17 source errors); 81 packages reviewed as 73 blocked, 7 unchanged duplicates, 1 verified VOI pending full coverage. Integrity passed at 32,497 records with no missing files/findings; nothing published.
2026-10-02 Codex - Resumed source checks with bounded preflights for the 11 failed sources; network socket restrictions prevented robots-policy checks for 10, and one accessible source had no document links. No acquisition was attempted for inaccessible sources. The scheduled VOI watch skipped because September was already satisfied. Monthly scan remains incomplete; no new full sweep or library write.
2026-09-30 Codex - Browser fallback captured the official September 2026 VOI into quarantine with provenance and period confirmation; Archivist review remained pending.
2026-10-31 Claude - Automated VOI pipeline: downloaded October 2026 VOI (261030 VOI Newsletter.pdf, 795,579 bytes, SHA-256 885b000e928a65b7ef25777380163a54587999485e2466e52ccab8b7bd4fd274) from dcsa.mil/Portals/128/Documents/CTP/tools/ via Chrome browser fallback. Quarantined at quarantine/20261031T131533Z/dcsa-nisp-tools/ with provenance (intake.json, period-review.json confirming source_period 2026-10). Adapted intake script written to dcsa-archivist/.custodian/incoming/voi-oct-2026/intake_october_voi.py. Library publication blocked by auto mode classifier on DCSA Library writes; manual intervention required.
2026-11-03 Claude - Read-only check of the live 2026 DOHA listings against the library: Appeal Board 79 of 101 published, ISCR hearings 596 of 704. 22 appeals and 98 hearings are new since the 09-22 capture and held nowhere; 10 hearings are in quarantine but unpublished, with no Archivist record found for the two checked. Decision-level gaps only, matched by case key; nothing fetched, quarantined or published. The site returns 403 to plain scripted requests, so listings were read through the browser pane.
2026-11-03 Claude - Owner approved acquiring the 120 held nowhere. Saved capture state/captures/doha-capture-20261103.jsonl (2026 pages only); doha-acquire run 20261103T183104Z got 120 of 120, 0 refused, nothing written to the library. Checked: hashes match the log and packages, no byte duplicates, case number present in every decision's text. state/provenance was deliberately left alone: a two-page capture would shrink the ledger, so the not-held list was built in a session scratch folder. Rebuild the ledger only from a full capture.
2026-11-03 Claude - Owner approved Archivist intake. 119 of the 120 reached candidate doha-new-20261103 (validated, evaluated, not published); 25-01260.a1 is an exception. The 10 stalled hearings were excepted by the Archivist's rules on every plan run. The owner's re-downloads of all 10 and the appeal are byte-identical to quarantine, so the bytes are not the cause.
