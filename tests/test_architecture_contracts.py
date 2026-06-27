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


contracts = load_module("tyf_architecture_contracts")
slots = load_module("tyf_workbench_slots")
wb = load_module("tyf_workbench_v06")
load_module("tyf_workbench_status")
load_module("tyf_recovery")
live = load_module("tyf_workbench_live")


class ArchitectureContractTests(unittest.TestCase):
    def test_storage_contract_has_required_classes(self):
        classes = contracts.storage_contract()
        for name in [
            "canonical-prose",
            "canonical-author-record",
            "mutable-record-store",
            "hash-chain-ledger",
            "append-log",
            "generated-review",
            "rebuildable-cache",
            "recovery-artifact",
        ]:
            self.assertIn(name, classes)

    def test_no_forbidden_manuscript_routes(self):
        self.assertEqual(contracts.forbidden_route_hits(ROOT), [])

    def test_slot_helper_fails_loudly_on_missing_anchor(self):
        with self.assertRaises(slots.WorkbenchSlotError):
            slots.apply_workbench_slots("<html></html>", slots.WorkbenchSlots(aside_before_images="x"))

    def test_live_html_uses_slot_helper_markers(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for rel in [".tyf", "drafts", "manuscript", "design", "knowledge-base"]:
                (root / rel).mkdir(parents=True, exist_ok=True)
            (root / "WORKSPACE_STATE.yaml").write_text("active_work: work\n", encoding="utf-8")
            (root / "work.yaml").write_text("title: Slot Book\nlanguage: en\nstatus: draft\n", encoding="utf-8")
            (root / "style-sheet.md").write_text("Voice: calm.\n", encoding="utf-8")
            (root / "design" / "book-style.yaml").write_text("font: Charter\n", encoding="utf-8")
            (root / "drafts" / "chapter-one.md").write_text("Draft.\n", encoding="utf-8")
            (root / "manuscript" / "chapter-one.md").write_text("Approved.\n", encoding="utf-8")
            old = os.getcwd()
            os.chdir(root)
            try:
                work_id, work_root, workspace = wb.resolve_work(None)
                wb.ensure_workbench_shape(work_root, workspace)
                html = live.enhanced_html(wb.collect_data(work_id, work_root, workspace, token="token"))
                self.assertIn("Review dashboard", html)
                self.assertIn("Prepare conflict packet", html)
                self.assertIn("Save my version as copy", html)
            finally:
                os.chdir(old)


if __name__ == "__main__":
    unittest.main()
