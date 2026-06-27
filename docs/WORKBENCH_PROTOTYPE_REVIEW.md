# Workbench prototype review

Status: review after scaffolding the Workbench, MCP bridge, Codex bridge, and hook recorder.

## What is now scaffolded

- `scripts/tyf_workbench_v06.py`: local multi-unit writing desk.
- `scripts/tyf_workbench_mcp.py`: stdio MCP server exposing TYF-safe tools.
- `scripts/tyf_codex_bridge.py`: local bridge scaffold for `codex app-server`.
- `scripts/tyf_codex_hook.py`: tolerant recorder for Codex hook events.
- `docs/CODEX_MCP_CONFIG.sample.toml`: MCP setup sample.
- `docs/CODEX_HOOKS.sample.toml`: hook wiring sample.
- `docs/WORKBENCH_TWO_WAY_MACHINERY.md`: two-way design.

## Critical review

### 1. Good: locality boundary is coherent

The Workbench, MCP server, bridge, and hook recorder all default to local files and loopback or stdio transport. The app-server bridge launches `codex app-server` over stdio instead of exposing a raw browser WebSocket to Codex.

This matches the target-state principle: the desk is local, file-backed, and author-owned.

### 2. Good: no manuscript write surface

The Workbench writes only drafts, notes, packets, status files, and event logs. The MCP server exposes TYF verbs rather than raw filesystem verbs. The app-server bridge builds context and forwards turns but does not expose any manuscript mutation route.

That is the most important invariant.

### 3. Fixed: Codex status has a plain-file visibility lane

Before this pass, the design had status in prose only. Now both MCP and hooks can write visible status files:

- `.review/surface/codex-turn-status.json`
- `.review/surface/codex-turn-status.jsonl`
- `.review/surface/codex-hooks.jsonl`
- `.review/surface/codex-bridge-events.jsonl`
- `.review/surface/codex-bridge-status.json`

The browser still needs a live UI panel, but the state now exists in files.

### 4. Fixed: app-server bridge is now shaped around the real protocol

The bridge uses newline-delimited JSON over stdio and omits the `jsonrpc` field on the wire, matching Codex app-server behavior. It initializes, emits `initialized`, starts threads, starts turns, and records notifications.

### 5. Remaining weakness: browser UI is not yet wired to bridge events

The Workbench can write context packets, and the bridge can record events, but the browser does not yet poll or stream those bridge/status files. The next fix should add a small status card in the Workbench side panel:

- last Codex status
- changed paths
- latest bridge event
- conflict warning if active draft changed on disk

This can be simple polling every 2 to 5 seconds before adding SSE.

### 6. Remaining weakness: app-server approvals are only recorded, not mirrored

The bridge records notifications generically. It does not yet provide an approval UI for app-server permission requests. Until that exists, the bridge should be treated as scaffolded, not a complete browser-native chat.

MCP remains the safe path for current authoring.

### 7. Remaining weakness: schema compatibility is not automated

The docs say to generate app-server schemas with `codex app-server generate-json-schema`, but no helper command exists yet. The next fix should add a command that:

1. runs schema generation into `.tyf/codex-app-server-schema/`
2. records the Codex version
3. writes a compatibility note to `.review/surface/codex-app-server-compat.md`

### 8. Remaining weakness: hook config is intentionally approximate

The hook recorder is tolerant, but `docs/CODEX_HOOKS.sample.toml` is a sample rather than verified exact current Codex hook syntax. This is acceptable for scaffold status, but the first real local test should validate it against the installed Codex version.

### 9. Remaining weakness: tests for bridge and hooks were not committed

The v0.6 Workbench and MCP server have tests in the branch. I attempted to add a combined bridge/hook test file, but the connector blocked that write. The code is still reviewable, but bridge/hook tests should be added from a local clone.

## Next fixes before calling this complete

1. Add Workbench polling for `.review/surface/codex-turn-status.json` and `.review/surface/codex-bridge-status.json`.
2. Add bridge/hook tests from a local clone.
3. Add schema generation helper for app-server compatibility.
4. Add a minimal approval-event model before any browser-native Codex chat is presented as usable.
5. Wire `tyf surface --v06` or a `tyf workbench` command so authors do not need to call a script path.

## Current verdict

The prototype is now a coherent local-first scaffold, not a finished browser-native Codex client.

It is strong enough for the immediate author workflow:

- write in the Workbench
- let Codex read active selection through MCP
- let Codex create notes or Gate packets through safe tools
- record Codex turn status visibly

It is not yet strong enough to replace the Codex CLI or IDE with an embedded browser chat. That should stay a later slice after UI polling, approval mirroring, and schema compatibility are in place.
