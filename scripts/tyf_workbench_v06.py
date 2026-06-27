#!/usr/bin/env python3
"""TYF v0.6 local double-surface writing workbench.

This module is intentionally stdlib-only and local-first. It gives the author a
real browser desk for multi-unit draft work while preserving TYF's core rule:
`manuscript/` is read-only here and still moves only through the Gate.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import http.server
import json
import os
from pathlib import Path
import re
import secrets
import socketserver
import sys
import urllib.parse
import webbrowser

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except AttributeError:
    pass

ROOT_WORK_ID = "work"
DEFAULT_PORT = 8766
MAX_POST_BYTES = 4 * 1024 * 1024
TEXT_EXTENSIONS = {".md", ".markdown", ".txt"}
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".tif", ".tiff", ".heic"}


# ---------------------------------------------------------------------------
# Small file and path helpers


def now() -> str:
    return _dt.datetime.now().strftime("%Y-%m-%d %H:%M")


def now_id() -> str:
    return _dt.datetime.now().strftime("%Y%m%d-%H%M%S")


def read_text(path: Path, default: str = "") -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return default


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    try:
        with tmp.open("w", encoding="utf-8") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(str(tmp), str(path))
    finally:
        try:
            if tmp.exists():
                tmp.unlink()
        except OSError:
            pass


def append_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(text)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def short_hash(*parts: str) -> str:
    joined = "\n".join(str(p) for p in parts if p is not None)
    return sha256_text(joined)[:12]


def one_line(value: object, fallback: str = "") -> str:
    text = str(value or fallback or "").replace("\r", " ").replace("\n", " ").strip()
    return text or fallback


def safe_slug(value: str, fallback: str = "unit") -> str:
    slug = re.sub(r"[^A-Za-z0-9._/-]+", "-", value.strip().replace("\\", "/"))
    slug = re.sub(r"-+", "-", slug).strip("-./")
    return slug or fallback


def safe_work_id(work_id: str) -> str:
    if (
        not work_id
        or work_id in (".", "..")
        or os.path.isabs(work_id)
        or work_id.startswith("~")
        or not re.fullmatch(r"[A-Za-z0-9._-]+", work_id)
    ):
        raise ValueError(
            f"unsafe work id {work_id!r}; use letters, digits, '.', '-' or '_' only"
        )
    return work_id


def load_flat_yaml(path: Path) -> dict:
    data = {}
    if not path.is_file():
        return data
    for raw in read_text(path).splitlines():
        if not raw.strip() or raw.lstrip().startswith("#") or ":" not in raw:
            continue
        if raw.startswith(" ") or raw.startswith("-"):
            continue
        key, _, value = raw.partition(":")
        value = value.strip()
        if len(value) >= 2 and value[0] == '"' and value[-1] == '"':
            try:
                value = json.loads(value)
            except json.JSONDecodeError:
                value = value[1:-1]
        data[key.strip()] = value
    return data


def reject_symlink_components(path: Path, label: str = "path") -> None:
    absolute = path.absolute()
    parts = absolute.parts
    if not parts:
        return
    current = Path(parts[0])
    for part in parts[1:]:
        current = current / part
        if current.is_symlink():
            raise ValueError(f"refused: {label} crosses a symlink: {current}")


def is_within(base: Path, target: Path) -> bool:
    base_resolved = base.resolve()
    target_resolved = target.resolve()
    return target_resolved == base_resolved or str(target_resolved).startswith(str(base_resolved) + os.sep)


def safe_rel_path(work_root: Path, rel: str, allowed_prefixes: tuple[str, ...]) -> tuple[str, Path]:
    norm = one_line(rel).replace("\\", "/")
    if os.path.isabs(norm) or norm in ("", ".", "..") or norm.startswith("../") or "/../" in norm:
        raise ValueError(f"unsafe workspace path: {rel!r}")
    if not any(norm == p.rstrip("/") or norm.startswith(p) for p in allowed_prefixes):
        raise ValueError(f"path must live under {', '.join(allowed_prefixes)}")
    path = work_root.joinpath(*norm.split("/"))
    reject_symlink_components(path, norm)
    if not is_within(work_root, path):
        raise ValueError(f"path resolves outside the work: {norm}")
    return norm, path


def workspace_root() -> Path:
    root = Path.cwd().resolve()
    if not (root / "WORKSPACE_STATE.yaml").is_file():
        raise SystemExit("Not in a TYF workspace: WORKSPACE_STATE.yaml is missing. Run `tyf init` first.")
    return root


def active_work_id(root: Path) -> str:
    state = load_flat_yaml(root / "WORKSPACE_STATE.yaml")
    active = one_line(state.get("active_work"))
    if active:
        return active
    if (root / "work.yaml").is_file():
        return ROOT_WORK_ID
    return ROOT_WORK_ID


def resolve_work(work_arg: str | None) -> tuple[str, Path, Path]:
    root = workspace_root()
    work_id = safe_work_id(work_arg or active_work_id(root) or ROOT_WORK_ID)
    if work_id == ROOT_WORK_ID and (root / "work.yaml").is_file():
        work_root = root
    else:
        work_root = root / "works" / work_id
    reject_symlink_components(work_root, "work root")
    if not (work_root / "work.yaml").is_file():
        raise SystemExit(f"Refused: no work {work_id!r}; missing {work_root / 'work.yaml'}")
    if not is_within(root, work_root):
        raise SystemExit("Refused: work root resolves outside the workspace.")
    return work_id, work_root, root


# ---------------------------------------------------------------------------
# Event journal and workbench shape


def event_record_hash(record: dict) -> str:
    payload = {k: record[k] for k in sorted(record) if k != "hash"}
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return sha256_text(raw)


def read_events(root: Path) -> list[dict]:
    path = root / ".tyf" / "events.jsonl"
    records = []
    for line in read_text(path).splitlines():
        if not line.strip():
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return records


def log_event(root: Path, kind: str, ref: str = "", detail: str = "") -> None:
    if not (root / "WORKSPACE_STATE.yaml").is_file():
        return
    path = root / ".tyf" / "events.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    records = read_events(root)
    previous = records[-1].get("hash", "") if records else ""
    seq = int(records[-1].get("seq", 0)) + 1 if records else 1
    record = {
        "seq": seq,
        "ts": now(),
        "kind": one_line(kind),
        "ref": one_line(ref),
        "detail": one_line(detail),
        "previous_hash": previous,
    }
    record["hash"] = event_record_hash(record)
    append_text(path, json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def ensure_workbench_shape(work_root: Path, workspace: Path) -> None:
    for rel in (
        "outline",
        "drafts",
        "manuscript",
        "knowledge-base",
        "assets/images",
        "design",
        ".review/surface",
        ".review/gate-packets",
        ".review/footnote-candidates",
        ".tyf",
    ):
        target = work_root / rel
        reject_symlink_components(target, rel)
        target.mkdir(parents=True, exist_ok=True)
    if not (work_root / "knowledge-base" / "author-notes.jsonl").exists():
        atomic_write(work_root / "knowledge-base" / "author-notes.jsonl", "")
    if not (work_root / ".tyf" / "workbench-state.json").exists():
        atomic_write(
            work_root / ".tyf" / "workbench-state.json",
            json.dumps({"active_unit": "", "selection": {}, "updated_at": now()}, indent=2) + "\n",
        )
    if not (workspace / ".tyf" / "events.jsonl").exists():
        (workspace / ".tyf").mkdir(parents=True, exist_ok=True)
        atomic_write(workspace / ".tyf" / "events.jsonl", "")
    if not (work_root / "outline" / "book-map.yaml").exists():
        write_book_map(work_root)


# ---------------------------------------------------------------------------
# Book map and unit discovery


def markdown_files(base: Path) -> list[Path]:
    if not base.is_dir():
        return []
    found = []
    for path in sorted(base.rglob("*")):
        if path.name.startswith(".") or not path.is_file():
            continue
        if path.suffix.lower() in TEXT_EXTENSIONS:
            found.append(path)
    return found


def rel_to_work(work_root: Path, path: Path) -> str:
    return path.relative_to(work_root).as_posix()


def unit_key_from_rel(rel: str) -> str:
    clean = rel.replace("\\", "/")
    for prefix in ("drafts/", "manuscript/"):
        if clean.startswith(prefix):
            clean = clean[len(prefix):]
    return os.path.splitext(clean)[0]


def unit_id_from_key(key: str) -> str:
    return safe_slug(key.replace("/", "-"), "unit")


def title_from_key(key: str) -> str:
    label = os.path.basename(key).replace("_", " ").replace("-", " ").strip()
    return label.title() if label else "Untitled Unit"


def discovered_units(work_root: Path) -> dict[str, dict]:
    units: dict[str, dict] = {}
    for path in markdown_files(work_root / "drafts"):
        rel = rel_to_work(work_root, path)
        key = unit_key_from_rel(rel)
        units.setdefault(key, {"key": key, "title": title_from_key(key), "kind": "chapter"})["draft"] = rel
    for path in markdown_files(work_root / "manuscript"):
        rel = rel_to_work(work_root, path)
        key = unit_key_from_rel(rel)
        units.setdefault(key, {"key": key, "title": title_from_key(key), "kind": "chapter"})["manuscript"] = rel
    if not units:
        rel = "drafts/candidate-draft.md"
        draft = work_root / rel
        if not draft.exists():
            atomic_write(draft, "# Candidate draft\n\n")
        units["candidate-draft"] = {
            "key": "candidate-draft",
            "title": "Candidate Draft",
            "kind": "draft",
            "draft": rel,
        }
    return units


def quote_yaml(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def write_book_map(work_root: Path) -> Path:
    units = discovered_units(work_root)
    lines = [
        "# TYF book map",
        "# Ordered multi-unit body for the local writing workbench.",
        "# This file is plain YAML-shaped text and may be edited by the author.",
        "units:",
    ]
    for key in sorted(units):
        item = units[key]
        lines.append(f"  - id: {quote_yaml(unit_id_from_key(key))}")
        lines.append(f"    title: {quote_yaml(item.get('title') or title_from_key(key))}")
        lines.append(f"    kind: {quote_yaml(item.get('kind') or 'chapter')}")
        lines.append(f"    draft: {quote_yaml(item.get('draft') or '')}")
        lines.append(f"    manuscript: {quote_yaml(item.get('manuscript') or '')}")
    path = work_root / "outline" / "book-map.yaml"
    atomic_write(path, "\n".join(lines) + "\n")
    return path


def scalar(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == '"' and value[-1] == '"':
        try:
            return str(json.loads(value))
        except json.JSONDecodeError:
            return value[1:-1]
    return value


def parse_book_map(path: Path) -> list[dict]:
    units: list[dict] = []
    current: dict | None = None
    for raw in read_text(path).splitlines():
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("- id:"):
            if current:
                units.append(current)
            current = {"id": scalar(stripped.partition(":")[2])}
        elif current and ":" in stripped:
            key, _, value = stripped.partition(":")
            current[key.strip()] = scalar(value)
    if current:
        units.append(current)
    return units


def text_unit(work_root: Path, rel: str, allowed: tuple[str, ...], fallback: str = "") -> dict:
    norm, path = safe_rel_path(work_root, rel, allowed)
    exists = path.is_file()
    text = read_text(path, fallback if not exists else "")
    return {"path": norm, "exists": exists, "text": text, "sha256": sha256_text(text)}


def collect_units(work_root: Path) -> list[dict]:
    discovered = discovered_units(work_root)
    by_key = {k: dict(v) for k, v in discovered.items()}
    order: list[str] = []
    for item in parse_book_map(work_root / "outline" / "book-map.yaml"):
        key = item.get("key") or unit_key_from_rel(item.get("draft") or item.get("manuscript") or item.get("id") or "")
        if not key:
            key = item.get("id") or "unit"
        existing = by_key.setdefault(key, {"key": key})
        existing.update({k: v for k, v in item.items() if v})
        if key not in order:
            order.append(key)
    for key in sorted(by_key):
        if key not in order:
            order.append(key)
    units = []
    for key in order:
        item = by_key[key]
        draft_rel = item.get("draft") or ""
        manuscript_rel = item.get("manuscript") or ""
        draft = text_unit(work_root, draft_rel, ("drafts/",), "") if draft_rel else None
        manuscript = text_unit(work_root, manuscript_rel, ("manuscript/",), "") if manuscript_rel else None
        units.append(
            {
                "id": item.get("id") or unit_id_from_key(key),
                "key": key,
                "title": item.get("title") or title_from_key(key),
                "kind": item.get("kind") or "chapter",
                "draft": draft,
                "manuscript": manuscript,
            }
        )
    return units


# ---------------------------------------------------------------------------
# Notes, footnotes, packets and context


def notes_path(work_root: Path) -> Path:
    return work_root / "knowledge-base" / "author-notes.jsonl"


def read_jsonl(path: Path) -> list[dict]:
    records = []
    for line in read_text(path).splitlines():
        if not line.strip():
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(item, dict):
            records.append(item)
    return records


def write_json(path: Path, data: dict) -> None:
    atomic_write(path, json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def append_jsonl(path: Path, record: dict) -> None:
    append_text(path, json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def load_notes(work_root: Path) -> list[dict]:
    return read_jsonl(notes_path(work_root))


def update_note(work_root: Path, note_id: str, **updates: object) -> dict | None:
    path = notes_path(work_root)
    notes = load_notes(work_root)
    changed = None
    for note in notes:
        if note.get("id") == note_id:
            note.update(updates)
            note["updated_at"] = now()
            changed = note
            break
    if changed is None:
        return None
    atomic_write(path, "".join(json.dumps(n, ensure_ascii=False, sort_keys=True) + "\n" for n in notes))
    return changed


def create_author_note(work_id: str, work_root: Path, workspace: Path, payload: dict) -> dict:
    target_path = one_line(payload.get("target_path") or payload.get("path"), "drafts/candidate-draft.md")
    target_kind = one_line(payload.get("target_kind"), "selection")
    if target_kind == "book":
        norm = "book"
    else:
        norm, _path = safe_rel_path(work_root, target_path, ("drafts/", "manuscript/", "assets/images/"))
    quote = str(payload.get("quote") or "")
    before = str(payload.get("before") or "")
    after = str(payload.get("after") or "")
    body = str(payload.get("body") or "").strip()
    if not body:
        raise ValueError("author note body is empty")
    note_id = "note-" + now_id() + "-" + short_hash(work_id, norm, quote, body)
    record = {
        "id": note_id,
        "target_path": norm,
        "target_kind": target_kind,
        "quote": quote,
        "quote_hash": short_hash(quote) if quote else "",
        "start_offset": payload.get("start_offset"),
        "end_offset": payload.get("end_offset"),
        "surrounding_context_hash": short_hash(before, quote, after) if (before or after or quote) else "",
        "body": body,
        "status": "open",
        "provenance": one_line(payload.get("provenance"), "author"),
        "source_refs": payload.get("source_refs") or [],
        "graph_refs": payload.get("graph_refs") or [],
        "created_at": now(),
        "updated_at": now(),
    }
    append_jsonl(notes_path(work_root), record)
    log_event(workspace, "workbench-author-note", work_id, f"{note_id} {norm}")
    return {"status": "note", "note": record, "message": "Author note saved."}


def footnote_candidate(work_id: str, work_root: Path, workspace: Path, note_id: str) -> dict:
    note = next((n for n in load_notes(work_root) if n.get("id") == note_id), None)
    if not note:
        raise ValueError(f"no author note with id {note_id}")
    candidate_id = "fn-" + now_id() + "-" + short_hash(work_id, note_id, note.get("body", ""))
    candidate = {
        "id": candidate_id,
        "kind": "footnote-candidate",
        "work": work_id,
        "source_note_id": note_id,
        "target_path": note.get("target_path"),
        "target_kind": note.get("target_kind"),
        "quote": note.get("quote", ""),
        "candidate_text": note.get("body", ""),
        "status": "candidate",
        "created_at": now(),
        "manuscript_written": False,
    }
    out_dir = work_root / ".review" / "footnote-candidates"
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / f"{candidate_id}.json"
    md_path = out_dir / f"{candidate_id}.md"
    write_json(json_path, candidate)
    md = f"""# TYF footnote candidate: {candidate_id}

