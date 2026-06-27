---
description: When repeated /fbs-synthesize attempts fail to close a Be↔Bs gap, weaken or split the failing Be (Reformulator-2). Do NOT use for changing Function — that requires human approval (Reformulator-3).
---

# fbs-reformulate

You are acting as **Reformulator-2** (Be → Be') in an FBS-driven flow.
Multiple S→S' attempts have failed for the same gap. The failing Be may be over-constrained.

## Step 1 — diagnose

Run `fbs test --json` and read the failing Be in `.fbs/be/`.
Decide one of:

- **Weaken the spec** (relax thresholds).
- **Split the spec** (one Be was conflating two behaviours).
- **Mark `xfail` with a reason** (legitimate impossibility).

## Step 2 — edit Be

Edit the Be file in `.fbs/be/`. Document the reason inline as a comment near the changed spec.

## Rules

- Weakening Be is a real architectural decision. Be conservative.
- Do not delete a spec without an explicit comment-rationale.
- Do not modify `.fbs/functions/` — changing F is Reformulator-3, which requires the **human**, not the agent.
- Do not modify `src/` — Synthesizer reacts to the new Be on next run.

## Step 3 — re-run

Run `fbs test` to confirm the new Be passes (or fails differently). Report to the user.
