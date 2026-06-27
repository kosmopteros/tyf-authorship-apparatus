#!/usr/bin/env python3
"""TYF provenance-first graph projection and JSONL ledger audit.

The graph is a rebuildable projection from local truth files. It is not a new
source of truth. Deleting generated graph artifacts must never delete author
knowledge.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import sqlite3
import sys
from typing import Any, Dict, List, Optional, Tuple

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import tyf_workbench_v06 as wb  # noqa: E402

GRAPH_JSON = "book-graph.json"
GRAPH_REPORT_JSON = "graph-build-report.json"
GRAPH_REPORT_MD = "graph-build-report.md"
GRAPH_SQLITE = "graph.sqlite"

LEDGER_PREFIXES = (
    ".tyf/",
    "knowledge-base/",
    ".review/surface/",
    "assets/images/",
)

STOP_WORDS = {
    "that", "this", "with", "from", "have", "will", "would", "there", "their",
    "about", "which", "when", "then", "than", "into", "onto", "because", "without",
    "within", "where", "what", "your", "author", "draft", "book", "text", "note",
}


def resolve(work_arg: Optional[str]) -> Tuple[str, Path, Path]:
    work_id, work_root, root = wb.resolve_work(work_arg)
    wb.ensure_workbench_shape(work_root, root)
    return work_id, work_root, root


def rel(work_root: Path, path: Path) -> str:
    return path.relative_to(work_root).as_posix()


def file_sha(path: Path) -> str:
    return wb.sha256_text(wb.read_text(path)) if path.is_file() else ""


def read_json(path: Path) -> Optional[Dict[str, Any]]:
    try:
        data = json.loads(wb.read_text(path, ""))
    except json.JSONDecodeError:
        return None
    return data if isinstance(data, dict) else None


def read_jsonl_records(path: Path) -> Tuple[List[Dict[str, Any]], int, int]:
    records: List[Dict[str, Any]] = []
    invalid = 0
    total = 0
    for line in wb.read_text(path).splitlines():
        if not line.strip():
            continue
        total += 1
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            invalid += 1
            continue
        if isinstance(item, dict):
            records.append(item)
        else:
            invalid += 1
    return records, total, invalid


def terms(text: str, limit: int = 12) -> List[str]:
    words = re.findall(r"[\w][\w'-]{3,}", text.lower(), flags=re.UNICODE)
    out: List[str] = []
    for word in words:
        if word not in STOP_WORDS and word not in out:
            out.append(word)
        if len(out) >= limit:
            break
    return out


class GraphBuilder:
    def __init__(self, work_id: str, work_root: Path) -> None:
        self.work_id = work_id
        self.work_root = work_root
        self.nodes: Dict[str, Dict[str, Any]] = {}
        self.edges: Dict[str, Dict[str, Any]] = {}
        self.warnings: List[str] = []

    def add_node(self, node_id: str, kind: str, label: str, provenance: str, source_path: str = "", source_hash: str = "", attrs: Optional[Dict[str, Any]] = None) -> str:
        existing = self.nodes.get(node_id, {})
        merged = {
            "id": node_id,
            "kind": kind,
            "label": label,
            "provenance": provenance,
            "source_path": source_path,
            "source_hash": source_hash,
            "attrs": attrs or {},
        }
        if existing:
            existing.update({k: v for k, v in merged.items() if v not in (None, "", {})})
            if attrs:
                existing.setdefault("attrs", {}).update(attrs)
        else:
            self.nodes[node_id] = merged
        return node_id

    def add_edge(self, from_id: str, to_id: str, kind: str, provenance: str, source_path: str = "", source_hash: str = "", confidence: float = 1.0, attrs: Optional[Dict[str, Any]] = None) -> str:
        edge_id = "edge:" + wb.short_hash(from_id, kind, to_id, source_path, source_hash)
        self.edges[edge_id] = {
            "id": edge_id,
            "from": from_id,
            "to": to_id,
            "kind": kind,
            "provenance": provenance,
            "source_path": source_path,
            "source_hash": source_hash,
            "confidence": confidence,
            "attrs": attrs or {},
        }
        return edge_id

    def file_node(self, path: Path, kind: str) -> str:
        r = rel(self.work_root, path)
        return self.add_node(f"file:{r}", kind, r, "apparatus-structural", r, file_sha(path), {"path": r})


def audit_event_chain(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not records:
        return {"chain": "empty", "valid": True, "breaks": []}
    breaks: List[Dict[str, Any]] = []
    previous = ""
    expected_seq = 1
    for item in records:
        seq = item.get("seq")
        if seq != expected_seq:
            breaks.append({"seq": seq, "problem": "unexpected sequence", "expected": expected_seq})
        if item.get("previous_hash", "") != previous:
            breaks.append({"seq": seq, "problem": "previous_hash mismatch"})
        expected_hash = wb.event_record_hash(item)
        if item.get("hash") != expected_hash:
            breaks.append({"seq": seq, "problem": "hash mismatch"})
        previous = item.get("hash", "")
        expected_seq += 1
    return {"chain": "hash-chain", "valid": not breaks, "breaks": breaks}


def jsonl_files(work_root: Path) -> List[Path]:
    found: List[Path] = []
    for path in sorted(work_root.rglob("*.jsonl")):
        try:
            r = rel(work_root, path)
        except ValueError:
            continue
        if any(r.startswith(prefix) for prefix in LEDGER_PREFIXES):
            found.append(path)
    return found


def audit_jsonl_ledgers(work_root: Path) -> Dict[str, Any]:
    files: List[Dict[str, Any]] = []
    totals = {
        "files": 0,
        "records": 0,
        "invalid_lines": 0,
        "hash_chain_ledgers": 0,
        "append_logs": 0,
        "mutable_record_stores": 0,
        "empty": 0,
    }
    for path in jsonl_files(work_root):
        r = rel(work_root, path)
        records, total, invalid = read_jsonl_records(path)
        field_counts = {
            "id": sum(1 for x in records if x.get("id")),
            "kind": sum(1 for x in records if x.get("kind")),
            "status": sum(1 for x in records if x.get("status")),
            "created_at": sum(1 for x in records if x.get("created_at")),
            "updated_at": sum(1 for x in records if x.get("updated_at")),
            "ts": sum(1 for x in records if x.get("ts")),
            "hash": sum(1 for x in records if x.get("hash")),
            "previous_hash": sum(1 for x in records if x.get("previous_hash") or x.get("previous_hash") == ""),
        }
        if not records and total == 0:
            classification = "empty-jsonl"
            chain = {"chain": "empty", "valid": True, "breaks": []}
            totals["empty"] += 1
        elif r.endswith(".tyf/events.jsonl") or r == ".tyf/events.jsonl":
            chain = audit_event_chain(records)
            classification = "hash-chain-ledger" if chain.get("valid") else "broken-hash-chain-ledger"
            totals["hash_chain_ledgers"] += 1
        elif r == "knowledge-base/author-notes.jsonl":
            chain = {"chain": "mutable-record-store", "valid": invalid == 0, "breaks": []}
            classification = "mutable-record-store-jsonl"
            totals["mutable_record_stores"] += 1
        else:
            chain = {"chain": "append-log", "valid": invalid == 0, "breaks": []}
            classification = "append-log-jsonl"
            totals["append_logs"] += 1
        totals["files"] += 1
        totals["records"] += len(records)
        totals["invalid_lines"] += invalid
        files.append({
            "path": r,
            "classification": classification,
            "records": len(records),
            "non_empty_lines": total,
            "invalid_lines": invalid,
            "field_counts": field_counts,
            "chain": chain,
            "source_hash": file_sha(path),
        })
    return {"kind": "tyf-jsonl-ledger-audit", "generated_at": wb.now(), "totals": totals, "files": files}


def build_graph(work_id: str, work_root: Path, root: Path) -> Dict[str, Any]:
    data = wb.collect_data(work_id, work_root, root)
    builder = GraphBuilder(work_id, work_root)
    work_node = builder.add_node(f"work:{work_id}", "work", data.get("work", {}).get("title") or work_id, "apparatus-structural", "work.yaml", file_sha(work_root / "work.yaml"), data.get("work", {}))

    term_owners: Dict[str, List[str]] = {}
    for unit in data.get("units", []):
        unit_id = str(unit.get("id") or unit.get("key") or "unit")
        unit_node = builder.add_node(f"unit:{unit_id}", "unit", str(unit.get("title") or unit_id), "apparatus-structural", "outline/book-map.yaml", file_sha(work_root / "outline" / "book-map.yaml"), {"key": unit.get("key"), "kind": unit.get("kind")})
        builder.add_edge(work_node, unit_node, "has-unit", "apparatus-structural", "outline/book-map.yaml", file_sha(work_root / "outline" / "book-map.yaml"))
        unit_text = ""
        for side in ("draft", "manuscript"):
            item = unit.get(side) or {}
            p = item.get("path")
            if not p:
                continue
            path = work_root / p
            file_node = builder.file_node(path, side)
            builder.add_edge(unit_node, file_node, f"has-{side}", "apparatus-structural", p, item.get("sha256", ""))
            unit_text += "\n" + str(item.get("text") or "")
        for t in terms(unit_text, 20):
            term_owners.setdefault(t, []).append(unit_node)

    notes = data.get("notes", [])
    for note in notes:
        note_id = str(note.get("id") or wb.short_hash(json.dumps(note, sort_keys=True)))
        source_path = "knowledge-base/author-notes.jsonl"
        provenance = "author-explicit" if note.get("provenance") == "author" else "amanuensis-derived"
        note_node = builder.add_node(f"note:{note_id}", "author-note", str(note.get("body") or note_id)[:80], provenance, source_path, file_sha(work_root / source_path), note)
        target = note.get("target_path") or ""
        if target and target != "book":
            target_node = builder.add_node(f"file:{target}", "target-file", target, "apparatus-structural", target, file_sha(work_root / target), {"path": target})
            builder.add_edge(note_node, target_node, "notes", provenance, source_path, file_sha(work_root / source_path))
        for t in terms(str(note.get("body") or ""), 8):
            term_node = builder.add_node(f"term:{t}", "term", t, "machine-derived")
            builder.add_edge(note_node, term_node, "mentions-term", "machine-derived", source_path, file_sha(work_root / source_path), 0.4)

    for folder, kind, edge_kind in ((".review/footnote-candidates", "footnote-candidate", "derived-from-note"), (".review/gate-packets", "gate-packet", "prepared-from-draft")):
        base = work_root / folder
        if not base.is_dir():
            continue
        for path in sorted(base.glob("*.json")):
            payload = read_json(path)
            if not payload:
                continue
            r = rel(work_root, path)
            node_id = f"{kind}:{payload.get('id') or path.stem}"
            node = builder.add_node(node_id, kind, str(payload.get("id") or path.stem), "apparatus-structural", r, file_sha(path), payload)
            if kind == "footnote-candidate" and payload.get("source_note_id"):
                builder.add_edge(node, f"note:{payload.get('source_note_id')}", edge_kind, "apparatus-structural", r, file_sha(path))
            if kind == "gate-packet" and payload.get("source_path"):
                target = f"file:{payload.get('source_path')}"
                builder.add_node(target, "draft", str(payload.get("source_path")), "apparatus-structural", str(payload.get("source_path")), file_sha(work_root / str(payload.get("source_path"))))
                builder.add_edge(node, target, edge_kind, "apparatus-structural", r, file_sha(path))

    audit = audit_jsonl_ledgers(work_root)
    for item in audit.get("files", []):
        ledger_node = builder.add_node(f"ledger:{item['path']}", "jsonl-ledger", item["path"], "apparatus-structural", item["path"], item.get("source_hash", ""), item)
        builder.add_edge(work_node, ledger_node, "has-ledger-or-log", "apparatus-structural", item["path"], item.get("source_hash", ""))
        records, _total, _invalid = read_jsonl_records(work_root / item["path"])
        for record in records[-200:]:
            rid = record.get("id") or record.get("seq") or wb.short_hash(json.dumps(record, ensure_ascii=False, sort_keys=True))
            event_node = builder.add_node(f"record:{item['path']}:{rid}", "jsonl-record", str(record.get("kind") or record.get("status") or rid), "apparatus-structural", item["path"], item.get("source_hash", ""), record)
            builder.add_edge(ledger_node, event_node, "contains-record", "apparatus-structural", item["path"], item.get("source_hash", ""))
            active_path = record.get("active_path") or record.get("target_path") or ""
            if active_path:
                target = builder.add_node(f"file:{active_path}", "target-file", active_path, "apparatus-structural", active_path, file_sha(work_root / str(active_path)))
                builder.add_edge(event_node, target, "references-path", "apparatus-structural", item["path"], item.get("source_hash", ""))

    for term, owners in term_owners.items():
        if len(set(owners)) < 2:
            continue
        term_node = builder.add_node(f"term:{term}", "term", term, "machine-derived")
        for owner in sorted(set(owners)):
            builder.add_edge(owner, term_node, "uses-term", "machine-derived", confidence=0.35)

    graph = {
        "kind": "tyf-book-graph",
        "version": 1,
        "work": work_id,
        "generated_at": wb.now(),
        "truth_model": "Derived projection only. Markdown, JSON, JSONL ledgers, notes, packets, and decisions remain canonical.",
        "nodes": list(builder.nodes.values()),
        "edges": list(builder.edges.values()),
        "warnings": builder.warnings,
        "ledger_audit": audit,
    }
    return graph


def write_sqlite(work_root: Path, graph: Dict[str, Any]) -> str:
    db_path = work_root / ".tyf" / GRAPH_SQLITE
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    try:
        cur = conn.cursor()
        cur.executescript(
            """
            DROP TABLE IF EXISTS nodes;
            DROP TABLE IF EXISTS edges;
            DROP TABLE IF EXISTS builds;
            CREATE TABLE nodes(id TEXT PRIMARY KEY, kind TEXT, label TEXT, provenance TEXT, source_path TEXT, source_hash TEXT, attrs_json TEXT);
            CREATE TABLE edges(id TEXT PRIMARY KEY, from_id TEXT, to_id TEXT, kind TEXT, provenance TEXT, confidence REAL, source_path TEXT, source_hash TEXT, attrs_json TEXT);
            CREATE TABLE builds(id TEXT PRIMARY KEY, created_at TEXT, nodes_count INTEGER, edges_count INTEGER, warnings_json TEXT);
            """
        )
        for n in graph.get("nodes", []):
            cur.execute("INSERT OR REPLACE INTO nodes VALUES (?,?,?,?,?,?,?)", (n.get("id"), n.get("kind"), n.get("label"), n.get("provenance"), n.get("source_path"), n.get("source_hash"), json.dumps(n.get("attrs", {}), ensure_ascii=False, sort_keys=True)))
        for e in graph.get("edges", []):
            cur.execute("INSERT OR REPLACE INTO edges VALUES (?,?,?,?,?,?,?,?,?)", (e.get("id"), e.get("from"), e.get("to"), e.get("kind"), e.get("provenance"), e.get("confidence"), e.get("source_path"), e.get("source_hash"), json.dumps(e.get("attrs", {}), ensure_ascii=False, sort_keys=True)))
        build_id = "build-" + wb.now_id() + "-" + wb.short_hash(str(len(graph.get("nodes", []))), str(len(graph.get("edges", []))))
        cur.execute("INSERT INTO builds VALUES (?,?,?,?,?)", (build_id, graph.get("generated_at"), len(graph.get("nodes", [])), len(graph.get("edges", [])), json.dumps(graph.get("warnings", []), ensure_ascii=False)))
        conn.commit()
    finally:
        conn.close()
    return db_path.relative_to(work_root).as_posix()


def write_outputs(work_id: str, work_root: Path, root: Path, include_sqlite: bool = False) -> Dict[str, Any]:
    graph = build_graph(work_id, work_root, root)
    out_dir = work_root / ".review" / "surface"
    out_dir.mkdir(parents=True, exist_ok=True)
    graph_path = out_dir / GRAPH_JSON
    report_json_path = out_dir / GRAPH_REPORT_JSON
    report_md_path = out_dir / GRAPH_REPORT_MD
    wb.write_json(graph_path, graph)
    report = {
        "kind": "tyf-graph-build-report",
        "generated_at": graph["generated_at"],
        "nodes": len(graph.get("nodes", [])),
        "edges": len(graph.get("edges", [])),
        "ledger_totals": graph.get("ledger_audit", {}).get("totals", {}),
        "warnings": graph.get("warnings", []),
        "sqlite": "not-written",
    }
    if include_sqlite:
        report["sqlite"] = write_sqlite(work_root, graph)
    wb.write_json(report_json_path, report)
    md = f"""# TYF graph build report

