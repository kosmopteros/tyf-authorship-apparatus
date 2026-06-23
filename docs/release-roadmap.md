# Release Roadmap

## 0.3.0 hardening

- Keep tightening the Gate: source-line partial acceptance, exact accepted patch application, enforced work-status transitions, and per-unit write locks are implemented; richer visual review and stale-lock recovery remain next.
- Keep converging sealed Gate records and the canonical `.tyf/events.jsonl` stream so record seals, write logs, and event history become one inspectable lineage rather than parallel truths.
- Promote acceptance evidence conventions into templates for Codex, Claude Cowork, and Gemini.
- Add optional per-language notice detectors on top of the explicit writing-language metadata and UTF-8 text path now stored and tested per work.
- Keep release metadata aligned across Python, Claude, Codex, Cursor, Gemini, and packaged plugin surfaces.

## 0.4.0 amanuensis entry

- Shipped the author-facing start/resume/import/adopt slice: titleless start, source/interview first-session packets, contained arrivals under `sources/imports/`, workspace-owned source fragments, direct author-edit adoption, and resume continuity.
- Shipped the first writing-runway slice on top of that amanuensis entry: the public start command preserves an optional cold-start scaffold, opens `.review/writing-runway.md`, creates `drafts/candidate-draft.md`, and treats title/structure/audit readiness as non-blocking for drafting.
- Shipped 0.5.0 Single Book Folder on top of the writing runway: beta launch workspaces treat the book folder as the single work, with root `work.yaml`, `outline/`, `drafts/`, `manuscript/`, `style-sheet.md`, and `.review/`.
- Keep improving the complete source-to-manuscript vertical slice: claim/example provenance, proposal generation from preserved evidence, author decision, audit, and write record.
- Promote the current canonical event journal from action history toward the authority for derived SQLite projections.
- Windows PowerShell install now has a local smoke test; add release-archive install validation for macOS and Linux next.

## Later workbench surface

- Revisit the author-facing ceremonial vocabulary as an interface layer backed by the plain runtime ontology.
- Add richer source ingestion for PDFs, transcripts, and citation indexes.
- Add richer lock-aware collaborative workflows for multi-agent and scheduled writing sessions, including stale-lock review and recovery guidance.
