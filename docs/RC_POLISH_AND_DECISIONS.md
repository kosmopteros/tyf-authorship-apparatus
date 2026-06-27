# RC polish and decision layer

Status: implemented as the next RC-hardening slice.

## Product purpose

Near-final books need a different apparatus mode from drafting. The apparatus should not rewrite the book. It should point to exact lines, explain the possible issue, offer minimal candidate patches only where appropriate, and preserve author decisions.

This slice adds two RC-level capabilities:

1. Author decisions on continuity findings.
2. Non-rewriting voice and typography polish review.

## Commands

```bash
tyf-continuity-decision <issue_key> --status intentional --note "planned voice break"
tyf-polish-review
```

## Continuity decisions

Decisions are appended to:

```text
.review/surface/continuity-decisions.jsonl
```

Allowed statuses:

```text
accepted
intentional
ignored
fixed
needs-rewrite
belongs-elsewhere
```

This is important because a real book contains intentional ruptures. The apparatus should not keep nagging the author about a planned voice break, an intentional open thread, or a passage that belongs in the appendix.

## Polish review

`tyf-polish-review` reads:

```text
knowledge-base/voice-map.jsonl
knowledge-base/typography-style.jsonl
```

and writes:

```text
.review/surface/polish-review.json
.review/surface/polish-review.md
```

## Voice map

Example:

```json
{"id":"third-calm","paths":["drafts/chapter-one.md"],"person":"third","register":"calm narration","avoid":["side-effecting APIs","schema compatibility"]}
```

The point is not to force one global voice. A finished book may have acts, appendices, first-person lanes, third-person lanes, colder documentary sections, and intentionally evolving registers. The voice map makes those zones explicit.

Current detection classes:

```text
narration-lane-mismatch
register-leak
```

## Typography style

Example:

```json
{"dash":"em-dash","ellipsis":"single-character","capitalization":{"gate":"Gate","workbench":"Workbench"}}
```

Current detection classes:

```text
dash-style-drift
ellipsis-style-drift
term-capitalization-drift
```

## Non-rewriting invariant

This layer does not rewrite prose. It outputs exact findings and minimal suggestions only.

Allowed:

```text
source path
line number
original quote
issue
why it matters
minimal suggestion
issue key
author decision
```

Not allowed:

```text
rewrite the chapter
rewrite the section
normalize all voices into one voice
silently change manuscript
```

## RC impact

This closes two major pre-RC gaps:

- intentional findings can now be marked and remembered;
- near-final books can be reviewed for voice-zone and house-style drift without becoming generic rewritten prose.

Remaining before a stronger RC:

- Workbench side-panel dashboard for continuity/polish summaries;
- conflict recovery choices;
- direct `tyf workbench` subcommand in `scripts/tyf.py`;
- real-book signal/noise calibration.
