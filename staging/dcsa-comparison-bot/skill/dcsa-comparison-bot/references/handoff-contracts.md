# Handoff contracts

## What becomes a proposed decision

Only `newer_edition_candidate`, and by default only when its basis is `deterministic`.
`--include-inferred` widens this, and the resulting decisions stay labelled
`proposal_basis: inferred` for the reviewer.

Everything else is skipped with a stated reason:

| Relationship | Why it carries no lifecycle consequence |
|---|---|
| `identical` / `identical_after_normalization` | the candidate duplicates content already held; an intake question for the Librarian |
| `older_edition_candidate` | the candidate is the older edition; the incumbent is unchanged |
| `same_edition_candidate` | same markers; check for a silent content revision, but nothing has been superseded |
| `edition_undetermined` | ordering was not established; a human must read both |
| `title_similar` | the pairing itself is unconfirmed |
| `no_match` | there is no incumbent to decide about |

## What blocks a proposal

- **No `https` candidate source URL.** The Archivist's `METADATA_DECISIONS` schema
  requires at least one evidence URL. Rather than fabricate one, the decision is moved
  to `blocked` with its draft body attached, so a reviewer can supply the evidence.
- **No `robot_text_path` on the incumbent.** There is nothing for the Archivist to key
  the decision to.
- **No named reviewer.** `propose` raises rather than signing as the bot.

## What a proposal is not

Each proposed decision carries `requires_official_lifecycle_evidence: true` and a note
that states, in words, that it was derived from identity signals and not from evidence
of withdrawal. The candidate's URL is attached as `evidence_type: candidate_location_only`.

This matters because the artifact is merged into a register used for compliance
decisions. If a reviewer skims, the artifact must still tell them what it does not know.
The Archivist's rule — official evidence for lifecycle, never inference from filename
similarity — is not weakened by arriving in machine-readable form.

## Applying a proposal

1. Read `state/proposals/proposal-<run>.json`. Work the `blocked` and `skipped` lists,
   not only the accepted decisions.
2. For each proposed decision, obtain official evidence that the library copy was
   withdrawn, replaced, or reissued. Add it to the decision's `evidence` array as
   `evidence_type: official_lifecycle_evidence`.
3. Merge the reviewed decisions into the Archivist's `decisions/metadata_decisions.json`.
   Keep `proposed_by`, `proposal_basis`, and `proposal_finding_id` so the provenance of
   the decision remains visible after the merge.
4. Run the Archivist's own `build-candidate`, `validate`, and `evaluate`. Approval and
   publication remain its gates, unchanged.

## The FSO guidance catalog feed

`proposal-<run>-fso-handoff.json` carries one row per finding: incumbent, candidate,
relationship, basis, edition ordering, and whether content was compared. It is an input
to that project's own monthly cycle. `fso-guidance-watch` owns the findings and
supersession register, constructs entries under its own narrow-construction method, and
verifies quotes against source documents. This project writes nothing into it, and must
not: two registers of supersession truth would leave no way to tell which was right.
