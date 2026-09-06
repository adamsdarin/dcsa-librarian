# Interfaces and boundaries

Four projects share one problem domain. This file states which one owns what, so
that no two of them write the same fact.

| Project | Owns | Does not |
|---|---|---|
| `dcsa-librarian` | Official-source discovery, quarantine, intake validation, parity | Say that a new file is a newer edition of a library document |
| `dcsa-archivist` | Corpus organization, lifecycle metadata, indexes, approval-gated releases | Work out *which* document superseded another |
| **`dcsa-comparison-bot`** | Edition pairing and text diff between a candidate and the library | Decide lifecycle, acquire documents, or analyse obligations |
| `fso-guidance-watch` | FSO findings, supersession register, variance report | Write into the governed library |

## Inbound

**From the Librarian.** `compare --candidates-jsonl <path>` reads a discovery or
browser-import `candidates.jsonl` directly. The fields used are `inferred_filename`,
`url`, `anchor_text`, `sha256`, `downloaded_path`, and `status`. Nothing is written
back; quarantine remains the Librarian's.

**From the Archivist.** `baseline --manifest <path>` reads a library manifest or an
Archivist enriched manifest (`ENRICHED_DOCUMENT`). It carries through `collection_id`,
`current_status`, `authority_role`, `answer_eligibility`, `effective_date`,
`duplicate_of`, and `robot_content_sha256` when present, and derives identity signals
from the title. `--deep` additionally reads robot text for content hashes and header
fields. It reads; it never writes into the library or `.custodian/`.

## Outbound

**To the Archivist.** `propose` writes `state/proposals/proposal-<run>.json`. Its
`archivist_metadata_decisions` block conforms to `dcsa-library/metadata-decisions/1.0`
and can be reviewed and merged into `decisions/metadata_decisions.json` by a human.
It is never merged automatically. Every decision carries
`requires_official_lifecycle_evidence: true`, `proposed_by`, `proposal_basis`, and
`proposal_finding_id`, so the provenance of a merged decision stays visible.

**To the FSO guidance catalog.** The same run writes
`state/proposals/proposal-<run>-fso-handoff.json`: one row per finding, giving the
incumbent, the candidate, the relationship, and the basis. It is an input feed, not a
findings file. `fso-guidance-watch` owns the findings and supersession register and
constructs its own entries under its own rules; this project proposes nothing to it.

## Why this project does not extract text

Extraction from binary formats is the Librarian's and Archivist's path, where the
source bytes, canonical URL, redirect chain, retrieval time, MIME type, and SHA-256
are preserved first. Re-implementing extraction here would create a second, weaker
provenance chain. Where a candidate has no robot text, the comparison is honest about
what it could not do: `content_comparison: unavailable_no_candidate_text`, repeated
into every proposal that depends on it.

## Why this project does not write the guidance register

`fso-guidance-watch` already answers "what changed for an FSO", with a narrow-construction
method, verbatim quote verification, and `EXPLICIT` versus `INFERRED` supersession
status. Reproducing that here would create two registers of supersession truth and no
way to tell which was right. This project supplies the corpus-level input that register
was previously assembling by hand.
