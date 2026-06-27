#!/usr/bin/env python3
"""Concept-level review for TYF Workbench.

This is the author-facing value layer on top of the structural graph: find exact
lines where a concept is named differently, a retired term remains, or a claim
may have drifted. Findings are review prompts, not verdicts.
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

CONCEPTS_PATH = "knowledge-base/concepts.jsonl"
INDEX_JSON = "concept-index.json"
REVIEW_JSON = "concept-review.json"
REVIEW_MD = "concept-review.md"

DEFAULT_STOP = {
    "about", "after", "again", "also", "because", "before", "being", "between",
    "chapter", "draft", "every", "first", "from", "have", "into", "itself", "line",
    "manuscript", "more", "never", "only", "other", "should", "source", "their", "there",
    "these", "thing", "this", "those", "through", "under", "where", "which", "while", "with",
    "without", "would", "writer", "writing",
}

OPPOSITION_PAIRS = [
    ("can", "cannot"),
    ("can", "can't"),
    ("is", "is not"),
    ("are", "are not"),
    ("must", "must not"),
    ("should", "should not"),
    ("always", "never"),
    ("local", "cloud"),
    ("author", "writer"),
    ("draft", "manuscript"),
]

DEF_PATTERNS = [
    re.compile(r"\b(?P<concept>[A-Z][A-Za-z0-9 _-]{2,40})\s+is\s+(?P<body>.+)", re.UNICODE),
    re.compile(r"\b(?P<concept>[A-Za-z0-9 _-]{3,40})\s+means\s+(?P<body>.+)", re.UNICODE),
    re.compile(r"\bwe call\s+(?P<concept>[A-Za-z0-9 _-]{3,40})\s+(?P<body>.+)", re.UNICODE | re.IGNORECASE),
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


def normalize(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def phrase_re(phrase: str) -> re.Pattern:
    escaped = re.escape(normalize(phrase)).replace("\\ ", r"\s+")
    return re.compile(r"(?<![a-z0-9])" + escaped + r"(?![a-z0-9])", re.IGNORECASE)


def iter_source_lines(work_root: Path) -> Iterable[Dict[str, Any]]:
    for base_name in ("drafts", "manuscript"):
        base = work_root / base_name
        if not base.is_dir():
            continue
        for path in wb.markdown_files(base):
            rel = path.relative_to(work_root).as_posix()
            text = wb.read_text(path)
            for idx, line in enumerate(text.splitlines(), start=1):
                stripped = line.strip()
                if not stripped:
                    continue
                yield {
                    "path": rel,
                    "line": idx,
                    "side": base_name,
                    "quote": stripped,
                    "line_hash": wb.short_hash(rel, str(idx), stripped),
                }


def load_concepts(work_root: Path) -> List[Dict[str, Any]]:
    path = work_root / CONCEPTS_PATH
    concepts = []
    for item in read_jsonl(path):
        canonical = str(item.get("canonical") or item.get("id") or "").strip()
        if not canonical:
            continue
        variants = [str(v).strip() for v in item.get("variants", []) if str(v).strip()]
        retired = [str(v).strip() for v in item.get("retired", []) if str(v).strip()]
        concepts.append({
            "canonical": canonical,
            "variants": sorted(set([canonical] + variants)),
            "retired": sorted(set(retired)),
            "note": str(item.get("note") or ""),
            "source_path": CONCEPTS_PATH,
        })
    return concepts


def candidate_terms(lines: List[Dict[str, Any]], limit: int = 80) -> List[Dict[str, Any]]:
    counts: Dict[str, Dict[str, Any]] = {}
    for line in lines:
        words = re.findall(r"[A-Za-z][A-Za-z0-9'-]{3,}", line["quote"])
        for word in words:
            norm = normalize(word)
            if norm in DEFAULT_STOP or len(norm) < 4:
                continue
            rec = counts.setdefault(norm, {"term": norm, "count": 0, "examples": []})
            rec["count"] += 1
            if len(rec["examples"]) < 3:
                rec["examples"].append({"path": line["path"], "line": line["line"], "quote": line["quote"]})
    return sorted([v for v in counts.values() if v["count"] >= 2], key=lambda x: (-x["count"], x["term"]))[:limit]


def extract_definitions(lines: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    defs: Dict[str, List[Dict[str, Any]]] = {}
    for line in lines:
        quote = line["quote"]
        for pattern in DEF_PATTERNS:
            m = pattern.search(quote)
            if not m:
                continue
            concept = normalize(m.group("concept"))
            if len(concept) < 3 or concept in DEFAULT_STOP:
                continue
            defs.setdefault(concept, []).append({"path": line["path"], "line": line["line"], "quote": quote, "line_hash": line["line_hash"]})
    return defs


def build_index(work_root: Path) -> Dict[str, Any]:
    lines = list(iter_source_lines(work_root))
    concepts = load_concepts(work_root)
    matches: List[Dict[str, Any]] = []
    for concept in concepts:
        phrases = [("canonical-or-variant", p) for p in concept["variants"]] + [("retired", p) for p in concept["retired"]]
        for role, phrase in phrases:
            rx = phrase_re(phrase)
            for line in lines:
                if rx.search(normalize(line["quote"])):
                    matches.append({
                        "canonical": concept["canonical"],
                        "phrase": phrase,
                        "role": role,
                        "path": line["path"],
                        "line": line["line"],
                        "quote": line["quote"],
                        "line_hash": line["line_hash"],
                    })
    return {
        "kind": "tyf-concept-index",
        "generated_at": wb.now(),
        "concept_registry_path": CONCEPTS_PATH,
        "concepts": concepts,
        "matches": matches,
        "candidate_terms": candidate_terms(lines),
        "definitions": extract_definitions(lines),
        "source_lines": len(lines),
    }


def find_variant_issues(index: Dict[str, Any]) -> List[Dict[str, Any]]:
    issues: List[Dict[str, Any]] = []
    by_concept: Dict[str, Dict[str, List[Dict[str, Any]]]] = {}
    for m in index["matches"]:
        by_concept.setdefault(m["canonical"], {}).setdefault(m["phrase"], []).append(m)
    for canonical, phrase_map in by_concept.items():
        if len(phrase_map) > 1:
            issues.append({
                "kind": "concept-variant",
                "severity": "review",
                "concept": canonical,
                "message": f"Concept appears under {len(phrase_map)} names.",
                "examples": [items[0] for items in phrase_map.values()],
            })
    return issues


def find_retired_terms(index: Dict[str, Any]) -> List[Dict[str, Any]]:
    return [
        {
            "kind": "retired-term-used",
            "severity": "likely-fix",
            "concept": m["canonical"],
            "message": f"Retired term still appears: {m['phrase']}",
            "examples": [m],
        }
        for m in index["matches"]
        if m["role"] == "retired"
    ]


def find_opposition_drift(index: Dict[str, Any]) -> List[Dict[str, Any]]:
    issues: List[Dict[str, Any]] = []
    by_concept: Dict[str, List[Dict[str, Any]]] = {}
    for m in index["matches"]:
        by_concept.setdefault(m["canonical"], []).append(m)
    for canonical, matches in by_concept.items():
        for left, right in OPPOSITION_PAIRS:
            left_hits = [m for m in matches if re.search(r"\b" + re.escape(left) + r"\b", m["quote"], re.IGNORECASE)]
            right_hits = [m for m in matches if re.search(r"\b" + re.escape(right) + r"\b", m["quote"], re.IGNORECASE)]
            if left_hits and right_hits:
                issues.append({
                    "kind": "opposition-drift",
                    "severity": "review",
                    "concept": canonical,
                    "message": f"Concept appears near both '{left}' and '{right}'.",
                    "examples": [left_hits[0], right_hits[0]],
                })
    return issues


def find_definition_drift(index: Dict[str, Any]) -> List[Dict[str, Any]]:
    issues: List[Dict[str, Any]] = []
    for concept, defs in index["definitions"].items():
        if len(defs) > 1:
            issues.append({
                "kind": "definition-drift",
                "severity": "review",
                "concept": concept,
                "message": f"Multiple definition-like lines found for '{concept}'.",
                "examples": defs[:5],
            })
    return issues


def find_unregistered_candidates(index: Dict[str, Any]) -> List[Dict[str, Any]]:
    registered = {normalize(c["canonical"]) for c in index.get("concepts", [])}
    out = []
    for c in index.get("candidate_terms", [])[:30]:
        if c["term"] not in registered:
            out.append({
                "kind": "unregistered-repeated-term",
                "severity": "low",
                "concept": c["term"],
                "message": f"Repeated term not in concept registry: {c['term']} ({c['count']} hits).",
                "examples": c["examples"],
            })
    return out


def build_review(index: Dict[str, Any]) -> Dict[str, Any]:
    issues = []
    issues.extend(find_retired_terms(index))
    issues.extend(find_variant_issues(index))
    issues.extend(find_opposition_drift(index))
    issues.extend(find_definition_drift(index))
    issues.extend(find_unregistered_candidates(index))
    return {
        "kind": "tyf-concept-review",
        "generated_at": wb.now(),
        "summary": {
            "issues": len(issues),
            "concepts": len(index.get("concepts", [])),
            "matches": len(index.get("matches", [])),
            "source_lines": index.get("source_lines", 0),
        },
        "issues": issues,
        "rule": "Findings are prompts for author review, not verdicts.",
    }


def write_outputs(work_root: Path) -> Dict[str, Any]:
    index = build_index(work_root)
    review = build_review(index)
    out_dir = work_root / ".review" / "surface"
    out_dir.mkdir(parents=True, exist_ok=True)
    index_path = out_dir / INDEX_JSON
    review_path = out_dir / REVIEW_JSON
    md_path = out_dir / REVIEW_MD
    wb.write_json(index_path, index)
    wb.write_json(review_path, review)
    lines = ["# TYF concept review", "", f"Generated: {review['generated_at']}", "", "Findings are prompts for author review, not verdicts.", "", f"- source lines scanned: {review['summary']['source_lines']}", f"- registered concepts: {review['summary']['concepts']}", f"- concept matches: {review['summary']['matches']}", f"- issues: {review['summary']['issues']}", ""]
    if not index.get("concepts"):
        lines += ["## No concept registry yet", "", f"Create `{CONCEPTS_PATH}` to catch renames and retired terms precisely.", ""]
    for issue in review["issues"][:80]:
        lines += [f"## {issue['kind']}: {issue['concept']}", "", issue["message"], ""]
        for ex in issue.get("examples", [])[:5]:
            lines.append(f"- `{ex['path']}:{ex['line']}` {ex['quote']}")
        lines.append("")
    wb.atomic_write(md_path, "\n".join(lines))
    return {
        "status": "concept-review-written",
        "index": index_path.relative_to(work_root).as_posix(),
        "review_json": review_path.relative_to(work_root).as_posix(),
        "review_markdown": md_path.relative_to(work_root).as_posix(),
        "issues": review["summary"]["issues"],
    }


def run(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Review concept-level naming, contradiction, and drift in TYF drafts/manuscript")
    parser.add_argument("work", nargs="?", default=None)
    args = parser.parse_args(argv)
    _work_id, work_root, _root = resolve(args.work)
    print(json.dumps(write_outputs(work_root), ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def main() -> None:
    raise SystemExit(run())


if __name__ == "__main__":
    main()
