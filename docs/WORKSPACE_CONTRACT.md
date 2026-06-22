# The workspace contract

The skills above are the apparatus. The **workspace** is where an author's body of work lives. State is plain, readable files: no black boxes. For the beta launch, one book folder is one single work: shared substrate and the book's drafts, outline, manuscript, style sheet, and review records live at the workspace root.

This is distinct from the plugin manifests. `plugin.json` describes the skill pack to a harness. The files below describe an author's writing workspace.

```
workspace/
├── CLAUDE.md / AGENTS.md         # router + the commitments + project conventions
├── manifest.yaml                 # voice inheritance rules, hooks
├── WORKSPACE_STATE.yaml          # durable state: active work, active band, write-control state
├── tyf.portable.json             # portable bundle marker: canonical text vs derived state
├── ASSUMPTIONS.md                # explicit, updated as the author learns
├── work.yaml                     # type, writing language, registers used, status, scope
├── outline/                      # thesis, argument-spine, chapter-outlines, seed.md
├── manuscript/                   # behind the controlled write
├── drafts/                       # candidate text from the amanuensis
├── style-sheet.md                # running, emitted by passes
├── .review/                      # findings, Gate records, record seals, never auto-applied
│
├── sources/                 # The sources: raw, preserved, shared
│   ├── uploads/  transcripts/  interviews/  imports/  notes/  links.md
│   ├── fragments/                  # stable workspace-owned source fragments
│   └── fragments.jsonl             # source fragment index
│
├── knowledge-base/               # The knowledge base: structured, shared
│   ├── concepts/  claims/  examples/  contradictions/  open-questions/
│   └── claims.md          # every load-bearing claim → source(s)
│
├── voice/                 # The voice registers: registers, shared
│   ├── registers/                # one file per register
│   ├── exemplar-passages/
│   ├── register-fences.md
│   └── anti-patterns.md
│
├── .tyf/                         # apparatus memory: events.jsonl + SQLite notice index (not the work)
├── .proposals/                   # harness self-extensions awaiting author commit
└── .hooks/                       # contextual hook definitions
```

## Read-only enforcement

Elicit, Read (sympathetic read), Diagnose, and Audit (adversarial audit) get no write access to any work's `manuscript/`. Propose writes only to `.review/`. Compose writes only to `drafts/`. Revise writes to `manuscript/`, and only through the controlled write: `tyf propose`, `tyf audit --record`, `tyf accept --evidence` with optional `--lines 2,5-8` for partial source-line acceptance or `--patch <diff>` for an exact reviewed unified diff, then `tyf write --decision`. The helper also updates and enforces `work.yaml` status: `structuring`/`ready-for-audit`, `drafting`, `audited`, `accepted`, and `written` are no longer labels only, because `tyf accept` refuses before `audited`, verifies the audit belongs to the same proposal, and `tyf write` refuses before `accepted`. Source captures and textual imports mint stable fragments in `sources/fragments/`; source-grounded proposals include them with `tyf propose --source-ref <id>`, and proposal, audit, decision, write-log, and doctor integrity checks carry those source refs forward. Fragments are workspace-owned: they preserve origin work/session, but later works may reuse them without duplicate capture. Proposal, audit, and decision records are sealed in `.review/record-seals.jsonl`; `tyf write` and `tyf doctor` refuse mismatched seals instead of trusting edited JSON. Controlled writes also acquire a per-unit lock under `.review/locks/` before mutating a manuscript destination. If the author directly edits a manuscript unit, `tyf adopt <work> <unit> --evidence "<what happened>"` preserves the direct edit in `.review/author-revisions/` and records it as the new base before the next controlled write. In Claude Code this is real tool scoping on the subagent. In Desktop it is enforced by routing every edit through `controlling-manuscript-writes`.

`tyf start [path]` is the public writing-session shortcut. It may run without a title, creates or reuses the root single work, records any supplied title or writing language, creates or reuses `sources/interviews/work-first-session.md`, preserves an optional scaffold/chat/folder/zip through `sources/imports/`, writes `.review/writing-runway.md`, and creates `drafts/candidate-draft.md` for candidate prose. Those files are prompts and working surfaces for the author; they are not manuscript. `tyf begin <id>` is the explicit-id form when an agent already needs a stable id. `tyf import <path>` preserves later material under `sources/imports/`, writes an orientation packet, and updates active root title/language metadata when supplied. Text imports can mint source fragments immediately; zip and folder arrivals are containment-first, listed and analyzed before anything is unpacked or merged into live workspace structure. `tyf capture work --kind source|voice|claim|question --text <text>` appends author-supplied material to `sources/notes/`, `voice/exemplar-passages/`, `knowledge-base/claims/`, or `knowledge-base/open-questions/` respectively. None of these write to `manuscript/`.

## Transparent reflexes and git recovery

TYF's hooks must be visible. `tyf reflexes` lists the active apparatus reflexes: documentation honesty after mutating commands, the attentive-amanuensis notice hook after controlled writes, integrity checks through `tyf doctor`, and the git recovery path. If the workspace is inside a git repository, mutating commands report the count of changed paths and suggest `tyf snapshot --message "..."`. They do not stage or commit. `tyf snapshot` is the explicit action that stages and commits the current workspace state as a recovery point.

## The harness, briefly

After intake, authorship is iterative, not a pipeline. A minimal harness handles three things: contextual hooks (save fires an AI-tell scan; opening a chapter loads the relevant registers and the chapter's `.review/`; marking a unit ready fires the adversarial audit), efficient context loading (only the active band, pass, and work are hydrated), and controlled self-extension (the system proposes new anti-patterns, fences, or skills to `.proposals/`; the author commits them). The harness never writes to `voice/` or the skills directory directly.
