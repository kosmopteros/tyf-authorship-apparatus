#!/usr/bin/env python3
"""Plain-file approval state for the local TYF Codex bridge.

Browser-native Codex chat needs a visible approval model before it can be
considered complete. This module records request-like notifications and author
responses under `.review/surface/`. It never edits draft or manuscript prose.
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

CURRENT_FILE = "codex-approval-current.json"
EVENTS_FILE = "codex-approval-events.jsonl"


def resolve(workspace: Optional[str]) -> tuple[str, Path, Path]:
    if workspace:
        os.chdir(str(Path(workspace).expanduser().resolve()))
    work_id, work_root, root = wb.resolve_work(None)
    wb.ensure_workbench_shape(work_root, root)
    return work_id, work_root, root


def surface_dir(work_root: Path) -> Path:
    out = work_root / ".review" / "surface"
    out.mkdir(parents=True, exist_ok=True)
    return out


def current_path(work_root: Path) -> Path:
    return surface_dir(work_root) / CURRENT_FILE


def events_path(work_root: Path) -> Path:
    return surface_dir(work_root) / EVENTS_FILE


def read_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(wb.read_text(path, ""))
    except json.JSONDecodeError:
        return default


def looks_like_request(method: str, params: Dict[str, Any]) -> bool:
    low = method.lower()
    if "approval" in low or "permission" in low or "review" in low:
        return True
    request_keys = {"approval_id", "approvalId", "request_id", "requestId", "tool", "action"}
    return any(key in params for key in request_keys) and "request" in low


def request_id_for(method: str, params: Dict[str, Any]) -> str:
    explicit = params.get("approval_id") or params.get("approvalId") or params.get("request_id") or params.get("requestId")
    if explicit:
        return wb.one_line(explicit)
    basis = json.dumps({"method": method, "params": params}, ensure_ascii=False, sort_keys=True)
    return "approval-" + wb.now_id() + "-" + wb.short_hash(basis)


def request_from_notification(method: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if not isinstance(params, dict):
        params = {}
    if not looks_like_request(method, params):
        return None
    return {
        "id": request_id_for(method, params),
        "kind": "codex-approval-request",
        "status": "pending",
        "method": wb.one_line(method, "notification"),
        "title": wb.one_line(params.get("title") or params.get("label") or params.get("tool") or params.get("action"), "Codex approval requested"),
        "body": str(params.get("body") or params.get("message") or params.get("description") or ""),
        "thread_id": wb.one_line(params.get("thread_id") or params.get("threadId")),
        "turn_id": wb.one_line(params.get("turn_id") or params.get("turnId")),
        "tool_name": wb.one_line(params.get("tool") or params.get("tool_name") or params.get("toolName")),
        "params": params,
        "created_at": wb.now(),
        "manuscript_written_by_approval_model": False,
    }


def append_event(work_id: str, work_root: Path, root: Path, record: Dict[str, Any]) -> Dict[str, Any]:
    event = {"work": work_id, "updated_at": wb.now(), **record}
    wb.append_text(events_path(work_root), json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")
    wb.write_json(current_path(work_root), event)
    wb.log_event(root, "codex-approval-event", work_id, wb.one_line(event.get("status"), "pending"))
    return event


def record_notification(work_id: str, work_root: Path, root: Path, method: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    record = request_from_notification(method, params)
    if not record:
        return None
    return append_event(work_id, work_root, root, record)


def decide(work_id: str, work_root: Path, root: Path, approval_id: str, decision: str, note: str = "") -> Dict[str, Any]:
    decision = wb.one_line(decision).lower()
    if decision not in ("approved", "rejected", "cancelled"):
        raise ValueError("decision must be approved, rejected, or cancelled")
    current = read_json(current_path(work_root), {})
    record = {
        "id": approval_id or current.get("id") or "unknown-approval",
        "kind": "codex-approval-decision",
        "status": decision,
        "decision_note": note,
        "decided_at": wb.now(),
        "previous": current,
        "manuscript_written_by_approval_model": False,
    }
    return append_event(work_id, work_root, root, record)


def list_events(work_root: Path, limit: int = 50) -> List[Dict[str, Any]]:
    events: List[Dict[str, Any]] = []
    for line in wb.read_text(events_path(work_root)).splitlines():
        if not line.strip():
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(item, dict):
            events.append(item)
    return events[-limit:]


def run(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Record or decide local TYF Codex approval events")
    sub = parser.add_subparsers(dest="cmd", required=True)
    rec = sub.add_parser("record")
    rec.add_argument("--workspace", default=None)
    rec.add_argument("--method", required=True)
    rec.add_argument("--params-json", default="{}")
    dec = sub.add_parser("decide")
    dec.add_argument("--workspace", default=None)
    dec.add_argument("--id", default="")
    dec.add_argument("--decision", required=True, choices=["approved", "rejected", "cancelled"])
    dec.add_argument("--note", default="")
    lst = sub.add_parser("list")
    lst.add_argument("--workspace", default=None)
    lst.add_argument("--limit", type=int, default=50)
    args = parser.parse_args(argv)
    work_id, work_root, root = resolve(args.workspace)
    if args.cmd == "record":
        try:
            params = json.loads(args.params_json)
        except json.JSONDecodeError as exc:
            raise SystemExit(f"invalid --params-json: {exc}")
        result = record_notification(work_id, work_root, root, args.method, params if isinstance(params, dict) else {})
        print(json.dumps(result or {"status": "ignored"}, ensure_ascii=False, indent=2, sort_keys=True))
    elif args.cmd == "decide":
        print(json.dumps(decide(work_id, work_root, root, args.id, args.decision, args.note), ensure_ascii=False, indent=2, sort_keys=True))
    elif args.cmd == "list":
        print(json.dumps({"events": list_events(work_root, args.limit)}, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def main() -> None:
    raise SystemExit(run())


if __name__ == "__main__":
    main()
