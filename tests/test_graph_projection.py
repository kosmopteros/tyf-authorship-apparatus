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

spec_graph = importlib.util.spec_from_file_location("tyf_graph_projection", SCRIPTS / "tyf_graph_projection.py")
graph = importlib.util.module_from_spec(spec_graph)
spec_graph.loader.exec_module(graph)


class GraphProjectionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        for rel in [".tyf", "drafts", "manuscript", "design", "knowledge-base"]:
            (self.root / rel).mkdir(parents=True, exist_ok=True)
        (self.root / "WORKSPACE_STATE.yaml").write_text("active_work: work\n", encoding="utf-8")
        (self.root / "work.yaml").write_text("title: Graph Book\nlanguage: en\nstatus: draft\n", encoding="utf-8")
        (self.root / "style-sheet.md").write_text("Voice: exact.\n", encoding="utf-8")
        (self.root / "design" / "book-style.yaml").write_text("font: Charter\n", encoding="utf-8")
        (self.root / "drafts" / "chapter-one.md").write_text("Alpha beta motif.\n", encoding="utf-8")
        (self.root / "drafts" / "chapter-two.md").write_text("The motif returns.\n", encoding="utf-8")
        (self.root / "manuscript" / "chapter-one.md").write_text("Approved alpha.\n", encoding="utf-8")
        self.old = os.getcwd()
        os.chdir(self.root)
        self.work_id, self.work_root, self.workspace = wb.resolve_work(None)
        wb.ensure_workbench_shape(self.work_root, self.workspace)
        wb.log_event(self.workspace, "unit-test", self.work_id, "first")
        data = wb.collect_data(self.work_id, self.work_root, self.workspace)
        draft = data["units"][0]["draft"]
        note = wb.create_author_note(
            self.work_id,
            self.work_root,
            self.workspace,
            {"target_path": draft["path"], "target_kind": "selection", "quote": "Alpha", "body": "Remember the motif here.", "provenance": "author"},
        )["note"]
        wb.footnote_candidate(self.work_id, self.work_root, self.workspace, note["id"])
        wb.gate_packet(self.work_id, self.work_root, self.workspace, {"path": draft["path"], "base_hash": draft["sha256"], "selection": "Alpha beta", "note": "ready"})
        surface = self.work_root / ".review" / "surface"
        surface.mkdir(parents=True, exist_ok=True)
        with (surface / "codex-turn-status.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps({"kind": "codex-turn-status", "status": "completed", "active_path": draft["path"]}) + "\n")

    def tearDown(self):
        os.chdir(self.old)
        self.tmp.cleanup()

    def test_audits_jsonl_and_builds_graph_outputs(self):
        audit = graph.audit_jsonl_ledgers(self.work_root)
        classes = {item["path"]: item["classification"] for item in audit["files"]}
        self.assertEqual(classes[".tyf/events.jsonl"], "hash-chain-ledger")
        self.assertIn("knowledge-base/author-notes.jsonl", classes)
        result = graph.write_outputs(self.work_id, self.work_root, self.workspace, include_sqlite=True)
        self.assertTrue((self.work_root / result["graph"]).is_file())
        self.assertTrue((self.work_root / result["report_markdown"]).is_file())
        self.assertTrue((self.work_root / result["sqlite"]).is_file())
        payload = json.loads((self.work_root / result["graph"]).read_text(encoding="utf-8"))
        self.assertEqual(payload["kind"], "tyf-book-graph")
        self.assertGreater(payload["nodes"].__len__(), 0)
        self.assertGreater(payload["edges"].__len__(), 0)
        self.assertIn("Derived projection only", payload["truth_model"])
        edge_kinds = {edge["kind"] for edge in payload["edges"]}
        self.assertIn("has-unit", edge_kinds)
        self.assertIn("notes", edge_kinds)
        self.assertIn("has-ledger-or-log", edge_kinds)


if __name__ == "__main__":
    unittest.main()
