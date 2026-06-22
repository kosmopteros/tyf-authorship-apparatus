#!/usr/bin/env python3
"""tyf: the TYF workspace helper.

The helper performs the concrete file operations of a TYF workspace so the agent
does not freelance, and it is the single writer into a work's manuscript/.

Commands:
  tyf init <name>                         scaffold a workspace (idempotent: creates
                                          only missing structure, never clobbers)
  tyf status                              active work, band, write control, write zones
  tyf new-work <id> [--type T] [--register R]
  tyf start "Working Title" [--id work-id]
                                          writer-facing first book/session entrypoint
  tyf begin <id> [--title T] [--register R]
                                          create a first-session packet for a book
  tyf capture <work-id> --kind K --text TEXT
                                          append author source/voice/claim/question notes
  tyf open <work-id>                      set active work; print what to load
  tyf mark-ready <work-id> <unit>         flag a unit for audit
  tyf propose <work-id> --from <draft>    create a manuscript proposal record
  tyf audit <work-id> <unit>              print or record the audit checklist
  tyf accept <work-id> <proposal-id>      create an author decision record
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

Apparatus memory (SQLite, stdlib)
  The body of work stays in Markdown and YAML, owned by and legible to the
  author. Only machine bookkeeping lives in .tyf/ledger.db: the content-addressed
  notice ledger (statuses, dismissals, real timestamps) and an append-only event
  log (a git-like spine of apparatus actions). It uses
  the stdlib sqlite3 module: no third-party dependencies. It is disposable derived
  state, rebuildable by re-scanning content, and mirrorable to Markdown with
  `tyf reconcile --export`. See docs/ATTENTIVENESS.md.

Documentation-honesty hook
  Every mutating command (init, new-work, start, begin, capture, propose, audit --record, accept, write, mark-ready) runs `check` as a
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
import unicodedata
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
                 "Run `tyf init <name>`, or cd into the workspace root.")
    real = os.path.realpath(".")
    if os.path.abspath(".") != real:
        os.chdir(real)


def _safe_work_id(work_id):
    """A work id is a simple slug, never a path. Enforce a strict charset so a
    write can never escape works/ and the rule matches the error message."""
    if (not work_id or work_id in (".", "..")
            or os.path.isabs(work_id) or work_id.startswith("~")
            or not re.fullmatch(r"[A-Za-z0-9._-]+", work_id)):
        sys.exit(f"Refused: unsafe work id {work_id!r}. Use letters, digits, "
                 "'.', '-' or '_' only; no spaces, slashes, '..', or absolute paths.")
    return work_id


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
    """Refuse a work whose path resolves outside works/ (e.g. a symlinked
    works/<id> or a mount). Defense in depth beyond the slug check."""
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
    if not os.path.isfile(os.path.join("works", work, "work.yaml")):
        sys.exit(f"Refused: no work {work!r} (works/{work}/work.yaml not found). Create it with `tyf new-work`.")

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
_DEAD_COMMANDS = ["tyf gate", "--apply <draft>", "fire-devils-reader"]

def _pack_root():
    """The pack root. Honors TYF_PACK_ROOT (set this when the helper is installed
    or copied outside the repo); otherwise resolves from this script's real
    location (realpath, so a symlinked `tyf` on PATH still finds the repo)."""
    env = os.environ.get("TYF_PACK_ROOT")
    if env:
        return os.path.realpath(env)
    return os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

def _iter_files(root, exts):
    skip_dirs = {"__pycache__", ".git", ".fbs", ".claude", ".pytest_cache"}
    for r, dirs, fs in os.walk(root):
        dirs[:] = [d for d in dirs if d not in skip_dirs]
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
    _dead_ref_exempt = {"VALIDATION.md", os.path.join("scripts", "tyf.py")}
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

    # 4. the three context files must be byte-identical
    ctx = [os.path.join(root, f) for f in ("CLAUDE.md", "AGENTS.md", "GEMINI.md")]
    present = [c for c in ctx if os.path.isfile(c)]
    if len(present) == 3:
        bodies = {_read_pack_file(c) for c in present}
        if len(bodies) != 1:
            problems.append("CLAUDE.md / AGENTS.md / GEMINI.md have drifted apart")
        else:
            notes.append("context files identical")
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

    # AUTHOR-needed gap marks left in drafts or manuscript (forgotten to fill).
    # Context = the neighboring lines, so the same gap text in a new passage is
    # treated as a new situation (and a dismissed one resurfaces).
    for r, dirs, fs in os.walk(os.path.join(root, "works")):
        dirs[:] = [d for d in dirs if d != ".review"]
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
    for r, dirs, fs in os.walk(os.path.join(root, "works")):
        dirs[:] = [d for d in dirs if d != ".review"]
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
    if os.path.isdir(os.path.join(root, "works")):
        for w in sorted(os.listdir(os.path.join(root, "works"))):
            wd = os.path.join(root, "works", w)
            if not os.path.isdir(wd):
                continue
            ss = os.path.join(wd, "style-sheet.md")
            man = os.path.join(wd, "manuscript")
            if os.path.isdir(man) and os.path.isfile(ss):
                newest = max([_mtime(os.path.join(man, f)) for f in os.listdir(man)] or [0])
                if newest > _mtime(ss):
                    add("style-sheet-lag", f"works/{w}",
                        "manuscript changed after the style sheet; decisions may be unrecorded", w)

    # Assumptions left untouched while the manuscript moved (mtime hint only).
    asm = os.path.join(root, "ASSUMPTIONS.md")
    if os.path.isfile(asm) and os.path.isdir(os.path.join(root, "works")):
        newest_man = 0
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
# machine bookkeeping the author never hand-edits lives here: the notice ledger
# (hashes, statuses, dismissals), real timestamps from the system clock, and an
# append-only event log (a git-like spine of what the apparatus did). It is
# disposable derived state: it can be rebuilt by re-scanning content, and it can
# be mirrored to Markdown with `tyf reconcile --export`.

import sqlite3

def _tyf_dir(root):
    return os.path.join(root, ".tyf")

def _db_path(root):
    return os.path.join(_tyf_dir(root), "ledger.db")

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
        return {}, 0
    conn = _db(root)
    cur = conn.cursor()
    items = {}
    for r in cur.execute("""SELECT content_hash, kind, where_ref, status,
                            first_seen FROM notices"""):
        items[r[0]] = {"kind": r[1], "where": r[2], "status": r[3], "first_seen": r[4]}
    ev = cur.execute("SELECT COUNT(*) FROM events").fetchone()[0]
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
             "Read-only mirror of .tyf/ledger.db. The database is the source of truth.", ""]
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
        "sources/uploads", "sources/transcripts", "sources/interviews", "sources/notes",
        "knowledge-base/concepts", "knowledge-base/claims", "knowledge-base/examples",
        "knowledge-base/contradictions", "knowledge-base/open-questions",
        "voice/registers", "voice/exemplar-passages",
        "redactor-canon", "works", ".proposals", ".hooks", ".tyf",
    ]
    context_contract = """# TYF Workspace Instructions

