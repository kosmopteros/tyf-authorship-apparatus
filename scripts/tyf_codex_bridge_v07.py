#!/usr/bin/env python3
"""Approval-aware local TYF bridge for Codex app-server."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import secrets
import socketserver
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


class BridgeRuntime(base.BridgeRuntime):
    """Bridge runtime that records approval-like app-server notifications."""

    def client_instance(self) -> base.CodexAppServerClient:
        if self.client is None:
            def on_event(msg: Dict[str, Any]) -> None:
                method = wb.one_line(msg.get("method"), "notification")
                params = msg.get("params") if isinstance(msg.get("params"), dict) else {}
                self.record({"type": "app-server-notification", "method": method, "params": params})
                approvals.record_notification(self.work_id, self.work_root, self.root, method, params)
                if method.startswith("turn/"):
                    base.record_codex_status(self.work_id, self.work_root, self.root, {"status": method, "params": params})
            self.client = base.CodexAppServerClient(self.codex_command, event_callback=on_event, cwd=str(self.root))
        return self.client


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
    server = base.ThreadingServer((args.host, args.port), base.make_handler(runtime, session_key))
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
