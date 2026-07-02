#!/usr/bin/env python3
"""Executable architecture contracts for TYF RC hardening.

These checks intentionally stay simple and stdlib-only. They are not a security
scanner; they are guard rails for the local single-author architecture.
"""

from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path
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
    "append-log": [".review/workbench/*.jsonl", ".review/conflicts/**/*.jsonl"],
    "generated-review": [".review/workbench/*-review.*", ".review/workbench/*-report.*", ".review/workbench/book-graph.json"],
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
        if path.name == Path(__file__).name:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for marker in FORBIDDEN_MANUSCRIPT_ROUTE_PATTERNS:
            if marker in text:
                hits.append({"path": path.relative_to(root).as_posix(), "marker": marker})
    return hits


def _call_name(node: ast.Call) -> str:
    func = node.func
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        return func.attr
    return ""


def _literal_path_mentions_manuscript(node: ast.AST) -> bool:
    """Return true when an expression visibly names manuscript as a path part."""
    for child in ast.walk(node):
        if isinstance(child, ast.Constant) and isinstance(child.value, str):
            parts = [part for part in child.value.replace("\\", "/").split("/") if part]
            if "manuscript" in parts:
                return True
    return False


class ManuscriptWriteVisitor(ast.NodeVisitor):
    def __init__(self, root: Path, path: Path, source: str) -> None:
        self.root = root
        self.path = path
        self.lines = source.splitlines()
        self.function_stack: List[str] = []
        self.hits: List[Dict[str, str]] = []

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self.function_stack.append(node.name)
        self.generic_visit(node)
        self.function_stack.pop()

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self.function_stack.append(node.name)
        self.generic_visit(node)
        self.function_stack.pop()

    def visit_Call(self, node: ast.Call) -> None:
        name = _call_name(node)
        target: Optional[ast.AST] = None
        if isinstance(node.func, ast.Attribute) and name in {"write_text", "write_bytes", "open"}:
            target = node.func.value
        elif isinstance(node.func, ast.Name) and name in {"atomic_write", "write", "append", "open"} and node.args:
            target = node.args[0]

        current_func = self.function_stack[-1] if self.function_stack else ""
        if (
            target is not None
            and current_func not in ALLOWED_MANUSCRIPT_WRITE_FUNCTIONS
            and _literal_path_mentions_manuscript(target)
        ):
            line = self.lines[node.lineno - 1].strip() if 0 < node.lineno <= len(self.lines) else ""
            self.hits.append({
                "path": self.path.relative_to(self.root).as_posix(),
                "line": str(node.lineno),
                "function": current_func,
                "text": line[:200],
            })
        self.generic_visit(node)


def suspicious_direct_manuscript_writes(root: Path = PACK_ROOT) -> List[Dict[str, str]]:
    """Find obvious direct writes to manuscript/ outside known Gate helpers.

    This is a conservative AST guard. It is meant to catch accidental new
    surfaces, not prove full semantic safety.
    """
    hits: List[Dict[str, str]] = []
    for path in sorted((root / "scripts").glob("tyf*.py")):
        source = path.read_text(encoding="utf-8", errors="replace")
        try:
            tree = ast.parse(source, filename=str(path))
        except SyntaxError as exc:
            hits.append({"path": path.relative_to(root).as_posix(), "line": str(exc.lineno or 0), "function": "", "text": f"syntax error: {exc.msg}"})
            continue
        visitor = ManuscriptWriteVisitor(root, path, source)
        visitor.visit(tree)
        hits.extend(visitor.hits)
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