This is an author-owned TYF workspace.

- If the author says "start my book" or gives a title, use `tyf start "<working title>"`.
- Keep source, interview notes, and candidate prose in `sources/`, `knowledge-base/`, `voice/`, and `works/*/drafts/`.
- Do not write manuscript prose directly. Manuscript writes must go through proposal, audit, author decision, and `tyf write --decision <id>`.
- Missing knowledge stays visible as `[AUTHOR: needed - what]`.
- Use `tyf notice --peek` for read-only inspection and `tyf snapshot --message "..."` only when the author wants an explicit git recovery point.
"""
    files = {
        "WORKSPACE_STATE.yaml":
            "active_work: \nactive_band: section\nwrite_control:\n  compose: locked\n  revise: locked\nstatus: intake\n",
        "manifest.yaml":
            "voice_inheritance:\n  default: layer\nhooks:\n  - on: save_chapter\n    run: [ai-tell-scan, register-fence-check]\n  - on: open_chapter\n    run: [load-registers, load-style-sheet, load-chapter-review]\n  - on: mark_ready\n    run: [audit-ready-unit]\nself_extension:\n  anti_pattern_growth: true\n  writes_to: .proposals/\n",
        "ASSUMPTIONS.md": "# Assumptions\n\nUpdated as the author corrects them.\n\n- (none yet)\n",
        "AGENTS.md": context_contract,
        "CLAUDE.md": context_contract,
        "GEMINI.md": context_contract,
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
        _db(root)  # initialize the SQLite ledger + event log if absent
    return created, present

def cmd_init(args):
    root = os.path.abspath(args.name)
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
        print("Next: run intake with `ingesting-sources` and `interviewing-the-author`, then `tyf new-work`.")

def cmd_new_work(args):
    _require_workspace()
    args.id = _safe_work_id(args.id)
    _confine_work(args.id)
    base, _reg = _create_work(args.id, args.type, args.register,
                              language=args.language, activate_if_none=True)
    log_event(".", "new-work", args.id, f"type={args.type} language={_one_line(args.language, 'undetermined')}")
    print(f"Created work: {base} (type={args.type}, language={_one_line(args.language, 'undetermined')})")

def _create_work(work_id, work_type="book", register=None, title=None,
                 language=None, activate_if_none=False, activate=False):
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
    title_line = f"title: {_yaml_scalar(title)}\n" if title else ""
    write(os.path.join(base, "work.yaml"),
          f"id: {work_id}\ntype: {_yaml_scalar(work_type)}\n{title_line}language: {_yaml_scalar(language)}\nregisters:\n  - {_yaml_scalar(reg)}\nstatus: structuring\nscope:\n  knowledge: full\n  sources: full\noverrides:\n  voice: []\n")
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

def _write_begin_packet(work_id, title=None, language=None):
    label = _one_line(title, work_id)
    language = _one_line(language, "undetermined")
    base = os.path.join("works", work_id)
    starter = os.path.join(base, "drafts", "00-start-here.md")
    seed = os.path.join(base, "outline", "seed.md")
    runway = os.path.join(base, ".review", "today.md")
    write(starter, f"""# Start here: {label}

