#!/usr/bin/env python3
"""TYF local double-surface Workbench v0.6.

A zero-dependency, local-first authoring desk:
- multi-unit book map in outline/book-map.yaml;
- editable draft units with compare-and-swap saves;
- read-only manuscript preview;
- author notes in knowledge-base/author-notes.jsonl;
- footnote candidates and Gate packets under .review/gate-packets/;
- active unit and selection in .tyf/workbench-state.json;
- no writes to manuscript/.
"""

import argparse
import datetime
import hashlib
import http.server
import json
import os
import re
import secrets
import socketserver
import sys
import urllib.parse
import webbrowser
from pathlib import Path

ROOT_WORK_ID = "work"
TEXT_EXTS = (".md", ".markdown", ".txt")
BOOK_MAP_PATH = "outline/book-map.yaml"
AUTHOR_NOTES_PATH = "knowledge-base/author-notes.jsonl"
STATE_PATH = ".tyf/workbench-state.json"
SURFACE_DIR = ".review/surface-v06"
GATE_DIR = ".review/gate-packets"

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except AttributeError:
    pass


def now():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M")


def now_iso():
    return datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat()


def _read(path):
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except OSError:
        return ""


def _atomic_write(path, text):
    parent = os.path.dirname(path) or "."
    os.makedirs(parent, exist_ok=True)
    tmp = os.path.join(parent, f".{os.path.basename(path)}.tmp-{os.getpid()}")
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        try:
            if os.path.exists(tmp):
                os.remove(tmp)
        except OSError:
            pass


def _write(path, text):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def _append(path, text):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(text)


