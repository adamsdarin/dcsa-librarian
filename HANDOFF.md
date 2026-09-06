# HANDOFF — dcsa-library-custodian

Last updated: 2026-09-06T22:45:00Z by Claude

## Current State
Integrity and discovery plane for the DCSA Library. Operates on a library passed via `--library`; deliberately not part of the corpus. Commit `f44bad1`.

Ran `doctor` against both library copies on 2026-08-31. That is what established `Documents\DCSA Library` as canonical (0 missing human files) and `src\_docs_backup\DCSA Library` as a broken fork (10,973 missing).

Its README states release promotion is intentionally not implemented in v0.1. **`dcsa-archivist` implements it** — see that project's `PROVENANCE.md`. The two are different implementations, not copies.

**A third project now exists: the DCSA Comparison Bot.** It consumes this project's
`candidates.jsonl` plus a library manifest and reports which existing document a new
release changes. It was built because this project's change detection stops at the URL
layer — `known` vs `missing_from_manifest` — and the Archivist can record `superseded`
without being able to work out what superseded it. The Archivist's 2026-09-01 session
found ten supersessions by hand and routed them nowhere.

It is **staged on this branch** at `staging/dcsa-comparison-bot/`, not native to this
repo, because the session that built it could not create a GitHub repository
(`403 Resource not accessible by integration`). See `staging/STAGING-NOTE.md` for the
extraction steps. Nothing in the Librarian imports from it.

## Next
1. Create `adamsdarin/dcsa-comparison-bot` and move `staging/` out of this repo.
2. Decide: merge with the Archivist, keep both with distinct responsibilities, or retire one.
3. Push to a private remote.
4. Absorb the `OPERATIONS/` scripts still living inside the corpus (reserved — waiting on the user).

## Open Questions
Merge with v2 or keep separate? This one has discovery and browser-import; v2 has enrichment and releases.

## Log
2026-08-31T16:47:01Z Claude — Committed the first baseline — the repo had been initialised with zero commits.
2026-09-06T22:45:00Z Claude — Analysed this project against `dcsa-archivist` to scope a new comparison agent. Found that `fso-guidance-watch` already owns obligation-level comparison, so scoped the new project to corpus/edition level to avoid a second supersession register. Staged the result under `staging/dcsa-comparison-bot/` because repository creation was refused by the GitHub integration; the staging note carries the extraction steps.