This is an author-owned first-session packet. Fill it with source, images, fragments, objections, questions, and pressure. TYF may ask, organize, and propose, but it must not invent book content here. Do not invent what the author has not supplied.

Writing language: {language}

## What is already true

- [AUTHOR: needed - name the lived pressure, question, or image that makes this book necessary]

## Source fragments

- [AUTHOR: needed - paste notes, memories, observations, phrases, or cited material]

## Voice samples

- [AUTHOR: needed - lines that sound like the book, even if they are rough]

## Open questions

- [AUTHOR: needed - what must be elicited before drafting]

## Candidate draft target

- No manuscript text here yet. Candidate prose may be drafted later in `drafts/` only after source, register, and structure are present.
""")
    write(seed, f"""# Seed outline: {label}

## Working promise

- [AUTHOR: needed - what this book is trying to make thinkable or feelable]

## Central pressure

- [AUTHOR: needed - the tension, contradiction, wound, demand, or question]

## Source inventory

- [AUTHOR: needed - sources already available]
- [AUTHOR: needed - sources still missing]

## Possible first unit

- [AUTHOR: needed - scene, argument, vignette, letter, chapter, or fragment]
""")
    write(runway, f"""# First-session runway: {label}

Active work: `{work_id}`

## Today's loop

1. Fill `works/{work_id}/drafts/00-start-here.md` with the author's material.
2. Capture short source, voice, claim, or question notes with `tyf capture`.
3. Use `interviewing-the-author` to elicit what is still tacit.
4. Use `structuring-knowledge` to turn captured material into claims, gaps, and possible shape.
5. Draft candidates only in `works/{work_id}/drafts/`.
6. Run `tyf audit {work_id} <unit>` before treating a unit as ready.
7. Move text into `manuscript/` only after `tyf propose`, `tyf audit --record`, `tyf accept`, and `tyf write --decision`.

## Guardrails