This is a draftable footnote candidate made from an author note. It is not a manuscript insertion and it is not author acceptance into `manuscript/`.

- work: {work_id}
- source note: {note_id}
- target: {note.get('target_path', '')}
- target kind: {note.get('target_kind', '')}

## Anchored quote

{note.get('quote') or '(no selected quote recorded)'}

## Candidate footnote text

{candidate['candidate_text']}

## Next

Refine this in draft/review space if needed. Any insertion into `manuscript/` still goes through proposal, audit, author review, author decision, and `tyf write --decision`.
"""
    atomic_write(md_path, md)
    update_note(work_root, note_id, status="converted-to-footnote", footnote_candidate_id=candidate_id)
    log_event(workspace, "workbench-footnote-candidate", work_id, candidate_id)
    return {
        "status": "footnote-candidate",
        "candidate": candidate,
        "json": json_path.relative_to(work_root).as_posix(),
        "markdown": md_path.relative_to(work_root).as_posix(),
        "message": "Footnote candidate written. manuscript/ was not touched.",
    }


def save_draft(work_id: str, work_root: Path, workspace: Path, payload: dict) -> dict:
    norm, path = safe_rel_path(work_root, one_line(payload.get("path")), ("drafts/",))
    current = read_text(path) if path.is_file() else ""
    current_hash = sha256_text(current)
    base_hash = one_line(payload.get("base_hash"))
    proposed = str(payload.get("text") or "")
    if base_hash != current_hash:
        return {
            "status": "conflict",
            "path": norm,
            "current_sha256": current_hash,
            "loaded_sha256": base_hash,
            "current_text": current,
            "browser_text": proposed,
            "message": "Draft changed on disk after the workbench loaded it; reload or merge deliberately before saving.",
        }
    atomic_write(path, proposed)
    new_hash = sha256_text(proposed)
    log_event(workspace, "workbench-save-draft", work_id, norm)
    return {"status": "saved", "path": norm, "sha256": new_hash, "message": "Draft saved. manuscript/ was not touched."}


def create_draft_unit(work_id: str, work_root: Path, workspace: Path, payload: dict) -> dict:
    rel = one_line(payload.get("path"))
    if not rel:
        title_for_path = one_line(payload.get("title"), "new-unit")
        rel = "drafts/" + safe_slug(title_for_path, "new-unit") + ".md"
    if not rel.startswith("drafts/"):
        rel = "drafts/" + rel
    if not rel.lower().endswith(".md"):
        rel += ".md"
    norm, path = safe_rel_path(work_root, rel, ("drafts/",))
    if path.exists():
        raise ValueError(f"draft unit already exists: {norm}")
    title = one_line(payload.get("title"), title_from_key(unit_key_from_rel(norm)))
    atomic_write(path, f"# {title}\n\n")
    write_book_map(work_root)
    log_event(workspace, "workbench-create-draft-unit", work_id, norm)
    return {"status": "created", "path": norm, "message": f"Draft unit created: {norm}"}


def gate_packet(work_id: str, work_root: Path, workspace: Path, payload: dict) -> dict:
    norm, path = safe_rel_path(work_root, one_line(payload.get("path")), ("drafts/",))
    current = read_text(path) if path.is_file() else ""
    current_hash = sha256_text(current)
    base_hash = one_line(payload.get("base_hash"))
    if base_hash != current_hash:
        return {
            "status": "conflict",
            "path": norm,
            "current_sha256": current_hash,
            "loaded_sha256": base_hash,
            "message": "Draft changed on disk after the workbench loaded it; reload before preparing a Gate packet.",
        }
    selection = str(payload.get("selection") or "")
    selected = selection if selection.strip() else current
    packet_id = "gate-" + now_id() + "-" + short_hash(work_id, norm, current_hash, selected)
    out_dir = work_root / ".review" / "gate-packets"
    out_dir.mkdir(parents=True, exist_ok=True)
    record = {
        "id": packet_id,
        "kind": "workbench-gate-packet",
        "work": work_id,
        "source_path": norm,
        "source_sha256": current_hash,
        "selection": selected,
        "note": str(payload.get("note") or "").strip(),
        "created_at": now(),
        "manuscript_written": False,
    }
    json_path = out_dir / f"{packet_id}.json"
    md_path = out_dir / f"{packet_id}.md"
    write_json(json_path, record)
    md = f"""# TYF Workbench Gate packet: {packet_id}

