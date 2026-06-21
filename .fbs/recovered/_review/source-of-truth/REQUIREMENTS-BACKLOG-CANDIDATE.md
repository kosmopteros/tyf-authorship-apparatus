# Requirements And Backlog Candidate

Status: review-only candidate.

This file converts recovered intent into reviewable requirements and
backlog items. It is not a SOLO requirements register yet.

## Status Values

- `implemented-lock`: code mostly appears to implement the claim; promote Be to lock it.
- `gap-needs-Be`: intent appears plausible but executable behaviour is missing or weak.
- `contradiction-ruling-needed`: sources disagree; the operator must rule.
- `candidate-review`: plausible recovered or synthesized intent; not accepted.
- `stale-rewrite`: docs need rewrite or demotion before agents rely on them.

## Candidate Requirements

| ID | Requirement | Status | Confidence | Primary evidence |
| --- | --- | --- | --- | --- |
| R-001 | TYF should prefer deterministic checks and use model judgment only for issues that cannot be settled mechanically. | gap-needs-Be | 0.72 | docs/LEARN_PASS.md:13, scripts/tyf.py:145 |
| R-002 | `tyf check` should hard-fail with exit code 1 when documentation or pack consistency drift is detected. | gap-needs-Be | 0.78 | skills/keeping-documentation-honest/SKILL.md:23, scripts/tyf.py:145 |
| R-003 | Each `tyf notice` run should reconcile surfaced items against the content-addressed ledger. | gap-needs-Be | 0.74 | docs/ATTENTIVENESS.md:35, scripts/tyf.py:145 |
| R-004 | After `tyf write`, the notice ledger should be updated so already-seen manuscript issues are not re-reported unless their context changes. | gap-needs-Be | 0.70 | docs/ATTENTIVENESS.md:36, scripts/tyf.py:145 |
| R-005 | TYF's pressure scenarios should be run against real agent/subagent harnesses before the pack is described as production-bulletproof. | candidate-review | 0.75 | TYF-manifesto-and-architecture.md:288, scripts/tyf.py:145 |
| R-006 | `tyf notice` should surface, without modifying files, gaps, trailing fragments, unsourced claims, stale style sheets, and unused registers. | gap-needs-Be | 0.82 | TYF-manifesto-and-architecture.md:254, scripts/tyf.py:145 |
| R-007 | The manuscript revise/write boundary should require explicit author action through `tyf write --confirm`. | gap-needs-Be | 0.84 | TYF-manifesto-and-architecture.md:173, scripts/tyf.py:145 |
| R-008 | A correctly installed harness should expose all sixteen TYF skills and route authorship requests through `using-tyf` first. | candidate-review | 0.68 | .opencode/INSTALL.md:13, scripts/tyf.py:145 |
| R-009 | The `tyf` helper command surface should include init, status, new-work, open, mark-ready, audit, write --confirm, doctor, check, notice, dismiss, and reconcile. | gap-needs-Be | 0.80 | TYF-manifesto-and-architecture.md:236, scripts/tyf.py:145 |
| R-010 | When `scripts/tyf.py` is copied outside the repo, `TYF_PACK_ROOT` should point back to the pack root so `tyf check` can inspect the correct files. | candidate-review | 0.76 | cowork/SETUP.md:13, scripts/tyf.py:145 |
| R-011 | Installed harness verification should confirm all sixteen TYF skills are visible and authorship requests route through `using-tyf`. | candidate-review | 0.67 | docs/PORTABILITY.md:65, scripts/tyf.py:145 |
| R-012 | Cowork install verification should confirm all sixteen skills are visible, `using-tyf` is the first authorship router, and manuscript writes are refused outside `tyf write`. | candidate-review | 0.72 | cowork/SETUP.md:37, scripts/tyf.py:145 |
| R-013 | TYF should preserve project lineage and rationale so contributors can challenge accepted and rejected design decisions. | candidate-review | 0.62 | TYF-manifesto-and-architecture.md:53, scripts/tyf.py:145 |
| R-014 | TYF should keep machine-only bookkeeping in `.tyf/ledger.db`, including notice statuses, dismissals, timestamps, and an append-only event log for init/write/mark-ready/dismiss/repair. | gap-needs-Be | 0.76 | TYF-manifesto-and-architecture.md:234, scripts/tyf.py:145 |
| R-015 | `tyf init` and `tyf doctor --repair` should be idempotent, creating only missing workspace structure without clobbering existing authored files. | gap-needs-Be | 0.80 | tests/acceptance-and-edge-cases.md:116, scripts/tyf.py:145 |
| R-016 | `tyf check` should exempt historical/validation files that intentionally preserve older command lists or examples. | gap-needs-Be | 0.66 | tests/acceptance-and-edge-cases.md:143, scripts/tyf.py:145 |
| R-017 | TYF workspace operations should preserve per-work isolation. | gap-needs-Be | 0.70 | tests/acceptance-and-edge-cases.md:126, scripts/tyf.py:145 |
| R-018 | When manuscript files and write logs disagree, `tyf doctor` should surface the inconsistency. | gap-needs-Be | 0.73 | tests/acceptance-and-edge-cases.md:106, scripts/tyf.py:145 |
| R-019 | When TYF is uncertain about a write boundary, not writing should be the safe default. | gap-needs-Be | 0.69 | tests/acceptance-and-edge-cases.md:127, scripts/tyf.py:145 |
| R-020 | TYF should resolve real paths and refuse writes outside the workspace root. | gap-needs-Be | 0.78 | tests/acceptance-and-edge-cases.md:125, scripts/tyf.py:145 |
| R-021 | Workspace-affecting commands should scaffold or repair required structure before relying on it. | gap-needs-Be | 0.64 | tests/acceptance-and-edge-cases.md:119, scripts/tyf.py:145 |
| R-022 | Source material areas should be treated as read-mostly, with writes reserved for explicit ingest or author-approved operations. | gap-needs-Be | 0.66 | tests/acceptance-and-edge-cases.md:128, scripts/tyf.py:145 |
| R-023 | Harnesses with post-turn hooks may call `tyf notice --peek` or append intent capture to `.proposals/`, while TYF itself should not claim this portability universally. | candidate-review | 0.68 | docs/ATTENTIVENESS.md:37, scripts/tyf.py:145 |
| R-024 | `tyf write` should require `--confirm` as the concrete signal of explicit author acceptance. | gap-needs-Be | 0.86 | cowork/SETUP.md:27, scripts/tyf.py:145 |
| R-025 | The documentation-honesty check should run warn-only after mutating `tyf` commands and hard-fail when invoked as standalone `tyf check`. | gap-needs-Be | 0.74 | VALIDATION.md:6, scripts/tyf.py:145 |
| R-026 | The existing validation evidence records an end-to-end POSIX exercise of core `tyf` helper commands, including write refusal without `--confirm` and success with it. | candidate-review | 0.70 | VALIDATION.md:13, scripts/tyf.py:145 |
| R-027 | Validation evidence should demonstrate that introduced documentation drift is warned after mutating commands and fails standalone `tyf check`. | candidate-review | 0.72 | VALIDATION.md:6, scripts/tyf.py:145 |

