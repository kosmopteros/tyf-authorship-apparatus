# Workbench v0.6 implementation plan

Status: implemented as a first local slice in `scripts/tyf_workbench_v06.py`, with the public `tyf workbench` front door now routed through the live wrapper in `scripts/tyf_workbench_live.py`.

See also: `docs/WORKBENCH_EXTERNAL_CRITIQUE_COUNCIL.md` for the 12-lens external-style critique and convergence map.

This document is the implementation bridge between `docs/WORKBENCH_TARGET_STATE.md` and runnable code. It chooses the smallest desk that solves the immediate authorship problem: the author can write inside TYF, across many draft units, while the manuscript remains protected by the Gate.

## Product judgement

The target state says the author needs a desk, not a command surface or a chat box. The first useful version should therefore be a writing environment, not an LLM conversation embedded into the repo.

The v0.6 slice chooses:

- local browser UI instead of Electron or a hosted app
- plain Markdown, YAML-shaped text, and JSONL instead of a database
- a small localhost server instead of a framework
- draft writes only, with compare-and-swap hashes
- manuscript preview only, with no manuscript write API
- context packets and MCP tools for the amanuensis instead of embedded chat

This keeps the apparatus aligned with the existing TYF rule: the author is the source, the apparatus proposes and preserves, and `manuscript/` is written only through the controlled Gate.

## How it looks

The base v0.6 Workbench is a four-panel browser desk. The public `tyf workbench`
command adds the live wrapper: assistant status, save-safety state, approval
state, review dashboard, and recovery actions.

1. **Book map sidebar**
   - reads `outline/book-map.yaml`
   - discovers `drafts/*.md` and `manuscript/*.md`
   - lets the author move between units
   - can create a new draft unit

2. **Draft surface**
   - editable Markdown textarea
   - saves only under `drafts/`
   - save is guarded by the hash loaded into the browser
   - stale browser state returns a conflict instead of overwriting disk

3. **Manuscript surface**
   - read-only preview from `manuscript/`
   - no POST route writes manuscript text
   - the UI repeats that manuscript writes remain Gate-only

4. **Apparatus side panel**
   - captures current selection
   - writes author notes to `knowledge-base/author-notes.jsonl`
   - converts notes into footnote candidate packets under `.review/footnote-candidates/`
   - writes selection Gate packets under `.review/gate-packets/`
   - writes an active context packet for Codex or another amanuensis under `.review/workbench/active-context.md`
   - shows the style sheet and image inventory

## How to run

From a TYF workspace root:

```bash
tyf workbench --serve --open
```

For a named work:

```bash
tyf workbench my-work --serve --open
```

To regenerate `outline/book-map.yaml` from discovered draft and manuscript files:

```bash
tyf workbench --refresh-map
```

To connect Codex to the Workbench MCP server without hand-editing paths:

```bash
tyf workbench --codex-mcp-config
```

That writes the ready Codex user config block to `$CODEX_HOME/config.toml` or
`~/.codex/config.toml`, using the current TYF pack path and workspace path. The
server is workspace-bound and exposes no tools when Codex is launched outside
that book folder. It exposes TYF-named Workbench tools only; it does not add raw
filesystem tools or a manuscript write API.

The helper delegates to `scripts/tyf_workbench_live.py`, which wraps the base
v0.6 Workbench. It writes author-facing artifacts to
`.review/workbench/workbench-live.html` and
`.review/workbench/workbench-live-data.json`. The base v0.6 module remains
callable for focused diagnostics and still owns the shared draft/note/Gate
packet primitives. Static HTML is useful for inspection, but draft saves and
note creation require `--serve`.

## MCP bridge

The first MCP bridge is `scripts/tyf_workbench_mcp.py`.

It is a stdio MCP server for Codex and other MCP clients. It exposes TYF operations, not raw filesystem operations:

- `get_active_workbench_context`
- `get_active_selection`
- `read_unit_context`
- `search_book_graph`
- `list_author_notes`
- `create_author_note`
- `propose_footnote_from_note`
- `prepare_gate_packet`
- `refresh_book_graph`
- `refresh_book_map`
- `workbench_current_conflicts`
- `record_codex_turn_status`

Configuration example: `docs/CODEX_MCP_CONFIG.sample.toml`.

The MCP bridge lets Codex know what the author is touching without manual copy-paste, and lets Codex create notes, footnote candidates, and review packets without receiving a raw write-any-file tool. It still has no manuscript write API.

From inside a book workspace, `tyf workbench --codex-mcp-config` writes the
ready Codex MCP config to `$CODEX_HOME/config.toml` or `~/.codex/config.toml`.
The sample file remains a readable reference for manual installs.

## Codex visibility and bridge scaffolds

Additional local bridge pieces now exist:

