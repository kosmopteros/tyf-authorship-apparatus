import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"


def load_module(name):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    sys.modules[name] = module
    return module


wb = load_module("tyf_workbench_v06")
load_module("tyf_concept_review")
load_module("tyf_continuity_review")
load_module("tyf_graph_projection")
load_module("tyf_polish_review")
load_module("tyf_workbench_status")
recovery = load_module("tyf_recovery")
live = load_module("tyf_workbench_live")
doctor_mod = load_module("tyf_rc_doctor")


class RcRecoveryDoctorTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        for rel in [".tyf", "drafts", "manuscript", "design", "knowledge-base"]:
            (self.root / rel).mkdir(parents=True, exist_ok=True)
        (self.root / "WORKSPACE_STATE.yaml").write_text("active_work: work\n", encoding="utf-8")
        (self.root / "work.yaml").write_text("title: RC Book\nlanguage: en\nstatus: draft\n", encoding="utf-8")
        (self.root / "style-sheet.md").write_text("Voice: calm.\n", encoding="utf-8")
        (self.root / "design" / "book-style.yaml").write_text("font: Charter\n", encoding="utf-8")
        (self.root / "drafts" / "chapter-one.md").write_text("Original draft.\n", encoding="utf-8")
        (self.root / "manuscript" / "chapter-one.md").write_text("Approved draft.\n", encoding="utf-8")
        self.old = os.getcwd()
        os.chdir(self.root)
        self.work_id, self.work_root, self.workspace = wb.resolve_work(None)
        wb.ensure_workbench_shape(self.work_root, self.workspace)
        wb.log_event(self.workspace, "unit-test", self.work_id, "ready")

    def tearDown(self):
        os.chdir(self.old)
        self.tmp.cleanup()

    def test_recovery_copy_packet_and_reload(self):
        source = "drafts/chapter-one.md"
        browser_text = "Browser draft.\n"
        copy = recovery.save_browser_copy(self.work_id, self.work_root, self.workspace, source, browser_text, "test")
        self.assertTrue((self.work_root / copy["copy_path"]).is_file())
        packet = recovery.write_conflict_packet(self.work_id, self.work_root, self.workspace, source, "loaded-hash", browser_text, "test")
        self.assertTrue((self.work_root / packet["report"]).is_file())
        disk = recovery.reload_disk_version(self.work_root, source)
        self.assertEqual(disk["text"], "Original draft.\n")

    def test_rc_doctor_passes_and_live_html_has_markers(self):
        result = doctor_mod.doctor(None)
        self.assertEqual(result["status"], "pass")
        self.assertTrue((self.work_root / result["report_markdown"]).is_file())
        html = live.enhanced_html(wb.collect_data(self.work_id, self.work_root, self.workspace, token="token"))
        self.assertIn("Review dashboard", html)
        self.assertIn("Reload disk version", html)
        self.assertIn("Save my version as copy", html)


if __name__ == "__main__":
    unittest.main()
