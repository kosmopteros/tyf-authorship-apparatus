#!/usr/bin/env python3
"""Executable smoke tests for the tyf helper.

Zero third-party dependencies (stdlib unittest), to match the helper itself.
Run from the repo root:

    python tests/test_tyf.py -v
    # or
    python -m unittest tests.test_tyf -v

CLI behaviour is exercised through real subprocess calls so the tests see what
an author would. Pure functions (the doc-honesty check, pack-root resolution)
are imported and called directly.
"""

import os
import sys
import subprocess
import tempfile
import shutil
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
TYF = REPO / "scripts" / "tyf.py"
sys.path.insert(0, str(REPO / "scripts"))
import tyf  # noqa: E402

# Silence the doc-honesty + amanuensis tail hooks during CLI tests so output is
# about the command under test, not the surrounding pack.
ENV = {**os.environ, "TYF_NO_DOC_HOOK": "1"}


def run_tyf(args, cwd):
    """Invoke the real CLI. Returns (returncode, combined_output)."""
    p = subprocess.run(
        [sys.executable, str(TYF), *args],
        cwd=str(cwd), capture_output=True, text=True, env=ENV,
    )
    return p.returncode, (p.stdout + p.stderr)


def _can_symlink(tmp):
    """True if this platform/user can create directory symlinks."""
    try:
        target = tmp / "_symtgt"
        target.mkdir()
        link = tmp / "_symlnk"
        os.symlink(target, link, target_is_directory=True)
        link.unlink()
        target.rmdir()
        return True
    except (OSError, NotImplementedError, AttributeError):
        return False