- `scripts/tyf_codex_hook.py`: tolerant Codex hook recorder that writes status files only.
- `docs/CODEX_HOOKS.sample.toml`: readable hook wiring sample.
- `scripts/tyf_codex_bridge.py`: local `codex app-server` bridge scaffold over stdio.
- `scripts/tyf_codex_bridge_v07.py`: approval-aware bridge wrapper that records app-server approval requests and returns bridge-side decisions to the app-server request id.
- `scripts/tyf_codex_schema.py`: helper for generating version-specific app-server schema compatibility artifacts.

The app-server bridge is intentionally behind TYF rather than exposed directly to the browser. It builds input from the active Workbench selection, unit hashes, notes, related passages, and style sheet. It records events and turn status under `.review/workbench/`. It does not expose a manuscript write route.

## Files created or used

- `outline/book-map.yaml`
- `drafts/*.md`
- `manuscript/*.md`
- `style-sheet.md`
- `design/book-style.yaml`
- `assets/images/index.jsonl`
- `knowledge-base/author-notes.jsonl`
- `.review/workbench/workbench-live.html`
- `.review/workbench/workbench-live-data.json`
- `.review/workbench/workbench-v06.html` (base helper diagnostic artifact)
- `.review/workbench/workbench-v06-data.json` (base helper diagnostic artifact)
- `.review/workbench/active-context.md`
- `.review/workbench/active-context.json`
- `.review/workbench/book-graph-lite.json`
- `.review/workbench/codex-turn-status.json`
- `.review/workbench/codex-turn-status.jsonl`
- `.review/workbench/codex-hooks.jsonl`
- `.review/workbench/codex-bridge-events.jsonl`
- `.review/workbench/codex-bridge-status.json`
- `.review/workbench/codex-approval-current.json`
- `.review/workbench/codex-approval-events.jsonl`
- `.review/workbench/codex-app-server-compat.md`
- `.review/workbench/codex-app-server-compat.json`
- `.review/gate-packets/*.md`
- `.review/gate-packets/*.json`
- `.review/footnote-candidates/*.md`
- `.review/footnote-candidates/*.json`
- `.tyf/workbench-state.json`
- `.tyf/events.jsonl`
- `.tyf/codex-app-server-schema/`

## Local server API

The local Workbench server exposes only TYF-named safe operations.

- `GET /`
- `GET /workbench-data.json`
- `POST /api/save-draft`
- `POST /api/create-draft-unit`
- `POST /api/author-note`
- `POST /api/footnote-candidate`
- `POST /api/gate-packet`
- `POST /api/context-packet`
- `POST /api/save-state`

There is no raw write-any-file route and no manuscript write route.

## Security and overwrite model

The default Workbench host is `127.0.0.1`. Binding to a non-loopback host requires `--allow-remote`.

Side-effecting POST requests require a per-session capability token embedded in the served page. This is not meant to be internet security. It is a local misuse guard so a random page cannot casually POST into the workbench without the session token.

All workspace paths are confined to expected TYF directories and symlink components are refused.

Draft saves use a per-draft Workbench lock plus compare-and-swap:

1. browser loads draft text and `sha256`
2. author edits
3. save request sends loaded hash and new text
4. server acquires a short-lived lock for that draft path
5. server checks the current disk hash inside the lock
6. if disk changed, save returns a conflict with current disk text and browser text
7. if disk did not change, draft is written atomically with a unique temporary file

## What this does not do yet

The current live Workbench still does not implement:

- browser-native Codex chat UI
- persistent semantic graph database
- visual drag and drop chapter reordering
- manuscript insertion
- print or export layout
- multi-user collaboration
The current live wrapper already refreshes visibly from Codex turn status and
bridge status files. The approval-aware bridge now records app-server approval
requests and sends approved, rejected, or cancelled decisions back to the
matching app-server request id. The correct next step is to validate the hook
sample against a local Codex install and build the browser-native chat UI on top
of the bridge rather than exposing `codex app-server` directly.

## Tests

The branch includes focused coverage for:

- Workbench unit discovery, scaffold, CAS save, notes, footnotes, Gate packets, and context packets: `tests/test_workbench_v06.py`
- MCP tool list, context, notes, footnotes, Gate packets, graph lite, status, and conflict detection: `tests/test_workbench_mcp.py`
- Codex hook recorder status files: `tests/test_codex_hook_recorder.py`
- Codex bridge context/status path and Windows launcher resolution: `tests/test_codex_bridge_context.py`
- Codex approval recording and app-server decision round-trip: `tests/test_codex_approvals.py`

## Success test

This slice passes the practical author test when the author can:

1. open the local workbench
2. create or select a draft unit
3. write real prose in that unit
4. see the approved manuscript beside it
5. select a phrase or paragraph
6. leave a note that survives as JSONL
7. create a footnote candidate from that note
8. prepare a Gate packet from selected draft text
9. expose active context to Codex through MCP
10. record Codex status visibly in the Workbench file surface
11. prepare a browser-chat turn through the local bridge without exposing manuscript writes
12. send approval decisions back to Codex app-server through the bridge rather than leaving them as display-only records

That is enough for the apparatus to stop being only a conversation with Codex and start becoming a real authorship desk.
