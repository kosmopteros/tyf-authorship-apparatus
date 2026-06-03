# The Learn pass (opt-in, unwired in v0.1)

The deterministic attentiveness layer (`tyf notice`) catches what code can see: gaps, unfinished lines, unsourced claims, a style sheet lagging the manuscript, an unused register. It spends no tokens and runs anywhere.

There is a second kind of drift code cannot see: *semantic* staleness. A paragraph in chapter nine that quietly contradicts a claim logged in chapter two. A manuscript whose argument has moved past what the outline still asserts. Prose that has drifted out of its declared register in a way no string match will catch. Surfacing that needs a reading pass, which means a model, which means tokens. This document specifies that pass. It is deliberately **not wired into anything** in v0.1: nothing reads your corpus or spends tokens in the background until you choose to run it.

## Principles it must obey

It inherits TYF's commitments without exception.

- **Surface, never modify.** The Learn pass is the attentive amanuensis with a reading habit. Its only output is notices appended to `.proposals/`. It never edits the manuscript, the redactor canon, the voice registers, or the knowledge base. Healing is always a human-gated act.
- **Bounded, not background-autonomous.** It runs on an explicit schedule the author sets, reads only the diff since its last run, and stops. It is not an always-on agent watching your files.
- **Code first, model only where intelligence is required.** Every check that can be done deterministically already lives in `tyf notice`. The Learn pass is reserved for the genuinely semantic questions below, nothing else.
- **Cheap by construction.** Diff-scoped input, a small fixed set of questions, a hard cap on tokens per run. If the diff is empty, it does not run.

## What it is allowed to ask the model

Only questions that are semantic and cannot be answered by string or timestamp logic:

1. Does any new or changed manuscript passage contradict a claim in the claims index, or another passage elsewhere in the work?
2. Has the argument in the manuscript moved past what the outline still asserts?
3. Does any passage read as drifted out of its declared register, in a way the deterministic AI-tell scan did not flag?
4. Is there tacit knowledge implied by a change (a new term, a new commitment) that is not yet recorded in the redactor canon or the knowledge base?

Each answer becomes a notice: "chapter nine appears to contradict claim C014; which holds?" handed back to the author. Never a fix.

## Sketch of a faithful run (pseudocode, not wired)

```
if not author_enabled_learn_pass: stop          # opt-in only
diff = changed_units_since_last_run()            # diff-scoped, not whole corpus
if diff is empty: stop                           # no tokens spent on nothing
for unit in diff (up to a fixed cap):
    notices += model_ask(SEMANTIC_QUESTIONS, context=unit + relevant_claims_and_register)
append notices to .proposals/notices.md          # surface only
# never writes to manuscript/, redactor-canon/, voice/, knowledge-base/
```

## How to enable it (when you choose to)

Wiring is intentionally left to the author so that turning on token spend is a deliberate act:

1. Implement `model_ask` against your harness (in Cowork, a scheduled task whose prompt is the four questions above, scoped to the diff).
2. Point it at `.proposals/notices.md` as its only output.
3. Schedule it at whatever cadence suits the work (see `cowork/SCHEDULED_TASKS.md`).
4. Confirm it has no write path to any manuscript, canon, voice, or knowledge-base file. If it can write to those, it is not the Learn pass; it is an autonomous editor, which TYF does not sanction.

Until you do this, `tyf notice` is the whole attentiveness layer, and it is fully faithful on its own.
