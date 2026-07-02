# PR History Intent Reconstruction: 2026-06-27

Truth status: review-only evidence for SOLO forward reconciliation.

Scope: merged GitHub PRs and first-parent commits after local baseline `7c4be8d`.
Closed unmerged PRs #2 and #4 are treated as superseded evidence only, not accepted intent.

## High-confidence merged-PR requirements

### R1. Local-first single-book amanuensis beta

Source: PR #1, `codex/solo-tyf-improvements`, merged 2026-06-27T00:48:13Z.

TYF should be a local-first single-book amanuensis beta with a clear author entry, controlled Gate, Codex skill/plugin surface, automatic author reflex hooks, portability documentation, and release hygiene. It should preserve author sovereignty while making the author able to start and return to real book work.

### R2. Typographer-redactor is core for existing manuscript bodies

Source: PR #1.

TYF should include a `typographer-redactor` lane and `tyf treat` review-only treatment surface for substantial existing manuscript bodies. This is redactor craft, voice, typography, and language treatment, not merely punctuation cleanup or more philosophical interviewing.

### R3. Workbench target state is a local double-surface writing desk

Source: PR #1, `docs/WORKBENCH_TARGET_STATE.md`.

TYF should evolve toward a local double-surface Workbench: multi-unit draft/manuscript body, contextual amanuensis chat, selection-aware author notes, note-to-footnote flow, Codex/MCP awareness, safe concurrency, and a derived book graph. Manuscript writes remain behind the Gate.

### R4. First runnable Workbench slice supports actual writing, not only chat

Source: PR #3, `workbench-v06-local-double-surface`, merged 2026-06-27T03:50:13Z.

TYF should provide a runnable local Workbench with book-map sidebar, multi-unit draft discovery, read-only manuscript preview, editable draft surface with compare-and-swap saves, draft unit creation, author notes, footnote-candidate packets, Gate packets, active context packets, loopback server token protection, MCP tools, Codex hook recorder, Codex bridge scaffold, and no manuscript write API.

### R5. Workbench integration should expose TYF-named safe tools, not raw filesystem power

Source: PR #3.

The Workbench MCP bridge should expose TYF concepts such as active selection, unit context, author notes, graph search, footnote candidates, Gate packets, status, and conflicts. It should not expose raw arbitrary write-file tools or direct manuscript writing.

### R6. Live Workbench status should make the desk visibly alive

Source: PR #5, `workbench-next-slice-status-conflicts-approvals`, merged 2026-06-27T04:08:40Z.

TYF should show live Workbench status for Codex activity, draft state, stale-draft detection, and approval requests. The status model should be read-only, local, and loopback by default.

### R7. Workbench author language should be calm and action-oriented

Source: PR #6, `workbench-realtime-status-sse`, merged 2026-06-27T08:12:07Z.

TYF should make the browser surface calmer and clearer with labels such as Assistant status, Save safety, Needs your approval, Safe to save, Changed outside this window, Prepare for manuscript review, Share this moment, and Make footnote candidate. Product calm matters more than more machinery.

### R8. Realtime Workbench updates should be read-only and local-first

Source: PR #6.

TYF should provide a read-only realtime Workbench update path through server-sent events with polling fallback. The endpoint must not create a manuscript write route, and draft writes should continue using compare-and-swap helpers.

### R9. Book graph is a rebuildable projection, not a new source of truth

Source: PR #7, `workbench-graph-projection-ledger-audit`, merged 2026-06-27T08:59:12Z.

TYF should derive a provenance-first book graph from existing local truth files. Graph JSON and optional SQLite cache are rebuildable artifacts. Deleting them must not delete author knowledge.

### R10. JSONL files require explicit storage semantics

Source: PR #7.

TYF should distinguish hash-chain ledgers, mutable JSONL record stores, append logs, empty placeholders, and broken ledgers. A `.jsonl` extension alone is not a ledger.

### R11. Concept and continuity review should exist as derived review surfaces

Source: first-parent commits `e0429da`, `def2e95`, `c8d77f5`, `3fafefa`, `987bd24`, `66aa16b`, `da85c26`, `0bbd7f0`, `9835aac`.

