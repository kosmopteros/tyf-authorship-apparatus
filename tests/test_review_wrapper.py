import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

spec = importlib.util.spec_from_file_location("tyf_review", SCRIPTS / "tyf_review.py")
review = importlib.util.module_from_spec(spec)
sys.modules["tyf_review"] = review
spec.loader.exec_module(review)


class ReviewWrapperTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        for rel in [".tyf", "drafts", "manuscript", "design", "knowledge-base"]:
            (self.root / rel).mkdir(parents=True, exist_ok=True)
        (self.root / "WORKSPACE_STATE.yaml").write_text("active_work: work\n", encoding="utf-8")
        (self.root / "work.yaml").write_text("title: Review Wrapper Book\nlanguage: en\nstatus: draft\n", encoding="utf-8")
        (self.root / "style-sheet.md").write_text("Voice: exact.\n", encoding="utf-8")
        (self.root / "design" / "book-style.yaml").write_text("font: Charter\n", encoding="utf-8")
        (self.root / "knowledge-base" / "concepts.jsonl").write_text(
            json.dumps({"canonical": "amanuensis", "variants": ["assistant"], "retired": ["AI writer"]}) + "\n",
            encoding="utf-8",
        )
        (self.root / "knowledge-base" / "voice-map.jsonl").write_text(
            json.dumps({"id": "author-facing", "paths": ["drafts/chapter-one.md"], "avoid": ["side-effecting APIs"]}) + "\n",
            encoding="utf-8",
        )
        (self.root / "drafts" / "chapter-one.md").write_text(
            "The AI writer should not appear. The side-effecting APIs leaked here.\n",
            encoding="utf-8",
        )
        (self.root / "manuscript" / "chapter-one.md").write_text("Approved alpha.\n", encoding="utf-8")
        self.old = os.getcwd()
        os.chdir(self.root)

    def tearDown(self):
        os.chdir(self.old)
        self.tmp.cleanup()

    def test_wrapper_dispatches_graph_concept_continuity_and_polish(self):
        self.assertEqual(review.run(["graph"]), 0)
        self.assertEqual(review.run(["concept"]), 0)
        self.assertEqual(review.run(["continuity"]), 0)
        self.assertEqual(review.run(["polish"]), 0)
        surface = self.root / ".review" / "surface"
        self.assertTrue((surface / "book-graph.json").is_file())
        self.assertTrue((surface / "concept-review.json").is_file())
        self.assertTrue((surface / "continuity-review.json").is_file())
        self.assertTrue((surface / "polish-review.json").is_file())

    def test_wrapper_dispatches_doctor_and_graph_sqlite(self):
        self.assertEqual(review.run(["graph", "--sqlite"]), 0)
        self.assertEqual(review.run(["doctor"]), 0)
        self.assertTrue((self.root / ".tyf" / "graph.sqlite").is_file())
        self.assertTrue((self.root / ".review" / "surface" / "rc-doctor.md").is_file())


if __name__ == "__main__":
    unittest.main()
