#!/usr/bin/env python3
"""Validate TYF's Codex plugin package without private host tooling."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


REQUIRED_INTERFACE_FIELDS = (
    "displayName",
    "shortDescription",
    "longDescription",
    "developerName",
    "category",
    "capabilities",
    "websiteURL",
    "defaultPrompt",
)


def _load_json(path: Path, errors: list[str]) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"missing file: {path}")
        # degradation: ok: validation continues to collect all package errors.
        return {}
    except json.JSONDecodeError as exc:
        errors.append(f"{path}: invalid JSON: {exc}")
        # degradation: ok: validation continues to collect all package errors.
        return {}
    if not isinstance(data, dict):
        errors.append(f"{path}: top-level JSON value must be an object")
        # degradation: ok: validation continues to collect all package errors.
        return {}
    return data


def _require_text(data: dict, key: str, where: str, errors: list[str]) -> None:
    if not isinstance(data.get(key), str) or not data.get(key, "").strip():
        errors.append(f"{where}: missing non-empty {key}")


def _frontmatter(path: Path, errors: list[str]) -> dict[str, str]:
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        errors.append(f"missing skill file: {path}")
        # degradation: ok: validation continues to collect all package errors.
        return {}
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        errors.append(f"{path}: missing YAML frontmatter")
        # degradation: ok: validation continues to collect all package errors.
        return {}
    try:
        end = next(i for i, line in enumerate(lines[1:], start=1) if line.strip() == "---")
    except StopIteration:
        errors.append(f"{path}: unterminated YAML frontmatter")
        # degradation: ok: validation continues to collect all package errors.
        return {}
    values: dict[str, str] = {}
    for line in lines[1:end]:
        if ":" not in line or line.lstrip() != line:
            continue
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def validate_plugin(root: Path) -> list[str]:
    errors: list[str] = []
    manifest_path = root / ".codex-plugin" / "plugin.json"
    manifest = _load_json(manifest_path, errors)
    if not manifest:
        return errors

    _require_text(manifest, "name", "plugin.json", errors)
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,63}", str(manifest.get("name", ""))):
        errors.append("plugin.json: name must be kebab-case and at most 64 characters")
    _require_text(manifest, "version", "plugin.json", errors)
    if not re.fullmatch(r"\d+\.\d+\.\d+", str(manifest.get("version", ""))):
        errors.append("plugin.json: version must use x.y.z")
    _require_text(manifest, "description", "plugin.json", errors)
    author = manifest.get("author")
    if not isinstance(author, dict) or not str(author.get("name", "")).strip():
        errors.append("plugin.json: author.name is required")
    interface = manifest.get("interface")
    if not isinstance(interface, dict):
        errors.append("plugin.json: interface object is required")
    else:
        for key in REQUIRED_INTERFACE_FIELDS:
            value = interface.get(key)
            if isinstance(value, str):
                if not value.strip():
                    errors.append(f"plugin.json: interface.{key} must not be empty")
            elif key in {"capabilities", "defaultPrompt"}:
                if not isinstance(value, list) or not value:
                    errors.append(f"plugin.json: interface.{key} must be a non-empty list")
            else:
                errors.append(f"plugin.json: interface.{key} is required")

    skills_ref = manifest.get("skills")
    if skills_ref != "./skills/":
        errors.append('plugin.json: skills must be "./skills/"')
    skills_dir = root / "skills"
    if not skills_dir.is_dir():
        errors.append("missing skills directory")
    else:
        skill_dirs = sorted(path for path in skills_dir.iterdir() if path.is_dir())
        if not skill_dirs:
            errors.append("skills directory contains no skills")
        for skill_dir in skill_dirs:
            metadata = _frontmatter(skill_dir / "SKILL.md", errors)
            if metadata:
                if not metadata.get("name"):
                    errors.append(f"{skill_dir / 'SKILL.md'}: frontmatter name is required")
                if not metadata.get("description"):
                    errors.append(f"{skill_dir / 'SKILL.md'}: frontmatter description is required")

    hooks_path = root / ".codex-plugin" / "hooks" / "hooks.json"
    hooks = _load_json(hooks_path, errors)
    hook_root = hooks.get("hooks") if hooks else None
    if not isinstance(hook_root, dict):
        errors.append("hooks.json: hooks object is required")
    else:
        hook_blob = json.dumps(hooks, sort_keys=True)
        for event in ("SessionStart", "UserPromptSubmit"):
            if event not in hook_root:
                errors.append(f"hooks.json: missing {event}")
        for command in ("tyf hook session-start", "tyf hook message-sent"):
            if command not in hook_blob:
                errors.append(f"hooks.json: missing command {command}")
        if "TYF:" not in hook_blob:
            errors.append("hooks.json: status messages must identify TYF")

    return errors


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    root = Path(args[0] if args else ".").resolve()
    errors = validate_plugin(root)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"Codex plugin validation passed: {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