class CLIBehaviour(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="tyf-test-"))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def ws(self):
        """Make and return an initialized workspace at <tmp>/ws."""
        rc, out = run_tyf(["init", "ws"], self.tmp)
        self.assertEqual(rc, 0, out)
        return self.tmp / "ws"

    def make_draft(self, ws, work="demo", name="ch1.md", text="Original line.\n"):
        d = ws / "works" / work / "drafts"
        d.mkdir(parents=True, exist_ok=True)
        (d / name).write_text(text, encoding="utf-8")
        return f"works/{work}/drafts/{name}"

    # ---- existing behaviour that must keep working (regression guards) ----

    def test_init_creates_and_is_idempotent(self):
        ws = self.ws()
        self.assertTrue((ws / "WORKSPACE_STATE.yaml").is_file())
        # Author edits a scaffolded file; re-init must heal, never clobber.
        (ws / "ASSUMPTIONS.md").write_text("CUSTOM CONTENT\n", encoding="utf-8")
        rc, out = run_tyf(["init", "ws"], self.tmp)
        self.assertEqual(rc, 0, out)
        self.assertEqual((ws / "ASSUMPTIONS.md").read_text(encoding="utf-8"),
                         "CUSTOM CONTENT\n")

    def test_write_refuses_without_confirm(self):
        ws = self.ws()
        run_tyf(["new-work", "demo"], ws)
        src = self.make_draft(ws)
        rc, out = run_tyf(["write", "demo", "--from", src], ws)
        self.assertNotEqual(rc, 0, "write without --confirm must refuse")
        self.assertFalse((ws / "works/demo/manuscript/ch1.md").exists())

    def test_write_with_confirm_copies_and_logs(self):
        ws = self.ws()
        run_tyf(["new-work", "demo"], ws)
        src = self.make_draft(ws)
        rc, out = run_tyf(["write", "demo", "--from", src, "--confirm"], ws)
        self.assertEqual(rc, 0, out)
        self.assertTrue((ws / "works/demo/manuscript/ch1.md").is_file())
        log = (ws / "works/demo/.review/write-log.md").read_text(encoding="utf-8")
        self.assertIn("ch1.md", log)

    def test_doctor_flags_unlogged_manuscript_file(self):
        ws = self.ws()
        run_tyf(["new-work", "demo"], ws)
        man = ws / "works/demo/manuscript"
        man.mkdir(parents=True, exist_ok=True)
        (man / "rogue.md").write_text("snuck in\n", encoding="utf-8")
        rc, out = run_tyf(["doctor"], ws)
        self.assertIn("rogue.md", out)
        self.assertRegex(out.lower(), r"uncontrolled|not recorded")

    # ---- P0 #3: mutating commands must require a workspace ----

    def test_new_work_requires_workspace(self):
        rc, out = run_tyf(["new-work", "demo"], self.tmp)  # no init here
        self.assertNotEqual(rc, 0, "new-work outside a workspace must refuse")
        self.assertFalse((self.tmp / "works").exists(),
                         "new-work must not create works/ outside a workspace")

    def test_write_requires_workspace(self):
        bare = self.tmp / "bare"
        (bare / "works/demo/drafts").mkdir(parents=True)
        (bare / "works/demo/drafts/ch1.md").write_text("x\n", encoding="utf-8")
        rc, out = run_tyf(
            ["write", "demo", "--from", "works/demo/drafts/ch1.md", "--confirm"], bare)
        self.assertNotEqual(rc, 0, "write outside a workspace must refuse")
        self.assertFalse((bare / "works/demo/manuscript").exists())

    # ---- P0 #4: work ids/paths must be sanitized and confined ----

    def test_new_work_rejects_absolute_id(self):
        ws = self.ws()
        pwn = self.tmp / "PWN"
        rc, out = run_tyf(["new-work", str(pwn)], ws)
        self.assertNotEqual(rc, 0, "absolute work id must be rejected")
        self.assertFalse((pwn / "work.yaml").exists(),
                         "absolute work id escaped the workspace")

    def test_new_work_rejects_parent_traversal(self):
        ws = self.ws()
        rc, out = run_tyf(["new-work", "../escape"], ws)
        self.assertNotEqual(rc, 0, "'..' in work id must be rejected")
        self.assertFalse((self.tmp / "escape").exists())
        self.assertFalse((ws / "escape").exists())

    def test_new_work_rejects_separator_in_id(self):
        ws = self.ws()
        rc, out = run_tyf(["new-work", "a/b"], ws)
        self.assertNotEqual(rc, 0, "path separators in a work id must be rejected")
        self.assertFalse((ws / "works/a/b").exists())

    def test_write_rejects_traversal_work(self):
        ws = self.ws()
        run_tyf(["new-work", "demo"], ws)
        src = self.make_draft(ws)
        rc, out = run_tyf(["write", "../../etc", "--from", src, "--confirm"], ws)
        self.assertNotEqual(rc, 0, "traversal in write work id must be rejected")

    # ---- P0 #5: controlled write integrity ----

    def test_write_rejects_source_outside_drafts(self):
        ws = self.ws()
        run_tyf(["new-work", "demo"], ws)
        (ws / "evil.md").write_text("not a draft\n", encoding="utf-8")
        rc, out = run_tyf(["write", "demo", "--from", "evil.md", "--confirm"], ws)
        self.assertNotEqual(rc, 0, "source outside the work's drafts/ must be rejected")
        self.assertFalse((ws / "works/demo/manuscript/evil.md").exists())

    def test_write_refuses_silent_overwrite(self):
        ws = self.ws()
        run_tyf(["new-work", "demo"], ws)
        src = self.make_draft(ws)
        rc, _ = run_tyf(["write", "demo", "--from", src, "--confirm"], ws)
        self.assertEqual(rc, 0)
        rc2, out2 = run_tyf(["write", "demo", "--from", src, "--confirm"], ws)
        self.assertNotEqual(rc2, 0, "overwriting an existing manuscript file needs --force")
        rc3, out3 = run_tyf(["write", "demo", "--from", src, "--confirm", "--force"], ws)
        self.assertEqual(rc3, 0, out3)

    # ---- P0 #6: doctor must detect out-of-band edits after a logged write ----

    def test_doctor_detects_out_of_band_edit(self):
        ws = self.ws()
        run_tyf(["new-work", "demo"], ws)
        src = self.make_draft(ws)
        rc, _ = run_tyf(["write", "demo", "--from", src, "--confirm"], ws)
        self.assertEqual(rc, 0)
        man_file = ws / "works/demo/manuscript/ch1.md"
        man_file.write_text(man_file.read_text(encoding="utf-8") + "SNUCK IN\n",
                            encoding="utf-8")
        rc, out = run_tyf(["doctor"], ws)
        self.assertIn("ch1.md", out)
        self.assertRegex(out.lower(), r"out-of-band|out of band|modified|hash")

    # ---- deeper-review holes: guards on the remaining commands ----

    def test_mark_ready_requires_workspace(self):
        rc, out = run_tyf(["mark-ready", "ghost", "u"], self.tmp)
        self.assertNotEqual(rc, 0, "mark-ready outside a workspace must refuse")
        self.assertFalse((self.tmp / "works").exists())

    def test_mark_ready_rejects_traversal(self):
        ws = self.ws()
        rc, out = run_tyf(["mark-ready", "../escape", "u"], ws)
        self.assertNotEqual(rc, 0, "traversal in mark-ready work id must be rejected")
        self.assertFalse((ws / "escape").exists())
        self.assertFalse((self.tmp / "escape").exists())

    def test_open_rejects_traversal(self):
        ws = self.ws()
        rc, out = run_tyf(["open", "../escape"], ws)
        self.assertNotEqual(rc, 0, "traversal in open work id must be rejected")

    def test_status_requires_workspace(self):
        rc, out = run_tyf(["status"], self.tmp)
        self.assertNotEqual(rc, 0, "status outside a workspace must refuse")

    def test_init_refuses_nonempty_foreign_dir(self):
        foreign = self.tmp / "foreign"
        foreign.mkdir()
        (foreign / "existing.txt").write_text("hi\n", encoding="utf-8")
        rc, out = run_tyf(["init", "."], foreign)
        self.assertNotEqual(rc, 0, "init into a non-empty non-TYF dir must refuse without --force")
        self.assertFalse((foreign / "WORKSPACE_STATE.yaml").exists())
        rc2, out2 = run_tyf(["init", ".", "--force"], foreign)
        self.assertEqual(rc2, 0, out2)
        self.assertTrue((foreign / "WORKSPACE_STATE.yaml").is_file())

    def test_write_refuses_symlinked_work_escape(self):
        ws = self.ws()
        if not _can_symlink(self.tmp):
            self.skipTest("platform/user cannot create symlinks")
        outside = self.tmp / "outside"
        (outside / "drafts").mkdir(parents=True)
        (outside / "drafts" / "c.md").write_text("x\n", encoding="utf-8")
        os.symlink(outside, ws / "works" / "evil", target_is_directory=True)
        rc, out = run_tyf(["write", "evil", "--from", "works/evil/drafts/c.md", "--confirm"], ws)
        self.assertNotEqual(rc, 0, "a write into a symlinked work escaping works/ must be refused")
        self.assertFalse((outside / "manuscript").exists())

    # ---- third review: --force must not clobber an out-of-band edit ----

    def test_write_force_refuses_out_of_band_edit(self):
        ws = self.ws()
        run_tyf(["new-work", "demo"], ws)
        src = self.make_draft(ws, name="ch.md", text="orig\n")
        self.assertEqual(run_tyf(["write", "demo", "--from", src, "--confirm"], ws)[0], 0)
        man = ws / "works/demo/manuscript/ch.md"
        man.write_text(man.read_text(encoding="utf-8") + "MANUAL\n", encoding="utf-8")
        (ws / "works/demo/drafts/ch.md").write_text("v2\n", encoding="utf-8")
        rc, out = run_tyf(["write", "demo", "--from", src, "--confirm", "--force"], ws)
        self.assertNotEqual(rc, 0, "--force must refuse to clobber an out-of-band edit")
        self.assertIn("MANUAL", man.read_text(encoding="utf-8"))

    def test_write_force_allows_clean_rewrite(self):
        ws = self.ws()
        run_tyf(["new-work", "demo"], ws)
        src = self.make_draft(ws, name="ch.md", text="orig\n")
        self.assertEqual(run_tyf(["write", "demo", "--from", src, "--confirm"], ws)[0], 0)
        (ws / "works/demo/drafts/ch.md").write_text("v2\n", encoding="utf-8")  # manuscript untouched
        rc, out = run_tyf(["write", "demo", "--from", src, "--confirm", "--force"], ws)
        self.assertEqual(rc, 0, out)
        self.assertEqual((ws / "works/demo/manuscript/ch.md").read_text(encoding="utf-8"), "v2\n")

    # ---- third review: commands must require the work to exist ----

    def test_mark_ready_requires_existing_work(self):
        ws = self.ws()
        rc, out = run_tyf(["mark-ready", "missing", "unit"], ws)
        self.assertNotEqual(rc, 0, "mark-ready on a nonexistent work must refuse")
        self.assertFalse((ws / "works/missing").exists())

    def test_open_requires_existing_work(self):
        ws = self.ws()
        rc, out = run_tyf(["open", "missing"], ws)
        self.assertNotEqual(rc, 0, "open on a nonexistent work must refuse")
        self.assertNotIn("active_work: missing",
                         (ws / "WORKSPACE_STATE.yaml").read_text(encoding="utf-8"))

    def test_audit_requires_existing_work(self):
        ws = self.ws()
        rc, out = run_tyf(["audit", "missing", "unit"], ws)
        self.assertNotEqual(rc, 0, "audit on a nonexistent work must refuse")

    def test_new_work_rejects_spaces_in_id(self):
        ws = self.ws()
        rc, out = run_tyf(["new-work", "a b"], ws)
        self.assertNotEqual(rc, 0, "a work id with a space must be rejected")