This review packet was prepared from the local writing workbench. It is not manuscript text and it is not author acceptance.

- work: {work_id}
- source: {norm}
- source sha256: `{current_hash}`
- note: {record['note'] or '(none)'}

## Selected candidate text

{selected}

## Next

If the author accepts this material for the manuscript, create a normal TYF proposal from the draft and continue through audit, author review, author decision, and `tyf write --decision`.
"""
    atomic_write(md_path, md)
    log_event(workspace, "workbench-gate-packet", work_id, packet_id)
    return {
        "status": "packet",
        "id": packet_id,
        "json": json_path.relative_to(work_root).as_posix(),
        "markdown": md_path.relative_to(work_root).as_posix(),
        "message": "Gate packet written. manuscript/ was not touched.",
    }


def selected_terms(text: str) -> list[str]:
    words = re.findall(r"[\w][\w'-]{3,}", text.lower(), flags=re.UNICODE)
    stop = {"that", "this", "with", "from", "have", "will", "would", "there", "their", "about", "which", "when", "then"}
    out = []
    for w in words:
        if w not in stop and w not in out:
            out.append(w)
    return out[:8]


def related_passages(work_root: Path, active_path: str, selection_text: str) -> list[dict]:
    terms = selected_terms(selection_text)
    if not terms:
        return []
    found = []
    for base in (work_root / "drafts", work_root / "manuscript"):
        for path in markdown_files(base):
            rel = rel_to_work(work_root, path)
            if rel == active_path:
                continue
            text = read_text(path)
            low = text.lower()
            score = sum(low.count(t) for t in terms)
            if score <= 0:
                continue
            idxs = [low.find(t) for t in terms if low.find(t) >= 0]
            start = max(min(idxs) - 160, 0) if idxs else 0
            snippet = text[start:start + 420].strip()
            found.append({"path": rel, "score": score, "snippet": snippet})
    return sorted(found, key=lambda x: (-int(x["score"]), x["path"]))[:8]


def save_state(work_root: Path, payload: dict) -> dict:
    state = {
        "active_unit": one_line(payload.get("active_unit")),
        "active_path": one_line(payload.get("active_path")),
        "selection": payload.get("selection") if isinstance(payload.get("selection"), dict) else {},
        "scroll": payload.get("scroll") if isinstance(payload.get("scroll"), dict) else {},
        "visible_panels": payload.get("visible_panels") if isinstance(payload.get("visible_panels"), dict) else {},
        "updated_at": now(),
    }
    write_json(work_root / ".tyf" / "workbench-state.json", state)
    return {"status": "saved", "state": state}


def create_context_packet(work_id: str, work_root: Path, workspace: Path, payload: dict) -> dict:
    state = save_state(work_root, payload)["state"]
    selection = state.get("selection") if isinstance(state.get("selection"), dict) else {}
    active_path = one_line(selection.get("path") or state.get("active_path"), "drafts/candidate-draft.md")
    norm, path = safe_rel_path(work_root, active_path, ("drafts/", "manuscript/"))
    text = read_text(path)
    quote = str(selection.get("text") or "")
    notes = [n for n in load_notes(work_root) if n.get("target_path") in (norm, "book") and n.get("status") != "dismissed"]
    packet_id = "ctx-" + now_id() + "-" + short_hash(work_id, norm, quote, text[:1000])
    context = {
        "id": packet_id,
        "kind": "workbench-active-context",
        "work": work_id,
        "active_path": norm,
        "active_sha256": sha256_text(text),
        "selection": selection,
        "style_sheet": read_text(work_root / "style-sheet.md"),
        "book_style": read_text(work_root / "design" / "book-style.yaml"),
        "author_notes": notes,
        "related_passages": related_passages(work_root, norm, quote),
        "created_at": now(),
        "manuscript_written": False,
    }
    out_dir = work_root / ".review" / "surface"
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "active-context.json"
    md_path = out_dir / "active-context.md"
    write_json(json_path, context)
    note_lines = "\n".join(f"- {n.get('id')}: {n.get('body')}" for n in notes) or "- no open notes on this target"
    related_lines = "\n".join(f"- {r['path']} (score {r['score']}): {r['snippet'][:160]}" for r in context["related_passages"]) or "- no related passages found by local term scan"
    selected_block = quote or "(no active selected text)"
    md = f"""# TYF active Workbench context: {packet_id}

