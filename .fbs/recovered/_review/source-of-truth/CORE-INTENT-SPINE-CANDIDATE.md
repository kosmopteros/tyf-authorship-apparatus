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

- confidence=0.66 source=docs/LEARN_PASS.md:13, scripts/tyf.py:883 **Code first, model only where intelligence is required.** Every check that can be done deterministically already lives in `tyf notice`.
- confidence=0.66 source=docs/RC_ARCHITECTURE_RED_TEAM.md:230, scripts/tyf.py:883 **Command surface is too fragmented.** Standalone commands are fine internally, but `tyf workbench` and `tyf review ...` should become canonical.
- confidence=0.66 source=skills/keeping-documentation-honest/SKILL.md:23, scripts/tyf.py:883 **Explicitly, hard-fail, as `tyf check`** (exit 1 on drift;
- confidence=0.66 source=skills/auditing-adversarially/SKILL.md:16, scripts/tyf.py:5057 **Frame-lock.** The work assumes its own frame and never tests it.
- confidence=0.66 source=docs/ATTENTIVENESS.md:37, scripts/tyf.py:883 **Per-run (always).** Any time `tyf notice` runs, manually or on a schedule, it reconciles against the ledger.

## Observed Structure

- Repo graph observed 743 nodes and 8786 edges.
- Recovery summary: docs: 80 (50 intent / 27 assessment / 3 noise, 0 legacy), 70 orphan(s), 0 with broken link(s), 13 discrepancy(ies); 376 requirement + 80 recommendation hypotheses; 0 TODO/FIXME; 4 undocumented module(s), 0 drift candidate(s), 68 large function(s); 14 prioritised Be gap(s)

## Candidate Architecture Claims


## Contradictions And Rulings


## Candidate End State

1. One accepted product spine.
2. One explicit source precedence ladder.
3. A reviewed R backlog with dispositions.
4. Executable Be for accepted high-priority claims.
5. A docs disposition pass that demotes stale constitutions.