class DocCheck(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="tyf-pack-"))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def min_pack(self):
        """A minimal pack that run_doc_check considers clean."""
        root = self.tmp / "pack"
        sk = root / "skills" / "demo-skill"
        sk.mkdir(parents=True)
        (sk / "SKILL.md").write_text(
            "---\nname: demo-skill\ndescription: Use when demonstrating.\n---\n# Demo\n",
            encoding="utf-8")
        for c in ("CLAUDE.md", "AGENTS.md", "GEMINI.md"):
            (root / c).write_text("# Context\n\nIdentical body.\n", encoding="utf-8")
        return root

    # ---- regression: real repo and a minimal pack are clean ----

    def test_min_pack_is_clean(self):
        problems, _ = tyf.run_doc_check(str(self.min_pack()))
        self.assertEqual(problems, [], problems)

    def test_repo_pack_is_clean(self):
        problems, _ = tyf.run_doc_check(str(REPO))
        self.assertEqual(problems, [], problems)

    # ---- P1: check must catch the drift the external review found ----

    def test_check_flags_legacy_ledger_path(self):
        root = self.min_pack()
        (root / "README.md").write_text(
            "The ledger lives in `.proposals/notice-ledger.json`.\n", encoding="utf-8")
        problems, _ = tyf.run_doc_check(str(root))
        self.assertTrue(any("ledger" in p.lower() for p in problems),
                        f"expected a stale-ledger-path problem, got {problems}")

    def test_check_flags_role_terminology_drift(self):
        root = self.min_pack()
        (root / "README.md").write_text(
            "TYF is the interviewer, machinist, first reader, editor, and typographer.\n",
            encoding="utf-8")
        problems, _ = tyf.run_doc_check(str(root))
        self.assertTrue(any("terminolog" in p.lower() or "machinist" in p.lower()
                            or "typographer" in p.lower() for p in problems),
                        f"expected a terminology-drift problem, got {problems}")


