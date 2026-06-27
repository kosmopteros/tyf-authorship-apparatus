#!/usr/bin/env python3
"""Generate and record Codex app-server schema compatibility artifacts.

This helper is local-only. It shells out to the installed Codex binary, stores the
version-specific schema files under `.tyf/codex-app-server-schema/`, and writes a
small review packet so the Workbench bridge does not pretend the app-server API
is timeless.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import List, Optional

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import tyf_workbench_v06 as wb  # noqa: E402


def resolve(workspace: Optional[str]) -> tuple[str, Path, Path]:
    if workspace:
        os.chdir(str(Path(workspace).expanduser().resolve()))
    work_id, work_root, root = wb.resolve_work(None)
    wb.ensure_workbench_shape(work_root, root)
    return work_id, work_root, root


def run_cmd(command: List[str], cwd: Path) -> dict:
    try:
        completed = subprocess.run(command, cwd=str(cwd), text=True, encoding="utf-8", errors="replace", capture_output=True, check=False)
        return {
            "ok": completed.returncode == 0,
            "returncode": completed.returncode,
            "stdout": completed.stdout.strip(),
            "stderr": completed.stderr.strip(),
            "command": command,
        }
    except OSError as exc:
        return {"ok": False, "returncode": None, "stdout": "", "stderr": str(exc), "command": command}


def generate_schema(work_id: str, work_root: Path, root: Path, codex_command: List[str]) -> dict:
    out_dir = work_root / ".tyf" / "codex-app-server-schema"
    out_dir.mkdir(parents=True, exist_ok=True)
    version = run_cmd(codex_command + ["--version"], root)
    schema = run_cmd(codex_command + ["app-server", "generate-json-schema", "--out", str(out_dir)], root)
    files = sorted(p.relative_to(work_root).as_posix() for p in out_dir.rglob("*") if p.is_file())
    record = {
        "kind": "codex-app-server-schema-compatibility",
        "work": work_id,
        "created_at": wb.now(),
        "codex_command": codex_command,
        "version": version,
        "schema_generation": schema,
        "schema_files": files,
        "local_only": True,
    }
    record_path = work_root / ".review" / "surface" / "codex-app-server-compat.json"
    md_path = work_root / ".review" / "surface" / "codex-app-server-compat.md"
    wb.write_json(record_path, record)
    status = "ok" if schema.get("ok") else "needs local Codex check"
    md = f"""# Codex app-server compatibility

Status: {status}

Generated: {record['created_at']}

This packet records the installed Codex app-server schema for the local TYF Workbench bridge. The schema is version-specific and should be regenerated after Codex upgrades.

## Command

```text
{' '.join(codex_command)} app-server generate-json-schema --out {out_dir.relative_to(work_root).as_posix()}
```

## Version stdout

```text
{version.get('stdout') or '(none)'}
```

## Version stderr

```text
{version.get('stderr') or '(none)'}
```

## Schema generation stdout

```text
{schema.get('stdout') or '(none)'}
```

## Schema generation stderr

```text
{schema.get('stderr') or '(none)'}
```

## Files

""" + "\n".join(f"- `{path}`" for path in files) + "\n"
    wb.atomic_write(md_path, md)
    wb.log_event(root, "codex-app-server-schema", work_id, status)
    return {"status": status, "record": record_path.relative_to(work_root).as_posix(), "markdown": md_path.relative_to(work_root).as_posix(), "files": files}


def run(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Generate Codex app-server schema compatibility files for TYF")
    parser.add_argument("--workspace", default=None)
    parser.add_argument("--codex-command", default="codex")
    args = parser.parse_args(argv)
    work_id, work_root, root = resolve(args.workspace)
    result = generate_schema(work_id, work_root, root, args.codex_command.split())
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def main() -> None:
    raise SystemExit(run())


if __name__ == "__main__":
    main()
