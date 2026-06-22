---
name: keeping-documentation-honest
description: Use when code, a CLI command, a skill count, the file structure, a manifest, a workflow, an API, the setup process, or any naming changes; before any structural change is considered done; or when a doc may now describe a state that no longer exists
---

# Keeping documentation honest

## Overview

Documentation is part of the apparatus. If it is stale, the apparatus lies. In an agentic system the docs are not reference material that a human may or may not read; they route what future agents and humans do. An outdated README is a poisoned constitution, and a wrong skill count or a renamed command in a context file becomes behavioral law that misleads every session after it.

This is a lifecycle discipline. It connects to the redactor canon, because keeping documentation true is apparatus integrity at the level of the pack and the workspace, not the manuscript.

## The rule

No structural change is complete until the documentation that routes future behavior has been checked. "Checked" means read and either updated or confirmed still accurate. The change is not done before this; the task stays open.

## Enforcement: the deterministic half runs in code

Most of this checklist is mechanically verifiable without a model: skill count, name-matches-directory, dead skill IDs or command names in routing surfaces, context-file divergence, invalid JSON, em-dashes in prose. That half lives in `tyf check`, a zero-token Python check with no dependencies. `tyf reflexes` makes the hook behavior inspectable. It runs two ways:

- **Automatically, warn-only, as a tail step of every mutating `tyf` command** (`init`, `new-work`, `start`, `begin`, `capture`, `propose`, `audit --record`, `accept`, `write`, `mark-ready`). The trigger is wired into the command itself, not into git or author memory, because a workspace may not be a repo and committing is a manual act that can be forgotten. The hook never blocks the action; it surfaces drift at the moment structure changes. Silence it with `TYF_NO_DOC_HOOK=1`.
- **Explicitly, hard-fail, as `tyf check`** (exit 1 on drift; `--no-strict` to warn only). Use it in CI or before publishing.

The deterministic check catches mechanical drift, which is what bites most often. It cannot catch semantic staleness: a paragraph that now describes the wrong workflow in correct-looking prose. That still needs the reading pass below. Code enforces; this skill teaches what to do when the check fails and covers what code cannot see.



## The checklist

```
[ ] README.md
[ ] AGENTS.md / CLAUDE.md / GEMINI.md   (and confirm the three still match)
[ ] manifest.yaml
[ ] package.json
[ ] install scripts
[ ] VALIDATION.md
[ ] docs/PORTABILITY.md
[ ] docs/WORKSPACE_CONTRACT.md
[ ] examples/
[ ] tests/pressure-scenarios.md
```

For a workspace rather than the pack, the routing surfaces are the work's router, `manifest.yaml`, `work.yaml`, `WORKSPACE_STATE.yaml`, the running style sheet, and `ASSUMPTIONS.md`.

## Rationalization table

| What you will tell yourself | The reality | Do instead |
|---|---|---|
| "The code change is done; docs are a separate task." | In an agentic system the docs are the behavior; the change is half-made. | Walk the checklist before declaring done. |
| "It is just a count, no one reads it closely." | A wrong count is a future agent's false fact, repeated with confidence. | Fix it, and prefer a computed count that cannot drift. |
| "I renamed the thing in the code, the docs still convey the idea." | A stale name in a router routes future behavior to the wrong place. | Update every surface that names it; confirm the three context files match. |
| "I updated the README, that is the important one." | The mirrored context files and manifests drift apart silently. | Diff the routing surfaces against each other, not just the obvious one. |
| "I will update the docs later." | Later is when the next agent has already acted on the lie. | The task is not done until the routing docs are true. |

## Red flags: stop if you catch yourself

- Declaring a structural change done without reading the docs it touches.
- Writing a count or a list by hand where it could be computed.
- Updating one router and leaving its mirrors stale.
- Treating documentation as description rather than as law.

## Output shape

```markdown
## Documentation honesty pass
Change made:
Surfaces checked: (each: updated | confirmed-accurate)
Drift found and fixed:
Counts now computed rather than written: yes / no
Verdict: change is done only when every routing surface is true.
```

## Next

This pass belongs at the end of every change, before `auditing-adversarially` signs a unit off. The redactor canon treats documentation as apparatus; see `keeping-the-redactor-canon`. Structural changes to a workspace also touch `working-the-workspace`.
