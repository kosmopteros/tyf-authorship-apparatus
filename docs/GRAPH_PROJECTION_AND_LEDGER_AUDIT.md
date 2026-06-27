# Graph projection and JSONL ledger audit

Status: implemented as `scripts/tyf_graph_projection.py`.

## Product decision

Do not add a new source-of-truth store for the graph.

The graph is a rebuildable projection from existing local truth:

- draft and manuscript Markdown files
- `outline/book-map.yaml`
- `knowledge-base/author-notes.jsonl`
- `.tyf/events.jsonl`
- review packet JSON/Markdown files
- Codex status and bridge JSON/JSONL files
- approval and hook JSON/JSONL files

Generated graph artifacts may be deleted and rebuilt. Deleting them must not delete author knowledge.

## Outputs

By default:

```text
.review/surface/book-graph.json
.review/surface/graph-build-report.json
.review/surface/graph-build-report.md
```

Optional cache:

```text
.tyf/graph.sqlite
```

The SQLite file is a query cache only. It is never canonical.

## Command

From a TYF workspace:

```bash
tyf-graph
```

Or directly:

```bash
python scripts/tyf_graph_projection.py
```

With the optional SQLite cache:

```bash
tyf-graph --sqlite
```

## Graph model

Nodes include:

- work
- units
- draft files
- manuscript files
- author notes
- footnote candidates
- Gate packets
- JSONL ledgers/logs
- JSONL records
- derived term nodes

Edges include:

- work `has-unit` unit
- unit `has-draft` draft file
- unit `has-manuscript` manuscript file
- note `notes` target file
- note `mentions-term` term
- footnote candidate `derived-from-note` note
- Gate packet `prepared-from-draft` draft file
- work `has-ledger-or-log` JSONL file
- JSONL file `contains-record` record
- record `references-path` file
- unit `uses-term` term

## Provenance classes

Every node and edge has a provenance class:

- `author-explicit`: author-authored note or declaration
- `amanuensis-derived`: assistant-authored note or related artifact
- `apparatus-structural`: file path, packet source, unit map, event record, hash
- `machine-derived`: term overlap and other weak inferences

Machine-derived edges are intentionally low-confidence. They should help retrieval and review, not assert truth.

## JSONL audit

The same command audits JSONL files under known local apparatus prefixes:

```text
.tyf/
knowledge-base/
.review/surface/
assets/images/
```

Classifications:

- `hash-chain-ledger`: currently `.tyf/events.jsonl` when its sequence and hash chain verify
- `broken-hash-chain-ledger`: event chain exists but does not verify
- `append-log-jsonl`: JSONL append logs without cryptographic chain semantics
- `empty-jsonl`: placeholder or unused JSONL file

This is intentionally blunt. A `.jsonl` extension alone does not make something a ledger.

## Answer to the storage question

No new primary storage.

Use existing Markdown/JSON/JSONL as truth. Use JSON graph output for author inspection. Use SQLite only as a rebuildable query cache when useful.

## Non-goals

This implementation does not add:

- Neo4j or any external graph database
- RDF/triplestore semantics
- semantic vector search
- automatic contradiction adjudication
- graph-authored manuscript edits

The graph is an attentive index, not another author and not another memory.