def _json_write(path, data):
    _atomic_write(path, json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def _sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _id(prefix, *parts):
    body = "\0".join(str(p) for p in parts)
    return prefix + "-" + hashlib.sha256(body.encode("utf-8")).hexdigest()[:16]


def _one_line(value, fallback=""):
    text = (value or fallback or "").replace("\r", " ").replace("\n", " ").strip()
    return text or fallback


def _strip_quotes(value):
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
        return value[1:-1]
    return value


def read_state(path):
    out = {}
    if not os.path.isfile(path):
        return out
    for raw in _read(path).splitlines():
        if not raw.strip() or raw.startswith(" ") or raw.lstrip().startswith("#") or ":" not in raw:
            continue
        key, value = raw.split(":", 1)
        out[key.strip()] = _strip_quotes(value.strip())
    return out


def require_workspace():
    if not os.path.isfile("WORKSPACE_STATE.yaml"):
        sys.exit("Not in a TYF workspace root (no WORKSPACE_STATE.yaml). Run `tyf init` first.")
    real = os.path.realpath(".")
    if os.path.abspath(".") != real:
        os.chdir(real)


def active_work_id():
    active = read_state("WORKSPACE_STATE.yaml").get("active_work") or ROOT_WORK_ID
    return active if re.fullmatch(r"[A-Za-z0-9._-]+", active or "") else ROOT_WORK_ID


def work_base(work_id):
    return "." if work_id == ROOT_WORK_ID and os.path.isfile("work.yaml") else os.path.join("works", work_id)


def require_work(work_id):
    if not re.fullmatch(r"[A-Za-z0-9._-]+", work_id or ""):
        sys.exit(f"Refused unsafe work id: {work_id!r}")
    if not os.path.isfile(os.path.join(work_base(work_id), "work.yaml")):
        sys.exit(f"Refused: no work {work_id!r}; missing work.yaml.")


def _within(base, target):
    base, target = os.path.realpath(base), os.path.realpath(target)
    return target == base or target.startswith(base + os.sep)


def _reject_symlink_components(path, label="path"):
    parts = Path(os.path.abspath(path)).parts
    if not parts:
        return
    cur = parts[0]
    for part in parts[1:]:
        cur = os.path.join(cur, part)
        if os.path.islink(cur):
            raise ValueError(f"Refused: {label} crosses a symlink: {cur}")


def safe_rel(work_id, rel, allowed_prefixes):
    norm = _one_line(rel).replace("\\", "/")
    if os.path.isabs(norm) or norm in ("", ".", "..") or norm.startswith("../") or "/../" in norm:
        raise ValueError(f"unsafe workspace path: {rel!r}")
    if not any(norm == p[:-1] or norm.startswith(p) for p in allowed_prefixes):
        raise ValueError(f"path must live under {', '.join(allowed_prefixes)}")
    path = os.path.join(work_base(work_id), *norm.split("/"))
    _reject_symlink_components(path, norm)
    if not _within(work_base(work_id), path):
        raise ValueError(f"path resolves outside the work: {norm}")
    return norm, path


def _ensure_scaffold(work_id):
    base = work_base(work_id)
    for rel in ("outline", "drafts", "manuscript", "knowledge-base", ".tyf", SURFACE_DIR, GATE_DIR, "design", "assets/images"):
        path = os.path.join(base, rel)
        _reject_symlink_components(path, rel)
        os.makedirs(path, exist_ok=True)
    if not os.path.isfile(os.path.join(base, AUTHOR_NOTES_PATH)):
        _write(os.path.join(base, AUTHOR_NOTES_PATH), "")
    if not os.path.isfile(os.path.join(base, STATE_PATH)):
        _json_write(os.path.join(base, STATE_PATH), {"schema_version": 1, "updated_at": now_iso(), "active_unit_id": ""})
    if not os.path.isfile(os.path.join(base, BOOK_MAP_PATH)):
        _write(os.path.join(base, BOOK_MAP_PATH), render_default_book_map(work_id))


def _text_files(work_id, root_rel):
    base = os.path.join(work_base(work_id), root_rel)
    found = []
    if not os.path.isdir(base):
        return found
    for cur, dirs, files in os.walk(base):
        dirs[:] = [d for d in sorted(dirs) if not d.startswith(".")]
        for name in sorted(files):
            if name.startswith(".") or os.path.splitext(name)[1].lower() not in TEXT_EXTS:
                continue
            path = os.path.join(cur, name)
            if _within(work_base(work_id), path):
                found.append(os.path.relpath(path, work_base(work_id)).replace(os.sep, "/"))
    return found


def _slug(value):
    value = re.sub(r"\.[a-z0-9]+$", "", value.lower().replace("\\", "/"))
    value = re.sub(r"^(drafts|manuscript)/", "", value)
    value = re.sub(r"[^a-z0-9._/-]+", "-", value).strip("-/._").replace("/", "-")
    return (value or "unit")[:80]


def _title(work_id, rel):
    path = os.path.join(work_base(work_id), *rel.split("/"))
    for line in _read(path).splitlines():
        m = re.match(r"^#\s+(.+)$", line.strip())
        if m:
            return m.group(1).strip()
    return os.path.splitext(os.path.basename(rel))[0].replace("-", " ").replace("_", " ").title()


def _key(rel):
    rel = rel.split("/", 1)[1] if "/" in rel else rel
    return re.sub(r"\.[^.]+$", "", rel)


def _paired_units(work_id):
    by_key = {}
    for rel in _text_files(work_id, "drafts"):
        by_key.setdefault(_key(rel), {})["draft"] = rel
    for rel in _text_files(work_id, "manuscript"):
        by_key.setdefault(_key(rel), {})["manuscript"] = rel
    by_key.setdefault("candidate-draft", {"draft": "drafts/candidate-draft.md"})
    units = []
    for key in sorted(by_key):
        item = by_key[key]
        draft = item.get("draft") or f"drafts/{key}.md"
        manuscript = item.get("manuscript") or f"manuscript/{key}.md"
        units.append({
            "id": _slug(key),
            "title": _title(work_id, item.get("draft") or item.get("manuscript") or draft),
            "role": "draft-manuscript" if item.get("draft") and item.get("manuscript") else ("draft" if item.get("draft") else "manuscript"),
            "draft_path": draft,
            "manuscript_path": manuscript,
        })
    units.sort(key=lambda u: (0 if u["draft_path"] == "drafts/candidate-draft.md" else 1, u["id"]))
    return units


def render_default_book_map(work_id):
    lines = ["# TYF book map", "# Ordered authoring units for the local Workbench.", "units:"]
    for unit in _paired_units(work_id):
        lines += [
            f"  - id: {unit['id']}",
            f"    title: {json.dumps(unit['title'], ensure_ascii=False)}",
            f"    role: {unit['role']}",
            f"    draft: {unit['draft_path']}",
            f"    manuscript: {unit['manuscript_path']}",
        ]
    return "\n".join(lines) + "\n"


def _parse_book_map(text):
    units, current = [], None
    for raw in text.splitlines():
        s = raw.strip()
        if not s or s.startswith("#"):
            continue
        if s.startswith("- "):
            if current:
                units.append(current)
            current = {}
            s = s[2:].strip()
        if current is not None and ":" in s:
            key, value = s.split(":", 1)
            current[key.strip()] = _strip_quotes(value.strip())
    if current:
        units.append(current)
    return units


def _normalize_unit(work_id, raw, order):
    draft = (raw.get("draft") or raw.get("draft_path") or "").replace("\\", "/")
    manuscript = (raw.get("manuscript") or raw.get("manuscript_path") or "").replace("\\", "/")
    if draft:
        safe_rel(work_id, draft, ("drafts/",))
    if manuscript:
        safe_rel(work_id, manuscript, ("manuscript/",))
    if not draft and manuscript:
        draft = f"drafts/{_key(manuscript)}.md"
    if not manuscript and draft:
        manuscript = f"manuscript/{_key(draft)}.md"
    draft = draft or f"drafts/unit-{order + 1}.md"
    manuscript = manuscript or f"manuscript/unit-{order + 1}.md"
    uid = _slug(raw.get("id") or draft or manuscript or f"unit-{order + 1}")
    title = raw.get("title") or (_title(work_id, draft) if os.path.isfile(os.path.join(work_base(work_id), *draft.split("/"))) else uid)
    return {"id": uid, "title": _one_line(title, uid), "role": _one_line(raw.get("role"), "unit"), "draft_path": draft, "manuscript_path": manuscript}


def read_book_map(work_id):
    _ensure_scaffold(work_id)
    parsed = _parse_book_map(_read(os.path.join(work_base(work_id), BOOK_MAP_PATH)))
    units = []
    for i, raw in enumerate(parsed):
        try:
            units.append(_normalize_unit(work_id, raw, i))
        except ValueError:
            continue
    return units or _paired_units(work_id)


def _json_load(path, default):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def _jsonl(path):
    rows = []
    for i, raw in enumerate(_read(path).splitlines(), 1):
        if not raw.strip():
            continue
        try:
            rows.append(json.loads(raw))
        except json.JSONDecodeError:
            rows.append({"kind": "invalid-json", "line": i, "raw": raw})
    return rows


def _text_unit(work_id, rel, readonly=False):
    norm, path = safe_rel(work_id, rel, ("drafts/", "manuscript/"))
    text = _read(path) if os.path.isfile(path) else ""
    return {"path": norm, "text": text, "sha256": _sha(text), "exists": os.path.isfile(path), "read_only": bool(readonly)}


def _assets(work_id):
    base = os.path.join(work_base(work_id), "assets", "images")
    files = []
    if os.path.isdir(base):
        for name in sorted(os.listdir(base)):
            if name.startswith(".") or name in ("README.md", "index.jsonl"):
                continue
            path = os.path.join(base, name)
            if os.path.isfile(path):
                files.append({"file": f"assets/images/{name}", "bytes": os.path.getsize(path)})
    return {"index_path": "assets/images/index.jsonl", "records": _jsonl(os.path.join(base, "index.jsonl")), "files": files}


def workbench_data(work_id):
    require_workspace(); require_work(work_id); _ensure_scaffold(work_id)
    base = work_base(work_id)
    state = _json_load(os.path.join(base, STATE_PATH), {})
    notes = _jsonl(os.path.join(base, AUTHOR_NOTES_PATH))
    units = []
    for unit in read_book_map(work_id):
        draft = _text_unit(work_id, unit["draft_path"])
        manuscript = _text_unit(work_id, unit["manuscript_path"], readonly=True)
        unit_notes = [n for n in notes if n.get("unit_id") == unit["id"] or n.get("target_path") in (draft["path"], manuscript["path"])]
        units.append({**unit, "draft": draft, "manuscript": manuscript, "notes": unit_notes})
    active_id = state.get("active_unit_id") or (units[0]["id"] if units else "")
    if units and not any(u["id"] == active_id for u in units):
        active_id = units[0]["id"]
    wy = read_state(os.path.join(base, "work.yaml"))
    return {
        "schema_version": 1,
        "generated_at": now(),
        "work": {"id": work_id, "title": wy.get("title") or "Untitled work", "title_status": wy.get("title_status") or "unknown", "language": wy.get("language") or "undetermined", "status": wy.get("status") or "unknown"},
        "book_map": {"path": BOOK_MAP_PATH, "units": units},
        "active_unit_id": active_id,
        "current": next((u for u in units if u["id"] == active_id), units[0] if units else None),
        "notes": {"path": AUTHOR_NOTES_PATH, "records": notes},
        "style": {"book_style_path": "design/book-style.yaml", "book_style": _read(os.path.join(base, "design", "book-style.yaml")), "style_sheet_path": "style-sheet.md", "style_sheet": _read(os.path.join(base, "style-sheet.md"))},
        "assets": _assets(work_id),
        "state": state,
        "gate": {"packet_dir": GATE_DIR, "manuscript_write": "read-only here; use the controlled write chain after author review and acceptance"},
    }


def save_workbench_state(work_id, payload):
    data = {"schema_version": 1, "updated_at": now_iso(), "active_unit_id": _one_line(payload.get("active_unit_id")), "active_path": _one_line(payload.get("active_path")), "selection": payload.get("selection") if isinstance(payload.get("selection"), dict) else {}, "scroll": payload.get("scroll") if isinstance(payload.get("scroll"), dict) else {}}
    _json_write(os.path.join(work_base(work_id), STATE_PATH), data)
    return {"status": "saved", "path": STATE_PATH, "message": "Workbench state saved."}


def save_draft(work_id, rel, base_hash, text):
    norm, path = safe_rel(work_id, rel, ("drafts/",))
    current = _read(path) if os.path.isfile(path) else ""
    current_hash = _sha(current)
    if base_hash != current_hash:
        return {"status": "conflict", "path": norm, "current_sha256": current_hash, "loaded_sha256": base_hash, "current_text": current, "proposed_text": text, "message": "Draft changed on disk after the Workbench loaded it; reload or merge deliberately before saving."}
    _atomic_write(path, text)
    return {"status": "saved", "path": norm, "sha256": _sha(text), "message": "Draft saved. manuscript/ was not touched."}


def create_author_note(work_id, payload):
    _ensure_scaffold(work_id)
    target_kind = _one_line(payload.get("target_kind"), "selection")
    if target_kind not in ("unit", "heading", "paragraph", "line", "selection", "image", "book"):
        raise ValueError("target_kind must be unit, heading, paragraph, line, selection, image, or book")
    target_path = _one_line(payload.get("target_path"), "drafts/candidate-draft.md")
    target_text = ""
    if target_kind == "book":
        norm = "book"
    elif target_path.startswith("assets/images/"):
        norm, _ = safe_rel(work_id, target_path, ("assets/images/",))
    else:
        norm, path = safe_rel(work_id, target_path, ("drafts/", "manuscript/"))
        target_text = _read(path)
    body = (payload.get("note_body") or "").strip()
    if not body:
        raise ValueError("note_body is required")
    quote = payload.get("text_quote") or payload.get("quote") or ""
    start, end = payload.get("start"), payload.get("end")
    context = target_text[max(0, int(start or 0) - 240):int(start or 0)] + target_text[int(end or 0):int(end or 0) + 240]
    created = now_iso()
    record = {"schema_version": 1, "kind": "author-note", "id": _id("note", work_id, norm, quote, body, created), "unit_id": _one_line(payload.get("unit_id")), "target_path": norm, "target_kind": target_kind, "text_quote": quote, "quote_hash": _sha(quote) if quote else "", "start": start, "end": end, "surrounding_context_hash": _sha(context) if context else "", "note_body": body, "status": "open", "provenance": _one_line(payload.get("provenance"), "author"), "source_refs": payload.get("source_refs") if isinstance(payload.get("source_refs"), list) else [], "graph_refs": payload.get("graph_refs") if isinstance(payload.get("graph_refs"), list) else [], "created_at": created, "updated_at": created}
    _append(os.path.join(work_base(work_id), AUTHOR_NOTES_PATH), json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
    return {"status": "note", "note": record, "message": "Author note saved. No prose was changed."}


def _find_note(work_id, note_id):
    for row in _jsonl(os.path.join(work_base(work_id), AUTHOR_NOTES_PATH)):
        if row.get("kind") == "author-note" and row.get("id") == note_id:
            return row
    return None


def footnote_candidate_from_note(work_id, note_id):
    note = _find_note(work_id, note_id)
    if not note:
        raise ValueError(f"unknown author note: {note_id}")
    created = now_iso()
    cid = _id("fn", note_id, note.get("note_body", ""), created)
    candidate = {"schema_version": 1, "kind": "footnote-candidate", "id": cid, "note_id": note_id, "work": work_id, "unit_id": note.get("unit_id", ""), "target_path": note.get("target_path", ""), "candidate_text": note.get("note_body", ""), "source_quote": note.get("text_quote", ""), "status": "candidate", "created_at": created, "manuscript_written": False}
    base, packet_dir = work_base(work_id), os.path.join(work_base(work_id), GATE_DIR)
    os.makedirs(packet_dir, exist_ok=True)
    json_path, md_path = os.path.join(packet_dir, cid + ".json"), os.path.join(packet_dir, cid + ".md")
    _json_write(json_path, candidate)
    _atomic_write(md_path, f"# TYF footnote candidate: {cid}\n\nThis packet was derived from an author note. It is a candidate footnote, not a manuscript insertion.\n\n- work: {work_id}\n- note: {note_id}\n- target: {note.get('target_path', '')}\n- unit: {note.get('unit_id', '')}\n- manuscript written: no\n\n## Candidate text\n\n{note.get('note_body', '')}\n\n## Source quote\n\n{note.get('text_quote', '') or '(none)'}\n\n## Next\n\nRefine this in draft or review space. Any manuscript insertion still goes through proposal, audit, author review, author decision, and the controlled write.\n")
    _append(os.path.join(base, AUTHOR_NOTES_PATH), json.dumps(candidate, ensure_ascii=False, sort_keys=True) + "\n")
    return {"status": "footnote-candidate", "candidate": candidate, "json": os.path.relpath(json_path, base).replace(os.sep, "/"), "markdown": os.path.relpath(md_path, base).replace(os.sep, "/"), "message": "Footnote candidate written. manuscript/ was not touched."}


def gate_packet_from_selection(work_id, payload):
    norm, path = safe_rel(work_id, _one_line(payload.get("path"), "drafts/candidate-draft.md"), ("drafts/",))
    current = _read(path) if os.path.isfile(path) else ""
    current_hash = _sha(current)
    if payload.get("base_hash", "") != current_hash:
        return {"status": "conflict", "path": norm, "current_sha256": current_hash, "loaded_sha256": payload.get("base_hash", ""), "message": "Draft changed on disk after the Workbench loaded it; reload before building a Gate packet."}
    selection = payload.get("selection") or current
    if not selection.strip():
        raise ValueError("selection or non-empty draft text is required")
    note = _one_line(payload.get("note"), "Workbench selection")
    pid = _id("gate", work_id, norm, current_hash, selection, note)
    base, packet_dir = work_base(work_id), os.path.join(work_base(work_id), GATE_DIR)
    os.makedirs(packet_dir, exist_ok=True)
    record = {"schema_version": 1, "kind": "workbench-gate-packet", "id": pid, "work": work_id, "unit_id": _one_line(payload.get("unit_id")), "source_path": norm, "source_sha256": current_hash, "selection": selection, "note": note, "created_at": now_iso(), "manuscript_written": False}
    json_path, md_path = os.path.join(packet_dir, pid + ".json"), os.path.join(packet_dir, pid + ".md")
    _json_write(json_path, record)
    _atomic_write(md_path, f"# TYF Workbench Gate packet: {pid}\n\nThis packet was prepared from the local Workbench. It is not manuscript text and it is not author acceptance.\n\n- work: {work_id}\n- unit: {record['unit_id'] or '(unspecified)'}\n- source: {norm}\n- source sha256: `{current_hash}`\n- note: {note}\n- manuscript written: no\n\n## Selected candidate text\n\n{selection}\n\n## Next\n\nIf the author accepts this material for the manuscript, continue through proposal, audit, author review, author decision, and the controlled write.\n")
    return {"status": "packet", "id": pid, "json": os.path.relpath(json_path, base).replace(os.sep, "/"), "markdown": os.path.relpath(md_path, base).replace(os.sep, "/"), "message": "Gate packet written. manuscript/ was not touched."}


def _html(data, token=""):
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>TYF Workbench v0.6</title><style>
body{{margin:0;background:#fbfaf7;color:#24211d;font-family:Inter,system-ui,sans-serif}}header{{padding:16px 22px;border-bottom:1px solid #d8d1c6;background:#fffdf9}}h1{{margin:0;font-size:22px}}.sub,.status{{color:#6b6258;font-size:13px}}.shell{{display:grid;grid-template-columns:260px minmax(360px,1.2fr) minmax(340px,1fr);min-height:calc(100vh - 72px)}}nav,main{{border-right:1px solid #d8d1c6}}h2{{margin:0;padding:12px 14px;border-bottom:1px solid #d8d1c6;color:#6b6258;font-size:13px;text-transform:uppercase;letter-spacing:.06em}}button,input,select,textarea{{font:inherit}}button{{border:1px solid #d8d1c6;background:#fffdf9;border-radius:7px;padding:8px 10px;cursor:pointer}}button.primary{{background:#315d75;color:white;border-color:#315d75}}.unit{{display:block;width:calc(100% - 20px);margin:8px 10px;text-align:left}}.unit.active{{outline:2px solid #315d75}}.editor{{display:flex;flex-direction:column}}#draftText{{flex:1;min-height:60vh;border:0;padding:20px;background:#fffdf9;font:18px/1.62 Georgia,serif}}.tools,.panel{{padding:10px;border-top:1px solid #d8d1c6;background:#eee8de;display:flex;gap:8px;flex-wrap:wrap;align-items:center}}.panel{{display:block;border-bottom:1px solid #d8d1c6;border-top:0;background:#fbfaf7}}.grow{{flex:1;min-width:170px}}.reader{{padding:18px;background:#fffdf9;border-bottom:1px solid #d8d1c6;max-height:36vh;overflow:auto;white-space:pre-wrap;font:17px/1.58 Georgia,serif}}.note{{border:1px solid #d8d1c6;border-radius:8px;background:#fffdf9;padding:8px;margin:8px 0}}pre{{white-space:pre-wrap;max-height:180px;overflow:auto;background:#fffdf9;border:1px solid #d8d1c6;padding:8px}}@media(max-width:1050px){{.shell{{grid-template-columns:1fr}}nav,main{{border-right:0;border-bottom:1px solid #d8d1c6}}}}
</style></head><body><header><h1>TYF Workbench v0.6</h1><div id="meta" class="sub"></div></header><div class="shell"><nav><h2>Book map</h2><div id="units"></div></nav><main class="editor"><h2 id="draftHead">Draft surface</h2><textarea id="draftText" spellcheck="true"></textarea><div class="tools"><button class="primary" id="saveDraft">Save Draft</button><button id="imageBlock">Add Image Block</button><button id="gatePacket">Build Gate Packet</button><input id="packetNote" class="grow" placeholder="selection note"><span id="draftStatus" class="status"></span></div></main><aside><h2>Manuscript preview</h2><div id="manuscript" class="reader"></div><div class="panel"><select id="noteKind"><option>selection</option><option>paragraph</option><option>line</option><option>unit</option><option>image</option><option>book</option></select><textarea id="noteBody" placeholder="What should the desk remember here?" style="width:100%;min-height:80px;margin-top:8px"></textarea><div class="tools"><button id="saveNote">Save Author Note</button><button id="footnoteLast">Footnote Candidate</button><span id="noteStatus" class="status"></span></div></div><div class="panel"><strong>Notes on this unit</strong><div id="noteList"></div></div><div class="panel"><strong>Style</strong><pre id="style"></pre></div><div class="panel"><strong>Images</strong><div id="assets"></div></div></aside></div><script>
let data={payload}; const token={json.dumps(token)}; let active=null; const draft=document.getElementById('draftText');
function esc(s){{return String(s||'').replace(/[&<>"']/g,c=>({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}}[c]))}} function units(){{return data.book_map.units||[]}} function sel(){{return {{text:draft.value.slice(draft.selectionStart,draft.selectionEnd),start:draft.selectionStart,end:draft.selectionEnd}}}} function stat(id,msg,cls){{let e=document.getElementById(id);e.textContent=msg||'';e.className='status '+(cls||'')}} async function post(url,body){{let r=await fetch(url,{{method:'POST',headers:{{'Content-Type':'application/json','X-TYF-Token':token}},body:JSON.stringify(body)}});let j=await r.json();if(!r.ok)throw j;return j}} async function reload(){{data=await fetch('/workbench-data.json').then(r=>r.json());render(active&&active.id)}}
function render(id){{document.getElementById('meta').textContent=`${{data.work.title}} · ${{data.work.language}} · ${{data.work.status}}`;active=units().find(u=>u.id===id)||units().find(u=>u.id===data.active_unit_id)||units()[0];document.getElementById('units').innerHTML=units().map(u=>`<button class="unit ${{active&&active.id===u.id?'active':''}}" data-u="${{esc(u.id)}}"><b>${{esc(u.title||u.id)}}</b><br><span class="status">${{esc(u.role)}} · ${{u.draft.exists?'draft':'new draft'}} · ${{u.manuscript.exists?'manuscript':'no manuscript'}}</span></button>`).join('');document.querySelectorAll('[data-u]').forEach(b=>b.onclick=()=>{{active=units().find(u=>u.id===b.dataset.u);render(b.dataset.u);post('/api/state',{{active_unit_id:active.id,active_path:active.draft.path,selection:sel()}}).catch(()=>{{}})}});if(!active)return;document.getElementById('draftHead').textContent='Draft surface: '+(active.title||active.id);draft.value=active.draft.text||'';draft.dataset.baseHash=active.draft.sha256;document.getElementById('manuscript').textContent=active.manuscript.exists?active.manuscript.text:'No approved manuscript unit exists for this draft yet.';stat('draftStatus',active.draft.path+(active.draft.exists?'':' (new)'));let notes=(active.notes||[]).filter(n=>n.kind==='author-note');document.getElementById('noteList').innerHTML=notes.length?notes.slice().reverse().map(n=>`<div class="note"><div class="status">${{esc(n.id)}} · ${{esc(n.target_kind)}} · ${{esc(n.target_path)}}</div>${{esc(n.note_body)}}<br><button data-fn="${{esc(n.id)}}">Make footnote candidate</button></div>`).join(''):'<p class="status">No notes on this unit yet.</p>';document.querySelectorAll('[data-fn]').forEach(b=>b.onclick=()=>footnote(b.dataset.fn));document.getElementById('style').textContent=(data.style.book_style||'')+'\n---\n'+(data.style.style_sheet||'');document.getElementById('assets').innerHTML=(data.assets.files||[]).map(f=>`<p>${{esc(f.file)}} (${{f.bytes}} bytes)</p>`).join('')||'<p class="status">No image assets recorded yet.</p>'}}
async function footnote(id){{try{{let r=await post('/api/footnote-candidate',{{note_id:id}});stat('noteStatus',r.message,'ok');await reload()}}catch(e){{stat('noteStatus',e.message||'Footnote failed','warn')}}}}
draft.onselect=()=>active&&post('/api/state',{{active_unit_id:active.id,active_path:active.draft.path,selection:sel()}}).catch(()=>{{}});document.getElementById('saveDraft').onclick=async()=>{{try{{let r=await post('/api/save-draft',{{path:active.draft.path,base_hash:active.draft.sha256,text:draft.value}});stat('draftStatus',r.message,'ok');await reload()}}catch(e){{stat('draftStatus',e.message||'Save failed. Use server mode.','warn')}}}};document.getElementById('imageBlock').onclick=()=>{{let file=prompt('Image file under assets/images/');if(!file)return;let alt=prompt('Alt text / caption hint')||'image';let block=`\n\n![${{alt}}](../assets/images/${{file}})\n*${{alt}}*\n`;let i=draft.selectionStart||draft.value.length;draft.value=draft.value.slice(0,i)+block+draft.value.slice(i);draft.focus();draft.selectionStart=draft.selectionEnd=i+block.length}};document.getElementById('gatePacket').onclick=async()=>{{try{{let r=await post('/api/gate-packet',{{path:active.draft.path,base_hash:active.draft.sha256,selection:sel().text,note:document.getElementById('packetNote').value,unit_id:active.id}});stat('draftStatus',r.message,'ok')}}catch(e){{stat('draftStatus',e.message||'Packet failed','warn')}}}};document.getElementById('saveNote').onclick=async()=>{{try{{let s=sel();let r=await post('/api/author-note',{{unit_id:active.id,target_path:active.draft.path,target_kind:document.getElementById('noteKind').value,text_quote:s.text,start:s.start,end:s.end,note_body:document.getElementById('noteBody').value}});document.getElementById('noteBody').value='';stat('noteStatus',r.message,'ok');await reload()}}catch(e){{stat('noteStatus',e.message||'Note failed','warn')}}}};document.getElementById('footnoteLast').onclick=()=>{{let notes=(active.notes||[]).filter(n=>n.kind==='author-note');if(!notes.length)return stat('noteStatus','No author note on this unit yet.','warn');footnote(notes[notes.length-1].id)}};render(data.active_unit_id);
</script></body></html>"""


class ReusableThreadingHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True


def _handler(work_id):
    class Handler(http.server.BaseHTTPRequestHandler):
        server_version = "TYFWorkbench/0.6"

        def _json(self, status, payload):
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(status); self.send_header("Content-Type", "application/json; charset=utf-8"); self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body)

        def _html(self, text):
            body = text.encode("utf-8")
            self.send_response(200); self.send_header("Content-Type", "text/html; charset=utf-8"); self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body)

        def _payload(self):
            raw = self.rfile.read(min(int(self.headers.get("Content-Length", "0")), 4 * 1024 * 1024)).decode("utf-8")
            return json.loads(raw or "{}")

        def _token_ok(self):
            if self.headers.get("X-TYF-Token", "") == getattr(self.server, "tyf_token", ""):
                return True
            self._json(403, {"status": "error", "message": "Missing or invalid local Workbench capability token."}); return False

        def do_GET(self):  # noqa: N802
            path = urllib.parse.urlparse(self.path).path
            if path in ("/", "/index.html"):
                self._html(_html(workbench_data(work_id), getattr(self.server, "tyf_token", "")))
            elif path == "/workbench-data.json":
                self._json(200, workbench_data(work_id))
            else:
                self.send_error(404)

        def do_POST(self):  # noqa: N802
            if not self._token_ok():
                return
            try:
                path, payload = urllib.parse.urlparse(self.path).path, self._payload()
                if path == "/api/state":
                    self._json(200, save_workbench_state(work_id, payload))
                elif path == "/api/save-draft":
                    r = save_draft(work_id, payload.get("path", "drafts/candidate-draft.md"), payload.get("base_hash", ""), payload.get("text", "")); self._json(409 if r.get("status") == "conflict" else 200, r)
                elif path == "/api/author-note":
                    self._json(200, create_author_note(work_id, payload))
                elif path == "/api/footnote-candidate":
                    self._json(200, footnote_candidate_from_note(work_id, payload.get("note_id", "")))
                elif path == "/api/gate-packet":
                    r = gate_packet_from_selection(work_id, payload); self._json(409 if r.get("status") == "conflict" else 200, r)
                else:
                    self.send_error(404)
            except ValueError as e:
                self._json(400, {"status": "error", "message": str(e)})
            except Exception as e:  # noqa: BLE001
                self._json(500, {"status": "error", "message": str(e)})

        def log_message(self, fmt, *args):  # noqa: A003
            return
    return Handler


def write_surface_files(work_id):
    data, base = workbench_data(work_id), work_base(work_id)
    surface = os.path.join(base, SURFACE_DIR)
    os.makedirs(surface, exist_ok=True)
    html_path, data_path = os.path.join(surface, "index.html"), os.path.join(surface, "workbench-data.json")
    _json_write(data_path, data)
    _atomic_write(html_path, _html(data))
    return html_path, data_path


def run_server(work_id, host, port, open_browser=False):
    server = ReusableThreadingHTTPServer((host, int(port)), _handler(work_id))
    server.tyf_token = secrets.token_urlsafe(24)
    url = f"http://{host}:{server.server_port}/"
    print(f"Serving TYF Workbench v0.6 at {url}")
    print("Local side-effect APIs require a per-session capability token embedded in this page.")
    if open_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped TYF Workbench.")


def main(argv=None):
    parser = argparse.ArgumentParser(prog="tyf_workbench", description="TYF local double-surface Workbench v0.6")
    parser.add_argument("work", nargs="?", default=None, help="work id; defaults to active root work")
    parser.add_argument("--serve", action="store_true", help="serve the local browser Workbench with draft, note, and packet actions")
    parser.add_argument("--host", default="127.0.0.1", help="host for --serve; default is loopback")
    parser.add_argument("--port", type=int, default=8766, help="port for --serve")
    parser.add_argument("--open", action="store_true", help="open the Workbench in the default browser")
    args = parser.parse_args(argv)
    require_workspace()
    work_id = args.work or active_work_id()
    require_work(work_id)
    html_path, data_path = write_surface_files(work_id)
    print(f"TYF Workbench v0.6: {html_path.replace(os.sep, '/')}")
    print(f"Workbench data: {data_path.replace(os.sep, '/')}")
    print(f"Book map: {os.path.join(work_base(work_id), BOOK_MAP_PATH).replace(os.sep, '/')}")
    print(f"Author notes: {os.path.join(work_base(work_id), AUTHOR_NOTES_PATH).replace(os.sep, '/')}")
    print("No manuscript text was written.")
    if args.serve:
        run_server(work_id, args.host, args.port, args.open)


if __name__ == "__main__":
    main()
