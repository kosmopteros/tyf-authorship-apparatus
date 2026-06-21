# Core Intent Spine Candidate

Status: review-only candidate.

This document reconstructs candidate product intent for `C:\Users\maste\Documents\TYF`
from deterministic recovery, documentation archaeology, graph evidence,
and optional bounded synthesis. Disagreements remain review items.

## Truth Boundary

This pack is a candidate spine. It does not promote anything into SOLO.
Promotion must happen through reviewed R, F, executable Be, prove-red
evidence, and a green gate.

## Inferred Product Intent

- confidence=0.72 source=docs/LEARN_PASS.md:13, scripts/tyf.py:145 TYF should prefer deterministic checks and use model judgment only for issues that cannot be settled mechanically.
- confidence=0.78 source=skills/keeping-documentation-honest/SKILL.md:23, scripts/tyf.py:145 `tyf check` should hard-fail with exit code 1 when documentation or pack consistency drift is detected.
- confidence=0.74 source=docs/ATTENTIVENESS.md:35, scripts/tyf.py:145 Each `tyf notice` run should reconcile surfaced items against the content-addressed ledger.
- confidence=0.70 source=docs/ATTENTIVENESS.md:36, scripts/tyf.py:145 After `tyf write`, the notice ledger should be updated so already-seen manuscript issues are not re-reported unless their context changes.
- confidence=0.82 source=TYF-manifesto-and-architecture.md:254, scripts/tyf.py:145 `tyf notice` should surface, without modifying files, gaps, trailing fragments, unsourced claims, stale style sheets, and unused registers.

## Observed Structure

- Repo graph observed 114 nodes and 385 edges.
- Recovery summary: docs: 46 (33 intent / 11 assessment / 2 noise, 0 legacy), 38 orphan(s), 0 with broken link(s), 4 discrepancy(ies); 212 requirement + 18 recommendation hypotheses; 0 TODO/FIXME; 0 undocumented module(s), 0 drift candidate(s), 6 large function(s); 4 prioritised Be gap(s)

## Candidate Architecture Claims

- confidence=0.68 source=.opencode/INSTALL.md:13, scripts/tyf.py:145 A correctly installed harness should expose all sixteen TYF skills and route authorship requests through `using-tyf` first.
- confidence=0.80 source=TYF-manifesto-and-architecture.md:236, scripts/tyf.py:145 The `tyf` helper command surface should include init, status, new-work, open, mark-ready, audit, write --confirm, doctor, check, notice, dismiss, and reconcile.
- confidence=0.76 source=cowork/SETUP.md:13, scripts/tyf.py:145 When `scripts/tyf.py` is copied outside the repo, `TYF_PACK_ROOT` should point back to the pack root so `tyf check` can inspect the correct files.
- confidence=0.67 source=docs/PORTABILITY.md:65, scripts/tyf.py:145 Installed harness verification should confirm all sixteen TYF skills are visible and authorship requests route through `using-tyf`.
- confidence=0.72 source=cowork/SETUP.md:37, scripts/tyf.py:145 Cowork install verification should confirm all sixteen skills are visible, `using-tyf` is the first authorship router, and manuscript writes are refused outside `tyf write`.
- confidence=0.66 source=tests/acceptance-and-edge-cases.md:143, scripts/tyf.py:145 `tyf check` should exempt historical/validation files that intentionally preserve older command lists or examples.
- confidence=0.64 source=tests/acceptance-and-edge-cases.md:119, scripts/tyf.py:145 Workspace-affecting commands should scaffold or repair required structure before relying on it.

## Contradictions And Rulings


## Candidate End State

1. One accepted product spine.
2. One explicit source precedence ladder.
3. A reviewed R backlog with dispositions.
4. Executable Be for accepted high-priority claims.
5. A docs disposition pass that demotes stale constitutions.
