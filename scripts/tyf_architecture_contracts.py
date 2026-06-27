#!/usr/bin/env python3
"""Executable architecture contracts for TYF RC hardening.

These checks intentionally stay simple and stdlib-only. They are not a security
scanner; they are guard rails for the local single-author architecture.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from typing import Dict, List, Optional

PACK_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = PACK_ROOT / "scripts"

STORAGE_CLASSES: Dict[str, List[str]] = {
    "canonical-prose": ["drafts/**/*.md", "manuscript/**/*.md"],
    "canonical-author-record": [
        "knowledge-base/concepts.jsonl",
        "knowledge-base/reader-promises.jsonl",
        "knowledge-base/open-threads.jsonl",
        "knowledge-base/register-rules.jsonl",
        "knowledge-base/scope-rules.jsonl",
        "knowledge-base/voice-map.jsonl",
        "knowledge-base/typography-style.jsonl",
    ],
    "mutable-record-store": ["knowledge-base/author-notes.jsonl"],
    "hash-chain-ledger": [".tyf/events.jsonl"],
    "append-log": [".review/surface/*.jsonl", ".review/conflicts/**/*.jsonl"],
    "generated-review": [".review/surface/*-review.*", ".review/surface/*-report.*", ".review/surface/book-graph.json"],
    "rebuildable-cache": [".tyf/graph.sqlite"],
    "recovery-artifact": ["drafts/.recovery-copies/**/*.md", ".review/conflicts/**"],
}

FORBIDDEN_MANUSCRIPT_ROUTE_PATTERNS = [
    "/api/save-manuscript",
    "/api/write-manuscript",
    "save_manuscript",
    "write_manuscript",
]

ALLOWED_MANUSCRIPT_WRITE_FUNCTIONS = {
    "cmd_write",
    "_write_decision_to_manuscript",
    "_adopt_direct_manuscript_edit",
}


def storage_contract() -> Dict[str, List[str]]:
    return STORAGE_CLASSES


def script_files() -> List[Path]:
    return sorted(path for path in SCRIPTS.glob("tyf*.py") if path.is_file())


def forbidden_route_hits(root: Path = PACK_ROOT) -> List[Dict[str, str]]:
    hits: List[Dict[str, str]] = []
    for path in sorted((root / "scripts").glob("tyf*.py")):
        text = path.read_text(encoding="utf-8", errors="replace")
        for marker in FORBIDDEN_MANUSCRIPT_ROUTE_PATTERNS:
            if marker in text:
                hits.append({"path": path.relative_to(root).as_posix(), "marker": marker})
    return hits


def suspicious_direct_manuscript_writes(root: Path = PACK_ROOT) -> List[Dict[str, str]]:
    """Find obvious direct writes to manuscript/ outside known Gate helpers.

    This is a conservative string-level guard. It is meant to catch accidental
    new surfaces, not prove full semantic safety.
    """
    hits: List[Dict[str, str]] = []
    write_re = re.compile(r"(atomic_write|write|append|open)\s*\([^\n]*(manuscript/|['\"]manuscript['\"])")
    current_func = ""
    for path in sorted((root / "scripts").glob("tyf*.py")):
        for line_no, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), start=1):
            m = re.match(r"def\s+([A-Za-z0-9_]+)\s*\(", line)
            if m:
                current_func = m.group(1)
            if write_re.search(line) and current_func not in ALLOWED_MANUSCRIPT_WRITE_FUNCTIONS:
                hits.append({"path": path.relative_to(root).as_posix(), "line": str(line_no), "function": current_func, "text": line.strip()[:200]})
    return hits


def run(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Run TYF architecture contract checks")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    route_hits = forbidden_route_hits()
    write_hits = suspicious_direct_manuscript_writes()
    result = {
        "status": "pass" if not route_hits and not write_hits else "fail",
        "storage_classes": STORAGE_CLASSES,
        "forbidden_route_hits": route_hits,
        "suspicious_manuscript_writes": write_hits,
    }
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(f"TYF architecture contracts: {result['status']}")
        for hit in route_hits:
            print(f"forbidden route marker: {hit}")
        for hit in write_hits:
            print(f"suspicious manuscript write: {hit}")
    return 0 if result["status"] == "pass" else 1


def main() -> None:
    raise SystemExit(run())


if __name__ == "__main__":
    main()
