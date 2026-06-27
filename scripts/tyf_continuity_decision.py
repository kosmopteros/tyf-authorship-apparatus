#!/usr/bin/env python3
"""Record author decisions on continuity review findings.

Continuity findings are review prompts, not verdicts. This command lets the
author mark a finding as intentional, fixed, ignored, accepted, needs-rewrite,
or belongs-elsewhere so the apparatus stops nagging without erasing history.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
from typing import Any, Dict, List, Optional

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import tyf_workbench_v06 as wb  # noqa: E402

DECISIONS = ".review/surface/continuity-decisions.jsonl"
VALID_STATUSES = {"accepted", "intentional", "ignored", "fixed", "needs-rewrite", "belongs-elsewhere"}


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


def record_decision(work_id: str, work_root: Path, root: Path, issue_key: str, status: str, note: str = "", source: str = "author") -> Dict[str, Any]:
    status = wb.one_line(status).lower()
    issue_key = wb.one_line(issue_key)
    if not issue_key:
        raise ValueError("issue_key is required")
    if status not in VALID_STATUSES:
        raise ValueError("status must be one of: " + ", ".join(sorted(VALID_STATUSES)))
    record = {
        "id": "continuity-decision-" + wb.now_id() + "-" + wb.short_hash(issue_key, status, note),
        "kind": "continuity-decision",
        "work": work_id,
        "issue_key": issue_key,
        "status": status,
        "note": note,
        "source": source,
        "created_at": wb.now(),
    }
    path = work_root / DECISIONS
    wb.append_text(path, json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
    wb.log_event(root, "continuity-decision", work_id, issue_key + " " + status)
    return record


def latest_decisions(work_root: Path) -> Dict[str, Dict[str, Any]]:
    latest: Dict[str, Dict[str, Any]] = {}
    for item in read_jsonl(work_root / DECISIONS):
        key = str(item.get("issue_key") or "")
        if key:
            latest[key] = item
    return latest


def run(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Record an author decision on a continuity review finding")
    parser.add_argument("issue_key")
    parser.add_argument("--status", required=True, choices=sorted(VALID_STATUSES))
    parser.add_argument("--note", default="")
    parser.add_argument("--work", default=None)
    args = parser.parse_args(argv)
    work_id, work_root, root = resolve(args.work)
    record = record_decision(work_id, work_root, root, args.issue_key, args.status, args.note)
    print(json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def main() -> None:
    raise SystemExit(run())


if __name__ == "__main__":
    main()
