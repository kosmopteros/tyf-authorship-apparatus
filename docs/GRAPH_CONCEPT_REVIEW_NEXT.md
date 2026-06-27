# Concept-level graph review plan

Status: design note after PR #7.

The first graph projection is useful as a provenance map, but it is not yet the highest-value book graph.

The real author value is not seeing that chapter A links to chapter B. The real value is catching atomic inconsistencies:

- the same idea named differently in different places
- a renamed thing still appearing under the old name
- a claim asserted in one line and softened or contradicted elsewhere
- a key term used before it is defined
- a concept whose emotional or doctrinal meaning drifts across the manuscript

## Product decision

Add a concept-level review layer on top of the graph projection.

Do not make it a new source of truth. Use:

- draft and manuscript lines as source
- optional `knowledge-base/concepts.jsonl` as author-editable concept registry
- review outputs under `.review/surface/`

## Atomic unit

The atomic review unit should usually be:

```text
source path + line number + line quote + concept match
```

Not chapter. Not paragraph. A paragraph is often already too large. The graph should help find the precise phrase or line that needs author attention.

## Optional concept registry

`knowledge-base/concepts.jsonl` can hold records like:

```json
{"canonical":"amanuensis","variants":["assistant","codex helper"],"retired":["AI writer"],"note":"TYF is not an AI writer."}
```

This is not required for simple scanning, but it makes rename and drift detection much stronger.

## Review outputs

```text
.review/surface/concept-index.json
.review/surface/concept-review.json
.review/surface/concept-review.md
```

## Detection classes

- `concept-variant`: same concept appears under multiple variants
- `retired-term-used`: a retired term still appears in draft/manuscript
- `opposition-drift`: nearby lines use polarity pairs like can/cannot, is/is-not, must/must-not, always/never
- `definition-drift`: a concept has multiple definition-like lines
- `unregistered-repeated-term`: a repeated candidate concept is not yet in the registry

## Rule

All findings are prompts for author review, not verdicts. The graph should surface “look here,” not decide what the book means.
