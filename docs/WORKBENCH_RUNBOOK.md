# Workbench runbook

Status: operator-facing runbook for testing and using the local browser Workbench.

TYF Workbench has two modes. The distinction matters.

## Editable browser mode

Use this when you want to actually write, save drafts, create notes, prepare context packets, or create Gate/recovery packets.

From a TYF book workspace root:

```bash
tyf workbench --serve --open
```

If the browser does not open automatically, run:

```bash
tyf workbench --serve
```

Then copy the printed `http://127.0.0.1:.../` URL into your browser.

`--open` implies `--serve`, so this also starts the editable local server:

```bash
tyf workbench --open
```

Compatibility shortcut if the package entry points are installed:

```bash
tyf-workbench --open
```

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

The static HTML is useful for inspection, but a `file://` browser tab cannot save drafts or call Workbench APIs. For editable browser mode, use `--serve`.

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

From a fresh or existing workspace:

```bash
tyf rc-doctor
# if using installed package shortcuts:
tyf-rc-doctor

tyf workbench --serve --open
```

Then verify in the browser:

- the editor pane appears;
- the manuscript pane is read-only;
- the side panel shows Assistant status, Save safety, Review dashboard, and Needs your approval;
- saving a draft works only in served mode;
- generated static files live under `.review/workbench/`.

## Codex MCP setup

To bind Codex to this book workspace:

```bash
tyf workbench --codex-mcp-config
```

Then restart Codex or reload MCP servers from a Codex session opened inside this workspace.
