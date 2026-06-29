import importlib.util
import http.client
import json
import os
from pathlib import Path
import sys
import tempfile
import threading
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

spec_bridge = importlib.util.spec_from_file_location("tyf_codex_bridge_v07", SCRIPTS / "tyf_codex_bridge_v07.py")
bridge_v07 = importlib.util.module_from_spec(spec_bridge)
spec_bridge.loader.exec_module(bridge_v07)


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

    def test_approval_aware_bridge_round_trips_decision_to_app_server_client(self):
        runtime = bridge_v07.BridgeRuntime(str(self.root), ["fake-codex"], "gpt-test")

        class FakeClient:
            def __init__(self):
                self.responses = []

            def respond(self, request_id, result):
                self.responses.append({"id": request_id, "result": result})
                return {"status": "sent", "id": request_id, "result": result}

        fake = FakeClient()
        runtime.client = fake
        event = runtime.handle_app_server_message(
            {
                "id": "req-1",
                "method": "item/commandExecution/requestApproval",
                "params": {
                    "approvalId": "approval-1",
                    "threadId": "thr",
                    "turnId": "turn",
                    "itemId": "item",
                    "command": "echo hi",
                },
            }
        )
        self.assertEqual(event["status"], "pending")

        decision = runtime.decide_approval("approval-1", "approved", "looks fine")
        self.assertEqual(decision["status"], "approved")
        self.assertEqual(fake.responses, [{"id": "req-1", "result": {"decision": "accept"}}])
        current = json.loads((self.root / ".review" / "surface" / "codex-approval-current.json").read_text(encoding="utf-8"))
        self.assertEqual(current["app_server_response"]["decision"], "accept")

    def test_approval_aware_bridge_http_decision_endpoint_requires_token_and_responds(self):
        runtime = bridge_v07.BridgeRuntime(str(self.root), ["fake-codex"], "gpt-test")

        class FakeClient:
            def __init__(self):
                self.responses = []

            def respond(self, request_id, result):
                self.responses.append({"id": request_id, "result": result})
                return {"status": "sent", "id": request_id, "result": result}

        fake = FakeClient()
        runtime.client = fake
        runtime.handle_app_server_message(
            {
                "id": "req-2",
                "method": "item/fileChange/requestApproval",
                "params": {"approvalId": "approval-2", "threadId": "thr", "turnId": "turn", "itemId": "item"},
            }
        )
        token = "approval-token"
        server = bridge_v07.base.ThreadingServer(("127.0.0.1", 0), bridge_v07.make_handler(runtime, token))
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            conn = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
            conn.request(
                "POST",
                "/api/approval/decide",
                body=json.dumps({"id": "approval-2", "decision": "rejected", "note": "not now"}),
                headers={"Content-Type": "application/json", "X-TYF-Bridge-Token": token},
            )
            response = conn.getresponse()
            payload = json.loads(response.read().decode("utf-8"))
            conn.close()
        finally:
            server.shutdown()
            server.server_close()
        self.assertEqual(response.status, 200)
        self.assertEqual(payload["decision"]["status"], "rejected")
        self.assertEqual(fake.responses, [{"id": "req-2", "result": {"decision": "decline"}}])


if __name__ == "__main__":
    unittest.main()
