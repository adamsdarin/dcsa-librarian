# HANDOFF — dcsa-comparison-bot

Last updated: 2026-09-06T00:00:00Z by Claude

## Current State
New project. Third plane in the DCSA family, sitting between `dcsa-librarian`
(discovery) and `dcsa-archivist` (lifecycle and release): given a newly released
document, which library document does it change, and what changed.

Built because the Archivist's 2026-09-01 session found ten material supersessions
**by hand** (DAAPM→DAAG, SEAD-3 desktop aid→revisedMay2024, NIST SP 800-61r2→r3,
IC Tech Spec v1.5→v1.5.1, and others), recorded them as English prose inside
`metadata_decisions.json` note fields, and routed them nowhere. The Librarian's
change detection stops at the URL layer (`known` vs `missing_from_manifest`);
nothing in either project could say that a new file is a newer edition of an
existing one.

Five commands, stdlib only, no network: `doctor`, `baseline`, `compare`, `diff`,
`propose`. 30 unit tests pass. Four of the ten hand-found supersessions are used
as fixtures and are reproduced automatically — three `deterministic`, one
`inferred`.

## Design decisions and why

- **No confidence score.** A score invites a threshold; a threshold invites
  automation; automating a lifecycle call is what both sibling contracts forbid.
  Findings carry `basis: deterministic | inferred` instead, plus the signals.
- **Different official document numbers are never paired.** ISL 2024-01 and
  ISL 2021-02 are concurrently in force. Title similarity between them would
  manufacture a supersession. Suppressed routes are recorded, not silent.
- **No PDF extraction.** Extraction belongs to the planes that preserve source
  provenance first. A missing text comparison is reported, not papered over.
- **Only `newer_edition_candidate` becomes a proposed decision**, and only when
  deterministic unless `--include-inferred` is passed. Identical, older, and
  same-edition pairings are intake questions, not lifecycle changes.
- **A candidate's source URL is `evidence_type: candidate_location_only`.** Where
  a document was found is not evidence the incumbent was withdrawn.
- **`propose` refuses an unnamed reviewer.** The bot does not sign decisions.

## Next
1. Run `baseline --deep` against the live library manifest. Every signal so far
   was exercised on fixtures; the real corpus is 14,431 documents and will expose
   title patterns the token rules do not cover.
2. Re-run the ten hand-found supersessions from the Archivist's 2026-09-01 session
   as a regression set. Six are not yet fixtures.
3. Decide whether `edition_undetermined` volume on the real corpus justifies a
   `--report-undetermined` filter; on fixtures it is rare.
4. Wire the FSO handoff feed into `fso-guidance-watch` as a read step. That repo
   must never be written to from here.

## Open Questions
Should `baseline --deep` cache per-document hashes between runs? On 14,431
documents a full re-hash per comparison run may be too slow to use casually, and a
cache introduces a staleness failure mode that has to fail closed.

## Log
2026-09-06T00:00:00Z Claude — Created the project. Analysed both sibling repos,
identified that `fso-guidance-watch` already owns obligation-level comparison and
scoped this project to corpus/edition level to avoid a second supersession
register. Built identity signals, comparison engine, section diff, and proposal
emitter; 30 tests pass.
