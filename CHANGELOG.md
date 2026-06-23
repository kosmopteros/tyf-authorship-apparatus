# Changelog

## 0.5.0

Release label: "Single Book Folder".

- Reshaped the beta launch workspace so one folder equals one work: `tyf init` now creates root-level `work.yaml`, `style-sheet.md`, `outline/`, `drafts/`, `manuscript/`, and `.review/` instead of making first-time authors manage `works/<id>`.
- Updated writing runway so `tyf start [path]` records supplied title/language metadata, creates or reuses `sources/interviews/work-first-session.md`, opens `.review/writing-runway.md`, and creates `drafts/candidate-draft.md` at the book-folder root, including cold-start folder/chat/zip arrivals.
- Preserved binary, unreadable, and oversized arrivals with explicit `Extraction needed` guidance instead of minting source fragments or implying the full file was read.
- Removed the accidental today-named public command rather than keeping a compatibility alias; `tyf start [path]` is the single public beta front door.
- Added inspectable Markdown audit notes beside audit JSON records, active-work status output in `tyf status`, and manifest-version drift detection in `tyf check`; aligned the nested Claude plugin manifest with the active release version.
- Updated `tyf.portable.json` to `format_version: "0.5.0"` with `single_work: true` and root-level canonical text state.
- Aligned public onboarding, generated context files, Codex/Claude/Gemini repo contexts, and workspace skills around the single-work beta surface.
- Expanded the helper smoke suite to 173 tests, including exported release-tree check/install smoke coverage, release manifest context-path validation, hidden portability-doc drift checks, a reproducible first-sitting rehearsal from a public example scaffold, language-neutral structure records for non-English source, answered-prompt resume handling, source-grounded `tyf attend` attention packets with transparent local retrieval, external-feedback triage, continuing-work session packets, resume return-context recovery, doctor repair-boundary coverage, diagnostic-isolation packets, private-context-free author/root/runtime surfaces, machine-checked pressure-eval honesty, and a fresh exported Codex install opening a separate book workspace from an arrival scaffold; development acceptance coverage is now 136 scenarios with 136/136 direct RED proof.

## 0.4.1

Release label: "writing runway".

- Added `tyf start [path]`, the public writing-session command for authors who need to start today rather than operate the apparatus.
- writing runway creates or reuses a titleless active work, writes `.review/writing-runway.md`, creates `drafts/candidate-draft.md`, and confirms no manuscript text was written.
- `tyf start <path>` preserves a cold-start scaffold, chat, folder, old workspace, or zip through the existing import/orientation lane before opening the writing runway.
- Re-centered public docs and Cowork prompts around truthful drafting today: title, final structure, and audit readiness are non-blocking for candidate prose.
- Added a proper Codex book-repo skill surface: Codex installs target `$CODEX_HOME/skills` or `~/.codex/skills`, `using-tyf` has Codex UI metadata, and root/generated `AGENTS.md` contexts route new-book work through `tyf start`.
- Expanded the helper smoke suite to 100 tests and hidden development acceptance coverage to 62 scenarios.

## 0.4.0

Release label: "Amanuensis entry".

- Added titleless cold start: `tyf start` can create an `untitled-...` work, record `title_status: "unknown"`, and keep first-session prompts non-blocking.
- Moved first-session evidence out of `drafts/` into `sources/interviews/<work>-first-session.md`; `drafts/` is reserved for candidate prose.
- Added `tyf import <path>` for existing material, preserving raw arrivals under `sources/imports/` and writing orientation packets without manuscript writes.
- Added containment-first zip/folder import guidance: bundles are listed and analyzed before anything is unpacked or merged into live TYF workspace surfaces.
- Added text/chat import source fragments and made source fragments workspace-owned, with origin work recorded but cross-work reuse allowed through `--source-ref`.
- Added `tyf resume [work]` to show active work, title/language/status, first-session evidence, live return context, pending proposals, decisions, open prompts, and next useful move.
- Added `tyf adopt <work> <unit> --evidence` to preserve direct author manuscript edits under `.review/author-revisions/` and record the edited unit as the new base.
- Expanded the helper smoke suite to 96 tests.

## 0.3.0

Release label: "Gate hardening".

- Replaced naked manuscript confirmation with a Gate chain: `tyf propose`, `tyf audit --record`, `tyf accept --evidence`, and `tyf write --decision`.
- Added sealed Gate review records in `.review/record-seals.jsonl` so writes and doctor detect tampered proposal, audit, or decision JSON.
- Added per-unit manuscript write locks under `.review/locks/`, with write refusal and doctor visibility for outstanding locks.
- Added line-range partial acceptance with `tyf accept --lines`, stored accepted scope, and write-time application of only the accepted source lines.
- Added exact accepted patch support with `tyf accept --patch`, patch path/hash/unit storage in author decisions, write-time patch application, and doctor/write refusal for missing or changed accepted patches.
- Added source-fragment provenance: `tyf capture --kind source` mints stable fragments in `sources/fragments/`, `tyf propose --source-ref` binds them into the Gate, and audit, decision, write-log, and doctor integrity checks carry them forward.
- Added `.tyf/events.jsonl` as the canonical hash-chained apparatus event journal, with SQLite kept as a derived event mirror, `tyf doctor` checking journal integrity, and mutating commands refusing to recreate missing history.
- Added enforced work-status transitions through the Gate, with proposal/audit/accept/write updating `work.yaml`, accept/write refusing the wrong state, and acceptance requiring a passing audit for the same proposal.
- Added explicit writing-language metadata for `new-work`, `start`, and `begin`, surfaced in first-session packets and style sheets.
- Added source hash, manuscript base hash, passing-audit, acceptance-evidence, symlink-boundary, and atomic-write checks to controlled manuscript writes.
- Scoped `tyf snapshot` to the TYF workspace path and kept derived `.tyf/ledger.db` out of commits by default.
- Hardened notice identity and recurrence: identical gaps in different locations remain distinct, resolved notices reopen when they return, and `tyf notice --peek` does not create a ledger database.
- Added non-Latin title support through stable generated work ids.
- Generated workspace context contracts for Codex, Claude, and Gemini.
- Expanded the helper smoke suite to 86 tests and hidden development acceptance coverage to 37 scenarios.

## 0.2.1

- Added paste-ready public onboarding for non-technical authors.
- Added the `tyf start` first-session path for new books.
- Added Codex plugin metadata and validation.
- Added explicit reflex and snapshot guidance for visible recovery points.
