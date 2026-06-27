#!/usr/bin/env python3
"""TYF continuity review.

A deterministic, author-owned continuity layer above concept review. It catches
promise/payoff gaps, open threads, register drift, scope leaks, reader-state
assumptions, and doctrine-vs-implementation confusion. Findings are prompts for
author review, not verdicts.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import sys
from typing import Any, Dict, Iterable, List, Optional, Tuple

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import tyf_workbench_v06 as wb  # noqa: E402
import tyf_concept_review as concept_review  # noqa: E402

PROMISES = "knowledge-base/reader-promises.jsonl"
OPEN_THREADS = "knowledge-base/open-threads.jsonl"
REGISTER_RULES = "knowledge-base/register-rules.jsonl"
SCOPE_RULES = "knowledge-base/scope-rules.jsonl"
DECISIONS = ".review/surface/continuity-decisions.jsonl"
REVIEW_JSON = "continuity-review.json"
REVIEW_MD = "continuity-review.md"

ASSUMPTION_MARKERS = [
    "as we saw",
    "as discussed",
    "of course",
    "obviously",
    "clearly",
    "it follows",
    "therefore",
    "as you remember",
]

IMPLEMENTATION_MARKERS = [
    "jsonl",
    "sqlite",
    "api",
    "endpoint",
    "schema",
    "token",
    "server",
    "hash",
    "cli",
]

DOCTRINE_MARKERS = [
    "author is the source",
    "never becomes the writer",
    "gate",
    "manuscript remains protected",
    "local-first",
    "author-owned",
]


def resolve(work_arg: Optional[str]) -> Tuple[str, Path, Path]:
    work_id, work_root, root = wb.resolve_work(work_arg)
    wb.ensure_workbench_shape(work_root, root)
    return work_id, work_root, root


def read_jsonl(path: Path) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for line in wb.read_text(path).splitlines():
        if not line.strip():
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(item, dict):
            out.append(item)
    return out


def norm(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def contains_phrase(text: str, phrase: str) -> bool:
    return norm(phrase) in norm(text)


def iter_lines(work_root: Path) -> List[Dict[str, Any]]:
    return list(concept_review.iter_source_lines(work_root))


def load_registry(work_root: Path, rel: str) -> List[Dict[str, Any]]:
    return read_jsonl(work_root / rel)


def first_match(lines: List[Dict[str, Any]], phrases: List[str]) -> Optional[Dict[str, Any]]:
    for line in lines:
        for phrase in phrases:
            if phrase and contains_phrase(line["quote"], phrase):
                return {**line, "matched_phrase": phrase}
    return None


def later_match(lines: List[Dict[str, Any]], after: Optional[Dict[str, Any]], phrases: List[str]) -> Optional[Dict[str, Any]]:
    for line in lines:
        if after:
            if line["path"] < after["path"]:
                continue
            if line["path"] == after["path"] and line["line"] <= after["line"]:
                continue
        for phrase in phrases:
            if phrase and contains_phrase(line["quote"], phrase):
                return {**line, "matched_phrase": phrase}
    return None


def issue(kind: str, severity: str, message: str, examples: List[Dict[str, Any]], registry: str = "", item_id: str = "") -> Dict[str, Any]:
    return {
        "kind": kind,
        "severity": severity,
        "message": message,
        "examples": examples[:5],
        "registry": registry,
        "item_id": item_id,
    }


def review_promises(work_root: Path, lines: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for item in load_registry(work_root, PROMISES):
        item_id = str(item.get("id") or item.get("promise") or "promise")
        status = str(item.get("status") or "open")
        if status in ("paid", "resolved", "do-not-resolve"):
            continue
        promise_terms = [str(x) for x in item.get("promise_terms", [])] or [str(item.get("promise") or "")]
        payoff_terms = [str(x) for x in item.get("payoff_terms", [])]
        intro = first_match(lines, promise_terms)
        payoff = later_match(lines, intro, payoff_terms)
        if intro and not payoff and payoff_terms:
            out.append(issue("unpaid-promise", "review", f"Reader promise may be unpaid: {item_id}", [intro], PROMISES, item_id))
        elif intro and payoff:
            out.append(issue("resolved-promise", "info", f"Reader promise appears to have a payoff: {item_id}", [intro, payoff], PROMISES, item_id))
    return out


def review_open_threads(work_root: Path, lines: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for item in load_registry(work_root, OPEN_THREADS):
        item_id = str(item.get("id") or item.get("thread") or "thread")
        status = str(item.get("status") or "needs-resolution")
        terms = [str(x) for x in item.get("terms", [])] or [str(item.get("thread") or "")]
        resolution_terms = [str(x) for x in item.get("resolution_terms", [])]
        match = first_match(lines, terms)
        resolved = later_match(lines, match, resolution_terms)
        if status == "intentional-open":
            if match:
                out.append(issue("intentional-open-thread", "info", f"Intentional open thread is present: {item_id}", [match], OPEN_THREADS, item_id))
        elif match and not resolved:
            out.append(issue("dangling-open-thread", "review", f"Open thread may still need resolution: {item_id}", [match], OPEN_THREADS, item_id))
    return out


def review_register(work_root: Path, lines: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for item in load_registry(work_root, REGISTER_RULES):
        item_id = str(item.get("id") or item.get("register") or "register")
        avoid = [str(x) for x in item.get("avoid", [])]
        for line in lines:
            for phrase in avoid:
                if phrase and contains_phrase(line["quote"], phrase):
                    out.append(issue("register-drift", "review", f"Register rule '{item_id}' avoids phrase: {phrase}", [{**line, "matched_phrase": phrase}], REGISTER_RULES, item_id))
    return out


def review_scope(work_root: Path, lines: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for item in load_registry(work_root, SCOPE_RULES):
        item_id = str(item.get("id") or item.get("scope") or "scope")
        leak_terms = [str(x) for x in item.get("leak_terms", [])]
        allowed_paths = [str(x) for x in item.get("allowed_paths", [])]
        for line in lines:
            if allowed_paths and any(line["path"].startswith(prefix) for prefix in allowed_paths):
                continue
            for phrase in leak_terms:
                if phrase and contains_phrase(line["quote"], phrase):
                    out.append(issue("scope-leak", "review", f"Possible scope leak for '{item_id}': {phrase}", [{**line, "matched_phrase": phrase}], SCOPE_RULES, item_id))
    return out


def review_reader_assumptions(lines: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for line in lines:
        for phrase in ASSUMPTION_MARKERS:
            if contains_phrase(line["quote"], phrase):
                out.append(issue("reader-state-assumption", "low", f"Line assumes reader state: {phrase}", [{**line, "matched_phrase": phrase}]))
    return out


def review_doctrine_implementation(lines: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for line in lines:
        q = line["quote"]
        has_doctrine = any(contains_phrase(q, marker) for marker in DOCTRINE_MARKERS)
        has_impl = any(contains_phrase(q, marker) for marker in IMPLEMENTATION_MARKERS)
        if has_doctrine and has_impl:
            out.append(issue("doctrine-vs-implementation-confusion", "review", "Line mixes doctrine and implementation language.", [line]))
    return out


def decisions_by_issue(work_root: Path) -> Dict[str, Dict[str, Any]]:
    out: Dict[str, Dict[str, Any]] = {}
    for item in read_jsonl(work_root / DECISIONS):
        key = str(item.get("issue_key") or "")
        if key:
            out[key] = item
    return out


def issue_key(item: Dict[str, Any]) -> str:
    first = item.get("examples", [{}])[0]
    return wb.short_hash(item.get("kind", ""), item.get("message", ""), first.get("path", ""), str(first.get("line", "")), first.get("line_hash", ""))


def build_review(work_root: Path) -> Dict[str, Any]:
    lines = iter_lines(work_root)
    concept_index = concept_review.build_index(work_root)
    concept_findings = concept_review.build_review(concept_index).get("issues", [])
    issues: List[Dict[str, Any]] = []
    issues.extend(concept_findings)
    issues.extend(review_promises(work_root, lines))
    issues.extend(review_open_threads(work_root, lines))
    issues.extend(review_register(work_root, lines))
    issues.extend(review_scope(work_root, lines))
    issues.extend(review_reader_assumptions(lines))
    issues.extend(review_doctrine_implementation(lines))
    decisions = decisions_by_issue(work_root)
    for item in issues:
        key = issue_key(item)
        item["issue_key"] = key
        if key in decisions:
            item["decision"] = decisions[key]
    return {
        "kind": "tyf-continuity-review",
        "generated_at": wb.now(),
        "summary": {
            "issues": len(issues),
            "source_lines": len(lines),
            "concept_issues": len(concept_findings),
            "registries": {
                "reader_promises": len(load_registry(work_root, PROMISES)),
                "open_threads": len(load_registry(work_root, OPEN_THREADS)),
                "register_rules": len(load_registry(work_root, REGISTER_RULES)),
                "scope_rules": len(load_registry(work_root, SCOPE_RULES)),
            },
        },
        "issues": issues,
        "rule": "Findings are prompts for author review, not verdicts.",
    }


def write_outputs(work_root: Path) -> Dict[str, Any]:
    review = build_review(work_root)
    out_dir = work_root / ".review" / "surface"
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "continuity-review.json"
    md_path = out_dir / "continuity-review.md"
    wb.write_json(json_path, review)
    lines = [
        "# TYF continuity review",
        "",
        f"Generated: {review['generated_at']}",
        "",
        "Findings are prompts for author review, not verdicts.",
        "",
        f"- source lines scanned: {review['summary']['source_lines']}",
        f"- issues: {review['summary']['issues']}",
        f"- concept issues included: {review['summary']['concept_issues']}",
        "",
        "## Registries",
        "",
    ]
    for name, count in review["summary"]["registries"].items():
        lines.append(f"- {name}: {count}")
    lines.append("")
    for item in review["issues"][:120]:
        lines += [f"## {item['kind']} — {item.get('severity', 'review')}", "", item["message"], "", f"issue_key: `{item['issue_key']}`", ""]
        for ex in item.get("examples", [])[:5]:
            if ex.get("path"):
                lines.append(f"- `{ex['path']}:{ex.get('line')}` {ex.get('quote')}")
        lines.append("")
    wb.atomic_write(md_path, "\n".join(lines))
    return {"status": "continuity-review-written", "review_json": json_path.relative_to(work_root).as_posix(), "review_markdown": md_path.relative_to(work_root).as_posix(), "issues": review["summary"]["issues"]}


def run(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Review book continuity: concepts, promises, open threads, register, scope, and reader assumptions")
    parser.add_argument("work", nargs="?", default=None)
    args = parser.parse_args(argv)
    _work_id, work_root, _root = resolve(args.work)
    print(json.dumps(write_outputs(work_root), ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def main() -> None:
    raise SystemExit(run())


if __name__ == "__main__":
    main()
