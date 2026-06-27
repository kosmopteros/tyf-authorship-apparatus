import http.client
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import threading
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
load_module("tyf_workbench_status")
load_module("tyf_recovery")
live = load_module("tyf_workbench_live")


class WorkbenchRecoveryRoutesTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        for rel in [".tyf", "drafts", "manuscript", "design", "knowledge-base"]:
            (self.root / rel).mkdir(parents=True, exist_ok=True)
        (self.root / "WORKSPACE_STATE.yaml").write_text("active_work: work\n", encoding="utf-8")
        (self.root / "work.yaml").write_text("title: Route Book\nlanguage: en\nstatus: draft\n", encoding="utf-8")
        (self.root / "style-sheet.md").write_text("Voice: calm.\n", encoding="utf-8")
        (self.root / "design" / "book-style.yaml").write_text("font: Charter\n", encoding="utf-8")
        (self.root / "drafts" / "chapter-one.md").write_text("Disk draft.\n", encoding="utf-8")
        (self.root / "manuscript" / "chapter-one.md").write_text("Approved.\n", encoding="utf-8")
        self.old = os.getcwd()
        os.chdir(self.root)
        self.work_id, self.work_root, self.workspace = wb.resolve_work(None)
        wb.ensure_workbench_shape(self.work_root, self.workspace)
        self.token = "route-token"
        handler = live.make_handler(self.work_id, self.work_root, self.workspace, self.token)
        self.server = live.ThreadingServer(("127.0.0.1", 0), handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.port = self.server.server_port

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        os.chdir(self.old)
        self.tmp.cleanup()

    def post(self, path, payload, token=True):
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        headers = {"Content-Type": "application/json"}
        if token:
            headers["X-TYF-Token"] = self.token
        conn.request("POST", path, body=json.dumps(payload), headers=headers)
        response = conn.getresponse()
        data = json.loads(response.read().decode("utf-8"))
        conn.close()
        return response.status, data

    def test_recovery_routes_require_token(self):
        status, data = self.post("/api/save-browser-copy", {"path": "drafts/chapter-one.md", "browser_text": "Browser\n"}, token=False)
        self.assertEqual(status, 403)
        self.assertIn("message", data)

    def test_recovery_routes_work_with_token(self):
        status, data = self.post("/api/reload-disk", {"path": "drafts/chapter-one.md"})
        self.assertEqual(status, 200)
        self.assertEqual(data["text"], "Disk draft.\n")
        status, data = self.post("/api/save-browser-copy", {"path": "drafts/chapter-one.md", "browser_text": "Browser\n"})
        self.assertEqual(status, 200)
        self.assertTrue((self.work_root / data["copy_path"]).is_file())
        status, data = self.post("/api/conflict-packet", {"path": "drafts/chapter-one.md", "loaded_sha256": "old", "browser_text": "Browser\n"})
        self.assertEqual(status, 200)
        self.assertTrue((self.work_root / data["report"]).is_file())


if __name__ == "__main__":
    unittest.main()
