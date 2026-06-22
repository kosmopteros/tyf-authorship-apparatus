# The workspace contract

The skills above are the apparatus. The **workspace** is where an author's body of work lives. State is plain, readable files: no black boxes. A workspace holds shared substrate at the top and per-work directories beneath, so several works can share knowledge and voice while staying contained.

This is distinct from the plugin manifests. `plugin.json` describes the skill pack to a harness. The files below describe an author's writing workspace.

```
workspace/
├── CLAUDE.md / AGENTS.md         # router + the commitments + project conventions
├── manifest.yaml                 # voice inheritance rules, hooks
├── WORKSPACE_STATE.yaml          # durable state: active work, active band, write-control state
├── ASSUMPTIONS.md                # explicit, updated as the author learns
│
├── sources/                 # The sources: raw, preserved, shared
│   ├── uploads/  transcripts/  interviews/  notes/  links.md
│   ├── fragments/                  # stable source fragments minted by capture
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
├── works/                        # the works: each work is contained
│   └── <work-id>/
│       ├── work.yaml             # type, writing language, registers used, status, scope
│       ├── outline/              # thesis, argument-spine, chapter-outlines, seed.md
│       ├── manuscript/           # behind the controlled write
│       ├── drafts/               # candidate text from the amanuensis, start packet
│       ├── style-sheet.md        # running, emitted by passes
│       └── .review/              # findings, Gate records, record seals, never auto-applied
│
├── .tyf/                         # apparatus memory: events.jsonl + SQLite notice index (not the work)
├── .proposals/                   # harness self-extensions awaiting author commit
└── .hooks/                       # contextual hook definitions
```

## Read-only enforcement

Elicit, Read (sympathetic read), Diagnose, and Audit (adversarial audit) get no write access to any work's `manuscript/`. Propose writes only to `.review/`. Compose writes only to `drafts/`. Revise writes to `manuscript/`, and only through the controlled write: `tyf propose`, `tyf audit --record`, `tyf accept --evidence` with optional `--lines 2,5-8` for partial source-line acceptance or `--patch <diff>` for an exact reviewed unified diff, then `tyf write --decision`. Source captures mint stable fragments in `sources/fragments/`; source-grounded proposals include them with `tyf propose --source-ref <id>`, and proposal, audit, decision, write-log, and doctor integrity checks carry those source refs forward. Proposal, audit, and decision records are sealed in `.review/record-seals.jsonl`; `tyf write` and `tyf doctor` refuse mismatched seals instead of trusting edited JSON. Controlled writes also acquire a per-unit lock under `.review/locks/` before mutating a manuscript destination. In Claude Code this is real tool scoping on the subagent. In Desktop it is enforced by routing every edit through `controlling-manuscript-writes`.

`tyf start "Working Title" --language "<writing language>"` is the public first-session shortcut. It creates a normal work from the title, marks it active, records the writing language in `work.yaml`, and adds `drafts/00-start-here.md`, `outline/seed.md`, and `.review/today.md`. Those files are prompts and records for the author; they are not manuscript. `tyf begin <id>` is the lower-level form when an agent already needs a stable work id. `tyf capture <work> --kind source|voice|claim|question --text <text>` appends author-supplied material to `sources/notes/`, `voice/exemplar-passages/`, `knowledge-base/claims/`, or `knowledge-base/open-questions/` respectively. Source captures also create an inspectable source fragment with an id such as `src-...`, and later `tyf propose --source-ref <id>` binds that preserved material into the Gate. Capture binds each note to an existing work and never writes to `works/<id>/manuscript/`.

## Transparent reflexes and git recovery

TYF's hooks must be visible. `tyf reflexes` lists the active apparatus reflexes: documentation honesty after mutating commands, the attentive-amanuensis notice hook after controlled writes, integrity checks through `tyf doctor`, and the git recovery path. If the workspace is inside a git repository, mutating commands report the count of changed paths and suggest `tyf snapshot --message "..."`. They do not stage or commit. `tyf snapshot` is the explicit action that stages and commits the current workspace state as a recovery point.

## The harness, briefly

After intake, authorship is iterative, not a pipeline. A minimal harness handles three things: contextual hooks (save fires an AI-tell scan; opening a chapter loads the relevant registers and the chapter's `.review/`; marking a unit ready fires the adversarial audit), efficient context loading (only the active band, pass, and work are hydrated), and controlled self-extension (the system proposes new anti-patterns, fences, or skills to `.proposals/`; the author commits them). The harness never writes to `voice/` or the skills directory directly.
