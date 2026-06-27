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

spec_cont = importlib.util.spec_from_file_location("tyf_continuity_review", SCRIPTS / "tyf_continuity_review.py")
continuity = importlib.util.module_from_spec(spec_cont)
spec_cont.loader.exec_module(continuity)


class ContinuityReviewTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        for rel in [".tyf", "drafts", "manuscript", "design", "knowledge-base"]:
            (self.root / rel).mkdir(parents=True, exist_ok=True)
        (self.root / "WORKSPACE_STATE.yaml").write_text("active_work: work\n", encoding="utf-8")
        (self.root / "work.yaml").write_text("title: Continuity Book\nlanguage: en\nstatus: draft\n", encoding="utf-8")
        (self.root / "style-sheet.md").write_text("Voice: exact.\n", encoding="utf-8")
        (self.root / "design" / "book-style.yaml").write_text("font: Charter\n", encoding="utf-8")
        (self.root / "knowledge-base" / "concepts.jsonl").write_text(
            json.dumps({"canonical": "amanuensis", "variants": ["assistant"], "retired": ["AI writer"]}) + "\n",
            encoding="utf-8",
        )
        (self.root / "knowledge-base" / "reader-promises.jsonl").write_text(
            json.dumps({"id": "gate-payoff", "promise": "why the Gate matters", "promise_terms": ["why the Gate matters"], "payoff_terms": ["Gate matters because"]}) + "\n",
            encoding="utf-8",
        )
        (self.root / "knowledge-base" / "open-threads.jsonl").write_text(
            json.dumps({"id": "local-first-objection", "thread": "local first objection", "terms": ["local-first objection"], "resolution_terms": ["answer the local-first objection"]}) + "\n",
            encoding="utf-8",
        )
        (self.root / "knowledge-base" / "register-rules.jsonl").write_text(
            json.dumps({"id": "author-facing", "register": "author-facing", "avoid": ["side-effecting APIs"]}) + "\n",
            encoding="utf-8",
        )
        (self.root / "knowledge-base" / "scope-rules.jsonl").write_text(
            json.dumps({"id": "main-book", "scope": "main book", "leak_terms": ["implementation detail"], "allowed_paths": ["docs/"]}) + "\n",
            encoding="utf-8",
        )
        (self.root / "drafts" / "chapter-one.md").write_text(
            "You will see why the Gate matters.\nThe local-first objection appears here.\nOf course the assistant understands this.\nThe side-effecting APIs are mentioned in the main draft.\nThis implementation detail belongs elsewhere.\nThe AI writer should not appear.\nAmanuensis is a faithful helper.\nAmanuensis is not the author.\n",
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

    def test_continuity_review_detects_registry_issues(self):
        result = continuity.write_outputs(self.work_root)
        self.assertTrue((self.work_root / result["review_json"]).is_file())
        self.assertTrue((self.work_root / result["review_markdown"]).is_file())
        review = json.loads((self.work_root / result["review_json"]).read_text(encoding="utf-8"))
        kinds = {item["kind"] for item in review["issues"]}
        self.assertIn("unpaid-promise", kinds)
        self.assertIn("dangling-open-thread", kinds)
        self.assertIn("register-drift", kinds)
        self.assertIn("scope-leak", kinds)
        self.assertIn("reader-state-assumption", kinds)
        self.assertIn("retired-term-used", kinds)
        self.assertGreater(result["issues"], 0)


if __name__ == "__main__":
    unittest.main()
