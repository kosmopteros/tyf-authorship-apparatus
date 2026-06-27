#!/usr/bin/env python3
"""Tests for the standalone TYF v0.6 Workbench slice."""

import importlib.util
import os
from pathlib import Path
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[1]
WORKBENCH = REPO / "scripts" / "tyf_workbench_v06.py"


def load_workbench_module():
    spec = importlib.util.spec_from_file_location("tyf_workbench_v06", WORKBENCH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class WorkbenchV06Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "drafts").mkdir()
        (self.root / "manuscript").mkdir()
        (self.root / "design").mkdir()
        (self.root / "WORKSPACE_STATE.yaml").write_text("active_work: work\n", encoding="utf-8")
        (self.root / "work.yaml").write_text(
            'id: work\ntitle: "The Kin"\nlanguage: "English"\nstatus: drafting\n',
            encoding="utf-8",
        )
        (self.root / "drafts" / "chapter-1.md").write_text("# Chapter 1\n\nThe kin remembers the organism.\n", encoding="utf-8")
        (self.root / "manuscript" / "chapter-1.md").write_text("# Chapter 1\n\nApproved text.\n", encoding="utf-8")
        (self.root / "style-sheet.md").write_text("# Style\n", encoding="utf-8")
        (self.root / "design" / "book-style.yaml").write_text("profile: working-print\n", encoding="utf-8")
        self.old_cwd = os.getcwd()
        os.chdir(self.root)
        self.wb = load_workbench_module()

    def tearDown(self):
        os.chdir(self.old_cwd)
        self.tmp.cleanup()

    def test_collect_data_creates_plain_file_workbench_state(self):
        work_id, work_root, workspace_root = self.wb.resolve_work_root(None)
        data = self.wb.collect_workbench_data(work_root, workspace_root, work_id)
        self.assertEqual(work_id, "work")
        self.assertTrue((self.root / "outline" / "book-map.yaml").is_file())
        self.assertTrue((self.root / "knowledge-base" / "author-notes.jsonl").is_file())
        self.assertTrue((self.root / ".tyf" / "workbench-state.json").is_file())
        self.assertEqual(data["book_map"]["unit_count"], 1)
        self.assertEqual(data["units"][0]["draft"]["path"], "drafts/chapter-1.md")
        self.assertTrue(data["units"][0]["manuscript"]["exists"])

    def test_save_draft_uses_base_hash_conflict_protection(self):
        work_id, work_root, workspace_root = self.wb.resolve_work_root(None)
        data = self.wb.collect_workbench_data(work_root, workspace_root, work_id)
        draft = data["units"][0]["draft"]
        saved = self.wb.save_draft(work_root, workspace_root, work_id, draft["path"], draft["sha256"], draft["text"] + "\nMore.\n")
        self.assertEqual(saved["status"], "saved")
        conflict = self.wb.save_draft(work_root, workspace_root, work_id, draft["path"], draft["sha256"], "stale browser edit")
        self.assertEqual(conflict["status"], "conflict")
        self.assertIn("current_text", conflict)
        self.assertIn("proposed_text", conflict)

    def test_author_note_to_footnote_candidate_stays_out_of_manuscript(self):
        work_id, work_root, workspace_root = self.wb.resolve_work_root(None)
        data = self.wb.collect_workbench_data(work_root, workspace_root, work_id)
        unit = data["units"][0]
        note = self.wb.create_author_note(work_root, workspace_root, work_id, {
            "unit_id": unit["id"],
            "target_path": unit["draft"]["path"],
            "target_kind": "selection",
            "quote": "kin",
            "start_offset": 14,
            "end_offset": 17,
            "body": "This may become a footnote.",
        })
        self.assertEqual(note["status"], "noted")
        candidate = self.wb.create_footnote_candidate(work_root, workspace_root, work_id, note["note"]["id"])
        self.assertEqual(candidate["status"], "candidate")
        self.assertTrue((self.root / candidate["markdown"]).is_file())
        self.assertEqual((self.root / "manuscript" / "chapter-1.md").read_text(encoding="utf-8"), "# Chapter 1\n\nApproved text.\n")

    def test_gate_and_context_packets_are_review_only(self):
        work_id, work_root, workspace_root = self.wb.resolve_work_root(None)
        data = self.wb.collect_workbench_data(work_root, workspace_root, work_id)
        unit = data["units"][0]
        gate = self.wb.create_gate_packet(work_root, workspace_root, work_id, {
            "path": unit["draft"]["path"],
            "base_hash": unit["draft"]["sha256"],
            "selection": "The kin remembers",
            "note": "ready for a normal Gate chain",
        })
        self.assertEqual(gate["status"], "packet")
        self.assertTrue((self.root / gate["markdown"]).is_file())
        context = self.wb.create_context_packet(work_root, workspace_root, work_id, {
            "unit_id": unit["id"],
            "selection": {"path": unit["draft"]["path"], "quote": "organism"},
        })
        self.assertEqual(context["status"], "context")
        self.assertTrue((self.root / context["markdown"]).is_file())
        self.assertFalse(context["packet"]["manuscript_written"])


if __name__ == "__main__":
    unittest.main()
