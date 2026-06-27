# TYF storage contract

Status: RC architecture contract.

TYF is a single-author, local-first workspace. It does not assume Git and it does not use a graph database as truth. Different file families have different authority. A path extension alone does not define trust.

## Storage classes

### `canonical-prose`

Author-facing prose surfaces.

```text
drafts/**/*.md
manuscript/**/*.md
```

Rules:

- `drafts/` is editable by the Workbench with hash-guarded saves.
- `manuscript/` is read-only from the Workbench and moves only through the Gate.
- No review tool may silently rewrite either tree.

### `canonical-author-record`

Author-owned local records that shape review behavior.

```text
knowledge-base/concepts.jsonl
knowledge-base/reader-promises.jsonl
knowledge-base/open-threads.jsonl
knowledge-base/register-rules.jsonl
knowledge-base/scope-rules.jsonl
knowledge-base/voice-map.jsonl
knowledge-base/typography-style.jsonl
```

Rules:

- Local JSONL record stores.
- Author-editable.
- Not automatically ledgers.
- Used to guide review, not to overwrite prose.

### `mutable-record-store`

Durable records that may be rewritten by apparatus state transitions.

```text
knowledge-base/author-notes.jsonl
```

Rules:

- Durable local record storage.
- Not append-only; note statuses may be updated.
- Not a hash-chain ledger.

### `hash-chain-ledger`

Tamper-evident event journal.

```text
.tyf/events.jsonl
```

Rules:

- Sequence and hash chain must verify.
- Used for local apparatus events and author-visible decisions.
- If broken, mutating commands should refuse or warn depending on command criticality.

### `append-log`

Append-style local logs without hash-chain semantics.

```text
.review/surface/*.jsonl
.review/conflicts/**/*.jsonl
```

Rules:

- Useful for histories/statuses.
- Not canonical truth unless explicitly classified elsewhere.
- Do not treat `.jsonl` alone as ledger semantics.

### `generated-review`

Human-readable and machine-readable derived review outputs.

```text
.review/surface/*-review.md
.review/surface/*-review.json
.review/surface/*-report.md
.review/surface/*-report.json
.review/surface/book-graph.json
.review/surface/workbench-*.html
.review/surface/workbench-*-data.json
```

Rules:

- Rebuildable.
- Useful for author review.
- Never accepted manuscript.
- May be deleted and regenerated.

### `rebuildable-cache`

Performance/query caches.

```text
.tyf/graph.sqlite
```

Rules:

- Rebuildable from local truth.
- Never canonical.
- Deleting it must not delete author knowledge.

### `recovery-artifact`

Local conflict recovery material.

```text
drafts/.recovery-copies/**/*.md
.review/conflicts/**
```

Rules:

- Preserves browser and disk versions when local concurrency occurs.
- Never auto-merged.
- Never promoted to manuscript without the normal Gate.

## Architectural invariants

1. No component silently writes `manuscript/` outside the Gate.
2. `drafts/` writes use compare-and-swap hashes or explicit recovery copies.
3. Generated review artifacts are not truth.
4. SQLite is never truth.
5. JSONL is not automatically a ledger.
6. The graph is an attentive index, not another memory or author.
7. The editor may point, annotate, and propose; only the author rewrites the book.