This is a context packet for the amanuensis. It captures what the author is touching in the local Workbench. It is not a command to write manuscript text.

- work: {work_id}
- active path: {norm}
- active sha256: `{context['active_sha256']}`
- created: {context['created_at']}

## Active selection

{selected_block}

## Open author notes on this target

{note_lines}

## Related passages by local scan

{related_lines}

## How to use this packet

When Codex or another amanuensis turn needs context, read this packet, the active unit, the style sheet, and the relevant notes. Propose only in draft/review space. Do not write `manuscript/` from this packet.
"""
    atomic_write(md_path, md)
    log_event(workspace, "workbench-active-context", work_id, packet_id)
    return {
        "status": "context",
        "id": packet_id,
        "json": json_path.relative_to(work_root).as_posix(),
        "markdown": md_path.relative_to(work_root).as_posix(),
        "message": "Amanuensis context packet written. Open .review/surface/active-context.md from Codex.",
    }


# ---------------------------------------------------------------------------
# Workbench data and HTML


def image_inventory(work_root: Path) -> dict:
    image_dir = work_root / "assets" / "images"
    records = read_jsonl(image_dir / "index.jsonl")
    files = []
    if image_dir.is_dir():
        for path in sorted(image_dir.iterdir()):
            if path.name.startswith(".") or not path.is_file():
                continue
            if path.suffix.lower() in IMAGE_EXTENSIONS:
                files.append({"file": rel_to_work(work_root, path), "bytes": path.stat().st_size})
    return {"records": records, "files": files, "index_path": "assets/images/index.jsonl"}


def collect_data(work_id: str, work_root: Path, workspace: Path, token: str = "") -> dict:
    ensure_workbench_shape(work_root, workspace)
    work = load_flat_yaml(work_root / "work.yaml")
    state = {}
    try:
        state = json.loads(read_text(work_root / ".tyf" / "workbench-state.json", "{}"))
    except json.JSONDecodeError:
        state = {}
    return {
        "generated_at": now(),
        "token": token,
        "work": {
            "id": work_id,
            "title": work.get("title") or "Untitled work",
            "title_status": work.get("title_status") or "unknown",
            "language": work.get("language") or "undetermined",
            "status": work.get("status") or "unknown",
        },
        "paths": {
            "book_map": "outline/book-map.yaml",
            "author_notes": "knowledge-base/author-notes.jsonl",
            "workbench_state": ".tyf/workbench-state.json",
            "surface_dir": ".review/surface/",
            "gate_packet_dir": ".review/gate-packets/",
            "footnote_candidate_dir": ".review/footnote-candidates/",
        },
        "units": collect_units(work_root),
        "notes": load_notes(work_root),
        "state": state,
        "style": {
            "style_sheet": read_text(work_root / "style-sheet.md"),
            "book_style": read_text(work_root / "design" / "book-style.yaml"),
        },
        "assets": image_inventory(work_root),
        "gate": {
            "manuscript_read_only": True,
            "rule": "Workbench writes drafts and packets only. manuscript/ remains Gate-only.",
        },
    }


HTML_TEMPLATE = r"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>TYF Workbench v0.6</title>
  <style>
    :root { color-scheme: light; --paper:#fbfaf7; --card:#fffdf9; --ink:#24211d; --muted:#6f665b; --line:#d8d1c6; --soft:#efe8dd; --accent:#315d75; --ok:#2f6b43; --warn:#8a4d13; --bad:#8b2f2f; font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
    * { box-sizing: border-box; }
    body { margin: 0; background: var(--paper); color: var(--ink); }
    header { display:flex; justify-content:space-between; gap:16px; padding:16px 20px 12px; border-bottom:1px solid var(--line); background:var(--card); }
    h1 { margin:0 0 4px; font-size:22px; }
    .sub { color:var(--muted); font-size:13px; }
    .grid { display:grid; grid-template-columns:260px minmax(340px,1.2fr) minmax(300px,1fr) 330px; min-height:calc(100vh - 70px); }
    nav, main, aside, .manuscript { min-width:0; border-right:1px solid var(--line); }
    nav, aside { background:#f4eee5; overflow:auto; }
    .pane-title { margin:0; padding:12px 14px; border-bottom:1px solid var(--line); color:var(--muted); font-size:12px; text-transform:uppercase; letter-spacing:.08em; }
    .unit { display:block; width:100%; text-align:left; border:0; border-bottom:1px solid var(--line); background:transparent; padding:10px 12px; cursor:pointer; color:var(--ink); }
    .unit.active { background:var(--card); border-left:4px solid var(--accent); padding-left:8px; }
    .unit small { display:block; color:var(--muted); margin-top:2px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
    .editor-wrap, .reader-wrap { display:flex; flex-direction:column; height:100%; min-height:calc(100vh - 70px); }
    .toolbar { display:flex; gap:8px; flex-wrap:wrap; align-items:center; padding:10px; border-bottom:1px solid var(--line); background:var(--soft); }
    button { border:1px solid var(--line); border-radius:7px; padding:8px 10px; background:var(--card); color:var(--ink); cursor:pointer; font:inherit; }
    button.primary { background:var(--accent); border-color:var(--accent); color:white; }
    button:disabled { opacity:.55; cursor:not-allowed; }
    textarea.editor { flex:1; width:100%; min-height:60vh; border:0; resize:none; padding:24px; outline:none; background:var(--card); color:var(--ink); font:18px/1.62 Georgia, "Times New Roman", serif; }
    .reader { flex:1; overflow:auto; padding:24px; background:var(--card); font:18px/1.62 Georgia, "Times New Roman", serif; white-space:pre-wrap; }
    .reader .empty { color:var(--muted); font-family:Inter, sans-serif; }
    .meta { color:var(--muted); font-size:12px; }
    section { padding:12px 14px; border-bottom:1px solid var(--line); }
    label { display:block; margin:0 0 5px; color:var(--muted); font-size:12px; }
    input, textarea.note { width:100%; border:1px solid var(--line); border-radius:7px; background:var(--card); color:var(--ink); padding:8px; font:inherit; }
    textarea.note { min-height:72px; resize:vertical; }
    pre { white-space:pre-wrap; max-height:190px; overflow:auto; background:var(--card); border:1px solid var(--line); border-radius:7px; padding:9px; font-size:12px; }
    .status { color:var(--muted); font-size:13px; }
    .ok { color:var(--ok); } .warn { color:var(--warn); } .bad { color:var(--bad); }
    .note-card { background:var(--card); border:1px solid var(--line); border-radius:8px; padding:8px; margin:8px 0; font-size:13px; }
    .note-card .body { white-space:pre-wrap; margin:4px 0 8px; }
    @media (max-width:1180px) { .grid { grid-template-columns:1fr; } nav, main, aside, .manuscript { border-right:0; border-bottom:1px solid var(--line); } .editor-wrap,.reader-wrap { min-height:50vh; } }
  </style>
</head>
<body>
  <header>
    <div><h1>TYF Workbench v0.6</h1><div class="sub" id="workMeta"></div></div>
    <div class="sub">Local writing desk. Drafts are editable. manuscript/ is read-only.</div>
  </header>
  <div class="grid">
    <nav aria-label="Book map">
      <h2 class="pane-title">Book map</h2>
      <div id="unitList"></div>
      <section>
        <label for="newUnitTitle">New draft unit</label>
        <input id="newUnitTitle" placeholder="Chapter or interlude title">
        <label for="newUnitPath" style="margin-top:8px">Path</label>
        <input id="newUnitPath" placeholder="drafts/chapter-title.md">
        <div style="margin-top:8px"><button id="createUnit">Create unit</button></div>
      </section>
      <section><button id="refreshData">Refresh from disk</button></section>
    </nav>
    <main class="editor-wrap" aria-label="Draft editor">
      <h2 class="pane-title">Draft surface</h2>
      <div class="toolbar">
        <button class="primary" id="saveDraft">Save draft</button>
        <button id="gatePacket">Gate packet from selection</button>
        <button id="contextPacket">Amanuensis context</button>
        <span class="status" id="draftStatus"></span>
      </div>
      <textarea class="editor" id="draftText" spellcheck="true"></textarea>
    </main>
    <div class="manuscript reader-wrap" aria-label="Read-only manuscript">
      <h2 class="pane-title">Approved manuscript preview</h2>
      <div class="reader" id="manuscriptText"></div>
      <div class="toolbar"><span class="warn">Read-only here. Use the Gate for manuscript writes.</span></div>
    </div>
    <aside aria-label="Apparatus">
      <h2 class="pane-title">Apparatus</h2>
      <section>
        <div class="meta">Active selection</div>
        <pre id="selectionBox">No selection yet.</pre>
      </section>
      <section>
        <label for="noteBody">Author note on selection or active unit</label>
        <textarea class="note" id="noteBody" placeholder="What should the amanuensis remember here?"></textarea>
        <div style="margin-top:8px"><button id="addNote">Save note</button></div>
      </section>
      <section>
        <label for="packetNote">Gate packet note</label>
        <input id="packetNote" placeholder="why this selection is ready or what to review">
      </section>
      <section>
        <strong>Notes</strong>
        <div id="notesList"></div>
      </section>
      <section>
        <strong>Style sheet</strong>
        <pre id="styleSheet"></pre>
      </section>
      <section>
        <strong>Images</strong>
        <div id="assets"></div>
      </section>
    </aside>
  </div>
  <script>
    let data = __PAYLOAD__;
    let activeUnitId = (data.state && data.state.active_unit) || (data.units[0] && data.units[0].id) || '';
    let lastSelection = (data.state && data.state.selection) || {};
    const draft = document.getElementById('draftText');
    const status = document.getElementById('draftStatus');
    function esc(s) { return String(s || '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])); }
    function activeUnit() { return data.units.find(u => u.id === activeUnitId) || data.units[0] || null; }
    function activeDraft() { const u = activeUnit(); return u && u.draft ? u.draft : null; }
    function activeManuscript() { const u = activeUnit(); return u && u.manuscript ? u.manuscript : null; }
    function setStatus(text, cls) { status.textContent = text || ''; status.className = 'status ' + (cls || ''); }
    function render() {
      document.getElementById('workMeta').textContent = `${data.work.title} · ${data.work.language} · ${data.work.status}`;
      const units = data.units || [];
      document.getElementById('unitList').innerHTML = units.map(u => `<button class="unit ${u.id === activeUnitId ? 'active' : ''}" data-unit="${esc(u.id)}"><strong>${esc(u.title)}</strong><small>${esc((u.draft&&u.draft.path)||'no draft')} · ${esc((u.manuscript&&u.manuscript.path)||'no manuscript')}</small></button>`).join('');
      document.querySelectorAll('[data-unit]').forEach(btn => btn.addEventListener('click', () => { activeUnitId = btn.getAttribute('data-unit'); render(); rememberState(); }));
      const d = activeDraft();
      draft.disabled = !d;
      draft.value = d ? (d.text || '') : '';
      draft.dataset.baseHash = d ? d.sha256 : '';
      draft.dataset.path = d ? d.path : '';
      const m = activeManuscript();
      document.getElementById('manuscriptText').innerHTML = m ? esc(m.text || '') : '<span class="empty">No approved manuscript unit mapped for this draft.</span>';
      document.getElementById('styleSheet').textContent = (data.style && data.style.style_sheet) || '';
      const assets = data.assets || {records:[], files:[]};
      const rows = (assets.records||[]).map(r => `<p>${esc(JSON.stringify(r))}</p>`).join('') + (assets.files||[]).map(f => `<p>${esc(f.file)} (${f.bytes} bytes)</p>`).join('');
      document.getElementById('assets').innerHTML = rows || '<p class="meta">No image assets recorded.</p>';
      renderSelection();
      renderNotes();
      setStatus(d ? d.path : 'No draft for this unit', '');
    }
    function renderSelection() {
      const text = lastSelection && lastSelection.text ? lastSelection.text : '';
      document.getElementById('selectionBox').textContent = text || 'No selection yet.';
    }
    function renderNotes() {
      const notes = (data.notes || []).filter(n => n.status !== 'dismissed').slice().reverse();
      document.getElementById('notesList').innerHTML = notes.length ? notes.map(n => `<div class="note-card"><div class="meta">${esc(n.id)} · ${esc(n.target_path)} · ${esc(n.status)}</div><div class="body">${esc(n.body)}</div><button data-footnote="${esc(n.id)}">Footnote candidate</button></div>`).join('') : '<p class="meta">No notes yet.</p>';
      document.querySelectorAll('[data-footnote]').forEach(btn => btn.addEventListener('click', async () => {
        try { const r = await postJson('/api/footnote-candidate', {note_id: btn.getAttribute('data-footnote')}); setStatus(r.message, 'ok'); await reload(); }
        catch (err) { setStatus(err.message || 'Could not create footnote candidate.', 'warn'); }
      }));
    }
    function captureSelection() {
      const d = activeDraft();
      if (!d) return;
      const start = draft.selectionStart || 0;
      const end = draft.selectionEnd || 0;
      const text = draft.value.slice(start, end);
      const before = draft.value.slice(Math.max(0, start - 220), start);
      const after = draft.value.slice(end, end + 220);
      lastSelection = {path: d.path, text, start_offset: start, end_offset: end, before, after};
      renderSelection();
    }
    async function postJson(url, body) {
      const response = await fetch(url, {method:'POST', headers:{'Content-Type':'application/json','X-TYF-Token':data.token || ''}, body:JSON.stringify(body || {})});
      const result = await response.json();
      if (!response.ok) throw result;
      return result;
    }
    async function reload() {
      data = await fetch('/workbench-data.json').then(r => r.json());
      if (!data.units.find(u => u.id === activeUnitId) && data.units[0]) activeUnitId = data.units[0].id;
      render();
    }
    async function rememberState() {
      try { await postJson('/api/save-state', {active_unit: activeUnitId, active_path: (activeDraft()||{}).path || '', selection: lastSelection}); } catch (_) {}
    }
    draft.addEventListener('keyup', captureSelection);
    draft.addEventListener('mouseup', captureSelection);
    document.getElementById('saveDraft').addEventListener('click', async () => {
      const d = activeDraft(); if (!d) return;
      try { const r = await postJson('/api/save-draft', {path:d.path, base_hash:draft.dataset.baseHash, text:draft.value}); setStatus(r.message, 'ok'); await reload(); }
      catch (err) { setStatus(err.message || 'Save failed. In static mode run with --serve.', err.status === 'conflict' ? 'warn' : 'bad'); }
    });
    document.getElementById('createUnit').addEventListener('click', async () => {
      try { const r = await postJson('/api/create-draft-unit', {title:document.getElementById('newUnitTitle').value, path:document.getElementById('newUnitPath').value}); setStatus(r.message, 'ok'); await reload(); }
      catch (err) { setStatus(err.message || 'Could not create unit.', 'warn'); }
    });
    document.getElementById('addNote').addEventListener('click', async () => {
      captureSelection();
      const d = activeDraft(); if (!d) return;
      try { const r = await postJson('/api/author-note', {target_path:d.path, target_kind:lastSelection.text ? 'selection' : 'unit', quote:lastSelection.text || '', start_offset:lastSelection.start_offset, end_offset:lastSelection.end_offset, before:lastSelection.before, after:lastSelection.after, body:document.getElementById('noteBody').value, provenance:'author'}); document.getElementById('noteBody').value=''; setStatus(r.message, 'ok'); await reload(); }
      catch (err) { setStatus(err.message || 'Could not save note.', 'warn'); }
    });
    document.getElementById('gatePacket').addEventListener('click', async () => {
      captureSelection(); const d = activeDraft(); if (!d) return;
      try { const r = await postJson('/api/gate-packet', {path:d.path, base_hash:draft.dataset.baseHash, selection:lastSelection.text || '', note:document.getElementById('packetNote').value}); setStatus(r.message + ' ' + r.markdown, 'ok'); }
      catch (err) { setStatus(err.message || 'Could not write Gate packet.', 'warn'); }
    });
    document.getElementById('contextPacket').addEventListener('click', async () => {
      captureSelection(); const d = activeDraft(); if (!d) return;
      try { const r = await postJson('/api/context-packet', {active_unit:activeUnitId, active_path:d.path, selection:lastSelection}); setStatus(r.message + ' ' + r.markdown, 'ok'); }
      catch (err) { setStatus(err.message || 'Could not write context packet.', 'warn'); }
    });
    document.getElementById('refreshData').addEventListener('click', reload);
    render();
  </script>
</body>
</html>
"""


