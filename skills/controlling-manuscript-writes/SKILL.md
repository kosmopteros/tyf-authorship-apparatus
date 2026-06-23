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
2. **Create** a proposal record from the draft: `tyf propose <work> --from <draft>`, adding `--source-ref <id>` for any preserved source fragments that ground the proposal.
3. **Record** an adversarial audit: `tyf audit <work> <unit> --record --proposal <proposal-id> --verdict pass --findings-answered`.
4. **Write** an author review packet: `tyf review <work> <proposal-id>`.
5. **Record** explicit author acceptance: `tyf accept <work> <proposal-id> [--lines 2,5-8 | --patch <diff>] --evidence "<verbatim acceptance or stable reference>"`.
6. **Write** only through the decision: `tyf write <work> --decision <decision-id>`.
7. **Preserve** rejected material only if the author asks.
8. **Adopt direct author edits** when needed: if the author changed `manuscript/` by hand, run `tyf adopt <work> <unit> --evidence "<what happened>"` before proposing against that new base.

The controlled write promotes a file under the work's `drafts/` only. To apply an accepted proposal that lives in `.review/`, copy the accepted text into `drafts/` first, then create a proposal, audit, review packet, decision, and write record, so every manuscript change has one inspectable source. The runtime stores the source hash, current manuscript base hash, source refs, author review packet, acceptance evidence, and accepted scope. It also moves `work.yaml` status through the Gate: proposal sets `drafting`, passing audit sets `audited`, failing audit sets `needs-revision`, author acceptance sets `accepted`, and write sets `written`; acceptance refuses before `audited`, verifies the audit belongs to the same proposal hash, requires a matching author review packet, and write refuses before `accepted`. `--source-ref` binds a proposal to workspace-owned source fragments minted by `tyf capture` or textual `tyf import`; proposal, audit, review, decision, and write records carry those refs forward, and `tyf write`/`tyf doctor` refuse missing or changed fragment files. `--lines` accepts strictly increasing, non-overlapping source line ranges; `--patch` accepts an exact unified diff stored under `.review/` and applies only that diff against the recorded manuscript base; omitting both accepts the whole file. Proposal, audit, review, and decision records are sealed in `.review/record-seals.jsonl`; if a record no longer matches its seal, `tyf write` and `tyf doctor` refuse it. Each controlled write acquires a unit lock in `.review/locks/` before mutating the manuscript destination and releases it afterward; an outstanding lock makes a write refuse and `tyf doctor` report it. If the author review packet, draft file, source fragment, manuscript base, or accepted patch file changes before the write, the write is refused and the change must be reviewed or accepted again from the current material. `tyf adopt` is the explicit reconciliation path for direct author manuscript edits: it preserves a copy under `.review/author-revisions/` and records the edited unit as the new base. Naked `--confirm` and `--force` are refused.

## Rationalization table

| What you will tell yourself | The reality | Do instead |
|---|---|---|
| "This is clearly better, I will merge it." | "Clearly better" is the rationalization the controlled write exists to stop. | Apply only accepted changes. |
| "The author went quiet, I will take that as yes." | Silence is not approval. | Wait for explicit acceptance. |
| "I improved the wording while applying the accepted change." | An unaccepted change rode in on an accepted one. | Apply the accepted change only; propose the rest separately. |
| "They rejected this, but a reworded version is fine." | Reworking rejected material to sneak it in violates the decision. | Leave it out unless the author revisits it. |
| "Approving each line is slow, I will apply the batch." | Batch-applying without line acceptance is disposing, not proposing. | Confirm the scope the author actually approved. |
| "The author edited the manuscript directly, so I should overwrite it with my proposal." | The author owns the manuscript; the apparatus needs to catch up. | Preserve and adopt the direct edit, then propose against the new base. |

## Red flags: stop if you catch yourself

- Auto-applying any proposal.
- Treating silence, "sure", or "looks good" as line-level approval.
- Smuggling an unapproved edit alongside an approved one.
- Rewriting rejected material as a workaround.

## Write record

```markdown
## Write record: <work>
Proposal:
Author review:
Decision:
Acceptance evidence:
Audit:
Applied file:
Source sha256:
Manuscript base sha256:
Source refs:
Accepted scope:
Accepted patch:
Rejected or deferred changes:
```

## Acceptance and edge cases

This is the highest-stakes skill: the only door into the work. Hold these beyond the happy path:

- **Partial acceptance** ("take 1 and 3, not 2"): use `tyf accept --lines 1,3` when the accepted subset maps exactly to source lines. For semantic edits that do not map cleanly to source line ranges, split the accepted subset into its own draft before proposing.
- **Exact hunk acceptance** ("apply this diff, not the whole rewrite"): put the reviewed unified diff under `.review/` and use `tyf accept --patch <diff>`. Do not combine it with `--lines`.
- **Source-grounded material:** if the draft is built from captured source material, include the fragment ids with `tyf propose --source-ref <id>`. A source ref is part of the Gate lineage, not decorative metadata.
- **No author review packet:** run `tyf review <work> <proposal-id>` before accepting. The packet is where the author sees what would change, source support, gaps, audit status, and available choices.
- **No prior acceptance at all:** the request to write is not itself approval. Require a decision record bound to a proposal; silence is never consent.
- **Edited review records:** if a proposal, audit, review, or decision JSON changes after creation, stop. The seal mismatch means the Gate record is no longer trustworthy; re-propose, re-audit, re-review, or re-accept from the current material.
- **The draft changed or vanished between proposal and write:** the source hash must still match the proposal and decision; never write stale or empty content.
- **Concurrent writes** (a scheduled task and a manual write touch one file): the unit lock must be free before writing. If a lock is present, stop and run `tyf doctor`; do not remove it unless you have established no write is active.
- **The author hand-edited the manuscript outside the gate:** run `tyf adopt <work> <unit> --evidence "<what happened>"` if the edit is truly theirs. That preserves the direct edit, records the new base hash, and lets the next proposal proceed without overwriting their work.

## Next

After applying, preserve the write record and continue from the next author source, interview answer, or fresh proposal. Any later change starts a new proposal, audit, review, decision, and write chain.