TYF should provide derived concept, contradiction/rename, and continuity review surfaces for full-book work. These surfaces should help the author see coherence risks without becoming manuscript-writing authority.

### R12. Continuity decisions should be author-owned append-only review memory

Source: PR #8, `rc-polish-decisions-voice-typography`, merged 2026-06-27T11:25:09Z.

TYF should let the author record decisions on continuity findings with statuses such as accepted, intentional, ignored, fixed, needs-rewrite, and belongs-elsewhere. These records are append-only review memory.

### R13. Polish review should be non-rewriting voice and typography review

Source: PR #8.

TYF should provide a non-rewriting polish review that reads local voice-map and typography-style records, reports narration-lane mismatch, register leaks, dash style drift, ellipsis style drift, and key-term capitalization drift, and points to exact lines without rewriting sections or manuscript files.

### R14. RC recovery should protect local draft edits without auto-merging

Source: PR #9, `rc-gap-recovery-dashboard-doctor`, merged 2026-06-27T14:35:48Z.

TYF should provide local draft recovery helpers and Workbench recovery actions when a draft changed outside the browser window. Recovery should write local review artifacts only, never manuscript text, and never auto-merge.

### R15. RC doctor should verify private-RC workspace health

Source: PR #9.

TYF should provide an RC doctor that checks the private-RC workspace surface and writes reports under `.review/workbench/`. Doctor checks should improve confidence without editing manuscript prose.

### R16. Storage contracts should be explicit and executable

Source: PR #10, `rc-architecture-contracts`, merged 2026-06-27T16:54:12Z.

TYF should declare storage classes for canonical prose, canonical author records, mutable record stores, hash-chain ledgers, append logs, generated review artifacts, rebuildable caches, and recovery artifacts. These contracts should be machine-readable and checked by tests or doctor tooling.

### R17. Workbench HTML extension should use named slots

Source: PR #10.

TYF should avoid brittle anonymous string replacement in Workbench HTML extensions. Live Workbench additions should pass through named slots that fail loudly when anchors drift.

### R18. Command surface should converge toward canonical review commands

Source: PR #10 and `docs/RC_ARCHITECTURE_RED_TEAM.md`.

TYF should reduce command-surface fragmentation by preserving standalone commands where useful while introducing canonical review wrappers such as `tyf-review graph`, `tyf-review concept`, `tyf-review continuity`, `tyf-review polish`, and `tyf-review doctor`.

### R19. Workbench recovery routes require executable route tests

Source: PR #10.

TYF should test Workbench recovery routes with a real loopback server harness, token enforcement for side-effecting routes, and concrete reload/copy/conflict-packet behavior.

### R20. Architecture safety invariants should be executable and proportional

Source: PR #10.

TYF should enforce architecture-level guard rails for local single-author safety: no new source-of-truth store, no manuscript write route, no remote server default, no browser automation dependency, no suspicious direct manuscript writes outside known Gate helpers, and no forbidden manuscript route markers.

## Medium-confidence commit-derived requirements

### R21. Concept-level review should include contradiction and rename detection

Source: first-parent commits `e0429da`, `def2e95`, `c8d77f5`, `3fafefa`.

TYF should support concept-level review outputs, including contradiction and rename detection, with executable tests and a command surface.

### R22. Continuity review should be registry-based

Source: first-parent commits `66aa16b`, `da85c26`, `0bbd7f0`, `9835aac`.

TYF should support registry-based continuity review with command exposure, tests, and documentation.

## Superseded evidence, not accepted requirements

### Closed PR #2

`Add v0.6 local double-surface Workbench slice` was closed unmerged and superseded by PR #3.

### Closed PR #4

`Add v0.6 local double-surface Workbench` was closed unmerged and superseded by PR #3.

These PRs support the Workbench direction but should not be promoted as separate accepted requirements.

## Reconciliation hints

- R3, R4, R6, R7, R8, R14, R17, and R19 all belong to the Workbench surface.
- R9, R10, R16, and R20 belong to storage and architecture truthfulness.
- R11, R12, R13, R21, and R22 belong to full-book review and redactor capability.
- R1, R2, R5, R15, and R18 are cross-cutting product or command-surface requirements.
- Preserve all items as review-only until the operator explicitly promotes, splits, edits, or rejects them.
