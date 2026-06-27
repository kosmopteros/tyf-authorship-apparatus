# Evidence Ledger

Status: review-only candidate.

This ledger records where the source-of-truth candidate pack came from
and how to interpret confidence labels.

## Recovery Inputs

- Source: `C:\Users\maste\Documents\TYF`
- Output: `C:\Users\maste\Documents\TYF\.fbs\recovered`
- Summary: docs: 46 (33 intent / 11 assessment / 2 noise, 0 legacy), 38 orphan(s), 0 with broken link(s), 4 discrepancy(ies); 212 requirement + 18 recommendation hypotheses; 0 TODO/FIXME; 0 undocumented module(s), 0 drift candidate(s), 6 large function(s); 4 prioritised Be gap(s)
- Candidates: 27
- Docs scanned: 46
- Legacy docs: 0
- Discrepancies: 4
- Repo graph: 114 nodes, 385 edges.

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

- Could `TYF should prefer deterministic checks and use model judgment only for issues th` be overclaimed from docs/LEARN_PASS.md:13, scripts/tyf.py:145?
- Could ``tyf check` should hard-fail with exit code 1 when documentation or pack consist` be overclaimed from skills/keeping-documentation-honest/SKILL.md:23, scripts/tyf.py:145?
- Could `Each `tyf notice` run should reconcile surfaced items against the content-addres` be overclaimed from docs/ATTENTIVENESS.md:35, scripts/tyf.py:145?
- Could `After `tyf write`, the notice ledger should be updated so already-seen manuscrip` be overclaimed from docs/ATTENTIVENESS.md:36, scripts/tyf.py:145?
- Could `TYF's pressure scenarios should be run against real agent/subagent harnesses bef` be overclaimed from TYF-manifesto-and-architecture.md:288, scripts/tyf.py:145?
