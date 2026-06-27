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

spec = importlib.util.spec_from_file_location("tyf_codex_approvals", SCRIPTS / "tyf_codex_approvals.py")
approvals = importlib.util.module_from_spec(spec)
spec.loader.exec_module(approvals)


class ApprovalEventTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        for rel in [".tyf", "drafts", "manuscript", "design"]:
            (self.root / rel).mkdir(parents=True, exist_ok=True)
        (self.root / "WORKSPACE_STATE.yaml").write_text("active_work: work\n", encoding="utf-8")
        (self.root / "work.yaml").write_text("title: Approval Book\nlanguage: en\nstatus: draft\n", encoding="utf-8")
        (self.root / "style-sheet.md").write_text("Voice: clear.\n", encoding="utf-8")
        (self.root / "design" / "book-style.yaml").write_text("font: Charter\n", encoding="utf-8")
        self.old = os.getcwd()
        os.chdir(self.root)
        wid, wroot, root = wb.resolve_work(None)
        wb.ensure_workbench_shape(wroot, root)

    def tearDown(self):
        os.chdir(self.old)
        self.tmp.cleanup()

    def test_record_and_decide(self):
        wid, wroot, root = wb.resolve_work(None)
        event = approvals.record_notification(wid, wroot, root, "approval_request", {"approval_id": "a1", "tool": "demo", "message": "review"})
        self.assertEqual(event["status"], "pending")
        decision = approvals.decide(wid, wroot, root, "a1", "approved", "ok")
        self.assertEqual(decision["status"], "approved")
        self.assertTrue((wroot / ".review" / "surface" / "codex-approval-events.jsonl").is_file())


if __name__ == "__main__":
    unittest.main()
