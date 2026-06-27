import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"

spec_v06 = importlib.util.spec_from_file_location("tyf_workbench_v06", SCRIPTS / "tyf_workbench_v06.py")
wb = importlib.util.module_from_spec(spec_v06)
spec_v06.loader.exec_module(wb)
sys.modules["tyf_workbench_v06"] = wb

spec_status = importlib.util.spec_from_file_location("tyf_workbench_status", SCRIPTS / "tyf_workbench_status.py")
status_model = importlib.util.module_from_spec(spec_status)
spec_status.loader.exec_module(status_model)
sys.modules["tyf_workbench_status"] = status_model

spec_live = importlib.util.spec_from_file_location("tyf_workbench_live", SCRIPTS / "tyf_workbench_live.py")
live = importlib.util.module_from_spec(spec_live)
spec_live.loader.exec_module(live)


class WorkbenchStatusTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        for rel in [".tyf", "drafts", "manuscript", "design"]:
            (self.root / rel).mkdir(parents=True, exist_ok=True)
        (self.root / "WORKSPACE_STATE.yaml").write_text("active_work: work\n", encoding="utf-8")
        (self.root / "work.yaml").write_text("title: Status Book\nlanguage: en\nstatus: draft\n", encoding="utf-8")
        (self.root / "style-sheet.md").write_text("Voice: plain.\n", encoding="utf-8")
        (self.root / "design" / "book-style.yaml").write_text("font: Charter\n", encoding="utf-8")
        (self.root / "drafts" / "chapter-one.md").write_text("Alpha beta.\n", encoding="utf-8")
        (self.root / "manuscript" / "chapter-one.md").write_text("Approved alpha.\n", encoding="utf-8")
        self.old = os.getcwd()
        os.chdir(self.root)
        wid, wroot, root = wb.resolve_work(None)
        wb.ensure_workbench_shape(wroot, root)

    def tearDown(self):
        os.chdir(self.old)
        self.tmp.cleanup()

    def test_status_and_stale_detection(self):
        wid, wroot, root = wb.resolve_work(None)
        data = wb.collect_data(wid, wroot, root)
        path = data["units"][0]["draft"]["path"]
        loaded = {path: data["units"][0]["draft"]["sha256"]}
        status = status_model.live_status(wid, wroot, root)
        self.assertEqual(status["drafts"][0]["path"], path)
        self.assertEqual(status_model.stale_drafts_from_loaded(wid, wroot, root, loaded), [])
        (wroot / path).write_text("Changed.\n", encoding="utf-8")
        self.assertEqual(status_model.stale_drafts_from_loaded(wid, wroot, root, loaded)[0]["path"], path)

    def test_live_workbench_html_has_realtime_and_calm_markers(self):
        wid, wroot, root = wb.resolve_work(None)
        html = live.enhanced_html(wb.collect_data(wid, wroot, root, token="test-token"))
        self.assertIn("Assistant status", html)
        self.assertIn("Save safety", html)
        self.assertIn("Needs your approval", html)
        self.assertIn("EventSource('/api/live-events')", html)
        self.assertIn("connectLiveStatus", html)
        self.assertIn("Changed outside this window", html)
        self.assertIn("Safe to save", html)
        self.assertIn("Prepare for manuscript review", html)
        self.assertIn("Share this moment", html)
        self.assertIn("Make footnote candidate", html)


if __name__ == "__main__":
    unittest.main()
