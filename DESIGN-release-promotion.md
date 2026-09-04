# Design — atomic release promotion (quarantine → library)

Status: **proposed, not implemented.** `README.md` states that "release
promotion is intentionally not implemented in version 0.1. A broken library
must first be recovered and a reviewed atomic-release design implemented."
This is that design, offered for review before any code is written.

## The gap this closes

`discover` places verified downloads in `quarantine/<timestamp>/<source-id>/`
with SHA-256, byte count and content type. The Archivist's `build-candidate`
reads from `--library-root`. Neither reads the other. The Librarian's
`SKILL.md` says its job is to "deliver validated quarantine candidates to the
DCSA Archivist"; the delivery mechanism is what is missing.

The gap is narrower than it first appears. The Archivist already owns
chunking (`chunks.py`), retrieval indexes (`indexes.py`), authority and
lifecycle metadata (`authority.py`), and approval-gated release
(`release.py`). **Promotion does not need to build any of that.** It needs to
place a document into the library in the shape the Archivist already knows how
to consume, and then get out of the way.

## What "placed correctly" means

Learned from a document already done right — SEAD-3 under
`PERSONNEL_VETTING/SECURITY_EXECUTIVE_AGENT_DIRECTIVES_(SEAD)`:

1. **Human artifact.** The original bytes, unmodified, at a taxonomy path
   under `HUMAN_READABLE_DIRECTORY/<DOMAIN>/<COLLECTION>/`.
2. **Robot artifact.** Machine-readable text under
   `ROBOT_READABLE_DIRECTORY/TEXT/<same taxonomy>/`, carrying a provenance
   header that states how the text was produced.
3. **Section manifest** (`manifest.json`) beside the robot text, recording
   `source_file`, `source_sha256`, `generated_by`, `cut_method`, and per
   section `file` / `title` / `body_sha256` / `lines`.
4. **Entry-point registration** in `START_HERE_FOR_ROBOTS.json` — the
   `documents`, `catalog`, `relationships` and `portability_index` keys — plus
   whatever `LOCAL_INDEXES` the Archivist rebuilds.

Human/robot parity and entry-point closure are what `doctor` audits. A
document present in one tier and absent from the other is a library defect,
not a partial success.

## Text production, and the honesty rule it must inherit

Two cases, and the library already has a convention for the hard one:

- **Text-layer PDF** (e.g. PVMS Appendix C — 12 pages, ~31k characters
  extract cleanly): extract directly. Header states the extraction method.
- **Image-only PDF** (e.g. the PVMS Standards scan, `/Creator: Hewlett-Packard
  MFP`; and both SEAD-3 and SEAD-4 as officially posted): OCR, and reproduce
  the existing banner in intent —

  > TEXT BELOW WAS PRODUCED BY OCR ... The source PDF has NO embedded text
  > layer. OCR introduces transcription errors. Treat wording as INDICATIVE,
  > NOT VERBATIM. Verify any passage against the original before quoting it
  > in a compliance answer.

  **This banner is load-bearing and must survive every derivation.**
  `split_sead_text.py` already propagates it into section files ("OCR
  artifacts in the source are reproduced unchanged"). Chunks fed to retrieval
  must carry it too, or a RAG answer will quote OCR text as if it were the
  signed directive. See "Known downstream gap" below.

## Command surface

```
python custodian.py promote --scan <timestamp> [--candidate <filename>]
       --domain <DOMAIN> --collection <COLLECTION>
       --authority <tier> --lifecycle <status>
       [--dry-run] [--library "<path>"]
```

`--dry-run` is the default posture in review: print the full placement plan —
every path to be written, every index key to be touched — and exit without
writing.

## Atomicity and rollback

The library must never be observed half-updated.

1. **Stage** the complete change set in `state/promotions/<id>/` — human
   artifact, robot text, manifest, and the computed index deltas.
2. **Verify the staged set in isolation**: hashes match quarantine, parity
   holds, no path collides with an existing document, every index delta
   applies cleanly to the current index.
3. **Snapshot** the index files the change touches into
   `state/promotions/<id>/rollback/`.
4. **Apply** by writing new files first, then rewriting index files last —
   the index rewrite is the commit point, because a document invisible to the
   index is inert, while an index entry pointing at a missing file is
   corruption.
5. **Re-audit** with the Archivist's `audit`. Any failure restores the
   rollback snapshot and removes the staged artifacts.

Promotion is refused outright if `doctor` does not pass beforehand. Promotion
into a library that is already broken is how a small defect becomes
unattributable.

## Governance gates (from `skills/dcsa-librarian/references/governance.md`)

Refuse promotion unless: the candidate's SHA-256 matches its quarantine
record; provenance names a retrievable official source URL **or** an
explicitly recorded operator attestation; authority and lifecycle are stated
rather than inferred; and a human has confirmed the bill of materials. The
attestation path exists for documents such as PVMS Appendix C, distributed by
agency transmittal rather than public posting — it is recorded as
`operator_attested` with the attesting person and date, never silently
labelled as retrieved.

## Then hand to the Archivist

Promotion ends at placement. Retrieval is the Archivist's:

```
python custodian.py audit
python custodian.py build-candidate --release-id <id>
python custodian.py validate  --release-id <id>
python custodian.py evaluate  --release-id <id>
python custodian.py approve   --release-id <id>
python custodian.py publish   --release-id <id>
```

This is what puts the document "in the RAG" — chunking, intent-routed
indexing, and retrieval regression all belong to that pipeline and must not be
duplicated here.

## Test plan

Against a scratch copy of the library, never the live one:

- a text-layer PDF promotes, and its robot text round-trips to the source hash
- an image-only PDF promotes with the OCR banner present in every derived file
- a hash mismatch against the quarantine record refuses
- a path collision with an existing document refuses
- a mid-apply failure restores every touched index byte-for-byte
- `doctor` passes before and after; parity and entry-point closure hold
- `--dry-run` writes nothing

## Known downstream gap, worth fixing alongside

`assemble_package.py` and `verify_output.py` in the
adverse-information-assistant contain no mention of OCR. The library discloses
OCR provenance at every internal hop and instructs the reader to verify
passages against the original before quoting them in a compliance answer — and
that instruction does not survive into the assembled report a person signs and
hands to a security officer. Whatever this design does about banners in
chunks, that gap lives in the other project and needs its own fix.
