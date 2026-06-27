# TYF Workbench v0.6 Implementation Pass

Status: implementation slice for the local double-surface Workbench target.

This pass turns the target-state document into the smallest real authoring desk that can help a live author write books now. It does not try to finish the v0.7, v0.8, or v0.9 roadmap in one jump.

## Research conclusion

The target state describes two surfaces:

1. A writing surface where the author can touch draft units, manuscript previews, notes, image references, style, and selections.
2. An amanuensis surface that can receive the active unit, selection, local notes, style context, and related passages without manual copy-paste.

The current v0.5 surface already has the right safety instincts: local HTML, plain JSON data, compare-and-swap draft saves, read-only manuscript preview, and Gate packet creation. The gap is not a missing LLM. The gap is that the author still has only one `drafts/candidate-draft.md` and no durable unit map, notes, footnote candidates, or active context packet.

So the first useful implementation is not React, Electron, a hosted database, or embedded chat. It is a local stdlib workbench daemon that extends the existing surface into a multi-unit writing desk while preserving the current doctrine.

## What to use now

Use the current repo's boring stack:

- Python stdlib only.
- Local `http.server` plus generated HTML.
- Plain Markdown, YAML-like files, and JSONL as the durable state.
- Compare-and-swap writes for draft units.
- Read-only manuscript preview.
- Review-only records for notes, footnote candidates, Gate packets, and amanuensis context.
- A local capability token for side-effecting browser APIs.
- Loopback binding by default.

Avoid for v0.6:

- React, Next, Electron, FastAPI, SQLite as primary Workbench state, cloud sync, auth systems, vector databases, embedded chat, and live multi-user editing.
- Raw write-any-file browser APIs.
- Any direct manuscript write from the browser.

The reason is simple: TYF is already a plain-file authorship apparatus. The Workbench should make the plain-file body touchable, not replace it with an app database.

## How it looks

The v0.6 Workbench is a four-part local desk:

```text
Book map | Editable draft unit | Read-only manuscript preview | Apparatus panel
```

The author can:

- select a unit from `outline/book-map.yaml`;
- write directly into the unit's draft file;
- see the matching manuscript file as read-only context;
- save the draft only when the loaded hash still matches disk;
- select text and leave an author note;
- turn an author note into a review-only footnote candidate;
- build a Gate packet from the selected draft text;
- write an amanuensis context packet for Codex or another TYF amanuensis surface.

The apparatus panel carries the parts that make this feel like a writing desk rather than a text box:

- unit notes;
- context packet preview;
- running style sheet;
- book style file.

## Files introduced by the slice

The standalone v0.6 script creates or uses:

```text
outline/book-map.yaml
knowledge-base/author-notes.jsonl
.review/footnote-candidates/*.json
.review/footnote-candidates/*.md
.review/gate-packets/*.json
.review/gate-packets/*.md
.review/surface/index.html
.review/surface/workbench-data.json
.review/surface/active-context.json
.tyf/workbench-state.json
.tyf/events.jsonl
```

These files are readable, diffable, and recoverable. Derived surface files can be rebuilt.

## Why this is a standalone script first

The existing `scripts/tyf.py` is already large and release-sensitive. This pass adds a standalone script first so the v0.6 desk can be used and tested without destabilizing `tyf surface` in v0.5.

The intended next integration is straightforward:

1. Run the standalone script while writing real book material.
2. Fold the stable primitives back into `scripts/tyf.py` or expose them through a `tyf workbench` command.
3. Keep the old `tyf surface` path as compatibility until the new desk is proven.

This is a product-first move: make the author able to write now, then harden the command surface.

## Command

From a TYF workspace root:

```bash
python scripts/tyf_workbench_v06.py --serve --open
```

Static preview only:

```bash
python scripts/tyf_workbench_v06.py
```

A non-default port:

```bash
python scripts/tyf_workbench_v06.py --serve --port 8766
```

By default the server binds to `127.0.0.1`. A non-loopback binding is refused unless the author explicitly passes `--allow-remote`.

## API surface

All side-effecting APIs require the in-page local capability token:

- `POST /api/save-draft`
- `POST /api/author-note`
- `POST /api/footnote-candidate`
- `POST /api/gate-packet`
- `POST /api/workbench-state`
- `POST /api/context-packet`

Read APIs:

- `GET /`
- `GET /index.html`
- `GET /workbench-data.json`

There is no raw write-any-file endpoint.

## v0.7 bridge after this

Once the local desk is stable, the next slice should not add browser chat first. It should make Codex and the Workbench aware of the same active context:

- expose `get_active_workbench_context`;
- expose `get_active_selection`;
- expose `list_author_notes`;
- expose `create_author_note`;
- expose `propose_footnote_from_note`;
- expose `prepare_gate_packet`;
- add quiet hooks that publish active unit and changed files.

Only after that should the browser-native amanuensis chat be considered.

## Acceptance check for this slice

This slice is successful when an author can open a local TYF book folder, see a multi-unit body, write directly in draft space, preserve manuscript as read-only, capture a selection, leave a durable author note, turn that note into a footnote candidate, prepare a Gate packet, and produce an amanuensis context packet without becoming the operator of a machine.
