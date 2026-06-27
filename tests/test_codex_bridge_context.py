import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = REPO_ROOT / "scripts"

spec_v06 = importlib.util.spec_from_file_location("tyf_workbench_v06", SCRIPTS / "tyf_workbench_v06.py")
workbench = importlib.util.module_from_spec(spec_v06)
spec_v06.loader.exec_module(workbench)
sys.modules["tyf_workbench_v06"] = workbench

spec_bridge = importlib.util.spec_from_file_location("tyf_codex_bridge", SCRIPTS / "tyf_codex_bridge.py")
bridge = importlib.util.module_from_spec(spec_bridge)
spec_bridge.loader.exec_module(bridge)


class CodexBridgeContextTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / ".tyf").mkdir()
        (self.root / "drafts").mkdir()
        (self.root / "manuscript").mkdir()
        (self.root / "design").mkdir()
        (self.root / "WORKSPACE_STATE.yaml").write_text("active_work: work\n", encoding="utf-8")
        (self.root / "work.yaml").write_text("title: Bridge Book\nlanguage: en\nstatus: draft\n", encoding="utf-8")
        (self.root / "style-sheet.md").write_text("Voice: attentive.\n", encoding="utf-8")
        (self.root / "design" / "book-style.yaml").write_text("font: Charter\n", encoding="utf-8")
        (self.root / "drafts" / "chapter-one.md").write_text("Alpha beta gamma.\n", encoding="utf-8")
        (self.root / "manuscript" / "chapter-one.md").write_text("Approved alpha.\n", encoding="utf-8")
        self.old_cwd = os.getcwd()
        os.chdir(self.root)
        work_id, work_root, workspace = workbench.resolve_work(None)
        workbench.ensure_workbench_shape(work_root, workspace)
        workbench.save_state(
            work_root,
            {
                "active_unit": "chapter-one",
                "active_path": "drafts/chapter-one.md",
                "selection": {"path": "drafts/chapter-one.md", "text": "beta gamma"},
            },
        )

    def tearDown(self):
        os.chdir(self.old_cwd)
        self.temp.cleanup()

    def test_prepares_input_and_records_status(self):
        work_id, work_root, workspace = workbench.resolve_work(None)
        before = (work_root / "manuscript" / "chapter-one.md").read_text(encoding="utf-8")
        context = bridge.active_workbench_context(work_id, work_root, workspace)
        items = bridge.build_codex_input("What needs attention?", context)
        event = bridge.record_bridge_event(work_id, work_root, workspace, {"type": "unit-test"})
        status = bridge.record_codex_status(work_id, work_root, workspace, {"status": "recorded"})

        self.assertEqual(context["selection"]["text"], "beta gamma")
        self.assertEqual(items[0]["type"], "text")
        self.assertIn("What needs attention?", items[0]["text"])
        self.assertEqual(event["type"], "unit-test")
        self.assertEqual(status["status"], "recorded")
        self.assertTrue((work_root / ".review" / "surface" / "codex-bridge-events.jsonl").is_file())
        self.assertEqual((work_root / "manuscript" / "chapter-one.md").read_text(encoding="utf-8"), before)


if __name__ == "__main__":
    unittest.main()
