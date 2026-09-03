# Governance and release gates

## Corpus boundary

The active DCSA Library may contain approved source artifacts, robot representations, metadata, chunks, indexes, schemas, and release records. Bot prompts, generated guidance, workflow code, audit scratch files, and web candidates stay outside the active corpus.

## Mandatory gates

Before any future promotion command activates a release, require:

1. Every entry-point target exists.
2. Every active document ID is unique.
3. Manifest existence, byte counts, and hashes match disk.
4. Every active document has verified local human/robot parity or an explicitly approved remote-source exception.
5. Robot text passes extraction-quality thresholds and maps to exact citation locators.
6. SQLite integrity checks pass and active index rows match approved manifests.
7. Authority, lifecycle, applicability, and provenance have evidence, not guesses.
8. Focused DOHA retrieval tests pass without unrestricted broad-index fallback.
9. Golden retrieval tests meet the configured thresholds.
10. A release bill of materials and rollback target exist.

Never lower a gate merely to approve the current candidate. Repairs should build a new candidate release and switch one release pointer atomically after review.

## Parity exception

A source intentionally represented only by a canonical official remote URL must not retain a fake local human path or `source_exists: true`. It requires a specific remote-source mode, source hash, retrieval time, canonical URL, and archived provenance receipt.

