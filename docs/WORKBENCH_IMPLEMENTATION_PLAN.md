# TYF Workbench v0.6 Implementation Plan

Status: initial executable slice implemented in `scripts/tyf_workbench.py`.

This plan translates `docs/WORKBENCH_TARGET_STATE.md` into the smallest useful authoring desk for writing real books now. It does not try to finish v0.7, v0.8, or v0.9 early. The point of this slice is simple: the author can touch the book body directly without bypassing TYF's Gate.

## Product decision

Use the current TYF shape: Python stdlib helper plus generated local HTML plus an optional localhost server.

Do not start with Electron, React, Monaco, a cloud app, or a database. Those can be justified later, but they would make the first real authoring desk slower to ship and easier to overdesign. The body of the book should stay in plain files. The browser is only the desk.

## What this v0.6 slice gives the author

Run from a TYF workspace root:

```bash
python scripts/tyf_workbench.py --serve --open
```

Or generate static review files only:

```bash
python scripts/tyf_workbench.py
```

The command creates or heals these local files:

```text
outline/book-map.yaml
knowledge-base/author-notes.jsonl
.review/gate-packets/
.review/surface-v06/
.tyf/workbench-state.json
```

The Workbench then shows three practical panes:

1. Book map: an ordered list of draft and manuscript units.
2. Draft surface: the active draft unit, editable with a per-unit base hash.
3. Manuscript and notes: the matching manuscript preview, author notes, footnote candidates, style, and images.

## Implemented behavior

### Multi-unit book body

`outline/book-map.yaml` is the stable structure file. If it does not exist, the Workbench derives an initial map from `drafts/` and `manuscript/` and writes a starter map for the author to edit later.

A unit can point to:

```yaml
units:
  - id: chapter-one
    title: "Chapter One"
    role: chapter
    draft: drafts/chapter-one.md
    manuscript: manuscript/chapter-one.md
```

Draft-only units are valid. Manuscript-only units are valid. A manuscript-only unit gets a matching draft path so the author can start revising in draft space instead of editing the protected manuscript.

### Per-unit draft saves

The Workbench saves only paths under `drafts/`. Each save carries the hash that was loaded in the browser. If the file changed on disk, the save returns a conflict with the current and proposed text instead of overwriting another authored change.

### Manuscript remains protected

The Workbench never writes `manuscript/`. The manuscript pane is preview-only. Candidate movement into manuscript still belongs to the controlled write chain after proposal, audit, author review, and author decision.

### Author notes

Author notes are append-only JSONL records in `knowledge-base/author-notes.jsonl`. A note records:

- id
- target path
- target kind
- selected quote and quote hash
- optional offsets
- surrounding context hash
- note body
- provenance
- status
- timestamps

Notes are author material, not commands. A note can guide an amanuensis proposal, but it does not grant permission to alter manuscript text.

### Footnote candidates

A note can become a footnote candidate. The Workbench writes a candidate record and a Markdown review packet under `.review/gate-packets/`. It does not insert the footnote into the manuscript.

### Gate packets from selections

Selected draft text can become a Gate packet under `.review/gate-packets/`. The packet stores the source path, source hash, selected candidate text, note, unit id, and the fact that no manuscript text was written.

### Local state

The Workbench records active unit and active selection in `.tyf/workbench-state.json`. This is ephemeral desk state, not book content.

### Local capability token

When served, side-effect APIs require a per-session capability token embedded in the local page. Static generated files remain inspectable, but draft save, note creation, and packet creation require server mode.

## Why this is the right first implementation

The target state has four layers: browser Workbench, daemon and event bus, MCP server, and optional Codex app-server or SDK bridge. Starting with the browser and local helper layer is the correct cut because it removes the author's current pain immediately: writing is trapped in chat.

This slice makes the book spatial and editable first. Codex awareness comes next, after the desk knows what the author is touching.

## What is intentionally not implemented yet

- No embedded Codex chat.
- No MCP server.
- No WebSocket or SSE event bus.
- No derived full-book graph.
- No print preview or PDF export.
- No real-time multi-user editing.
- No raw arbitrary file write API.

## Recommended next phases

### Fold into `tyf surface`

The current file is standalone so it can be tested without rewriting the large helper in one risky patch. Once the slice proves usable, fold it into `scripts/tyf.py` behind the existing `tyf surface` command or a `tyf surface --v06` flag.

### v0.7: Codex-aware amanuensis

Add a small TYF MCP server exposing safe operations:

```text
get_active_workbench_context
get_active_selection
read_unit_context
list_author_notes
create_author_note
propose_footnote_from_note
prepare_gate_packet
```

The MCP server should not expose raw filesystem writes. It should expose TYF operations with TYF constraints.

### v0.8: browser-native amanuensis chat

Only after v0.7 is stable, add a browser chat bridge through Codex app-server or SDK. The chat should stream amanuensis output into the Workbench while preserving Codex permissions and TYF Gate boundaries.

### v0.9: book graph

Derive graph records from units, headings, source fragments, claims, notes, motifs, character dossiers, image placements, and Gate decisions. The graph should answer practical writing questions without turning the author into a graph operator.

## Acceptance test for this slice

The v0.6 slice is good enough when an author can open one local book folder, see more than one unit, write into a draft unit, select text, save an author note on that selection, turn the note into a footnote candidate, and prepare a Gate packet without `manuscript/` changing.