class PackRoot(unittest.TestCase):
    def test_pack_root_env_override(self):
        d = Path(tempfile.mkdtemp(prefix="tyf-root-"))
        try:
            old = os.environ.get("TYF_PACK_ROOT")
            os.environ["TYF_PACK_ROOT"] = str(d)
            try:
                self.assertEqual(os.path.realpath(tyf._pack_root()),
                                 os.path.realpath(str(d)))
            finally:
                if old is None:
                    os.environ.pop("TYF_PACK_ROOT", None)
                else:
                    os.environ["TYF_PACK_ROOT"] = old
        finally:
            shutil.rmtree(d, ignore_errors=True)


class Installer(unittest.TestCase):
    @unittest.skipUnless(shutil.which("bash"), "bash not available")
    def test_bin_shim_runs_check(self):
        shim = REPO / "bin" / "tyf"
        self.assertTrue(shim.is_file(), "bin/tyf launcher should exist")
        # Invoke from the repo with a forward-slash relative path so bash gets a
        # clean argument on every platform (a Windows absolute path with
        # backslashes would be mangled by the shell).
        p = subprocess.run(["bash", "bin/tyf", "check"], cwd=str(REPO),
                           capture_output=True, text=True, env=ENV)
        out = p.stdout + p.stderr
        self.assertEqual(p.returncode, 0, out)
        self.assertIn("skill directories", out)


