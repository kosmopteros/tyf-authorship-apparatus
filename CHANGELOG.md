# Changelog

## 0.6.4

Release label: "Workbench Style Surface".

- Made the Workbench author surface show `design/book-style.yaml` alongside the running style sheet.
- Added governed Workbench evidence that the generated surface exposes book-style text and image inventory records/files.
- Expanded development acceptance coverage to 179 scenarios with 179/179 direct RED proof.
- Kept package, plugin, Gemini, and nested Cowork manifest versions aligned at 0.6.4.

## 0.6.3

Release label: "Release Acceptance Review".

- Added an evidence-led release acceptance review for the current local-first single-book beta candidate.
- Updated public release documentation to name local release evidence accurately without claiming unavailable CI evidence.
- Kept package, plugin, Gemini, and nested Cowork manifest versions aligned at 0.6.3.

## 0.6.2

Release label: "Codex Workbench MCP".

- Added `tyf workbench --codex-mcp-config` as the one-command Codex MCP setup path for a TYF book workspace.
- The helper writes the Codex-recognized user config at `$CODEX_HOME/config.toml` or `~/.codex/config.toml`, not an invisible project-local config.
- The Workbench MCP server is workspace-bound and exposes no tools when Codex is launched outside the bound book folder.
- Expanded the helper smoke suite to 202 tests and development acceptance coverage to 178 scenarios with 178/178 direct RED proof.

## 0.6.1

Release label: "Codex Install Path".

- Added `codex-plugin` install targets to the bash and PowerShell installers so Codex users can refresh the version-aligned personal plugin cache under `$CODEX_HOME/plugins/cache/personal/tyf/<version>` or `~/.codex/plugins/cache/personal/tyf/<version>`.
- The `codex-plugin` installer path now removes older TYF personal plugin cache versions, leaving Codex with one current TYF plugin cache path after update.
- Aligned package, plugin, Gemini, and nested Cowork manifest versions at 0.6.1.
- Expanded the helper smoke suite to 201 tests and development acceptance coverage to 177 scenarios with 177/177 direct RED proof.

## 0.6.0

Release label: "Workbench Path".

- Made `tyf workbench` the single author-facing Workbench command, removed the public `tyf surface` command and the separate `tyf-workbench` console script, and moved generated Workbench artifacts to `.review/workbench/`.
- Kept the Workbench's draft-only authority intact: local browser saves remain compare-and-swap guarded under `drafts/`, while `manuscript/` stays read-only until the proposal, audit, author review, author decision, and `tyf write --decision` Gate path.
- Refreshed Codex skills, plugin metadata, author contexts, Cowork instructions, docs, tests, and development evidence around the one-path Workbench contract.

## 0.5.0

Release label: "Single Book Folder".

- Reshaped the beta launch workspace so one folder equals one work: `tyf init` now creates root-level `work.yaml`, `style-sheet.md`, `outline/`, `drafts/`, `manuscript/`, and `.review/` instead of making first-time authors manage `works/<id>`.
- Updated writing runway so `tyf start [path]` records supplied title/language metadata, creates or reuses `sources/interviews/work-first-session.md`, opens `.review/writing-runway.md`, and creates `drafts/candidate-draft.md` at the book-folder root, including cold-start folder/chat/zip arrivals.
- Preserved binary, unreadable, and oversized arrivals with explicit `Extraction needed` guidance instead of minting source fragments or implying the full file was read.
- Removed the accidental today-named public command rather than keeping a compatibility alias; `tyf start [path]` is the single public beta front door.
- Added inspectable Markdown audit notes beside audit JSON records, active-work status output in `tyf status`, and manifest-version drift detection in `tyf check`; aligned the nested Claude plugin manifest with the active release version.
- Updated `tyf.portable.json` to `format_version: "0.5.0"` with `single_work: true` and root-level canonical text state.
- Aligned public onboarding, generated context files, Codex/Claude/Gemini repo contexts, and workspace skills around the single-work beta surface.
- Added the first Draft Review Workbench slice: `tyf workbench` opens the v0.6 local browser desk with multi-unit draft/manuscript review, book-style and image-asset scaffolding, author notes, footnote candidates, Gate/context packets, and conflict-protected draft saves while keeping `manuscript/` read-only.
- Added the local-first beta stop rule: faithfulness includes helping the author finish, and possible future improvement is not itself a blocking defect.
- Expanded the helper smoke suite to 199 tests, including exported release-tree check/install smoke coverage, release manifest context-path validation, hidden portability-doc drift checks, a reproducible first-sitting rehearsal from a public example scaffold, existing-work recovery packets for formatted and illustrated arrivals, language-neutral structure records for non-English source, answered-prompt resume handling, source-grounded `tyf attend` attention packets with transparent local retrieval, external-feedback triage, continuing-work session packets, resume return-context recovery, workspace-bounded read-only session-start and message-sent hook contexts, Codex and Claude hook manifests with TYF-identifying status messages, doctor repair-boundary coverage, diagnostic-isolation packets, typographer-redactor treatment packets for existing body prose, Draft Review Workbench generation with draft-save conflict protection, Workbench bridge containment, rebuildable book-graph projections, concept/continuity/polish review wrapper coverage, private-context-free author/root/runtime surfaces, machine-checked pressure-eval honesty, and a fresh exported Codex install opening a separate book workspace from an arrival scaffold; development acceptance coverage is now 175 scenarios with 175/175 direct RED proof.

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
