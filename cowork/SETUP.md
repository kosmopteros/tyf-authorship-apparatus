# TYF in Claude Cowork

Cowork is the primary target for TYF v1. It gives TYF what it needs: direct access to your local files, skills that drop in as the same SKILL.md files, plugins that bundle those skills, and a scheduler for the ongoing-work cadence. Cowork is generally available on macOS and Windows.

One thing to design around: Cowork can make real changes to the files you share, and it has no hard per-subagent read-only scoping. So in Cowork the controlled write is a contract enforced by these instructions and by the helper, not a physical wall. The mitigations below make that contract hold.

## Install

You have two paths.

**A. As a plugin (recommended for sharing).** Package this repository as a Claude plugin and install it from the plugin marketplace, the same way other Cowork plugins are installed. The plugin bundles all eighteen skills.

**B. Manual drop-in.** Copy `skills/*` into the skills location Cowork reads. For the helper, put this repo's `bin/` on your PATH or symlink `bin/tyf` into a PATH directory (`scripts/install.sh` does this for you). Do not copy `scripts/tyf.py` to a bare location on PATH: it locates the pack from its own path, so a loose copy breaks `tyf check`. If you must copy it, set `TYF_PACK_ROOT` to this repo. The skill files load directly.

```
bash scripts/install.sh claude     # or an explicit Cowork skills path
```

## Set up a project

1. Create a Cowork project and point its folder at where your workspace will live.
2. Paste the contents of `cowork/PROJECT_INSTRUCTIONS.md` into the project's instructions. This loads the commitments, the mandatory skill check, and the write zones at the start of every task.
3. In a task, paste: "Use TYF to help me start writing my new book today. Set up the workspace if needed, do not block on a title, preserve any existing material first, show me the orientation and writing runway, structure any minted text source fragment before drafting, and help me begin one candidate passage in drafts with gentle questions and without writing manuscript text."

Claude should load `using-tyf`, run `tyf init` if the folder is not a workspace yet, then run `tyf start` or `tyf start <path>` if a chat export, folder, old workspace, zip, or scaffold arrives. It should read the orientation packet before organizing anything, run `tyf structure work --source-ref <id>` for any minted text source fragment, show `.review/writing-runway.md` and `drafts/candidate-draft.md`, and tell you what files were created in plain language.

## Make the controlled write hold in Cowork

- The helper is the only writer into `manuscript/`. Read-only passes and Compose never write there. Manuscript writes require a proposal record, passing audit record, author review packet, author decision record with `--evidence` and optional `--lines` for selected source-line acceptance, and `tyf write --decision <id>`. A bare `--confirm` is refused.
- The project instructions repeat the write-zone table so every fresh task and every scheduled session reloads it.
- Run `tyf doctor` on a daily schedule to catch any manuscript file that appeared without a write-log entry.

## Set the cadence

Use scheduled tasks for the ongoing-work hooks. See `cowork/SCHEDULED_TASKS.md` for paste-ready templates. Scheduled tasks run while your computer is awake and the desktop app is open; for cadences that should run while the laptop is closed, use cloud Routines where available.

## Verify

In a new task, ask Claude to list its TYF skills and to state the write zones. It should return all eighteen skills, route any authorship request through `using-tyf`, and refuse to write into `manuscript/` outside `tyf write --decision`.
