# RC 20-pass code / critique / improvement log

Status: RC-hardening pass after continuity review.

This log records twenty alternating code-persona and critic passes for the RC direction. The code changes from this pass are:

- `scripts/tyf_continuity_decision.py`
- `scripts/tyf_polish_review.py`
- `tests/test_polish_and_decisions.py`
- `docs/RC_POLISH_AND_DECISIONS.md`
- package commands for `tyf-continuity-decision` and `tyf-polish-review`

## Pass 01

**Coder:** Add a continuity decision writer so findings can be marked `intentional`, `fixed`, `ignored`, `needs-rewrite`, `accepted`, or `belongs-elsewhere`.

**Critic:** This is RC-critical. Without it, the system keeps resurfacing intentional author choices and becomes noise.

## Pass 02

**Coder:** Store decisions in `.review/surface/continuity-decisions.jsonl`.

**Critic:** Correct location for review state. This is append-log review memory, not manuscript content.

## Pass 03

**Coder:** Validate decision status values with an allow-list.

**Critic:** Good. Ambiguous statuses would make review reports harder to filter.

## Pass 04

**Coder:** Record decision events into the normal TYF event log.

**Critic:** Good; this keeps author decisions visible to the apparatus.

## Pass 05

**Coder:** Add a near-final polish reviewer instead of extending concept review with style concerns.

**Critic:** Correct separation. Concept continuity and polish are related but not the same product surface.

## Pass 06

**Coder:** Add `knowledge-base/voice-map.jsonl` as an author-owned registry for voice zones.

**Critic:** Essential. Books with acts, appendices, first-person lanes, and third-person lanes must not be normalized into one voice.

## Pass 07

**Coder:** Add narration-lane mismatch detection for first-person language inside declared third-person zones.

**Critic:** Useful first heuristic, but keep it as review, not a verdict. Some third-person sections may quote or contain intentional fragments.

## Pass 08

**Coder:** Add register-leak detection through voice-zone `avoid` terms.

**Critic:** Strong value for this apparatus because technical language can leak into author-facing prose.

## Pass 09

**Coder:** Add `knowledge-base/typography-style.jsonl` for house-style rules.

**Critic:** Correct. Typography choices should be explicit local records, not implicit model preferences.

## Pass 10

**Coder:** Detect dash style drift.

**Critic:** Useful, but candidate text should remain minimal. Do not auto-normalize punctuation.

## Pass 11

**Coder:** Detect ellipsis style drift.

**Critic:** Useful in near-final copyedit. Again, no auto-write.

## Pass 12

**Coder:** Detect term capitalization drift.

**Critic:** Strong for books with key terms like Gate, Workbench, apparatus, amanuensis.

## Pass 13

**Coder:** Write both `.json` and `.md` polish outputs.

**Critic:** Correct: JSON for tools, Markdown for the author/editor.

## Pass 14

**Coder:** Add issue keys to polish findings.

**Critic:** Good. Future decision memory must be able to refer to exact findings.

## Pass 15

**Coder:** Include minimal suggestion fields for typography issues.

**Critic:** Acceptable because it is line-level and minimal. Do not add whole-paragraph rewrites.

## Pass 16

**Coder:** Add tests for decision writing and latest-decision lookup.

**Critic:** Good. This prevents silent breakage of the author decision layer.

## Pass 17

**Coder:** Add tests for narration lane mismatch, register leak, dash drift, ellipsis drift, and capitalization drift.

**Critic:** Good first coverage. Future tests should use real excerpts from both book structures.

## Pass 18

**Coder:** Expose `tyf-continuity-decision` and `tyf-polish-review` in package scripts.

**Critic:** Better than hidden scripts. Still not final command UX; canonical `tyf review polish` can come later.

## Pass 19

**Coder:** Document the non-rewriting invariant explicitly.

**Critic:** Critical. This is what separates TYF from the older rewrite-happy TIF failure mode.

## Pass 20

**Coder:** Keep the slice focused: decisions and polish review, not embedded chat or semantic model judging.

**Critic:** Correct. RC moves forward by reducing author risk and editorial noise, not by adding more AI surface.

## Result

Approximate RC readiness after this slice:

```text
Safety boundary:          8.8/10
Writing desk:             7.7/10
Continuity review:        7.7/10
Polish/editorial mode:    7.0/10
Workbench UX integration: 6.6/10
Overall private RC:       7.6/10
```

## Remaining RC blockers

1. Conflict recovery choices in the Workbench.
2. Continuity/polish summary cards in the Workbench side panel.
3. Direct `tyf workbench` / `tyf review` command integration.
4. Real-book signal/noise calibration.
5. Optional line-edit candidate packet generator for exact minimal edits.

## Product verdict

This pass moves TYF materially closer to a private RC for near-final book work because it adds two missing editorial primitives: the author can remember decisions, and the apparatus can review voice/typography without rewriting the book.
