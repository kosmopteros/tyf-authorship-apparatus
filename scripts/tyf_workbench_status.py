#!/usr/bin/env python3
"""Plain-file live status helpers for the TYF Workbench.

The browser can poll this state to show Codex turn status, bridge status,
approval state, and stale draft hashes. This module performs read-only
inspection and never writes draft or manuscript prose.
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


def read_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(wb.read_text(path, ""))
    except json.JSONDecodeError:
        return default


def resolve(workspace: Optional[str], work: Optional[str]) -> tuple[str, Path, Path]:
    if workspace:
        os.chdir(str(Path(workspace).expanduser().resolve()))
    work_id, work_root, root = wb.resolve_work(work)
    wb.ensure_workbench_shape(work_root, root)
    return work_id, work_root, root


def surface(work_root: Path, name: str) -> Path:
    return work_root / ".review" / "surface" / name


def draft_rows(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for unit in data.get("units") or []:
        draft = unit.get("draft") if isinstance(unit, dict) else None
        if isinstance(draft, dict) and draft.get("path"):
            rows.append({
                "unit_id": unit.get("id"),
                "title": unit.get("title"),
                "path": draft.get("path"),
                "sha256": draft.get("sha256"),
                "exists": draft.get("exists"),
            })
    return rows


def live_status(work_id: str, work_root: Path, root: Path) -> Dict[str, Any]:
    data = wb.collect_data(work_id, work_root, root)
    return {
        "generated_at": wb.now(),
        "work": data.get("work"),
        "drafts": draft_rows(data),
        "codex": read_json(surface(work_root, "codex-turn-status.json"), {}),
        "bridge": read_json(surface(work_root, "codex-bridge-status.json"), {}),
        "approval": read_json(surface(work_root, "codex-approval-current.json"), {}),
    }


def stale_drafts_from_loaded(work_id: str, work_root: Path, root: Path, loaded: Dict[str, str]) -> List[Dict[str, Any]]:
    status = live_status(work_id, work_root, root)
    stale: List[Dict[str, Any]] = []
    for row in status.get("drafts", []):
        path = row.get("path") or ""
        loaded_hash = loaded.get(path) or ""
        disk_hash = row.get("sha256") or ""
        if loaded_hash and disk_hash and loaded_hash != disk_hash:
            stale.append({"path": path, "loaded_sha256": loaded_hash, "current_sha256": disk_hash, "status": "stale"})
    return stale


def run(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Print TYF Workbench live status")
    parser.add_argument("work", nargs="?", default=None)
    parser.add_argument("--workspace", default=None)
    args = parser.parse_args(argv)
    work_id, work_root, root = resolve(args.workspace, args.work)
    print(json.dumps(live_status(work_id, work_root, root), ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def main(argv: Optional[List[str]] = None) -> None:
    raise SystemExit(run(argv))


if __name__ == "__main__":
    main()
