# TYF Workbench Target State

Status: target-state concept, not an implemented v0.5 promise.

TYF v0.5 has a modest Draft Review Workbench: a local HTML surface that shows
one candidate draft beside read-only manuscript units. Real book work has now
shown the next shape. The author needs a desk, not only a command surface and
not only a chat box.

The target Workbench is a local, double-surface authorship environment:

- a free writing surface where the author can work directly with draft units,
  manuscript units, notes, images, styles, and selections;
- a contextual amanuensis surface where the author can ask about the active
  unit, a selected phrase, a margin note, a recurring claim, or the whole book.

Codex remains one natural home for the amanuensis, because TYF's doctrine,
skills, Gate discipline, and hidden reflexes already live well there. The
Workbench gives the author the spatial body of the book. The two surfaces should
stay aware of each other through a local event bus and plain files.

## Product Promise

The Workbench should make TYF feel like an attentive writing desk:

- the author writes freely in draft space;
- the author can select any text and ask the amanuensis about it;
- the author can leave notes on lines, paragraphs, sections, images, or whole
  units;
- an author note can become a footnote candidate without copy-paste ceremony;
- the amanuensis knows the active selection, local context, source refs, style
  sheet, notes, and related book graph;
- the manuscript remains protected by the Gate;
- every important state is inspectable in local files.

This is not a move toward a cloud SaaS product. The default shape stays local
first, author-owned, and portable.

## Current Surface Versus Target Surface

Current v0.5 surface:

- one active editable draft: `drafts/candidate-draft.md`;
- many read-only manuscript units;
- local HTML/JSON generated under `.review/surface/`;
- served mode can save the candidate draft with a base-hash conflict check;
- selected candidate text can become a review packet;
- no embedded amanuensis chat;
- no per-segment notes;
- no full-book graph.

Target surface:

- many draft units and manuscript units;
- unit map for front matter, chapters, interludes, afterword, companion matter,
  images, and appendices;
- draft editing per unit, with per-unit base hashes;
- manuscript preview per unit, read-only by default;
- selection-aware amanuensis actions;
- author notes attached to stable text or structural anchors;
- footnote candidates derived from author notes;
- local book graph for cross-unit implications;
- Codex skill, hooks, MCP, and optional app-server/SDK bridge for two-way
  awareness.

## Double Surface

### Writing Surface

The writing surface is where the author touches the book body.

It should support:

- selecting a draft or manuscript unit from a book map;
- editing draft units directly;
- seeing the corresponding approved manuscript unit when one exists;
- comparing draft and manuscript state without treating them as the same thing;
- preserving scroll position and active selection;
- adding image blocks and image notes;
- inspecting paragraph styles and typeface intent;
- creating author notes at line, paragraph, section, image, or unit scope;
- turning an author note into a footnote candidate;
- preparing a Gate packet from a selection, a whole unit, or a reviewed patch.

The manuscript pane is read-only unless a future explicitly marked author mode
uses `tyf adopt` to preserve direct manuscript edits as the new base. The normal
path into `manuscript/` remains proposal, audit, author review, author decision,
and controlled write.

### Amanuensis Surface

The amanuensis surface is not a generic assistant chat. It is the same TYF
amanuensis that already lives in the skills:

- source-grounded;
- voice-aware;
- redactor-aware;
- selection-aware;
- gentle rather than suspicious;
- able to ask one substantive question when needed;
- able to propose candidate prose or treatment in draft/review space;
- never able to silently publish into manuscript.

The author should be able to ask normal writing questions:

- "What is not landing in this paragraph?"
- "Make this less AI-sounding, but keep the argument."
- "Where else does this idea recur?"
- "What source supports this sentence?"
- "Turn this note into a footnote."
- "What would this character say here?"
- "What breaks elsewhere if I remove this chapter?"

The Workbench passes the active unit, selection, note, source refs, relevant
graph neighborhood, and style/register context to the amanuensis. The author
should not need to manually paste context from the browser into chat.

## Codex Integration Shape

The target architecture has four local pieces.

```text
Browser Workbench
  <-> TYF daemon and event bus <-> workspace files
             ^
             |
        TYF MCP server
             ^
             |
        Codex skill

Optional deeper bridge:
Browser chat <-> Codex app-server or SDK <-> Codex thread
```

