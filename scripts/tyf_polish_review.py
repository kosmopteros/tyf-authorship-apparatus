#!/usr/bin/env python3
"""Near-final polish review for TYF books.

This is a non-rewriting editor/typographer pass. It checks voice zones,
register leaks, narration-lane mismatches, and house-style typography rules.
It writes review reports and candidate observations only; it never edits prose.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import sys
from typing import Any, Dict, List, Optional

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import tyf_workbench_v06 as wb  # noqa: E402
import tyf_concept_review as concept_review  # noqa: E402

VOICE_MAP = "knowledge-base/voice-map.jsonl"
TYPOGRAPHY_STYLE = "knowledge-base/typography-style.jsonl"
POLISH_JSON = "polish-review.json"
POLISH_MD = "polish-review.md"

FIRST_PERSON_RE = re.compile(r"\b(I|me|my|mine|myself|we|us|our|ours)\b")
THIRD_PERSON_SELF_RE = re.compile(r"\b(he|she|they|him|her|them|his|hers|their)\b", re.IGNORECASE)


def resolve(work_arg: Optional[str]) -> tuple[str, Path, Path]:
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


def line_key(issue: Dict[str, Any]) -> str:
    ex = issue.get("examples", [{}])[0]
    return wb.short_hash(issue.get("kind", ""), issue.get("message", ""), ex.get("path", ""), str(ex.get("line", "")), ex.get("line_hash", ""))


def issue(kind: str, severity: str, message: str, examples: List[Dict[str, Any]], registry: str = "", rule_id: str = "", suggested: str = "") -> Dict[str, Any]:
    out = {
        "kind": kind,
        "severity": severity,
        "message": message,
        "examples": examples[:5],
        "registry": registry,
        "rule_id": rule_id,
        "suggested": suggested,
    }
    out["issue_key"] = line_key(out)
    return out


def path_matches(path: str, prefixes: List[str]) -> bool:
    return any(path.startswith(prefix) for prefix in prefixes)


def load_voice_zones(work_root: Path) -> List[Dict[str, Any]]:
    zones = []
    for item in read_jsonl(work_root / VOICE_MAP):
        paths = [str(p) for p in item.get("paths", []) if str(p)]
        if not paths:
            continue
        zones.append({
            "id": str(item.get("id") or item.get("voice") or "voice-zone"),
            "paths": paths,
            "person": str(item.get("person") or "mixed").lower(),
            "register": str(item.get("register") or ""),
            "voice": str(item.get("voice") or ""),
            "avoid": [str(x) for x in item.get("avoid", []) if str(x)],
            "allow": [str(x) for x in item.get("allow", []) if str(x)],
            "note": str(item.get("note") or ""),
        })
    return zones


def zones_for(path: str, zones: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [zone for zone in zones if path_matches(path, zone["paths"])]


def review_voice(work_root: Path, lines: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    zones = load_voice_zones(work_root)
    issues: List[Dict[str, Any]] = []
    for line in lines:
        active = zones_for(line["path"], zones)
        for zone in active:
            quote = line["quote"]
            if zone["person"] == "third" and FIRST_PERSON_RE.search(quote):
                issues.append(issue("narration-lane-mismatch", "review", f"First-person language appears in third-person zone '{zone['id']}'.", [line], VOICE_MAP, zone["id"]))
            if zone["person"] == "first" and quote.lower().startswith(("he ", "she ", "they ")):
                issues.append(issue("narration-lane-mismatch", "low", f"Line may drift away from first-person zone '{zone['id']}'.", [line], VOICE_MAP, zone["id"]))
            for avoid in zone["avoid"]:
                if avoid.lower() in quote.lower():
                    issues.append(issue("register-leak", "review", f"Voice zone '{zone['id']}' avoids phrase: {avoid}", [{**line, "matched_phrase": avoid}], VOICE_MAP, zone["id"]))
    return issues


def load_typography_rules(work_root: Path) -> Dict[str, Any]:
    rules: Dict[str, Any] = {"capitalization": {}}
    for item in read_jsonl(work_root / TYPOGRAPHY_STYLE):
        rules.update(item)
        if isinstance(item.get("capitalization"), dict):
            rules.setdefault("capitalization", {}).update(item["capitalization"])
    return rules


def review_typography(work_root: Path, lines: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    rules = load_typography_rules(work_root)
    issues: List[Dict[str, Any]] = []
    dash = str(rules.get("dash") or "")
    ellipsis = str(rules.get("ellipsis") or "")
    capitalization = rules.get("capitalization") if isinstance(rules.get("capitalization"), dict) else {}
    for line in lines:
        quote = line["quote"]
        if dash == "em-dash" and " -- " in quote:
            issues.append(issue("dash-style-drift", "likely-fix", "Double hyphen appears where house style expects em dash.", [line], TYPOGRAPHY_STYLE, "dash", "Replace spaced double hyphen with em dash if intentional."))
        if ellipsis == "single-character" and "..." in quote:
            issues.append(issue("ellipsis-style-drift", "likely-fix", "Three-dot ellipsis appears where house style expects single-character ellipsis.", [line], TYPOGRAPHY_STYLE, "ellipsis", "Replace ... with … if house style applies."))
        for term, canonical in capitalization.items():
            term_text = str(term)
            canonical_text = str(canonical)
            if not term_text or not canonical_text:
                continue
            pattern = re.compile(r"\b" + re.escape(term_text) + r"\b", re.IGNORECASE)
            for match in pattern.finditer(quote):
                actual = match.group(0)
                if actual != canonical_text:
                    issues.append(issue("term-capitalization-drift", "likely-fix", f"Term capitalization differs from house style: {actual} -> {canonical_text}", [line], TYPOGRAPHY_STYLE, term_text, canonical_text))
                    break
    return issues


def build_review(work_root: Path) -> Dict[str, Any]:
    lines = list(concept_review.iter_source_lines(work_root))
    issues = []
    issues.extend(review_voice(work_root, lines))
    issues.extend(review_typography(work_root, lines))
    return {
        "kind": "tyf-polish-review",
        "generated_at": wb.now(),
        "summary": {
            "issues": len(issues),
            "source_lines": len(lines),
            "voice_zones": len(load_voice_zones(work_root)),
            "typography_rules": 1 if (work_root / TYPOGRAPHY_STYLE).is_file() else 0,
        },
        "issues": issues,
        "rule": "Near-final polish review points and suggests minimal patches; it does not rewrite the book.",
    }


def write_outputs(work_root: Path) -> Dict[str, Any]:
    review = build_review(work_root)
    out_dir = work_root / ".review" / "surface"
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / POLISH_JSON
    md_path = out_dir / POLISH_MD
    wb.write_json(json_path, review)
    lines = [
        "# TYF polish review",
        "",
        f"Generated: {review['generated_at']}",
        "",
        "Near-final polish review points and suggests minimal patches; it does not rewrite the book.",
        "",
        f"- source lines scanned: {review['summary']['source_lines']}",
        f"- voice zones: {review['summary']['voice_zones']}",
        f"- issues: {review['summary']['issues']}",
        "",
    ]
    if not (work_root / VOICE_MAP).is_file():
        lines += ["## No voice map yet", "", f"Create `{VOICE_MAP}` to make voice evolution intentional instead of globally normalized.", ""]
    if not (work_root / TYPOGRAPHY_STYLE).is_file():
        lines += ["## No typography style yet", "", f"Create `{TYPOGRAPHY_STYLE}` to check dashes, ellipses, and term capitalization.", ""]
    for item in review["issues"][:120]:
        lines += [f"## {item['kind']} — {item.get('severity', 'review')}", "", item["message"], "", f"issue_key: `{item['issue_key']}`", ""]
        if item.get("suggested"):
            lines += ["Suggested minimal patch:", "", item["suggested"], ""]
        for ex in item.get("examples", [])[:5]:
            lines.append(f"- `{ex['path']}:{ex['line']}` {ex['quote']}")
        lines.append("")
    wb.atomic_write(md_path, "\n".join(lines))
    return {"status": "polish-review-written", "review_json": json_path.relative_to(work_root).as_posix(), "review_markdown": md_path.relative_to(work_root).as_posix(), "issues": review["summary"]["issues"]}


def run(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Run near-final voice and typography polish review")
    parser.add_argument("work", nargs="?", default=None)
    args = parser.parse_args(argv)
    _work_id, work_root, _root = resolve(args.work)
    print(json.dumps(write_outputs(work_root), ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def main() -> None:
    raise SystemExit(run())


if __name__ == "__main__":
    main()
