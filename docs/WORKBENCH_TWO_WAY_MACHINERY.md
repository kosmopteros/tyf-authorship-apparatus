# Workbench two-way machinery

Status: design plus first runnable scaffolds for Workbench, MCP, Codex bridge, hooks, and schema compatibility.

This document specifies how the TYF Workbench, TYF MCP server, Codex hooks, and optional Codex app-server bridge should work together without turning TYF into a cloud product or a raw filesystem tool.

## Direct answer: is it local?

Yes, by default the TYF side is local.

The intended normal stack is:

```text
Browser Workbench on localhost
  <-> TYF Workbench daemon and event files
  <-> plain workspace files
  <-> TYF MCP server over stdio
  <-> Codex CLI or Codex IDE extension
```

No TYF daemon needs to be public. No manuscript or source text is sent anywhere merely because the Workbench is open. Text leaves the machine only when the author uses Codex or another model path that sends the selected context to that provider.

Codex app-server is also a local process when launched as `codex app-server` over stdio, Unix socket, or a localhost WebSocket. It still talks to OpenAI services as Codex normally does. So the transport can be local while the model execution is not purely offline.

## Responsibilities

### Workbench daemon

The Workbench daemon owns the author-facing desk.

It:

- serves the browser on loopback
- writes draft files only under `drafts/`
- saves draft edits with compare-and-swap hashes
- stores active unit, selection, scroll, and visible panel state in `.tyf/workbench-state.json`
- appends author notes to `knowledge-base/author-notes.jsonl`
- writes footnote candidate packets to `.review/footnote-candidates/`
- writes Gate packets to `.review/gate-packets/`
- writes active context packets to `.review/surface/active-context.md`
- logs apparatus events to `.tyf/events.jsonl`

It does not:

- expose a raw write-any-file API
- expose a manuscript write API
- call a model by default
- decide author intent

### TYF MCP server

The MCP server is the safe tool bridge from Codex into the local desk.

It exposes TYF verbs, not filesystem verbs:

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
- `surface_current_conflicts`
- `record_codex_turn_status`

It does not expose:

- raw `read_file`
- raw `write_file`
- shell
- manuscript write
- source upload
- arbitrary path access

The first implementation is `scripts/tyf_workbench_mcp.py`. It is stdio-only by design, because Codex can launch local stdio MCP servers from configuration. This is the cleanest default trust boundary.

### Codex hooks

Hooks are the quiet visibility lane. They should publish status into local files, not edit prose.

The first recorder is `scripts/tyf_codex_hook.py`. It reads tolerant hook JSON from stdin and writes only status records under `.review/surface/`:

- `.review/surface/codex-turn-status.json`
- `.review/surface/codex-turn-status.jsonl`
- `.review/surface/codex-hooks.jsonl`

Recommended hook behavior:

- `SessionStart`: surface that Codex has entered a TYF workspace
- `UserPromptSubmit`: record prompt class and active Workbench state if relevant
- `PostToolUse`: record changed paths and whether a Gate packet or review packet changed
- `Stop`: record turn summary, pending decisions, and conflict notices

Hooks should not write `manuscript/`.

### Codex app-server bridge

Codex app-server is not a replacement for MCP. It is the optional browser-native amanuensis chat path.

The first local bridge is `scripts/tyf_codex_bridge.py`.

Use it when the Workbench itself needs to:

- start or resume a Codex thread
- send active selection plus context into that thread
- stream or record Codex events back into the desk
- show tool calls, approval prompts, file changes, and turn status inside the desk

The bridge shape is:

```text
Browser Workbench chat panel
  <-> TYF Codex bridge on localhost
  <-> codex app-server over stdio
  <-> Codex agent thread
  <-> TYF MCP server tools
  <-> workspace files
```

The browser should not talk directly to `codex app-server` in WebSocket mode by default. Keep a TYF bridge in between so TYF can:

- inject active Workbench context
- keep a local event ledger
- filter what is sent
- display permissions and tool calls plainly
- keep the manuscript Gate boundary visible
- support a fallback when Codex is not installed

The bridge currently records app-server events to:

- `.review/surface/codex-bridge-events.jsonl`
- `.review/surface/codex-bridge-status.json`
- `.review/surface/codex-turn-status.json`
- `.review/surface/codex-turn-status.jsonl`

It is still a scaffold, not a complete browser-native chat client.

## Two-way flows

### Flow A: Browser selection to Codex context

1. Author selects text in the Workbench draft pane.
2. Browser saves active selection to `.tyf/workbench-state.json` through `/api/save-state`.
3. Author asks Codex in the CLI, IDE, or future browser chat.
4. Codex calls `get_active_workbench_context` through MCP.
5. MCP returns active unit, selected text, notes, style sheet, and related local passages.
6. Codex answers or proposes material in draft/review space.

No copy-paste is needed. The desk remembers what the author touched.

### Flow B: Codex creates a note

1. Codex reads context through MCP.
2. Codex decides that the author intention should be preserved as a note.
3. Codex calls `create_author_note`.
4. MCP appends a JSONL note under `knowledge-base/author-notes.jsonl`.
5. Workbench refreshes or receives a future event notification and shows the note.

The note is author material or amanuensis material. It is not a command to edit manuscript text.

### Flow C: Note to footnote candidate

