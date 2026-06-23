---
name: initializing-a-workspace
description: Use when starting a new TYF workspace or a new body of work, when a folder has no workspace structure yet, when the author says "let's start", "set up a project", "new book", "new essay series", or when intake needs a place to write its results
---

# Initializing a workspace

## Overview

Initialization scaffolds a workspace before any authorship happens, then runs intake into it. For the beta launch, a workspace is a single book folder: shared substrate, outline, drafts, manuscript, style sheet, and review records live together at the root.

This is the front door. Until the structure exists, the other passes have nowhere to write.

## The disciplined move

Scaffold first, then elicit, then write the substrate. Do not draft, and do not invent the author's thesis or registers while setting up. Initialization produces empty, labelled structure plus whatever intake legitimately fills.

1. **Scaffold.** Create the `workspace/` tree (see `working-the-workspace`). Prefer the helper: `tyf init` in the book folder, or `tyf init <name>` near it. Init is idempotent: it creates only missing structure and never overwrites existing files, so it safely heals a partial workspace. It also initializes apparatus memory: `.tyf/events.jsonl` for the hash-chained action journal and `.tyf/ledger.db` for the derived notice index. Run `tyf doctor --repair` any time to restore missing structure. Write `WORKSPACE_STATE.yaml`, `manifest.yaml`, `ASSUMPTIONS.md`, and the router/standing-instructions file.
2. **Run intake.** Invoke `ingesting-sources` for any material the author brings, then `interviewing-the-author` for tacit knowledge, thesis, and registers.
3. **Seed the substrate.** Write at least one register to the voice registers via `managing-voice`, seed the knowledge base via `structuring-knowledge`, and start the redactor canon and the running style sheet via `keeping-the-redactor-canon`.
4. **Open the writing runway.** For a book that needs a first writing session, use `tyf start`; if the author brings existing material, run `tyf start <path>`. The helper creates or reuses the root single work, records any supplied title/language, creates or reuses `sources/interviews/work-first-session.md`, preserves arrivals through the import lane, writes `.review/writing-runway.md`, and creates `drafts/candidate-draft.md` for candidate prose.
5. **Preserve arrivals.** `tyf start <path>` already preserves a provided path. If material arrives later, run `tyf import <path>` before analyzing it. Text/chat imports preserve the raw file and can mint source fragments. Zip and folder imports are containment-first: read the orientation packet, classify contents, propose an organization principle, and ask before moving anything into sources, knowledge, voice, drafts, or manuscript.
6. **Set state.** Record the active work and band in `WORKSPACE_STATE.yaml`, gates closed. If the author wants recoverability and recall, initialize git for the workspace and use `tyf snapshot --message "..."` at session boundaries. TYF may report git status, but it never commits silently.

Intake can pause and resume across days. If it does, leave `ASSUMPTIONS.md` and `WORKSPACE_STATE.yaml` honest about what is done and what is still open.

## Rationalization table

| What you will tell yourself | The reality | Do instead |
|---|---|---|
| "The author wants to write now, skip setup." | Without the structure, every later pass freelances and state is lost. | Scaffold first; it takes one command. |
| "I will pick sensible default registers." | Default registers are your voice wearing the author's name. | Elicit at least one register in The author interview; never invent one. |
| "One folder of notes is enough, no workspace needed." | A book folder needs visible source, draft, review, and manuscript boundaries. | Create the full tree once; TYF is workspace-aware without making the author manage multiple works. |
| "I can fill ASSUMPTIONS later." | Unstated assumptions are where the project quietly drifts. | Write what you assumed during setup, and update it as the author corrects you. |

## Red flags: stop if you catch yourself

- Drafting prose during setup.
- Choosing the thesis, structure, or registers for the author.
- Leaving the workspace half-scaffolded with no state file.
- Skipping the redactor canon and style sheet.

## Commands

```
tyf init                        # scaffold this book folder
tyf init <workspace-name>       # or scaffold a named book folder nearby
tyf start [path]                # preserve an optional arrival and open the writing runway
tyf start --title "<title>" --language "<writing language>"
tyf import <path>               # preserve existing material and create an orientation packet
tyf resume                      # recover active work, state, prompts, and next move
tyf status                      # confirm what exists
tyf reflexes                    # show hooks and git recovery behavior
tyf snapshot -m "first session" # explicit git recovery point
```

Do not present this block as the author's first task. In Codex or Cowork, run it for them when you have permission to work in the shared folder, then summarize the result in plain language.

## Next

After initialization, `working-the-workspace` governs where each pass reads and writes, and `scheduling-ongoing-work` sets the cadence for the iterative phase.