Generated: {report['generated_at']}

This graph is a rebuildable projection. It is not a source of truth.

- nodes: {report['nodes']}
- edges: {report['edges']}
- JSON graph: `{graph_path.relative_to(work_root).as_posix()}`
- SQLite cache: {report['sqlite']}

## JSONL ledger audit

- files: {report['ledger_totals'].get('files', 0)}
- records: {report['ledger_totals'].get('records', 0)}
- invalid lines: {report['ledger_totals'].get('invalid_lines', 0)}
- hash-chain ledgers: {report['ledger_totals'].get('hash_chain_ledgers', 0)}
- append logs: {report['ledger_totals'].get('append_logs', 0)}
- mutable record stores: {report['ledger_totals'].get('mutable_record_stores', 0)}
- empty JSONL files: {report['ledger_totals'].get('empty', 0)}

## Rule

Deleting `.tyf/graph.sqlite` or `.review/surface/book-graph.json` must never delete author knowledge. Rebuild from Markdown, notes, packets, status files, and ledgers.
"""
    wb.atomic_write(report_md_path, md)
    wb.log_event(root, "graph-projection", work_id, f"nodes={report['nodes']} edges={report['edges']}")
    return {
        "status": "graph-written",
        "graph": graph_path.relative_to(work_root).as_posix(),
        "report_json": report_json_path.relative_to(work_root).as_posix(),
        "report_markdown": report_md_path.relative_to(work_root).as_posix(),
        "sqlite": report["sqlite"],
        "nodes": report["nodes"],
        "edges": report["edges"],
    }


def run(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Build TYF's provenance-first graph projection and JSONL ledger audit")
    parser.add_argument("work", nargs="?", default=None)
    parser.add_argument("--sqlite", action="store_true", help="also write a rebuildable SQLite query cache under .tyf/graph.sqlite")
    args = parser.parse_args(argv)
    work_id, work_root, root = resolve(args.work)
    result = write_outputs(work_id, work_root, root, include_sqlite=args.sqlite)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def main() -> None:
    raise SystemExit(run())


if __name__ == "__main__":
    main()
