# Staged, not native to this repository

`staging/dcsa-comparison-bot/` is a complete, self-contained third project. It is
**not** part of the DCSA Librarian and must not be treated as one: it has its own
`AGENTS.md` operating contract, its own package, and its own tests.

It is staged here only because the session that built it could not create a new
GitHub repository (`403 Resource not accessible by integration`), and a container
is ephemeral. Pushing it to a branch was the only way to preserve it.

## To move it to its own repository

```bash
# create the empty private repo adamsdarin/dcsa-comparison-bot first, then:
git clone <this repo> /tmp/extract && cd /tmp/extract
git checkout claude/dcsa-comparison-bot-k0ttop
cd staging/dcsa-comparison-bot
git init && git add -A && git commit -m "Add DCSA Comparison Bot"
git remote add origin https://github.com/adamsdarin/dcsa-comparison-bot.git
git push -u origin main
```

Then delete `staging/` from this branch. Nothing in the Librarian imports from it.

## Why it exists

The Librarian detects that a URL is new. It cannot say that the file behind that
URL is a newer edition of a document the library already holds. The Archivist can
record `superseded` but cannot work out what superseded it. That step was being
done by hand — see the ten supersession findings in the Archivist's `HANDOFF.md`
for 2026-09-01, recorded as prose in `metadata_decisions.json` note fields and
routed nowhere.

The Comparison Bot reads a Librarian `candidates.jsonl` and a library manifest,
pairs candidates against incumbents using official document numbers and edition
tokens, diffs their robot text, and emits proposals for human review. It writes
nothing into this project, the Archivist, or the FSO guidance catalog.
