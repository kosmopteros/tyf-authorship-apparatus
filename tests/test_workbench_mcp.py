import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
V06_PATH = REPO_ROOT / "scripts" / "tyf_workbench_v06.py"
MCP_PATH = REPO_ROOT / "scripts" / "tyf_workbench_mcp.py"

spec_v06 = importlib.util.spec_from_file_location("tyf_workbench_v06", V06_PATH)
workbench = importlib.util.module_from_spec(spec_v06)
spec_v06.loader.exec_module(workbench)

# The MCP module imports tyf_workbench_v06 by name from scripts/.
import sys
if str(REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.modules["tyf_workbench_v06"] = workbench

spec_mcp = importlib.util.spec_from_file_location("tyf_workbench_mcp", MCP_PATH)
mcp = importlib.util.module_from_spec(spec_mcp)
spec_mcp.loader.exec_module(mcp)


class WorkbenchMCPTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / ".tyf").mkdir()
        (self.root / "drafts").mkdir()
        (self.root / "manuscript").mkdir()
        (self.root / "design").mkdir()
        (self.root / "WORKSPACE_STATE.yaml").write_text("active_work: work\n", encoding="utf-8")
        (self.root / "work.yaml").write_text("title: MCP Book\nlanguage: en\nstatus: draft\n", encoding="utf-8")
        (self.root / "style-sheet.md").write_text("Voice: spare.\n", encoding="utf-8")
        (self.root / "design" / "book-style.yaml").write_text("font: Charter\n", encoding="utf-8")
        (self.root / "drafts" / "chapter-one.md").write_text("Alpha beta gamma.\n", encoding="utf-8")
        (self.root / "drafts" / "chapter-two.md").write_text("Gamma returns later.\n", encoding="utf-8")
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
                "selection": {
                    "path": "drafts/chapter-one.md",
                    "text": "beta gamma",
                    "start_offset": 6,
                    "end_offset": 16,
                },
            },
        )

    def tearDown(self):
        os.chdir(self.old_cwd)
        self.temp.cleanup()

    def server(self):
        return mcp.MCPServer(mcp.WorkbenchContext(str(self.root), None))

    def call_tool(self, name, args=None):
        server = self.server()
        init = server.handle({"jsonrpc": "2.0", "id": 0, "method": "initialize", "params": {}})
        self.assertEqual(init["result"]["serverInfo"]["name"], "tyf-workbench")
        out = server.handle({"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": name, "arguments": args or {}}})
        self.assertIn("result", out)
        return out["result"]["structuredContent"]

    def test_lists_expected_tools_after_initialize(self):
        server = self.server()
        server.handle({"jsonrpc": "2.0", "id": 0, "method": "initialize", "params": {}})
        out = server.handle({"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}})
        names = {tool["name"] for tool in out["result"]["tools"]}
        self.assertIn("get_active_workbench_context", names)
        self.assertIn("prepare_gate_packet", names)
        self.assertIn("record_codex_turn_status", names)
        self.assertNotIn("write_file", names)

    def test_reads_active_context_and_selection(self):
        ctx = self.call_tool("get_active_workbench_context", {"include_text": True})
        self.assertEqual(ctx["work"]["title"], "MCP Book")
        self.assertEqual(ctx["selection"]["text"], "beta gamma")
        self.assertEqual(ctx["active_unit"]["draft"]["path"], "drafts/chapter-one.md")

        selection = self.call_tool("get_active_selection")
        self.assertEqual(selection["selection"]["path"], "drafts/chapter-one.md")

    def test_note_footnote_gate_graph_and_status_actions_do_not_touch_manuscript(self):
        original_manuscript = (self.root / "manuscript" / "chapter-one.md").read_text(encoding="utf-8")
        note = self.call_tool(
            "create_author_note",
            {
                "target_path": "drafts/chapter-one.md",
                "target_kind": "selection",
                "quote": "beta gamma",
                "body": "Footnote this recurrence later.",
                "provenance": "amanuensis",
            },
        )["note"]
        self.assertTrue(note["id"].startswith("note-"))

        footnote = self.call_tool("propose_footnote_from_note", {"note_id": note["id"]})
        self.assertEqual(footnote["status"], "footnote-candidate")
        self.assertTrue((self.root / footnote["markdown"]).is_file())

        draft = (self.root / "drafts" / "chapter-one.md").read_text(encoding="utf-8")
        gate = self.call_tool(
            "prepare_gate_packet",
            {
                "source_path": "drafts/chapter-one.md",
                "base_hash": workbench.sha256_text(draft),
                "selection": "Alpha beta",
                "note": "Candidate opening.",
            },
        )
        self.assertEqual(gate["status"], "packet")
        self.assertTrue((self.root / gate["markdown"]).is_file())

        graph = self.call_tool("refresh_book_graph")
        self.assertEqual(graph["graph"]["kind"], "tyf-book-graph-lite")
        self.assertTrue((self.root / graph["path"]).is_file())

        status = self.call_tool(
            "record_codex_turn_status",
            {"thread_id": "thr", "turn_id": "turn", "status": "completed", "summary": "No manuscript write."},
        )
        self.assertEqual(status["status"], "recorded")
        self.assertTrue((self.root / status["path"]).is_file())

        self.assertEqual((self.root / "manuscript" / "chapter-one.md").read_text(encoding="utf-8"), original_manuscript)

    def test_conflict_detection(self):
        snapshot = workbench.collect_data("work", self.root, self.root)
        old_hash = snapshot["units"][0]["draft"]["sha256"]
        (self.root / "drafts" / "chapter-one.md").write_text("Changed on disk.\n", encoding="utf-8")
        conflicts = self.call_tool(
            "surface_current_conflicts",
            {"path": "drafts/chapter-one.md", "loaded_sha256": old_hash},
        )
        self.assertEqual(len(conflicts["conflicts"]), 1)


if __name__ == "__main__":
    unittest.main()
