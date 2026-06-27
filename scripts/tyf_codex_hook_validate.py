#!/usr/bin/env python3
"""Validate the TYF Codex hook sample against the local Codex install.

This helper performs local checks only. It verifies that a Codex command can be
invoked, that the hook recorder exists, that the sample hook config is present,
and writes an inspectable report under `.review/surface/`.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Dict, List, Optional

SCRIPT_DIR = Path(__file__).resolve().parent
PACK_ROOT = SCRIPT_DIR.parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import tyf_workbench_v06 as wb  # noqa: E402


def resolve(workspace: Optional[str]) -> tuple[str, Path, Path]:
    if workspace:
        os.chdir(str(Path(workspace).expanduser().resolve()))
    work_id, work_root, root = wb.resolve_work(None)
    wb.ensure_workbench_shape(work_root, root)
    return work_id, work_root, root


def run_cmd(command: List[str], cwd: Path) -> Dict[str, object]:
    try:
        completed = subprocess.run(command, cwd=str(cwd), capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
        return {"ok": completed.returncode == 0, "returncode": completed.returncode, "stdout": completed.stdout.strip(), "stderr": completed.stderr.strip(), "command": command}
    except OSError as exc:
        return {"ok": False, "returncode": None, "stdout": "", "stderr": str(exc), "command": command}


def validate(work_id: str, work_root: Path, root: Path, codex_command: List[str]) -> Dict[str, object]:
    sample = PACK_ROOT / "docs" / "CODEX_HOOKS.sample.toml"
    recorder = SCRIPT_DIR / "tyf_codex_hook.py"
    version = run_cmd(codex_command + ["--version"], root)
    help_result = run_cmd(codex_command + ["--help"], root)
    sample_text = wb.read_text(sample)
    checks = {
        "codex_version_ok": bool(version.get("ok")),
        "codex_help_ok": bool(help_result.get("ok")),
        "sample_exists": sample.is_file(),
        "recorder_exists": recorder.is_file(),
        "sample_mentions_recorder": "tyf_codex_hook.py" in sample_text,
        "sample_mentions_stop_hook": "Stop" in sample_text,
        "sample_mentions_post_tool_use_hook": "PostToolUse" in sample_text,
    }
    overall = "ok" if all(checks.values()) else "needs-local-attention"
    report = {
        "kind": "codex-hook-config-validation",
        "work": work_id,
        "created_at": wb.now(),
        "status": overall,
        "checks": checks,
        "codex_version": version,
        "codex_help": help_result,
        "sample_path": str(sample),
        "recorder_path": str(recorder),
        "local_only": True,
    }
    out = work_root / ".review" / "surface" / "codex-hook-config-validation.json"
    md = work_root / ".review" / "surface" / "codex-hook-config-validation.md"
    wb.write_json(out, report)
    md_text = "# Codex hook config validation\n\n"
    md_text += f"Status: {overall}\n\n"
    md_text += "## Checks\n\n" + "\n".join(f"- {k}: {v}" for k, v in checks.items()) + "\n\n"
    md_text += "## Codex version stdout\n\n```text\n" + str(version.get("stdout") or "") + "\n```\n\n"
    md_text += "## Codex version stderr\n\n```text\n" + str(version.get("stderr") or "") + "\n```\n"
    wb.atomic_write(md, md_text)
    wb.log_event(root, "codex-hook-validation", work_id, overall)
    return {"status": overall, "report": out.relative_to(work_root).as_posix(), "markdown": md.relative_to(work_root).as_posix(), "checks": checks}


def run(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Validate TYF Codex hook sample against the local Codex command")
    parser.add_argument("--workspace", default=None)
    parser.add_argument("--codex-command", default="codex")
    args = parser.parse_args(argv)
    work_id, work_root, root = resolve(args.workspace)
    print(json.dumps(validate(work_id, work_root, root, args.codex_command.split()), ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def main() -> None:
    raise SystemExit(run())


if __name__ == "__main__":
    main()
