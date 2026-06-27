# Workbench v0.6 implementation plan

Status: implemented as a first local slice in `scripts/tyf_workbench_v06.py`.

This document is the implementation bridge between `docs/WORKBENCH_TARGET_STATE.md` and runnable code. It chooses the smallest desk that solves the immediate authorship problem: the author can write inside TYF, across many draft units, while the manuscript remains protected by the Gate.

## Product judgement

The target state says the author needs a desk, not a command surface or a chat box. The first useful version should therefore be a writing environment, not an LLM conversation embedded into the repo.

The v0.6 slice chooses:

- local browser UI instead of Electron or a hosted app
- plain Markdown, YAML-shaped text, and JSONL instead of a database
- a small localhost server instead of a framework
- draft writes only, with compare-and-swap hashes
- manuscript preview only, with no manuscript write API
- context packets for the amanuensis instead of embedded chat

This keeps the apparatus aligned with the existing TYF rule: the author is the source, the apparatus proposes and preserves, and `manuscript/` is written only through the controlled Gate.

## How it looks

The v0.6 Workbench is a four-panel browser desk.

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
   - writes an active context packet for Codex or another amanuensis under `.review/surface/active-context.md`
   - shows the style sheet and image inventory

## How to run

From a TYF workspace root:

```bash
python scripts/tyf_workbench_v06.py --serve --open
```

For a named work:

```bash
python scripts/tyf_workbench_v06.py my-work --serve --open
```

To regenerate `outline/book-map.yaml` from discovered draft and manuscript files:

```bash
python scripts/tyf_workbench_v06.py --refresh-map
```

The script also writes static artifacts to `.review/surface/workbench-v06.html` and `.review/surface/workbench-v06-data.json`. Static HTML is useful for inspection, but draft saves and note creation require `--serve`.

## Files created or used

- `outline/book-map.yaml`
- `drafts/*.md`
- `manuscript/*.md`
- `style-sheet.md`
- `design/book-style.yaml`
- `assets/images/index.jsonl`
- `knowledge-base/author-notes.jsonl`
- `.review/surface/workbench-v06.html`
- `.review/surface/workbench-v06-data.json`
- `.review/surface/active-context.md`
- `.review/surface/active-context.json`
- `.review/gate-packets/*.md`
- `.review/gate-packets/*.json`
- `.review/footnote-candidates/*.md`
- `.review/footnote-candidates/*.json`
- `.tyf/workbench-state.json`
- `.tyf/events.jsonl`

## Local server API

The local server exposes only TYF-named safe operations.

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

The default host is `127.0.0.1`. Binding to a non-loopback host requires `--allow-remote`.

Side-effecting POST requests require a per-session capability token embedded in the served page. This is not meant to be internet security. It is a local misuse guard so a random page cannot casually POST into the workbench without the session token.

All workspace paths are confined to expected TYF directories and symlink components are refused.

Draft saves use compare-and-swap:

1. browser loads draft text and `sha256`
2. author edits
3. save request sends loaded hash and new text
4. server checks current disk hash
5. if disk changed, save returns a conflict with current disk text and browser text
6. if disk did not change, draft is written atomically

## What this does not do yet

v0.6 intentionally does not implement:

- embedded Codex chat
- MCP server tools
- a persistent graph database
- visual drag and drop chapter reordering
- manuscript insertion
- print or export layout
- multi-user collaboration

The correct next step is probably not to add chat immediately. The next step should be to make the context packet richer and let the external amanuensis consume it cleanly. Then MCP can expose the same operations when the local desk feels right.

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
9. export an active context packet for Codex
10. continue writing without leaving the apparatus

That is enough for the apparatus to stop being only a conversation with Codex and start becoming a real authorship desk.
