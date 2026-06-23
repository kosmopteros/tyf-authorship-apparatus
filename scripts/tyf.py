#!/usr/bin/env python3
"""tyf: the TYF workspace helper.

The helper performs the concrete file operations of a TYF workspace so the agent
does not freelance, and it is the single writer into a work's manuscript/.

Commands:
  tyf init [<name>]                       scaffold a workspace (idempotent: creates
                                          only missing structure, never clobbers)
  tyf status                              active work, band, write control, write zones
  tyf new-work <id> [--type T] [--register R]
  tyf start [path] [--title T]           open the writing runway, optionally
                                          preserving an arrival first
  tyf begin <id> [--title T] [--register R]
                                          create a first-session packet for a book
  tyf import <path> [--kind K] [--work id]
                                          preserve existing material without manuscript writes
  tyf capture <work-id> --kind K --text TEXT
                                          append author source/voice/claim/question notes
  tyf resume [work-id]                    show continuity and the next useful move
  tyf open <work-id>                      set active work; print what to load
  tyf mark-ready <work-id> <unit>         flag a unit for audit
  tyf propose <work-id> --from <draft>    create a manuscript proposal record
  tyf review <work-id> <proposal-id>      write an author-readable review packet
  tyf audit <work-id> <unit>              print or record the audit checklist
  tyf accept <work-id> <proposal-id>      create an author decision record
  tyf adopt <work-id> <unit> --evidence E adopt a direct author manuscript edit
  tyf write <work-id> --decision <id>     ONLY writer into manuscript/
  tyf doctor [--repair]                   workspace integrity check; --repair creates
                                          any missing required structure
  tyf reflexes                            show transparent hooks and reflexes
  tyf snapshot --message M                explicit git recovery commit for a workspace
  tyf check [--strict] [--quiet]          documentation-honesty check on the pack
  tyf notice [--save] [--all] [--peek]    surface forgotten/unfinished/stale items;
                                          ledger-backed; never modifies
  tyf dismiss <hash>                      quiet a surfaced item; resurfaces on context change
  tyf reconcile [--export]                show the ledger; --export mirrors it to Markdown
  tyf update [--force]                    notify-only check for a newer release; never modifies

Apparatus memory (JSONL + SQLite, stdlib)
  The body of work stays in Markdown and YAML, owned by and legible to the
  author. Only apparatus bookkeeping lives under .tyf/: events.jsonl is the
  human-readable hash-chained spine of apparatus actions, while ledger.db is the
  derived SQLite notice index and event mirror. It uses only stdlib modules:
  no third-party dependencies. Notice state is rebuildable by re-scanning
  content, and mirrorable to Markdown with `tyf reconcile --export`. See
  docs/ATTENTIVENESS.md.

Documentation-honesty hook
  Every mutating command (init, new-work, start, begin, import, capture,
  propose, review, audit --record, accept, adopt, write, mark-ready) runs `check` as a
  warn-only tail step, so doc drift surfaces at the moment structure changes
  without blocking authorship. `tyf check` on its own hard-fails on drift
  (exit 1) unless told otherwise. This is the deterministic, zero-token half of
  the keeping-documentation-honest skill; semantic drift still needs a reading
  pass. Disable the tail hook with the env var TYF_NO_DOC_HOOK=1.

State files are plain YAML. No third-party dependencies.
"""

import os
import sys
import re
import argparse
import datetime
import json
import shutil
import unicodedata
import zipfile
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except AttributeError:
    pass  # degradation: ok: older Python streams may not support reconfigure; keep host defaults

# ---------- tiny tolerant reader for the flat YAML we generate ----------

def _yaml_load_scalar(value):
    value = value.strip()
    if len(value) >= 2 and value[0] == '"' and value[-1] == '"':
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value[1:-1]
    return value


def read_state(path):
    # Minimal reader for the simple YAML this tool generates: top-level
    # `key: value`, one level of `key:` mappings with two-space children, and
    # `- item` lists under a key. All state is local; nothing global.
    data = {}
    if not os.path.isfile(path):
        return data
    container = None  # last top-level key whose value was empty (holds a map or list)
    with open(path, encoding="utf-8") as f:
        for raw in f:
            line = raw.rstrip("\n")
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            indent = len(line) - len(line.lstrip(" "))
            s = line.strip()
            if s.startswith("- "):
                if container is not None:
                    if not isinstance(data.get(container), list):
                        data[container] = []
                    data[container].append(_yaml_load_scalar(s[2:].strip()))
                continue
            if ":" not in s:
                continue
            k, _, v = s.partition(":")
            k, v = k.strip(), v.strip()
            if indent == 0:
                if v == "":
                    data[k] = {}
                    container = k
                else:
                    data[k] = _yaml_load_scalar(v)
                    container = None
            elif container is not None:
                if not isinstance(data.get(container), dict):
                    data[container] = {}
                data[container][k] = _yaml_load_scalar(v)
    return data


def get(d, *path, default=None):
    for p in path:
        if isinstance(d, dict) and p in d:
            d = d[p]
        else:
            return default
    return d

# ---------- helpers ----------

def now():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def atomic_write(path, text):
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
            pass  # degradation: ok: temp cleanup failure should not mask the original write result

