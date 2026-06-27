---
description: Generate or modify code under src/ to satisfy current Be specs. Use after /fbs-formulate or after a failing /fbs-status.
---

# fbs-synthesize

You are acting as the **Synthesizer** in an FBS-driven flow.

## Step 1 — read state

Run `fbs test --json` to get current Be↔Bs verdict.
Read failing Be in `.fbs/be/`. Read corresponding code in `src/` (or note it's missing).

## Step 2 — make minimal edits

Use Edit/Write to modify code in `src/` so that failing Be will pass.
Stay focused on the failing Be — do not refactor unrelated code.

## Rules

- Do NOT modify files under `.fbs/be/`, `.fbs/functions/`, or `.fbs/store/`.
- Do not weaken or skip Be specs — that's Reformulator-2's role (`/fbs-reformulate`).
- Do not add dependencies without need.

## Step 3 — verify

Run `fbs test` again. Report the new verdict to the user.
If still failing after a focused attempt, suggest `/fbs-reformulate`.
