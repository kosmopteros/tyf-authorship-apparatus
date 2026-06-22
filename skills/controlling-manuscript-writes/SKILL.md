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
2. **Create** a proposal record from the draft: `tyf propose <work> --from <draft>`.
3. **Record** an adversarial audit: `tyf audit <work> <unit> --record --proposal <proposal-id> --verdict pass --findings-answered`.
4. **Record** explicit author acceptance: `tyf accept <work> <proposal-id> [--lines 2,5-8] --evidence "<verbatim acceptance or stable reference>"`.
5. **Write** only through the decision: `tyf write <work> --decision <decision-id>`.
6. **Preserve** rejected material only if the author asks.

The controlled write promotes a file under the work's `drafts/` only. To apply an accepted proposal that lives in `.review/`, copy the accepted text into `drafts/` first, then create a proposal, audit, decision, and write record, so every manuscript change has one inspectable source. The runtime stores the source hash, current manuscript base hash, acceptance evidence, and accepted scope. `--lines` accepts strictly increasing, non-overlapping source line ranges; omitting it accepts the whole file. If either file hash changes before the write, the write is refused and the change must be re-proposed. Naked `--confirm` and `--force` are refused.

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
Proposal:
Decision:
Acceptance evidence:
Audit:
Applied file:
Source sha256:
Manuscript base sha256:
Accepted scope:
Rejected or deferred changes:
```

## Acceptance and edge cases

This is the highest-stakes skill: the only door into the work. Hold these beyond the happy path:

- **Partial acceptance** ("take 1 and 3, not 2"): use `tyf accept --lines 1,3` when the accepted subset maps exactly to source lines. For semantic edits that do not map cleanly to source line ranges, split the accepted subset into its own draft before proposing.
- **No prior acceptance at all:** the request to write is not itself approval. Require a decision record bound to a proposal; silence is never consent.
- **The draft changed or vanished between proposal and write:** the source hash must still match the proposal and decision; never write stale or empty content.
- **Concurrent writes** (a scheduled task and a manual write touch one file): every write is logged; `tyf doctor` surfaces a manuscript file whose log is inconsistent, rather than letting last-write-wins clobber silently.
- **The author hand-edited the manuscript outside the gate:** detect the out-of-band change or base-hash mismatch and reconcile with the author; do not assume the apparatus owns the file and overwrite their work.

## Next

After applying, the unit is still not done until `auditing-adversarially` has attacked it and the findings are answered.
