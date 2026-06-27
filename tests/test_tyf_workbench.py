#!/usr/bin/env python3
"""Tests for the standalone TYF Workbench v0.6 slice."""

import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
import tyf_workbench as wb  # noqa: E402


class WorkbenchV06Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="tyf-workbench-test-"))
        self.old = os.getcwd()
        os.chdir(self.tmp)
        self.make_workspace()

    def tearDown(self):
        os.chdir(self.old)
        shutil.rmtree(self.tmp, ignore_errors=True)

    def make_workspace(self):
        for rel in (
            "drafts", "manuscript", "outline", "knowledge-base", ".tyf",
            ".review", "design", "assets/images",
        ):
            (self.tmp / rel).mkdir(parents=True, exist_ok=True)
        (self.tmp / "WORKSPACE_STATE.yaml").write_text("active_work: work\nstatus: intake\n", encoding="utf-8")
        (self.tmp / "work.yaml").write_text(
            'id: work\ntype: "book"\ntitle: "Workbench Book"\ntitle_status: "working"\nlanguage: "English"\nstatus: drafting\n',
            encoding="utf-8",
        )
        (self.tmp / "style-sheet.md").write_text("# Style\n\nWriting language: English\n", encoding="utf-8")
        (self.tmp / "design" / "book-style.yaml").write_text("paragraph_styles:\n  body: {}\n", encoding="utf-8")
        (self.tmp / "assets" / "images" / "index.jsonl").write_text("", encoding="utf-8")
        (self.tmp / "drafts" / "candidate-draft.md").write_text("# Candidate\n\nFirst body.\n", encoding="utf-8")
        (self.tmp / "drafts" / "chapter-two.md").write_text("# Chapter Two\n\nSecond body.\n", encoding="utf-8")
        (self.tmp / "manuscript" / "chapter-two.md").write_text("# Chapter Two\n\nApproved body.\n", encoding="utf-8")

    def test_workbench_generates_multi_unit_book_map_and_data(self):
        html_path, data_path = wb.write_surface_files("work")

        self.assertTrue(Path(html_path).is_file())
        self.assertTrue(Path(data_path).is_file())
        self.assertTrue((self.tmp / "outline" / "book-map.yaml").is_file())
        self.assertTrue((self.tmp / "knowledge-base" / "author-notes.jsonl").is_file())
        self.assertTrue((self.tmp / ".review" / "gate-packets").is_dir())

        html = Path(html_path).read_text(encoding="utf-8")
        self.assertIn("TYF Workbench v0.6", html)
        self.assertIn("Save Draft", html)
        self.assertIn("Save Author Note", html)
        self.assertIn("Footnote Candidate", html)

        data = json.loads(Path(data_path).read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(data["book_map"]["units"]), 2)
        current = data["current"]
        self.assertTrue(current["draft"]["path"].startswith("drafts/"))
        self.assertTrue(current["manuscript"]["read_only"])
        self.assertEqual(data["gate"]["packet_dir"], ".review/gate-packets")

    def test_save_draft_is_per_unit_compare_and_swap(self):
        data = wb.workbench_data("work")
        chapter = next(u for u in data["book_map"]["units"] if u["draft"]["path"] == "drafts/chapter-two.md")
        base_hash = chapter["draft"]["sha256"]

        result = wb.save_draft("work", "drafts/chapter-two.md", base_hash, "# Chapter Two\n\nSaved body.\n")
        self.assertEqual(result["status"], "saved")
        self.assertIn("Saved body", (self.tmp / "drafts" / "chapter-two.md").read_text(encoding="utf-8"))

        conflict = wb.save_draft("work", "drafts/chapter-two.md", base_hash, "Clobber attempt.\n")
        self.assertEqual(conflict["status"], "conflict")
        self.assertNotIn("Clobber", (self.tmp / "drafts" / "chapter-two.md").read_text(encoding="utf-8"))

    def test_author_note_and_footnote_candidate_are_plain_files(self):
        note_result = wb.create_author_note("work", {
            "unit_id": "chapter-two",
            "target_path": "drafts/chapter-two.md",
            "target_kind": "selection",
            "text_quote": "Second body.",
            "start": 15,
            "end": 27,
            "note_body": "This should become a quiet explanatory footnote.",
        })
        self.assertEqual(note_result["status"], "note")
        note_id = note_result["note"]["id"]
        records = [
            json.loads(line)
            for line in (self.tmp / "knowledge-base" / "author-notes.jsonl").read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        self.assertEqual(records[0]["id"], note_id)
        self.assertEqual(records[0]["target_kind"], "selection")
        self.assertTrue(records[0]["quote_hash"])

        before = (self.tmp / "manuscript" / "chapter-two.md").read_text(encoding="utf-8")
        candidate = wb.footnote_candidate_from_note("work", note_id)
        self.assertEqual(candidate["status"], "footnote-candidate")
        self.assertTrue((self.tmp / candidate["json"]).is_file())
        self.assertTrue((self.tmp / candidate["markdown"]).is_file())
        self.assertEqual((self.tmp / "manuscript" / "chapter-two.md").read_text(encoding="utf-8"), before)

    def test_gate_packet_uses_review_dir_and_refuses_stale_base(self):
        draft = (self.tmp / "drafts" / "candidate-draft.md").read_text(encoding="utf-8")
        base_hash = wb._sha(draft)
        result = wb.gate_packet_from_selection("work", {
            "path": "drafts/candidate-draft.md",
            "base_hash": base_hash,
            "selection": "First body.",
            "note": "ready enough for review",
            "unit_id": "candidate-draft",
        })
        self.assertEqual(result["status"], "packet")
        self.assertTrue(result["json"].startswith(".review/gate-packets/"))
        self.assertTrue((self.tmp / result["markdown"]).is_file())

        (self.tmp / "drafts" / "candidate-draft.md").write_text("Changed on disk.\n", encoding="utf-8")
        conflict = wb.gate_packet_from_selection("work", {
            "path": "drafts/candidate-draft.md",
            "base_hash": base_hash,
            "selection": "First body.",
        })
        self.assertEqual(conflict["status"], "conflict")

    def test_save_draft_refuses_manuscript_path(self):
        with self.assertRaises(ValueError):
            wb.save_draft("work", "manuscript/chapter-two.md", "anything", "Nope.\n")


if __name__ == "__main__":
    unittest.main()
