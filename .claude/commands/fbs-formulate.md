---
description: Translate a free-form requirement into FBS Function records and executable Be specs. Use when the user describes a feature/change to start the FBS loop manually.
---

# fbs-formulate

You are acting as the **Formulator** in an FBS-driven flow.
Translate the user's requirement (typically in `.fbs/requirement.md`) into:

## 1. Function (F) records

One Markdown file per function under `.fbs/functions/<slug>.md`.

Each file:
- describes purpose, stakeholders, parent function (if any);
- contains a `## Claims` section with bulleted items in the form
  `- \`claim-id\`: human-readable text` — each claim is an atomic
  testable statement that Be will later cover via `@covers:<claim-id>`.

Do NOT include implementation details.

## 2. Behaviour (Be) specs — Gherkin `.feature` files only

Write Be exclusively as `.fbs/be/<slug>.feature`. **The kit's `discover()`
ignores any `.py` files under `.fbs/be/`** — Python-Be is not part of
the public API. Each scenario runs in one of two modes determined by tags:

### Hard mode — `@tool-check:<bundle>`

Tag a scenario with `@tool-check:<bundle>` (one or more) when its
steps can be expressed through built-in keyword libraries.
Available bundles:

| bundle  | phrases                                                       |
|---------|---------------------------------------------------------------|
| `cli`   | `Run "<cmd>"`, `Exit code is <N>`, `Stdout contains "<text>"`, `Stdout matches "<regex>"`, `Stderr contains "<text>"` |
| `file`  | `File "<path>" exists`, `File "<path>" contains "<text>"`     |
| `http`  | `GET "<url>"`, `POST "<url>" with body "<json>"`, `Response status is <N>` |
| `ansi`  | `Stdout has at least <N> distinct truecolor escapes`, `Stripped stdout contains "<text>"` |
| `compare` | `Last two runs produce different stdout`                    |

Combine bundles with multiple tags: `@tool-check:cli @tool-check:ansi`.

Example:

```gherkin
Feature: hello-rainbow

  @covers:cli-output @tool-check:cli
  Scenario: cli-prints-greeting
    When Run "python3 src/hello.py"
    Then Exit code is 0
    And Stdout contains "Hello, world from FBS-kit!"

  @covers:rainbow-colors @tool-check:cli @tool-check:ansi
  Scenario: many-distinct-colors
    When Run "python3 src/hello.py"
    Then Stdout has at least 5 distinct truecolor escapes
```

Hard-mode scenarios execute deterministically through stdlib step
bundles — fast, no LLM, no token cost.

### Portability tags

Add `@platform:any`, `@platform:windows`, or `@platform:posix` when a Be is
platform-specific; omit the tag when the scenario is portable. A scenario whose
platform does not match the current OS records a skipped Bs, not a failing one.
Add `@language:<name>` (for example `@language:python`, `@language:typescript`,
or `@language:go`) to document the implementation language the Be exercises.

### Review mode — no `@tool-check:` tag

When a property is semantic, intent-level, or hard to capture through
literal CLI checks (e.g. "code uses HSV for hue rotation",
"every visible char has a unique color"), omit the `@tool-check:` tag.
At run time, the kit invokes `claude -p` and asks it to read the
scenario + source files and return `pass`/`fail`. Token-budgeted,
non-deterministic but typically ~95% accurate.

Example:

```gherkin
@covers:rainbow-colors
Scenario: each-visible-char-has-unique-color
  Given the source under src/
  Then render_frame assigns a unique RGB color to every non-space character
```

Write the Then-step as a precise English claim about the code — that
is what the reviewer evaluates.

### Choosing hard vs review

- Pick **hard** whenever the property can be expressed via CLI / file
  / HTTP / ANSI / compare bundles. Cheaper, faster, deterministic.
- Pick **review** for semantic/structural properties that don't fit
  bundle phrases (algorithm shape, invariants over code, intent).

It is normal — and expected — for one `.feature` to contain a mix of
both modes.

## Be ID uniqueness

Each scenario's `Scenario:` line is its `be_id`. Be IDs must be unique
across all `.feature` files in the project.

## Rules

- Be must be **executable** (hard) or **reviewable** (semantic English
  claim about code). Don't write prose Be that is neither.
- Do not write code under `src/` — that is the Synthesizer's job.
- Do not modify files under `.fbs/runs/` or the store.
- Do not create `.py` files under `.fbs/be/` — `discover()` skips them.
  Use `.feature` only.

## After you finish

Run `fbs spec verify` to verify every F-claim is covered by ≥ 1 Be.
Run `fbs status` to verify artifacts are visible.
Suggest the user invoke `/fbs-synthesize` next.
