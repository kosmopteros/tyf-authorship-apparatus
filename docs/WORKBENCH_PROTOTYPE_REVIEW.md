# Workbench prototype review

Status: review after scaffolding the Workbench, MCP bridge, Codex bridge, hook recorder, schema helper, and focused tests.

## What is now scaffolded

- `scripts/tyf_workbench_v06.py`: local multi-unit writing desk.
- `scripts/tyf_workbench_mcp.py`: stdio MCP server exposing TYF-safe tools.
- `scripts/tyf_codex_bridge.py`: local bridge scaffold for `codex app-server`.
- `scripts/tyf_codex_hook.py`: tolerant recorder for Codex hook events.
- `scripts/tyf_codex_schema.py`: local schema compatibility helper for Codex app-server.
- `docs/CODEX_MCP_CONFIG.sample.toml`: MCP setup sample.
- `docs/CODEX_HOOKS.sample.toml`: hook wiring sample.
- `docs/WORKBENCH_TWO_WAY_MACHINERY.md`: two-way design.
- `tests/test_workbench_v06.py`: Workbench primitive coverage.
- `tests/test_workbench_mcp.py`: MCP tool coverage.
- `tests/test_codex_hook_recorder.py`: hook recorder status coverage.
- `tests/test_codex_bridge_context.py`: bridge context and status coverage.

## Critical review

### 1. Good: locality boundary is coherent

The Workbench, MCP server, bridge, and hook recorder all default to local files and loopback or stdio transport. The app-server bridge launches `codex app-server` over stdio instead of exposing a raw browser WebSocket to Codex.

This matches the target-state principle: the desk is local, file-backed, and author-owned.

### 2. Good: no manuscript write surface

The Workbench writes only drafts, notes, packets, status files, and event logs. The MCP server exposes TYF verbs rather than raw filesystem verbs. The app-server bridge builds context and forwards turns but does not expose any manuscript mutation route.

That is the most important invariant.

### 3. Fixed: Codex status has a plain-file visibility lane

Both MCP and hooks can write visible status files:

- `.review/surface/codex-turn-status.json`
- `.review/surface/codex-turn-status.jsonl`
- `.review/surface/codex-hooks.jsonl`
- `.review/surface/codex-bridge-events.jsonl`
- `.review/surface/codex-bridge-status.json`

The browser still needs a live status card, but the state now exists in files and is covered by tests.

### 4. Fixed: app-server bridge is shaped around the protocol boundary

The bridge uses newline-delimited JSON over stdio and omits the `jsonrpc` field on the app-server wire. It initializes, emits `initialized`, starts threads, starts turns, and records notifications.

It also stays behind a local TYF bridge instead of letting the browser talk directly to Codex app-server.

### 5. Fixed: schema compatibility has a helper

`tyf_codex_schema.py` runs the local Codex schema generation command, stores version-specific artifacts under `.tyf/codex-app-server-schema/`, and writes review packets:

- `.review/surface/codex-app-server-compat.json`
- `.review/surface/codex-app-server-compat.md`

This does not prove compatibility by itself, but it prevents the bridge from pretending the app-server schema is timeless.

### 6. Fixed: bridge and hook tests now exist

The original combined bridge/hook test write was blocked by the connector. Splitting the tests solved it:

- `tests/test_codex_hook_recorder.py`
- `tests/test_codex_bridge_context.py`

Both assert that status/context paths are written while `manuscript/` stays unchanged.

### 7. Remaining weakness: browser UI is not yet wired to bridge events

The Workbench can write context packets, and the bridge can record events, but the browser does not yet poll or stream those bridge/status files. The next fix should add a small status card in the Workbench side panel:

- last Codex status
- changed paths
- latest bridge event
- conflict warning if active draft changed on disk

This can be simple polling every 2 to 5 seconds before adding SSE.

### 8. Remaining weakness: app-server approvals are only recorded, not mirrored

The bridge records notifications generically. It does not yet provide an approval UI for app-server permission requests. Until that exists, the bridge should be treated as scaffolded, not a complete browser-native chat.

MCP remains the safe path for current authoring.

### 9. Remaining weakness: hook config is intentionally approximate

The hook recorder is tolerant, but `docs/CODEX_HOOKS.sample.toml` is a sample rather than verified exact current Codex hook syntax. This is acceptable for scaffold status, but the first real local test should validate it against the installed Codex version.

## Next fixes before calling browser-native chat complete

1. Add Workbench polling for `.review/surface/codex-turn-status.json` and `.review/surface/codex-bridge-status.json`.
2. Add an approval-event model before any browser-native Codex chat is presented as usable.
3. Validate the sample hook config against the installed Codex version.
4. Wire `tyf surface --v06` or a `tyf workbench` command so authors do not need to call script paths.

## Current verdict

The prototype is now a coherent local-first scaffold with tests for the core Workbench, MCP bridge, hook recorder, and bridge context path.

It is strong enough for the immediate author workflow:

- write in the Workbench
- let Codex read active selection through MCP
- let Codex create notes or Gate packets through safe tools
- record Codex turn status visibly
- prepare app-server context without exposing manuscript writes

It is not yet strong enough to replace the Codex CLI or IDE with an embedded browser chat. That should stay a later slice after UI polling, approval mirroring, and local hook validation are in place.
