# Continuity engine 20x coder/critic review

Status: implemented first layer and reviewed through 20 alternating coder/critic passes.

This log is intentionally concrete: each coder pass describes what was added or strengthened, and each critic pass records the remaining risk. The result is not a claim of perfection; it is a directionally stronger continuity engine that stays author-owned.

## Baseline entering the 20x pass

Already present before this pass:

- provenance-first graph projection: `tyf-graph`
- JSONL ledger audit
- concept-level review plan
- concept-level review implementation: `tyf-concept-review`
- line-level findings with path, line, quote, and line hash
- optional `knowledge-base/concepts.jsonl`

## Pass 01

**Coder:** Add the concept registry model: canonical name, variants, retired terms, notes.

**Critic:** Good start, but a registry alone does not create author value unless findings point to exact manuscript lines.

## Pass 02

**Coder:** Scan drafts and manuscript line-by-line and store `path`, `line`, `side`, `quote`, and `line_hash`.

**Critic:** Correct atomic unit. Do not regress to paragraph/chapter-level findings for continuity issues.

## Pass 03

**Coder:** Add retired-term detection for rename residue.

**Critic:** This is high-value because it catches the exact “renamed in one place but not another” problem. It should stay `likely-fix`, not a vague review warning.

## Pass 04

**Coder:** Add concept-variant detection when one canonical concept appears under multiple variants.

**Critic:** Useful, but not all variants are mistakes. The output must remain review-oriented, not prescriptive.

## Pass 05

**Coder:** Add opposition drift detection with polarity pairs such as `can/cannot`, `must/must not`, `always/never`, `author/writer`, `draft/manuscript`.

**Critic:** This is a heuristic, not semantic contradiction detection. It can surface likely tension but must not adjudicate doctrine.

## Pass 06

**Coder:** Add definition-drift detection for multiple definition-like lines.

**Critic:** Strong author value. Definitions often drift quietly across books. This should eventually connect to doctrine records.

## Pass 07

**Coder:** Add repeated unregistered term detection so recurring concepts can be promoted into the registry.

**Critic:** Risk of noise. Keep severity low and cap output.

## Pass 08

**Coder:** Write author-facing outputs under `.review/surface/`: `concept-index.json`, `concept-review.json`, and `concept-review.md`.

**Critic:** Correct. `.md` is the author surface; `.json` is machine-readable state. Do not replace author reports with opaque graph dumps.

## Pass 09

**Coder:** Add package command `tyf-concept-review`.

**Critic:** Good, but the canonical long-term command should probably become `tyf continuity-review` or `tyf review continuity` inside `tyf.py`.

## Pass 10

**Coder:** Add test coverage that catches retired terms, variants, opposition drift, and definition drift.

**Critic:** Tests prove the first layer, but not real-book signal quality. Future tests should use messy real excerpts.

## Pass 11

**Coder:** Preserve the rule that findings are prompts for author review, not verdicts.

**Critic:** Essential. A continuity engine must not become an invisible editor deciding the book’s meaning.

## Pass 12

**Coder:** Keep concept review independent from SQLite or graph storage. It reads manuscript/draft lines and concept registry directly.

**Critic:** Good. Graph storage should never be required for author trust or recovery.

## Pass 13

**Coder:** Ensure exact-line references are present in Markdown reports.

**Critic:** This is the difference between a useful review and a vague hallucinated critique. Keep exact source locations everywhere.

## Pass 14

**Coder:** Keep `knowledge-base/concepts.jsonl` optional. If absent, still report repeated candidates.

**Critic:** Good onboarding. The tool should help the registry emerge from the book rather than require perfect setup first.

## Pass 15

**Coder:** Separate severity levels: `likely-fix`, `review`, `low`.

**Critic:** Useful but still primitive. Future versions should include author decision status: accepted, ignored, intentional, fixed.

## Pass 16

**Coder:** Keep the concept registry author-editable JSONL instead of inventing a database.

**Critic:** Correct. This preserves the local, inspectable apparatus. But it is a mutable record store, not a ledger.

## Pass 17

**Coder:** Document that concept-level review is a layer above structural graph projection, not a replacement for it.

**Critic:** Good separation. Structural graph answers “what is connected?” Continuity review answers “what may now be inconsistent?”

## Pass 18

**Coder:** Add line hashes so findings survive enough context to be traced even if line numbers later shift.

**Critic:** Useful, but future recovery should also match quote/context, not only line hash.

## Pass 19

**Coder:** Identify the next registries: promises, open threads, register rules, scope rules.

**Critic:** This is the next true 10/10 direction. Concept review catches terms and definitions; continuity review must catch reader-state and promise/payoff.

## Pass 20

**Coder:** Keep the first layer small and mergeable; avoid jumping directly into semantic LLM adjudication.

**Critic:** Correct restraint. The next layer should add explicit author-owned registries and deterministic reviews before using models.

## Current score

Approximate product score after this pass: **8.2/10**.

Why not higher:

- no promise/payoff registry yet
- no open-thread review yet
- no register drift detection yet
- no scope leak detection yet
- no author decisions on review findings yet
- no Workbench UI card for continuity findings yet
- no integration into the main `tyf` command parser yet
- no real-book signal/noise calibration yet

## Next 10/10 path

### Slice A: Continuity registry layer

Add:

```text
knowledge-base/reader-promises.jsonl
knowledge-base/open-threads.jsonl
knowledge-base/register-rules.jsonl
knowledge-base/scope-rules.jsonl
```

### Slice B: Continuity review command

Add:

```text
tyf-continuity-review
.review/surface/continuity-review.json
.review/surface/continuity-review.md
```

Detection classes:

- unpaid-promise
- resolved-promise
- dangling-open-thread
- intentional-open-thread
- register-drift
- scope-leak
- reader-state-assumption
- doctrine-vs-implementation-confusion
- revision-blast-radius

### Slice C: Workbench integration

Add a side-panel card:

```text
Continuity review
  3 likely fixes
  5 review points
  12 low-priority candidates
```

### Slice D: Author decisions on findings

Add review decision records:

```text
.review/surface/continuity-decisions.jsonl
```

Statuses:

```text
accepted
intentional
ignored
fixed
needs-rewrite
belongs-elsewhere
```

### Slice E: Model-assisted review, later

Only after deterministic registries exist, allow an amanuensis to propose additional findings. Model-derived findings must be marked as machine-derived and never replace author decisions.

## Product doctrine

The continuity engine should not say:

```text
The book is wrong.
```

It should say:

```text
Look here. This line may have drifted from what the reader, doctrine, or earlier promise now expects.
```

That is the core 10/10 direction.