1. Author or Codex chooses an existing note.
2. Codex calls `propose_footnote_from_note`, or the browser calls the equivalent local API.
3. TYF writes `.review/footnote-candidates/<id>.md` and JSON.
4. The note status becomes `converted-to-footnote`.
5. Any actual manuscript insertion still goes through the Gate.

### Flow D: Selected draft text to Gate packet

1. Author selects a draft passage.
2. Browser or Codex calls `prepare_gate_packet` with the source path, selection, note, and loaded base hash.
3. TYF verifies the current disk hash.
4. If stale, TYF returns a conflict.
5. If current, TYF writes a Gate packet under `.review/gate-packets/`.
6. A later normal TYF proposal, audit, review, decision, and write can move accepted text into `manuscript/`.

### Flow E: Codex turn status back to the browser

1. Codex starts or completes a turn.
2. Hook, MCP call, or bridge event records status.
3. TYF writes `.review/surface/codex-turn-status.json` and appends JSONL history.
4. Workbench can poll this file and show the last turn status and changed paths.
5. If a changed draft hash conflicts with browser state, Workbench should show conflict before save.

### Flow F: Browser-native chat through app-server

This is scaffolded, not complete.

1. Author opens the future Workbench chat panel.
2. Browser asks the TYF bridge to start or resume a Codex thread.
3. Bridge launches `codex app-server` over stdio.
4. Bridge sends `initialize`, then `initialized`.
5. Bridge starts or resumes a thread.
6. On each author question, bridge builds input from:
   - user question
   - active selection
   - active unit path and hash
   - style sheet digest
   - author notes
   - related local passages
   - MCP server availability
7. Bridge sends `turn/start` to app-server.
8. Bridge records Codex notifications as local event/status files.
9. Future browser UI renders agent messages, tool calls, approval needs, changed paths, and final status.
10. Any file changes still happen through Codex permissions and TYF tools.

## Why MCP and app-server are both needed

MCP answers: what can Codex safely know or do inside the TYF workspace?

App-server answers: how can the Workbench host a full Codex conversation with streamed events and approvals?

They should not be collapsed.

MCP is the tool and context surface. App-server is the rich conversation transport. The same TYF tools should be available whether the author talks in the Codex CLI, IDE, or future Workbench chat.

## Local setup

### MCP only

Use `docs/CODEX_MCP_CONFIG.sample.toml` as the starting point.

Minimal shape:

```toml
[mcp_servers.tyf_workbench]
command = "python"
args = [
  "/absolute/path/to/tyf-authorship-apparatus/scripts/tyf_workbench_mcp.py",
  "--workspace",
  "/absolute/path/to/your-tyf-book-workspace"
]
default_tools_approval_mode = "prompt"
```

Read-only context tools can be set to `approve`. Packet-writing or note-writing tools should stay `prompt` until usage proves they are calm.

### Hooks

Use `docs/CODEX_HOOKS.sample.toml` as a readable wiring sample. The exact hook config should be validated against the installed Codex version.

### App-server bridge

Run the local bridge from the TYF workspace:

```bash
python scripts/tyf_codex_bridge.py --workspace /absolute/path/to/your-tyf-book-workspace
```

The bridge launches this by default:

```bash
codex app-server
```

Side-effecting bridge APIs are protected by a per-session `X-TYF-Bridge-Token`. Non-loopback binding requires `--allow-remote`.

### Schema compatibility

Use the helper after Codex upgrades:

```bash
python scripts/tyf_codex_schema.py --workspace /absolute/path/to/your-tyf-book-workspace
```

It stores version-specific artifacts under `.tyf/codex-app-server-schema/` and writes:

- `.review/surface/codex-app-server-compat.json`
- `.review/surface/codex-app-server-compat.md`

## Trust boundary

The local Workbench is trusted by the author because it is the desk.

Codex is trusted only through explicit surfaces:

- MCP tools with TYF names
- approval prompts for side-effecting tools
- app-server permissions and approval events
- local event ledger
- Gate enforcement

No component should silently convert a selection, note, or model suggestion into manuscript text.

## Implementation status

Implemented now:

- local Workbench v0.6 in `scripts/tyf_workbench_v06.py`
- MCP stdio server in `scripts/tyf_workbench_mcp.py`
- Codex MCP config sample in `docs/CODEX_MCP_CONFIG.sample.toml`
- Codex hook recorder in `scripts/tyf_codex_hook.py`
- Codex hooks sample in `docs/CODEX_HOOKS.sample.toml`
- local app-server bridge scaffold in `scripts/tyf_codex_bridge.py`
- schema compatibility helper in `scripts/tyf_codex_schema.py`
- active context packet path in `.review/surface/active-context.md`
- Codex turn status record path in `.review/surface/codex-turn-status.json`
- focused tests for Workbench, MCP, hook recorder, and bridge context

Still to implement before browser-native chat is complete:

- Workbench live polling or SSE display for Codex status files
- approval UI mirroring for app-server events
- local validation of exact hook config syntax against installed Codex
- command wiring such as `tyf surface --v06` or `tyf workbench`

## Product decision

Start with MCP as the usable path. Keep browser-native Codex chat behind the bridge until status polling, approval mirroring, and local hook validation are in place.

The immediate author pain is not the lack of chat. It is that the book has no spatial body. MCP fixes the copy-paste problem while preserving the current Codex workflow. App-server becomes valuable after the desk itself is trustworthy enough to host the conversation.
