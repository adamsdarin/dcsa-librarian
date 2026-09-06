# DCSA Comparison Bot

This is the model-agnostic comparison plane for a governed DCSA evidence library. The DCSA Comparison Bot answers one question: **when a new document is released, which document already in the library does it change, and what changed?** It is not part of the library corpus, it does not acquire documents, it does not maintain the corpus, and it does not answer FSO questions.

It sits between the two existing planes:

- The **DCSA Librarian** discovers that a URL is new. It cannot say that the file behind that URL is a newer edition of something the library already holds.
- The **DCSA Archivist** records that a document is `superseded`. It cannot work out which document superseded it.

That gap was being closed by hand. This project closes it deterministically and leaves the decision where it belongs.

## Commands

```powershell
python comparison.py doctor    --manifest "C:\path\to\manifest.jsonl"
python comparison.py baseline  --manifest "C:\path\to\manifest.jsonl" --library-root "C:\path\to\DCSA Library" --deep
python comparison.py compare   --baseline state\baselines\baseline-<run>.json --candidates-jsonl "C:\path\to\candidates.jsonl"
python comparison.py diff      --left "<library robot text>" --right "<candidate robot text>"
python comparison.py propose   --report state\comparisons\<run>\comparison-report.json --reviewer "Full Name"
```

Every command is read-only with respect to the DCSA Library, the Librarian's quarantine, the Archivist's release state, and the FSO guidance catalog. All output is written under this project's ignored `state/` directory.

## What a finding is

A **finding** pairs one candidate document with one library document and records the route that produced the pair, the tokens behind it, and one of two bases:

- `deterministic` — reproducible from observable evidence: equal content hashes, or a shared official document number plus an ordered edition token (`v1.5` → `v1.5.1`, `Rev 2` → `r3`, `2022-04` → `May 2024`).
- `inferred` — a similarity judgement, from a matching series key or title overlap.

There is no confidence score. A score invites a threshold, a threshold invites automation, and automating this step is precisely what the Librarian and Archivist contracts forbid. The label is the honest unit: either the machine can show its work, or it says it is guessing.

Relationships are `identical`, `identical_after_normalization`, `newer_edition_candidate`, `older_edition_candidate`, `same_edition_candidate`, `edition_undetermined`, `title_similar`, and `no_match`. Every one carries `disposition: proposed_for_human_review`.

## What it refuses to do

- **It will not pair two documents that carry different official numbers.** ISL 2024-01 and ISL 2021-02 are both in force; a title-similarity route between them would manufacture a supersession that does not exist. When a candidate carries an official document number, similarity routes are suppressed and the suppression is recorded in the report.
- **It will not compare content it cannot read.** This project extracts nothing from PDFs. Hashing a PDF's bytes against a robot-text hash is a false equivalence, so a candidate without extracted text is reported as `content_comparison: unavailable_no_candidate_text` and the shortfall is repeated in every proposal it feeds.
- **It will not sign a decision.** `propose` requires a named human reviewer and refuses an empty one.
- **It will not present a location as a lifecycle fact.** A candidate's source URL is emitted as `evidence_type: candidate_location_only`. Where the candidate was found is not evidence that the library copy was withdrawn.
- **It will not write into another project.** Proposals land under `state/proposals/`. Applying them is the Archivist's approval-gated job.

## Safety boundary

- Default and only mode is read-only. There is no publish path and no network access.
- A `newer_edition_candidate` is the only relationship that becomes a proposed decision, and only when `deterministic`. Inferred pairings require `--include-inferred` and stay labelled as inferred all the way through.
- Every proposed decision carries `requires_official_lifecycle_evidence: true` and a note stating in plain words that a version token is not evidence of withdrawal.
- A section diff reports what text changed. What *obligation* changed is a human judgement that belongs in the FSO guidance catalog, not here.

## Interfaces

See [INTERFACES.md](INTERFACES.md) for the exact contract with the Librarian, the Archivist, and the FSO guidance catalog.
