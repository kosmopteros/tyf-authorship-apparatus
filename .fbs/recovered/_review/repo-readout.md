# Recovery Repo Readout

Review-only advisory artifact. No requirements were promoted, marked done, or accepted.

- truth=observed source=recovery-source `C:\Users\maste\Documents\TYF`
- truth=observed source=recovery-output `C:\Users\maste\Documents\TYF\.fbs\recovered`
- truth=observed source=doc-archaeology `docs: 80 (50 intent / 27 assessment / 3 noise, 0 legacy), 70 orphan(s), 0 with broken link(s), 13 discrepancy(ies); 376 requirement + 80 recommendation hypotheses; 0 TODO/FIXME; 4 undocumented module(s), 0 drift candidate(s), 68 large function(s); 14 prioritised Be gap(s)`

## Inferred Repo Intent

- truth=inferred confidence=0.66 source=docs/LEARN_PASS.md:13,scripts/tyf.py:883 `**Code first, model only where intelligence is required.** Every check that can be done deterministically already lives in `tyf notice`.`
- truth=inferred confidence=0.66 source=docs/RC_ARCHITECTURE_RED_TEAM.md:230,scripts/tyf.py:883 `**Command surface is too fragmented.** Standalone commands are fine internally, but `tyf workbench` and `tyf review ...` should become canonical.`
- truth=inferred confidence=0.66 source=skills/keeping-documentation-honest/SKILL.md:23,scripts/tyf.py:883 `**Explicitly, hard-fail, as `tyf check`** (exit 1 on drift;`

## Evidence-Backed Strengths

- truth=observed source=repo-graph nodes=743 edges=8786
- truth=inferred confidence=0.66 kind=recovered-intent source=docs/LEARN_PASS.md:13,scripts/tyf.py:883 `**Code first, model only where intelligence is required.** Every check that can `
- truth=inferred confidence=0.66 kind=recovered-intent source=docs/RC_ARCHITECTURE_RED_TEAM.md:230,scripts/tyf.py:883 `**Command surface is too fragmented.** Standalone commands are fine internally, `
- truth=inferred confidence=0.66 kind=recovered-intent source=skills/keeping-documentation-honest/SKILL.md:23,scripts/tyf.py:883 `**Explicitly, hard-fail, as `tyf check`** (exit 1 on drift;`
- truth=inferred confidence=0.66 kind=recovered-intent source=skills/auditing-adversarially/SKILL.md:16,scripts/tyf.py:5057 `**Frame-lock.** The work assumes its own frame and never tests it`
- truth=inferred confidence=0.66 kind=recovered-intent source=docs/ATTENTIVENESS.md:37,scripts/tyf.py:883 `**Per-run (always).** Any time `tyf notice` runs, manually or on a schedule, it `

## Gaps And Risks

- truth=observed source=doc-inventory 70 orphan doc(s) need review
- truth=observed source=.opencode/INSTALL.md,AGENTS.md,CLAUDE.md,GEMINI.md,cowork/SETUP.md,docs/PORTABILITY.md discrepancy `using-tyf`: conflicting polarity (affirm vs negate)
- truth=observed source=author-context/AGENTS.md,author-context/CLAUDE.md,author-context/GEMINI.md,cowork/PROJECT_INSTRUCTIONS.md,skills/using-tyf/SKILL.md discrepancy `drafts/candidate-draft.md`: conflicting polarity (affirm vs negate)
- truth=observed source=TYF-manifesto-and-architecture.md,docs/ATTENTIVENESS.md,docs/LEARN_PASS.md discrepancy `tyf notice`: conflicting polarity (affirm vs negate)
- truth=observed source=docs/RC_ARCHITECTURE_RED_TEAM.md,docs/WORKBENCH_ADVERSARIAL_PRODUCT_CRITIQUE_POST_PR5.md,docs/WORKBENCH_EXTERNAL_CRITIQUE_COUNCIL.md discrepancy `tyf workbench`: conflicting values: tyf review ..., tyf surface --v06
- truth=observed source=docs/WORKBENCH_EXTERNAL_CRITIQUE_COUNCIL.md,docs/WORKBENCH_TWO_WAY_MACHINERY.md discrepancy `codex app-server`: conflicting polarity (affirm vs negate)
- truth=observed source=code-scan 4 undocumented module(s)
- truth=observed source=code-scan 6 god-object candidate(s)
- truth=missing-evidence source=VALIDATION.md:6 gap=unmapped `tyf` - It runs automatically warn-only after every mutating `tyf` command and hard-fails (exit 1) as a standalone command.
- truth=missing-evidence source=.claude/commands/fbs-formulate.md:78 gap=unmapped `pass` - scenario + source files and return `pass`/`fail`.
- truth=missing-evidence source=tests/acceptance-and-edge-cases.md:153 gap=unmapped `.review/` - Should: write findings to `.review/` only;
- truth=missing-evidence source=docs/WORKBENCH_TWO_WAY_MACHINERY.md:99 gap=unmapped `manuscript/` - Hooks should not write `manuscript/`.
- truth=missing-evidence source=docs/WORKBENCH_TWO_WAY_MACHINERY.md:242 gap=unmapped `prompt` - Packet-writing or note-writing tools should stay `prompt` until usage proves they are calm.

## Recommended Review Queue

- truth=missing-evidence source=VALIDATION.md:6 review `tyf` (unmapped)
- truth=missing-evidence source=.claude/commands/fbs-formulate.md:78 review `pass` (unmapped)
- truth=missing-evidence source=tests/acceptance-and-edge-cases.md:153 review `.review/` (unmapped)
- truth=missing-evidence source=docs/WORKBENCH_TWO_WAY_MACHINERY.md:99 review `manuscript/` (unmapped)
- truth=missing-evidence source=docs/WORKBENCH_TWO_WAY_MACHINERY.md:242 review `prompt` (unmapped)

## Product Red-Team

- truth=speculative source=VALIDATION.md:6 Could `tyf` be an overclaimed promise without executable evidence?
- truth=speculative source=.claude/commands/fbs-formulate.md:78 Could `pass` be an overclaimed promise without executable evidence?
- truth=speculative source=tests/acceptance-and-edge-cases.md:153 Could `.review/` be an overclaimed promise without executable evidence?
- truth=speculative source=scripts/tyf.py:683 Could `gather_notices` concentrate too much behaviour for safe agent iteration?
- truth=speculative source=docs/LEARN_PASS.md:13,scripts/tyf.py:883 What would falsify `**Code first, model only where intelligence is required.** Every check that can `? counter=doc-side intent has no recovered behaviour cluster
- truth=speculative source=docs/RC_ARCHITECTURE_RED_TEAM.md:230,scripts/tyf.py:883 What would falsify `**Command surface is too fragmented.** Standalone commands are fine internally, `? counter=doc-side intent has no recovered behaviour cluster
- truth=speculative source=skills/keeping-documentation-honest/SKILL.md:23,scripts/tyf.py:883 What would falsify `**Explicitly, hard-fail, as `tyf check`** (exit 1 on drift;`? counter=doc-side intent has no recovered behaviour cluster

## Truth Boundary

- truth=observed means deterministic recovery counted or found the item.
- truth=inferred means SOLO connected docs, graph paths, or candidate R evidence.
- truth=missing-evidence means a documented or structural claim lacks enough backing evidence.
- truth=speculative means a review question or red-team hypothesis, not a verdict.
- No requirements were promoted; use `fbs requirements add` only after human review.
