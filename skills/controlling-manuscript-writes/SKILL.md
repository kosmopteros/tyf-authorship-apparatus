---
name: controlling-manuscript-writes
description: Use whenever a candidate draft, a proposed edit, an accepted change, a revision, a finalization, or an approval decision could alter manuscript text; the controlled write is the only path into the work
---

# Controlling manuscript writes

## Overview

The controlled write is the only path into the manuscript. Candidate text from the amanuensis and proposals from the editor do not become the work until the author accepts them. The controlled write makes commitment #2 mechanical: the system proposes, the author disposes.

In Claude Code this is real tool scoping: read-only passes get no write access to `manuscript/`. In Desktop it is enforced by routing every edit through this one controlled skill.

## The disciplined move

Nothing crosses into `manuscript/` on its own. For every change:

1. **Identify** the candidate or proposal precisely.
2. **Confirm** explicit author acceptance. Silence is not acceptance. "Sounds good" on a batch is not line-by-line acceptance unless the author says so.
3. **Apply** only what was accepted, as a reviewable diff or track-changes.
4. **Log** what changed in the work's record.
5. **Preserve** rejected material only if the author asks.

The controlled write promotes a file under the work's `drafts/` only. To apply an accepted proposal that lives in `.review/`, copy the accepted text into `drafts/` first, then run the write, so every manuscript change has one inspectable source. A rewrite of an existing manuscript file needs `--force`, and even then the write is refused if the file changed out of band since the last logged write (reconcile first).

## Rationalization table

| What you will tell yourself | The reality | Do instead |
|---|---|---|
| "This is clearly better, I will merge it." | "Clearly better" is the rationalization the controlled write exists to stop. | Apply only accepted changes. |
| "The author went quiet, I will take that as yes." | Silence is not approval. | Wait for explicit acceptance. |
| "I improved the wording while applying the accepted change." | An unaccepted change rode in on an accepted one. | Apply the accepted change only; propose the rest separately. |
| "They rejected this, but a reworded version is fine." | Reworking rejected material to sneak it in violates the decision. | Leave it out unless the author revisits it. |
| "Approving each line is slow, I will apply the batch." | Batch-applying without line acceptance is disposing, not proposing. | Confirm the scope the author actually approved. |

## Red flags: stop if you catch yourself

- Auto-applying any proposal.
- Treating silence, "sure", or "looks good" as line-level approval.
- Smuggling an unapproved edit alongside an approved one.
- Rewriting rejected material as a workaround.

## Write record

```markdown
## Write record: <work>
Candidate / proposal:
Decision: accepted | rejected | partially accepted
Applied changes (diff / track-changes):
Rejected changes:
Remaining decisions:
```

## Acceptance and edge cases

This is the highest-stakes skill: the only door into the work. Hold these beyond the happy path:

- **Partial acceptance** ("take 1 and 3, not 2"): apply exactly the accepted subset, never all-or-nothing.
- **No prior acceptance at all:** the request to write is not itself approval. Require explicit confirmation (the `--confirm` contract); silence is never consent.
- **The draft changed or vanished between proposal and write:** verify the source still exists and is current before applying; never write stale or empty content.
- **Concurrent writes** (a scheduled task and a manual write touch one file): every write is logged; `tyf doctor` surfaces a manuscript file whose log is inconsistent, rather than letting last-write-wins clobber silently.
- **The author hand-edited the manuscript outside the gate:** detect the out-of-band change (a manuscript file with no matching write-log entry) and reconcile with the author; do not assume the apparatus owns the file and overwrite their work.

## Next

After applying, the unit is still not done until `auditing-adversarially` has attacked it and the findings are answered.
