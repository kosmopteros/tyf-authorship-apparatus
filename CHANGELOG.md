# Changelog

## 0.3.0

Release label: "Gate hardening".

- Replaced naked manuscript confirmation with a Gate chain: `tyf propose`, `tyf audit --record`, `tyf accept --evidence`, and `tyf write --decision`.
- Added sealed Gate review records in `.review/record-seals.jsonl` so writes and doctor detect tampered proposal, audit, or decision JSON.
- Added per-unit manuscript write locks under `.review/locks/`, with write refusal and doctor visibility for outstanding locks.
- Added line-range partial acceptance with `tyf accept --lines`, stored accepted scope, and write-time application of only the accepted source lines.
- Added source-fragment provenance: `tyf capture --kind source` mints stable fragments in `sources/fragments/`, `tyf propose --source-ref` binds them into the Gate, and audit, decision, write-log, and doctor integrity checks carry them forward.
- Added explicit writing-language metadata for `new-work`, `start`, and `begin`, surfaced in first-session packets and style sheets.
- Added source hash, manuscript base hash, passing-audit, acceptance-evidence, symlink-boundary, and atomic-write checks to controlled manuscript writes.
- Scoped `tyf snapshot` to the TYF workspace path and kept derived `.tyf/ledger.db` out of commits by default.
- Hardened notice identity and recurrence: identical gaps in different locations remain distinct, resolved notices reopen when they return, and `tyf notice --peek` does not create a ledger database.
- Added non-Latin title support through stable generated work ids.
- Generated workspace context contracts for Codex, Claude, and Gemini.
- Expanded the helper smoke suite to 70 tests and SOLO Be coverage to 22 scenarios.

## 0.2.1

- Added paste-ready public onboarding for non-technical authors.
- Added the `tyf start` first-session path for new books.
- Added Codex plugin metadata and validation.
- Added explicit reflex and snapshot guidance for visible recovery points.
