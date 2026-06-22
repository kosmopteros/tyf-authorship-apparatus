# Release Roadmap

## 0.3.0 hardening

- Keep tightening the Gate: source-line partial acceptance and per-unit write locks are implemented, while semantic hunk-level decisions remain next.
- Promote sealed Gate records toward a canonical event stream so the tamper-evident seal log and SQLite event index converge rather than becoming parallel truths.
- Promote acceptance evidence conventions into templates for Codex, Claude Cowork, and Gemini.
- Add optional per-language notice detectors on top of the explicit writing-language metadata now stored per work.
- Keep release metadata aligned across Python, Claude, Codex, Cursor, Gemini, and packaged plugin surfaces.

## v0.4 provenance engine

- Implement one complete source-to-manuscript vertical slice: source fragment identity, interview evidence, claim provenance, proposal generation, author decision, audit, and write record.
- Separate canonical event records from derived SQLite projections.
- Add install validation for macOS, Linux, and Windows.

## Later workbench surface

- Revisit the author-facing ceremonial vocabulary as an interface layer backed by the plain runtime ontology.
- Add richer source ingestion for PDFs, transcripts, and citation indexes.
- Add richer lock-aware collaborative workflows for multi-agent and scheduled writing sessions, including stale-lock review and recovery guidance.