### TYF Daemon And Event Bus

The daemon owns live workspace awareness:

- watches draft, manuscript, style, notes, image, source, and review files;
- serves the browser Workbench on localhost;
- pushes file and graph updates to the browser over WebSocket or Server-Sent
  Events;
- stores ephemeral UI state such as active unit, active selection, scroll
  position, and visible panels;
- writes durable actions through TYF helper routines rather than ad hoc file
  writes.

The daemon is local-only by default. It should bind to loopback, require a local
capability token for side-effecting APIs, and make all remote exposure an
explicit advanced choice.

### TYF MCP Server

MCP is the bridge from Codex into the Workbench state.

It should expose read tools and carefully scoped actions such as:

- `get_active_workbench_context`;
- `get_active_selection`;
- `read_unit_context`;
- `search_book_graph`;
- `list_author_notes`;
- `create_author_note`;
- `propose_footnote_from_note`;
- `prepare_gate_packet`;
- `refresh_book_graph`;
- `surface_current_conflicts`.

The MCP server should not offer a raw write-any-file tool. It should expose TYF
operations with TYF names and TYF constraints.

MCP is not the main live push channel into Codex. It lets Codex call into TYF
when a turn needs context or action. Live browser updates belong to the daemon.

### Codex Hooks

Codex hooks can keep the two worlds synchronized:

- `SessionStart` can publish that Codex has entered a TYF workspace and can
  request return context;
- `UserPromptSubmit` can publish the prompt class and active TYF routing context;
- `PostToolUse` can publish changed file paths or review packets;
- `Stop` can publish a turn summary, pending Gate state, or conflict notice.

Hooks should be quiet and local. They should enrich context and update the event
bus, not perform manuscript writes.

### Codex App-Server Or SDK

For a browser-native amanuensis chat, the Workbench can use Codex app-server or
the Codex SDK to start, resume, steer, and stream a Codex thread.

This is the deeper integration path:

- the Workbench sends a user question plus the active selection and workspace
  context;
- Codex runs with the TYF skill and MCP server available;
- streamed agent output appears in the Workbench chat;
- tool calls and file changes still go through Codex permissions and TYF helper
  constraints.

This is optional. The smaller path is still valuable: the author works in the
Workbench and continues using Codex chat separately, while MCP and hooks keep
context synchronized.

## Plain-File State

The Workbench should not trap a book in an opaque app database. The workspace
remains the source of truth.

Likely target files and directories:

```text
outline/book-map.yaml              ordered units and book structure
drafts/*.md                        editable candidate units
manuscript/*.md                    approved units, Gate-only by default
style-sheet.md                     running style decisions
design/book-style.yaml             typeface, paragraph styles, production intent
assets/images/                     image files and image-use index
knowledge-base/retrieval-index.jsonl
knowledge-base/author-notes.jsonl  sidecar notes and footnote candidates
.review/surface/                   generated UI data and review packets
.review/gate-packets/              packets prepared from selections
.tyf/events.jsonl                  canonical apparatus event stream
.tyf/workbench-state.json          ephemeral active surface state
```

Names may change during implementation, but the principle should not: durable
author state is readable, diffable, and recoverable. Derived indexes can be
rebuilt.

## Anchors And Notes

Author notes need stable anchors without making Markdown unpleasant.

A note record should include:

- note id;
- target path;
- target kind: unit, heading, paragraph, line, selection, image, or book;
- text quote when a selection exists;
- quote hash;
- optional character offsets from the last observed version;
- surrounding-context hash for re-anchoring;
- note body;
- note status: open, resolved, converted-to-footnote, dismissed;
- provenance: author, amanuensis, import, treatment, critique;
- timestamps;
- optional source refs and graph refs.

Notes should remain author material, not agent commands. If a note says "make
this harsher," TYF should treat it as a writing intention that still needs a
proposal, not as permission to alter manuscript.

Footnotes should be generated as draftable candidates:

1. The author writes or selects a note.
2. The Workbench creates a footnote candidate record.
3. The amanuensis may refine it in draft/review space.
4. The author accepts or rejects it.
5. Any manuscript footnote insertion goes through the Gate.

## Full-Book Graph

The book graph should be derived local machinery, not a new burden on the
author.

It can derive nodes from:

- units and headings;
- claims and examples;
- source fragments;
- author notes;
- motifs, terms, and repeated phrases;
- character dossiers;
- image placements and captions;
- Gate proposals and decisions;
- unresolved gaps and contradictions.

It can derive edges such as:

- supports;
- contradicts;
- repeats;
- depends-on;
- introduces;
- resolves;
- echoes;
- illustrates;
- footnotes;
- cites-source;
- changes-with.

The Workbench should use the graph to answer practical writing questions:

- "Where does this term first appear?"
- "Which later passages depend on this claim?"
- "If this chapter moves earlier, what references become confusing?"
- "Which notes are attached to this motif?"
- "What unresolved source gaps affect this section?"

The graph should be transparent enough to inspect but hidden enough that the
author does not become its operator.

## Concurrency And Conflict Handling

The Workbench should assume that several surfaces may touch the same files:

- the browser editor;
- Codex;
- a desktop editor;
- Git operations;
- TYF helper commands;
- future scheduled checks.

The rule is compare-and-swap for ordinary draft edits and locks for controlled
manuscript writes.

Draft saves:

- load a unit with its current hash;
- save only if the hash still matches;
- return a conflict if the file changed on disk;
- show the current disk version and the proposed browser version;
- allow the author or amanuensis to merge deliberately.

Manuscript writes:

- remain per-unit;
- require proposal, audit, review, decision, base hash, and lock;
- refuse stale base;
- log the resulting hash.

No surface should silently overwrite an authored change.

## Security And Trust Boundary

TYF is an amanuensis, not a cybersecurity prison, but the Workbench still needs
clean boundaries:

- local-only server by default;
- loopback binding by default;
- no unauthenticated non-loopback listener;
- no raw arbitrary file write API;
- no manuscript write API outside the Gate;
- MCP tools named around TYF operations, not filesystem primitives;
- hooks that enrich context rather than perform side effects;
- app-server or SDK integration only when the author chooses browser-native
  amanuensis chat;
- no manuscript or source text sent to external services unless the author uses
  an agent/model path that clearly requires it.

The author should experience protection as calm continuity, not as a wall of
security ceremony.

## Phasing

### v0.6: Local Double Surface

Build the smallest real authoring desk:

- multi-unit draft and manuscript browser;
- `outline/book-map.yaml`;
- editable draft unit pane;
- read-only manuscript unit pane;
- per-unit base-hash saves;
- selection capture;
- author notes sidecar;
- note-to-footnote candidate packet;
- generated Gate packet from selected draft text;
- no embedded Codex chat yet.

### v0.7: Codex-Aware Amanuensis

Make Codex and the Workbench mutually aware:

- TYF daemon and event bus;
- TYF MCP server with read context and safe actions;
- Codex hook publishing into the daemon;
- active selection and active unit available to Codex;
- browser-visible turn status when Codex changes workspace files.

### v0.8: Browser-Native Amanuensis Chat

Add the deeper optional bridge:

- Codex app-server or SDK integration;
- start/resume/steer Codex thread from the Workbench;
- stream amanuensis output into the browser;
- preserve Codex permission and TYF Gate boundaries;
- keep the same TYF skill doctrine.

### v0.9: Book Graph And Treatment

Use the graph to make whole-body edits safer:

- derived book graph;
- motif/claim/source/note relation views;
- cross-unit impact checks;
- typographer-redactor whole-body treatment packets;
- contradiction and dependency surfacing.

### Later: Production Output

Only after the authoring desk is real:

- print preview;
- pagination;
- KDP trim and bleed checks;
- image resolution and rights preflight;
- font embedding checks;
- PDF export;
- publisher templates.

## Non-Goals

The target Workbench is not:

- a cloud-first writing platform;
- a generic chat wrapper;
- a replacement for Codex skills;
- a real-time multi-user editor in the first versions;
- a promise that v0.5 can already do this;
- a way to bypass the controlled write.

## Success Test

The Workbench target is met when an author can open a local book folder, see the
book as a multi-unit body, write in draft space, select text, ask the
amanuensis about that exact text, leave a note, turn a note into a footnote
candidate, see related passages, and move accepted material toward manuscript
without becoming the operator of a machine.

The author should feel: "I am writing the book, and the desk remembers what I am
touching."
