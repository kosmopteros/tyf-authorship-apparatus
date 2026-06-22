---
name: initializing-a-workspace
description: Use when starting a new TYF workspace or a new body of work, when a folder has no workspace structure yet, when the author says "let's start", "set up a project", "new book", "new essay series", or when intake needs a place to write its results
---

# Initializing a workspace

## Overview

Initialization scaffolds a workspace before any authorship happens, then runs intake into it. A workspace holds shared substrate at the top (sources, knowledge base, voice registers, redactor canon) and per-work directories beneath, so several works can share knowledge and voice while staying contained.

This is the front door. Until the structure exists, the other passes have nowhere to write.

## The disciplined move

Scaffold first, then elicit, then write the substrate. Do not draft, and do not invent the author's thesis or registers while setting up. Initialization produces empty, labelled structure plus whatever intake legitimately fills.

1. **Scaffold.** Create the `workspace/` tree (see `working-the-workspace`). Prefer the helper: `tyf init <name>`. Init is idempotent: it creates only missing structure and never overwrites existing files, so it safely heals a partial workspace. It also initializes the apparatus memory database `.tyf/ledger.db` (stdlib SQLite). Run `tyf doctor --repair` any time to restore missing structure. Write `WORKSPACE_STATE.yaml`, `manifest.yaml`, `ASSUMPTIONS.md`, and the router/standing-instructions file.
2. **Run intake.** Invoke `ingesting-sources` for any material the author brings, then `interviewing-the-author` for tacit knowledge, thesis, and registers.
3. **Seed the substrate.** Write at least one register to the voice registers via `managing-voice`, seed the knowledge base via `structuring-knowledge`, and start the redactor canon and the running style sheet via `keeping-the-redactor-canon`.
4. **Start the first work.** For a book that needs to start today, prefer `tyf start "Working Title" --language "<writing language>"`. It creates `works/<id>/`, marks it active, records the writing language in `work.yaml`, and writes the first-session source packet, seed outline, and review runway. It also prints the first source questions the agent should ask. Use `tyf begin <id>` only when a stable id is already required.
5. **Set state.** Record the active work and band in `WORKSPACE_STATE.yaml`, gates closed. If the author wants recoverability and recall, initialize git for the workspace and use `tyf snapshot --message "..."` at session boundaries. TYF may report git status, but it never commits silently.

Intake can pause and resume across days. If it does, leave `ASSUMPTIONS.md` and `WORKSPACE_STATE.yaml` honest about what is done and what is still open.

## Rationalization table

| What you will tell yourself | The reality | Do instead |
|---|---|---|
| "The author wants to write now, skip setup." | Without the structure, every later pass freelances and state is lost. | Scaffold first; it takes one command. |
| "I will pick sensible default registers." | Default registers are your voice wearing the author's name. | Elicit at least one register in The author interview; never invent one. |
| "One folder of notes is enough, no workspace needed." | Shared substrate is what keeps several works coherent. | Create the full tree even for a single work; v0.1 ships workspace-aware. |
| "I can fill ASSUMPTIONS later." | Unstated assumptions are where the project quietly drifts. | Write what you assumed during setup, and update it as the author corrects you. |

## Red flags: stop if you catch yourself

- Drafting prose during setup.
- Choosing the thesis, structure, or registers for the author.
- Leaving the workspace half-scaffolded with no state file.
- Skipping the redactor canon and style sheet.

## Commands

```
tyf init <workspace-name>       # scaffold the tree and state files
tyf start "Working Title" --language "<writing language>"
                               # create the first-session packet and ask source questions
tyf status                      # confirm what exists
tyf reflexes                    # show hooks and git recovery behavior
tyf snapshot -m "first session" # explicit git recovery point
```

Do not present this block as the author's first task. In Codex or Cowork, run it for them when you have permission to work in the shared folder, then summarize the result in plain language.

## Next

After initialization, `working-the-workspace` governs where each pass reads and writes, and `scheduling-ongoing-work` sets the cadence for the iterative phase.
