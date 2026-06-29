# Evidence Ledger

Status: review-only candidate.

This ledger records where the source-of-truth candidate pack came from
and how to interpret confidence labels.

## Recovery Inputs

- Source: `C:\Users\maste\Documents\TYF`
- Output: `C:\Users\maste\Documents\TYF\.fbs\recovered`
- Summary: docs: 80 (50 intent / 27 assessment / 3 noise, 0 legacy), 70 orphan(s), 0 with broken link(s), 13 discrepancy(ies); 376 requirement + 80 recommendation hypotheses; 0 TODO/FIXME; 4 undocumented module(s), 0 drift candidate(s), 68 large function(s); 14 prioritised Be gap(s)
- Candidates: 40
- Docs scanned: 80
- Legacy docs: 0
- Discrepancies: 13
- Repo graph: 743 nodes, 8786 edges.

## Public Synthesis Stages

Stage 0: source filtering.
Stage 1: deterministic SOLO recovery.
Stage 2: bounded multi-agent or LLM synthesis when enabled.
Stage 3: convergence into a candidate spine and backlog.
Stage 4: operator review.
Stage 5: SOLO promotion into R/F/Be/prove-red.
Stage 6: documentation cleanup and disposition.

## Source Precedence

- High trust: current routing docs, current truth docs, live code, live tests, memory surfaces.
- Medium trust: current README/API/design docs and recent audits.
- Low trust: legacy docs, old handoffs, generated recovery output.
- Noise: runtime output, caches, logs, archives, and generated buckets.

## Confidence Rubric

- 0.95 to 1.00: strong observed or governance fact.
- 0.85 to 0.94: strong candidate with minor drift or missing promotion.
- 0.70 to 0.84: plausible but incomplete or between states.
- 0.50 to 0.69: advisory single-source signal.
- Below 0.50: likely stale, noisy, or speculative.

## Document Disposition Labels

- `canonical-active`: current source of truth after review.
- `candidate-review`: plausible future source, not accepted yet.
- `implemented-lock`: current code behavior needing Be coverage.
- `gap-needs-Be`: documented or intended behavior missing executable proof.
- `contradiction-ruling-needed`: code/docs disagree; operator must rule.
- `historical-demoted`: useful archaeology, not governing.
- `archive-only`: preserve for audit, not active docs.
- `stale-rewrite`: must be rewritten before future agents use it.

## Product Red-Team

- Could `**Code first, model only where intelligence is required.** Every check that can ` be overclaimed from docs/LEARN_PASS.md:13, scripts/tyf.py:883?
- Could `**Command surface is too fragmented.** Standalone commands are fine internally, ` be overclaimed from docs/RC_ARCHITECTURE_RED_TEAM.md:230, scripts/tyf.py:883?
- Could `**Explicitly, hard-fail, as `tyf check`** (exit 1 on drift;` be overclaimed from skills/keeping-documentation-honest/SKILL.md:23, scripts/tyf.py:883?
- Could `**Frame-lock.** The work assumes its own frame and never tests it` be overclaimed from skills/auditing-adversarially/SKILL.md:16, scripts/tyf.py:5057?
- Could `**Per-run (always).** Any time `tyf notice` runs, manually or on a schedule, it ` be overclaimed from docs/ATTENTIVENESS.md:37, scripts/tyf.py:883?
