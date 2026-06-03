#!/usr/bin/env python3
"""tyf: the TYF workspace helper.

The helper performs the concrete file operations of a TYF workspace so the agent
does not freelance, and it is the single writer into a work's manuscript/.

Commands:
  tyf init <name>                         scaffold a workspace (idempotent: creates
                                          only missing structure, never clobbers)
  tyf status                              active work, band, write control, write zones
  tyf new-work <id> [--type T] [--register R]
  tyf open <work-id>                      set active work; print what to load
  tyf mark-ready <work-id> <unit>         flag a unit for audit
  tyf audit <work-id> <unit>              print the audit checklist (no fix)
  tyf write <work-id> --from <draft> --confirm   ONLY writer into manuscript/
  tyf doctor [--repair]                   workspace integrity check; --repair creates
                                          any missing required structure
  tyf check [--strict] [--quiet]          documentation-honesty check on the pack
  tyf notice [--save] [--all] [--peek]    surface forgotten/unfinished/stale items;
                                          ledger-backed; never modifies
  tyf dismiss <hash>                      quiet a surfaced item; resurfaces on context change
  tyf reconcile [--export]                show the ledger; --export mirrors it to Markdown

Apparatus memory (SQLite, stdlib)
  The body of work stays in Markdown and YAML, owned by and legible to the
  author. Only machine bookkeeping lives in .tyf/ledger.db: the content-addressed
  notice ledger (statuses, dismissals, real timestamps) and an append-only event
  log (a git-like spine of init/write/mark-ready/dismiss/repair actions). It uses
  the stdlib sqlite3 module: no third-party dependencies. It is disposable derived
  state, rebuildable by re-scanning content, and mirrorable to Markdown with
  `tyf reconcile --export`. See docs/ATTENTIVENESS.md.

Documentation-honesty hook
  Every mutating command (init, new-work, write, mark-ready) runs `check` as a
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

# ---------- tiny tolerant reader for the flat YAML we generate ----------

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
                    data[container].append(s[2:].strip())
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
                    data[k] = v
                    container = None
            elif container is not None:
                if not isinstance(data.get(container), dict):
                    data[container] = {}
                data[container][k] = v
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

def append(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(text)

def mkdirs(*paths):
    for p in paths:
        os.makedirs(p, exist_ok=True)


def _require_workspace():
    """Refuse any mutating command run outside a TYF workspace root."""
    if not os.path.isfile("WORKSPACE_STATE.yaml"):
        sys.exit("Not in a TYF workspace (no WORKSPACE_STATE.yaml). "
                 "Run `tyf init <name>`, or cd into the workspace root.")


def _safe_work_id(work_id):
    """A work id is a simple slug, never a path. Reject separators, traversal,
    and absolute or home paths so a write can never escape works/."""
    if (not work_id or work_id in (".", "..")
            or os.path.isabs(work_id)
            or "/" in work_id or "\\" in work_id
            or work_id.startswith("~")):
        sys.exit(f"Refused: unsafe work id {work_id!r}. Use a simple name "
                 "(letters, digits, '-' or '_'); no slashes, '..', or absolute paths.")
    return work_id


def _within(base, target):
    """True if target resolves to inside base (real paths; symlink-safe)."""
    base = os.path.realpath(base)
    target = os.path.realpath(target)
    return target == base or target.startswith(base + os.sep)


def _confine_work(work):
    """Refuse a work whose path resolves outside works/ (e.g. a symlinked
    works/<id> or a mount). Defense in depth beyond the slug check."""
    base = os.path.realpath("works")
    target = os.path.realpath(os.path.join("works", work))
    if not (target == base or target.startswith(base + os.sep)):
        sys.exit(f"Refused: work {work!r} resolves outside works/ (symlink or mount escape).")

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
    for r, dirs, fs in os.walk(root):
        dirs[:] = [d for d in dirs if d != "__pycache__" and not d.startswith(".git")]
        for f in fs:
            if f.endswith(exts):
                yield os.path.join(r, f)

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
        t = open(p, encoding="utf-8").read()
        m = re.search(r"^name:\s*(.+)$", t, re.M)
        d = re.search(r"^description:\s*(.+)$", t, re.M)
        if not m or m.group(1).strip() != s:
            problems.append(f"{s}: frontmatter name does not match directory")
        if not d or not d.group(1).strip().lower().startswith("use when"):
            problems.append(f"{s}: description should start with 'Use when'")

    # 2. spelled-out and numeric skill counts across docs must equal n
    wrong_words = [w for i, w in enumerate(_NUMBER_WORDS, start=11) if i != n]
    for p in _iter_files(root, (".md", ".sh")):
        rel = os.path.relpath(p, root)
        for i, line in enumerate(open(p, encoding="utf-8"), 1):
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
        txt = open(p, encoding="utf-8").read()
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
        bodies = {open(c, encoding="utf-8").read() for c in present}
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
                _json.load(open(p, encoding="utf-8"))
            except Exception as e:
                problems.append(f"{j}: invalid JSON ({e})")

    # 6. no em-dash in prose except the canonical [AUTHOR: needed — what] token
    for p in _iter_files(root, (".md",)):
        rel = os.path.relpath(p, root)
        for i, line in enumerate(open(p, encoding="utf-8"), 1):
            if "\u2014" in line and "AUTHOR: needed" not in line:
                problems.append(f"{rel}:{i}: em-dash in prose")

    # 7. stale apparatus-memory path: the notice ledger is .tyf/ledger.db now,
    #    not the old .proposals/notice-ledger.json. (Exempt: VALIDATION.md
    #    changelog and this script, which name the old path as a search target.)
    for p in _iter_files(root, (".md", ".json", ".sh")):
        rel = os.path.relpath(p, root)
        if rel in _dead_ref_exempt:
            continue
        for i, line in enumerate(open(p, encoding="utf-8"), 1):
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
        for i, line in enumerate(open(p, encoding="utf-8"), 1):
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
    except OSError:
        return 0

def _read(path):
    try:
        return open(path, encoding="utf-8").read()
    except OSError:
        return ""

def _h(*parts):
    """Stable short hash of normalized content. Whitespace-insensitive so a
    reflow does not read as new content."""
    norm = " ".join(" ".join(p.split()) for p in parts if p)
    return hashlib.sha1(norm.encode("utf-8")).hexdigest()[:12]

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
            "content_hash": _h(kind, content),
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

def _db(root):
    os.makedirs(_tyf_dir(root), exist_ok=True)
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
    except Exception:
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
    conn = _db(root)
    cur = conn.cursor()
    rows = {r[0]: r for r in cur.execute(
        "SELECT content_hash, kind, where_ref, message, context_hash, status FROM notices")}
    new, still_open, resurfaced = [], [], []
    seen_now = set()

    # Dedupe within this run: the same content can appear in more than one place
    # (a gap in both a draft and its manuscript copy). Keep the first occurrence.
    deduped = []
    seen_hashes = set()
    for n in notices:
        if n["content_hash"] in seen_hashes:
            continue
        seen_hashes.add(n["content_hash"])
        deduped.append(n)

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
    files = {
        "WORKSPACE_STATE.yaml":
            "active_work: \nactive_band: section\nwrite_control:\n  compose: locked\n  revise: locked\nstatus: intake\n",
        "manifest.yaml":
            "voice_inheritance:\n  default: layer\nhooks:\n  - on: save_chapter\n    run: [ai-tell-scan, register-fence-check]\n  - on: open_chapter\n    run: [load-registers, load-style-sheet, load-chapter-review]\n  - on: mark_ready\n    run: [audit-ready-unit]\nself_extension:\n  anti_pattern_growth: true\n  writes_to: .proposals/\n",
        "ASSUMPTIONS.md": "# Assumptions\n\nUpdated as the author corrects them.\n\n- (none yet)\n",
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
        ".tyf/.gitignore": "# Apparatus memory: regenerable derived state.\n# Track it or not, your choice; it is not the body of work.\n",
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
    base = os.path.join("works", args.id)
    if os.path.exists(base):
        sys.exit(f"work already exists: {base}")
    mkdirs(os.path.join(base, "outline"), os.path.join(base, "drafts"),
           os.path.join(base, "manuscript"), os.path.join(base, ".review"))
    reg = args.register or "(elicit at least one register before composing)"
    write(os.path.join(base, "work.yaml"),
          f"id: {args.id}\ntype: {args.type}\nregisters:\n  - {reg}\nstatus: structuring\nscope:\n  knowledge: full\n  sources: full\noverrides:\n  voice: []\n")
    write(os.path.join(base, "style-sheet.md"),
          f"# Running style sheet: {args.id}\n\nThe Redactor's instrument. Every pass appends decisions here and reads before proposing.\n\n## Terminology decisions\n## Apparatus decisions\n## Finish decisions\n")
    write(os.path.join(base, ".review", "write-log.md"), f"# Write log: {args.id}\n\nThe only record of writes into manuscript/.\n")
    # set active work if none
    st = read_state("WORKSPACE_STATE.yaml")
    if not get(st, "active_work"):
        _set_active(args.id)
    print(f"Created work: {base} (type={args.type})")

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
    path = os.path.join("works", args.work, ".review", "ready.md")
    append(path, f"- {now()} unit READY for audit: {args.unit}\n")
    log_event(".", "mark-ready", f"{args.work}/{args.unit}")
    print(f"Marked ready: {args.work} / {args.unit}. Run `auditing-adversarially` before this is done.")

def cmd_audit(args):
    _require_workspace()
    args.work = _safe_work_id(args.work)
    print(f"Audit checklist for {args.work} / {args.unit} (read-only; write findings to .review/):")
    for item in ["frame-lock", "unsupported claims (check claims index)", "hidden assumptions",
                 "machine cadence", "register cross-talk", "citation integrity (verify via MCP)",
                 "terminology drift (vs style sheet)", "cross-references resolve",
                 "logical contradiction", "kept promises / composition"]:
        print(f"  [ ] {item}")
    print("Verdict PASSED only when every finding is answered: fixed, or accepted with reason.")

def cmd_write(args):
    _require_workspace()
    work = _safe_work_id(args.work)
    _confine_work(work)
    if not args.confirm:
        sys.exit("Refused. Writing to the manuscript requires explicit author acceptance: pass --confirm.")
    src = args.src
    if not src or not os.path.isfile(src):
        sys.exit(f"draft not found: {src}")
    drafts = os.path.join("works", work, "drafts")
    if not os.path.isdir(drafts):
        sys.exit(f"Refused: work {work!r} has no drafts/; the controlled write only promotes this work's own drafts.")
    if not _within(drafts, src):
        sys.exit(f"Refused: source must live under {drafts}{os.sep} (only this work's drafts may enter its manuscript). Got: {src}")
    man = os.path.join("works", work, "manuscript")
    mkdirs(man)
    dest = os.path.join(man, os.path.basename(src))
    if os.path.isfile(dest) and not getattr(args, "force", False):
        sys.exit(f"Refused: {dest} already exists. Re-writing manuscript text needs explicit --force (the prior version stays in the write log).")
    with open(src, encoding="utf-8") as f:
        content = f.read()
    digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
    write(dest, content)
    log = os.path.join("works", work, ".review", "write-log.md")
    forced = " --force" if getattr(args, "force", False) else ""
    append(log, f"\n## Write record {now()}\n- Applied: {src} -> {dest}\n- File: {os.path.basename(src)}\n- sha256: {digest}\n- Decision: accepted (--confirm{forced})\n")
    log_event(".", "write", f"{work}/{os.path.basename(src)}", f"{src} -> {dest} sha256={digest[:12]}")
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

def main():
    p = argparse.ArgumentParser(prog="tyf", description="TYF workspace helper")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("init"); s.add_argument("name"); s.add_argument("--force", action="store_true", help="scaffold even into a non-empty non-TYF directory"); s.set_defaults(fn=cmd_init)
    s = sub.add_parser("status"); s.set_defaults(fn=cmd_status)
    s = sub.add_parser("new-work"); s.add_argument("id"); s.add_argument("--type", default="book"); s.add_argument("--register", default=None); s.set_defaults(fn=cmd_new_work)
    s = sub.add_parser("open"); s.add_argument("work"); s.set_defaults(fn=cmd_open)
    s = sub.add_parser("mark-ready"); s.add_argument("work"); s.add_argument("unit"); s.set_defaults(fn=cmd_mark_ready)
    s = sub.add_parser("audit"); s.add_argument("work"); s.add_argument("unit"); s.set_defaults(fn=cmd_audit)
    s = sub.add_parser("write"); s.add_argument("work"); s.add_argument("--from", dest="src", required=True); s.add_argument("--confirm", action="store_true"); s.add_argument("--force", action="store_true", help="allow re-writing an existing manuscript file"); s.set_defaults(fn=cmd_write)
    s = sub.add_parser("doctor"); s.add_argument("--repair", action="store_true", help="create any missing required structure"); s.set_defaults(fn=cmd_doctor)
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
    args = p.parse_args()
    args.fn(args)
    # Documentation-honesty hook: mutating commands run the doc check warn-only.
    if getattr(args, "cmd", None) in {"init", "new-work", "write", "mark-ready"}:
        _doc_hook_tail()
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
