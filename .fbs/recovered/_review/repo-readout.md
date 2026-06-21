# Recovery Repo Readout

Review-only advisory artifact. No requirements were promoted, marked done, or accepted.

- truth=observed source=recovery-source `C:\Users\maste\Documents\TYF`
- truth=observed source=recovery-output `C:\Users\maste\Documents\TYF\.fbs\recovered`
- truth=observed source=doc-archaeology `docs: 46 (33 intent / 11 assessment / 2 noise, 0 legacy), 38 orphan(s), 0 with broken link(s), 4 discrepancy(ies); 212 requirement + 18 recommendation hypotheses; 0 TODO/FIXME; 0 undocumented module(s), 0 drift candidate(s), 6 large function(s); 4 prioritised Be gap(s)`

## Inferred Repo Intent

- truth=inferred confidence=0.72 source=docs/LEARN_PASS.md:13,scripts/tyf.py:145 `TYF should prefer deterministic checks and use model judgment only for issues that cannot be settled mechanically.`
- truth=inferred confidence=0.78 source=skills/keeping-documentation-honest/SKILL.md:23,scripts/tyf.py:145 ``tyf check` should hard-fail with exit code 1 when documentation or pack consistency drift is detected.`
- truth=inferred confidence=0.74 source=docs/ATTENTIVENESS.md:35,scripts/tyf.py:145 `Each `tyf notice` run should reconcile surfaced items against the content-addressed ledger.`

## Evidence-Backed Strengths

- truth=observed source=repo-graph nodes=114 edges=385
- truth=inferred confidence=0.72 kind=recovered-intent source=docs/LEARN_PASS.md:13,scripts/tyf.py:145 `TYF should prefer deterministic checks and use model judgment only for issues th`
- truth=inferred confidence=0.78 kind=recovered-intent source=skills/keeping-documentation-honest/SKILL.md:23,scripts/tyf.py:145 ``tyf check` should hard-fail with exit code 1 when documentation or pack consist`
- truth=inferred confidence=0.74 kind=recovered-intent source=docs/ATTENTIVENESS.md:35,scripts/tyf.py:145 `Each `tyf notice` run should reconcile surfaced items against the content-addres`
- truth=inferred confidence=0.70 kind=recovered-intent source=docs/ATTENTIVENESS.md:36,scripts/tyf.py:145 `After `tyf write`, the notice ledger should be updated so already-seen manuscrip`

## Gaps And Risks

- truth=observed source=doc-inventory 38 orphan doc(s) need review
- truth=observed source=cowork/SETUP.md,docs/ATTENTIVENESS.md discrepancy `tyf write`: conflicting polarity (affirm vs negate)
- truth=observed source=TYF-manifesto-and-architecture.md,docs/ATTENTIVENESS.md,docs/LEARN_PASS.md discrepancy `tyf notice`: conflicting polarity (affirm vs negate)
- truth=observed source=README.md,tests/acceptance-and-edge-cases.md discrepancy `conflict`: conflicting polarity (affirm vs negate)
- truth=observed source=skills/editing-faithfully/SKILL.md,skills/managing-voice/SKILL.md,tests/acceptance-and-edge-cases.md discrepancy `controlling-manuscript-writes`: conflicting polarity (affirm vs negate)
- truth=observed source=code-scan 3 god-object candidate(s)
- truth=missing-evidence source=skills/controlling-manuscript-writes/SKILL.md:59 gap=unmapped `--confirm` - Require explicit confirmation (the `--confirm` contract);
- truth=missing-evidence source=skills/controlling-manuscript-writes/SKILL.md:58 gap=unmapped `all-or-nothing` - **Partial acceptance** ("take 1 and 3, not 2"): apply exactly the accepted subset, never all-or-nothing.
- truth=missing-evidence source=.claude/commands/fbs-formulate.md:78 gap=unmapped `pass` - scenario + source files and return `pass`/`fail`.
- truth=missing-evidence source=skills/controlling-manuscript-writes/SKILL.md:60 gap=unmapped `stale` - never write stale or empty content.
- truth=missing-evidence source=cowork/SCHEDULED_TASKS.md:3 gap=unmapped `cloud` - Use cloud Routines for cadences that should run while the laptop is closed.

## Recommended Review Queue

- truth=missing-evidence source=skills/controlling-manuscript-writes/SKILL.md:59 review `--confirm` (unmapped)
- truth=missing-evidence source=skills/controlling-manuscript-writes/SKILL.md:58 review `all-or-nothing` (unmapped)
- truth=missing-evidence source=.claude/commands/fbs-formulate.md:78 review `pass` (unmapped)
- truth=missing-evidence source=skills/controlling-manuscript-writes/SKILL.md:60 review `stale` (unmapped)
- truth=missing-evidence source=cowork/SCHEDULED_TASKS.md:3 review `cloud` (unmapped)

## Product Red-Team

- truth=speculative source=skills/controlling-manuscript-writes/SKILL.md:59 Could `--confirm` be an overclaimed promise without executable evidence?
- truth=speculative source=skills/controlling-manuscript-writes/SKILL.md:58 Could `all-or-nothing` be an overclaimed promise without executable evidence?
- truth=speculative source=.claude/commands/fbs-formulate.md:78 Could `pass` be an overclaimed promise without executable evidence?
- truth=speculative source=scripts/tyf.py:354 Could `gather_notices` concentrate too much behaviour for safe agent iteration?
- truth=speculative source=docs/LEARN_PASS.md:13,scripts/tyf.py:145 What would falsify `TYF should prefer deterministic checks and use model judgment only for issues th`? counter=doc-side intent has no recovered behaviour cluster
- truth=speculative source=skills/keeping-documentation-honest/SKILL.md:23,scripts/tyf.py:145 What would falsify ``tyf check` should hard-fail with exit code 1 when documentation or pack consist`? counter=doc-side intent has no recovered behaviour cluster
- truth=speculative source=docs/ATTENTIVENESS.md:35,scripts/tyf.py:145 What would falsify `Each `tyf notice` run should reconcile surfaced items against the content-addres`? counter=doc-side intent has no recovered behaviour cluster

## Truth Boundary

- truth=observed means deterministic recovery counted or found the item.
- truth=inferred means SOLO connected docs, graph paths, or candidate R evidence.
- truth=missing-evidence means a documented or structural claim lacks enough backing evidence.
- truth=speculative means a review question or red-team hypothesis, not a verdict.
- No requirements were promoted; use `fbs requirements add` only after human review.
