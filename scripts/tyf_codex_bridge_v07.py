#!/usr/bin/env python3
"""Approval-aware local TYF bridge for Codex app-server."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import secrets
import sys
import webbrowser
from typing import Any, Dict, List, Optional

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import tyf_codex_approvals as approvals  # noqa: E402
import tyf_codex_bridge as base  # noqa: E402
import tyf_workbench_v06 as wb  # noqa: E402

DEFAULT_PORT = 8771


def approval_result_for(method: str, request_params: Dict[str, Any], decision: str) -> Dict[str, Any]:
    decision = wb.one_line(decision).lower()
    if decision not in ("approved", "rejected", "cancelled"):
        raise ValueError("decision must be approved, rejected, or cancelled")
    if method in ("item/commandExecution/requestApproval", "item/fileChange/requestApproval"):
        return {"decision": {"approved": "accept", "rejected": "decline", "cancelled": "cancel"}[decision]}
    if method == "item/permissions/requestApproval":
        if decision == "approved":
            return {
                "permissions": request_params.get("permissions") if isinstance(request_params.get("permissions"), dict) else {},
                "scope": "turn",
                "strictAutoReview": False,
            }
        return {"permissions": {"fileSystem": None, "network": None}, "scope": "turn", "strictAutoReview": False}
    if method in ("execCommandApproval", "applyPatchApproval"):
        return {"decision": {"approved": "approved", "rejected": "denied", "cancelled": "abort"}[decision]}
    if method == "mcpServer/elicitation/request":
        return {"action": {"approved": "accept", "rejected": "decline", "cancelled": "cancel"}[decision], "content": None}
    if method == "item/tool/requestUserInput":
        return {"answers": {}}
    return {"decision": {"approved": "accept", "rejected": "decline", "cancelled": "cancel"}[decision]}


class BridgeRuntime(base.BridgeRuntime):
    """Bridge runtime that records approval-like app-server notifications."""

    def handle_app_server_message(self, msg: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        method = wb.one_line(msg.get("method"), "notification")
        params = msg.get("params") if isinstance(msg.get("params"), dict) else {}
        self.record({"type": "app-server-notification", "method": method, "params": params})
        event = approvals.record_notification(self.work_id, self.work_root, self.root, method, params)
        if event and "id" in msg:
            event["app_server_request_id"] = msg.get("id")
            event["app_server_method"] = method
            event["app_server_params"] = params
            approvals.append_event(self.work_id, self.work_root, self.root, event)
        if method.startswith("turn/"):
            base.record_codex_status(self.work_id, self.work_root, self.root, {"status": method, "params": params})
        return event

    def decide_approval(self, approval_id: str, decision: str, note: str = "") -> Dict[str, Any]:
        current = approvals.read_json(approvals.current_path(self.work_root), {})
        if approval_id and current.get("id") and current.get("id") != approval_id:
            raise ValueError("approval id does not match the current pending request")
        method = wb.one_line(current.get("app_server_method") or current.get("method"))
        params = current.get("app_server_params") if isinstance(current.get("app_server_params"), dict) else {}
        request_id = current.get("app_server_request_id")
        app_response = approval_result_for(method, params, decision)
        sent = None
        if request_id is not None and self.client is not None:
            responder = getattr(self.client, "respond", None)
            if responder:
                sent = responder(request_id, app_response)
        record = approvals.decide(self.work_id, self.work_root, self.root, approval_id, decision, note)
        record["app_server_request_id"] = request_id
        record["app_server_method"] = method
        record["app_server_response"] = app_response
        if sent:
            record["app_server_sent"] = sent
        return approvals.append_event(self.work_id, self.work_root, self.root, record)

    def client_instance(self) -> base.CodexAppServerClient:
        if self.client is None:
            def on_event(msg: Dict[str, Any]) -> None:
                self.handle_app_server_message(msg)
            self.client = base.CodexAppServerClient(self.codex_command, event_callback=on_event, cwd=str(self.root))
        return self.client


def make_handler(runtime: BridgeRuntime, token: str):
    parent = base.make_handler(runtime, token)

    class Handler(parent):
        server_version = "TYFCodexBridgeApproval/0.2"

        def do_POST(self):  # noqa: N802
            parsed = base.urllib.parse.urlparse(self.path)
            if parsed.path == "/api/approval/decide":
                if not self.require_token():
                    return
                try:
                    payload = self.read_payload()
                    decision = runtime.decide_approval(
                        wb.one_line(payload.get("id") or payload.get("approval_id")),
                        wb.one_line(payload.get("decision")),
                        str(payload.get("note") or ""),
                    )
                    self.json_response(200, {"status": "recorded", "decision": decision})
                except ValueError as exc:
                    self.json_response(400, {"status": "error", "message": str(exc)})
                except Exception as exc:  # noqa: BLE001
                    self.json_response(500, {"status": "error", "message": str(exc)})
                return
            super().do_POST()

    return Handler


def run(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Local TYF bridge to Codex app-server with approval-state recording")
    parser.add_argument("--workspace", default=None)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--allow-remote", action="store_true")
    parser.add_argument("--model", default="gpt-5.5")
    parser.add_argument("--codex-command", default="codex app-server")
    parser.add_argument("--open-status", action="store_true")
    args = parser.parse_args(argv)
    if not args.allow_remote and not base.is_loopback(args.host):
        raise SystemExit("Refused: non-loopback bridge host requires --allow-remote.")
    runtime = BridgeRuntime(args.workspace, args.codex_command.split(), args.model)
    session_key = secrets.token_urlsafe(24)
    server = base.ThreadingServer((args.host, args.port), make_handler(runtime, session_key))
    url = f"http://{args.host}:{server.server_port}"
    runtime.record({"type": "bridge-started", "url": url, "approval_model": True})
    print(f"TYF approval-aware Codex bridge: {url}")
    print("Side-effecting bridge APIs require X-TYF-Bridge-Token.")
    print(f"Token: {session_key}")
    if args.open_status:
        webbrowser.open(url + "/status")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped TYF approval-aware Codex bridge.")
    finally:
        if runtime.client:
            runtime.client.close()
    return 0


def main() -> None:
    raise SystemExit(run())


if __name__ == "__main__":
    main()
