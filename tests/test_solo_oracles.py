#!/usr/bin/env python3
"""Small independent SOLO oracles for TYF's immediate feature claims.

These complement the broad unittest smoke suite and the Codex plugin validator
with direct structural checks, so SOLO can see more than one executable oracle.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys


ROOT = pathlib.Path(__file__).resolve().parents[1]


def check_helper() -> None:
    source = (ROOT / "scripts" / "tyf.py").read_text(encoding="utf-8")
    required = {"start", "begin", "capture", "reflexes", "snapshot", "write", "doctor", "check"}
    missing = sorted(
        command for command in required
        if f'add_parser("{command}"' not in source
    )
    assert not missing, f"missing TYF commands: {missing}"
    for handler in ("cmd_start", "cmd_begin", "cmd_capture", "cmd_reflexes", "cmd_snapshot"):
        assert f"def {handler}(" in source, f"missing {handler}"
        assert f"fn={handler}" in source, f"{handler} is not wired into argparse"


def check_plugin() -> None:
    manifest_path = ROOT / ".codex-plugin" / "plugin.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["name"] == "tyf"
    assert manifest["skills"] == "./skills/"
    assert manifest["author"]["name"]
    interface = manifest["interface"]
    assert interface["displayName"]
    assert "writing" in " ".join(manifest.get("keywords", [])).lower()
    assert (ROOT / "skills").is_dir()


def check_onboarding() -> None:
    start_here = (ROOT / "docs" / "START_HERE.md").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    using = (ROOT / "skills" / "using-tyf" / "SKILL.md").read_text(encoding="utf-8")
    init = (ROOT / "skills" / "initializing-a-workspace" / "SKILL.md").read_text(encoding="utf-8")
    cowork = (ROOT / "cowork" / "SETUP.md").read_text(encoding="utf-8")

    assert "## Paste Into Codex" in start_here
    assert "## Paste Into Claude Cowork" in start_here
    assert 'tyf start "<working title>"' in start_here
    assert "[docs/START_HERE.md]" in readme
    assert "do not hand them a command list" in using.lower()
    assert 'tyf start "Working Title"' in init
    assert "Use TYF to start my new book" in cowork


def check_onboarding_entry() -> None:
    start_here = (ROOT / "docs" / "START_HERE.md").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "Paste Into Codex" in start_here
    assert "Paste Into Claude Cowork" in start_here
    assert "Do not draft manuscript prose yet" in start_here
    assert "start with a paste prompt" in readme
    assert "You should not need to learn the helper commands" in readme


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("oracle", choices=("helper", "plugin", "onboarding", "onboarding-entry"))
    args = parser.parse_args(argv)
    if args.oracle == "helper":
        check_helper()
    elif args.oracle == "plugin":
        check_plugin()
    elif args.oracle == "onboarding":
        check_onboarding()
    else:
        check_onboarding_entry()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