def surface_html(data: dict) -> str:
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    return HTML_TEMPLATE.replace("__PAYLOAD__", payload)


def write_surface_files(work_id: str, work_root: Path, workspace: Path, token: str = "") -> tuple[Path, Path]:
    data = collect_data(work_id, work_root, workspace, token=token)
    out_dir = work_root / ".review" / "surface"
    out_dir.mkdir(parents=True, exist_ok=True)
    html_path = out_dir / "workbench-v06.html"
    data_path = out_dir / "workbench-v06-data.json"
    atomic_write(html_path, surface_html(data))
    write_json(data_path, data)
    return html_path, data_path


# ---------------------------------------------------------------------------
# Local server


class ReusableThreadingHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True


def is_loopback(host: str) -> bool:
    return host in ("127.0.0.1", "localhost", "::1")


def make_handler(work_id: str, work_root: Path, workspace: Path, token: str):
    class Handler(http.server.BaseHTTPRequestHandler):
        server_version = "TYFWorkbenchV06/0.1"

        def json_response(self, status: int, payload: dict) -> None:
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def html_response(self, text: str) -> None:
            body = text.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def require_token(self) -> bool:
            supplied = self.headers.get("X-TYF-Token", "")
            if not secrets.compare_digest(supplied, token):
                self.json_response(403, {"status": "error", "message": "Missing or invalid local workbench token."})
                return False
            return True

        def do_GET(self):  # noqa: N802
            parsed = urllib.parse.urlparse(self.path)
            if parsed.path in ("/", "/index.html", "/workbench-v06.html"):
                self.html_response(surface_html(collect_data(work_id, work_root, workspace, token=token)))
            elif parsed.path == "/workbench-data.json":
                self.json_response(200, collect_data(work_id, work_root, workspace, token=token))
            else:
                self.send_error(404)

        def do_POST(self):  # noqa: N802
            if not self.require_token():
                return
            try:
                size = int(self.headers.get("Content-Length", "0"))
                raw = self.rfile.read(min(size, MAX_POST_BYTES)).decode("utf-8")
                payload = json.loads(raw or "{}")
                parsed = urllib.parse.urlparse(self.path)
                if parsed.path == "/api/save-draft":
                    result = save_draft(work_id, work_root, workspace, payload)
                    self.json_response(409 if result.get("status") == "conflict" else 200, result)
                elif parsed.path == "/api/create-draft-unit":
                    self.json_response(200, create_draft_unit(work_id, work_root, workspace, payload))
                elif parsed.path == "/api/author-note":
                    self.json_response(200, create_author_note(work_id, work_root, workspace, payload))
                elif parsed.path == "/api/footnote-candidate":
                    self.json_response(200, footnote_candidate(work_id, work_root, workspace, one_line(payload.get("note_id"))))
                elif parsed.path == "/api/gate-packet":
                    result = gate_packet(work_id, work_root, workspace, payload)
                    self.json_response(409 if result.get("status") == "conflict" else 200, result)
                elif parsed.path == "/api/context-packet":
                    self.json_response(200, create_context_packet(work_id, work_root, workspace, payload))
                elif parsed.path == "/api/save-state":
                    self.json_response(200, save_state(work_root, payload))
                else:
                    self.send_error(404)
            except ValueError as e:
                self.json_response(400, {"status": "error", "message": str(e)})
            except Exception as e:  # noqa: BLE001
                self.json_response(500, {"status": "error", "message": str(e)})

        def log_message(self, fmt, *args):  # noqa: A003
            return

    return Handler


