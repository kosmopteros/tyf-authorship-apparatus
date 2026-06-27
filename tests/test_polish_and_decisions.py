import importlib.util
import json
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

spec_concept = importlib.util.spec_from_file_location("tyf_concept_review", SCRIPTS / "tyf_concept_review.py")
concept = importlib.util.module_from_spec(spec_concept)
spec_concept.loader.exec_module(concept)
sys.modules["tyf_concept_review"] = concept

spec_decision = importlib.util.spec_from_file_location("tyf_continuity_decision", SCRIPTS / "tyf_continuity_decision.py")
decision = importlib.util.module_from_spec(spec_decision)
spec_decision.loader.exec_module(decision)

spec_polish = importlib.util.spec_from_file_location("tyf_polish_review", SCRIPTS / "tyf_polish_review.py")
polish = importlib.util.module_from_spec(spec_polish)
spec_polish.loader.exec_module(polish)


class PolishAndDecisionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        for rel in [".tyf", "drafts", "manuscript", "design", "knowledge-base"]:
            (self.root / rel).mkdir(parents=True, exist_ok=True)
        (self.root / "WORKSPACE_STATE.yaml").write_text("active_work: work\n", encoding="utf-8")
        (self.root / "work.yaml").write_text("title: Polish Book\nlanguage: en\nstatus: draft\n", encoding="utf-8")
        (self.root / "style-sheet.md").write_text("Voice: exact.\n", encoding="utf-8")
        (self.root / "design" / "book-style.yaml").write_text("font: Charter\n", encoding="utf-8")
        (self.root / "knowledge-base" / "voice-map.jsonl").write_text(
            json.dumps({"id": "third-calm", "paths": ["drafts/chapter-one.md"], "person": "third", "avoid": ["side-effecting APIs"]}) + "\n",
            encoding="utf-8",
        )
        (self.root / "knowledge-base" / "typography-style.jsonl").write_text(
            json.dumps({"dash": "em-dash", "ellipsis": "single-character", "capitalization": {"gate": "Gate"}}) + "\n",
            encoding="utf-8",
        )
        (self.root / "drafts" / "chapter-one.md").write_text(
            "I entered the gate -- slowly...\nThe side-effecting APIs leaked into the voice.\n",
            encoding="utf-8",
        )
        (self.root / "manuscript" / "chapter-one.md").write_text("Approved alpha.\n", encoding="utf-8")
        self.old = os.getcwd()
        os.chdir(self.root)
        self.work_id, self.work_root, self.workspace = wb.resolve_work(None)
        wb.ensure_workbench_shape(self.work_root, self.workspace)

    def tearDown(self):
        os.chdir(self.old)
        self.tmp.cleanup()

    def test_decision_writer_records_latest_decision(self):
        record = decision.record_decision(self.work_id, self.work_root, self.workspace, "issue-1", "intentional", "planned break")
        self.assertEqual(record["status"], "intentional")
        latest = decision.latest_decisions(self.work_root)
        self.assertEqual(latest["issue-1"]["note"], "planned break")

    def test_polish_review_detects_voice_and_typography(self):
        result = polish.write_outputs(self.work_root)
        self.assertTrue((self.work_root / result["review_json"]).is_file())
        review = json.loads((self.work_root / result["review_json"]).read_text(encoding="utf-8"))
        kinds = {item["kind"] for item in review["issues"]}
        self.assertIn("narration-lane-mismatch", kinds)
        self.assertIn("register-leak", kinds)
        self.assertIn("dash-style-drift", kinds)
        self.assertIn("ellipsis-style-drift", kinds)
        self.assertIn("term-capitalization-drift", kinds)
        self.assertGreater(result["issues"], 0)


if __name__ == "__main__":
    unittest.main()
