#!/usr/bin/env python3
"""RC doctor for a single-author TYF workspace.

The doctor verifies the private-RC safety surface: workspace shape, JSONL parse
health, event-ledger integrity, rebuildable review projections, and live
Workbench HTML generation. It writes a local report and never edits manuscript
prose.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Dict, List, Optional

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import tyf_concept_review as concept_review  # noqa: E402
import tyf_continuity_review as continuity_review  # noqa: E402
import tyf_graph_projection as graph_projection  # noqa: E402
import tyf_polish_review as polish_review  # noqa: E402
import tyf_workbench_live as live_workbench  # noqa: E402
import tyf_workbench_v06 as wb  # noqa: E402

REQUIRED_DIRS = ["drafts", "manuscript", ".tyf", ".review/surface", "knowledge-base"]
REQUIRED_FILES = ["WORKSPACE_STATE.yaml", "work.yaml"]


def check(name: str, ok: bool, detail: str = "", severity: str = "error") -> Dict[str, Any]:
    return {"name": name, "ok": bool(ok), "detail": detail, "severity": severity}


def parse_jsonl(path: Path) -> Dict[str, Any]:
    invalid = 0
    records = 0
    for line in wb.read_text(path).splitlines():
        if not line.strip():
            continue
        try:
            json.loads(line)
            records += 1
        except json.JSONDecodeError:
            invalid += 1
    return {"records": records, "invalid": invalid}


def registry_checks(work_root: Path) -> List[Dict[str, Any]]:
    checks = []
    for rel in [
        "knowledge-base/author-notes.jsonl",
        "knowledge-base/concepts.jsonl",
        "knowledge-base/reader-promises.jsonl",
        "knowledge-base/open-threads.jsonl",
        "knowledge-base/register-rules.jsonl",
        "knowledge-base/scope-rules.jsonl",
        "knowledge-base/voice-map.jsonl",
        "knowledge-base/typography-style.jsonl",
    ]:
        path = work_root / rel
        if not path.exists():
            checks.append(check("jsonl optional: " + rel, True, "absent", "info"))
            continue
        parsed = parse_jsonl(path)
        checks.append(check("jsonl parses: " + rel, parsed["invalid"] == 0, json.dumps(parsed), "error"))
    return checks


def build_checks(work_id: str, work_root: Path, root: Path) -> List[Dict[str, Any]]:
    checks = []
    try:
        graph = graph_projection.build_graph(work_id, work_root, root)
        checks.append(check("graph projection builds", graph.get("kind") == "tyf-book-graph", f"nodes={len(graph.get('nodes', []))} edges={len(graph.get('edges', []))}"))
    except Exception as exc:  # noqa: BLE001
        checks.append(check("graph projection builds", False, str(exc)))
    try:
        concept = concept_review.build_review(concept_review.build_index(work_root))
        checks.append(check("concept review builds", concept.get("kind") == "tyf-concept-review", f"issues={len(concept.get('issues', []))}"))
    except Exception as exc:  # noqa: BLE001
        checks.append(check("concept review builds", False, str(exc)))
    try:
        continuity = continuity_review.build_review(work_root)
        checks.append(check("continuity review builds", continuity.get("kind") == "tyf-continuity-review", f"issues={len(continuity.get('issues', []))}"))
    except Exception as exc:  # noqa: BLE001
        checks.append(check("continuity review builds", False, str(exc)))
    try:
        polish = polish_review.build_review(work_root)
        checks.append(check("polish review builds", polish.get("kind") == "tyf-polish-review", f"issues={len(polish.get('issues', []))}"))
    except Exception as exc:  # noqa: BLE001
        checks.append(check("polish review builds", False, str(exc)))
    try:
        html = live_workbench.enhanced_html(wb.collect_data(work_id, work_root, root, token="doctor"))
        required = ["Assistant status", "Save safety", "Review dashboard", "Changed outside this window", "Prepare conflict packet"]
        missing = [item for item in required if item not in html]
        checks.append(check("live Workbench HTML builds with RC markers", not missing, ", ".join(missing) if missing else "ok"))
    except Exception as exc:  # noqa: BLE001
        checks.append(check("live Workbench HTML builds with RC markers", False, str(exc)))
    return checks


def doctor(work_arg: Optional[str] = None) -> Dict[str, Any]:
    work_id, work_root, root = wb.resolve_work(work_arg)
    wb.ensure_workbench_shape(work_root, root)
    checks: List[Dict[str, Any]] = []
    for rel in REQUIRED_FILES:
        checks.append(check("required file: " + rel, (work_root / rel).is_file(), rel))
    for rel in REQUIRED_DIRS:
        checks.append(check("required dir: " + rel, (work_root / rel).is_dir(), rel))
    audit = graph_projection.audit_jsonl_ledgers(work_root)
    invalid_lines = audit.get("totals", {}).get("invalid_lines", 0)
    checks.append(check("JSONL audit has no invalid lines", invalid_lines == 0, f"invalid_lines={invalid_lines}"))
    event_files = [item for item in audit.get("files", []) if item.get("path") == ".tyf/events.jsonl"]
    if event_files:
        chain = event_files[0].get("chain", {})
        checks.append(check("event ledger hash-chain verifies", bool(chain.get("valid")), json.dumps(chain.get("breaks", []))))
    else:
        checks.append(check("event ledger hash-chain verifies", False, ".tyf/events.jsonl missing"))
    checks.extend(registry_checks(work_root))
    checks.extend(build_checks(work_id, work_root, root))
    failures = [c for c in checks if not c["ok"] and c.get("severity") == "error"]
    report = {
        "kind": "tyf-rc-doctor",
        "work": work_id,
        "generated_at": wb.now(),
        "status": "pass" if not failures else "fail",
        "failures": len(failures),
        "checks": checks,
    }
    out_dir = work_root / ".review" / "surface"
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "rc-doctor.json"
    md_path = out_dir / "rc-doctor.md"
    wb.write_json(json_path, report)
    lines = ["# TYF RC doctor", "", f"Status: {report['status']}", "", f"Generated: {report['generated_at']}", "", f"Failures: {report['failures']}", ""]
    for item in checks:
        mark = "OK" if item["ok"] else "FAIL"
        lines.append(f"- {mark}: {item['name']} — {item.get('detail', '')}")
    wb.atomic_write(md_path, "\n".join(lines) + "\n")
    return {**report, "report_json": json_path.relative_to(work_root).as_posix(), "report_markdown": md_path.relative_to(work_root).as_posix()}


def run(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Run TYF private-RC workspace doctor")
    parser.add_argument("work", nargs="?", default=None)
    args = parser.parse_args(argv)
    result = doctor(args.work)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["status"] == "pass" else 1


def main() -> None:
    raise SystemExit(run())


if __name__ == "__main__":
    main()