## P0 Promotion Candidates

1. R-002 `tyf check` should hard-fail with exit code 1 when documentation or pack consist
2. R-005 TYF's pressure scenarios should be run against real agent/subagent harnesses bef
3. R-006 `tyf notice` should surface, without modifying files, gaps, trailing fragments,
4. R-007 The manuscript revise/write boundary should require explicit author action throu
5. R-009 The `tyf` helper command surface should include init, status, new-work, open, ma
6. R-010 When `scripts/tyf.py` is copied outside the repo, `TYF_PACK_ROOT` should point b

## Rulings Needed Before Implementation Work

No contradiction-ruling-needed candidates were ranked.

## Backlog From Accepted Direction

1. --confirm - Require explicit confirmation (the `--confirm` contract);
2. all-or-nothing - **Partial acceptance** ("take 1 and 3, not 2"): apply exactly the accepted subset, never all-or-nothing.
3. pass - scenario + source files and return `pass`/`fail`.
4. stale - never write stale or empty content.
5. cloud - Use cloud Routines for cadences that should run while the laptop is closed.
6. consent - silence is never consent.
7. tyf - It runs automatically warn-only after every mutating `tyf` command and hard-fails (exit 1) as a standalone command.
8. using-tyf - It should return all sixteen skills, route any authorship request through `using-tyf`, and refuse to write into `manuscript/` outside `tyf write`.

## Suggested SOLO Promotion Shape

1. Add the R with exact reviewed wording.
2. Formulate one small F claim.
3. Add one executable Be that can fail.
4. Run prove-red before claiming coverage.
5. Run the relevant gate and doc-honesty checks.
