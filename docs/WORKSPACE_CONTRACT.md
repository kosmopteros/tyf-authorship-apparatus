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
│   ├── characters/                # isolated character knowledge dossiers
│   └── claims.md          # every load-bearing claim → source(s)
│
├── voice/                 # The voice registers: registers, shared
│   ├── registers/                # one file per register
│   ├── characters/               # isolated character voice dossiers
│   ├── exemplar-passages/
│   ├── register-fences.md
│   └── anti-patterns.md
│
├── .tyf/                         # apparatus memory: events.jsonl + SQLite notice index (not the work)
├── .proposals/                   # harness self-extensions awaiting author commit
└── .hooks/                       # contextual hook definitions
```

## Read-only enforcement

Elicit, Read (sympathetic read), Diagnose, and Audit (adversarial audit) get no write access to any work's `manuscript/`. Propose writes only to `.review/`. Compose writes only to `drafts/`. Revise writes to `manuscript/`, and only through the controlled write: `tyf propose`, `tyf audit --record`, `tyf review`, `tyf accept --evidence` with optional `--lines 2,5-8` for partial source-line acceptance or `--patch <diff>` for an exact reviewed unified diff, then `tyf write --decision`. The helper also updates and enforces `work.yaml` status: `structuring`/`ready-for-audit`, `drafting`, `audited`, `accepted`, and `written` are no longer labels only, because `tyf accept` refuses before `audited`, verifies the audit belongs to the same proposal, requires a matching author-readable review packet, and `tyf write` refuses before `accepted`. Source captures and textual imports mint stable fragments in `sources/fragments/`; source-grounded proposals include them with `tyf propose --source-ref <id>`, and proposal, audit, review, decision, write-log, and doctor integrity checks carry those source refs forward. Fragments are workspace-owned: they preserve origin work/session, but later works may reuse them without duplicate capture. Proposal, audit, review, and decision records are sealed in `.review/record-seals.jsonl`; `tyf write` and `tyf doctor` refuse mismatched seals instead of trusting edited JSON. Controlled writes also acquire a per-unit lock under `.review/locks/` before mutating a manuscript destination. If the author directly edits a manuscript unit, `tyf adopt <work> <unit> --evidence "<what happened>"` preserves the direct edit in `.review/author-revisions/` and records it as the new base before the next controlled write. In Claude Code this is real tool scoping on the subagent. In Desktop it is enforced by routing every edit through `controlling-manuscript-writes`.

`tyf start [path]` is the public writing-session shortcut. It may run without a title, creates or reuses the root single work, records any supplied title or writing language, creates or reuses `sources/interviews/work-first-session.md`, preserves an optional scaffold/chat/PDF/Pages file/formatted manuscript/audio/scan/folder/zip through `sources/imports/`, prints the source fragment id when textual source is minted, writes `.review/writing-runway.md`, and creates `drafts/candidate-draft.md` for candidate prose. The first-session packet includes a gentle attention deck; it invites only enough source, pressure, voice, care, flattening-risk, and first-passage material to begin one candidate passage. A faithful next candidate beats an endless perfection pass, so these prompts stop once drafting can begin. Those files are prompts and working surfaces for the author; they are not manuscript. `tyf begin <id>` is the explicit-id form when an agent already needs a stable id. `tyf import <path>` preserves later material under `sources/imports/`, writes an orientation packet, and updates active root title/language metadata when supplied. Text imports can mint source fragments immediately; zip and folder arrivals are containment-first, listed and analyzed before anything is unpacked or merged into live workspace structure. Binary, unreadable, and too-large arrivals are preserved but marked `Extraction needed`: use OCR or transcription, document conversion, or chunk explicitly before structuring. Do not invent contents from preserved artifacts or imply that a file was read when no source fragment was minted. Existing work recovery is review-only: when prior-manuscript or illustration signals appear, TYF writes `.review/existing-work-recovery.md` for spine recovery, source-status mapping, uncertain or AI-drafted passage mapping, voice clues, illustration inventory, open author decisions, and one next writing move before forward drafting. `tyf capture work --kind source|voice|claim|question --text <text>` appends author-supplied material to `sources/notes/`, `voice/exemplar-passages/`, `knowledge-base/claims/`, or `knowledge-base/open-questions/` respectively. `tyf structure work --source-ref <id> [--record <json>]` reads stable source fragments, records source-linked claims, examples, questions, and unclassified material into `knowledge-base/`, updates the derived and inspectable `knowledge-base/retrieval-index.jsonl` with sample questions for each anchor, and writes `.review/amanuensis-brief.md`. Without `--record`, the helper only extracts explicit labelled source lines. With `--record`, the skill-guided amanuensis can interpret non-English, unlabeled, or nuanced material into a small language-neutral JSON object, while the helper validates, IDs, stores, and links. Its questions are gentle nudges of attention, not doubts in the author's judgment. `tyf attend [work] [--source-ref <id>] [--query <focus>]` writes `.review/gentle-attention.md`, a review-only amanuensis packet that turns those structured anchors into source-grounded next questions without treating silence as a defect, running audit pressure, or writing manuscript text. The packet shows the transparent local retrieval anchors used to choose the first question; retrieval guides attention, but source and author judgment remain visible. `tyf diagnose [work] --unit drafts/candidate-draft.md --band section --symptom "<reader symptom>"` writes `.review/current-diagnosis.md` and an archived `.review/diagnostics/<id>.md` packet for systematic isolation: band, reader symptom, source/register reminders, mechanical cause-frame prompts, and one next experiment. It is not a rewrite and writes no manuscript text. `tyf character <name>` appends isolated per-character knowledge and voice notes; `tyf consult-character <work> <name> --prompt <question>` writes a quarantined `.review/character-consults/` packet for candidate dramatic insight grounded only in that character dossier. If a hidden sub-agent is used, that packet is its full boundary and the answer returns through the amanuensis. `tyf resume` recovers the live return context from those review-only packets: current session, diagnosis, gentle attention, feedback, amanuensis brief, runway, unanswered prompts, and proposals. None of these write to `manuscript/`.

## Transparent reflexes and git recovery

TYF's hooks must be visible. `tyf reflexes` lists the active apparatus reflexes: the read-only session-start hook, the read-only message-sent prompt hook, documentation honesty after mutating commands, the attentive-amanuensis notice hook after controlled writes, integrity checks through `tyf doctor`, and the git recovery path. `tyf hook session-start` emits host-injectable JSON context with the active work status and automatic author reflexes so an agent entering the workspace can run `tyf resume`, `tyf start`, or `tyf start <path>` without asking the author to invoke a skill. `tyf hook message-sent` can run on a host prompt-submit event: it reads the submitted prompt from stdin JSON, adds context only for continuation, arrivals, character questions, and Gate-adjacent prompts, and stays silent for unrelated prompts. Neither hook mutates `.tyf/events.jsonl`, the notice index, or manuscript files. If the workspace is inside a git repository, mutating commands report the count of changed paths and suggest `tyf snapshot --message "..."`. They do not stage or commit. `tyf snapshot` is the explicit action that stages and commits the current workspace state as a recovery point.

## The harness, briefly

After intake, authorship is iterative, not a pipeline. A minimal harness handles three things: contextual hooks (save fires an AI-tell scan; opening a chapter loads the relevant registers and the chapter's `.review/`; marking a unit ready fires the adversarial audit), efficient context loading (only the active band, pass, and work are hydrated), and controlled self-extension (the system proposes new anti-patterns, fences, or skills to `.proposals/`; the author commits them). The harness never writes to `voice/` or the skills directory directly.
