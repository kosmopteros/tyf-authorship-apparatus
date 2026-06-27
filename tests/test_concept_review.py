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


class ConceptReviewTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        for rel in [".tyf", "drafts", "manuscript", "design", "knowledge-base"]:
            (self.root / rel).mkdir(parents=True, exist_ok=True)
        (self.root / "WORKSPACE_STATE.yaml").write_text("active_work: work\n", encoding="utf-8")
        (self.root / "work.yaml").write_text("title: Concept Book\nlanguage: en\nstatus: draft\n", encoding="utf-8")
        (self.root / "style-sheet.md").write_text("Voice: exact.\n", encoding="utf-8")
        (self.root / "design" / "book-style.yaml").write_text("font: Charter\n", encoding="utf-8")
        (self.root / "knowledge-base" / "concepts.jsonl").write_text(
            json.dumps({"canonical": "amanuensis", "variants": ["assistant"], "retired": ["AI writer"], "note": "TYF is not an AI writer."}) + "\n",
            encoding="utf-8",
        )
        (self.root / "drafts" / "chapter-one.md").write_text(
            "The amanuensis can help the author.\nThe AI writer should not appear anymore.\nThe assistant cannot decide the manuscript.\nAmanuensis is a faithful helper.\nAmanuensis is not the author.\n",
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

    def test_concept_review_finds_rename_and_drift(self):
        result = concept.write_outputs(self.work_root)
        self.assertTrue((self.work_root / result["index"]).is_file())
        self.assertTrue((self.work_root / result["review_markdown"]).is_file())
        review = json.loads((self.work_root / result["review_json"]).read_text(encoding="utf-8"))
        kinds = {item["kind"] for item in review["issues"]}
        self.assertIn("retired-term-used", kinds)
        self.assertIn("concept-variant", kinds)
        self.assertIn("opposition-drift", kinds)
        self.assertIn("definition-drift", kinds)
        self.assertGreater(result["issues"], 0)


if __name__ == "__main__":
    unittest.main()
