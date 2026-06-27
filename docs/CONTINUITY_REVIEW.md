# Continuity review

Status: first deterministic continuity engine layer implemented as `tyf-continuity-review`.

The concept review catches line-level naming and definition drift. Continuity review adds author-owned registries for the reader's open loops, promised payoffs, register boundaries, and scope boundaries.

## Command

```bash
tyf-continuity-review
```

Outputs:

```text
.review/surface/continuity-review.json
.review/surface/continuity-review.md
```

## Registries

All registries are optional and author-editable. They are local JSONL record stores, not ledgers.

### `knowledge-base/reader-promises.jsonl`

Tracks promises made to the reader and expected payoff language.

```json
{"id":"gate-payoff","promise":"why the Gate matters","promise_terms":["why the Gate matters"],"payoff_terms":["Gate matters because"],"status":"open"}
```

Findings:

- `unpaid-promise`
- `resolved-promise`

### `knowledge-base/open-threads.jsonl`

Tracks intentionally open or unresolved threads.

```json
{"id":"local-first-objection","thread":"local-first objection","terms":["local-first objection"],"resolution_terms":["answer the local-first objection"],"status":"needs-resolution"}
```

Statuses:

- `needs-resolution`
- `intentional-open`
- `resolved`
- `do-not-resolve`

Findings:

- `dangling-open-thread`
- `intentional-open-thread`

### `knowledge-base/register-rules.jsonl`

Tracks language/register boundaries.

```json
{"id":"author-facing","register":"author-facing","avoid":["side-effecting APIs","schema compatibility"]}
```

Findings:

- `register-drift`

### `knowledge-base/scope-rules.jsonl`

Tracks material that belongs elsewhere.

```json
{"id":"main-book","scope":"main book","leak_terms":["implementation detail"],"allowed_paths":["docs/"]}
```

Findings:

- `scope-leak`

## Built-in detectors

Continuity review also includes:

- concept review findings from `tyf-concept-review`
- `reader-state-assumption` for phrases such as “of course,” “as we saw,” or “as discussed”
- `doctrine-vs-implementation-confusion` when doctrine language and implementation language appear in the same line

## Decisions

Each issue receives a stable-ish `issue_key` based on kind, message, path, line, and line hash.

Future decisions can be stored in:

```text
.review/surface/continuity-decisions.jsonl
```

Suggested statuses:

```text
accepted
intentional
ignored
fixed
needs-rewrite
belongs-elsewhere
```

The first implementation reads decisions if present but does not yet provide a writer command for them.

## Rule

The continuity engine should not say:

```text
The book is wrong.
```

It should say:

```text
Look here. This line may have drifted from what the reader, doctrine, or earlier promise now expects.
```

Findings are prompts for author review, not verdicts.
