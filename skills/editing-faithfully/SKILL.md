---
name: editing-faithfully
description: Use when the author asks you to improve, edit, tighten, rewrite, line-edit, or polish existing text; covers proposing specific edits and, only after explicit approval, applying them
---

# Editing faithfully

## Overview

The editor has two stances, and they are separate by design.

- **Propose:** suggest specific edits. Apply nothing. Write findings to the review log.
- **Revise:** apply edits the author has accepted. This is controlled and writes reviewable diffs to the manuscript.

The default stance is Propose. Crossing into Revise requires `controlling-manuscript-writes`.

## The disciplined move

**Read the register first.** Edits preserve the author's voice and register. Identify the register from the voice registers before proposing anything. Preserve productive strangeness; do not standardize toward generic polish.

**Propose, do not dispose.** Every edit is a suggestion with a reason. The author decides. You never apply an edit because it "seems obviously better."

**Separate proposal from application.** Proposing writes to `.review/`. Applying writes to `manuscript/`, and only through the controlled write, as a reviewable diff or track-changes. There is no shortcut between the two.

## Redactor layer (Milchin)

Every proposal must conform to the redactor canon at its band, and every accepted decision is recorded in the work's running style sheet so it survives to later chapters. See `keeping-the-redactor-canon`.

- micro: honor punctuation and typographic finish.
- macro: keep terminology canonical, cross-references resolving, transitions sound.
- meta: read the style sheet before proposing; append new decisions after.

Where voice and canon seem to conflict, the register fence wins on voice and the canon wins on integrity. Surface the tension; do not resolve it silently.

## Rationalization table

| What you will tell yourself | The reality | Do instead |
|---|---|---|
| "This edit is obviously better, I will just make it." | "Obviously better" is the most common voice-eraser and write-control-skipper. | Propose it with a reason; let the author accept it through the controlled write. |
| "Improve means make it standard and clean." | Standard and clean can flatten the exact voice the author wants. | Edit within the register; keep the anchors and the quirks. |
| "I improved a few lines while I was answering." | If it altered manuscript content, it bypassed the controlled write. | Move every applied change back through `controlling-manuscript-writes`. |
| "The author said improve, so silence is approval to apply." | Silence is not approval. | Apply only what is explicitly accepted. |
| "This claim is weak, I will fix it by softening the prose." | Polishing an unsupported claim hides the defect. | Flag the claim to the knowledge base; do not paper over it with style. |

## Red flags: stop if you catch yourself

- Applying an edit the author did not accept.
- Editing toward generic professionalism without naming the register.
- Treating silence or "sure" as write approval.
- Smoothing prose over an unsupported claim.

## Output shape

```markdown
## Editorial proposals: <work> / <span>
Register honored:
Proposal 1: <location>: change, reason
Proposal 2: ...
(Nothing applied. Acceptance required via the controlled write.)
```

## Acceptance and edge cases

- **Silence or a batch "looks good":** neither is line-by-line acceptance. Confirm the actual scope approved before anything is applied.
- **An edit that improves prose but hides a weak claim:** flag the claim to `structuring-knowledge`; do not let style smooth over an integrity defect.
- **A rejected edit you are tempted to reword and reintroduce:** leave it out unless the author revisits it; rewording a rejection to sneak it past is a violation of the decision.
- **Register not yet identified:** do not edit toward generic polish. Identify the register first, or stay in diagnosis only.

## Next

Accepted proposals go through `controlling-manuscript-writes` to become manuscript text. Before a unit is called done, run `auditing-adversarially`.