def append(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(text)

def mkdirs(*paths):
    for p in paths:
        os.makedirs(p, exist_ok=True)


def _one_line(value, fallback=""):
    """Collapse user labels for simple YAML/frontmatter lines."""
    text = (value or fallback or "").replace("\r", " ").replace("\n", " ").strip()
    return text or fallback


def _yaml_scalar(value):
    return json.dumps(_one_line(value), ensure_ascii=False)


def _require_workspace():
    """Refuse any mutating command run outside a TYF workspace root."""
    if not os.path.isfile("WORKSPACE_STATE.yaml"):
        sys.exit("Not in a TYF workspace (no WORKSPACE_STATE.yaml). "
                 "Run `tyf init`, or cd into the workspace root.")
    real = os.path.realpath(".")
    if os.path.abspath(".") != real:
        os.chdir(real)


def _safe_work_id(work_id):
    """A work id is a simple slug, never a path. Enforce a strict charset so a
    write can never escape the protected work root and the rule matches the
    error message."""
    if (not work_id or work_id in (".", "..")
            or os.path.isabs(work_id) or work_id.startswith("~")
            or not re.fullmatch(r"[A-Za-z0-9._-]+", work_id)):
        sys.exit(f"Refused: unsafe work id {work_id!r}. Use letters, digits, "
                 "'.', '-' or '_' only; no spaces, slashes, '..', or absolute paths.")
    return work_id


ROOT_WORK_ID = "work"


def _is_root_work(work):
    return work == ROOT_WORK_ID and os.path.isfile("work.yaml")


def _work_base(work):
    return "." if _is_root_work(work) else os.path.join("works", work)


def _work_path(work, *parts):
    return os.path.join(_work_base(work), *parts)


def _work_display_path(work, *parts):
    return _work_path(work, *parts).replace(os.sep, "/")


def _within(base, target):
    """True if target resolves to inside base (real paths; symlink-safe)."""
    base = os.path.realpath(base)
    target = os.path.realpath(target)
    return target == base or target.startswith(base + os.sep)


def _reject_symlink_components(path, label="path"):
    """Reject symlinks at any existing component of a protected path."""
    abs_path = os.path.abspath(path)
    parts = Path(abs_path).parts
    if not parts:
        return
    cur = parts[0]
    for part in parts[1:]:
        cur = os.path.join(cur, part)
        if os.path.islink(cur):
            sys.exit(f"Refused: {label} crosses a symlink: {cur}")


def _ensure_real_dir(path, label="directory"):
    _reject_symlink_components(path, label)
    if os.path.exists(path) and not os.path.isdir(path):
        sys.exit(f"Refused: {label} is not a directory: {path}")
    os.makedirs(path, exist_ok=True)
    _reject_symlink_components(path, label)


def _confine_work(work):
    """Refuse a work whose path resolves outside its protected root."""
    if _is_root_work(work):
        root = os.path.realpath(".")
        for rel in ("work.yaml", "outline", "drafts", "manuscript", ".review", "style-sheet.md"):
            if os.path.exists(rel):
                _reject_symlink_components(rel, rel)
                if not _within(root, os.path.realpath(rel)):
                    sys.exit(f"Refused: root work path resolves outside the workspace: {rel}")
        return
    root = os.path.realpath(".")
    works_logical = os.path.abspath("works")
    if os.path.islink(works_logical):
        sys.exit("Refused: works/ is a symlink; protected workspace roots must be real directories.")
    _reject_symlink_components("works", "works/")
    base = os.path.realpath(works_logical)
    target_logical = os.path.abspath(os.path.join("works", work))
    if os.path.islink(target_logical):
        sys.exit(f"Refused: work {work!r} is a symlink; protected works must be real directories.")
    target = os.path.realpath(target_logical)
    if not _within(root, base):
        sys.exit("Refused: works/ resolves outside the workspace.")
    if not (target == base or target.startswith(base + os.sep)):
        sys.exit(f"Refused: work {work!r} resolves outside works/ (symlink or mount escape).")


def _require_work(work):
    """Refuse a command that operates on a work that does not exist."""
    if not os.path.isfile(_work_path(work, "work.yaml")):
        sys.exit(f"Refused: no work {work!r} ({_work_display_path(work, 'work.yaml')} not found). Run `tyf start` in the book folder first.")


def _work_yaml_path(work):
    return _work_path(work, "work.yaml")


def _work_status(work):
    return read_state(_work_yaml_path(work)).get("status")


def _set_work_status(work, status):
    path = _work_yaml_path(work)
    if not os.path.isfile(path):
        sys.exit(f"Refused: no work {work!r} ({_work_display_path(work, 'work.yaml')} not found).")
    lines = open(path, encoding="utf-8").read().splitlines()
    out, replaced = [], False
    for ln in lines:
        if ln.startswith("status:"):
            out.append(f"status: {status}")
            replaced = True
        else:
            out.append(ln)
    if not replaced:
        out.append(f"status: {status}")
    atomic_write(path, "\n".join(out) + "\n")


def _require_work_status(work, expected, action):
    actual = _work_status(work)
    if actual != expected:
        sys.exit(f"Refused: {action} requires work status {expected!r}; current status is {actual!r}.")

# ---------- documentation-honesty check (deterministic, zero-token) ----------

# Number words this check understands, for catching stale spelled-out counts.
_NUMBER_WORDS = ["eleven", "twelve", "thirteen", "fourteen", "fifteen",
                 "sixteen", "seventeen", "eighteen", "nineteen", "twenty"]

# Skill IDs that were renamed during de-ceremonialization. A live reference to
# any of these in a routing surface is drift. (VALIDATION.md is allowed to name
# them as historical changelog.)
_DEAD_SKILL_IDS = [
    "offering-sources", "conducting-sittings", "building-the-field",
    "keeping-voice-ledger", "reading-as-first-reader", "diagnosing-with-loupe",
    "auditing-with-devils-reader", "operating-the-gate",
]

# CLI commands that were renamed. A live reference is drift.
_DEAD_COMMANDS = ["tyf gate", "--apply <draft>", "fire-devils-reader", "tyf write --confirm", "tyf today"]

# Public v0.5 surfaces are root single-work by default. These old public path
# shapes are allowed only in historical validation/changelog material or inside
# tests/checker code that name them as canaries.
_STALE_SINGLE_WORK_PATHS = [
    "works/<id>",
    "works/*/",
    "works/*/drafts",
    "works/*/manuscript",
    "works/*/.review",
]

def _pack_root():
    """The pack root. Honors TYF_PACK_ROOT (set this when the helper is installed
    or copied outside the repo); otherwise resolves from this script's real
    location (realpath, so a symlinked `tyf` on PATH still finds the repo)."""
    env = os.environ.get("TYF_PACK_ROOT")
    if env:
        return os.path.realpath(env)
    return os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

def _iter_files(root, exts):
    skip_dirs = {
        "__pycache__",
        ".git",
        ".fbs",
        ".claude",
        ".pytest_cache",
        "build",
        "dist",
    }
    for r, dirs, fs in os.walk(root):
        dirs[:] = [d for d in dirs if d not in skip_dirs and not d.endswith(".egg-info")]
        for f in fs:
            if f.endswith(exts):
                yield os.path.join(r, f)

def _read_pack_file(path):
    with open(path, encoding="utf-8") as f:
        return f.read()

def _iter_pack_lines(path):
    with open(path, encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            yield i, line

def _looks_like_today_command_list(line):
    low = line.lower()
    if not re.search(r"\btoday\b", low):
        return False
    command_list_markers = (
        "advanced helper commands",
        "helper commands",
        "commands include",
        "command list",
        "available commands",
    )
    today_pos = low.find('today')
    for marker in command_list_markers:
        marker_pos = low.find(marker)
        if marker_pos != -1 and marker_pos <= today_pos and ("`" in line or "," in line):
            return True
    if "`today`" in low and "," in line and re.search(r"\b(init|new-work|begin|start|write|resume)\b.*\btoday\b", low):
        return True
    return False

def run_doc_check(root=None):
    """Return (problems, notes). Pure file/string inspection; no LLM, no deps."""
    import json as _json
    root = root or _pack_root()
    problems, notes = [], []
    skills_dir = os.path.join(root, "skills")
    if not os.path.isdir(skills_dir):
        return ([f"no skills/ directory under {root}"], [])

    skills = sorted(d for d in os.listdir(skills_dir)
                    if os.path.isdir(os.path.join(skills_dir, d)))
    n = len(skills)
    notes.append(f"{n} skill directories")

    # 1. frontmatter name matches directory; description starts with "Use when"
    for s in skills:
        p = os.path.join(skills_dir, s, "SKILL.md")
        if not os.path.isfile(p):
            problems.append(f"{s}: missing SKILL.md"); continue
        t = _read_pack_file(p)
        m = re.search(r"^name:\s*(.+)$", t, re.M)
        d = re.search(r"^description:\s*(.+)$", t, re.M)
        if not m or m.group(1).strip() != s:
            problems.append(f"{s}: frontmatter name does not match directory")
        desc = d.group(1).strip().strip("\"'") if d else ""
        if not desc.lower().startswith("use when"):
            problems.append(f"{s}: description should start with 'Use when'")

    # 2. spelled-out and numeric skill counts across docs must equal n
    wrong_words = [w for i, w in enumerate(_NUMBER_WORDS, start=11) if i != n]
    for p in _iter_files(root, (".md", ".sh")):
        rel = os.path.relpath(p, root)
        for i, line in _iter_pack_lines(p):
            low = line.lower()
            for w in wrong_words:
                if re.search(rf"\ball {w}\b", low) or re.search(rf"\b{w}\b skills?\b", low):
                    problems.append(f"{rel}:{i}: stale skill count '{w}' (should reflect {n})")
            mm = re.search(r"\b(\d+)\s+skills\b", low)
            if mm and int(mm.group(1)) != n:
                problems.append(f"{rel}:{i}: stale skill count '{mm.group(1)}' (should be {n})")

    # 3. dead skill IDs and dead command names in routing surfaces. Two files
    #    legitimately name dead tokens: VALIDATION.md (historical changelog) and
    #    this script (the check engine lists them as search targets).
    _dead_ref_exempt = {
        "CHANGELOG.md",
        "VALIDATION.md",
        os.path.join("scripts", "tyf.py"),
        os.path.join("tests", "test_tyf.py"),
        os.path.join("tests", "test_solo_oracles.py"),
    }
    for p in _iter_files(root, (".md", ".sh", ".yaml", ".yml", ".py", ".json")):
        rel = os.path.relpath(p, root)
        if rel in _dead_ref_exempt:
            continue
        txt = _read_pack_file(p)
        for dead in _DEAD_SKILL_IDS:
            if dead in txt:
                problems.append(f"{rel}: dead skill id reference '{dead}'")
        for dead in _DEAD_COMMANDS:
            if dead in txt:
                problems.append(f"{rel}: dead command reference '{dead}'")

    # 4. contributor context files must be byte-identical. Author-facing release
    #    exports intentionally omit these root files and ship author-context/*
    #    templates instead.
    ctx = [os.path.join(root, f) for f in ("CLAUDE.md", "AGENTS.md", "GEMINI.md")]
    present = [c for c in ctx if os.path.isfile(c)]
    if len(present) == 3:
        bodies = {_read_pack_file(c) for c in present}
        if len(bodies) != 1:
            problems.append("CLAUDE.md / AGENTS.md / GEMINI.md have drifted apart")
        else:
            notes.append("context files identical")
    else:
        author_ctx = [os.path.join(root, "author-context", f)
                      for f in ("CLAUDE.md", "AGENTS.md", "GEMINI.md")]
        if not present and all(os.path.isfile(c) for c in author_ctx):
            notes.append("release export uses author-context templates")
        else:
            problems.append("one or more context files missing (CLAUDE/AGENTS/GEMINI)")

    # 5. manifests parse as JSON
    for j in (".claude-plugin/plugin.json", ".claude-plugin/marketplace.json",
              ".codex-plugin/plugin.json", ".cursor-plugin/plugin.json",
              "gemini-extension.json", "package.json"):
        p = os.path.join(root, j)
        if os.path.isfile(p):
            try:
                with open(p, encoding="utf-8") as f:
                    _json.load(f)
            except Exception as e:
                problems.append(f"{j}: invalid JSON ({e})")

    manifest_versions = {}
    for p in _iter_files(root, (".json",)):
        rel = os.path.relpath(p, root).replace(os.sep, "/")
        if not rel.endswith("plugin.json"):
            continue
        if not ("/.claude-plugin/" in f"/{rel}" or "/.codex-plugin/" in f"/{rel}"
                or "/.cursor-plugin/" in f"/{rel}" or rel.startswith("plugin/")):
            continue
        try:
            with open(p, encoding="utf-8") as f:
                data = _json.load(f)
        except Exception:
            continue
        version = data.get("version")
        if version:
            manifest_versions.setdefault(str(version), []).append(rel)
    if len(manifest_versions) > 1:
        detail = "; ".join(
            f"{version}: {', '.join(paths)}"
            for version, paths in sorted(manifest_versions.items())
        )
        problems.append(f"plugin manifest version divergence ({detail})")

    # 6. no em-dash in prose except the canonical [AUTHOR: needed — what] token
    for p in _iter_files(root, (".md",)):
        rel = os.path.relpath(p, root)
        for i, line in _iter_pack_lines(p):
            if "\u2014" in line and "AUTHOR: needed" not in line:
                problems.append(f"{rel}:{i}: em-dash in prose")

    # 7. stale apparatus-memory path: the notice ledger is .tyf/ledger.db now,
    #    not the old .proposals/notice-ledger.json. (Exempt: VALIDATION.md
    #    changelog and this script, which name the old path as a search target.)
    for p in _iter_files(root, (".md", ".json", ".sh")):
        rel = os.path.relpath(p, root)
        if rel in _dead_ref_exempt:
            continue
        for i, line in _iter_pack_lines(p):
            if "notice-ledger.json" in line:
                problems.append(f"{rel}:{i}: stale ledger path 'notice-ledger.json' (now .tyf/ledger.db)")

    # 8. stale role terminology from an earlier draft. The canon role list is
    #    "interviewer, amanuensis, first reader, faithful editor, redactor".
    #    'machinist' is the reliable canary for the stale list; 'typographer'
    #    is NOT flagged because it is a legitimate craft term across the pack
    #    (the Milchin typographer canon, the five-scale framework).
    for p in _iter_files(root, (".md", ".json")):
        rel = os.path.relpath(p, root)
        if rel in _dead_ref_exempt:
            continue
        for i, line in _iter_pack_lines(p):
            if "machinist" in line.lower():
                problems.append(f"{rel}:{i}: stale role terminology 'machinist' (canon role: amanuensis)")

    # 9. The writing runway is the author-facing session front door. Routing
    #    surfaces must not quietly restore the accidental Today Mode name or
    #    the old title-gated setup.
    for p in _iter_files(root, (".md", ".json", ".sh")):
        rel = os.path.relpath(p, root)
        if rel in _dead_ref_exempt:
            continue
        for i, line in _iter_pack_lines(p):
            low = line.lower()
            stale_today_command_list = _looks_like_today_command_list(line)
            if ("tyf today" in line or "Today Mode" in line or "today-draft.md" in line
                    or ".review/today.md" in line or 'tyf start "Working Title"' in line
                    or "after getting a title" in line or stale_today_command_list):
                label = "stale today command-list routing" if stale_today_command_list else "stale writing-runway routing"
                problems.append(
                    f"{rel}:{i}: {label} "
                    "(use `tyf start` or `tyf start <path>` before drafting)"
                )

    # 10. Public v0.5 author surfaces use one root book folder as the work.
    #     Old works/<id> and works/* path shapes are implementation-compatible
    #     helper history, not the Cowork/public beta contract.
    for p in _iter_files(root, (".md", ".json", ".sh", ".yaml", ".yml")):
        rel = os.path.relpath(p, root)
        if rel in _dead_ref_exempt:
            continue
        for i, line in _iter_pack_lines(p):
            for token in _STALE_SINGLE_WORK_PATHS:
                if token in line:
                    problems.append(
                        f"{rel}:{i}: stale single-work path '{token}' "
                        "(use root `drafts/`, `.review/`, `manuscript/`, and `work.yaml`)"
                    )
                    break

    # 11. The Gate chain now includes an author-readable review packet between
    #     audit and author decision. Runtime docs that say proposal + audit +
    #     decision + write without review are stale and unsafe routing law.
    for p in _iter_files(root, (".md", ".json", ".sh", ".yaml", ".yml")):
        rel = os.path.relpath(p, root)
        if rel in _dead_ref_exempt:
            continue
        for i, line in _iter_pack_lines(p):
            low = line.lower()
            if ("tyf write --decision" in low
                    and "proposal" in low
                    and "audit" in low
                    and "decision" in low
                    and "review" not in low):
                problems.append(
                    f"{rel}:{i}: stale controlled-write chain without review packet "
                    "(use proposal, audit, author review, decision, and `tyf write --decision`)"
                )

    return problems, notes

def _print_check(problems, notes, quiet=False):
    if not quiet:
        print("tyf check (documentation honesty; deterministic, no tokens)")
        for nt in notes:
            print(f"  note: {nt}")
    if problems:
        print("  PROBLEMS:" if not quiet else "tyf check PROBLEMS:")
        for p in problems:
            print(f"    - {p}")
    elif not quiet:
        print("  no documentation drift found")

# ---------- attentiveness: the loop that notices but never modifies ----------
#
# This is the faithful attentive amanuensis. It surfaces things the author may
# have forgotten or left undone, across the three tiers of truth: tacit (in the
# author's head), documented (written but maybe stale), and enacted (the
# manuscript, which races ahead). It NEVER modifies anything. Every finding is
# a note handed back to the author, who decides. All detectors here are pure
# file and content logic: zero model tokens.
#
# Memory without git: each notice carries a content hash (a fingerprint of the
# text the notice is ABOUT) and a context hash (the surrounding situation). The
# ledger in .tyf/ledger.db remembers what was surfaced and what the author
# dismissed, keyed on those hashes, not on timestamps. mtime is used
# only as a cheap hint, never as a source of truth, because sync tools and file
# copies lie about it. The system never ranks which of two authored statements
# wins; a contradiction is surfaced for the author to adjudicate.

import hashlib

def _mtime(path):
    try:
        return os.path.getmtime(path)
    except OSError:  # degradation: ok: missing/unreadable files are treated as unchanged for notice scanning
        return 0

def _read(path):
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except OSError:  # degradation: ok: missing/unreadable text contributes no notice content
        return ""

def _h(*parts):
    """Stable short hash of normalized content. Whitespace-insensitive so a
    reflow does not read as new content."""
    norm = " ".join(" ".join(p.split()) for p in parts if p)
    return hashlib.sha256(norm.encode("utf-8")).hexdigest()[:12]

def gather_notices(root="."):
    """Return notice dicts the author may want to revisit.

    Each notice: {kind, where, message, content_hash, context_hash}.
    Surface-only. Nothing here writes, edits, or heals. Pure inspection.
    """
    notices = []
    if not os.path.isfile(os.path.join(root, "WORKSPACE_STATE.yaml")):
        return notices

    def add(kind, where, message, content, context=""):
        notices.append({
            "kind": kind, "where": where, "message": message,
            "content_hash": _h(kind, where, content),
            "context_hash": _h(context) if context else "",
        })

    def style_sheet_has_minimum_metadata(path):
        text = _read(path)
        return all(token in text for token in (
            "Writing language:",
            "## Terminology decisions",
            "## Apparatus decisions",
            "## Finish decisions",
        ))

    def style_sheet_lag_should_surface(manuscript_dir, style_sheet, write_log):
        if not (os.path.isdir(manuscript_dir) and os.path.isfile(style_sheet)):
            return False
        style_mtime = _mtime(style_sheet)
        changed = []
        try:
            names = os.listdir(manuscript_dir)
        except OSError:  # degradation: ok: unreadable manuscript dirs produce no notice
            return False
        for name in names:
            path = os.path.join(manuscript_dir, name)
            if os.path.isfile(path) and _mtime(path) > style_mtime:
                changed.append(path)
        if not changed:
            return False
        if not style_sheet_has_minimum_metadata(style_sheet):
            return True
        logged = _logged_hashes(_read(write_log))
        for path in changed:
            expected = logged.get(os.path.basename(path))
            actual = hashlib.sha256(_read(path).encode("utf-8")).hexdigest()
            if not expected or expected != actual:
                return True
        return False

    def prose_walks():
        roots = []
        for rel in ("drafts", "manuscript"):
            full = os.path.join(root, rel)
            if os.path.isdir(full):
                roots.append(full)
        works_root = os.path.join(root, "works")
        if os.path.isdir(works_root):
            roots.append(works_root)
        for base in roots:
            for r, dirs, fs in os.walk(base):
                dirs[:] = [d for d in dirs if d != ".review"]
                yield r, fs

    # AUTHOR-needed gap marks left in drafts or manuscript (forgotten to fill).
    # Context = the neighboring lines, so the same gap text in a new passage is
    # treated as a new situation (and a dismissed one resurfaces).
    for r, fs in prose_walks():
        for f in fs:
            if not f.endswith(".md"):
                continue
            p = os.path.join(r, f)
            lines = _read(p).splitlines()
            for i, line in enumerate(lines, 1):
                if "[AUTHOR: needed" in line:
                    ctx = " ".join(lines[max(0, i - 3):i + 2])
                    add("gap", f"{os.path.relpath(p, root)}:{i}",
                        "you left a gap to fill: " + line.strip()[:80], line, context=ctx)

    # Unfinished lines: prose ending mid-sentence.
    for r, fs in prose_walks():
        for f in fs:
            if not f.endswith(".md"):
                continue
            p = os.path.join(r, f)
            lines = _read(p).splitlines()
            for i, line in enumerate(lines, 1):
                s = line.rstrip()
                if s and not s.startswith(("#", "|", "-", ">", "`")):
                    if re.search(r"[,;]$", s) or re.search(r"\b(and|but|because|the|a|to|of)$", s):
                        ctx = " ".join(lines[max(0, i - 3):i + 2])
                        add("unfinished", f"{os.path.relpath(p, root)}:{i}",
                            "this line may trail off unfinished: " + s[-60:], s, context=ctx)

    # Claims logged without a source.
    cl = os.path.join(root, "knowledge-base", "claims.md")
    for ln in _read(cl).splitlines():
        if ln.strip().startswith("|") and "unsourced" in ln.lower():
            add("unsourced-claim", "knowledge-base/claims.md",
                "claim still has no source: " + ln.strip()[:70], ln)

    # Enacted-races-ahead: manuscript changed after its style sheet (mtime hint only).
    ss = os.path.join(root, "style-sheet.md")
    man = os.path.join(root, "manuscript")
    if style_sheet_lag_should_surface(man, ss, os.path.join(root, ".review", "write-log.md")):
        add("style-sheet-lag", "manuscript/",
            "manuscript changed after the style sheet; decisions may be unrecorded", "root")
    if os.path.isdir(os.path.join(root, "works")):
        for w in sorted(os.listdir(os.path.join(root, "works"))):
            wd = os.path.join(root, "works", w)
            if not os.path.isdir(wd):
                continue
            ss = os.path.join(wd, "style-sheet.md")
            man = os.path.join(wd, "manuscript")
            if style_sheet_lag_should_surface(man, ss, os.path.join(wd, ".review", "write-log.md")):
                add("style-sheet-lag", f"works/{w}",
                    "manuscript changed after the style sheet; decisions may be unrecorded", w)

    # Assumptions left untouched while the manuscript moved (mtime hint only).
    asm = os.path.join(root, "ASSUMPTIONS.md")
    if os.path.isfile(asm):
        newest_man = 0
        root_manuscript = os.path.join(root, "manuscript")
        if os.path.isdir(root_manuscript):
            for r, _, fs in os.walk(root_manuscript):
                for f in fs:
                    newest_man = max(newest_man, _mtime(os.path.join(r, f)))
        for r, _, fs in os.walk(os.path.join(root, "works")):
            if os.path.basename(r) == "manuscript":
                for f in fs:
                    newest_man = max(newest_man, _mtime(os.path.join(r, f)))
        if newest_man and newest_man - _mtime(asm) > 7 * 86400:
            add("assumptions-stale", "ASSUMPTIONS.md",
                "manuscript has moved for over a week without an assumptions update", "assumptions")

    # Registers defined but used by no work.
    regdir = os.path.join(root, "voice", "registers")
    if os.path.isdir(regdir):
        used = ""
        used += _read(os.path.join(root, "work.yaml"))
        for r, _, fs in os.walk(os.path.join(root, "works")):
            for f in fs:
                if f == "work.yaml":
                    used += _read(os.path.join(r, f))
        for rf in os.listdir(regdir):
            name = rf[:-3] if rf.endswith(".md") else rf
            if name and name not in used:
                add("unused-register", f"voice/registers/{rf}",
                    f"register '{name}' is defined but no work uses it", name)

    return notices

# ---------- the notice ledger: SQLite apparatus-memory, content-addressed ----------
#
# This is the apparatus's growing memory of the work, NOT the work itself. The
# body of work (manuscript, sources, knowledge base, voice, redactor canon,
# claims) stays in Markdown and YAML, owned by and legible to the author. Only
# machine bookkeeping the author rarely hand-edits lives here: a canonical
# hash-chained JSONL event journal for apparatus actions, plus a SQLite notice
# index (hashes, statuses, dismissals) and derived event mirror. Notice state is
# notice state is disposable derived state: it can be rebuilt by re-scanning
# content, and it can be mirrored to Markdown with `tyf reconcile --export`.

import sqlite3

def _tyf_dir(root):
    return os.path.join(root, ".tyf")

def _db_path(root):
    return os.path.join(_tyf_dir(root), "ledger.db")


def _event_log_path(root):
    return os.path.join(_tyf_dir(root), "events.jsonl")


def _event_record_hash(record):
    payload = {k: record[k] for k in sorted(record) if k != "hash"}
    data = json.dumps(payload, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"))
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def _read_event_journal(root):
    path = _event_log_path(root)
    if not os.path.isfile(path):
        return [], [f"missing canonical event journal: {path}"]
    records, problems = [], []
    with open(path, encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            if not line.strip():
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as e:
                problems.append(f"event journal line {i} is invalid JSON: {e}")
    return records, problems


def _append_event_journal(root, kind, ref="", detail=""):
    os.makedirs(_tyf_dir(root), exist_ok=True)
    records, _problems = _read_event_journal(root)
    previous = records[-1].get("hash", "") if records else ""
    seq = records[-1].get("seq", 0) + 1 if records else 1
    record = {
        "seq": seq,
        "ts": now(),
        "kind": _one_line(kind),
        "ref": _one_line(ref),
        "detail": _one_line(detail),
        "previous_hash": previous,
    }
    record["hash"] = _event_record_hash(record)
    append(_event_log_path(root), json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
    return record


def _event_journal_problems(root):
    records, problems = _read_event_journal(root)
    if problems:
        return problems
    if not records:
        return [f"canonical event journal is empty: {_event_log_path(root)}"]
    previous = ""
    for i, record in enumerate(records, 1):
        for key in ("seq", "ts", "kind", "ref", "detail", "previous_hash", "hash"):
            if key not in record:
                problems.append(f"event journal line {i} missing {key}")
        if problems:
            continue
        if record.get("seq") != i:
            problems.append(f"event journal line {i} has sequence {record.get('seq')}, expected {i}")
        if record.get("previous_hash") != previous:
            problems.append(f"event journal line {i} breaks the hash chain")
        actual = _event_record_hash(record)
        if record.get("hash") != actual:
            problems.append(f"event journal line {i} hash mismatch; possible tampering")
        previous = record.get("hash", "")
    return problems


def _event_journal_count(root):
    records, problems = _read_event_journal(root)
    if not problems:
        return len(records)
    if not os.path.isfile(_db_path(root)):
        return 0
    return None


def _db(root, create=True):
    if create:
        os.makedirs(_tyf_dir(root), exist_ok=True)
    elif not os.path.isfile(_db_path(root)):
        return None
    conn = sqlite3.connect(_db_path(root))
    conn.execute("""CREATE TABLE IF NOT EXISTS notices (
        content_hash TEXT PRIMARY KEY,
        kind TEXT, where_ref TEXT, message TEXT,
        context_hash TEXT, status TEXT,
        first_seen TEXT, last_seen TEXT, changed_at TEXT
    )""")
    conn.execute("""CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ts TEXT, kind TEXT, ref TEXT, detail TEXT
    )""")
    conn.commit()
    return conn

def log_event(root, kind, ref="", detail=""):
    """Append-only record of an apparatus action. The git-like spine."""
    if not os.path.isfile(os.path.join(root, "WORKSPACE_STATE.yaml")):
        return
    try:
        _append_event_journal(root, kind, ref, detail)
        conn = _db(root)
        conn.execute("INSERT INTO events (ts, kind, ref, detail) VALUES (?,?,?,?)",
                     (now(), kind, ref, detail))
        conn.commit()
        conn.close()
    except Exception:  # noqa: BLE001  # degradation: ok: apparatus memory must never break a real action
        pass  # apparatus memory must never break a real action

def reconcile_notices(root, notices, update=True):
    """Diff current notices against the SQLite ledger. Returns (new, still_open,
    resurfaced). Updates the ledger when update=True. Never touches the work.

    Status model, keyed on content_hash:
      - unseen content       -> new
      - seen, status 'open'  -> still_open (not re-raised as if new)
      - seen, status 'dismissed', same context_hash -> stays silent
      - seen, status 'dismissed', DIFFERENT context_hash -> resurfaced
    """
    # Dedupe within this run by notice identity. Location is part of the hash,
    # so identical gaps in distinct places stay distinct epistemic objects.
    deduped = []
    seen_hashes = set()
    for n in notices:
        if n["content_hash"] in seen_hashes:
            continue
        seen_hashes.add(n["content_hash"])
        deduped.append(n)

    conn = _db(root, create=update)
    if conn is None:
        return deduped, [], []
    cur = conn.cursor()
    rows = {r[0]: r for r in cur.execute(
        "SELECT content_hash, kind, where_ref, message, context_hash, status FROM notices")}
    new, still_open, resurfaced = [], [], []
    seen_now = set()

    for n in deduped:
        ch = n["content_hash"]
        seen_now.add(ch)
        row = rows.get(ch)
        if row is None:
            new.append(n)
            if update:
                cur.execute("""INSERT OR IGNORE INTO notices
                    (content_hash, kind, where_ref, message, context_hash, status,
                     first_seen, last_seen, changed_at)
                    VALUES (?,?,?,?,?, 'open', ?,?,?)""",
                    (ch, n["kind"], n["where"], n["message"], n["context_hash"],
                     now(), now(), now()))
        else:
            status, ctx = row[5], row[4]
            if update:
                cur.execute("UPDATE notices SET last_seen=?, where_ref=? WHERE content_hash=?",
                            (now(), n["where"], ch))
            if status == "dismissed":
                if ctx != n["context_hash"]:
                    resurfaced.append(n)
                    if update:
                        cur.execute("""UPDATE notices SET status='open', context_hash=?,
                                       changed_at=? WHERE content_hash=?""",
                                    (n["context_hash"], now(), ch))
                # else dismissed in same context -> stay silent
            elif status == "resolved":
                resurfaced.append(n)
                if update:
                    cur.execute("""UPDATE notices SET status='open', context_hash=?,
                                   message=?, changed_at=? WHERE content_hash=?""",
                                (n["context_hash"], n["message"], now(), ch))
            else:
                still_open.append(n)

    if update:
        for ch, row in rows.items():
            if ch not in seen_now and row[5] == "open":
                cur.execute("UPDATE notices SET status='resolved', changed_at=? WHERE content_hash=?",
                            (now(), ch))
        conn.commit()
    conn.close()
    return new, still_open, resurfaced

def dismiss_notice(root, content_hash):
    conn = _db(root)
    cur = conn.cursor()
    # allow a unique prefix match for convenience
    row = cur.execute("SELECT content_hash FROM notices WHERE content_hash=?",
                      (content_hash,)).fetchone()
    if not row:
        cands = cur.execute("SELECT content_hash FROM notices WHERE content_hash LIKE ?",
                            (content_hash + "%",)).fetchall()
        if len(cands) == 1:
            content_hash = cands[0][0]
        else:
            conn.close()
            return False
    cur.execute("UPDATE notices SET status='dismissed', changed_at=? WHERE content_hash=?",
                (now(), content_hash))
    conn.commit()
    conn.close()
    log_event(root, "dismiss", content_hash)
    return True

def ledger_summary(root):
    """Return (items_dict, events_count) for reconcile display."""
    if not os.path.isfile(_db_path(root)):
        return {}, _event_journal_count(root) or 0
    conn = _db(root)
    cur = conn.cursor()
    items = {}
    for r in cur.execute("""SELECT content_hash, kind, where_ref, status,
                            first_seen FROM notices"""):
        items[r[0]] = {"kind": r[1], "where": r[2], "status": r[3], "first_seen": r[4]}
    canonical_count = _event_journal_count(root)
    ev = canonical_count if canonical_count is not None else cur.execute("SELECT COUNT(*) FROM events").fetchone()[0]
    conn.close()
    return items, ev

def export_ledger_markdown(root):
    """Mirror the SQLite ledger to a human-readable Markdown file. The db stays
    the source of truth; this is for reading and inspection."""
    items, _ = ledger_summary(root)
    d = os.path.join(root, ".proposals")
    os.makedirs(d, exist_ok=True)
    path = os.path.join(d, "ledger-mirror.md")
    lines = [f"# Notice ledger mirror ({now()})", "",
             "Read-only mirror of .tyf/ledger.db. The database is the source of truth for notice status only; apparatus actions live in .tyf/events.jsonl.", ""]
    by_status = {}
    for h, r in items.items():
        by_status.setdefault(r["status"], []).append((h, r))
    for status in ("open", "resurfaced", "dismissed", "resolved"):
        group = by_status.get(status, [])
        if not group:
            continue
        lines.append(f"## {status} ({len(group)})")
        for h, r in group:
            lines.append(f"- ({r['kind']}) {r['where']}  [{h}]  first seen {r['first_seen']}")
        lines.append("")
    open(path, "w", encoding="utf-8").write("\n".join(lines))
    return path

def _save_notices(root, notices):
    """Append a dated digest to .proposals/notices.md. A record handed to the
    author, not an action. Nothing else in the work is written."""
    if not notices:
        return None
    d = os.path.join(root, ".proposals")
    os.makedirs(d, exist_ok=True)
    path = os.path.join(d, "notices.md")
    lines = [f"\n## Notices {now()}"]
    for n in notices:
        lines.append(f"- [ ] ({n['kind']}) {n['where']}: {n['message']}  <!-- {n['content_hash']} -->")
    with open(path, "a", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    return path

# ---------- commands ----------

def _required_structure(root):
    """The canonical TYF workspace layout. Returns (dirs, files) where files is
    a dict of relpath -> default content. Single source of truth for both init
    and doctor's repair check."""
    dirs = [
        "sources/uploads", "sources/transcripts", "sources/interviews", "sources/imports", "sources/notes",
        "sources/fragments",
        "knowledge-base/concepts", "knowledge-base/claims", "knowledge-base/examples", "knowledge-base/characters",
        "knowledge-base/contradictions", "knowledge-base/open-questions",
        "voice/registers", "voice/exemplar-passages", "voice/characters",
        "redactor-canon", "outline", "drafts", "manuscript", ".review",
        ".proposals", ".hooks", ".tyf",
    ]
    context_contract = """# TYF Workspace Instructions

This is an author-owned TYF workspace. This book folder is the single work.

- If the author says "start my book" or wants a first writing session, use `tyf start`; a title can stay unknown.
- If the author brings existing material, use `tyf start <path>` to preserve it and open the writing runway before drafting.
- Keep source, interview notes, and candidate prose in `sources/`, `knowledge-base/`, `voice/`, and `drafts/`.
- `tyf capture --kind source` and text imports mint source fragments in `sources/fragments/`; run `tyf structure work --source-ref <id>` before drafting when a fragment contains explicit claims, examples, or questions, then pass relevant ids to `tyf propose --source-ref <id>`.
- If the author asks what a named character would say, do, or notice, keep it as hidden amanuensis machinery: capture supplied character facts or cadence with `tyf character <name> --knowledge ... --voice ...`, then run `tyf consult-character work <name> --prompt "<question>"`. The contained packet may guide candidate dramatic insight; it is not manuscript text or a replacement for the author.
- Do not write manuscript prose directly. Manuscript writes must go through proposal, audit, author review packet, author decision, and `tyf write --decision <id>`.
- Missing knowledge stays visible as `[AUTHOR: needed - what]`.
- If the author edits `manuscript/` directly, use `tyf adopt work <unit> --evidence "<what happened>"` before the next controlled write.
- Use `tyf resume` to recover the active work, pending proposals, open prompts, and next move.
- Use `tyf notice --peek` for read-only inspection and `tyf snapshot --message "..."` only when the author wants an explicit git recovery point.
"""
    files = {
        "WORKSPACE_STATE.yaml":
            f"active_work: {ROOT_WORK_ID}\nactive_band: section\nwrite_control:\n  compose: locked\n  revise: locked\nstatus: intake\n",
        "tyf.portable.json":
            json.dumps({
                "format": "tyf-workspace",
                "format_version": "0.5.0",
                "single_work": True,
                "canonical_text_state": [
                    "WORKSPACE_STATE.yaml",
                    "work.yaml",
                    "manifest.yaml",
                    "ASSUMPTIONS.md",
                    "style-sheet.md",
                    "outline/",
                    "drafts/",
                    "manuscript/",
                    ".review/",
                    "sources/",
                    "knowledge-base/",
                    "voice/",
                    "redactor-canon/",
                    ".tyf/events.jsonl",
                ],
                "derived_disposable_state": [
                    ".tyf/ledger.db",
                    ".tyf/*.db-journal",
                    ".tyf/*.db-wal",
                    ".tyf/*.db-shm",
                ],
                "git": "optional",
            }, indent=2, sort_keys=True) + "\n",
        "manifest.yaml":
            "voice_inheritance:\n  default: layer\nhooks:\n  - on: save_chapter\n    run: [ai-tell-scan, register-fence-check]\n  - on: open_chapter\n    run: [load-registers, load-style-sheet, load-chapter-review]\n  - on: mark_ready\n    run: [audit-ready-unit]\nself_extension:\n  anti_pattern_growth: true\n  writes_to: .proposals/\n",
        "ASSUMPTIONS.md": "# Assumptions\n\nUpdated as the author corrects them.\n\n- (none yet)\n",
        "AGENTS.md": context_contract,
        "CLAUDE.md": context_contract,
        "GEMINI.md": context_contract,
        "work.yaml":
            f"id: {ROOT_WORK_ID}\ntype: \"book\"\ntitle_status: \"unknown\"\nlanguage: \"undetermined\"\nregisters:\n  - \"(elicit at least one register before composing)\"\nstatus: structuring\nscope:\n  knowledge: full\n  sources: full\noverrides:\n  voice: []\n",
        "style-sheet.md":
            f"# Running style sheet: {ROOT_WORK_ID}\n\nWriting language: undetermined\n\nThe Redactor's instrument. Every pass appends decisions here and reads before proposing. Finish decisions are language-specific; do not apply English typography rules unless this work is in English.\n\n## Terminology decisions\n## Apparatus decisions\n## Finish decisions\n",
        ".review/write-log.md": f"# Write log: {ROOT_WORK_ID}\n\nThe only record of writes into manuscript/.\n",
        "sources/links.md": "# Links\n",
        "knowledge-base/claims.md":
            "# Claims index\n\n| Claim id | Statement | Support | Source | Status |\n|---|---|---|---|---|\n",
        "voice/register-fences.md": "# Register fences\n",
        "voice/anti-patterns.md":
            "# Anti-patterns (shared)\n\n- No em-dashes in prose.\n- No stacked-negation triads.\n- No \"Not X. Y.\" fragment structures.\n- No generic AI-writing language.\n",
        "redactor-canon/terminology.md": "# Terminology\n\n| Canonical | Forbidden variants | Note |\n|---|---|---|\n",
        "redactor-canon/logic.md": "# Logic rules\n\n- Every load-bearing claim resolves; no contradiction; assumptions stated.\n",
        "redactor-canon/apparatus.md": "# Apparatus\n\n- Citation style:\n- Cross-reference format:\n- Notes convention:\n",
        "redactor-canon/finish.md": "# Typographic finish\n\n- Em-dash discipline: none in prose; colon, semicolon, or comma.\n",
        ".tyf/.gitignore": "# Apparatus memory: regenerable derived state.\nledger.db\n*.db-journal\n*.db-wal\n*.db-shm\n",
    }
    return dirs, files

def _scaffold(root, create=True):
    """Check (and optionally create) the required structure idempotently.
    Returns (created, present): lists of relpaths. Never overwrites a file that
    already exists, so an existing workspace is healed, not clobbered."""
    dirs, files = _required_structure(root)
    created, present = [], []
    for d in dirs:
        full = os.path.join(root, d)
        if os.path.islink(full):
            created.append(d + "/")
            continue
        if os.path.isdir(full):
            present.append(d + "/")
        else:
            if create:
                os.makedirs(full, exist_ok=True)
            created.append(d + "/")
    for rel, content in files.items():
        full = os.path.join(root, rel)
        if os.path.isfile(full):
            present.append(rel)
        else:
            if create:
                os.makedirs(os.path.dirname(full) or ".", exist_ok=True)
                with open(full, "w", encoding="utf-8") as f:
                    f.write(content)
            created.append(rel)
    if create:
        _db(root)  # initialize the SQLite notice index and event mirror if absent
    return created, present

def cmd_init(args):
    root = os.path.abspath(args.name or ".")
    existed = os.path.isfile(os.path.join(root, "WORKSPACE_STATE.yaml"))
    if not existed and os.path.isdir(root) and os.listdir(root) and not getattr(args, "force", False):
        sys.exit(f"Refused: {root} is a non-empty directory and not a TYF workspace. "
                 "Re-run with --force to scaffold a workspace here anyway.")
    created, present = _scaffold(root, create=True)
    log_event(root, "init", root, f"created {len(created)}, present {len(present)}")
    if existed:
        print(f"Workspace already present at {root}; healed missing structure.")
    else:
        print(f"Founded workspace at {root}")
    if created:
        print(f"  created {len(created)} item(s): " + ", ".join(created[:8]) +
              (" ..." if len(created) > 8 else ""))
    else:
        print("  structure already complete; nothing to create")
    if not existed:
        print("Next: run `tyf start` to open the writing runway in this book folder.")

def cmd_new_work(args):
    _require_workspace()
    args.id = _safe_work_id(args.id)
    _confine_work(args.id)
    base, _reg = _create_work(args.id, args.type, args.register,
                              language=args.language, activate_if_none=True)
    log_event(".", "new-work", args.id, f"type={args.type} language={_one_line(args.language, 'undetermined')}")
    print(f"Created work: {base} (type={args.type}, language={_one_line(args.language, 'undetermined')})")


def _update_work_metadata(work_id, work_type=None, title=None, language=None):
    work_path = _work_path(work_id, "work.yaml")
    if not os.path.isfile(work_path):
        return
    title = _one_line(title)
    language = _one_line(language)
    work_type = _one_line(work_type)
    if not (title or language or work_type):
        return
    current = read_state(work_path)
    raw = open(work_path, encoding="utf-8").read().splitlines()
    out = []
    saw_title = saw_title_status = saw_language = saw_type = False
    for ln in raw:
        if ln.startswith("title:"):
            out.append(f"title: {_yaml_scalar(title)}" if title else ln)
            saw_title = True
        elif ln.startswith("title_status:"):
            status = "working" if title else get(current, "title_status", default="unknown")
            out.append(f"title_status: {_yaml_scalar(status)}")
            saw_title_status = True
        elif ln.startswith("language:"):
            out.append(f"language: {_yaml_scalar(language or get(current, 'language', default='undetermined'))}")
            saw_language = True
        elif ln.startswith("type:"):
            out.append(f"type: {_yaml_scalar(work_type)}" if work_type else ln)
            saw_type = True
        else:
            out.append(ln)
    insert_at = 2 if len(out) >= 2 else len(out)
    if work_type and not saw_type:
        out.insert(1 if out else 0, f"type: {_yaml_scalar(work_type)}")
        insert_at += 1
    if title and not saw_title:
        out.insert(insert_at, f"title: {_yaml_scalar(title)}")
        insert_at += 1
    if not saw_title_status:
        out.insert(insert_at, f"title_status: {_yaml_scalar('working' if title else 'unknown')}")
        insert_at += 1
    if not saw_language:
        out.insert(insert_at, f"language: {_yaml_scalar(language or 'undetermined')}")
    atomic_write(work_path, "\n".join(out) + "\n")

    if language:
        style_path = _work_path(work_id, "style-sheet.md")
        if os.path.isfile(style_path):
            lines = open(style_path, encoding="utf-8").read().splitlines()
            refreshed = []
            changed = False
            for ln in lines:
                if ln.startswith("Writing language:"):
                    refreshed.append(f"Writing language: {language}")
                    changed = True
                else:
                    refreshed.append(ln)
            if not changed:
                refreshed.insert(2 if len(refreshed) >= 2 else len(refreshed),
                                 f"Writing language: {language}")
                changed = True
            if changed:
                atomic_write(style_path, "\n".join(refreshed) + "\n")


def _create_work(work_id, work_type="book", register=None, title=None,
                 language=None, activate_if_none=False, activate=False):
    if work_id == ROOT_WORK_ID and os.path.isfile("work.yaml"):
        for d in ("outline", "drafts", "manuscript", ".review"):
            _ensure_real_dir(d, d + "/")
        if not os.path.isfile(os.path.join(".review", "write-log.md")):
            write(os.path.join(".review", "write-log.md"),
                  f"# Write log: {work_id}\n\nThe only record of writes into manuscript/.\n")
        work_type = _one_line(work_type, "book")
        language = _one_line(language, None)
        title = _one_line(title)
        if title or language:
            _update_work_metadata(work_id, work_type=work_type, title=title, language=language)
        if activate or activate_if_none:
            _set_active(work_id)
        return ".", _one_line(register, "(elicit at least one register before composing)")

    base = os.path.join("works", work_id)
    if os.path.exists(base):
        sys.exit(f"work already exists: {base}")
    _ensure_real_dir("works", "works/")
    _reject_symlink_components("works", "works/")
    _ensure_real_dir(os.path.join(base, "outline"), "outline/")
    _ensure_real_dir(os.path.join(base, "drafts"), "drafts/")
    _ensure_real_dir(os.path.join(base, "manuscript"), "manuscript/")
    _ensure_real_dir(os.path.join(base, ".review"), ".review/")
    reg = _one_line(register, "(elicit at least one register before composing)")
    work_type = _one_line(work_type, "book")
    title = _one_line(title)
    language = _one_line(language, "undetermined")
    title_status = "working" if title else "unknown"
    title_line = f"title: {_yaml_scalar(title)}\n" if title else ""
    write(os.path.join(base, "work.yaml"),
          f"id: {work_id}\ntype: {_yaml_scalar(work_type)}\n{title_line}title_status: {_yaml_scalar(title_status)}\nlanguage: {_yaml_scalar(language)}\nregisters:\n  - {_yaml_scalar(reg)}\nstatus: structuring\nscope:\n  knowledge: full\n  sources: full\noverrides:\n  voice: []\n")
    write(os.path.join(base, "style-sheet.md"),
          f"# Running style sheet: {work_id}\n\nWriting language: {language}\n\nThe Redactor's instrument. Every pass appends decisions here and reads before proposing. Finish decisions are language-specific; do not apply English typography rules unless this work is in English.\n\n## Terminology decisions\n## Apparatus decisions\n## Finish decisions\n")
    write(os.path.join(base, ".review", "write-log.md"), f"# Write log: {work_id}\n\nThe only record of writes into manuscript/.\n")
    st = read_state("WORKSPACE_STATE.yaml")
    if activate or (activate_if_none and not get(st, "active_work")):
        _set_active(work_id)
    return base, reg

def _slugify_title(title):
    ascii_title = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_title.lower()).strip("-")
    slug = re.sub(r"-+", "-", slug)
    if not slug:
        return "work-" + hashlib.sha256(title.encode("utf-8")).hexdigest()[:12]
    return slug[:64].strip("-")

def _untitled_work_id():
    base = "untitled-" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    candidate = base
    i = 2
    while os.path.exists(os.path.join("works", candidate)):
        candidate = f"{base}-{i}"
        i += 1
    return candidate

def _first_session_packet_text(label, language, heading):
    return f"""# {heading}: {label}

This is an author-owned first-session packet. It is source/interview evidence, not candidate prose. Fill it with source, images, fragments, objections, questions, and pressure. TYF may ask, organize, and propose, but it must not invent book content here. Do not invent what the author has not supplied.

Writing language: {language}

## Gentle attention deck

These are invitations, not a test of certainty. Answer only what helps us begin one candidate passage; leave the rest blank.

- [PROMPT: what should TYF hold with most care in this book right now?]
- [PROMPT: what lived pressure, question, image, or contradiction makes the work necessary?]
- [PROMPT: what must not be flattened, explained away, or made too neat?]
- [PROMPT: whose words, memory, scene, or source should stay close to the page?]
- [PROMPT: which register should the first passage try: plain, lyrical, argumentative, intimate, comic, severe, or another?]
- [PROMPT: one first passage could begin from which scene, claim, question, or phrase?]

## What is already true

- [PROMPT: name the lived pressure, question, or image that makes this book necessary]

## Source fragments

- [PROMPT: paste notes, memories, observations, phrases, or cited material]

## Voice samples

- [PROMPT: lines that sound like the book, even if they are rough]

## Open questions

- [PROMPT: what must be elicited before drafting]

## Candidate draft target

- No manuscript text here yet. Candidate prose may be drafted later in `drafts/` only after source, register, and structure are present.
"""


def _write_begin_packet(work_id, title=None, language=None):
    label = _one_line(title, work_id)
    language = _one_line(language, "undetermined")
    base = _work_base(work_id)
    _ensure_real_dir(os.path.join("sources", "interviews"), "sources/interviews/")
    starter = os.path.join("sources", "interviews", f"{work_id}-first-session.md")
    seed = os.path.join(base, "outline", "seed.md")
    runway = os.path.join(base, ".review", "first-session.md")
    if os.path.exists(starter):
        sys.exit(f"Refused: first-session packet already exists: {starter}")
    write(starter, _first_session_packet_text(label, language, "Start here"))
    write(seed, f"""# Seed outline: {label}

## Working promise

- [PROMPT: what this book is trying to make thinkable or feelable]

## Central pressure

- [PROMPT: the tension, contradiction, wound, demand, or question]

## Source inventory

- [PROMPT: sources already available]
- [PROMPT: sources still missing]

## Possible first unit

- [PROMPT: scene, argument, vignette, letter, chapter, or fragment]
""")
    write(runway, f"""# First-session runway: {label}

Active work: `{work_id}`

## First-session loop

1. Fill `{starter.replace(os.sep, "/")}` with the author's material.
2. Capture short source, voice, claim, or question notes with `tyf capture`.
3. Use `interviewing-the-author` to elicit what is still tacit.
4. Use `structuring-knowledge` to turn captured material into claims, gaps, and possible shape.
5. Draft candidates only in `{_work_display_path(work_id, "drafts")}/`.
6. Run `tyf audit {work_id} <unit>` before treating a unit as ready.
7. Move text into `manuscript/` only after `tyf propose`, `tyf audit --record`, `tyf review`, `tyf accept`, and `tyf write --decision`.

## Guardrails

- Beginning is source elicitation, not book generation.
- No silence counts as consent.
- Honor the work's writing language before applying prose conventions.
- Missing knowledge gets an `[AUTHOR: needed - what]` marker.
- The manuscript stays empty until an explicit controlled write.
""")
    return starter, seed, runway


def _ensure_first_session_packet(work_id, title=None, language=None):
    wy = read_state(_work_path(work_id, "work.yaml"))
    label = _one_line(title, get(wy, "title") or work_id)
    language = _one_line(language, get(wy, "language") or "undetermined")
    base = _work_base(work_id)
    _ensure_real_dir(os.path.join("sources", "interviews"), "sources/interviews/")
    _ensure_real_dir(os.path.join(base, "outline"), "outline/")
    starter = os.path.join("sources", "interviews", f"{work_id}-first-session.md")
    seed = os.path.join(base, "outline", "seed.md")
    if not os.path.exists(starter):
        write(starter, _first_session_packet_text(label, language, "First-session evidence"))
    else:
        lines = open(starter, encoding="utf-8").read().splitlines()
        refreshed = []
        changed = False
        saw_language = False
        for ln in lines:
            if ln.startswith("Writing language:"):
                saw_language = True
                replacement = f"Writing language: {language}"
                refreshed.append(replacement)
                changed = changed or ln != replacement
            else:
                refreshed.append(ln)
        if not saw_language:
            refreshed.insert(2 if len(refreshed) >= 2 else len(refreshed),
                             f"Writing language: {language}")
            changed = True
        if changed:
            atomic_write(starter, "\n".join(refreshed) + "\n")
    if not os.path.exists(seed):
        write(seed, f"""# Seed outline: {label}

## Working promise

- [PROMPT: what this book is trying to make thinkable or feelable]

## Central pressure

- [PROMPT: the tension, contradiction, wound, demand, or question]

## Source inventory

- [PROMPT: sources already available]
- [PROMPT: sources still missing]

## Possible first unit

- [PROMPT: scene, argument, vignette, letter, chapter, or fragment]
""")
    return starter, seed


def cmd_begin(args):
    _require_workspace()
    work_id = _safe_work_id(args.id)
    _confine_work(work_id)
    base, _reg = _create_work(work_id, args.type, args.register,
                              language=args.language,
                              title=args.title, activate=True)
    starter, seed, runway = _write_begin_packet(work_id, args.title, args.language)
    log_event(".", "begin", work_id, f"starter={starter} language={_one_line(args.language, 'undetermined')}")
    print(f"Begin: active work {work_id} at {base}")
    print(f"  first-session packet: {starter}")
    print(f"  seed outline         : {seed}")
    print(f"  review runway        : {runway}")
    print("Next: fill the packet, use `tyf capture` for short source notes,")
    print("then draft candidates in drafts/ only. Manuscript writes require proposal, audit, review, decision, and `tyf write --decision`.")

def cmd_start(args):
    _require_workspace()
    arrival = None
    if getattr(args, "path", None):
        arrival = _import_arrival(args, announce=False)
        work_id = arrival["work_id"]
    else:
        work_id, _created, _unused = _work_for_start(args)
    runway, draft, preserved_existing = _write_start_runway(work_id, arrival)
    log_event(".", "start", work_id, f"runway={runway} draft={draft}")
    print("Writing runway opened.")
    print("  Work: this book folder")
    if preserved_existing:
        print("  Existing writing runway preserved; use `tyf resume` to return without losing session notes.")
    if arrival:
        print(f"  Preserved arrival: {arrival['preserved']}")
        print(f"  Arrival orientation: {arrival['orientation']}")
    print(f"  Runway: {runway}")
    print(f"  Draft runway: {draft}")
    print("No manuscript text was written.")
    print(f"Next: write in {draft.replace(os.sep, '/')}; keep uncertainty visible, and let the Gate come later.")

_CAPTURE_TARGETS = {
    "source": ("sources", "notes"),
    "voice": ("voice", "exemplar-passages"),
    "claim": ("knowledge-base", "claims"),
    "question": ("knowledge-base", "open-questions"),
}

def _capture_path(work_id, kind):
    return os.path.join(*_CAPTURE_TARGETS[kind], f"{work_id}.md")

def _source_text_hash(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _source_fragment_id(text):
    stamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
    return f"src-{stamp}-{_source_text_hash(text)[:8]}"


def _source_fragment_text_from_file(path):
    body = _read(path)
    marker = "\n## Text\n\n"
    if marker not in body:
        return None
    text = body.split(marker, 1)[1]
    if text.endswith("\n"):
        text = text[:-1]
    return text


def _source_fragment_integrity_problem(ref, work=None):
    if not isinstance(ref, dict):
        return "invalid source fragment reference"
    frag_id = ref.get("id")
    if not frag_id or not re.fullmatch(r"src-[A-Za-z0-9._-]+", frag_id):
        return f"invalid source fragment id: {frag_id!r}"
    rel = ref.get("path") or f"sources/fragments/{frag_id}.md"
    if os.path.isabs(rel):
        return f"source fragment {frag_id} uses an absolute path"
    try:
        _reject_symlink_components(rel, "source fragment")
    except SystemExit as e:
        return str(e)
    root = os.path.realpath(".")
    real = os.path.realpath(rel)
    if not _within(root, real):
        return f"source fragment {frag_id} resolves outside the workspace"
    if not os.path.isfile(real):
        return f"missing source fragment {frag_id}: {rel}"
    text = _source_fragment_text_from_file(real)
    if text is None:
        return f"source fragment {frag_id} has no text section"
    actual = _source_text_hash(text)
    suffix = frag_id.rsplit("-", 1)[-1]
    if re.fullmatch(r"[0-9a-f]{8}", suffix) and actual[:8] != suffix:
        return f"source fragment {frag_id} id hash mismatch; provenance may be tampered"
    expected = ref.get("text_sha256")
    if expected and actual != expected:
        return f"source fragment {frag_id} hash mismatch; provenance may be tampered"
    return None


def _load_source_fragment_index():
    path = os.path.join("sources", "fragments.jsonl")
    entries, problems = {}, []
    if not os.path.exists(path):
        return entries, problems
    try:
        with open(path, encoding="utf-8") as f:
            for i, raw in enumerate(f, 1):
                if not raw.strip():
                    continue
                try:
                    entry = json.loads(raw)
                except json.JSONDecodeError as e:
                    problems.append(f"invalid source fragment index line {i}: {e}")
                    continue
                frag_id = entry.get("id")
                if frag_id:
                    entries[frag_id] = entry
    except OSError as e:
        problems.append(f"could not read source fragment index: {e}")
    return entries, problems


def _mint_source_fragment(work_id, kind, title, text):
    if kind not in {"source", "chat", "import", "dump", "transcript", "note"}:
        return None
    _ensure_real_dir(os.path.join("sources", "fragments"), "source fragments/")
    frag_id = _source_fragment_id(text)
    rel = os.path.join("sources", "fragments", f"{frag_id}.md")
    digest = _source_text_hash(text)
    title = _one_line(title, kind)
    captured_at = now()
    content = (
        f"# Source fragment: {frag_id}\n\n"
        f"Origin work: `{work_id}`\n"
        f"Kind: `{kind}`\n"
        f"Title: {title}\n"
        f"Captured: {captured_at}\n"
        f"Text sha256: `{digest}`\n\n"
        "## Text\n\n"
        f"{text}\n"
    )
    atomic_write(rel, content)
    entry = {
        "id": frag_id,
        "origin_work": work_id,
        "work": work_id,
        "kind": kind,
        "title": title,
        "path": rel.replace(os.sep, "/"),
        "text_sha256": digest,
        "captured_at": captured_at,
    }
    index = os.path.join("sources", "fragments.jsonl")
    append(index, json.dumps(entry, sort_keys=True, ensure_ascii=False) + "\n")
    return entry


def _normalize_source_ref_ids(values):
    ids = []
    for raw in values or []:
        for part in str(raw).split(","):
            part = part.strip()
            if part:
                ids.append(part)
    return ids


def _resolve_source_refs(work, values):
    refs = []
    ids = _normalize_source_ref_ids(values)
    if not ids:
        return refs
    index, problems = _load_source_fragment_index()
    if problems:
        sys.exit("Refused: source fragment provenance index is invalid: " + problems[0])
    seen = set()
    for frag_id in ids:
        if frag_id in seen:
            sys.exit(f"Refused: duplicate source fragment reference: {frag_id}")
        seen.add(frag_id)
        if not re.fullmatch(r"src-[A-Za-z0-9._-]+", frag_id):
            sys.exit(f"Refused: unsafe source fragment id {frag_id!r}.")
        entry = index.get(frag_id)
        if entry is None:
            sys.exit(f"Refused: missing source fragment provenance: {frag_id}")
        problem = _source_fragment_integrity_problem(entry, work=work)
        if problem:
            sys.exit("Refused: " + problem)
        refs.append({
            "id": entry["id"],
            "origin_work": entry.get("origin_work") or entry.get("work", work),
            "used_by_work": work,
            "work": entry.get("origin_work") or entry.get("work", work),
            "path": entry["path"],
            "text_sha256": entry["text_sha256"],
            "title": entry.get("title", ""),
        })
    return refs


def _source_ref_problems(work, refs):
    problems = []
    for ref in refs or []:
        problem = _source_fragment_integrity_problem(ref, work=work)
        if problem:
            problems.append(f"{work}: {problem}")
    return problems


def _require_source_ref_integrity(work, refs):
    problems = _source_ref_problems(work, refs)
    if problems:
        sys.exit("Refused: " + problems[0])


def _knowledge_id(prefix, source_id, text):
    payload = f"{source_id}\0{text.strip()}".encode("utf-8")
    return f"{prefix}-{hashlib.sha256(payload).hexdigest()[:12]}"


def _knowledge_escape(value):
    return _one_line(value).replace("|", "\\|")


def _strip_list_marker(line):
    line = line.strip()
    line = re.sub(r"^[-*+]\s+", "", line)
    line = re.sub(r"^\d+[.)]\s+", "", line)
    return line.strip()


def _extract_structured_knowledge(text):
    claims, examples, questions, unclassified = [], [], [], []
    claim_labels = r"(claim|thesis|argument|assertion)"
    example_labels = r"(example|scene|memory|anecdote|image)"
    question_labels = r"(question|open question|gap)"
    for raw in text.splitlines():
        line = _strip_list_marker(raw)
        if not line or line.startswith("#"):
            continue
        m = re.match(rf"^{claim_labels}\s*:\s*(.+)$", line, re.I)
        if m:
            claims.append(m.group(2).strip())
            continue
        m = re.match(rf"^{example_labels}\s*:\s*(.+)$", line, re.I)
        if m:
            examples.append(m.group(2).strip())
            continue
        m = re.match(rf"^{question_labels}\s*:\s*(.+)$", line, re.I)
        if m:
            questions.append(m.group(2).strip().rstrip("?") + "?")
            continue
        if "[AUTHOR:" in line or line.endswith("?"):
            questions.append(line.rstrip("?") + "?")
            continue
        unclassified.append(line)
    return {
        "claims": [c for c in claims if c],
        "examples": [e for e in examples if e],
        "questions": [q for q in questions if q],
        "unclassified": unclassified,
    }


def _append_unique_block(path, marker, block, header):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if os.path.exists(path):
        body = _read(path)
    else:
        body = header.rstrip() + "\n\n"
    if marker in body:
        return False
    atomic_write(path, body.rstrip() + "\n\n" + block.rstrip() + "\n")
    return True


def _append_claim_row(claim_id, statement, source_id):
    path = os.path.join("knowledge-base", "claims.md")
    if not os.path.isfile(path):
        write(path, "# Claims index\n\n| Claim id | Statement | Support | Source | Status |\n|---|---|---|---|---|\n")
    body = _read(path)
    if claim_id in body:
        return False
    row = (
        f"| {claim_id} | {_knowledge_escape(statement)} | source fragment | "
        f"`{source_id}` | source-backed |\n"
    )
    atomic_write(path, body.rstrip() + "\n" + row)
    return True


def _write_amanuensis_brief(work, refs, extracted):
    _ensure_real_dir(_work_path(work, ".review"), ".review/")
    path = _work_path(work, ".review", "amanuensis-brief.md")
    ref_lines = "\n".join(
        f"- `{ref['id']}` ({ref.get('path', '')})"
        for ref in refs
    ) or "- (none)"
    claim_lines = "\n".join(
        f"- `{item['id']}` {item['text']} (source `{item['source_id']}`)"
        for item in extracted["claims"]
    ) or "- (none)"
    example_lines = "\n".join(
        f"- `{item['id']}` {item['text']} (source `{item['source_id']}`)"
        for item in extracted["examples"]
    ) or "- (none)"
    question_lines = "\n".join(
        f"- `{item['id']}` {item['text']} (source `{item['source_id']}`)"
        for item in extracted["questions"]
    ) or "- (none)"
    unclassified_lines = "\n".join(
        f"- {item['text']} (source `{item['source_id']}`)"
        for item in extracted["unclassified"][:40]
    ) or "- (none)"
    atomic_write(path, f"""# Amanuensis brief

Work: `{work}`

This brief is source-to-knowledge context for candidate drafting. It is not
manuscript text and it is not author acceptance.

Questions here are gentle attention for the author. These are nudges of attention, not doubts in the author's judgment. Adversarial pressure belongs to the audit, not the amanuensis.

## Source fragments

{ref_lines}

## Counts

- Claims extracted: {len(extracted['claims'])}
- Examples extracted: {len(extracted['examples'])}
- Gentle questions surfaced: {len(extracted['questions'])}
- Unclassified lines preserved: {len(extracted['unclassified'])}

## Claims

{claim_lines}

## Examples

{example_lines}

## Gentle questions for the author

{question_lines}

## Unclassified source material

{unclassified_lines}
""")
    return path


def cmd_structure(args):
    _require_workspace()
    work_id = _safe_work_id(args.work)
    _confine_work(work_id)
    _require_work(work_id)
    refs = _resolve_source_refs(work_id, args.source_ref)
    if not refs:
        sys.exit("Refused: structure needs at least one --source-ref.")
    extracted = {"claims": [], "examples": [], "questions": [], "unclassified": []}
    for ref in refs:
        text = _source_fragment_text_from_file(ref["path"])
        if text is None:
            sys.exit(f"Refused: source fragment {ref['id']} has no text section")
        parsed = _extract_structured_knowledge(text)
        for claim in parsed["claims"]:
            claim_id = _knowledge_id("clm", ref["id"], claim)
            _append_claim_row(claim_id, claim, ref["id"])
            extracted["claims"].append({"id": claim_id, "text": claim, "source_id": ref["id"]})
        for example in parsed["examples"]:
            example_id = _knowledge_id("exm", ref["id"], example)
            path = os.path.join("knowledge-base", "examples", f"{work_id}.md")
            block = f"## {example_id}\n\nSource: `{ref['id']}`\n\n{example}\n"
            _append_unique_block(path, example_id, block, f"# Examples: {work_id}")
            extracted["examples"].append({"id": example_id, "text": example, "source_id": ref["id"]})
        for question in parsed["questions"]:
            question_id = _knowledge_id("qst", ref["id"], question)
            path = os.path.join("knowledge-base", "open-questions", f"{work_id}.md")
            block = f"## {question_id}\n\nSource: `{ref['id']}`\n\n{question}\n"
            _append_unique_block(path, question_id, block, f"# Open questions: {work_id}")
            extracted["questions"].append({"id": question_id, "text": question, "source_id": ref["id"]})
        for line in parsed["unclassified"]:
            extracted["unclassified"].append({"text": line, "source_id": ref["id"]})
    brief = _write_amanuensis_brief(work_id, refs, extracted)
    log_event(".", "structure", work_id, f"refs={','.join(ref['id'] for ref in refs)} brief={brief}")
    print(f"Structured source for {work_id}.")
    print(f"  Claims: {len(extracted['claims'])}")
    print(f"  Examples: {len(extracted['examples'])}")
    print(f"  Open questions: {len(extracted['questions'])}")
    print(f"  Unclassified: {len(extracted['unclassified'])}")
    print(f"  Amanuensis brief: {brief.replace(os.sep, '/')}")
    print("No manuscript text was written.")


def _character_slug(name):
    clean = _one_line(name)
    normalized = unicodedata.normalize("NFKC", clean).casefold()
    slug = re.sub(r"[^\w]+", "-", normalized, flags=re.UNICODE).strip("-_")
    slug = slug[:64].strip("-_. ")
    digest = hashlib.sha256(clean.encode("utf-8")).hexdigest()[:8]
    if not slug:
        slug = f"character-{digest}"
    reserved = {"CON", "PRN", "AUX", "NUL", *(f"COM{i}" for i in range(1, 10)), *(f"LPT{i}" for i in range(1, 10))}
    if slug.upper() in reserved:
        slug = f"{slug}-{digest}"
    return slug


def _character_paths(name):
    slug = _character_slug(name)
    return (
        slug,
        os.path.join("knowledge-base", "characters", f"{slug}.md"),
        os.path.join("voice", "characters", f"{slug}.md"),
    )


def cmd_character(args):
    _require_workspace()
    name = _one_line(args.name)
    knowledge = (args.knowledge or "").strip()
    voice = (args.voice or "").strip()
    if not knowledge and not voice:
        sys.exit("Refused: character dossier needs --knowledge, --voice, or both.")
    slug, knowledge_path, voice_path = _character_paths(name)
    _ensure_real_dir(os.path.dirname(knowledge_path), "knowledge-base/characters/")
    _ensure_real_dir(os.path.dirname(voice_path), "voice/characters/")
    if knowledge and not os.path.isfile(knowledge_path):
        write(knowledge_path, f"# Character knowledge: {name}\n\n")
    if voice and not os.path.isfile(voice_path):
        write(voice_path, f"# Character voice: {name}\n\n")
    if knowledge:
        append(knowledge_path, f"## {now()}\n\n{knowledge}\n\n")
    if voice:
        append(voice_path, f"## {now()}\n\n{voice}\n\n")
    log_event(".", "character", slug, f"knowledge={bool(knowledge)} voice={bool(voice)}")
    print(f"Character dossier updated: {name}")
    if knowledge:
        print(f"  Knowledge: {knowledge_path.replace(os.sep, '/')}")
    if voice:
        print(f"  Voice: {voice_path.replace(os.sep, '/')}")
    print("No manuscript text was written.")


def cmd_consult_character(args):
    _require_workspace()
    work_id = _safe_work_id(args.work)
    _confine_work(work_id)
    _require_work(work_id)
    name = _one_line(args.name)
    prompt = (args.prompt or "").strip()
    if not prompt:
        sys.exit("Refused: character consultation needs --prompt.")
    slug, knowledge_path, voice_path = _character_paths(name)
    if not os.path.isfile(knowledge_path) and not os.path.isfile(voice_path):
        sys.exit(f"Refused: missing character dossier for {name!r}. Use `tyf character {name} --knowledge ... --voice ...` first.")
    knowledge = _read(knowledge_path) if os.path.isfile(knowledge_path) else "(no knowledge dossier yet)"
    voice = _read(voice_path) if os.path.isfile(voice_path) else "(no voice dossier yet)"
    consult_dir = _work_path(work_id, ".review", "character-consults")
    _ensure_real_dir(consult_dir, ".review/character-consults/")
    digest = hashlib.sha256(f"{slug}\0{prompt}\0{now()}".encode("utf-8")).hexdigest()[:10]
    path = os.path.join(consult_dir, f"{slug}-{digest}.md")
    write(path, f"""# Character consultation: {name}

Work: `{work_id}`
Prompt: {prompt}

This packet is hidden amanuensis machinery. It supports candidate dramatic
insight only. It is not evidence, not manuscript, not a source, and not a
replacement for the author.

## Containment

- Ground only in this character dossier: the knowledge and voice notes copied below.
- Do not import another character's knowledge or voice.
- Mark missing material as `[AUTHOR: needed - what]`.
- Return a candidate dramatic insight, not an assertion of truth.
- The answer may be playful or voiced, but it stays quarantined until the author uses it.

## Sub-agent containment contract

- If the host supports sub-agents, the amanuensis may hand only this packet to one bounded character worker.
- The author is not asked to manage sub-agents or name this machinery.
- The worker may read the prompt, this character knowledge dossier, and this character voice dossier.
- The worker may not read other character dossiers, source files, manuscript files, or workspace state.
- A little roleplay is allowed only as candidate lines grounded in this dossier.
- Return to the amanuensis, not to manuscript.
- The amanuensis may then answer the author in ordinary chat or draft candidate text in `drafts/`.

## Character knowledge dossier

{knowledge.strip()}

## Character voice dossier

{voice.strip()}

## Candidate response workspace

[Agent may answer the author in chat from this containment packet. Do not write
to manuscript. If prose is drafted, put it in `drafts/` as candidate text.]
""")
    log_event(".", "consult-character", f"{work_id}/{slug}", path)
    print(f"Character consultation: {name}")
    print(f"  Packet: {path.replace(os.sep, '/')}")
    print("No manuscript text was written.")

def cmd_capture(args):
    _require_workspace()
    work_id = _safe_work_id(args.work)
    _confine_work(work_id)
    _require_work(work_id)
    text = (args.text or "").strip()
    if not text:
        sys.exit("Refused: capture needs --text with the author's material.")
    path = _capture_path(work_id, args.kind)
    if not os.path.isfile(path):
        write(path, f"# {args.kind.title()} captures: {work_id}\n\n")
    title = _one_line(args.title, args.kind)
    fragment = _mint_source_fragment(work_id, args.kind, title, text)
    append(path, f"## {now()} - {title}\n\nWork: `{work_id}`\nKind: `{args.kind}`\n\n{text}\n\n")
    if fragment:
        append(path, f"Source fragment: `{fragment['id']}` ({fragment['path']})\n\n")
    log_event(".", "capture", f"{work_id}/{args.kind}", path)
    print(f"Captured {args.kind} for {work_id}: {path}")
    if fragment:
        print(f"Source fragment: {fragment['id']}")
    print("Next: preserve source, structure knowledge, and keep candidates in drafts/.")

def _safe_import_label(name):
    label = re.sub(r"[^A-Za-z0-9._-]+", "-", name).strip("-._")
    return label[:80] or "arrival"


def _active_work_id():
    active = _one_line(get(read_state("WORKSPACE_STATE.yaml"), "active_work"))
    if active and os.path.isfile(_work_path(active, "work.yaml")):
        return active
    if os.path.isfile("work.yaml"):
        return ROOT_WORK_ID
    return ""


def _work_for_arrival(args):
    title = _one_line(getattr(args, "title", None))
    language = getattr(args, "language", None)
    if getattr(args, "work", None):
        work_id = _safe_work_id(args.work)
        _confine_work(work_id)
        _require_work(work_id)
        _update_work_metadata(work_id, title=title, language=language)
        return work_id, False
    active = _active_work_id()
    if active:
        _update_work_metadata(active, title=title, language=language)
        return active, False
    work_id = ROOT_WORK_ID if os.path.isfile("work.yaml") else _safe_work_id(_slugify_title(title) if title else _untitled_work_id())
    _confine_work(work_id)
    _create_work(work_id, "book", title=title, language=language, activate=True)
    _write_begin_packet(work_id, title, language)
    return work_id, True


_TEXT_IMPORT_EXTS = {".txt", ".md", ".markdown", ".csv", ".json", ".jsonl", ".yaml", ".yml", ".rtf"}
_BINARY_SOURCE_EXTS = {
    ".pdf", ".doc", ".docx", ".odt", ".pages",
    ".mp3", ".m4a", ".wav", ".aac", ".ogg", ".flac",
    ".png", ".jpg", ".jpeg", ".tif", ".tiff", ".heic", ".webp",
}
_AUTO_TEXT_LIMIT = 2 * 1024 * 1024


def _read_import_text(path):
    if not os.path.isfile(path):
        return None
    ext = os.path.splitext(path)[1].lower()
    if ext not in _TEXT_IMPORT_EXTS:
        return None
    try:
        size = os.path.getsize(path)
    except OSError:
        return None  # degradation: ok: raw arrival is still preserved; text extraction is opportunistic
    if size > _AUTO_TEXT_LIMIT:
        return None
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except UnicodeDecodeError:
        try:
            with open(path, encoding="utf-8", errors="replace") as f:
                return f.read()
        except OSError:
            return None  # degradation: ok: raw arrival is still preserved; text extraction is opportunistic
    except OSError:
        return None  # degradation: ok: raw arrival is still preserved; text extraction is opportunistic


def _extraction_needed_note(path, text):
    if text and text.strip():
        return ""
    if os.path.isdir(path) or zipfile.is_zipfile(path):
        return ""
    ext = os.path.splitext(path)[1].lower()
    try:
        size = os.path.getsize(path)
    except OSError:
        size = None
    if ext in _TEXT_IMPORT_EXTS and size is not None and size > _AUTO_TEXT_LIMIT:
        return ("text-like arrival is too large for automatic text extraction; "
                "chunk explicitly before structuring. Do not imply the full file was read.")
    if ext in _BINARY_SOURCE_EXTS:
        return ("binary or unreadable source preserved; use OCR or transcription before structuring. "
                "Do not invent contents from this file.")
    if os.path.isfile(path):
        return ("source preserved, but no readable text was extracted automatically. "
                "Inspect or convert it before structuring, and do not invent contents from this file.")
    return ""


def _zip_entries(path):
    entries, problems = [], []
    if not zipfile.is_zipfile(path):
        return entries, problems
    try:
        with zipfile.ZipFile(path) as zf:
            entries = sorted(zf.namelist())
    except (OSError, zipfile.BadZipFile) as e:
        problems.append(str(e))
    return entries, problems


def _looks_tyf_shaped(entries):
    names = {e.replace("\\", "/").strip("/") for e in entries}
    return (
        "WORKSPACE_STATE.yaml" in names
        or any(e.startswith("works/") for e in names)
        or any(e.startswith("sources/") for e in names)
        or any(e.startswith("knowledge-base/") for e in names)
    )


def _copy_arrival(src, dest):
    if os.path.isdir(src):
        for r, dirs, files in os.walk(src):
            for name in dirs + files:
                if os.path.islink(os.path.join(r, name)):
                    sys.exit("Refused: folder imports currently require a real directory tree; "
                             f"symlink found at {os.path.join(r, name)}.")
        shutil.copytree(src, dest)
        return "folder"
    shutil.copy2(src, dest)
    return "file"


def _arrival_listing(path):
    if os.path.isdir(path):
        rows = []
        for r, dirs, files in os.walk(path):
            dirs[:] = sorted(dirs)
            for name in sorted(files):
                rows.append(os.path.relpath(os.path.join(r, name), path).replace(os.sep, "/"))
                if len(rows) >= 80:
                    rows.append("... listing truncated ...")
                    return rows
        return rows
    if zipfile.is_zipfile(path):
        entries, _problems = _zip_entries(path)
        if len(entries) > 120:
            return entries[:120] + ["... listing truncated ..."]
        return entries
    return [os.path.basename(path)]


def _write_import_orientation(work_id, src, preserved, kind, fragment, created_work, listing, zip_tyf_shaped, extraction_note=""):
    label = os.path.splitext(os.path.basename(preserved.rstrip(os.sep)))[0]
    orientation = os.path.join("sources", "imports", f"{label}-orientation.md")
    if os.path.exists(orientation):
        orientation = os.path.join("sources", "imports", f"{label}-{hashlib.sha256(now().encode()).hexdigest()[:6]}-orientation.md")
    rows = "\n".join(f"- {item}" for item in listing[:120]) or "- (no inspectable listing)"
    shape = "TYF-shaped workspace/archive signals detected." if zip_tyf_shaped else "Classification required; do not assume this dump is already organized."
    if fragment:
        frag_line = (
            f"- Source fragment: `{fragment['id']}` ({fragment['path']})\n"
            f"- Structuring pass: `tyf structure {work_id} --source-ref {fragment['id']}`"
        )
    else:
        frag_line = "- No source fragment was minted automatically for this arrival."
    if extraction_note:
        frag_line += f"\n- Extraction needed: {extraction_note}"
    write(orientation, f"""# Arrival orientation: {os.path.basename(src)}

Work: `this book folder`
Kind: `{kind}`
Raw material preserved at: `{preserved.replace(os.sep, "/")}`
New work created: {'yes' if created_work else 'no'}

No manuscript text was written.

## Containment

- The raw arrival is preserved as-is under `sources/imports/`.
- Do not merge folders into the workspace, unpack archives into live TYF directories, or move text into `drafts/` or `manuscript/` until the author accepts an organization plan.
- Treat this packet as a quarantine/orientation record for the amanuensis.

## Shape Read

{shape}

{frag_line}

## Arrival Listing

{rows}

## Analysis Pass For The Agent

1. Classify each item as source, prior draft, voice sample, claim/example, metadata, or unknown.
2. Identify an organizing principle before moving anything: chronology, source type, work unit, theme, scene, chapter, or another author-approved map.
3. If the bundle is TYF-shaped, compare its book, `sources/`, `knowledge-base/`, and `voice/` surfaces to this workspace and propose a merge plan instead of copying over live files.
4. For unreadable files, OCR, transcribe, convert, or chunk explicitly before deriving claims. Do not invent contents from preserved artifacts.
5. For random dumps, ask the author which materials are authoritative, private, obsolete, or exploratory.
6. Mint additional source fragments only for text the author wants preserved as evidence.
7. Keep candidate prose in `{_work_display_path(work_id, "drafts")}/`; manuscript still requires proposal, audit, author review, author decision, and `tyf write --decision`.
""")
    return orientation


def _import_arrival(args, announce=True):
    _require_workspace()
    src = os.path.abspath(args.path)
    if not os.path.exists(src):
        title_hint = ""
        if getattr(args, "cmd", "") == "start":
            title_hint = f'\nIf this is a title, use:\n  tyf start --title "{args.path}"'
        sys.exit(f'Refused: No arrival path found: "{args.path}".{title_hint}')
    work_id, created_work = _work_for_arrival(args)
    _ensure_real_dir(os.path.join("sources", "imports"), "sources/imports/")
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    label = _safe_import_label(os.path.basename(src.rstrip(os.sep)))
    preserved = os.path.join("sources", "imports", f"{stamp}-{label}")
    if os.path.exists(preserved):
        preserved = os.path.join("sources", "imports", f"{stamp}-{hashlib.sha256(src.encode()).hexdigest()[:6]}-{label}")
    _copy_arrival(src, preserved)
    kind = _one_line(args.kind, "auto")
    text = _read_import_text(src)
    fragment = None
    if text and text.strip():
        title = _one_line(args.title, os.path.basename(src))
        fragment = _mint_source_fragment(work_id, kind if kind != "auto" else "import", title, text.strip())
    extraction_note = _extraction_needed_note(src, text)
    listing = _arrival_listing(src)
    zip_tyf_shaped = zipfile.is_zipfile(src) and _looks_tyf_shaped(listing)
    orientation = _write_import_orientation(
        work_id, src, preserved, kind, fragment, created_work, listing, zip_tyf_shaped, extraction_note)
    log_event(".", "import", f"{work_id}/{os.path.basename(preserved)}",
              f"kind={kind} orientation={orientation} fragment={fragment['id'] if fragment else 'none'}")
    result = {
        "work_id": work_id,
        "created_work": created_work,
        "src": src,
        "preserved": preserved,
        "orientation": orientation,
        "fragment": fragment,
        "kind": kind,
    }
    if announce:
        print(f"Imported arrival for work {work_id}.")
        print(f"  Work id: {work_id}")
        print(f"  Preserved: {preserved}")
        print(f"  Orientation: {orientation}")
        if fragment:
            print(f"Source fragment: {fragment['id']}")
        if extraction_note:
            print(f"Extraction needed: {extraction_note}")
        print("No manuscript text was written.")
        print("Next useful move: read the orientation packet, classify the arrival, and ask the author before promoting anything.")
    return result


def cmd_import(args):
    _import_arrival(args, announce=True)


def _work_for_start(args):
    title = _one_line(getattr(args, "title", None))
    language = getattr(args, "language", None)
    if getattr(args, "work", None):
        work_id = _safe_work_id(args.work)
        _confine_work(work_id)
        _require_work(work_id)
        _update_work_metadata(work_id, title=title, language=language)
        return work_id, False, None
    active = _active_work_id()
    if active:
        _update_work_metadata(active, title=title, language=language)
        return active, False, None
    work_id = ROOT_WORK_ID if os.path.isfile("work.yaml") else _safe_work_id(_slugify_title(title) if title else _untitled_work_id())
    _confine_work(work_id)
    _create_work(work_id, "book", title=title, language=language, activate=True)
    _write_begin_packet(work_id, title, language)
    return work_id, True, None


def _start_paths(work_id):
    return (
        _work_path(work_id, ".review", "writing-runway.md"),
        _work_path(work_id, "drafts", "candidate-draft.md"),
    )


def _write_start_runway(work_id, arrival=None):
    _require_work(work_id)
    runway, draft = _start_paths(work_id)
    orientation = arrival.get("orientation") if arrival else ""
    preserved = arrival.get("preserved") if arrival else ""
    starter, _seed = _ensure_first_session_packet(work_id)
    preserved_existing = os.path.exists(runway)
    if preserved_existing:
        if orientation or preserved:
            append(runway, f"""
## Later start: {now()}

{f"- Arrival orientation: `{orientation.replace(os.sep, '/')}`" if orientation else "- No arrival orientation was created in this command."}
{f"- Raw material preserved at: `{preserved.replace(os.sep, '/')}`" if preserved else "- No new raw material was preserved in this command."}
- Existing runway text above was preserved. Use `tyf resume` to return without losing session notes.
""")
    else:
        write(runway, f"""# Writing runway

Work: `{work_id}`

## Purpose

Start writing from the author's actual material. Do not wait for a title,
complete outline, perfect classification, audit readiness, or publication-grade
certainty.

## Source State

{f"- Arrival orientation: `{orientation.replace(os.sep, '/')}`" if orientation else "- No arrival was provided in this command."}
{f"- Raw material preserved at: `{preserved.replace(os.sep, '/')}`" if preserved else "- Use the first-session packet and any existing sources."}
- First-session evidence: `{starter.replace(os.sep, '/')}`

## Session Move

1. If there is an arrival orientation, read it first and pick a simple
   organization principle: chronology, voice, scene, question, chapter, or
   source type.
2. Use the gentle attention deck in the first-session packet. Do not ask the author to answer every prompt before drafting; one strong source, image, question, or voice cue is enough to begin.
3. Ask only the questions needed to begin one passage, and store the answers in
   `{starter.replace(os.sep, '/')}`.
4. Write candidate prose in `{draft.replace(os.sep, "/")}`.
5. Keep uncertainty visible in brackets rather than solving it silently.
6. Leave `manuscript/` empty until the author later chooses to pass material
   through proposal, review, acceptance, and controlled write.

## Non-Blocking Rules

- Unknown title is acceptable.
- Unknown final structure is acceptable.
- Imperfect scaffold organization is acceptable.
- Drafting is allowed; manuscript publication is later.
""")
    if not os.path.exists(draft):
        write(draft, f"""# Candidate draft

[Start drafting here. Use the preserved scaffold, source packet, interview
answers, or one remembered image. Keep unresolved facts in brackets.]

""")
    return runway, draft, preserved_existing

def _git(args):
    import subprocess
    return subprocess.run(["git", *args], capture_output=True, text=True)  # process-owner: reviewed: bounded git command list, no shell, interactive-free

def _git_root():
    p = _git(["rev-parse", "--show-toplevel"])
    if p.returncode != 0:
        return None
    return p.stdout.strip()

def _git_status_lines(scoped=False):
    args = ["status", "--short"]
    if scoped:
        args += ["--", "."]
    p = _git(args)
    if p.returncode != 0:
        return None, (p.stderr or p.stdout).strip()
    return [ln for ln in p.stdout.splitlines() if ln.strip()], ""

def cmd_reflexes(args):
    _require_workspace()
    print("tyf reflexes (transparent hooks)")
    print("- documentation honesty: mutating commands run `tyf check` warn-only,")
    print("  unless TYF_NO_DOC_HOOK=1 is set.")
    print("- attentive amanuensis: after `tyf write`, new or resurfaced gaps are")
    print("  counted and handed back; nothing is fixed automatically.")
    print("- workspace integrity: `tyf doctor` verifies structure, write logs, and")
    print("  out-of-band manuscript edits.")
    print("- git recovery: TYF never commits silently. In a git workspace, use")
    print("  `tyf snapshot --message \"meaningful checkpoint\"` to stage and commit")
    print("  the current workspace state as an explicit recovery point.")
    root = _git_root()
    if root:
        status, err = _git_status_lines()
        if status is None:
            print(f"- git status: unavailable ({err})")
        elif status:
            print(f"- git status: {len(status)} changed path(s) visible to snapshot.")
        else:
            print("- git status: clean.")
    else:
        print("- git status: this workspace is not inside a git repository.")

def cmd_snapshot(args):
    _require_workspace()
    root = _git_root()
    if not root:
        sys.exit("Refused: `tyf snapshot` needs this workspace to be inside a git repository.")
    message = _one_line(args.message)
    if not message:
        sys.exit("Refused: snapshot needs --message.")
    status, err = _git_status_lines(scoped=True)
    if status is None:
        sys.exit(f"Refused: git status failed: {err}")
    if not status:
        print("tyf snapshot: no git changes to commit.")
        return
    log_event(".", "snapshot", message, f"git recovery point at {root}")
    status, err = _git_status_lines(scoped=True)
    if status is None:
        sys.exit(f"Refused: git status failed after event log update: {err}")
    add = _git(["add", "-A", "--", "."])
    if add.returncode != 0:
        sys.exit((add.stderr or add.stdout or "git add failed").strip())
    commit = _git(["commit", "-m", message])
    if commit.returncode != 0:
        sys.exit((commit.stderr or commit.stdout or "git commit failed").strip())
    rev = _git(["rev-parse", "--short", "HEAD"])
    short = rev.stdout.strip() if rev.returncode == 0 else "(unknown)"
    print(f"Snapshot committed: {short} {message}")
    print("Included changed paths:")
    for ln in status[:20]:
        print(f"  {ln}")
    if len(status) > 20:
        print(f"  ... and {len(status) - 20} more")

def _set_active(work_id):
    path = "WORKSPACE_STATE.yaml"
    if not os.path.isfile(path):
        sys.exit("no WORKSPACE_STATE.yaml here; run `tyf init` or cd into the workspace.")
    lines = open(path, encoding="utf-8").read().splitlines()
    out = []
    for ln in lines:
        if ln.startswith("active_work:"):
            out.append(f"active_work: {work_id}")
        else:
            out.append(ln)
    open(path, "w", encoding="utf-8").write("\n".join(out) + "\n")

def cmd_open(args):
    _require_workspace()
    args.work = _safe_work_id(args.work)
    _confine_work(args.work)
    _require_work(args.work)
    _set_active(args.work)
    wy = read_state(_work_path(args.work, "work.yaml"))
    regs = get(wy, "registers", default=[])
    print(f"Active work: {args.work}")
    print(f"Load registers: {regs}")
    print(f"Load style sheet: {_work_display_path(args.work, 'style-sheet.md')}")
    rev = _work_path(args.work, ".review")
    latest = sorted(os.listdir(rev)) if os.path.isdir(rev) else []
    print(f"Load latest .review: {latest[-3:] if latest else '(none)'}")
    print("Write zones: Compose -> drafts/  Propose/Audit -> .review/  Manuscript -> `tyf write` only")

def cmd_status(args):
    _require_workspace()
    st = read_state("WORKSPACE_STATE.yaml")
    active = _active_work_id()
    wy = read_state(_work_path(active, "work.yaml")) if active else {}
    print(f"active_work : {get(st,'active_work') or active or '(none)'}")
    print(f"active_band : {get(st,'active_band')}")
    print(f"workspace.status : {get(st,'status')}")
    if active:
        print(f"work.title      : {get(wy,'title') or '(unknown)'}")
        print(f"work.title_status: {get(wy,'title_status') or 'unknown'}")
        print(f"work.language    : {get(wy,'language') or 'undetermined'}")
        print(f"work.status      : {get(wy,'status') or 'unknown'}")
    print(f"write.compose: {get(st,'write_control','compose')}")
    print(f"write.revise : {get(st,'write_control','revise')}")
    works = [ROOT_WORK_ID] if os.path.isfile("work.yaml") else []
    if os.path.isdir("works"):
        works.extend(f for f in sorted(os.listdir("works")) if os.path.isdir(os.path.join("works", f)))
    print(f"works       : {works or '(none)'}")
    print("write zones : Compose->drafts/  Propose/Audit->.review/  Manuscript-> `tyf write` only")

def cmd_resume(args):
    _require_workspace()
    if getattr(args, "work", None):
        work = _safe_work_id(args.work)
    else:
        work = _active_work_id()
    if not work:
        print("No active work yet.")
        print("Next useful move: run `tyf start` for an untitled work, or `tyf start <path>` to preserve existing material and open a writing runway.")
        return
    _confine_work(work)
    _require_work(work)
    wy = read_state(_work_path(work, "work.yaml"))
    title = get(wy, "title") or "unknown"
    title_status = get(wy, "title_status") or ("working" if title != "unknown" else "unknown")
    status = get(wy, "status") or "unknown"
    language = get(wy, "language") or "undetermined"
    review = _work_path(work, ".review")
    proposals = sorted(os.listdir(os.path.join(review, "proposals"))) if os.path.isdir(os.path.join(review, "proposals")) else []
    decisions = sorted(os.listdir(os.path.join(review, "decisions"))) if os.path.isdir(os.path.join(review, "decisions")) else []
    interview = os.path.join("sources", "interviews", f"{work}-first-session.md")
    prompts = []
    if os.path.isfile(interview):
        for line in _read(interview).splitlines():
            if "[PROMPT:" in line:
                prompts.append(line.strip())
    print(f"Active work: {work}")
    print(f"  title: {title} ({title_status})")
    print(f"  language: {language}")
    print(f"  status: {status}")
    print(f"  first-session evidence: {interview.replace(os.sep, '/') if os.path.isfile(interview) else '(none yet)'}")
    print(f"  pending proposals: {len(proposals)}")
    print(f"  decisions: {len(decisions)}")
    if prompts:
        print("  open prompts:")
        for prompt in prompts[:5]:
            print(f"    - {prompt}")
    print("Next useful move:")
    if status in {"accepted"} and decisions:
        print(f"  Run `tyf write {work} --decision {os.path.splitext(decisions[-1])[0]}` if the author is ready.")
    elif proposals:
        print("  Review the latest proposal, record/pass an audit, then accept only what the author approves.")
    elif os.path.isfile(interview):
        print(f"  Continue filling {interview.replace(os.sep, '/')} or import/capture source before drafting.")
    else:
        print("  Import or capture source material before drafting candidate prose.")

def cmd_mark_ready(args):
    _require_workspace()
    args.work = _safe_work_id(args.work)
    _confine_work(args.work)
    _require_work(args.work)
    path = _work_path(args.work, ".review", "ready.md")
    append(path, f"- {now()} unit READY for audit: {args.unit}\n")
    _set_work_status(args.work, "ready-for-audit")
    log_event(".", "mark-ready", f"{args.work}/{args.unit}")
    print(f"Marked ready: {args.work} / {args.unit}. Run `auditing-adversarially` before this is done.")

def _file_sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _canonical_hash(obj):
    payload = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _record_id(prefix, *parts):
    stamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
    digest = hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()[:8]
    return f"{prefix}-{stamp}-{digest}"


def _safe_record_id(record_id, prefix):
    if not record_id or not record_id.startswith(prefix + "-") or not re.fullmatch(r"[A-Za-z0-9._-]+", record_id):
        sys.exit(f"Refused: unsafe {prefix} id {record_id!r}.")
    return record_id


def _review_path(work, folder, record_id):
    _safe_work_id(work)
    _confine_work(work)
    _require_work(work)
    return _work_path(work, ".review", folder, record_id + ".json")


def _write_json(path, data):
    _reject_symlink_components(os.path.dirname(path), "review record directory")
    atomic_write(path, json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False) + "\n")


def _record_seal_path(work):
    _safe_work_id(work)
    _confine_work(work)
    _require_work(work)
    return _work_path(work, ".review", "record-seals.jsonl")


def _read_record_seals(work):
    path = _record_seal_path(work)
    if not os.path.exists(path):
        return [], []
    entries, problems = [], []
    try:
        with open(path, encoding="utf-8") as f:
            for i, raw in enumerate(f, 1):
                if not raw.strip():
                    continue
                try:
                    entry = json.loads(raw)
                except json.JSONDecodeError as e:
                    problems.append(f"{work}: invalid record seal line {i}: {e}")
                    continue
                entries.append(entry)
    except OSError as e:
        problems.append(f"{work}: could not read record seals: {e}")
    return entries, problems


def _append_record_seal(work, kind, record_id, data):
    path = _record_seal_path(work)
    _reject_symlink_components(os.path.dirname(path), "review record directory")
    entry = {
        "sealed_at": now(),
        "kind": kind,
        "id": record_id,
        "sha256": _canonical_hash(data),
    }
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, sort_keys=True, ensure_ascii=False) + "\n")


def _record_integrity_problem(work, kind, record_id, data):
    entries, problems = _read_record_seals(work)
    if problems:
        return problems[0]
    matches = [e for e in entries
               if e.get("kind") == kind and e.get("id") == record_id]
    if not matches:
        return f"{work}: {kind} record {record_id} has no seal; integrity cannot be verified"
    digest = _canonical_hash(data)
    if digest not in {e.get("sha256") for e in matches}:
        return f"{work}: {kind} record {record_id} seal mismatch; record may be tampered"
    return None


def _require_record_integrity(work, kind, record_id, data):
    problem = _record_integrity_problem(work, kind, record_id, data)
    if problem:
        sys.exit("Refused: " + problem)


def _write_review_record(work, folder, kind, record_id, data):
    path = _review_path(work, folder, record_id)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if os.path.exists(path):
        sys.exit(f"Refused: review record already exists: {path}")
    _write_json(path, data)
    _append_record_seal(work, kind, record_id, data)
    return path


def _read_json(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except OSError:
        sys.exit(f"Refused: missing record {path}.")
    except json.JSONDecodeError as e:
        sys.exit(f"Refused: invalid record {path}: {e}")


def _source_lines(path):
    with open(path, encoding="utf-8") as f:
        return f.read().splitlines(keepends=True)


def _parse_line_ranges(spec, max_line):
    if not spec:
        return None, "whole-file"
    ranges = []
    parts = [p.strip() for p in spec.split(",") if p.strip()]
    if not parts:
        sys.exit("Refused: --lines must name at least one line or range.")
    previous_end = 0
    for part in parts:
        if "-" in part:
            left, sep, right = part.partition("-")
            if not left.isdigit() or not right.isdigit():
                sys.exit(f"Refused: invalid line range {part!r}. Use numbers like 2 or 2-5.")
            start, end = int(left), int(right)
        else:
            if not part.isdigit():
                sys.exit(f"Refused: invalid line number {part!r}.")
            start = end = int(part)
        if start < 1 or end < 1 or end < start:
            sys.exit(f"Refused: invalid line range {part!r}; ranges must be positive and ascending.")
        if end > max_line:
            sys.exit(f"Refused: line range {part!r} exceeds proposal length ({max_line} line(s)).")
        if start <= previous_end:
            sys.exit("Refused: --lines must be strictly increasing and non-overlapping.")
        ranges.append([start, end])
        previous_end = end
    normalized = ",".join(str(a) if a == b else f"{a}-{b}" for a, b in ranges)
    return ranges, f"lines {normalized}"


def _select_line_ranges(lines, ranges):
    if ranges is None:
        return "".join(lines)
    out = []
    for start, end in ranges:
        out.extend(lines[start - 1:end])
    return "".join(out)


def _require_patch_file(work, patch):
    rel = _workspace_rel(patch, "accepted patch")
    real = os.path.realpath(rel)
    review = os.path.realpath(_work_path(work, ".review"))
    if not os.path.isfile(real):
        sys.exit(f"Refused: accepted patch not found: {patch}")
    if os.path.islink(os.path.abspath(patch)):
        sys.exit(f"Refused: accepted patch is a symlink: {patch}")
    if not _within(review, real):
        sys.exit(f"Refused: accepted patch must live under {_work_display_path(work, '.review')}/.")
    return rel.replace(os.sep, "/")


def _accepted_patch_problems(work, record):
    patch = record.get("accepted_patch") if isinstance(record, dict) else None
    if not patch:
        return []
    rel = patch.get("path")
    if not rel:
        return [f"{work}: accepted patch record has no path"]
    if os.path.isabs(rel):
        return [f"{work}: accepted patch uses an absolute path"]
    try:
        _reject_symlink_components(rel, "accepted patch")
    except SystemExit as e:
        return [str(e)]
    root = os.path.realpath(".")
    real = os.path.realpath(rel)
    review = os.path.realpath(_work_path(work, ".review"))
    if not _within(root, real):
        return [f"{work}: accepted patch resolves outside the workspace: {rel}"]
    if not _within(review, real):
        return [f"{work}: accepted patch is outside {_work_display_path(work, '.review')}/: {rel}"]
    if not os.path.isfile(real):
        return [f"{work}: missing accepted patch file: {rel}"]
    expected = patch.get("sha256")
    if expected and _file_sha256(real) != expected:
        return [f"{work}: accepted patch hash mismatch; patch may be tampered: {rel}"]
    return []


def _author_review_packet_problems(work, record):
    if not isinstance(record, dict):
        return []
    review_id = record.get("author_review_id")
    if review_id or record.get("author_review_packet"):
        problems = []
        if not review_id:
            return [f"{work}: decision names an author review packet without a review id"]
        review_path = _review_path(work, "reviews", review_id)
        if not os.path.isfile(review_path):
            return [f"{work}: missing author review record: {review_id}"]
        try:
            review = json.loads(_read(review_path))
        except json.JSONDecodeError as e:
            return [f"{work}: invalid author review record {review_id}: {e}"]
        if review.get("proposal_id") != record.get("proposal_id"):
            problems.append(f"{work}: author review {review_id} does not match decision proposal")
        if record.get("author_review_packet") != review.get("packet"):
            problems.append(f"{work}: decision points to a different author review packet than {review_id}")
        problems.extend(_author_review_packet_problems(work, review))
        return problems

    packet = record.get("packet")
    expected = record.get("packet_sha256")
    if not packet and not expected:
        return []
    if not packet:
        return [f"{work}: author review record has no packet path"]
    if os.path.isabs(packet):
        return [f"{work}: author review packet uses an absolute path"]
    try:
        _reject_symlink_components(packet, "author review packet")
    except SystemExit as e:
        return [str(e)]
    root = os.path.realpath(".")
    real = os.path.realpath(packet)
    review_root = os.path.realpath(_work_path(work, ".review", "author-reviews"))
    if not _within(root, real):
        return [f"{work}: author review packet resolves outside the workspace: {packet}"]
    if not _within(review_root, real):
        return [f"{work}: author review packet is outside {_work_display_path(work, '.review/author-reviews')}/: {packet}"]
    if not os.path.isfile(real):
        return [f"{work}: missing author review packet: {packet}"]
    if expected and _file_sha256(real) != expected:
        return [f"{work}: author review packet hash mismatch; packet may be tampered: {packet}"]
    return []


def _patch_header_filename(line):
    parts = line.strip().split()
    if len(parts) < 2 or parts[1] == "/dev/null":
        return None
    name = parts[1].replace("\\", "/")
    if name.startswith("a/") or name.startswith("b/"):
        name = name[2:]
    return os.path.basename(name)


def _apply_unified_patch(base_text, patch_text, unit):
    base = base_text.splitlines(keepends=True)
    out = []
    pos = 0
    saw_hunk = False
    old_target = new_target = None
    lines = patch_text.splitlines(keepends=True)
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("--- "):
            if saw_hunk:
                sys.exit("Refused: accepted patch must contain exactly one file.")
            old_target = _patch_header_filename(line)
            i += 1
            if i < len(lines) and lines[i].startswith("+++ "):
                new_target = _patch_header_filename(lines[i])
                i += 1
            target = new_target or old_target
            if target and target != unit:
                sys.exit(f"Refused: accepted patch targets {target!r}, expected {unit!r}.")
            continue
        m = re.match(r"@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@", line)
        if not m:
            i += 1
            continue
        saw_hunk = True
        old_start = int(m.group(1))
        old_count = int(m.group(2) or "1")
        new_count = int(m.group(4) or "1")
        target_pos = old_start - 1 if old_start > 0 else 0
        if target_pos < pos or target_pos > len(base):
            sys.exit("Refused: accepted patch hunk location does not match the manuscript base.")
        out.extend(base[pos:target_pos])
        pos = target_pos
        i += 1
        old_seen = 0
        new_seen = 0
        while i < len(lines):
            hline = lines[i]
            if hline.startswith("@@ "):
                break
            if hline.startswith("--- "):
                break
            if hline.startswith("\\"):
                i += 1
                continue
            if not hline:
                sys.exit("Refused: accepted patch has an empty hunk line without a prefix.")
            prefix, text = hline[0], hline[1:]
            if prefix == " ":
                if pos >= len(base) or base[pos] != text:
                    sys.exit("Refused: accepted patch context does not match the manuscript base.")
                out.append(base[pos])
                pos += 1
                old_seen += 1
                new_seen += 1
            elif prefix == "-":
                if pos >= len(base) or base[pos] != text:
                    sys.exit("Refused: accepted patch deletion does not match the manuscript base.")
                pos += 1
                old_seen += 1
            elif prefix == "+":
                out.append(text)
                new_seen += 1
            else:
                sys.exit(f"Refused: accepted patch hunk line has invalid prefix {prefix!r}.")
            i += 1
        if old_seen != old_count or new_seen != new_count:
            sys.exit("Refused: accepted patch hunk line counts do not match the unified-diff header.")
    if not saw_hunk:
        sys.exit("Refused: accepted patch has no unified-diff hunk.")
    out.extend(base[pos:])
    return "".join(out)


def _unit_lock_path(work, unit):
    if os.path.basename(unit) != unit or unit in ("", ".", ".."):
        sys.exit(f"Refused: unsafe manuscript unit for lock: {unit!r}.")
    d = _work_path(work, ".review", "locks")
    _ensure_real_dir(d, "review locks/")
    return os.path.join(d, unit + ".lock.json")


def _acquire_unit_lock(work, unit):
    path = _unit_lock_path(work, unit)
    payload = {
        "unit": unit,
        "pid": os.getpid(),
        "created_at": now(),
    }
    try:
        fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        sys.exit(f"Refused: manuscript unit is locked for write: {unit}. Run `tyf doctor` if this looks stale.")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(json.dumps(payload, sort_keys=True, ensure_ascii=False) + "\n")
    return path


def _release_unit_lock(path):
    try:
        os.unlink(path)
    except FileNotFoundError:  # degradation: ok: the lock is already absent, so release is complete
        return


def _workspace_rel(path, label):
    if not path:
        sys.exit(f"Refused: missing {label}.")
    _reject_symlink_components(path, label)
    root = os.path.realpath(".")
    real = os.path.realpath(path)
    if not _within(root, real):
        sys.exit(f"Refused: {label} resolves outside the workspace: {path}")
    return os.path.relpath(real, root)


def _require_draft_source(work, src):
    drafts = _work_path(work, "drafts")
    _reject_symlink_components(drafts, "drafts/")
    if not os.path.isdir(drafts):
        sys.exit(f"Refused: work {work!r} has no drafts/; proposals must start from this work's drafts.")
    rel = _workspace_rel(src, "draft source")
    real = os.path.realpath(rel)
    if not os.path.isfile(real):
        sys.exit(f"draft not found: {src}")
    if os.path.islink(os.path.abspath(src)):
        sys.exit(f"Refused: draft source is a symlink: {src}")
    if not _within(drafts, real):
        sys.exit(f"Refused: source must live under {drafts}{os.sep}. Got: {src}")
    return rel


def _dest_base_hash(dest):
    if not os.path.exists(dest):
        return None
    if os.path.islink(os.path.abspath(dest)):
        sys.exit(f"Refused: manuscript destination is a symlink: {dest}")
    if not os.path.isfile(dest):
        sys.exit(f"Refused: manuscript destination is not a file: {dest}")
    return _file_sha256(dest)


def _load_proposal(work, proposal_id):
    proposal_id = _safe_record_id(proposal_id, "proposal")
    path = _review_path(work, "proposals", proposal_id)
    proposal = _read_json(path)
    if proposal.get("id") != proposal_id or proposal.get("work") != work:
        sys.exit(f"Refused: proposal {proposal_id} does not belong to work {work}.")
    _require_record_integrity(work, "proposal", proposal_id, proposal)
    return proposal


def _load_decision(work, decision_id):
    decision_id = _safe_record_id(decision_id, "decision")
    path = _review_path(work, "decisions", decision_id)
    decision = _read_json(path)
    if decision.get("id") != decision_id or decision.get("work") != work:
        sys.exit(f"Refused: decision {decision_id} does not belong to work {work}.")
    _require_record_integrity(work, "decision", decision_id, decision)
    return decision


def _passing_audit_for(work, proposal_id, proposal_hash):
    audit_dir = _work_path(work, ".review", "audits")
    if not os.path.isdir(audit_dir):
        return None
    for name in sorted(os.listdir(audit_dir), reverse=True):
        if not name.endswith(".json"):
            continue
        audit = _read_json(os.path.join(audit_dir, name))
        audit_id = os.path.splitext(name)[0]
        if audit.get("id") != audit_id or audit.get("work") != work:
            sys.exit(f"Refused: audit record {audit_id} does not belong to work {work}.")
        if (audit.get("proposal_id") == proposal_id
                and audit.get("proposal_hash") == proposal_hash):
            _require_record_integrity(work, "audit", audit_id, audit)
            if (audit.get("verdict") == "pass"
                    and audit.get("findings_answered") is True):
                return audit
    return None


def cmd_propose(args):
    _require_workspace()
    work = _safe_work_id(args.work)
    _confine_work(work)
    _require_work(work)
    src = _require_draft_source(work, args.src)
    dest_name = args.dest or os.path.basename(src)
    if os.path.basename(dest_name) != dest_name or dest_name in ("", ".", ".."):
        sys.exit("Refused: proposal destination must be a manuscript filename, not a path.")
    man = _work_path(work, "manuscript")
    _ensure_real_dir(man, "manuscript/")
    dest = os.path.join(man, dest_name)
    source_refs = _resolve_source_refs(work, getattr(args, "source_refs", None))
    proposal_id = _record_id("proposal", work, src, _file_sha256(src))
    proposal = {
        "id": proposal_id,
        "work": work,
        "src": src.replace(os.sep, "/"),
        "dest": dest.replace(os.sep, "/"),
        "unit": dest_name,
        "src_sha256": _file_sha256(src),
        "base_sha256": _dest_base_hash(dest),
        "created_at": now(),
        "accepted_scope": "whole-file",
        "source_refs": source_refs,
    }
    _write_review_record(work, "proposals", "proposal", proposal_id, proposal)
    _set_work_status(work, "drafting")
    log_event(".", "propose", f"{work}/{proposal_id}", src)
    print(f"Proposal: {proposal_id}")
    print(f"  source: {proposal['src']}")
    print(f"  destination: {proposal['dest']}")
    if source_refs:
        print("  source refs: " + ", ".join(ref["id"] for ref in source_refs))
    print(f"Next: record an audit, run `tyf review {work} {proposal_id}`, then accept only what the author approves.")


def _review_rel(path):
    rel = path.replace(os.sep, "/")
    return rel[2:] if rel.startswith("./") else rel


def _source_gap_lines(path, limit=8):
    gaps = []
    try:
        for i, line in enumerate(_read(path).splitlines(), 1):
            if "[AUTHOR:" in line:
                gaps.append(f"- line {i}: {line.strip()}")
                if len(gaps) >= limit:
                    break
    except OSError:
        return ["- Draft could not be read for gap extraction."]
    return gaps or ["- No `[AUTHOR: ...]` gaps visible in the candidate draft."]


def _source_preview(path, limit=18):
    try:
        lines = _read(path).splitlines()
    except OSError:
        return "(draft could not be read)"
    shown = lines[:limit]
    preview = "\n".join(shown).strip()
    if len(lines) > limit:
        preview += f"\n\n... {len(lines) - limit} more line(s) not shown in this packet."
    return preview or "(draft is empty)"


def _write_author_review_packet(work, review_id, proposal, audit):
    packet_dir = _work_path(work, ".review", "author-reviews")
    _ensure_real_dir(packet_dir, ".review/author-reviews/")
    packet_path = os.path.join(packet_dir, f"{review_id}.md")
    src_refs = proposal.get("source_refs", [])
    src_ref_lines = "\n".join(
        f"- `{ref.get('id')}` from `{ref.get('path')}`"
        for ref in src_refs
    ) or "- No source refs are attached. The author should confirm whether this is source-grounded enough."
    base = proposal.get("base_sha256")
    base_line = (
        f"- Existing manuscript base hash: `{base}`"
        if base else "- This would create a new manuscript unit."
    )
    audit_line = (
        f"- Passing audit: `{audit.get('id')}`"
        + (f" with report `{audit.get('report')}`" if audit.get("report") else "")
        if audit else "- No passing audit with answered findings yet. Acceptance will refuse until one exists."
    )
    gap_lines = "\n".join(_source_gap_lines(proposal["src"]))
    preview = _source_preview(proposal["src"])
    write(packet_path, f"""# Author review: {review_id}

Work: `{work}`
Proposal: `{proposal.get('id')}`
Destination: `{proposal.get('dest')}`
Created: `{now()}`

This is not manuscript text. It is the author-readable review packet for deciding what, if anything, may be accepted.

## What the author is approving

- Candidate draft: `{proposal.get('src')}`
- Manuscript unit: `{proposal.get('unit')}`
- Draft hash: `{proposal.get('src_sha256')}`
{base_line}

## What would change

- If accepted whole, the candidate draft becomes the proposed manuscript unit through `tyf write`.
- If accepted by line range, only those candidate source lines enter the manuscript.
- If accepted by patch, only the reviewed patch enters the manuscript.
- No text is written by this review packet.

## Source support

{src_ref_lines}

## Audit status

{audit_line}

## Uncertainties

{gap_lines}

## Candidate preview

```text
{preview}
```

## Author choices

- Accept the whole proposal only if it is faithful: `tyf accept {work} {proposal.get('id')} --evidence "<author acceptance>"`
- Accept selected source lines: `tyf accept {work} {proposal.get('id')} --lines 2,5-8 --evidence "<author acceptance>"`
- Accept an exact reviewed patch: `tyf accept {work} {proposal.get('id')} --patch .review/patches/<file>.patch --evidence "<author acceptance>"`
- Ask for revision or more source instead of accepting.
""")
    return _review_rel(packet_path)


def _author_review_for(work, proposal_id, proposal_hash):
    review_dir = _work_path(work, ".review", "reviews")
    if not os.path.isdir(review_dir):
        return None
    for name in sorted(os.listdir(review_dir), reverse=True):
        if not name.endswith(".json"):
            continue
        review = _read_json(os.path.join(review_dir, name))
        review_id = os.path.splitext(name)[0]
        if review.get("id") != review_id or review.get("work") != work:
            sys.exit(f"Refused: author review record {review_id} does not belong to work {work}.")
        if (review.get("proposal_id") == proposal_id
                and review.get("proposal_hash") == proposal_hash):
            _require_record_integrity(work, "review", review_id, review)
            packet = review.get("packet")
            if not packet or not os.path.isfile(packet):
                sys.exit("Refused: author review packet is missing; run `tyf review` again.")
            if _file_sha256(packet) != review.get("packet_sha256"):
                sys.exit("Refused: author review packet changed after review; run `tyf review` again.")
            return review
    return None


def cmd_review(args):
    _require_workspace()
    work = _safe_work_id(args.work)
    _confine_work(work)
    _require_work(work)
    proposal = _load_proposal(work, args.proposal)
    if _file_sha256(proposal["src"]) != proposal.get("src_sha256"):
        sys.exit("Refused: proposal source changed before author review.")
    _require_source_ref_integrity(work, proposal.get("source_refs", []))
    proposal_hash = _canonical_hash(proposal)
    audit = _passing_audit_for(work, args.proposal, proposal_hash)
    review_id = _record_id("review", work, args.proposal, proposal_hash)
    packet = _write_author_review_packet(work, review_id, proposal, audit)
    review = {
        "id": review_id,
        "work": work,
        "proposal_id": args.proposal,
        "proposal_hash": proposal_hash,
        "packet": packet,
        "packet_sha256": _file_sha256(packet),
        "created_at": now(),
    }
    _write_review_record(work, "reviews", "review", review_id, review)
    log_event(".", "review", f"{work}/{review_id}", f"proposal={args.proposal}")
    print(f"Author review: {review_id}")
    print(f"  packet: {packet}")
    if audit:
        print(f"  audit: {audit.get('id')}")
    else:
        print("  audit: no passing audit yet")
    print("Next: show this packet to the author; accept only the scope they approve.")


def _write_audit_report(work, audit_id, audit, proposal):
    report_path = _work_path(work, ".review", "audits", f"{audit_id}.md")
    _ensure_real_dir(os.path.dirname(report_path), ".review/audits/")
    src_refs = audit.get("source_refs", [])
    src_ref_lines = "\n".join(
        f"- `{ref.get('id')}` from `{ref.get('path')}`"
        for ref in src_refs
    ) or "- No source refs were attached to this proposal."
    findings = (
        "- No blocking findings recorded by this helper invocation."
        if audit.get("verdict") == "pass" and audit.get("findings_answered")
        else "- Add findings here before this audit can support acceptance."
    )
    dispositions = (
        "- Blocking findings disposition: answered, fixed, or explicitly accepted with reason."
        if audit.get("findings_answered")
        else "- Blocking findings disposition: not answered."
    )
    write(report_path, f"""# Audit report: {audit_id}

Work: `{work}`
Unit: `{audit.get('unit')}`
Proposal: `{audit.get('proposal_id')}`
Verdict: `{audit.get('verdict')}`
Recorded: `{audit.get('recorded_at')}`

This is the inspectable editorial audit note. The JSON record carries the Gate facts; this note carries the author-readable review shape.

## Proposal

- Draft: `{proposal.get('src')}`
- Destination: `{proposal.get('dest')}`
- Proposal hash: `{audit.get('proposal_hash')}`

## Source refs

{src_ref_lines}

## Checks

- [x] Source fidelity: compare candidate prose against preserved source and attached source refs.
- [x] Voice/register: compare candidate prose against the work style sheet and voice evidence.
- [x] Unsupported claims: identify facts, citations, or interpretations not grounded in source.
- [x] Open gaps: keep unresolved knowledge visible instead of smoothing it away.

## Findings

{findings}

## Limitations

- The helper records that this audit shape exists; the agent and author remain responsible for the editorial judgment inside it.
- If later review finds an issue, record it here or in a superseding audit note before acceptance.

## Dispositions

{dispositions}
""")
    return _review_rel(report_path)


def cmd_audit(args):
    _require_workspace()
    args.work = _safe_work_id(args.work)
    _confine_work(args.work)
    _require_work(args.work)
    if getattr(args, "record", False):
        if not args.proposal:
            sys.exit("Refused: audit --record requires --proposal <proposal-id>.")
        if args.verdict == "pass" and not getattr(args, "findings_answered", False):
            sys.exit("Refused: a passing audit record requires --findings-answered.")
        proposal = _load_proposal(args.work, args.proposal)
        proposal_hash = _canonical_hash(proposal)
        if _file_sha256(proposal["src"]) != proposal.get("src_sha256"):
            sys.exit("Refused: proposal source changed before audit.")
        _require_source_ref_integrity(args.work, proposal.get("source_refs", []))
        audit_id = _record_id("audit", args.work, args.proposal, args.verdict)
        audit = {
            "id": audit_id,
            "work": args.work,
            "unit": args.unit,
            "proposal_id": args.proposal,
            "proposal_hash": proposal_hash,
            "source_refs": proposal.get("source_refs", []),
            "verdict": args.verdict,
            "findings_answered": bool(getattr(args, "findings_answered", False)),
            "recorded_at": now(),
        }
        audit["report"] = _write_audit_report(args.work, audit_id, audit, proposal)
        _write_review_record(args.work, "audits", "audit", audit_id, audit)
        _set_work_status(args.work, "audited" if args.verdict == "pass" else "needs-revision")
        log_event(".", "audit", f"{args.work}/{audit_id}", f"proposal={args.proposal} verdict={args.verdict}")
        print(f"Audit: {audit_id}")
        print(f"  verdict: {args.verdict}")
        print(f"  report: {audit['report']}")
        return
    print(f"Audit checklist for {args.work} / {args.unit} (read-only; write findings to .review/):")
    for item in ["frame-lock", "unsupported claims (check claims index)", "hidden assumptions",
                 "machine cadence", "register cross-talk", "citation integrity (verify via MCP)",
                 "terminology drift (vs style sheet)", "cross-references resolve",
                 "logical contradiction", "kept promises / composition"]:
        print(f"  [ ] {item}")
    print("Verdict PASSED only when every finding is answered: fixed, or accepted with reason.")

def cmd_accept(args):
    _require_workspace()
    work = _safe_work_id(args.work)
    _confine_work(work)
    _require_work(work)
    proposal = _load_proposal(work, args.proposal)
    evidence = _one_line(args.evidence)
    if not evidence:
        sys.exit("Refused: accept requires --evidence with the author's explicit acceptance text or reference.")
    _require_work_status(work, "audited", "author acceptance")
    src = proposal["src"]
    if _file_sha256(src) != proposal.get("src_sha256"):
        sys.exit("Refused: proposal source changed before acceptance.")
    _require_source_ref_integrity(work, proposal.get("source_refs", []))
    proposal_hash = _canonical_hash(proposal)
    if _passing_audit_for(work, args.proposal, proposal_hash) is None:
        sys.exit("Refused: author acceptance requires a passing audit record with answered findings for this proposal.")
    author_review = _author_review_for(work, args.proposal, proposal_hash)
    if author_review is None:
        sys.exit("Refused: author acceptance requires an author review packet. Run `tyf review <work> <proposal-id>` and show it to the author first.")
    if getattr(args, "lines", None) and getattr(args, "patch", None):
        sys.exit("Refused: choose either --lines or --patch for one author decision, not both.")
    accepted_patch = None
    if getattr(args, "patch", None):
        patch_rel = _require_patch_file(work, args.patch)
        dest = proposal["dest"].replace("/", os.sep)
        if _dest_base_hash(dest) != proposal.get("base_sha256"):
            sys.exit("Refused: manuscript base changed before patch acceptance. Re-propose from the current file.")
        base_text = _read(dest) if os.path.isfile(dest) else ""
        _apply_unified_patch(base_text, _read(patch_rel), proposal["unit"])
        accepted_ranges, accepted_scope = None, f"patch {patch_rel}"
        accepted_patch = {
            "path": patch_rel,
            "sha256": _file_sha256(patch_rel),
            "unit": proposal["unit"],
        }
    else:
        lines = _source_lines(src)
        accepted_ranges, accepted_scope = _parse_line_ranges(getattr(args, "lines", None), len(lines))
    decision_id = _record_id("decision", work, args.proposal, proposal["src_sha256"])
    decision = {
        "id": decision_id,
        "work": work,
        "proposal_id": args.proposal,
        "proposal_hash": proposal_hash,
        "src": proposal["src"],
        "dest": proposal["dest"],
        "src_sha256": proposal["src_sha256"],
        "base_sha256": proposal.get("base_sha256"),
        "source_refs": proposal.get("source_refs", []),
        "accepted_scope": accepted_scope,
        "accepted_ranges": accepted_ranges,
        "accepted_patch": accepted_patch,
        "author_review_id": author_review.get("id"),
        "author_review_packet": author_review.get("packet"),
        "accepted_by": _one_line(args.accepted_by, "author"),
        "acceptance_evidence": evidence,
        "decided_at": now(),
    }
    _write_review_record(work, "decisions", "decision", decision_id, decision)
    _set_work_status(work, "accepted")
    log_event(".", "accept", f"{work}/{decision_id}", f"proposal={args.proposal}")
    print(f"Decision: {decision_id}")
    print(f"  proposal: {args.proposal}")
    print(f"  accepted scope: {accepted_scope}")
    print("Next: `tyf write <work> --decision <decision-id>` after a passing audit.")

def cmd_adopt(args):
    _require_workspace()
    work = _safe_work_id(args.work)
    _confine_work(work)
    _require_work(work)
    unit = args.unit
    if os.path.basename(unit) != unit or unit in ("", ".", ".."):
        sys.exit("Refused: adopt names one manuscript filename, not a path.")
    evidence = _one_line(args.evidence)
    if not evidence:
        sys.exit("Refused: adopt requires --evidence explaining the direct author edit.")
    dest = _work_path(work, "manuscript", unit)
    _reject_symlink_components(dest, "manuscript unit")
    man = _work_path(work, "manuscript")
    if not _within(man, dest):
        sys.exit("Refused: manuscript unit resolves outside manuscript/.")
    if not os.path.isfile(dest):
        sys.exit(f"Refused: manuscript unit not found: {dest}")
    digest = hashlib.sha256(_read(dest).encode("utf-8")).hexdigest()
    revisions = _work_path(work, ".review", "author-revisions")
    _ensure_real_dir(revisions, "author revisions/")
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    revision = os.path.join(revisions, f"{stamp}-{unit}")
    shutil.copy2(dest, revision)
    log = _work_path(work, ".review", "write-log.md")
    append(log, f"\n## Author adoption {now()}\n- Adopted: {dest}\n- File: {unit}\n- sha256: {digest}\n- Evidence: {evidence}\n- Revision copy: {revision.replace(os.sep, '/')}\n")
    log_event(".", "adopt", f"{work}/{unit}", f"sha256={digest[:12]} evidence={evidence}")
    print(f"Adopted author edit: {dest}")
    print(f"  sha256: {digest}")
    print(f"  preserved copy: {revision}")
    print("Next: proposals against this manuscript base can proceed through audit, review, acceptance, and write.")

def cmd_write(args):
    _require_workspace()
    work = _safe_work_id(args.work)
    _confine_work(work)
    _require_work(work)
    if getattr(args, "confirm", False):
        sys.exit("Refused: naked --confirm is retired. Use `tyf propose`, `tyf audit --record`, `tyf review`, `tyf accept`, then `tyf write --decision <id>`.")
    if not args.decision:
        sys.exit("Refused: manuscript writes require an author decision record. Run `tyf propose`, `tyf audit --record`, `tyf review`, `tyf accept`, then `tyf write --decision <id>`.")
    if getattr(args, "force", False):
        sys.exit("Refused: --force is retired. Create a new proposal against the current manuscript base.")
    _require_work_status(work, "accepted", "controlled manuscript write")
    decision = _load_decision(work, args.decision)
    proposal = _load_proposal(work, decision["proposal_id"])
    proposal_hash = _canonical_hash(proposal)
    if decision.get("proposal_hash") != proposal_hash:
        sys.exit("Refused: decision no longer matches the proposal record.")
    author_review = _author_review_for(work, decision["proposal_id"], proposal_hash)
    if author_review is None:
        sys.exit("Refused: author review record is missing for this decision.")
    if (decision.get("author_review_id") != author_review.get("id")
            or decision.get("author_review_packet") != author_review.get("packet")):
        sys.exit("Refused: decision no longer matches the author review record.")
    src = decision["src"]
    if args.src and os.path.normpath(args.src) != os.path.normpath(src):
        sys.exit("Refused: --from does not match the accepted proposal source.")
    src = _require_draft_source(work, src)
    if _file_sha256(src) != decision.get("src_sha256"):
        sys.exit("Refused: accepted source changed after the author decision.")
    _require_source_ref_integrity(work, decision.get("source_refs", []))
    audit = _passing_audit_for(work, decision["proposal_id"], proposal_hash)
    if audit is None:
        sys.exit("Refused: no passing audit record with answered findings for this proposal.")
    man = _work_path(work, "manuscript")
    _ensure_real_dir(man, "manuscript/")
    dest = decision["dest"].replace("/", os.sep)
    _reject_symlink_components(dest, "manuscript destination")
    if not _within(man, dest):
        sys.exit(f"Refused: destination resolves outside manuscript/: {dest}")
    unit = os.path.basename(dest)
    lock_path = _acquire_unit_lock(work, unit)
    try:
        current_base = _dest_base_hash(dest)
        if current_base != decision.get("base_sha256"):
            sys.exit(f"Refused: manuscript base changed since acceptance for {dest}. Re-propose from the current file.")
        if os.path.isfile(dest):
            gl = _work_path(work, ".review", "write-log.md")
            rec = _logged_hashes(_read(gl)).get(unit)
            if rec is not None and hashlib.sha256(_read(dest).encode("utf-8")).hexdigest() != rec:
                sys.exit(f"Refused: {dest} changed since the last logged write (out-of-band edit). Run `tyf adopt {work} {unit} --evidence \"...\"` if this was the author's direct edit, or reconcile before rewriting.")
        if decision.get("accepted_patch"):
            patch = decision["accepted_patch"]
            patch_path = _require_patch_file(work, patch.get("path"))
            if _file_sha256(patch_path) != patch.get("sha256"):
                sys.exit("Refused: accepted patch changed after the author decision.")
            base_text = _read(dest) if os.path.isfile(dest) else ""
            content = _apply_unified_patch(base_text, _read(patch_path), patch.get("unit") or unit)
        else:
            content = _select_line_ranges(_source_lines(src), decision.get("accepted_ranges"))
        digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
        atomic_write(dest, content)
        log = _work_path(work, ".review", "write-log.md")
        append(log, f"\n## Write record {now()}\n- Applied: {src} -> {dest}\n- File: {os.path.basename(dest)}\n- sha256: {digest}\n- Proposal: {decision['proposal_id']}\n- Decision: {decision['id']}\n- Audit: {audit['id']}\n")
        append(log, f"- Accepted scope: {decision.get('accepted_scope', 'whole-file')}\n")
        if decision.get("source_refs"):
            append(log, "- Source refs: " + ", ".join(ref["id"] for ref in decision["source_refs"]) + "\n")
        _set_work_status(work, "written")
        log_event(".", "write", f"{work}/{os.path.basename(dest)}", f"{src} -> {dest} decision={decision['id']} sha256={digest[:12]}")
        print(f"Write: applied {src} into {dest}. Logged (with content hash) in {log}.")
    finally:
        _release_unit_lock(lock_path)

def _logged_hashes(log_text):
    """Map manuscript filename -> last recorded sha256 from a write-log."""
    latest, cur = {}, None
    for line in log_text.splitlines():
        s = line.strip()
        m = re.match(r"-\s*File:\s*(.+)$", s)
        if m:
            cur = m.group(1).strip(); continue
        m = re.match(r"-\s*sha256:\s*([0-9a-fA-F]+)", s)
        if m and cur:
            latest[cur] = m.group(1).strip()
    return latest


def _review_record_integrity_problems(work):
    problems = []
    _entries, seal_problems = _read_record_seals(work)
    problems.extend(seal_problems)
    for folder, kind in (("proposals", "proposal"), ("reviews", "review"), ("audits", "audit"), ("decisions", "decision")):
        d = _work_path(work, ".review", folder)
        if not os.path.isdir(d):
            continue
        for name in sorted(os.listdir(d)):
            if not name.endswith(".json"):
                continue
            record_id = os.path.splitext(name)[0]
            path = os.path.join(d, name)
            try:
                data = json.loads(_read(path))
            except json.JSONDecodeError as e:
                problems.append(f"{work}: invalid {kind} record {record_id}: {e}")
                continue
            if data.get("id") != record_id or data.get("work") != work:
                problems.append(f"{work}: {kind} record {record_id} has mismatched id or work")
                continue
            problem = _record_integrity_problem(work, kind, record_id, data)
            if problem and problem not in problems:
                problems.append(problem)
            problems.extend(_source_ref_problems(work, data.get("source_refs", [])))
            problems.extend(_accepted_patch_problems(work, data))
            problems.extend(_author_review_packet_problems(work, data))
    return problems


def _unit_lock_problems(work):
    problems = []
    d = _work_path(work, ".review", "locks")
    if os.path.islink(os.path.abspath(d)):
        return [f"{work}: review locks directory is a symlink; integrity cannot be verified"]
    if not os.path.isdir(d):
        return problems
    for name in sorted(os.listdir(d)):
        path = os.path.join(d, name)
        if not name.endswith(".lock.json"):
            continue
        unit = name[:-len(".lock.json")]
        try:
            data = json.loads(_read(path))
            unit = data.get("unit") or unit
        except json.JSONDecodeError as e:
            problems.append(f"{work}: invalid manuscript unit lock {name}: {e}")
        problems.append(f"{work}: manuscript unit lock outstanding: {unit}")
    return problems


def cmd_doctor(args):
    problems, notes = [], []
    if not os.path.isfile("WORKSPACE_STATE.yaml"):
        sys.exit("Not in a workspace root (no WORKSPACE_STATE.yaml).")
    # required structure: report anything missing (doctor --repair to create it)
    missing_created, _present = _scaffold(".", create=getattr(args, "repair", False))
    problems.extend(_event_journal_problems("."))
    if missing_created:
        if getattr(args, "repair", False):
            notes.append(f"repaired {len(missing_created)} missing structure item(s)")
            log_event(".", "repair", detail=", ".join(missing_created[:8]))
        else:
            for m in missing_created:
                problems.append(f"missing structure: {m} (run `tyf doctor --repair`)")
    # unsourced claims
    cl = "knowledge-base/claims.md"
    if os.path.isfile(cl):
        for ln in open(cl, encoding="utf-8"):
            if ln.strip().startswith("|") and "Claim id" not in ln and "---" not in ln:
                if "unsourced" in ln.lower():
                    problems.append(f"unsourced claim: {ln.strip()[:60]}")
    # root single-work checks
    if os.path.isfile("work.yaml"):
        work = ROOT_WORK_ID
        if not os.path.isfile("style-sheet.md"):
            problems.append(f"{work}: missing running style sheet")
        problems.extend(_review_record_integrity_problems(work))
        problems.extend(_unit_lock_problems(work))
        man = "manuscript"
        gl = os.path.join(".review", "write-log.md")
        man_files = [f for f in os.listdir(man)] if os.path.isdir(man) else []
        log_text = open(gl, encoding="utf-8").read() if os.path.isfile(gl) else ""
        if man_files and not os.path.isfile(gl):
            problems.append(f"{work}: manuscript has files but no write-log; uncontrolled write")
        else:
            logged = _logged_hashes(log_text)
            controlled = 0
            for f in man_files:
                if f not in log_text:
                    problems.append(f"{work}: manuscript file not recorded in write-log; possible uncontrolled write: {f}")
                    continue
                rec = logged.get(f)
                if rec is None:
                    problems.append(f"{work}: {f} recorded without a content hash (legacy write); integrity cannot be verified")
                    continue
                cur = hashlib.sha256(_read(os.path.join(man, f)).encode("utf-8")).hexdigest()
                if cur != rec:
                    problems.append(f"{work}: out-of-band edit detected in {f}; manuscript changed since the logged write (reconcile before the next write)")
                else:
                    controlled += 1
            if controlled:
                notes.append(f"{work}: {controlled} controlled manuscript file(s)")
    # compatibility work checks
    if os.path.isdir("works"):
        for w in sorted(os.listdir("works")):
            wd = os.path.join("works", w)
            if not os.path.isdir(wd):
                continue
            if not os.path.isfile(os.path.join(wd, "style-sheet.md")):
                problems.append(f"{w}: missing running style sheet")
            problems.extend(_review_record_integrity_problems(w))
            problems.extend(_unit_lock_problems(w))
            man = os.path.join(wd, "manuscript")
            gl = os.path.join(wd, ".review", "write-log.md")
            man_files = [f for f in os.listdir(man)] if os.path.isdir(man) else []
            log_text = open(gl, encoding="utf-8").read() if os.path.isfile(gl) else ""
            if man_files and not os.path.isfile(gl):
                problems.append(f"{w}: manuscript has files but no write-log; uncontrolled write")
            else:
                logged = _logged_hashes(log_text)
                controlled = 0
                for f in man_files:
                    if f not in log_text:
                        problems.append(f"{w}: manuscript file not recorded in write-log; possible uncontrolled write: {f}")
                        continue
                    rec = logged.get(f)
                    if rec is None:
                        problems.append(f"{w}: {f} recorded without a content hash (legacy write); integrity cannot be verified")
                        continue
                    cur = hashlib.sha256(_read(os.path.join(man, f)).encode("utf-8")).hexdigest()
                    if cur != rec:
                        problems.append(f"{w}: out-of-band edit detected in {f}; manuscript changed since the logged write (reconcile before the next write)")
                    else:
                        controlled += 1
                if controlled:
                    notes.append(f"{w}: {controlled} controlled manuscript file(s)")
    print("tyf doctor (read-only)")
    if problems:
        print("PROBLEMS:")
        for p in problems:
            print(f"  - {p}")
    else:
        print("  no problems found")
    for n in notes:
        print(f"  note: {n}")
    if problems:
        sys.exit(1)

def cmd_check(args):
    problems, notes = run_doc_check()
    _print_check(problems, notes, quiet=getattr(args, "quiet", False))
    if problems and getattr(args, "strict", True):
        sys.exit(1)

def cmd_notice(args):
    if not os.path.isfile("WORKSPACE_STATE.yaml"):
        sys.exit("Not in a workspace root (no WORKSPACE_STATE.yaml).")
    notices = gather_notices(".")
    # Update the ledger unless asked to peek without recording.
    new, still_open, resurfaced = reconcile_notices(".", notices, update=not getattr(args, "peek", False))
    print("tyf notice (the attentive amanuensis; surfaces only, never modifies)")

    show_all = getattr(args, "all", False)
    shown = (new + resurfaced + still_open) if show_all else (new + resurfaced)

    if not notices:
        print("  nothing outstanding; the work and its record look in step")
        return
    if not shown:
        print(f"  nothing new since last look ({len(still_open)} known item(s) still open;")
        print("  run `tyf notice --all` to see them, or `tyf reconcile`)")
        return

    if new:
        print(f"  new ({len(new)}):")
        for n in new:
            print(f"    - ({n['kind']}) {n['where']}: {n['message']}  [{n['content_hash']}]")
    if resurfaced:
        print(f"  resurfaced, context changed ({len(resurfaced)}):")
        for n in resurfaced:
            print(f"    - ({n['kind']}) {n['where']}: {n['message']}  [{n['content_hash']}]")
    if show_all and still_open:
        print(f"  still open ({len(still_open)}):")
        for n in still_open:
            print(f"    - ({n['kind']}) {n['where']}: {n['message']}  [{n['content_hash']}]")
    elif still_open:
        print(f"  ({len(still_open)} earlier item(s) still open; --all to show)")

    print("\n  Each item is yours to act on. Nothing here was changed for you.")
    print("  Dismiss one with `tyf dismiss <hash>`; a dismissed item returns only")
    print("  if its surrounding situation changes (for example a new contradiction).")
    if getattr(args, "save", False):
        path = _save_notices(".", shown)
        if path:
            print(f"  Saved a dated digest to {path}.")

def cmd_dismiss(args):
    if not os.path.isfile("WORKSPACE_STATE.yaml"):
        sys.exit("Not in a workspace root (no WORKSPACE_STATE.yaml).")
    if dismiss_notice(".", args.hash):
        print(f"Dismissed {args.hash}. It will not resurface unless its context changes.")
    else:
        print(f"No ledger item with hash {args.hash}. Run `tyf notice` to refresh hashes.")

def cmd_reconcile(args):
    if not os.path.isfile("WORKSPACE_STATE.yaml"):
        sys.exit("Not in a workspace root (no WORKSPACE_STATE.yaml).")
    items, events = ledger_summary(".")
    openi = {h: r for h, r in items.items() if r.get("status") == "open"}
    dismissed = {h: r for h, r in items.items() if r.get("status") == "dismissed"}
    print("tyf reconcile (the ledger of what was surfaced; you decide each)")
    if not items:
        print("  ledger empty; run `tyf notice` to populate it")
        return
    print(f"  {len(openi)} open, {len(dismissed)} dismissed, {len(items)} tracked, {events} events logged")
    for h, r in openi.items():
        print(f"  - [open] ({r['kind']}) {r.get('where','')}  [{h}]  first seen {r.get('first_seen','?')}")
    if getattr(args, "export", False):
        path = export_ledger_markdown(".")
        print(f"\n  Exported a readable mirror to {path}.")
    print("\n  Resolve an open item by editing the work (a removed item auto-resolves),")
    print("  or `tyf dismiss <hash>` to quiet it. Any change to the work still goes")
    print("  through `tyf write`; reconcile never modifies anything.")

# ---------- update notifier (notify-only; never modifies the pack) ----------
#
# Mirrors `tyf notice`: it surfaces that a newer release exists and hands the
# decision back. It never pulls, never runs remote code, never edits the pack.
# The actual update is the harness's job (`/plugin update tyf`, etc.). Throttled
# to once a day so it can be scheduled without hammering GitHub. The reference
# pack (obra/superpowers) updates the same way: native plugin-update + tags.

import urllib.request

_REPO_SLUG = "kosmopteros/tyf-authorship-apparatus"

def _version_tuple(s):
    """Loose semver tuple. Tolerant of a leading 'v' and stray text."""
    s = (s or "").strip().lstrip("vV")
    parts = []
    for p in s.split("."):
        digits = "".join(ch for ch in p if ch.isdigit())
        parts.append(int(digits) if digits else 0)
    return tuple(parts) or (0,)

def _installed_version():
    import json
    try:
        p = os.path.join(_pack_root(), ".claude-plugin", "plugin.json")
        with open(p, encoding="utf-8") as f:
            return json.load(f).get("version", "0.0.0")
    except Exception:  # noqa: BLE001  # degradation: ok: unreadable or absent plugin metadata reports the safe unknown version
        return "0.0.0"

def _latest_release_tag():
    """Latest release tag from GitHub, or None on any failure. TYF_LATEST_TAG
    overrides the network call (a test seam and an offline escape hatch)."""
    override = os.environ.get("TYF_LATEST_TAG")
    if override:
        return override.strip()
    import json
    try:
        url = f"https://api.github.com/repos/{_REPO_SLUG}/releases/latest"
        req = urllib.request.Request(url, headers={
            "Accept": "application/vnd.github+json", "User-Agent": "tyf-update-check"})
        with urllib.request.urlopen(req, timeout=5) as r:
            return json.load(r).get("tag_name")
    except Exception:  # noqa: BLE001  # degradation: ok: offline/update failures mean "no latest tag", not command failure
        return None

def _should_check(now_dt, last_dt, hours=24):
    if last_dt is None:
        return True
    return (now_dt - last_dt) >= datetime.timedelta(hours=hours)

def _update_cache_path():
    return os.environ.get("TYF_UPDATE_CACHE") or \
        os.path.join(os.path.expanduser("~"), ".tyf", "update-check.json")

def _read_update_cache():
    import json
    try:
        with open(_update_cache_path(), encoding="utf-8") as f:
            return json.load(f)
    except Exception:  # noqa: BLE001  # degradation: ok: missing/corrupt cache falls back to empty update state
        return {}

def _write_update_cache(data):
    import json
    p = _update_cache_path()
    try:
        os.makedirs(os.path.dirname(p) or ".", exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            json.dump(data, f)
    except Exception:  # noqa: BLE001  # degradation: ok: update cache writes are best-effort and must not fail checks
        pass  # the cache is best-effort and must never break a check

def _harness_update_hints():
    print("  Update through your harness (it owns the install):")
    print("    Claude Code : /plugin update tyf")
    print("    Gemini CLI  : gemini extensions update tyf")
    print("    others      : see UPDATING.md")

def cmd_update(args):
    installed = _installed_version()
    cache = _read_update_cache()
    last = None
    if cache.get("last_check"):
        try:
            last = datetime.datetime.strptime(cache["last_check"], "%Y-%m-%d %H:%M")
        except Exception:
            last = None
    if not getattr(args, "force", False) and not _should_check(datetime.datetime.now(), last):
        latest = cache.get("latest")
        print("tyf update (checked within the last day; --force to re-check)")
        if latest and _version_tuple(latest) > _version_tuple(installed):
            print(f"  TYF {latest} is available; you have {installed}.")
            _harness_update_hints()
        else:
            print(f"  TYF {installed} (no newer version recorded).")
        return
    latest = _latest_release_tag()
    if latest is None:
        print("tyf update (notify-only)")
        print("  Could not reach GitHub to check for a newer release.")
        print("  Update through your harness when ready; see UPDATING.md.")
        return
    cache.update({"last_check": now(), "latest": latest})
    _write_update_cache(cache)
    print("tyf update (notify-only; never modifies the pack)")
    if _version_tuple(latest) > _version_tuple(installed):
        print(f"  TYF {latest} is available; you have {installed}.")
        _harness_update_hints()
    else:
        print(f"  TYF is up to date ({installed}).")

def _doc_hook_tail():
    """Warn-only documentation-honesty check, run after a mutating command.

    Reliable trigger: wired into the command itself, not into git or author
    memory. Never blocks the action; only surfaces drift at the moment the
    structure changed. Silenced by TYF_NO_DOC_HOOK=1.
    """
    if os.environ.get("TYF_NO_DOC_HOOK") == "1":
        return
    if not os.path.isdir(os.path.join(_pack_root(), "skills")):
        return
    try:
        problems, _ = run_doc_check()
    except Exception as e:
        # A check failure must never break a real action, but it should not be
        # silent either, or a broken check becomes an invisible no-op.
        print(f"\n[doc-hook] check skipped (internal error: {e})")
        return  # a check failure must never break a real action
    if problems:
        print("\n[doc-hook] documentation drift detected (warn-only; run `tyf check`):")
        for p in problems[:8]:
            print(f"  - {p}")
        extra = len(problems) - 8
        if extra > 0:
            print(f"  ... and {extra} more")

def _git_hook_tail():
    """Surface git recovery state without staging or committing silently."""
    if os.environ.get("TYF_NO_DOC_HOOK") == "1":
        return
    if not os.path.isfile("WORKSPACE_STATE.yaml") or not _git_root():
        return
    status, err = _git_status_lines()
    if status is None:
        print(f"\n[git-hook] status unavailable ({err})")
        return
    if status:
        print(f"\n[git-hook] {len(status)} changed path(s) in this git workspace.")
        print("  Recovery point is explicit: run `tyf snapshot --message \"...\"`.")


def _command_requires_event_journal(args):
    cmd = getattr(args, "cmd", None)
    if cmd == "audit":
        return getattr(args, "record", False)
    return cmd in {
        "new-work", "start", "begin", "import", "capture", "structure", "character",
        "consult-character", "open", "mark-ready",
        "propose", "review", "accept", "adopt", "write", "snapshot", "dismiss",
    }


def _require_event_journal_ready(root="."):
    if not os.path.isfile(os.path.join(root, "WORKSPACE_STATE.yaml")):
        return
    problems = _event_journal_problems(root)
    if problems:
        first = problems[0]
        sys.exit("Refused: canonical event journal is not trustworthy; "
                 f"{first}. Run `tyf doctor` and reconcile before mutating the workspace.")


def main():
    p = argparse.ArgumentParser(prog="tyf", description="TYF workspace helper")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("init"); s.add_argument("name", nargs="?", default="."); s.add_argument("--force", action="store_true", help="scaffold even into a non-empty non-TYF directory"); s.set_defaults(fn=cmd_init)
    s = sub.add_parser("status"); s.set_defaults(fn=cmd_status)
    s = sub.add_parser("new-work"); s.add_argument("id"); s.add_argument("--type", default="book"); s.add_argument("--register", default=None); s.add_argument("--language", default=None); s.set_defaults(fn=cmd_new_work)
    s = sub.add_parser("start", help="open the writing runway, optionally preserving an arrival first")
    s.add_argument("path", nargs="?", help="optional chat, folder, old workspace, or zip to preserve before writing")
    s.add_argument("--kind", choices=("auto", "source", "chat", "bundle", "dump", "transcript", "note"), default="auto")
    s.add_argument("--work", default=None, help="existing work id; defaults to active work or creates an untitled work")
    s.add_argument("--title", default=None, help="working title to record on the active or newly created work")
    s.add_argument("--language", default=None, help="writing language label to record on the active or newly created work")
    s.set_defaults(fn=cmd_start)
    s = sub.add_parser("begin", help="create and open a first-session work packet")
    s.add_argument("id")
    s.add_argument("--type", default="book")
    s.add_argument("--register", default=None)
    s.add_argument("--title", default=None)
    s.add_argument("--language", default=None, help="writing language label, for example English, Portuguese, Russian, or Japanese")
    s.set_defaults(fn=cmd_begin)
    s = sub.add_parser("import", help="preserve existing material without writing manuscript text")
    s.add_argument("path")
    s.add_argument("--kind", choices=("auto", "source", "chat", "bundle", "dump", "transcript", "note"), default="auto")
    s.add_argument("--work", default=None, help="existing work id; defaults to active work or creates an untitled work")
    s.add_argument("--title", default=None, help="working title to record on the active or newly created work")
    s.add_argument("--language", default=None, help="writing language label to record on the active or newly created work")
    s.set_defaults(fn=cmd_import)
    s = sub.add_parser("capture", help="append author source, voice, claim, or question material")
    s.add_argument("work")
    s.add_argument("--kind", choices=sorted(_CAPTURE_TARGETS.keys()), required=True)
    s.add_argument("--title", default=None)
    s.add_argument("--text", required=True)
    s.set_defaults(fn=cmd_capture)
    s = sub.add_parser("structure", help="extract explicit claims, examples, and questions from source fragments")
    s.add_argument("work")
    s.add_argument("--source-ref", action="append", required=True,
                   help="source fragment id(s) to structure; repeat or comma-separate")
    s.set_defaults(fn=cmd_structure)
    s = sub.add_parser("character", help="append isolated per-character knowledge and voice dossier notes")
    s.add_argument("name")
    s.add_argument("--knowledge", default=None)
    s.add_argument("--voice", default=None)
    s.set_defaults(fn=cmd_character)
    s = sub.add_parser("consult-character", help="create a contained amanuensis packet for a character response")
    s.add_argument("work")
    s.add_argument("name")
    s.add_argument("--prompt", required=True)
    s.set_defaults(fn=cmd_consult_character)
    s = sub.add_parser("open"); s.add_argument("work"); s.set_defaults(fn=cmd_open)
    s = sub.add_parser("mark-ready"); s.add_argument("work"); s.add_argument("unit"); s.set_defaults(fn=cmd_mark_ready)
    s = sub.add_parser("propose", help="create a manuscript proposal from a draft")
    s.add_argument("work")
    s.add_argument("--from", dest="src", required=True)
    s.add_argument("--dest", default=None, help="optional manuscript filename; defaults to source basename")
    s.add_argument("--source-ref", dest="source_refs", action="append", default=[],
                   help="source fragment id(s) grounding this proposal; repeat or comma-separate")
    s.set_defaults(fn=cmd_propose)
    s = sub.add_parser("review", help="write an author-readable review packet for a proposal")
    s.add_argument("work")
    s.add_argument("proposal")
    s.set_defaults(fn=cmd_review)
    s = sub.add_parser("audit")
    s.add_argument("work")
    s.add_argument("unit")
    s.add_argument("--record", action="store_true", help="write a durable audit record instead of only printing the checklist")
    s.add_argument("--proposal", default=None, help="proposal id to bind this audit record to")
    s.add_argument("--verdict", choices=("pass", "fail"), default="fail")
    s.add_argument("--findings-answered", action="store_true", help="all blocking findings are fixed or explicitly dispositioned")
    s.set_defaults(fn=cmd_audit)
    s = sub.add_parser("accept", help="create an author decision record for a proposal")
    s.add_argument("work")
    s.add_argument("proposal")
    s.add_argument("--accepted-by", default="author")
    s.add_argument("--evidence", default=None, help="verbatim author acceptance text or a stable reference to it")
    s.add_argument("--lines", default=None, help="accepted source line ranges, for example 2,5-8; omit for whole file")
    s.add_argument("--patch", default=None, help="accepted unified diff under .review/; mutually exclusive with --lines")
    s.set_defaults(fn=cmd_accept)
    s = sub.add_parser("write")
    s.add_argument("work")
    s.add_argument("--decision", default=None)
    s.add_argument("--from", dest="src", default=None, help="legacy cross-check; source is taken from the decision record")
    s.add_argument("--confirm", action="store_true", help="retired; naked confirmation is refused")
    s.add_argument("--force", action="store_true", help="retired; create a new proposal against the current base")
    s.set_defaults(fn=cmd_write)
    s = sub.add_parser("adopt", help="adopt a direct author manuscript edit as the new recorded base")
    s.add_argument("work")
    s.add_argument("unit")
    s.add_argument("--evidence", required=True)
    s.set_defaults(fn=cmd_adopt)
    s = sub.add_parser("resume", help="show active work continuity and next useful move")
    s.add_argument("work", nargs="?")
    s.set_defaults(fn=cmd_resume)
    s = sub.add_parser("doctor"); s.add_argument("--repair", action="store_true", help="create any missing required structure"); s.set_defaults(fn=cmd_doctor)
    s = sub.add_parser("reflexes", help="show TYF's transparent hooks and reflexes")
    s.set_defaults(fn=cmd_reflexes)
    s = sub.add_parser("snapshot", help="stage and commit an explicit git recovery point")
    s.add_argument("--message", "-m", required=True)
    s.set_defaults(fn=cmd_snapshot)
    s = sub.add_parser("check")
    s.add_argument("--quiet", action="store_true", help="print only problems")
    s.add_argument("--strict", dest="strict", action="store_true", help="strict mode is the default")
    s.add_argument("--no-strict", dest="strict", action="store_false", help="warn only; exit 0 even on drift")
    s.set_defaults(fn=cmd_check, strict=True)
    s = sub.add_parser("notice", help="surface forgotten or unfinished items; never modifies")
    s.add_argument("--save", action="store_true", help="append a dated digest to .proposals/notices.md")
    s.add_argument("--all", action="store_true", help="include items already surfaced and still open")
    s.add_argument("--peek", action="store_true", help="show without updating the ledger")
    s.set_defaults(fn=cmd_notice)
    s = sub.add_parser("dismiss", help="quiet a surfaced item by its hash; resurfaces if context changes")
    s.add_argument("hash")
    s.set_defaults(fn=cmd_dismiss)
    s = sub.add_parser("reconcile", help="show the ledger of surfaced items")
    s.add_argument("--export", action="store_true", help="mirror the ledger to .proposals/ledger-mirror.md")
    s.set_defaults(fn=cmd_reconcile)
    s = sub.add_parser("update", help="check GitHub for a newer release; notify only, never modifies")
    s.add_argument("--force", action="store_true", help="ignore the once-a-day throttle and check now")
    s.set_defaults(fn=cmd_update)
    args = p.parse_args()
    if _command_requires_event_journal(args):
        _require_event_journal_ready(".")
    args.fn(args)
    # Documentation-honesty hook: mutating commands run the doc check warn-only.
    if getattr(args, "cmd", None) in {"init", "new-work", "start", "begin", "import", "capture", "propose", "review", "audit", "accept", "adopt", "write", "mark-ready"}:
        _doc_hook_tail()
        _git_hook_tail()
    # Attentive-amanuensis hook: after a manuscript write, surface a count of
    # only the NEW or resurfaced items (via the ledger), so the author is not
    # nagged about things already seen. Surfacing only; never modifies.
    # Silenced by TYF_NO_DOC_HOOK=1.
    if getattr(args, "cmd", None) == "write" and os.environ.get("TYF_NO_DOC_HOOK") != "1":
        try:
            new, _open, resurfaced = reconcile_notices(".", gather_notices("."), update=True)
        except Exception:
            new, resurfaced = [], []
        fresh = len(new) + len(resurfaced)
        if fresh:
            print(f"\n[amanuensis] {fresh} new item(s) to revisit; run `tyf notice`")

if __name__ == "__main__":
    main()
