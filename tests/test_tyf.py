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
import re
import json
import hashlib
import zipfile
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
        cwd=str(cwd), capture_output=True, text=True, encoding="utf-8",
        errors="replace", env=ENV,
    )
    return p.returncode, (p.stdout + p.stderr)


def event_record_hash(record):
    payload = {k: record[k] for k in sorted(record) if k != "hash"}
    data = json.dumps(payload, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"))
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


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

    def gate_decision(self, ws, work="demo", src=None, unit="ch1.md"):
        """Create a proposal, passing audit record, and author decision."""
        src = src or self.make_draft(ws, work=work, name=unit)
        rc, out = run_tyf(["propose", work, "--from", src], ws)
        self.assertEqual(rc, 0, out)
        m = re.search(r"Proposal:\s+(\S+)", out)
        self.assertIsNotNone(m, out)
        proposal = m.group(1)
        rc, out = run_tyf(
            ["audit", work, unit, "--record", "--proposal", proposal,
             "--verdict", "pass", "--findings-answered"], ws)
        self.assertEqual(rc, 0, out)
        rc, out = run_tyf(["accept", work, proposal, "--evidence", "author accepted this proposal"], ws)
        self.assertEqual(rc, 0, out)
        m = re.search(r"Decision:\s+(\S+)", out)
        self.assertIsNotNone(m, out)
        return m.group(1)

    def work_status(self, ws, work="demo"):
        return tyf.read_state(str(ws / "works" / work / "work.yaml")).get("status")

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

    def test_init_creates_single_work_root_layout(self):
        ws = self.ws()
        for path in ("work.yaml", "style-sheet.md", "outline", "drafts", "manuscript", ".review"):
            self.assertTrue((ws / path).exists(), f"{path} should live at the book folder root")
        self.assertFalse((ws / "works").exists(), "beta launch workspaces should not make authors manage works/<id>")
        state = (ws / "WORKSPACE_STATE.yaml").read_text(encoding="utf-8")
        self.assertIn("active_work: work", state)
        work_yaml = (ws / "work.yaml").read_text(encoding="utf-8")
        self.assertIn("id: work", work_yaml)
        self.assertIn('title_status: "unknown"', work_yaml)

    def test_init_creates_portable_workspace_marker(self):
        ws = self.ws()
        marker = json.loads((ws / "tyf.portable.json").read_text(encoding="utf-8"))
        self.assertEqual(marker["format"], "tyf-workspace")
        self.assertEqual(marker["format_version"], "0.5.0")
        self.assertEqual(marker["git"], "optional")
        self.assertTrue(marker["single_work"])
        self.assertIn("WORKSPACE_STATE.yaml", marker["canonical_text_state"])
        self.assertIn("work.yaml", marker["canonical_text_state"])
        self.assertIn("manifest.yaml", marker["canonical_text_state"])
        self.assertIn("sources/", marker["canonical_text_state"])
        self.assertIn("drafts/", marker["canonical_text_state"])
        self.assertIn("manuscript/", marker["canonical_text_state"])
        self.assertNotIn("works/", marker["canonical_text_state"])
        self.assertIn(".tyf/events.jsonl", marker["canonical_text_state"])
        self.assertIn(".tyf/ledger.db", marker["derived_disposable_state"])
        self.assertIn(".tyf/*.db-wal", marker["derived_disposable_state"])

    def test_beta_portable_marker_declares_single_work_bundle(self):
        self.test_init_creates_portable_workspace_marker()

    def test_write_refuses_without_decision(self):
        ws = self.ws()
        run_tyf(["new-work", "demo"], ws)
        src = self.make_draft(ws)
        rc, out = run_tyf(["write", "demo", "--from", src], ws)
        self.assertNotEqual(rc, 0, "write without a decision record must refuse")
        rc, out = run_tyf(["write", "demo", "--from", src, "--confirm"], ws)
        self.assertNotEqual(rc, 0, "naked --confirm must not be a manuscript gate")
        self.assertFalse((ws / "works/demo/manuscript/ch1.md").exists())

    def test_accept_requires_author_acceptance_evidence(self):
        ws = self.ws()
        run_tyf(["new-work", "demo"], ws)
        src = self.make_draft(ws)
        rc, out = run_tyf(["propose", "demo", "--from", src], ws)
        self.assertEqual(rc, 0, out)
        proposal = re.search(r"Proposal:\s+(\S+)", out).group(1)
        rc, out = run_tyf(["accept", "demo", proposal], ws)
        self.assertNotEqual(rc, 0, "acceptance without recorded author evidence must refuse")
        rc, out = run_tyf(
            ["audit", "demo", "ch1.md", "--record", "--proposal", proposal,
             "--verdict", "pass", "--findings-answered"], ws)
        self.assertEqual(rc, 0, out)
        rc, out = run_tyf(["accept", "demo", proposal, "--evidence", "Alexander: accept this file"], ws)
        self.assertEqual(rc, 0, out)

    def test_gate_updates_work_status_across_transitions(self):
        ws = self.ws()
        run_tyf(["new-work", "demo"], ws)
        self.assertEqual(self.work_status(ws), "structuring")
        src = self.make_draft(ws, name="chapter.md", text="draft\n")
        rc, out = run_tyf(["propose", "demo", "--from", src], ws)
        self.assertEqual(rc, 0, out)
        self.assertEqual(self.work_status(ws), "drafting")
        proposal = re.search(r"Proposal:\s+(\S+)", out).group(1)
        rc, out = run_tyf(
            ["audit", "demo", "chapter.md", "--record", "--proposal", proposal,
             "--verdict", "pass", "--findings-answered"], ws)
        self.assertEqual(rc, 0, out)
        self.assertEqual(self.work_status(ws), "audited")
        rc, out = run_tyf(
            ["accept", "demo", proposal, "--evidence", "Alexander: accept this"], ws)
        self.assertEqual(rc, 0, out)
        self.assertEqual(self.work_status(ws), "accepted")
        decision = re.search(r"Decision:\s+(\S+)", out).group(1)
        rc, out = run_tyf(["write", "demo", "--decision", decision], ws)
        self.assertEqual(rc, 0, out)
        self.assertEqual(self.work_status(ws), "written")

    def test_audit_record_writes_inspectable_editorial_note(self):
        ws = self.ws()
        (ws / "drafts" / "chapter.md").write_text("A candidate passage from preserved source.\n", encoding="utf-8")
        rc, out = run_tyf(["propose", "work", "--from", "drafts/chapter.md"], ws)
        self.assertEqual(rc, 0, out)
        proposal = re.search(r"Proposal:\s+(\S+)", out).group(1)

        rc, out = run_tyf(
            ["audit", "work", "chapter.md", "--record", "--proposal", proposal,
             "--verdict", "pass", "--findings-answered"], ws)
        self.assertEqual(rc, 0, out)
        audit = re.search(r"Audit:\s+(\S+)", out).group(1)
        note = ws / ".review" / "audits" / f"{audit}.md"
        self.assertTrue(note.is_file(), "audit --record should create a human-readable editorial note")
        text = note.read_text(encoding="utf-8")
        for label in ("Source fidelity", "Voice/register", "Unsupported claims", "Open gaps", "Findings", "Dispositions"):
            self.assertIn(label, text)
        record = json.loads((ws / ".review" / "audits" / f"{audit}.json").read_text(encoding="utf-8"))
        self.assertEqual(record.get("report"), f".review/audits/{audit}.md")

    def test_accept_refuses_before_passing_audit_state(self):
        ws = self.ws()
        run_tyf(["new-work", "demo"], ws)
        src = self.make_draft(ws)
        rc, out = run_tyf(["propose", "demo", "--from", src], ws)
        self.assertEqual(rc, 0, out)
        proposal = re.search(r"Proposal:\s+(\S+)", out).group(1)
        rc, out = run_tyf(
            ["accept", "demo", proposal, "--evidence", "Alexander: accept this"], ws)
        self.assertNotEqual(rc, 0, "author acceptance must not bypass the audit transition")
        self.assertRegex(out.lower(), r"audit|audited|state|status")
        self.assertEqual(self.work_status(ws), "drafting")

    def test_accept_refuses_after_failed_audit_state(self):
        ws = self.ws()
        run_tyf(["new-work", "demo"], ws)
        src = self.make_draft(ws)
        rc, out = run_tyf(["propose", "demo", "--from", src], ws)
        self.assertEqual(rc, 0, out)
        proposal = re.search(r"Proposal:\s+(\S+)", out).group(1)
        rc, out = run_tyf(
            ["audit", "demo", "ch1.md", "--record", "--proposal", proposal,
             "--verdict", "fail"], ws)
        self.assertEqual(rc, 0, out)
        self.assertEqual(self.work_status(ws), "needs-revision")
        rc, out = run_tyf(
            ["accept", "demo", proposal, "--evidence", "Alexander: accept this"], ws)
        self.assertNotEqual(rc, 0, "author acceptance must not bypass a failed audit")
        self.assertRegex(out.lower(), r"audited|needs-revision|state|status")

    def test_accept_requires_audit_for_the_same_proposal(self):
        ws = self.ws()
        run_tyf(["new-work", "demo"], ws)
        first_src = self.make_draft(ws, name="first.md", text="first\n")
        rc, out = run_tyf(["propose", "demo", "--from", first_src], ws)
        self.assertEqual(rc, 0, out)
        first_proposal = re.search(r"Proposal:\s+(\S+)", out).group(1)
        rc, out = run_tyf(
            ["audit", "demo", "first.md", "--record", "--proposal", first_proposal,
             "--verdict", "pass", "--findings-answered"], ws)
        self.assertEqual(rc, 0, out)
        self.assertEqual(self.work_status(ws), "audited")

        second_src = self.make_draft(ws, name="second.md", text="second\n")
        rc, out = run_tyf(["propose", "demo", "--from", second_src], ws)
        self.assertEqual(rc, 0, out)
        second_proposal = re.search(r"Proposal:\s+(\S+)", out).group(1)
        work_yaml = ws / "works/demo/work.yaml"
        work_yaml.write_text(work_yaml.read_text(encoding="utf-8").replace(
            "status: drafting", "status: audited"), encoding="utf-8")
        rc, out = run_tyf(
            ["accept", "demo", second_proposal,
             "--evidence", "Alexander: accept this second proposal"], ws)
        self.assertNotEqual(rc, 0, "acceptance must be bound to the proposal's own passing audit")
        self.assertRegex(out.lower(), r"audit|proposal|findings")

    def test_write_refuses_when_work_status_is_not_accepted(self):
        ws = self.ws()
        run_tyf(["new-work", "demo"], ws)
        src = self.make_draft(ws)
        decision = self.gate_decision(ws, src=src)
        work_yaml = ws / "works/demo/work.yaml"
        work_yaml.write_text(work_yaml.read_text(encoding="utf-8").replace(
            "status: accepted", "status: drafting"), encoding="utf-8")
        rc, out = run_tyf(["write", "demo", "--decision", decision], ws)
        self.assertNotEqual(rc, 0, "write must refuse when the work state is not accepted")
        self.assertRegex(out.lower(), r"status|state|accepted")
        self.assertFalse((ws / "works/demo/manuscript/ch1.md").exists())

    def test_write_with_decision_copies_and_logs(self):
        ws = self.ws()
        run_tyf(["new-work", "demo"], ws)
        src = self.make_draft(ws)
        decision = self.gate_decision(ws, src=src)
        rc, out = run_tyf(["write", "demo", "--decision", decision], ws)
        self.assertEqual(rc, 0, out)
        self.assertTrue((ws / "works/demo/manuscript/ch1.md").is_file())
        log = (ws / "works/demo/.review/write-log.md").read_text(encoding="utf-8")
        self.assertIn("ch1.md", log)
        self.assertIn(decision, log)

    def test_accept_line_ranges_writes_only_selected_lines(self):
        ws = self.ws()
        run_tyf(["new-work", "demo"], ws)
        src = self.make_draft(
            ws, name="chapter.md",
            text="keep opening\nreject this\nkeep middle\nkeep end\nreject tail\n",
        )
        rc, out = run_tyf(["propose", "demo", "--from", src], ws)
        self.assertEqual(rc, 0, out)
        proposal = re.search(r"Proposal:\s+(\S+)", out).group(1)
        rc, out = run_tyf(
            ["audit", "demo", "chapter.md", "--record", "--proposal", proposal,
             "--verdict", "pass", "--findings-answered"], ws)
        self.assertEqual(rc, 0, out)
        rc, out = run_tyf(
            ["accept", "demo", proposal, "--lines", "1,3-4",
             "--evidence", "Alexander: accept lines 1, 3, and 4"], ws)
        self.assertEqual(rc, 0, out)
        decision = re.search(r"Decision:\s+(\S+)", out).group(1)
        rc, out = run_tyf(["write", "demo", "--decision", decision], ws)
        self.assertEqual(rc, 0, out)
        manuscript = (ws / "works/demo/manuscript/chapter.md").read_text(encoding="utf-8")
        self.assertEqual(manuscript, "keep opening\nkeep middle\nkeep end\n")
        log = (ws / "works/demo/.review/write-log.md").read_text(encoding="utf-8")
        self.assertIn("Accepted scope: lines 1,3-4", log)

    def test_accept_line_ranges_refuses_invalid_or_out_of_range_selection(self):
        ws = self.ws()
        run_tyf(["new-work", "demo"], ws)
        src = self.make_draft(ws, name="chapter.md", text="one\ntwo\nthree\n")
        rc, out = run_tyf(["propose", "demo", "--from", src], ws)
        self.assertEqual(rc, 0, out)
        proposal = re.search(r"Proposal:\s+(\S+)", out).group(1)
        rc, out = run_tyf(
            ["audit", "demo", "chapter.md", "--record", "--proposal", proposal,
             "--verdict", "pass", "--findings-answered"], ws)
        self.assertEqual(rc, 0, out)
        rc, out = run_tyf(
            ["accept", "demo", proposal, "--lines", "2-1",
             "--evidence", "Alexander: accept this"], ws)
        self.assertNotEqual(rc, 0, "line ranges must be ascending")
        rc, out = run_tyf(
            ["accept", "demo", proposal, "--lines", "1,9",
             "--evidence", "Alexander: accept this"], ws)
        self.assertNotEqual(rc, 0, "line ranges must fit the proposal source")
        rc, out = run_tyf(
            ["accept", "demo", proposal, "--lines", "1,1-2",
             "--evidence", "Alexander: accept this"], ws)
        self.assertNotEqual(rc, 0, "line ranges must not overlap or duplicate text")
        rc, out = run_tyf(
            ["accept", "demo", proposal, "--lines", "3,2",
             "--evidence", "Alexander: accept this"], ws)
        self.assertNotEqual(rc, 0, "line ranges must preserve source order")

    def test_accept_patch_applies_exact_unified_diff_to_manuscript_base(self):
        ws = self.ws()
        run_tyf(["new-work", "demo"], ws)
        src = self.make_draft(ws, name="chapter.md", text="Alpha\nBeta\nGamma\n")
        first = self.gate_decision(ws, src=src, unit="chapter.md")
        self.assertEqual(run_tyf(["write", "demo", "--decision", first], ws)[0], 0)

        (ws / "works/demo/drafts/chapter.md").write_text(
            "Alpha\nBeta revised\nGamma\nDelta\n", encoding="utf-8")
        rc, out = run_tyf(["propose", "demo", "--from", src], ws)
        self.assertEqual(rc, 0, out)
        proposal = re.search(r"Proposal:\s+(\S+)", out).group(1)
        patches = ws / "works/demo/.review/patches"
        patches.mkdir(parents=True, exist_ok=True)
        patch_path = patches / "chapter.patch"
        patch_path.write_text(
            "--- a/chapter.md\n"
            "+++ b/chapter.md\n"
            "@@ -1,3 +1,4 @@\n"
            " Alpha\n"
            "-Beta\n"
            "+Beta revised\n"
            " Gamma\n"
            "+Delta\n",
            encoding="utf-8",
        )
        rc, out = run_tyf(
            ["audit", "demo", "chapter.md", "--record", "--proposal", proposal,
             "--verdict", "pass", "--findings-answered"], ws)
        self.assertEqual(rc, 0, out)
        rc, out = run_tyf(
            ["accept", "demo", proposal, "--patch", "works/demo/.review/patches/chapter.patch",
             "--evidence", "Alexander: accept this exact patch"], ws)
        self.assertEqual(rc, 0, out)
        decision = re.search(r"Decision:\s+(\S+)", out).group(1)
        decision_data = json.loads(
            (ws / "works/demo/.review/decisions" / f"{decision}.json").read_text(encoding="utf-8"))
        self.assertEqual(decision_data["accepted_scope"], "patch works/demo/.review/patches/chapter.patch")
        self.assertEqual(decision_data["accepted_patch"]["path"], "works/demo/.review/patches/chapter.patch")

        rc, out = run_tyf(["write", "demo", "--decision", decision], ws)
        self.assertEqual(rc, 0, out)
        manuscript = (ws / "works/demo/manuscript/chapter.md").read_text(encoding="utf-8")
        self.assertEqual(manuscript, "Alpha\nBeta revised\nGamma\nDelta\n")
        log = (ws / "works/demo/.review/write-log.md").read_text(encoding="utf-8")
        self.assertIn("Accepted scope: patch works/demo/.review/patches/chapter.patch", log)

    def test_accept_patch_refuses_mixed_line_scope(self):
        ws = self.ws()
        run_tyf(["new-work", "demo"], ws)
        src = self.make_draft(ws, name="chapter.md", text="one\ntwo\n")
        rc, out = run_tyf(["propose", "demo", "--from", src], ws)
        self.assertEqual(rc, 0, out)
        proposal = re.search(r"Proposal:\s+(\S+)", out).group(1)
        rc, out = run_tyf(
            ["audit", "demo", "chapter.md", "--record", "--proposal", proposal,
             "--verdict", "pass", "--findings-answered"], ws)
        self.assertEqual(rc, 0, out)
        patches = ws / "works/demo/.review/patches"
        patches.mkdir(parents=True, exist_ok=True)
        (patches / "chapter.patch").write_text(
            "--- a/chapter.md\n+++ b/chapter.md\n@@ -0,0 +1,1 @@\n+one\n",
            encoding="utf-8",
        )
        rc, out = run_tyf(
            ["accept", "demo", proposal, "--lines", "1",
             "--patch", "works/demo/.review/patches/chapter.patch",
             "--evidence", "Alexander: accept this"], ws)
        self.assertNotEqual(rc, 0, "patch acceptance and line-range acceptance must be mutually exclusive")
        self.assertRegex(out.lower(), r"patch|lines|exclusive|choose")

    def test_accept_patch_refuses_hunk_count_mismatch(self):
        ws = self.ws()
        run_tyf(["new-work", "demo"], ws)
        src = self.make_draft(ws, name="chapter.md", text="one\n")
        rc, out = run_tyf(["propose", "demo", "--from", src], ws)
        self.assertEqual(rc, 0, out)
        proposal = re.search(r"Proposal:\s+(\S+)", out).group(1)
        rc, out = run_tyf(
            ["audit", "demo", "chapter.md", "--record", "--proposal", proposal,
             "--verdict", "pass", "--findings-answered"], ws)
        self.assertEqual(rc, 0, out)
        patches = ws / "works/demo/.review/patches"
        patches.mkdir(parents=True, exist_ok=True)
        (patches / "chapter.patch").write_text(
            "--- a/chapter.md\n+++ b/chapter.md\n@@ -0,0 +1,3 @@\n+one\n",
            encoding="utf-8",
        )
        rc, out = run_tyf(
            ["accept", "demo", proposal, "--patch", "works/demo/.review/patches/chapter.patch",
             "--evidence", "Alexander: accept this exact patch"], ws)
        self.assertNotEqual(rc, 0, "patch acceptance must reject malformed hunk counts")
        self.assertRegex(out.lower(), r"hunk|count|patch")

    def test_write_refuses_tampered_accepted_patch_file(self):
        ws = self.ws()
        run_tyf(["new-work", "demo"], ws)
        src = self.make_draft(ws, name="chapter.md", text="Alpha\nBeta\n")
        first = self.gate_decision(ws, src=src, unit="chapter.md")
        self.assertEqual(run_tyf(["write", "demo", "--decision", first], ws)[0], 0)
        (ws / "works/demo/drafts/chapter.md").write_text("Alpha\nBeta revised\n", encoding="utf-8")
        rc, out = run_tyf(["propose", "demo", "--from", src], ws)
        self.assertEqual(rc, 0, out)
        proposal = re.search(r"Proposal:\s+(\S+)", out).group(1)
        patches = ws / "works/demo/.review/patches"
        patches.mkdir(parents=True, exist_ok=True)
        patch_path = patches / "chapter.patch"
        patch_path.write_text(
            "--- a/chapter.md\n+++ b/chapter.md\n@@ -1,2 +1,2 @@\n Alpha\n-Beta\n+Beta revised\n",
            encoding="utf-8",
        )
        rc, out = run_tyf(
            ["audit", "demo", "chapter.md", "--record", "--proposal", proposal,
             "--verdict", "pass", "--findings-answered"], ws)
        self.assertEqual(rc, 0, out)
        rc, out = run_tyf(
            ["accept", "demo", proposal, "--patch", "works/demo/.review/patches/chapter.patch",
             "--evidence", "Alexander: accept this patch"], ws)
        self.assertEqual(rc, 0, out)
        decision = re.search(r"Decision:\s+(\S+)", out).group(1)
        patch_path.write_text(
            "--- a/chapter.md\n+++ b/chapter.md\n@@ -1,2 +1,2 @@\n Alpha\n-Beta\n+Different edit\n",
            encoding="utf-8",
        )
        rc, out = run_tyf(["write", "demo", "--decision", decision], ws)
        self.assertNotEqual(rc, 0, "write must refuse a patch file changed after acceptance")
        self.assertRegex(out.lower(), r"patch|changed|hash|tamper")
        self.assertEqual((ws / "works/demo/manuscript/chapter.md").read_text(encoding="utf-8"),
                         "Alpha\nBeta\n")

    def test_doctor_flags_missing_accepted_patch_file(self):
        ws = self.ws()
        run_tyf(["new-work", "demo"], ws)
        src = self.make_draft(ws, name="chapter.md", text="Alpha\nBeta\n")
        first = self.gate_decision(ws, src=src, unit="chapter.md")
        self.assertEqual(run_tyf(["write", "demo", "--decision", first], ws)[0], 0)
        (ws / "works/demo/drafts/chapter.md").write_text("Alpha\nBeta revised\n", encoding="utf-8")
        rc, out = run_tyf(["propose", "demo", "--from", src], ws)
        self.assertEqual(rc, 0, out)
        proposal = re.search(r"Proposal:\s+(\S+)", out).group(1)
        patches = ws / "works/demo/.review/patches"
        patches.mkdir(parents=True, exist_ok=True)
        patch_path = patches / "chapter.patch"
        patch_path.write_text(
            "--- a/chapter.md\n+++ b/chapter.md\n@@ -1,2 +1,2 @@\n Alpha\n-Beta\n+Beta revised\n",
            encoding="utf-8",
        )
        rc, out = run_tyf(
            ["audit", "demo", "chapter.md", "--record", "--proposal", proposal,
             "--verdict", "pass", "--findings-answered"], ws)
        self.assertEqual(rc, 0, out)
        rc, out = run_tyf(
            ["accept", "demo", proposal, "--patch", "works/demo/.review/patches/chapter.patch",
             "--evidence", "Alexander: accept this patch"], ws)
        self.assertEqual(rc, 0, out)
        patch_path.unlink()
        rc, out = run_tyf(["doctor"], ws)
        self.assertNotEqual(rc, 0, "doctor must flag accepted patch files that vanish after the decision")
        self.assertRegex(out.lower(), r"patch|missing|integrity")

    def test_write_refuses_tampered_decision_record(self):
        ws = self.ws()
        run_tyf(["new-work", "demo"], ws)
        src = self.make_draft(
            ws, name="chapter.md",
            text="accepted line\nrejected line\n",
        )
        rc, out = run_tyf(["propose", "demo", "--from", src], ws)
        self.assertEqual(rc, 0, out)
        proposal = re.search(r"Proposal:\s+(\S+)", out).group(1)
        rc, out = run_tyf(
            ["audit", "demo", "chapter.md", "--record", "--proposal", proposal,
             "--verdict", "pass", "--findings-answered"], ws)
        self.assertEqual(rc, 0, out)
        rc, out = run_tyf(
            ["accept", "demo", proposal, "--lines", "1",
             "--evidence", "Alexander: accept only line 1"], ws)
        self.assertEqual(rc, 0, out)
        decision = re.search(r"Decision:\s+(\S+)", out).group(1)
        decision_path = ws / "works/demo/.review/decisions" / f"{decision}.json"
        data = json.loads(decision_path.read_text(encoding="utf-8"))
        data["accepted_ranges"] = None
        data["accepted_scope"] = "whole-file"
        decision_path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        rc, out = run_tyf(["write", "demo", "--decision", decision], ws)
        self.assertNotEqual(rc, 0, "tampered decision records must not write manuscript text")
        self.assertFalse((ws / "works/demo/manuscript/chapter.md").exists())

    def test_write_refuses_tampered_audit_record(self):
        ws = self.ws()
        run_tyf(["new-work", "demo"], ws)
        src = self.make_draft(ws, name="chapter.md", text="draft\n")
        rc, out = run_tyf(["propose", "demo", "--from", src], ws)
        self.assertEqual(rc, 0, out)
        proposal = re.search(r"Proposal:\s+(\S+)", out).group(1)
        rc, out = run_tyf(
            ["audit", "demo", "chapter.md", "--record", "--proposal", proposal,
             "--verdict", "pass", "--findings-answered"], ws)
        self.assertEqual(rc, 0, out)
        audit = re.search(r"Audit:\s+(\S+)", out).group(1)
        rc, out = run_tyf(
            ["accept", "demo", proposal, "--evidence", "Alexander: accept this"], ws)
        self.assertEqual(rc, 0, out)
        decision = re.search(r"Decision:\s+(\S+)", out).group(1)
        audit_path = ws / "works/demo/.review/audits" / f"{audit}.json"
        data = json.loads(audit_path.read_text(encoding="utf-8"))
        data["verdict"] = "fail"
        data["findings_answered"] = False
        audit_path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        rc, out = run_tyf(["write", "demo", "--decision", decision], ws)
        self.assertNotEqual(rc, 0, "tampered audit records must not satisfy the Gate")
        self.assertFalse((ws / "works/demo/manuscript/chapter.md").exists())

    def test_doctor_flags_tampered_gate_record(self):
        ws = self.ws()
        run_tyf(["new-work", "demo"], ws)
        src = self.make_draft(ws)
        decision = self.gate_decision(ws, src=src)
        decision_path = ws / "works/demo/.review/decisions" / f"{decision}.json"
        data = json.loads(decision_path.read_text(encoding="utf-8"))
        data["acceptance_evidence"] = "rewritten after the fact"
        decision_path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        rc, out = run_tyf(["doctor"], ws)
        self.assertNotEqual(rc, 0, "doctor must flag tampered Gate records")
        self.assertIn("decision", out.lower())
        self.assertRegex(out.lower(), r"tamper|seal|integrity")

    def test_doctor_flags_missing_gate_record_seal(self):
        ws = self.ws()
        run_tyf(["new-work", "demo"], ws)
        src = self.make_draft(ws)
        self.gate_decision(ws, src=src)
        (ws / "works/demo/.review/record-seals.jsonl").unlink()
        rc, out = run_tyf(["doctor"], ws)
        self.assertNotEqual(rc, 0, "doctor must flag unsealed Gate records")
        self.assertRegex(out.lower(), r"no seal|integrity")

    def test_doctor_flags_unlogged_manuscript_file(self):
        ws = self.ws()
        run_tyf(["new-work", "demo"], ws)
        man = ws / "works/demo/manuscript"
        man.mkdir(parents=True, exist_ok=True)
        (man / "rogue.md").write_text("snuck in\n", encoding="utf-8")
        rc, out = run_tyf(["doctor"], ws)
        self.assertIn("rogue.md", out)
        self.assertRegex(out.lower(), r"uncontrolled|not recorded")

    def test_write_refuses_existing_manuscript_unit_lock(self):
        ws = self.ws()
        run_tyf(["new-work", "demo"], ws)
        src = self.make_draft(ws)
        decision = self.gate_decision(ws, src=src)
        locks = ws / "works/demo/.review/locks"
        locks.mkdir(parents=True)
        (locks / "ch1.md.lock.json").write_text(
            '{"unit":"ch1.md","created_at":"test","pid":999999}\n',
            encoding="utf-8")
        rc, out = run_tyf(["write", "demo", "--decision", decision], ws)
        self.assertNotEqual(rc, 0, "write must refuse when a unit lock already exists")
        self.assertRegex(out.lower(), r"lock|locked")
        self.assertFalse((ws / "works/demo/manuscript/ch1.md").exists())

    def test_doctor_flags_manuscript_unit_lock(self):
        ws = self.ws()
        run_tyf(["new-work", "demo"], ws)
        locks = ws / "works/demo/.review/locks"
        locks.mkdir(parents=True)
        (locks / "chapter.md.lock.json").write_text(
            '{"unit":"chapter.md","created_at":"test","pid":999999}\n',
            encoding="utf-8")
        rc, out = run_tyf(["doctor"], ws)
        self.assertNotEqual(rc, 0, "doctor must surface outstanding unit locks")
        self.assertIn("chapter.md", out)
        self.assertRegex(out.lower(), r"lock|locked")

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

    def test_write_refuses_replaying_same_decision(self):
        ws = self.ws()
        run_tyf(["new-work", "demo"], ws)
        src = self.make_draft(ws)
        decision = self.gate_decision(ws, src=src)
        rc, _ = run_tyf(["write", "demo", "--decision", decision], ws)
        self.assertEqual(rc, 0)
        rc2, out2 = run_tyf(["write", "demo", "--decision", decision], ws)
        self.assertNotEqual(rc2, 0, "a decision must not be replayable after the base changes")

    # ---- P0 #6: doctor must detect out-of-band edits after a logged write ----

    def test_doctor_detects_out_of_band_edit(self):
        ws = self.ws()
        run_tyf(["new-work", "demo"], ws)
        src = self.make_draft(ws)
        decision = self.gate_decision(ws, src=src)
        rc, _ = run_tyf(["write", "demo", "--decision", decision], ws)
        self.assertEqual(rc, 0)
        man_file = ws / "works/demo/manuscript/ch1.md"
        man_file.write_text(man_file.read_text(encoding="utf-8") + "SNUCK IN\n",
                            encoding="utf-8")
        rc, out = run_tyf(["doctor"], ws)
        self.assertNotEqual(rc, 0)
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
        (ws / "works").mkdir()
        os.symlink(outside, ws / "works" / "evil", target_is_directory=True)
        rc, out = run_tyf(["write", "evil", "--from", "works/evil/drafts/c.md", "--confirm"], ws)
        self.assertNotEqual(rc, 0, "a write into a symlinked work escaping works/ must be refused")
        self.assertFalse((outside / "manuscript").exists())

    def test_new_work_refuses_symlinked_works_root_escape(self):
        ws = self.ws()
        if not _can_symlink(self.tmp):
            self.skipTest("platform/user cannot create symlinks")
        outside = self.tmp / "outside-works"
        outside.mkdir()
        os.symlink(outside, ws / "works", target_is_directory=True)
        rc, out = run_tyf(["new-work", "escape"], ws)
        self.assertNotEqual(rc, 0, "a symlinked works/ root must not relocate the workspace jail")
        self.assertFalse((outside / "escape").exists())

    def test_propose_refuses_symlinked_manuscript_escape(self):
        ws = self.ws()
        if not _can_symlink(self.tmp):
            self.skipTest("platform/user cannot create symlinks")
        run_tyf(["new-work", "demo"], ws)
        outside = self.tmp / "outside-manuscript"
        outside.mkdir()
        shutil.rmtree(ws / "works" / "demo" / "manuscript")
        os.symlink(outside, ws / "works" / "demo" / "manuscript", target_is_directory=True)
        src = self.make_draft(ws)
        rc, out = run_tyf(["propose", "demo", "--from", src], ws)
        self.assertNotEqual(rc, 0, "a symlinked manuscript/ must not receive a proposal or write")
        self.assertFalse((outside / "ch1.md").exists())

    # ---- third review: --force must not clobber an out-of-band edit ----

    def test_write_decision_refuses_out_of_band_edit_after_acceptance(self):
        ws = self.ws()
        run_tyf(["new-work", "demo"], ws)
        src = self.make_draft(ws, name="ch.md", text="orig\n")
        first = self.gate_decision(ws, src=src, unit="ch.md")
        self.assertEqual(run_tyf(["write", "demo", "--decision", first], ws)[0], 0)
        (ws / "works/demo/drafts/ch.md").write_text("v2\n", encoding="utf-8")
        decision = self.gate_decision(ws, src=src, unit="ch.md")
        man = ws / "works/demo/manuscript/ch.md"
        man.write_text(man.read_text(encoding="utf-8") + "MANUAL\n", encoding="utf-8")
        rc, out = run_tyf(["write", "demo", "--decision", decision], ws)
        self.assertNotEqual(rc, 0, "a decision bound to an older base must refuse manual edits")
        self.assertIn("MANUAL", man.read_text(encoding="utf-8"))

    def test_write_decision_allows_clean_rewrite_against_recorded_base(self):
        ws = self.ws()
        run_tyf(["new-work", "demo"], ws)
        src = self.make_draft(ws, name="ch.md", text="orig\n")
        first = self.gate_decision(ws, src=src, unit="ch.md")
        self.assertEqual(run_tyf(["write", "demo", "--decision", first], ws)[0], 0)
        (ws / "works/demo/drafts/ch.md").write_text("v2\n", encoding="utf-8")  # manuscript untouched
        decision = self.gate_decision(ws, src=src, unit="ch.md")
        rc, out = run_tyf(["write", "demo", "--decision", decision], ws)
        self.assertEqual(rc, 0, out)
        self.assertEqual((ws / "works/demo/manuscript/ch.md").read_text(encoding="utf-8"), "v2\n")

    def test_adopt_author_manuscript_edit_updates_base_for_next_decision(self):
        ws = self.ws()
        run_tyf(["new-work", "demo"], ws)
        src = self.make_draft(ws, name="ch.md", text="v1\n")
        first = self.gate_decision(ws, src=src, unit="ch.md")
        self.assertEqual(run_tyf(["write", "demo", "--decision", first], ws)[0], 0)

        man = ws / "works" / "demo" / "manuscript" / "ch.md"
        man.write_text("author direct edit\n", encoding="utf-8")
        self.make_draft(ws, name="ch.md", text="author direct edit\namanuensis continuation\n")
        second = self.gate_decision(ws, src="works/demo/drafts/ch.md", unit="ch.md")

        rc, out = run_tyf(["write", "demo", "--decision", second], ws)
        self.assertNotEqual(rc, 0, "direct author edits should require explicit adoption before the next write")
        self.assertRegex(out.lower(), r"out-of-band|adopt|reconcile|changed")

        rc, out = run_tyf(
            ["adopt", "demo", "ch.md", "--evidence", "Alexander edited the manuscript directly"], ws)
        self.assertEqual(rc, 0, out)
        self.assertIn("Adopted author edit", out)
        revisions = list((ws / "works" / "demo" / ".review" / "author-revisions").glob("*ch.md"))
        self.assertEqual(len(revisions), 1)
        self.assertIn("author direct edit", revisions[0].read_text(encoding="utf-8"))

        rc, out = run_tyf(["write", "demo", "--decision", second], ws)
        self.assertEqual(rc, 0, out)
        self.assertEqual(man.read_text(encoding="utf-8"), "author direct edit\namanuensis continuation\n")

    def test_resume_reports_active_work_state_and_next_useful_move(self):
        ws = self.ws()
        rc, out = run_tyf(["start"], ws)
        self.assertEqual(rc, 0, out)
        rc, out = run_tyf(["resume"], ws)
        self.assertEqual(rc, 0, out)
        self.assertIn("Active work: work", out)
        self.assertIn("title: unknown", out.lower())
        self.assertIn("status: structuring", out.lower())
        self.assertIn("Next useful move", out)
        self.assertIn("sources/interviews", out)

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

    # ---- first-day authorship lane: source first, manuscript by consent only ----

    def test_begin_creates_first_session_packet_without_manuscript_text(self):
        ws = self.ws()
        rc, out = run_tyf(
            ["begin", "new-book", "--title", "The New Book",
             "--register", "author-poetic-philosophical"], ws)
        self.assertEqual(rc, 0, out)
        base = ws / "works" / "new-book"
        starter_path = ws / "sources" / "interviews" / "new-book-first-session.md"
        self.assertTrue(starter_path.is_file())
        self.assertFalse((base / "drafts" / "00-start-here.md").exists(),
                         "first-session evidence belongs in sources/interviews, not drafts")
        self.assertTrue((base / "outline" / "seed.md").is_file())
        self.assertTrue((base / ".review" / "first-session.md").is_file())
        self.assertEqual(list((base / "manuscript").iterdir()), [],
                         "begin must not create manuscript text")
        self.assertIn("active_work: new-book",
                      (ws / "WORKSPACE_STATE.yaml").read_text(encoding="utf-8"))
        starter = starter_path.read_text(encoding="utf-8")
        self.assertIn("author-owned", starter)
        self.assertIn("do not invent", starter.lower())
        self.assertNotIn("[AUTHOR: needed", starter,
                         "fresh intake prompts should not be treated as overdue author gaps")
        self.assertIn("tyf capture", out)
        self.assertIn("tyf write", out)

    def test_begin_rejects_existing_work_without_overwriting_packet(self):
        ws = self.ws()
        rc, out = run_tyf(["begin", "new-book"], ws)
        self.assertEqual(rc, 0, out)
        starter = ws / "sources" / "interviews" / "new-book-first-session.md"
        starter.write_text("AUTHOR SEED\n", encoding="utf-8")
        rc, out = run_tyf(["begin", "new-book"], ws)
        self.assertNotEqual(rc, 0, "begin must not clobber an existing work")
        self.assertEqual(starter.read_text(encoding="utf-8"), "AUTHOR SEED\n")

    def test_capture_records_author_source_without_touching_manuscript(self):
        ws = self.ws()
        run_tyf(["begin", "new-book"], ws)
        rc, out = run_tyf(
            ["capture", "new-book", "--kind", "source", "--title", "opening pressure",
             "--text", "The book begins from a pressure I can feel but not name yet."], ws)
        self.assertEqual(rc, 0, out)
        note = ws / "sources" / "notes" / "new-book.md"
        self.assertTrue(note.is_file())
        text = note.read_text(encoding="utf-8")
        self.assertIn("opening pressure", text)
        self.assertIn("pressure I can feel", text)
        self.assertEqual(list((ws / "works" / "new-book" / "manuscript").iterdir()), [])

    def test_source_capture_fragment_survives_proposal_decision_and_write(self):
        ws = self.ws()
        run_tyf(["begin", "new-book"], ws)
        rc, out = run_tyf(
            ["capture", "new-book", "--kind", "source", "--title", "opening pressure",
             "--text", "The book begins from a pressure I can feel but not name yet."], ws)
        self.assertEqual(rc, 0, out)
        m = re.search(r"Source fragment:\s+(\S+)", out)
        self.assertIsNotNone(m, out)
        fragment = m.group(1)
        fragment_path = ws / "sources" / "fragments" / f"{fragment}.md"
        self.assertTrue(fragment_path.is_file(), "capture must preserve a stable fragment file")
        index = [json.loads(line) for line in
                 (ws / "sources" / "fragments.jsonl").read_text(encoding="utf-8").splitlines()
                 if line.strip()]
        self.assertEqual(index[-1]["id"], fragment)

        src = self.make_draft(
            ws, work="new-book", name="chapter.md",
            text="The pressure becomes an opening chapter.\n",
        )
        rc, out = run_tyf(["propose", "new-book", "--from", src, "--source-ref", fragment], ws)
        self.assertEqual(rc, 0, out)
        proposal = re.search(r"Proposal:\s+(\S+)", out).group(1)
        proposal_path = ws / "works/new-book/.review/proposals" / f"{proposal}.json"
        proposal_data = json.loads(proposal_path.read_text(encoding="utf-8"))
        self.assertEqual(proposal_data["source_refs"][0]["id"], fragment)

        rc, out = run_tyf(
            ["audit", "new-book", "chapter.md", "--record", "--proposal", proposal,
             "--verdict", "pass", "--findings-answered"], ws)
        self.assertEqual(rc, 0, out)
        rc, out = run_tyf(
            ["accept", "new-book", proposal,
             "--evidence", "Alexander: accept this source-grounded proposal"], ws)
        self.assertEqual(rc, 0, out)
        decision = re.search(r"Decision:\s+(\S+)", out).group(1)
        decision_path = ws / "works/new-book/.review/decisions" / f"{decision}.json"
        decision_data = json.loads(decision_path.read_text(encoding="utf-8"))
        self.assertEqual(decision_data["source_refs"][0]["id"], fragment)

        rc, out = run_tyf(["write", "new-book", "--decision", decision], ws)
        self.assertEqual(rc, 0, out)
        log = (ws / "works/new-book/.review/write-log.md").read_text(encoding="utf-8")
        self.assertIn(fragment, log)
        self.assertIn("Source refs", log)

    def test_source_fragments_are_workspace_owned_and_reusable_across_works(self):
        ws = self.ws()
        run_tyf(["begin", "book-one"], ws)
        rc, out = run_tyf(
            ["capture", "book-one", "--kind", "source", "--title", "shared memory",
             "--text", "This remembered image may belong in several works."], ws)
        self.assertEqual(rc, 0, out)
        fragment = re.search(r"Source fragment:\s+(\S+)", out).group(1)

        run_tyf(["begin", "book-two"], ws)
        src = self.make_draft(
            ws, work="book-two", name="chapter.md",
            text="The remembered image enters a different book.\n",
        )
        rc, out = run_tyf(["propose", "book-two", "--from", src, "--source-ref", fragment], ws)
        self.assertEqual(rc, 0, out)
        proposal = re.search(r"Proposal:\s+(\S+)", out).group(1)
        proposal_data = json.loads(
            (ws / "works/book-two/.review/proposals" / f"{proposal}.json").read_text(encoding="utf-8"))
        self.assertEqual(proposal_data["source_refs"][0]["id"], fragment)
        self.assertEqual(proposal_data["source_refs"][0]["origin_work"], "book-one")

    def test_propose_refuses_missing_or_tampered_source_fragment(self):
        ws = self.ws()
        run_tyf(["begin", "new-book"], ws)
        src = self.make_draft(ws, work="new-book", name="chapter.md", text="draft\n")
        rc, out = run_tyf(
            ["propose", "new-book", "--from", src, "--source-ref", "src-missing"], ws)
        self.assertNotEqual(rc, 0, "proposal must refuse unknown source refs")
        self.assertRegex(out.lower(), r"source fragment|provenance|missing")

        rc, out = run_tyf(
            ["capture", "new-book", "--kind", "source", "--title", "seed",
             "--text", "Original source text."], ws)
        self.assertEqual(rc, 0, out)
        m = re.search(r"Source fragment:\s+(\S+)", out)
        self.assertIsNotNone(m, out)
        fragment = m.group(1)
        fragment_path = ws / "sources" / "fragments" / f"{fragment}.md"
        fragment_path.write_text(
            fragment_path.read_text(encoding="utf-8").replace("Original source text.", "Changed source text."),
            encoding="utf-8")
        rc, out = run_tyf(["propose", "new-book", "--from", src, "--source-ref", fragment], ws)
        self.assertNotEqual(rc, 0, "proposal must refuse tampered source fragments")
        self.assertRegex(out.lower(), r"source fragment|provenance|hash|tamper")

    def test_propose_refuses_fragment_file_and_index_rewritten_under_same_id(self):
        ws = self.ws()
        run_tyf(["begin", "new-book"], ws)
        rc, out = run_tyf(
            ["capture", "new-book", "--kind", "source", "--title", "seed",
             "--text", "Original source text."], ws)
        self.assertEqual(rc, 0, out)
        fragment = re.search(r"Source fragment:\s+(\S+)", out).group(1)
        fragment_path = ws / "sources" / "fragments" / f"{fragment}.md"
        changed = "Changed source text."
        fragment_path.write_text(
            fragment_path.read_text(encoding="utf-8").replace("Original source text.", changed),
            encoding="utf-8")
        index_path = ws / "sources" / "fragments.jsonl"
        index = [json.loads(line) for line in index_path.read_text(encoding="utf-8").splitlines()
                 if line.strip()]
        index[-1]["text_sha256"] = hashlib.sha256(changed.encode("utf-8")).hexdigest()
        index_path.write_text(
            "\n".join(json.dumps(row, sort_keys=True) for row in index) + "\n",
            encoding="utf-8")
        src = self.make_draft(ws, work="new-book", name="chapter.md", text="draft\n")
        rc, out = run_tyf(["propose", "new-book", "--from", src, "--source-ref", fragment], ws)
        self.assertNotEqual(rc, 0, "proposal must refuse a source fragment rewritten under its old id")
        self.assertRegex(out.lower(), r"id|hash|source fragment|tamper")

    def test_write_and_doctor_refuse_tampered_source_fragment_after_decision(self):
        ws = self.ws()
        run_tyf(["begin", "new-book"], ws)
        rc, out = run_tyf(
            ["capture", "new-book", "--kind", "source", "--title", "seed",
             "--text", "Original source text."], ws)
        self.assertEqual(rc, 0, out)
        fragment = re.search(r"Source fragment:\s+(\S+)", out).group(1)
        src = self.make_draft(ws, work="new-book", name="chapter.md", text="draft\n")
        rc, out = run_tyf(["propose", "new-book", "--from", src, "--source-ref", fragment], ws)
        self.assertEqual(rc, 0, out)
        proposal = re.search(r"Proposal:\s+(\S+)", out).group(1)
        rc, out = run_tyf(
            ["audit", "new-book", "chapter.md", "--record", "--proposal", proposal,
             "--verdict", "pass", "--findings-answered"], ws)
        self.assertEqual(rc, 0, out)
        rc, out = run_tyf(
            ["accept", "new-book", proposal,
             "--evidence", "Alexander: accept this source-grounded proposal"], ws)
        self.assertEqual(rc, 0, out)
        decision = re.search(r"Decision:\s+(\S+)", out).group(1)

        fragment_path = ws / "sources" / "fragments" / f"{fragment}.md"
        fragment_path.write_text(
            fragment_path.read_text(encoding="utf-8").replace("Original source text.", "Changed source text."),
            encoding="utf-8")

        rc, out = run_tyf(["doctor"], ws)
        self.assertNotEqual(rc, 0, "doctor must flag source fragments changed after Gate records reference them")
        self.assertRegex(out.lower(), r"source fragment|hash|tamper")
        rc, out = run_tyf(["write", "new-book", "--decision", decision], ws)
        self.assertNotEqual(rc, 0, "write must refuse when accepted source provenance changed")
        self.assertFalse((ws / "works/new-book/manuscript/chapter.md").exists())

    def test_structure_source_fragment_builds_knowledge_and_amanuensis_brief(self):
        ws = self.ws()
        text = "\n".join([
            "Claim: Kinship is a weather system.",
            "Example: The aunt keeps a list of storms by name.",
            "Question: Which family member first taught the weather ritual?",
            "Loose image of rain on the kitchen window.",
        ])
        rc, out = run_tyf(
            ["capture", "work", "--kind", "source", "--title", "storm notes", "--text", text],
            ws)
        self.assertEqual(rc, 0, out)
        fragment = re.search(r"Source fragment:\s+(\S+)", out).group(1)

        rc, out = run_tyf(["structure", "work", "--source-ref", fragment], ws)
        self.assertEqual(rc, 0, out)
        self.assertIn("Claims: 1", out)
        self.assertIn("Examples: 1", out)
        self.assertIn("Open questions: 1", out)

        claims = (ws / "knowledge-base" / "claims.md").read_text(encoding="utf-8")
        self.assertRegex(claims, r"clm-[0-9a-f]{12}")
        self.assertIn("Kinship is a weather system.", claims)
        self.assertIn(fragment, claims)
        self.assertIn("source-backed", claims)

        examples = (ws / "knowledge-base" / "examples" / "work.md").read_text(encoding="utf-8")
        self.assertIn("The aunt keeps a list of storms by name.", examples)
        self.assertIn(fragment, examples)

        questions = (ws / "knowledge-base" / "open-questions" / "work.md").read_text(encoding="utf-8")
        self.assertIn("Which family member first taught the weather ritual?", questions)
        self.assertIn(fragment, questions)

        brief = (ws / ".review" / "amanuensis-brief.md").read_text(encoding="utf-8")
        self.assertIn("Source fragments", brief)
        self.assertIn(fragment, brief)
        self.assertIn("Claims extracted: 1", brief)
        self.assertIn("Gentle questions for the author", brief)
        self.assertIn("These are nudges of attention, not doubts in the author's judgment.", brief)
        self.assertIn("Loose image of rain on the kitchen window.", brief)
        self.assertEqual(list((ws / "manuscript").iterdir()), [])

    def test_structure_source_fragment_is_idempotent(self):
        ws = self.ws()
        text = "\n".join([
            "Claim: A room can remember an argument.",
            "Example: The chair remains turned toward the door.",
            "Question: Who moved the chair?",
        ])
        rc, out = run_tyf(
            ["capture", "work", "--kind", "source", "--title", "room note", "--text", text],
            ws)
        self.assertEqual(rc, 0, out)
        fragment = re.search(r"Source fragment:\s+(\S+)", out).group(1)
        for _ in range(2):
            rc, out = run_tyf(["structure", "work", "--source-ref", fragment], ws)
            self.assertEqual(rc, 0, out)

        claims = (ws / "knowledge-base" / "claims.md").read_text(encoding="utf-8")
        examples = (ws / "knowledge-base" / "examples" / "work.md").read_text(encoding="utf-8")
        questions = (ws / "knowledge-base" / "open-questions" / "work.md").read_text(encoding="utf-8")
        self.assertEqual(claims.count("A room can remember an argument."), 1)
        self.assertEqual(examples.count("The chair remains turned toward the door."), 1)
        self.assertEqual(questions.count("Who moved the chair?"), 1)

    def test_structure_refuses_tampered_source_fragment(self):
        ws = self.ws()
        rc, out = run_tyf(
            ["capture", "work", "--kind", "source", "--title", "seed",
             "--text", "Claim: The first image is true."], ws)
        self.assertEqual(rc, 0, out)
        fragment = re.search(r"Source fragment:\s+(\S+)", out).group(1)
        fragment_path = ws / "sources" / "fragments" / f"{fragment}.md"
        fragment_path.write_text(
            fragment_path.read_text(encoding="utf-8").replace("first image", "second image"),
            encoding="utf-8")

        rc, out = run_tyf(["structure", "work", "--source-ref", fragment], ws)
        self.assertNotEqual(rc, 0, "structure must refuse changed source fragments")
        self.assertRegex(out.lower(), r"source fragment|hash|tamper")
        claims = (ws / "knowledge-base" / "claims.md").read_text(encoding="utf-8")
        self.assertNotIn("second image", claims)

    def test_import_text_orientation_points_to_structure_pass(self):
        ws = self.ws()
        chat = self.tmp / "arrival-chat.txt"
        chat.write_text("Claim: The family archive begins with a silence.\n", encoding="utf-8")
        rc, out = run_tyf(["import", str(chat), "--kind", "chat"], ws)
        self.assertEqual(rc, 0, out)
        fragment = re.search(r"Source fragment:\s+(\S+)", out).group(1)
        orientation = "\n".join(
            p.read_text(encoding="utf-8")
            for p in (ws / "sources" / "imports").glob("*orientation.md")
        )
        self.assertIn(f"tyf structure work --source-ref {fragment}", orientation)

    def test_character_dossier_and_consultation_stay_contained(self):
        ws = self.ws()
        rc, out = run_tyf(
            ["character", "Mark",
             "--knowledge", "Mark knows the archive was locked before winter.",
             "--voice", "short, dry, protective"], ws)
        self.assertEqual(rc, 0, out)
        self.assertTrue((ws / "knowledge-base" / "characters" / "mark.md").is_file())
        self.assertTrue((ws / "voice" / "characters" / "mark.md").is_file())

        rc, out = run_tyf(
            ["consult-character", "work", "Mark",
             "--prompt", "What would Mark say in response to the opened archive?"], ws)
        self.assertEqual(rc, 0, out)
        self.assertIn("Character consultation", out)
        consults = list((ws / ".review" / "character-consults").glob("mark-*.md"))
        self.assertEqual(len(consults), 1)
        packet = consults[0].read_text(encoding="utf-8")
        self.assertIn("hidden amanuensis machinery", packet)
        self.assertIn("candidate dramatic insight", packet)
        self.assertIn("not evidence", packet)
        self.assertIn("not manuscript", packet)
        self.assertIn("Ground only in this character dossier", packet)
        self.assertIn("Mark knows the archive was locked before winter.", packet)
        self.assertIn("short, dry, protective", packet)
        self.assertIn("What would Mark say in response to the opened archive?", packet)
        self.assertEqual(list((ws / "manuscript").iterdir()), [])

    def test_character_consultation_refuses_missing_dossier(self):
        ws = self.ws()
        rc, out = run_tyf(
            ["consult-character", "work", "Mark", "--prompt", "What would Mark say?"], ws)
        self.assertNotEqual(rc, 0, "character consult must not invent a dossier")
        self.assertRegex(out.lower(), r"character|dossier|missing")
        self.assertFalse((ws / ".review" / "character-consults").exists())

    def test_character_dossier_supports_non_latin_names(self):
        ws = self.ws()
        rc, out = run_tyf(
            ["character", "Мария",
             "--knowledge", "Мария знает старую песню.",
             "--voice", "тихо, точно"], ws)
        self.assertEqual(rc, 0, out)
        self.assertTrue((ws / "knowledge-base" / "characters" / "мария.md").is_file())
        self.assertTrue((ws / "voice" / "characters" / "мария.md").is_file())

        rc, out = run_tyf(
            ["consult-character", "work", "Мария",
             "--prompt", "Что Мария сказала бы здесь?"], ws)
        self.assertEqual(rc, 0, out)
        consults = list((ws / ".review" / "character-consults").glob("мария-*.md"))
        self.assertEqual(len(consults), 1)
        packet = consults[0].read_text(encoding="utf-8")
        self.assertIn("Мария знает старую песню.", packet)
        self.assertIn("тихо, точно", packet)
        self.assertIn("Ground only in this character dossier", packet)

    def test_capture_requires_existing_work(self):
        ws = self.ws()
        rc, out = run_tyf(
            ["capture", "missing", "--kind", "source", "--text", "not yet"], ws)
        self.assertNotEqual(rc, 0, "capture must bind source to an existing work")
        self.assertFalse((ws / "sources" / "notes" / "missing.md").exists())

    def test_start_positional_title_is_not_a_compatibility_alias(self):
        ws = self.ws()
        rc, out = run_tyf(["start", "The New Book"], ws)
        self.assertNotEqual(rc, 0, "positional title compatibility should be gone")
        self.assertIn('No arrival path found: "The New Book"', out)
        self.assertIn('tyf start --title "The New Book"', out)
        self.assertFalse((ws / "works" / "the-new-book").exists())

    def test_start_positional_title_error_points_to_title_flag(self):
        ws = self.ws()
        rc, out = run_tyf(["start", "Working Title"], ws)
        self.assertNotEqual(rc, 0, "positional title must not be accepted")
        self.assertIn('No arrival path found: "Working Title"', out)
        self.assertIn('tyf start --title "Working Title"', out)

    def test_today_command_is_removed(self):
        ws = self.ws()
        rc, out = run_tyf(["today"], ws)
        self.assertNotEqual(rc, 0, "today must not survive as a compatibility alias")
        self.assertIn("invalid choice", out.lower())

    def test_start_allows_no_title_and_keeps_intake_non_blocking(self):
        ws = self.ws()
        rc, out = run_tyf(["start"], ws)
        self.assertEqual(rc, 0, out)
        work_yaml = (ws / "work.yaml").read_text(encoding="utf-8")
        self.assertIn('title_status: "unknown"', work_yaml)
        self.assertIn('language: "undetermined"', work_yaml)
        self.assertTrue((ws / "sources" / "interviews" / "work-first-session.md").is_file())
        self.assertTrue((ws / ".review" / "writing-runway.md").is_file())
        self.assertTrue((ws / "drafts" / "candidate-draft.md").is_file())
        self.assertEqual(list((ws / "manuscript").iterdir()), [])
        self.assertFalse((ws / "works").exists())
        self.assertIn("Writing runway opened", out)
        self.assertNotIn("Work id:", out)

        rc, notice = run_tyf(["notice", "--peek"], ws)
        self.assertEqual(rc, 0, notice)
        self.assertIn("nothing outstanding", notice.lower())

    def test_start_records_non_latin_title_without_id_gate(self):
        ws = self.ws()
        rc, out = run_tyf(["start", "--title", "Русская книга"], ws)
        self.assertEqual(rc, 0, out)
        work_yaml = (ws / "work.yaml").read_text(encoding="utf-8")
        self.assertIn('title: "Русская книга"', work_yaml)
        self.assertFalse((ws / "works").exists())

    def test_start_records_explicit_writing_language(self):
        ws = self.ws()
        rc, out = run_tyf(["start", "--title", "Livro Novo", "--language", "Portuguese"], ws)
        self.assertEqual(rc, 0, out)
        work_yaml = (ws / "work.yaml").read_text(encoding="utf-8")
        starter = (ws / "sources" / "interviews" / "work-first-session.md").read_text(encoding="utf-8")
        style = (ws / "style-sheet.md").read_text(encoding="utf-8")
        self.assertIn('language: "Portuguese"', work_yaml)
        self.assertIn("Writing language: Portuguese", starter)
        self.assertIn("Writing language: Portuguese", style)
        self.assertIn("Writing runway opened", out)

    def test_gate_preserves_utf8_manuscript_text_for_declared_language(self):
        ws = self.ws()
        rc, out = run_tyf(["new-work", "demo", "--language", "Japanese"], ws)
        self.assertEqual(rc, 0, out)
        text = "第一章\n声はここにある。\nРусская строка тоже жива.\n"
        src = self.make_draft(ws, name="chapter.md", text=text)
        decision = self.gate_decision(ws, src=src, unit="chapter.md")
        rc, out = run_tyf(["write", "demo", "--decision", decision], ws)
        self.assertEqual(rc, 0, out)
        self.assertIn('language: "Japanese"',
                      (ws / "works/demo/work.yaml").read_text(encoding="utf-8"))
        self.assertEqual((ws / "works/demo/manuscript/chapter.md").read_text(encoding="utf-8"),
                         text)

    def test_import_chat_preserves_raw_input_creates_titleless_work_and_fragment(self):
        ws = self.ws()
        chat = self.tmp / "arrival-chat.txt"
        chat.write_text("Alexander: The book starts from an inherited silence.\n", encoding="utf-8")

        rc, out = run_tyf(["import", str(chat), "--kind", "chat"], ws)
        self.assertEqual(rc, 0, out)
        work_id = re.search(r"Work id:\s+(\S+)", out).group(1)
        fragment = re.search(r"Source fragment:\s+(\S+)", out).group(1)
        self.assertEqual(work_id, "work")
        self.assertTrue((ws / "work.yaml").is_file())
        self.assertIn('title_status: "unknown"',
                      (ws / "work.yaml").read_text(encoding="utf-8"))
        imports = list((ws / "sources" / "imports").glob("*arrival-chat.txt"))
        self.assertEqual(len(imports), 1)
        self.assertIn("inherited silence", imports[0].read_text(encoding="utf-8"))
        orientation = list((ws / "sources" / "imports").glob("*orientation.md"))
        self.assertEqual(len(orientation), 1)
        self.assertIn("No manuscript text was written", orientation[0].read_text(encoding="utf-8"))
        index = (ws / "sources" / "fragments.jsonl").read_text(encoding="utf-8")
        self.assertIn(fragment, index)
        self.assertEqual(list((ws / "manuscript").iterdir()), [])

    def test_import_zip_preserves_bundle_without_manuscript_write(self):
        ws = self.ws()
        bundle = self.tmp / "old-project.zip"
        with zipfile.ZipFile(bundle, "w") as zf:
            zf.writestr("notes/opening.md", "A remembered draft from elsewhere.\n")
            zf.writestr("state/work.yaml", "title: old\n")

        rc, out = run_tyf(["import", str(bundle), "--kind", "bundle", "--title", "Imported Kin"], ws)
        self.assertEqual(rc, 0, out)
        work_id = re.search(r"Work id:\s+(\S+)", out).group(1)
        imports = list((ws / "sources" / "imports").glob("*old-project.zip"))
        self.assertEqual(len(imports), 1)
        orientation = list((ws / "sources" / "imports").glob("*orientation.md"))
        self.assertTrue(any("notes/opening.md" in p.read_text(encoding="utf-8") for p in orientation))
        self.assertEqual(work_id, "work")
        work_yaml = (ws / "work.yaml").read_text(encoding="utf-8")
        self.assertIn('title: "Imported Kin"', work_yaml)
        self.assertIn('title_status: "working"', work_yaml)
        self.assertEqual(list((ws / "manuscript").iterdir()), [])

    def test_import_folder_preserves_tree_and_lists_without_live_merge(self):
        ws = self.ws()
        dump = self.tmp / "random-dump"
        (dump / "notes").mkdir(parents=True)
        (dump / "works" / "old" / "manuscript").mkdir(parents=True)
        (dump / "notes" / "opening.md").write_text("A loose source note.\n", encoding="utf-8")
        (dump / "works" / "old" / "manuscript" / "chapter.md").write_text(
            "Old prose that should not be live yet.\n", encoding="utf-8")

        rc, out = run_tyf(["import", str(dump), "--kind", "dump"], ws)
        self.assertEqual(rc, 0, out)
        work_id = re.search(r"Work id:\s+(\S+)", out).group(1)
        preserved = list((ws / "sources" / "imports").glob("*random-dump"))
        self.assertEqual(len(preserved), 1)
        self.assertTrue((preserved[0] / "works" / "old" / "manuscript" / "chapter.md").is_file())
        orientation = list((ws / "sources" / "imports").glob("*orientation.md"))
        orientation_text = "\n".join(p.read_text(encoding="utf-8") for p in orientation)
        self.assertIn("notes/opening.md", orientation_text)
        self.assertIn("works/old/manuscript/chapter.md", orientation_text)
        self.assertIn("organization plan", orientation_text)
        self.assertFalse((ws / "works" / "old").exists())
        self.assertEqual(work_id, "work")
        self.assertEqual(list((ws / "manuscript").iterdir()), [])

    def test_import_tyf_shaped_zip_is_detected_without_merging(self):
        ws = self.ws()
        bundle = self.tmp / "tyf-shaped.zip"
        with zipfile.ZipFile(bundle, "w") as zf:
            zf.writestr("WORKSPACE_STATE.yaml", "active_work: old\n")
            zf.writestr("sources/notes/opening.md", "Existing source.\n")
            zf.writestr("works/old/manuscript/chapter.md", "Existing manuscript.\n")

        rc, out = run_tyf(["import", str(bundle), "--kind", "bundle"], ws)
        self.assertEqual(rc, 0, out)
        work_id = re.search(r"Work id:\s+(\S+)", out).group(1)
        orientation = list((ws / "sources" / "imports").glob("*orientation.md"))
        orientation_text = "\n".join(p.read_text(encoding="utf-8") for p in orientation)
        self.assertIn("TYF-shaped workspace/archive signals detected", orientation_text)
        self.assertIn("propose a merge plan", orientation_text)
        self.assertIn("works/old/manuscript/chapter.md", orientation_text)
        self.assertFalse((ws / "works" / "old").exists())
        self.assertEqual(work_id, "work")
        self.assertEqual(list((ws / "manuscript").iterdir()), [])

    def test_start_without_arrival_opens_titleless_writing_runway(self):
        ws = self.ws()
        rc, out = run_tyf(["start"], ws)
        self.assertEqual(rc, 0, out)
        runway = ws / ".review" / "writing-runway.md"
        draft = ws / "drafts" / "candidate-draft.md"
        self.assertTrue(runway.is_file())
        self.assertTrue(draft.is_file())
        self.assertIn("Writing runway", runway.read_text(encoding="utf-8"))
        self.assertIn("Do not wait for a title", runway.read_text(encoding="utf-8"))
        self.assertIn("sources/interviews/work-first-session.md", runway.read_text(encoding="utf-8"))
        self.assertIn("Start drafting here", draft.read_text(encoding="utf-8"))
        self.assertIn('title_status: "unknown"', (ws / "work.yaml").read_text(encoding="utf-8"))
        starter = ws / "sources" / "interviews" / "work-first-session.md"
        self.assertTrue(starter.is_file())
        self.assertIn("author-owned first-session packet", starter.read_text(encoding="utf-8"))
        self.assertEqual(list((ws / "manuscript").iterdir()), [])
        self.assertFalse((ws / "works").exists())
        self.assertIn("Writing runway opened", out)
        self.assertIn("No manuscript text was written", out)
        self.assertIn("Draft runway", out)
        self.assertNotIn("Work id:", out)

    def test_start_updates_root_title_language_and_evidence_packet(self):
        ws = self.ws()
        rc, out = run_tyf(["start", "--title", "My Great Book", "--language", "English"], ws)
        self.assertEqual(rc, 0, out)
        work_yaml = (ws / "work.yaml").read_text(encoding="utf-8")
        self.assertIn('title: "My Great Book"', work_yaml)
        self.assertIn('title_status: "working"', work_yaml)
        self.assertIn('language: "English"', work_yaml)
        starter = (ws / "sources" / "interviews" / "work-first-session.md").read_text(encoding="utf-8")
        self.assertIn("Writing language: English", starter)
        runway = (ws / ".review" / "writing-runway.md").read_text(encoding="utf-8")
        self.assertIn("sources/interviews/work-first-session.md", runway)
        self.assertIn("No manuscript text was written", out)

    def test_start_with_folder_arrival_preserves_scaffold_and_opens_runway(self):
        ws = self.ws()
        scaffold = self.tmp / "cold-start-scaffold"
        (scaffold / "notes").mkdir(parents=True)
        (scaffold / "notes" / "voice.md").write_text(
            "I want the book to begin from kinship and weather.\n", encoding="utf-8")
        (scaffold / "outline.md").write_text("No fixed title yet.\n", encoding="utf-8")

        rc, out = run_tyf(["start", str(scaffold), "--kind", "dump"], ws)
        self.assertEqual(rc, 0, out)
        preserved = list((ws / "sources" / "imports").glob("*cold-start-scaffold"))
        self.assertEqual(len(preserved), 1)
        self.assertTrue((preserved[0] / "notes" / "voice.md").is_file())
        orientation = list((ws / "sources" / "imports").glob("*orientation.md"))
        orientation_text = "\n".join(p.read_text(encoding="utf-8") for p in orientation)
        self.assertIn("notes/voice.md", orientation_text)
        runway = (ws / ".review" / "writing-runway.md").read_text(encoding="utf-8")
        draft = (ws / "drafts" / "candidate-draft.md").read_text(encoding="utf-8")
        self.assertIn("Arrival orientation", runway)
        self.assertIn("sources/interviews/work-first-session.md", runway)
        self.assertIn("organization principle", runway)
        self.assertIn("Start drafting here", draft)
        self.assertEqual(list((ws / "manuscript").iterdir()), [])
        self.assertFalse((ws / "works").exists())
        self.assertIn("Arrival orientation", out)
        self.assertIn("Next: write in", out)

    def test_status_reports_active_work_status_from_work_yaml(self):
        ws = self.ws()
        raw = (ws / "work.yaml").read_text(encoding="utf-8")
        (ws / "work.yaml").write_text(raw.replace("status: structuring", "status: written"), encoding="utf-8")
        rc, out = run_tyf(["status"], ws)
        self.assertEqual(rc, 0, out)
        self.assertIn("workspace.status : intake", out)
        self.assertIn("work.status      : written", out)
        self.assertIn("work.language    : undetermined", out)

    def test_beta_start_arrival_uses_root_book_folder(self):
        self.test_start_with_folder_arrival_preserves_scaffold_and_opens_runway()

    def test_user_yaml_values_are_safely_quoted(self):
        ws = self.ws()
        rc, out = run_tyf(
            ["new-work", "yaml-demo", "--type", "book: essay",
             "--register", "voice: one"], ws)
        self.assertEqual(rc, 0, out)
        raw = (ws / "works" / "yaml-demo" / "work.yaml").read_text(encoding="utf-8")
        self.assertIn('type: "book: essay"', raw)
        self.assertIn('- "voice: one"', raw)
        parsed = tyf.read_state(str(ws / "works" / "yaml-demo" / "work.yaml"))
        self.assertEqual(parsed["type"], "book: essay")
        self.assertEqual(parsed["language"], "undetermined")
        self.assertEqual(parsed["registers"], ["voice: one"])

    def test_init_creates_workspace_context_contracts(self):
        ws = self.ws()
        for name in ("AGENTS.md", "CLAUDE.md", "GEMINI.md"):
            text = (ws / name).read_text(encoding="utf-8")
            self.assertIn("TYF workspace", text)
            self.assertIn("tyf start", text)
            self.assertNotIn("tyf today", text)
            self.assertIn("single work", text.lower())
            self.assertIn("drafts/", text)
            self.assertNotIn("works/*/drafts", text)

    def test_new_work_adds_event_log_entry(self):
        ws = self.ws()
        before = tyf.ledger_summary(str(ws))[1]
        rc, out = run_tyf(["new-work", "event-demo"], ws)
        self.assertEqual(rc, 0, out)
        after = tyf.ledger_summary(str(ws))[1]
        self.assertGreater(after, before)

    def test_canonical_event_journal_records_core_actions_with_hash_chain(self):
        ws = self.ws()
        rc, out = run_tyf(["new-work", "event-demo", "--language", "Portuguese"], ws)
        self.assertEqual(rc, 0, out)
        rc, out = run_tyf(
            ["capture", "event-demo", "--kind", "source", "--text", "Fonte viva."], ws)
        self.assertEqual(rc, 0, out)
        rc, out = run_tyf(["mark-ready", "event-demo", "chapter.md"], ws)
        self.assertEqual(rc, 0, out)

        journal = ws / ".tyf" / "events.jsonl"
        self.assertTrue(journal.is_file(), "apparatus events should have a canonical JSONL journal")
        records = [json.loads(line) for line in journal.read_text(encoding="utf-8").splitlines()]
        self.assertGreaterEqual(len(records), 4)
        self.assertEqual([r["seq"] for r in records], list(range(1, len(records) + 1)))
        previous = ""
        for record in records:
            self.assertEqual(record["previous_hash"], previous)
            self.assertEqual(record["hash"], event_record_hash(record))
            previous = record["hash"]
        kinds = [r["kind"] for r in records]
        self.assertEqual(kinds[:1], ["init"])
        self.assertIn("new-work", kinds)
        self.assertIn("capture", kinds)
        self.assertIn("mark-ready", kinds)

    def test_doctor_flags_tampered_canonical_event_journal(self):
        ws = self.ws()
        rc, out = run_tyf(["new-work", "event-demo"], ws)
        self.assertEqual(rc, 0, out)
        journal = ws / ".tyf" / "events.jsonl"
        self.assertTrue(journal.is_file(), "apparatus events should have a canonical JSONL journal")
        records = [json.loads(line) for line in journal.read_text(encoding="utf-8").splitlines()]
        records[0]["kind"] = "rewritten-init"
        journal.write_text("\n".join(json.dumps(r, ensure_ascii=False, sort_keys=True)
                                     for r in records) + "\n",
                           encoding="utf-8")
        rc, out = run_tyf(["doctor"], ws)
        self.assertNotEqual(rc, 0, "doctor must flag tampered canonical event journals")
        self.assertRegex(out.lower(), r"event journal|event log|tamper|hash|chain")

    def test_doctor_flags_missing_canonical_event_journal(self):
        ws = self.ws()
        journal = ws / ".tyf" / "events.jsonl"
        journal.unlink()
        rc, out = run_tyf(["doctor"], ws)
        self.assertNotEqual(rc, 0, "doctor must flag a missing canonical event journal")
        self.assertRegex(out.lower(), r"event journal|missing")

    def test_doctor_flags_malformed_canonical_event_journal(self):
        ws = self.ws()
        journal = ws / ".tyf" / "events.jsonl"
        journal.write_text("{not json}\n", encoding="utf-8")
        rc, out = run_tyf(["doctor"], ws)
        self.assertNotEqual(rc, 0, "doctor must flag malformed canonical event journals")
        self.assertRegex(out.lower(), r"event journal|invalid json|malformed")

    def test_mutating_command_refuses_missing_canonical_event_journal(self):
        ws = self.ws()
        journal = ws / ".tyf" / "events.jsonl"
        journal.unlink()
        rc, out = run_tyf(["new-work", "after-loss"], ws)
        self.assertNotEqual(rc, 0, "mutating commands must not recreate a missing event journal over lost history")
        self.assertRegex(out.lower(), r"event journal|missing|doctor")
        self.assertFalse((ws / "works" / "after-loss").exists())

    # ---- transparent reflexes and explicit git recovery points ----

    def test_reflexes_explains_hooks_and_snapshot(self):
        ws = self.ws()
        rc, out = run_tyf(["reflexes"], ws)
        self.assertEqual(rc, 0, out)
        self.assertIn("documentation honesty", out.lower())
        self.assertIn("attentive amanuensis", out.lower())
        self.assertIn("tyf snapshot", out)
        self.assertIn("never commits silently", out.lower())

    @unittest.skipUnless(shutil.which("git"), "git not available")
    def test_snapshot_commits_workspace_changes_when_git_repo(self):
        ws = self.ws()
        subprocess.run(["git", "init"], cwd=str(ws), check=True,
                       capture_output=True, text=True)
        subprocess.run(["git", "config", "user.email", "tyf@example.test"],
                       cwd=str(ws), check=True)
        subprocess.run(["git", "config", "user.name", "TYF Test"],
                       cwd=str(ws), check=True)
        rc, out = run_tyf(["begin", "new-book"], ws)
        self.assertEqual(rc, 0, out)
        rc, out = run_tyf(["snapshot", "--message", "first session"], ws)
        self.assertEqual(rc, 0, out)
        subject = subprocess.run(
            ["git", "log", "-1", "--format=%s"], cwd=str(ws),
            capture_output=True, text=True, check=True).stdout.strip()
        self.assertEqual(subject, "first session")
        status = subprocess.run(
            ["git", "status", "--short"], cwd=str(ws),
            capture_output=True, text=True, check=True).stdout.strip()
        self.assertEqual(status, "")

    def test_snapshot_refuses_outside_git(self):
        ws = self.ws()
        rc, out = run_tyf(["snapshot", "--message", "no repo"], ws)
        self.assertNotEqual(rc, 0, "snapshot needs an explicit git workspace")
        self.assertIn("git", out.lower())

    @unittest.skipUnless(shutil.which("git"), "git not available")
    def test_snapshot_scopes_commit_to_workspace_inside_parent_repo(self):
        parent = self.tmp / "parent"
        parent.mkdir()
        subprocess.run(["git", "init"], cwd=str(parent), check=True,
                       capture_output=True, text=True)
        subprocess.run(["git", "config", "user.email", "tyf@example.test"],
                       cwd=str(parent), check=True)
        subprocess.run(["git", "config", "user.name", "TYF Test"],
                       cwd=str(parent), check=True)
        rc, out = run_tyf(["init", "book"], parent)
        self.assertEqual(rc, 0, out)
        ws = parent / "book"
        (parent / "app-secret.txt").write_text("outside\n", encoding="utf-8")
        rc, out = run_tyf(["start", "--title", "Book"], ws)
        self.assertEqual(rc, 0, out)
        rc, out = run_tyf(["snapshot", "--message", "book checkpoint"], ws)
        self.assertEqual(rc, 0, out)
        committed = subprocess.run(
            ["git", "show", "--name-only", "--format=", "HEAD"], cwd=str(parent),
            capture_output=True, text=True, check=True).stdout.splitlines()
        self.assertTrue(any(p.startswith("book/") for p in committed), committed)
        self.assertNotIn("app-secret.txt", committed)
        self.assertNotIn("book/.tyf/ledger.db", committed)
        status = subprocess.run(
            ["git", "status", "--short"], cwd=str(parent),
            capture_output=True, text=True, check=True).stdout
        self.assertIn("?? app-secret.txt", status)

    def test_notice_peek_does_not_create_ledger_database(self):
        ws = self.ws()
        db = ws / ".tyf" / "ledger.db"
        db.unlink()
        (ws / "works").mkdir(exist_ok=True)
        rc, out = run_tyf(["notice", "--peek"], ws)
        self.assertEqual(rc, 0, out)
        self.assertFalse(db.exists(), "--peek must not initialize apparatus memory")

    def test_resolved_notice_reopens_when_same_gap_returns(self):
        ws = self.ws()
        run_tyf(["new-work", "demo"], ws)
        gap = ws / "works" / "demo" / "drafts" / "gap.md"
        gap.write_text("[AUTHOR: needed - cite this]\n", encoding="utf-8")
        rc, out = run_tyf(["notice"], ws)
        self.assertEqual(rc, 0, out)
        self.assertIn("new (", out)
        gap.write_text("filled\n", encoding="utf-8")
        self.assertEqual(run_tyf(["notice"], ws)[0], 0)
        gap.write_text("[AUTHOR: needed - cite this]\n", encoding="utf-8")
        rc, out = run_tyf(["notice"], ws)
        self.assertEqual(rc, 0, out)
        self.assertRegex(out.lower(), r"new|resurfaced")
        items, _events = tyf.ledger_summary(str(ws))
        self.assertTrue(any(r["status"] == "open" for r in items.values()), items)

    def test_identical_gaps_in_different_locations_have_distinct_notice_ids(self):
        ws = self.ws()
        run_tyf(["new-work", "demo"], ws)
        a = ws / "works" / "demo" / "drafts" / "a.md"
        b = ws / "works" / "demo" / "drafts" / "b.md"
        a.write_text("[AUTHOR: needed - citation]\n", encoding="utf-8")
        b.write_text("[AUTHOR: needed - citation]\n", encoding="utf-8")
        notices = [n for n in tyf.gather_notices(str(ws)) if n["kind"] == "gap"]
        hashes = {n["content_hash"] for n in notices}
        self.assertEqual(len(notices), 2)
        self.assertEqual(len(hashes), 2, notices)

    def test_notice_does_not_report_style_lag_after_clean_controlled_write(self):
        ws = self.ws()
        rc, out = run_tyf(["new-work", "demo"], ws)
        self.assertEqual(rc, 0, out)
        style = ws / "works" / "demo" / "style-sheet.md"
        old = 1_600_000_000
        os.utime(style, (old, old))
        src = self.make_draft(ws, work="demo", name="chapter.md", text="Controlled prose.\n")
        decision = self.gate_decision(ws, work="demo", src=src, unit="chapter.md")
        rc, out = run_tyf(["write", "demo", "--decision", decision], ws)
        self.assertEqual(rc, 0, out)
        notices = tyf.gather_notices(str(ws))
        self.assertFalse(
            [n for n in notices if n["kind"] == "style-sheet-lag" and n["where"] == "works/demo"],
            notices,
        )

    def test_notice_reports_style_lag_for_unlogged_manuscript_change(self):
        ws = self.ws()
        rc, out = run_tyf(["new-work", "demo"], ws)
        self.assertEqual(rc, 0, out)
        style = ws / "works" / "demo" / "style-sheet.md"
        old = 1_600_000_000
        os.utime(style, (old, old))
        manuscript = ws / "works" / "demo" / "manuscript" / "chapter.md"
        manuscript.write_text("Manual prose.\n", encoding="utf-8")
        notices = tyf.gather_notices(str(ws))
        self.assertTrue(
            [n for n in notices if n["kind"] == "style-sheet-lag" and n["where"] == "works/demo"],
            notices,
        )


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

    def test_check_ignores_solo_generated_control_dirs(self):
        root = self.min_pack()
        (root / ".fbs" / "recovered").mkdir(parents=True)
        (root / ".claude" / "commands").mkdir(parents=True)
        dead_command = "tyf " + "gate"
        (root / ".fbs" / "recovered" / "note.md").write_text(
            f"Generated SOLO evidence with an em dash — and {dead_command}.\n",
            encoding="utf-8")
        (root / ".claude" / "commands" / "fbs-formulate.md").write_text(
            "Generated command docs with an em dash — not TYF pack law.\n",
            encoding="utf-8")
        problems, _ = tyf.run_doc_check(str(root))
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

    def test_check_flags_retired_write_confirm_command(self):
        root = self.min_pack()
        (root / "README.md").write_text(
            "Apply accepted text with `tyf write --confirm`.\n", encoding="utf-8")
        problems, _ = tyf.run_doc_check(str(root))
        self.assertTrue(any("tyf write --confirm" in p for p in problems),
                        f"expected a retired-command problem, got {problems}")

    def test_check_flags_role_terminology_drift(self):
        root = self.min_pack()
        (root / "README.md").write_text(
            "TYF is the interviewer, machinist, first reader, editor, and typographer.\n",
            encoding="utf-8")
        problems, _ = tyf.run_doc_check(str(root))
        self.assertTrue(any("terminolog" in p.lower() or "machinist" in p.lower()
                            or "typographer" in p.lower() for p in problems),
                        f"expected a terminology-drift problem, got {problems}")

    def test_check_flags_stale_writing_runway_routing(self):
        root = self.min_pack()
        stale = (
            "# Context\n\n"
            "If the author says start my book, run `tyf today` or "
            "`tyf start \"Working Title\"` after getting a title.\n"
        )
        for name in ("CLAUDE.md", "AGENTS.md", "GEMINI.md"):
            (root / name).write_text(stale, encoding="utf-8")
        problems, _ = tyf.run_doc_check(str(root))
        self.assertTrue(any("writing-runway" in p.lower() or "stale writing" in p.lower()
                            for p in problems),
                        f"expected a stale writing-runway routing problem, got {problems}")

    def test_check_flags_stale_single_work_path_drift(self):
        root = self.min_pack()
        path = root / "cowork" / "PROJECT_INSTRUCTIONS.md"
        path.parent.mkdir(parents=True)
        path.write_text(
            "Compose writes to `works/<id>/drafts/` only.\n"
            "Audit writes findings to `works/<id>/.review/`.\n",
            encoding="utf-8")
        problems, _ = tyf.run_doc_check(str(root))
        self.assertTrue(any("single-work" in p.lower() or "works/<id>" in p
                            for p in problems),
                        f"expected a stale single-work path problem, got {problems}")

    def test_check_flags_stale_multi_work_globs(self):
        root = self.min_pack()
        path = root / "cowork" / "SCHEDULED_TASKS.md"
        path.parent.mkdir(parents=True)
        path.write_text(
            "Find chapters in any `works/*/drafts/` or `works/*/manuscript/`.\n",
            encoding="utf-8")
        problems, _ = tyf.run_doc_check(str(root))
        self.assertTrue(any("single-work" in p.lower() or "works/*/" in p
                            for p in problems),
                        f"expected a stale multi-work glob problem, got {problems}")

    def test_check_flags_today_inside_command_lists(self):
        root = self.min_pack()
        (root / "README.md").write_text(
            "Advanced helper commands include `init`, `new-work`, `today`, `start`, and `write`.\n",
            encoding="utf-8")
        problems, _ = tyf.run_doc_check(str(root))
        self.assertTrue(any("today" in p.lower() and "command" in p.lower()
                            for p in problems),
                        f"expected a stale today command-list problem, got {problems}")

    def test_check_flags_plugin_manifest_version_divergence(self):
        root = self.min_pack()
        for rel, version in (
                (".claude-plugin/plugin.json", "0.5.0"),
                (".codex-plugin/plugin.json", "0.5.0"),
                ("plugin/.claude-plugin/plugin.json", "0.3.0")):
            path = root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps({"name": "tyf", "version": version}) + "\n", encoding="utf-8")
        problems, _ = tyf.run_doc_check(str(root))
        self.assertTrue(any("manifest version" in p.lower() or "version divergence" in p.lower()
                            for p in problems),
                        f"expected manifest version divergence, got {problems}")

    def test_author_context_templates_do_not_include_solo_development_reflex(self):
        for name in ("AGENTS.md", "CLAUDE.md", "GEMINI.md"):
            path = REPO / "author-context" / name
            self.assertTrue(path.is_file(), f"{name} author context template should exist")
            text = path.read_text(encoding="utf-8")
            self.assertIn("TYF workspace", text)
            self.assertIn("tyf start", text)
            self.assertIn("single work", text.lower())
            self.assertNotIn("SOLO Reflex", text)
            self.assertNotIn("using-solo", text)
            self.assertNotIn("fbs", text.lower())

    def test_release_archive_excludes_workshop_debris(self):
        attrs = (REPO / ".gitattributes").read_text(encoding="utf-8")
        for token in (
                ".fbs/** export-ignore",
                ".pytest_cache/** export-ignore",
                "**/__pycache__/** export-ignore",
                "*.pyc export-ignore",
                "fbs.yaml export-ignore",
                ".claude/commands/fbs-* export-ignore",
                ".claude/settings.json export-ignore",
                "AGENTS.md export-ignore",
                "CLAUDE.md export-ignore",
                "GEMINI.md export-ignore"):
            self.assertIn(token, attrs)

    def test_readme_pressure_status_matches_validation_evidence(self):
        readme = (REPO / "README.md").read_text(encoding="utf-8")
        self.assertNotIn("have not yet been run against a subagent", readme)
        self.assertIn("GREEN passed 11/11", readme)
        self.assertIn("RED baseline", readme)
        self.assertIn("proof is partial", readme)

    def test_install_docs_route_author_workspaces_away_from_dev_context(self):
        install = (REPO / "scripts" / "install.sh").read_text(encoding="utf-8")
        portability = (REPO / "docs" / "PORTABILITY.md").read_text(encoding="utf-8")
        self.assertIn("For a book workspace, run `tyf init`", install)
        self.assertIn("Do not copy the pack development context", install)
        self.assertIn("author-context", install)
        self.assertIn("author-context", portability)
        self.assertIn("run `tyf init`", portability)
        self.assertNotIn(
            "place the matching context file where the harness reads session context",
            portability,
        )


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

    def test_codex_install_targets_current_skill_root(self):
        script = (REPO / "scripts" / "install.sh").read_text(encoding="utf-8")
        self.assertIn('${CODEX_HOME:-$HOME/.codex}/skills', script)
        self.assertNotIn('$HOME/.agents/skills', script)


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
