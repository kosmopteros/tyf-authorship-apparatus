#!/usr/bin/env python3
"""Single-author local recovery helpers for TYF.

TYF does not need multiplayer editing. It needs calm recovery when the browser
and a local amanuensis process touch the same draft file. This module never
writes manuscript text and never auto-merges.
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

CONFLICTS_DIR = ".review/conflicts"
DRAFT_COPY_DIR = "drafts/.recovery-copies"


def resolve(work_arg: Optional[str]) -> tuple[str, Path, Path]:
    work_id, work_root, root = wb.resolve_work(work_arg)
    wb.ensure_workbench_shape(work_root, root)
    return work_id, work_root, root


def draft_path(work_root: Path, path: str) -> tuple[str, Path]:
    return wb.safe_rel_path(work_root, wb.one_line(path), ("drafts/",))


def current_draft(work_root: Path, path: str) -> Dict[str, Any]:
    norm, file_path = draft_path(work_root, path)
    text = wb.read_text(file_path)
    return {"path": norm, "text": text, "sha256": wb.sha256_text(text), "exists": file_path.is_file()}


def safe_copy_name(source_path: str, suffix: str) -> str:
    stem = Path(source_path).stem or "draft"
    return wb.safe_slug(stem, "draft") + "-" + suffix + ".md"


def save_browser_copy(work_id: str, work_root: Path, root: Path, source_path: str, browser_text: str, note: str = "") -> Dict[str, Any]:
    norm, _file_path = draft_path(work_root, source_path)
    out_dir = work_root / DRAFT_COPY_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    copy_rel = DRAFT_COPY_DIR + "/" + safe_copy_name(norm, "browser-" + wb.now_id())
    copy_path = work_root / copy_rel
    header = f"<!-- TYF recovery copy from {norm}; created {wb.now()}; work {work_id}. -->\n"
    if note:
        header += f"<!-- note: {note.replace('--', '—')} -->\n"
    wb.atomic_write(copy_path, header + browser_text)
    wb.log_event(root, "recovery-browser-copy", work_id, copy_rel)
    return {"status": "browser-copy-written", "source_path": norm, "copy_path": copy_rel, "sha256": wb.sha256_text(header + browser_text)}


def write_conflict_packet(work_id: str, work_root: Path, root: Path, source_path: str, loaded_sha256: str, browser_text: str, note: str = "") -> Dict[str, Any]:
    current = current_draft(work_root, source_path)
    conflict_id = "conflict-" + wb.now_id() + "-" + wb.short_hash(work_id, current["path"], loaded_sha256, current["sha256"], browser_text[:200])
    out_dir = work_root / CONFLICTS_DIR / conflict_id
    out_dir.mkdir(parents=True, exist_ok=True)
    disk_path = out_dir / "disk.md"
    browser_path = out_dir / "browser.md"
    meta_path = out_dir / "conflict.json"
    report_path = out_dir / "conflict.md"
    wb.atomic_write(disk_path, current["text"])
    wb.atomic_write(browser_path, browser_text)
    meta = {
        "id": conflict_id,
        "kind": "tyf-draft-recovery-conflict",
        "work": work_id,
        "source_path": current["path"],
        "loaded_sha256": loaded_sha256,
        "disk_sha256": current["sha256"],
        "browser_sha256": wb.sha256_text(browser_text),
        "created_at": wb.now(),
        "note": note,
        "manuscript_written": False,
    }
    wb.write_json(meta_path, meta)
    md = f"""# TYF draft recovery packet: {conflict_id}

The draft changed outside the browser window. TYF did not merge or overwrite anything.

- work: {work_id}
- source: `{current['path']}`
- loaded sha256: `{loaded_sha256}`
- disk sha256: `{current['sha256']}`
- browser sha256: `{meta['browser_sha256']}`
- created: {meta['created_at']}

## Safe choices

- Reload disk version in the Workbench.
- Save browser version as a recovery copy.
- Compare `disk.md` and `browser.md` manually.
- Ask the amanuensis for a review, but do not auto-merge.

## Disk version

See `disk.md`.

## Browser version

See `browser.md`.
"""
    wb.atomic_write(report_path, md)
    wb.log_event(root, "recovery-conflict-packet", work_id, f"{conflict_id} {current['path']}")
    return {
        "status": "conflict-packet-written",
        "id": conflict_id,
        "source_path": current["path"],
        "packet_dir": (Path(CONFLICTS_DIR) / conflict_id).as_posix(),
        "report": (Path(CONFLICTS_DIR) / conflict_id / "conflict.md").as_posix(),
        "disk": (Path(CONFLICTS_DIR) / conflict_id / "disk.md").as_posix(),
        "browser": (Path(CONFLICTS_DIR) / conflict_id / "browser.md").as_posix(),
    }


def reload_disk_version(work_root: Path, source_path: str) -> Dict[str, Any]:
    current = current_draft(work_root, source_path)
    return {"status": "disk-version", **current}


def run(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="TYF single-author draft recovery helpers")
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("reload")
    p.add_argument("path")
    p.add_argument("--work", default=None)
    p = sub.add_parser("copy")
    p.add_argument("path")
    p.add_argument("--browser-file", required=True)
    p.add_argument("--note", default="")
    p.add_argument("--work", default=None)
    p = sub.add_parser("packet")
    p.add_argument("path")
    p.add_argument("--loaded-sha256", required=True)
    p.add_argument("--browser-file", required=True)
    p.add_argument("--note", default="")
    p.add_argument("--work", default=None)
    args = parser.parse_args(argv)
    work_id, work_root, root = resolve(getattr(args, "work", None))
    if args.cmd == "reload":
        result = reload_disk_version(work_root, args.path)
    elif args.cmd == "copy":
        result = save_browser_copy(work_id, work_root, root, args.path, wb.read_text(Path(args.browser_file)), args.note)
    else:
        result = write_conflict_packet(work_id, work_root, root, args.path, args.loaded_sha256, wb.read_text(Path(args.browser_file)), args.note)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def main() -> None:
    raise SystemExit(run())


if __name__ == "__main__":
    main()