- Beginning is source elicitation, not book generation.
- No silence counts as consent.
- Honor the work's writing language before applying prose conventions.
- Missing knowledge gets an `[AUTHOR: needed - what]` marker.
- The manuscript stays empty until an explicit controlled write.
""")
    return starter, seed, runway

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
    print("then draft candidates in drafts/ only. Manuscript writes require proposal, audit, decision, and `tyf write --decision`.")

def cmd_start(args):
    _require_workspace()
    title = _one_line(args.title)
    if not title:
        sys.exit("Refused: start needs the working title or plain name of the book.")
    work_id = _safe_work_id(args.id or _slugify_title(title))
    _confine_work(work_id)
    base, _reg = _create_work(work_id, args.type, args.register,
                              language=args.language,
                              title=title, activate=True)
    starter, seed, runway = _write_begin_packet(work_id, title, args.language)
    log_event(".", "start", work_id, f"starter={starter} language={_one_line(args.language, 'undetermined')}")
    print(f"I created the TYF workspace packet for {title!r}.")
    print(f"  Work id: {work_id}")
    print(f"  Writing language: {_one_line(args.language, 'undetermined')}")
    print(f"  Start here: {starter}")
    print(f"  Seed outline: {seed}")
    print(f"  Session runway: {runway}")
    print("No manuscript text was written.")
    print("Next, ask the author:")
    print("  1. What pressure, question, image, or wound makes this book necessary?")
    print("  2. What source material should we preserve before drafting?")
    print("  3. What lines or writers sound close to the desired voice?")
    print("Keep answers in the packet and drafts. Move text to manuscript only after explicit author acceptance.")

_CAPTURE_TARGETS = {
    "source": ("sources", "notes"),
    "voice": ("voice", "exemplar-passages"),
    "claim": ("knowledge-base", "claims"),
    "question": ("knowledge-base", "open-questions"),
}

def _capture_path(work_id, kind):
    return os.path.join(*_CAPTURE_TARGETS[kind], f"{work_id}.md")

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
    append(path, f"## {now()} - {title}\n\nWork: `{work_id}`\nKind: `{args.kind}`\n\n{text}\n\n")
    log_event(".", "capture", f"{work_id}/{args.kind}", path)
    print(f"Captured {args.kind} for {work_id}: {path}")
    print("Next: preserve source, structure knowledge, and keep candidates in drafts/.")

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
    wy = read_state(os.path.join("works", args.work, "work.yaml"))
    regs = get(wy, "registers", default=[])
    print(f"Active work: {args.work}")
    print(f"Load registers: {regs}")
    print(f"Load style sheet: works/{args.work}/style-sheet.md")
    rev = os.path.join("works", args.work, ".review")
    latest = sorted(os.listdir(rev)) if os.path.isdir(rev) else []
    print(f"Load latest .review: {latest[-3:] if latest else '(none)'}")
    print("Write zones: Compose -> drafts/  Propose/Audit -> .review/  Manuscript -> `tyf write` only")

def cmd_status(args):
    _require_workspace()
    st = read_state("WORKSPACE_STATE.yaml")
    print(f"active_work : {get(st,'active_work') or '(none)'}")
    print(f"active_band : {get(st,'active_band')}")
    print(f"status      : {get(st,'status')}")
    print(f"write.compose: {get(st,'write_control','compose')}")
    print(f"write.revise : {get(st,'write_control','revise')}")
    works = sorted(os.listdir("works")) if os.path.isdir("works") else []
    print(f"works       : {works or '(none)'}")
    print("write zones : Compose->drafts/  Propose/Audit->.review/  Manuscript-> `tyf write` only")

def cmd_mark_ready(args):
    _require_workspace()
    args.work = _safe_work_id(args.work)
    _confine_work(args.work)
    _require_work(args.work)
    path = os.path.join("works", args.work, ".review", "ready.md")
    append(path, f"- {now()} unit READY for audit: {args.unit}\n")
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
    return os.path.join("works", work, ".review", folder, record_id + ".json")


def _write_json(path, data):
    _reject_symlink_components(os.path.dirname(path), "review record directory")
    atomic_write(path, json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False) + "\n")


def _record_seal_path(work):
    _safe_work_id(work)
    _confine_work(work)
    _require_work(work)
    return os.path.join("works", work, ".review", "record-seals.jsonl")


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
    drafts = os.path.join("works", work, "drafts")
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
    audit_dir = os.path.join("works", work, ".review", "audits")
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
    man = os.path.join("works", work, "manuscript")
    _ensure_real_dir(man, "manuscript/")
    dest = os.path.join(man, dest_name)
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
    }
    _write_review_record(work, "proposals", "proposal", proposal_id, proposal)
    log_event(".", "propose", f"{work}/{proposal_id}", src)
    print(f"Proposal: {proposal_id}")
    print(f"  source: {proposal['src']}")
    print(f"  destination: {proposal['dest']}")
    print("Next: record an audit and author decision before writing.")


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
        audit_id = _record_id("audit", args.work, args.proposal, args.verdict)
        audit = {
            "id": audit_id,
            "work": args.work,
            "unit": args.unit,
            "proposal_id": args.proposal,
            "proposal_hash": proposal_hash,
            "verdict": args.verdict,
            "findings_answered": bool(getattr(args, "findings_answered", False)),
            "recorded_at": now(),
        }
        _write_review_record(args.work, "audits", "audit", audit_id, audit)
        log_event(".", "audit", f"{args.work}/{audit_id}", f"proposal={args.proposal} verdict={args.verdict}")
        print(f"Audit: {audit_id}")
        print(f"  verdict: {args.verdict}")
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
    src = proposal["src"]
    if _file_sha256(src) != proposal.get("src_sha256"):
        sys.exit("Refused: proposal source changed before acceptance.")
    lines = _source_lines(src)
    accepted_ranges, accepted_scope = _parse_line_ranges(getattr(args, "lines", None), len(lines))
    decision_id = _record_id("decision", work, args.proposal, proposal["src_sha256"])
    decision = {
        "id": decision_id,
        "work": work,
        "proposal_id": args.proposal,
        "proposal_hash": _canonical_hash(proposal),
        "src": proposal["src"],
        "dest": proposal["dest"],
        "src_sha256": proposal["src_sha256"],
        "base_sha256": proposal.get("base_sha256"),
        "accepted_scope": accepted_scope,
        "accepted_ranges": accepted_ranges,
        "accepted_by": _one_line(args.accepted_by, "author"),
        "acceptance_evidence": evidence,
        "decided_at": now(),
    }
    _write_review_record(work, "decisions", "decision", decision_id, decision)
    log_event(".", "accept", f"{work}/{decision_id}", f"proposal={args.proposal}")
    print(f"Decision: {decision_id}")
    print(f"  proposal: {args.proposal}")
    print(f"  accepted scope: {accepted_scope}")
    print("Next: `tyf write <work> --decision <decision-id>` after a passing audit.")

def cmd_write(args):
    _require_workspace()
    work = _safe_work_id(args.work)
    _confine_work(work)
    _require_work(work)
    if getattr(args, "confirm", False):
        sys.exit("Refused: naked --confirm is retired. Use `tyf propose`, `tyf audit --record`, `tyf accept`, then `tyf write --decision <id>`.")
    if not args.decision:
        sys.exit("Refused: manuscript writes require an author decision record. Run `tyf propose`, `tyf audit --record`, `tyf accept`, then `tyf write --decision <id>`.")
    if getattr(args, "force", False):
        sys.exit("Refused: --force is retired. Create a new proposal against the current manuscript base.")
    decision = _load_decision(work, args.decision)
    proposal = _load_proposal(work, decision["proposal_id"])
    proposal_hash = _canonical_hash(proposal)
    if decision.get("proposal_hash") != proposal_hash:
        sys.exit("Refused: decision no longer matches the proposal record.")
    src = decision["src"]
    if args.src and os.path.normpath(args.src) != os.path.normpath(src):
        sys.exit("Refused: --from does not match the accepted proposal source.")
    src = _require_draft_source(work, src)
    if _file_sha256(src) != decision.get("src_sha256"):
        sys.exit("Refused: accepted source changed after the author decision.")
    audit = _passing_audit_for(work, decision["proposal_id"], proposal_hash)
    if audit is None:
        sys.exit("Refused: no passing audit record with answered findings for this proposal.")
    man = os.path.join("works", work, "manuscript")
    _ensure_real_dir(man, "manuscript/")
    dest = decision["dest"].replace("/", os.sep)
    _reject_symlink_components(dest, "manuscript destination")
    if not _within(man, dest):
        sys.exit(f"Refused: destination resolves outside manuscript/: {dest}")
    current_base = _dest_base_hash(dest)
    if current_base != decision.get("base_sha256"):
        sys.exit(f"Refused: manuscript base changed since acceptance for {dest}. Re-propose from the current file.")
    if os.path.isfile(dest):
        gl = os.path.join("works", work, ".review", "write-log.md")
        rec = _logged_hashes(_read(gl)).get(os.path.basename(src))
        if rec is not None and hashlib.sha256(_read(dest).encode("utf-8")).hexdigest() != rec:
            sys.exit(f"Refused: {dest} changed since the last logged write (out-of-band edit). Run `tyf doctor` and reconcile before forcing a rewrite.")
    content = _select_line_ranges(_source_lines(src), decision.get("accepted_ranges"))
    digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
    atomic_write(dest, content)
    log = os.path.join("works", work, ".review", "write-log.md")
    append(log, f"\n## Write record {now()}\n- Applied: {src} -> {dest}\n- File: {os.path.basename(dest)}\n- sha256: {digest}\n- Proposal: {decision['proposal_id']}\n- Decision: {decision['id']}\n- Audit: {audit['id']}\n")
    append(log, f"- Accepted scope: {decision.get('accepted_scope', 'whole-file')}\n")
    log_event(".", "write", f"{work}/{os.path.basename(dest)}", f"{src} -> {dest} decision={decision['id']} sha256={digest[:12]}")
    print(f"Write: applied {src} into {dest}. Logged (with content hash) in {log}.")

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
    for folder, kind in (("proposals", "proposal"), ("audits", "audit"), ("decisions", "decision")):
        d = os.path.join("works", work, ".review", folder)
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
    return problems


def cmd_doctor(args):
    problems, notes = [], []
    if not os.path.isfile("WORKSPACE_STATE.yaml"):
        sys.exit("Not in a workspace root (no WORKSPACE_STATE.yaml).")
    # required structure: report anything missing (doctor --repair to create it)
    missing_created, _present = _scaffold(".", create=getattr(args, "repair", False))
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
    # per work checks
    if os.path.isdir("works"):
        for w in sorted(os.listdir("works")):
            wd = os.path.join("works", w)
            if not os.path.isdir(wd):
                continue
            if not os.path.isfile(os.path.join(wd, "style-sheet.md")):
                problems.append(f"{w}: missing running style sheet")
            problems.extend(_review_record_integrity_problems(w))
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

def main():
    p = argparse.ArgumentParser(prog="tyf", description="TYF workspace helper")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("init"); s.add_argument("name"); s.add_argument("--force", action="store_true", help="scaffold even into a non-empty non-TYF directory"); s.set_defaults(fn=cmd_init)
    s = sub.add_parser("status"); s.set_defaults(fn=cmd_status)
    s = sub.add_parser("new-work"); s.add_argument("id"); s.add_argument("--type", default="book"); s.add_argument("--register", default=None); s.add_argument("--language", default=None); s.set_defaults(fn=cmd_new_work)
    s = sub.add_parser("start", help="plain-language first book/session entrypoint")
    s.add_argument("title")
    s.add_argument("--id", default=None, help="optional stable work id; otherwise slugged from title")
    s.add_argument("--type", default="book")
    s.add_argument("--register", default=None)
    s.add_argument("--language", default=None, help="writing language label, for example English, Portuguese, Russian, or Japanese")
    s.set_defaults(fn=cmd_start)
    s = sub.add_parser("begin", help="create and open a first-session work packet")
    s.add_argument("id")
    s.add_argument("--type", default="book")
    s.add_argument("--register", default=None)
    s.add_argument("--title", default=None)
    s.add_argument("--language", default=None, help="writing language label, for example English, Portuguese, Russian, or Japanese")
    s.set_defaults(fn=cmd_begin)
    s = sub.add_parser("capture", help="append author source, voice, claim, or question material")
    s.add_argument("work")
    s.add_argument("--kind", choices=sorted(_CAPTURE_TARGETS.keys()), required=True)
    s.add_argument("--title", default=None)
    s.add_argument("--text", required=True)
    s.set_defaults(fn=cmd_capture)
    s = sub.add_parser("open"); s.add_argument("work"); s.set_defaults(fn=cmd_open)
    s = sub.add_parser("mark-ready"); s.add_argument("work"); s.add_argument("unit"); s.set_defaults(fn=cmd_mark_ready)
    s = sub.add_parser("propose", help="create a manuscript proposal from a draft")
    s.add_argument("work")
    s.add_argument("--from", dest="src", required=True)
    s.add_argument("--dest", default=None, help="optional manuscript filename; defaults to source basename")
    s.set_defaults(fn=cmd_propose)
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
    s.set_defaults(fn=cmd_accept)
    s = sub.add_parser("write")
    s.add_argument("work")
    s.add_argument("--decision", default=None)
    s.add_argument("--from", dest="src", default=None, help="legacy cross-check; source is taken from the decision record")
    s.add_argument("--confirm", action="store_true", help="retired; naked confirmation is refused")
    s.add_argument("--force", action="store_true", help="retired; create a new proposal against the current base")
    s.set_defaults(fn=cmd_write)
    s = sub.add_parser("doctor"); s.add_argument("--repair", action="store_true", help="create any missing required structure"); s.set_defaults(fn=cmd_doctor)
    s = sub.add_parser("reflexes", help="show TYF's transparent hooks and reflexes")
    s.set_defaults(fn=cmd_reflexes)
    s = sub.add_parser("snapshot", help="stage and commit an explicit git recovery point")
    s.add_argument("--message", "-m", required=True)
    s.set_defaults(fn=cmd_snapshot)
    s = sub.add_parser("check")
    s.add_argument("--quiet", action="store_true", help="print only problems")
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
    args.fn(args)
    # Documentation-honesty hook: mutating commands run the doc check warn-only.
    if getattr(args, "cmd", None) in {"init", "new-work", "start", "begin", "capture", "propose", "audit", "accept", "write", "mark-ready"}:
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