class UpdateCheck(unittest.TestCase):
    def test_version_tuple_compares(self):
        self.assertTrue(tyf._version_tuple("0.10.0") > tyf._version_tuple("0.9.0"))
        self.assertEqual(tyf._version_tuple("v0.2.0"), tyf._version_tuple("0.2.0"))
        self.assertTrue(tyf._version_tuple("1.0.0") > tyf._version_tuple("0.99.99"))

    def test_should_check_throttle(self):
        import datetime as dt
        now = dt.datetime(2026, 6, 3, 12, 0)
        self.assertTrue(tyf._should_check(now, None, 24))
        self.assertFalse(tyf._should_check(now, now - dt.timedelta(hours=1), 24))
        self.assertTrue(tyf._should_check(now, now - dt.timedelta(hours=30), 24))

    def test_update_reports_newer_version(self):
        tmp = Path(tempfile.mkdtemp(prefix="tyf-upd-"))
        try:
            env = {**ENV, "TYF_LATEST_TAG": "v99.0.0",
                   "TYF_UPDATE_CACHE": str(tmp / "cache.json")}
            p = subprocess.run([sys.executable, str(TYF), "update", "--force"],
                               cwd=str(REPO), capture_output=True, text=True, env=env)
            out = p.stdout + p.stderr
            self.assertEqual(p.returncode, 0, out)
            self.assertIn("99.0.0", out)
            self.assertRegex(out.lower(), r"available|update")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_update_reports_up_to_date(self):
        tmp = Path(tempfile.mkdtemp(prefix="tyf-upd-"))
        try:
            installed = tyf._installed_version()
            env = {**ENV, "TYF_LATEST_TAG": installed,
                   "TYF_UPDATE_CACHE": str(tmp / "cache.json")}
            p = subprocess.run([sys.executable, str(TYF), "update", "--force"],
                               cwd=str(REPO), capture_output=True, text=True, env=env)
            out = p.stdout + p.stderr
            self.assertEqual(p.returncode, 0, out)
            self.assertRegex(out.lower(), r"up to date|current|latest")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_update_never_writes_to_the_pack(self):
        # notify-only: a check must not modify any tracked pack file
        tmp = Path(tempfile.mkdtemp(prefix="tyf-upd-"))
        try:
            env = {**ENV, "TYF_LATEST_TAG": "v99.0.0",
                   "TYF_UPDATE_CACHE": str(tmp / "cache.json")}
            before = subprocess.run(["git", "status", "--porcelain"], cwd=str(REPO),
                                    capture_output=True, text=True).stdout
            subprocess.run([sys.executable, str(TYF), "update", "--force"],
                           cwd=str(REPO), capture_output=True, text=True, env=env)
            after = subprocess.run(["git", "status", "--porcelain"], cwd=str(REPO),
                                   capture_output=True, text=True).stdout
            self.assertEqual(before, after, "tyf update must not modify the pack")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
