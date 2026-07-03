# Workbench runbook

Status: operator-facing runbook for testing and using the local browser Workbench.

TYF Workbench has two modes. The distinction matters. In Codex Desktop or Claude Code Desktop, the **agent runs these commands**. The non-technical author should experience the Workbench as a local browser desk, not as a terminal task.

## Editable browser mode

Use this when the author wants to actually write, save drafts, create notes, prepare context packets, or create Gate/recovery packets.

From a TYF book workspace root, the agent runs:

```bash
tyf workbench --open
```

`--open` implies `--serve`, so the command starts the editable local server and opens the browser.

If the browser does not open automatically, the agent runs:

```bash
tyf workbench --serve
```

Then give the author the printed `http://127.0.0.1:.../` URL in plain language.

The explicit form is still valid:

```bash
tyf workbench --serve --open
```

Do not ask a non-technical author to choose between static and served mode. Use served mode whenever the author wants to work in the browser.

## Static inspection mode

This only writes inspectable files:

```bash
tyf workbench
```

Outputs:

```text
.review/workbench/workbench-live.html
.review/workbench/workbench-live-data.json
```

The static HTML is useful for inspection, but a `file://` browser tab cannot save drafts or call Workbench APIs. For editable browser mode, use `tyf workbench --open`.

## Safety model

- Workbench writes only `drafts/`, notes, review packets, recovery packets, and generated review state.
- `manuscript/` remains read-only in the Workbench.
- Draft saves use compare-and-swap hashes.
- If Codex or another local process changes a draft while the browser is open, the Workbench shows `Changed outside this window` and offers recovery choices.

## Recovery choices

When a draft changed outside the browser window:

```text
Save my version as copy
Prepare conflict packet
Reload disk version
```

Prefer saving a copy or preparing a packet before reloading disk text over browser text.

## Quick smoke test

From a fresh or existing workspace, the agent runs:

```bash
tyf-rc-doctor
tyf workbench --open
```

Then verify in the browser:

- the editor pane appears;
- the manuscript pane is read-only;
- the side panel shows Assistant status, Save safety, Review dashboard, and Needs your approval;
- saving a draft works only in served mode;
- generated static files live under `.review/workbench/`.

## Codex MCP setup

To bind Codex to this book workspace, the agent runs:

```bash
tyf workbench --codex-mcp-config
```

Then restart Codex or reload MCP servers from a Codex session opened inside this workspace.

## Author-facing language

Do not say:

```text
Run this in your terminal.
```

Say:

```text
I opened the local Workbench for this book. It is running on your machine, and manuscript files remain read-only there.
```
