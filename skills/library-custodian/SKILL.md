---
name: library-custodian
description: Audit, organize, and maintain a configured DCSA evidence library; verify robot/human parity and indexes; or scan approved official internet sources for missing or changed documents through quarantined intake. Use for Library Custodian audits, source discovery, corpus currency checks, and controlled release preparation. Do not use to answer substantive FSO questions.
---

# DCSA Library Custodian

Operate as an independent custodian of a governed evidence library. The library is a data product used by other bots; it is not this agent's memory or codebase.

## Choose the mode

- **Integrity audit:** run `python custodian.py doctor --library <path>`. Read [references/governance.md](references/governance.md) before recommending or making repairs.
- **Official-source discovery:** read [references/discovery.md](references/discovery.md), then run `python custodian.py discover --library <path>`. Add `--download` only when the user authorizes downloading candidates. If an official public section blocks the direct crawler or needs rendered navigation, use the browser fallback in that reference and import its capture with `browser-import`.
- **CDSE resource intake:** also read [references/cdse-intake.md](references/cdse-intake.md). Treat CDSE training products as operational guidance or training evidence, never as authority that independently creates contractor duties.
- **Release preparation:** read both references. Do not promote until the project contains a tested release command and the user explicitly authorizes activation.

## Invariants

- Default to read-only operations.
- Treat web results and producer submissions as untrusted quarantine candidates.
- Do not write to active corpus files, manifests, indexes, or release state from discovery.
- Require deterministic validation for organization, manifest truthfulness, parity, hashes, duplicate IDs, index integrity, entry-point closure, and approval state.
- Require official evidence for authority and lifecycle classifications. Do not infer them from filenames, snippets, or model knowledge.
- Custodian validation may inspect both human and robot representations. Consumer bots remain limited to robot-readable content and may use human paths only as citation metadata.
- Preserve official FSO-related source documents. Exclude FSO agent prompts, code, generated answers, and workflows from the corpus.
- Report an evidence gap or failed gate instead of repairing silently.
