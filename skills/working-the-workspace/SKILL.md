---
name: working-the-workspace
description: "Use whenever operating on the workspace files or repo: reading or writing sources, knowledge-base, voice, works, drafts, or manuscript; deciding where a pass may write; or when unsure which directory a result belongs in"
---

# Working the workspace

## Overview

The workspace is plain, readable files. Every pass has a place it may read and a place it may write, and the manuscript is fenced behind the controlled write. This skill is the map and the rule: it says where things live and who may touch them.

In Cowork and Desktop there is no hard per-subagent read-only scoping, so this discipline is the enforcement. The helper script is the single writer into `manuscript/`.

## The map

```
workspace/
├── WORKSPACE_STATE.yaml      durable state: active work, active band, gates
├── manifest.yaml             voice inheritance, hooks
├── ASSUMPTIONS.md            explicit, updated as the author learns
├── sources/             raw, preserved, source fragments [read-mostly]
├── knowledge-base/           concepts, claims, argument spine, claims index
├── voice/             registers, fences, anti-patterns
├── redactor-canon/           terminology, logic, apparatus, type rules
└── works/<id>/
    ├── work.yaml             type, registers, status, scope, overrides
    ├── outline/              thesis, argument-spine, chapter outlines
    ├── drafts/               candidate text from the amanuensis   [Compose writes here]
    ├── manuscript/           the work itself                       [controlled write only]
    ├── style-sheet.md        running, the redactor's instrument
    └── .review/              findings, never auto-applied          [Propose/Audit write here]
```

## Who may write where

| Pass | May write to | Never writes to |
|---|---|---|
| Elicit (ingest, interview) | `sources/`, `knowledge-base/`, `voice/` | any `manuscript/` |
| Read (sympathetic read) | nothing | everything |
| Diagnose | nothing | everything |
| Propose (editor) | `works/<id>/.review/` | `manuscript/`, `drafts/` |
| Compose (Amanuensis) | `works/<id>/drafts/` | `manuscript/` |
| Audit (adversarial audit) | `works/<id>/.review/` | `manuscript/` |
| Revise (the controlled write) | `works/<id>/manuscript/` | nothing it was not given |

## The disciplined move

Before writing anything, name the pass you are in and check the table. If the pass has no write access to the target directory, you are in the wrong pass. Route the result to where that pass may write, or stop and go through the controlled write.

The only path into `manuscript/` is `tyf write --decision <id>`, after `tyf propose`, `tyf audit --record`, and `tyf accept --evidence`; `tyf propose --source-ref <id>` binds preserved source fragments into the Gate, and `tyf accept --lines 2,5-8` narrows the accepted subset when the author approves only selected source lines. A read-only pass that "just fixes one thing" in the manuscript has broken the contract.

For a first writing session, `tyf start "Working Title" --language "<writing language>"` creates a normal work plus a safe source/interview packet in `drafts/`, a seed outline, and a `.review/` runway, then prints plain source questions for the agent to ask. `tyf begin <id>` is the lower-level form when a stable id is already needed. `tyf capture <work> --kind source|voice|claim|question --text <text>` appends author-supplied material into the shared source, voice, or knowledge substrate; source captures also mint stable files under `sources/fragments/`. These commands are elicitation and setup paths; none writes to `manuscript/`.

## Rationalization table

| What you will tell yourself | The reality | Do instead |
|---|---|---|
| "It is one small fix, I will edit the manuscript directly." | One uncontrolled write is the whole contract broken. | Route through proposal, audit, decision, and `tyf write --decision`. |
| "Drafts and manuscript are basically the same." | Drafts are candidates; the manuscript is the work. | Compose writes to `drafts/` only. |
| "I will tidy the sources while I am here." | The sources is the source of truth and is read-mostly. | Add derived structure to the knowledge base, leave the raw intact. |
| "I am not sure which pass I am in, I will just write." | Unsure-which-pass is exactly when the contract leaks. | Name the pass first; consult the table. |

## Red flags: stop if you catch yourself

- Writing to `manuscript/` outside `tyf write --decision`.
- Composing into `manuscript/` instead of `drafts/`.
- Editing the raw sources.
- Writing without naming the current pass.

## Commands

```
tyf status            # active work, band, open gates, write-zone reminder
tyf start "Title" --language "<writing language>"
                     # public first-session flow, no manuscript text
tyf begin <work> --language "<writing language>"
                     # lower-level first-session packet with explicit id
tyf capture <work>     # append author source, voice, claim, or question material
tyf doctor            # read-only integrity check, including stray manuscript writes
tyf reflexes          # show visible hooks and git recovery behavior
tyf snapshot -m <msg> # explicit git recovery commit; never automatic
tyf propose <work> --from <draft> [--source-ref <id>]
tyf audit <work> <unit> --record --proposal <proposal-id> --verdict pass --findings-answered
tyf accept <work> <proposal-id> [--lines 2,5-8] --evidence "<author acceptance>"
tyf write <work> --decision <decision-id>
```

## Next

`controlling-manuscript-writes` is the discipline of the controlled write itself. `scheduling-ongoing-work` runs the standing checks that catch contract leaks.
