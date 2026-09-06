# Comparison method

## The two questions, kept apart

1. **Which library document does this candidate correspond to?** Answered by identity
   signals: official document numbers, edition tokens, and a normalized series key.
2. **What changed between them?** Answered by a section-level text diff, and only when
   robot text exists for both sides.

Question 1 can produce a pairing with no answer to question 2. That is reported, not
hidden: `content_comparison: unavailable_no_candidate_text`.

## Identity signals

**Document numbers** are normalized to `kind:number` — `nist-sp:800-61`, `dod:i-5205.16`,
`sead:3`, `cfr:32-117`, `isl:2024-01`, `ics:705`, `eo:13526`, `cnssi:7003`, `dfars:…`,
`far:…`. Text is scanned twice, raw and run-split, because mixed-case acronyms (`DoDI`)
read correctly raw while concatenated ones (`DoDI5205.16`) only read once split.

**Edition tokens** come in four kinds, in descending authority:

| Kind | Examples |
|---|---|
| `version` | `v1.5`, `v1.5.1`, `Version 2.2` |
| `revision` | `Rev 2`, `Revision 3`, `Change 1`, the NIST-style `800-61r3` |
| `edition_date` | `2022-04`, `May 2024`, `revisedMay2024`, `20220525`, `7-24-2026` |
| `year` | a bare `2015`, used only when nothing stronger is present |

Two documents are ordered only by tokens **of the same kind**. A version on one side
against a date on the other is not an ordering; it is reported as `edition_undetermined`.
Where both sides carry the same kind and the values are equal, the next kind down is
tried before giving up.

**Series key** is the title with edition tokens and publication artifacts (`final`,
`508`, `draft`, `signed`) removed. It exists so that `Cleared CUI Quick Reference Guide
Dec 2020` and `… October 2024` collapse to one key.

## Routes, and why one of them is suppressed

| Route | Used when | Basis of a resulting edition ordering |
|---|---|---|
| `document_number` | candidate and incumbent share a normalized number | `deterministic` |
| `series_key` | neither carries a number, and the keys match exactly (≥3 tokens) | `inferred` |
| `title_similarity` | neither carries a number, Jaccard ≥ threshold (≥4 tokens each) | `inferred` |

**When a candidate carries an official document number, the similarity routes are
suppressed entirely.** A numbered document is identified by its number. Pairing
`ISL 2024-01` with `ISL 2021-02` on title overlap would assert a supersession between
two issuances that are both in force — the failure this rule exists to prevent. The
suppression is recorded in `suppressed_routes` so a reviewer can see what was not
looked at.

## Basis, not confidence

`deterministic` means a reader can reproduce the conclusion from the artifact: equal
hashes, or a shared number plus an ordered token of one kind. `inferred` means a
similarity judgement was involved.

There is deliberately no numeric confidence. A score invites a threshold; a threshold
invites automation; and automating a lifecycle call is what the Librarian and Archivist
contracts forbid. A reviewer reading `inferred` knows to read both documents. A
reviewer reading `0.87` does not know anything they can act on.

## Reading a diff

Sections are split on headings (`§ 117.7`, `2.1 Scope`, `APPENDIX B`, all-caps lines),
falling back to form-feed pages, then to a single block. Sections are aligned by exact
normalized heading first, then by heading-token overlap ≥ 0.8. Library header fields
(`TIER`, `STATUS`, `EFFECTIVE`, `DOC TYPE`, `BASIS`) are pulled out of the section flow
and reported in `header_changes`, because a changed effective date is a signal in its
own right rather than diff noise.

`summary.substantively_identical` is true only when no section changed, none was added
or removed, and no header field moved.

A diff describes text. What a change *requires* is a judgement about obligation, and it
is made downstream by a human working in the FSO guidance catalog.
