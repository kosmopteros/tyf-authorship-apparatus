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
│       ├── work.yaml             # type, registers used, status, scope, overrides
│       ├── outline/              # thesis, argument-spine, chapter-outlines
│       ├── manuscript/           # behind the controlled write
│       ├── drafts/               # candidate text from the amanuensis
│       ├── style-sheet.md        # running, emitted by passes
│       └── .review/              # findings, never auto-applied
│
├── .tyf/                         # apparatus memory: SQLite ledger + event log (not the work)
├── .proposals/                   # harness self-extensions awaiting author commit
└── .hooks/                       # contextual hook definitions
```

## Read-only enforcement

Elicit, Read (sympathetic read), Diagnose, and Audit (adversarial audit) get no write access to any work's `manuscript/`. Propose writes only to `.review/`. Compose writes only to `drafts/`. Revise writes to `manuscript/`, and only through the controlled write. In Claude Code this is real tool scoping on the subagent. In Desktop it is enforced by routing every edit through `controlling-manuscript-writes`.

## The harness, briefly

After intake, authorship is iterative, not a pipeline. A minimal harness handles three things: contextual hooks (save fires an AI-tell scan; opening a chapter loads the relevant registers and the chapter's `.review/`; marking a unit ready fires the adversarial audit), efficient context loading (only the active band, pass, and work are hydrated), and controlled self-extension (the system proposes new anti-patterns, fences, or skills to `.proposals/`; the author commits them). The harness never writes to `voice/` or the skills directory directly.