# ---------------------------------------------------------------------------
# CLI


def run(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="TYF v0.6 local double-surface writing workbench")
    parser.add_argument("work", nargs="?", default=None, help="optional work id; defaults to active work")
    parser.add_argument("--serve", action="store_true", help="serve the local browser workbench with save/note/packet APIs")
    parser.add_argument("--host", default="127.0.0.1", help="host for --serve; loopback only unless --allow-remote is set")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="port for --serve")
    parser.add_argument("--open", action="store_true", help="open the workbench URL in the default browser")
    parser.add_argument("--allow-remote", action="store_true", help="advanced: allow binding to a non-loopback host")
    parser.add_argument("--refresh-map", action="store_true", help="regenerate outline/book-map.yaml from draft and manuscript files")
    args = parser.parse_args(argv)

    work_id, work_root, workspace = resolve_work(args.work)
    ensure_workbench_shape(work_root, workspace)
    if args.refresh_map:
        write_book_map(work_root)
    token = secrets.token_urlsafe(24) if args.serve else ""
    html_path, data_path = write_surface_files(work_id, work_root, workspace, token=token)
    log_event(workspace, "workbench-v06", work_id, html_path.relative_to(work_root).as_posix())
    print(f"TYF Workbench v0.6: {html_path.relative_to(work_root).as_posix()}")
    print(f"Workbench data: {data_path.relative_to(work_root).as_posix()}")
    print("No manuscript text was written. manuscript/ remains Gate-only.")

    if args.serve:
        if not args.allow_remote and not is_loopback(args.host):
            raise SystemExit("Refused: non-loopback host requires --allow-remote.")
        server = ReusableThreadingHTTPServer((args.host, int(args.port)), make_handler(work_id, work_root, workspace, token))
        url = f"http://{args.host}:{server.server_port}/"
        print(f"Serving local TYF Workbench v0.6 at {url}")
        print("Side-effecting APIs require a local capability token embedded in this browser session.")
        if args.open:
            webbrowser.open(url)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nStopped TYF Workbench v0.6.")
    return 0


def main(argv: list[str] | None = None) -> None:
    raise SystemExit(run(argv))


if __name__ == "__main__":
    main()
