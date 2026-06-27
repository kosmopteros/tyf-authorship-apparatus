import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = REPO_ROOT / "scripts" / "tyf_workbench_v06.py"

spec = importlib.util.spec_from_file_location("tyf_workbench_v06", MODULE_PATH)
workbench = importlib.util.module_from_spec(spec)
spec.loader.exec_module(workbench)


class WorkbenchV06Tests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / ".tyf").mkdir()
        (self.root / "drafts").mkdir()
        (self.root / "manuscript").mkdir()
        (self.root / "design").mkdir()
        (self.root / "WORKSPACE_STATE.yaml").write_text("active_work: work\n", encoding="utf-8")
        (self.root / "work.yaml").write_text(
            "title: Test Book\nlanguage: en\nstatus: draft\n",
            encoding="utf-8",
        )
        (self.root / "style-sheet.md").write_text("Plain, exact, author-first.\n", encoding="utf-8")
        (self.root / "design" / "book-style.yaml").write_text("register: spare\n", encoding="utf-8")
        (self.root / "drafts" / "chapter-one.md").write_text("Alpha beta gamma.\n", encoding="utf-8")
        (self.root / "manuscript" / "chapter-one.md").write_text("Approved alpha.\n", encoding="utf-8")
        self.old_cwd = os.getcwd()
        os.chdir(self.root)

    def tearDown(self):
        os.chdir(self.old_cwd)
        self.temp.cleanup()

    def resolved(self):
        work_id, work_root, workspace = workbench.resolve_work(None)
        workbench.ensure_workbench_shape(work_root, workspace)
        return work_id, work_root, workspace

    def test_collects_multi_surface_units_and_scaffold(self):
        work_id, work_root, workspace = self.resolved()
        data = workbench.collect_data(work_id, work_root, workspace)

        self.assertEqual(work_id, "work")
        self.assertEqual(data["work"]["title"], "Test Book")
        self.assertEqual(len(data["units"]), 1)
        unit = data["units"][0]
        self.assertEqual(unit["draft"]["path"], "drafts/chapter-one.md")
        self.assertEqual(unit["manuscript"]["path"], "manuscript/chapter-one.md")
        self.assertTrue((work_root / "outline" / "book-map.yaml").is_file())
        self.assertTrue((work_root / "knowledge-base" / "author-notes.jsonl").is_file())
        self.assertTrue((work_root / ".tyf" / "workbench-state.json").is_file())

    def test_saves_draft_with_compare_and_swap(self):
        work_id, work_root, workspace = self.resolved()
        data = workbench.collect_data(work_id, work_root, workspace)
        draft = data["units"][0]["draft"]

        saved = workbench.save_draft(
            work_id,
            work_root,
            workspace,
            {"path": draft["path"], "base_hash": draft["sha256"], "text": "Alpha beta delta.\n"},
        )
        self.assertEqual(saved["status"], "saved")
        self.assertEqual((work_root / "drafts" / "chapter-one.md").read_text(encoding="utf-8"), "Alpha beta delta.\n")

        conflict = workbench.save_draft(
            work_id,
            work_root,
            workspace,
            {"path": draft["path"], "base_hash": draft["sha256"], "text": "stale browser text"},
        )
        self.assertEqual(conflict["status"], "conflict")
        self.assertIn("current_text", conflict)

    def test_notes_footnotes_gate_packets_and_context_do_not_touch_manuscript(self):
        work_id, work_root, workspace = self.resolved()
        original_manuscript = (work_root / "manuscript" / "chapter-one.md").read_text(encoding="utf-8")
        data = workbench.collect_data(work_id, work_root, workspace)
        draft = data["units"][0]["draft"]

        note = workbench.create_author_note(
            work_id,
            work_root,
            workspace,
            {
                "target_path": draft["path"],
                "target_kind": "selection",
                "quote": "beta",
                "start_offset": 6,
                "end_offset": 10,
                "body": "Maybe this wants a historical footnote.",
                "provenance": "author",
            },
        )["note"]
        self.assertEqual(note["status"], "open")

        footnote = workbench.footnote_candidate(work_id, work_root, workspace, note["id"])
        self.assertEqual(footnote["status"], "footnote-candidate")
        self.assertTrue((work_root / footnote["markdown"]).is_file())

        gate = workbench.gate_packet(
            work_id,
            work_root,
            workspace,
            {"path": draft["path"], "base_hash": draft["sha256"], "selection": "Alpha beta", "note": "review this opening"},
        )
        self.assertEqual(gate["status"], "packet")
        self.assertTrue((work_root / gate["markdown"]).is_file())

        context = workbench.create_context_packet(
            work_id,
            work_root,
            workspace,
            {
                "active_unit": data["units"][0]["id"],
                "active_path": draft["path"],
                "selection": {"path": draft["path"], "text": "Alpha beta", "start_offset": 0, "end_offset": 10},
            },
        )
        self.assertEqual(context["status"], "context")
        self.assertTrue((work_root / context["markdown"]).is_file())
        self.assertEqual((work_root / "manuscript" / "chapter-one.md").read_text(encoding="utf-8"), original_manuscript)

    def test_can_create_new_draft_unit(self):
        work_id, work_root, workspace = self.resolved()
        result = workbench.create_draft_unit(
            work_id,
            work_root,
            workspace,
            {"title": "Interlude One", "path": "interlude-one"},
        )
        self.assertEqual(result["status"], "created")
        self.assertTrue((work_root / "drafts" / "interlude-one.md").is_file())
        book_map = (work_root / "outline" / "book-map.yaml").read_text(encoding="utf-8")
        self.assertIn("drafts/interlude-one.md", book_map)


if __name__ == "__main__":
    unittest.main()
