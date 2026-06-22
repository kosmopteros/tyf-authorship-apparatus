# Release Roadmap

## 0.3.0 hardening

- Keep tightening the Gate: source-line partial acceptance, exact accepted patch application, and per-unit write locks are implemented; richer visual review and stale-lock recovery remain next.
- Keep converging sealed Gate records and the canonical `.tyf/events.jsonl` stream so record seals, write logs, and event history become one inspectable lineage rather than parallel truths.
- Promote acceptance evidence conventions into templates for Codex, Claude Cowork, and Gemini.
- Add optional per-language notice detectors on top of the explicit writing-language metadata and UTF-8 text path now stored and tested per work.
- Keep release metadata aligned across Python, Claude, Codex, Cursor, Gemini, and packaged plugin surfaces.

## v0.4 provenance engine

- Implement one complete source-to-manuscript vertical slice: source fragment identity, interview evidence, claim provenance, proposal generation, author decision, audit, and write record.
- Promote the current canonical event journal from action history toward the authority for derived SQLite projections.
- Add install validation for macOS, Linux, and Windows.

## Later workbench surface

- Revisit the author-facing ceremonial vocabulary as an interface layer backed by the plain runtime ontology.
- Add richer source ingestion for PDFs, transcripts, and citation indexes.
- Add richer lock-aware collaborative workflows for multi-agent and scheduled writing sessions, including stale-lock review and recovery guidance.
