#!/usr/bin/env python3
"""Record Codex hook events into TYF Workbench status files.

The script is deliberately tolerant of host JSON shapes. It reads a hook payload
from stdin, extracts a small visible status, writes it to .review/surface/, and
never mutates draft or manuscript prose.
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


def load_payload() -> Dict[str, Any]:
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return {"raw": raw, "parse_error": True}
    return data if isinstance(data, dict) else {"payload": data}


def ensure_workspace(workspace: Optional[str]) -> tuple[str, Path, Path]:
    if workspace:
        os.chdir(str(Path(workspace).expanduser().resolve()))
    work_id, work_root, root = wb.resolve_work(None)
    wb.ensure_workbench_shape(work_root, root)
    return work_id, work_root, root


def find_changed_paths(payload: Dict[str, Any]) -> List[str]:
    candidates: List[str] = []
    for key in ("changed_paths", "changedFiles", "files", "paths"):
        value = payload.get(key)
        if isinstance(value, list):
            candidates.extend(str(item) for item in value)
    tool = payload.get("tool") if isinstance(payload.get("tool"), dict) else {}
    for key in ("changed_paths", "changedFiles", "files", "paths"):
        value = tool.get(key)
        if isinstance(value, list):
            candidates.extend(str(item) for item in value)
    return sorted(dict.fromkeys(p for p in candidates if p))


def summarize_payload(payload: Dict[str, Any]) -> str:
    for key in ("summary", "message", "prompt", "user_prompt", "text"):
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()[:500]
    return ""


def record_hook(work_id: str, work_root: Path, root: Path, hook_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    record = {
        "kind": "codex-hook-status",
        "hook": hook_name,
        "work": work_id,
        "created_at": wb.now(),
        "status": payload.get("status") or hook_name,
        "thread_id": payload.get("thread_id") or payload.get("threadId") or "",
        "turn_id": payload.get("turn_id") or payload.get("turnId") or "",
        "summary": summarize_payload(payload),
        "changed_paths": find_changed_paths(payload),
        "manuscript_written_by_hook": False,
    }
    status_path = work_root / ".review" / "surface" / "codex-turn-status.json"
    history_path = work_root / ".review" / "surface" / "codex-turn-status.jsonl"
    hook_path = work_root / ".review" / "surface" / "codex-hooks.jsonl"
    wb.write_json(status_path, record)
    line = json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n"
    wb.append_text(history_path, line)
    wb.append_text(hook_path, line)
    wb.log_event(root, "codex-hook", work_id, hook_name)
    return record


def run(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Record a Codex hook event for the TYF Workbench")
    parser.add_argument("hook", choices=["SessionStart", "UserPromptSubmit", "PostToolUse", "Stop", "Other"])
    parser.add_argument("--workspace", default=None)
    parser.add_argument("--print", action="store_true", help="print the recorded JSON status")
    args = parser.parse_args(argv)
    work_id, work_root, root = ensure_workspace(args.workspace)
    record = record_hook(work_id, work_root, root, args.hook, load_payload())
    if args.print:
        print(json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def main() -> None:
    raise SystemExit(run())


if __name__ == "__main__":
    main()
