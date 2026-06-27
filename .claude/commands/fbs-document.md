---
description: After all Be pass, write a PR-style description of what changed and why. Use as the final step of an FBS flow.
---

# fbs-document

You are acting as the **Documenter** (S → D).

## Preconditions

Run `fbs test` first. If verdict is not OK, refuse — there's nothing to document yet.

## What to produce

Create `.fbs/runs/<timestamp>/description.md` with:

1. One-line summary of what was built.
2. Bulleted list of **Be IDs** that now hold (from `fbs test --json`).
3. Bulleted list of **changed files** under `src/`.
4. Anything notable about the approach or trade-offs.

## Rules

- Do NOT modify `src/`, `.fbs/be/`, or `.fbs/functions/`.
- Keep it short — this is a description, not an essay.
