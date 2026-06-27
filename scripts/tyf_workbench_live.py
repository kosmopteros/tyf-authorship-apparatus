#!/usr/bin/env python3
"""Live TYF Workbench wrapper with Codex status and stale draft badges."""

from __future__ import annotations

import argparse
import http.server
import json
from pathlib import Path
import secrets
import socketserver
import sys
import urllib.parse
import webbrowser
from typing import Any, Dict, Optional

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import tyf_workbench_v06 as wb  # noqa: E402
import tyf_workbench_status as status_model  # noqa: E402

DEFAULT_PORT = 8767
MAX_POST_BYTES = 4 * 1024 * 1024

PANEL = """      <section>
        <strong>Codex status</strong>
        <div id="codexStatusBox" class="note-card"><div class="meta">No Codex status recorded yet.</div></div>
      </section>
      <section>
        <strong>Draft state</strong>
        <div id="conflictBadge" class="note-card"><div class="meta">Draft state not checked yet.</div></div>
      </section>
      <section>
        <strong>Approval requests</strong>
        <div id="approvalBox" class="note-card"><div class="meta">No pending approval request.</div></div>
      </section>
"""

SCRIPT = r"""
    function objectSummary(obj) {
      if (!obj || Object.keys(obj).length === 0) return '<div class="meta">none</div>';
      const label = obj.status || obj.method || obj.type || obj.kind || 'recorded';
      const when = obj.created_at || obj.updated_at || '';
      const summary = obj.summary || obj.message || obj.title || obj.method || '';
      const paths = Array.isArray(obj.changed_paths) && obj.changed_paths.length ? `<div class="meta">${esc(obj.changed_paths.join(', '))}</div>` : '';
      return `<div><strong>${esc(label)}</strong></div><div class="body">${esc(summary)}</div><div class="meta">${esc(when)}</div>${paths}`;
    }
    function renderLiveStatus(live) {
      const codex = live.codex || {};
      const bridge = live.bridge || {};
      const approval = live.approval || {};
      document.getElementById('codexStatusBox').innerHTML = objectSummary(Object.keys(codex).length ? codex : bridge);
      document.getElementById('approvalBox').innerHTML = Object.keys(approval).length ? `<div><strong>${esc(approval.status || 'pending')}</strong></div><div class="body">${esc(approval.title || approval.method || 'Codex approval request')}</div><div class="meta">${esc(approval.id || '')}</div>` : '<div class="meta">No pending approval request.</div>';
      const d = activeDraft();
      const row = d ? (live.drafts || []).find(x => x.path === d.path) : null;
      const stale = !!(row && d && d.sha256 && row.sha256 && row.sha256 !== d.sha256);
      if (stale) document.getElementById('conflictBadge').innerHTML = `<div class="warn"><strong>Stale draft on disk</strong></div><div class="meta">${esc(d.path)}</div>`;
      else if (d && row) document.getElementById('conflictBadge').innerHTML = `<div class="ok"><strong>Draft hash current</strong></div><div class="meta">${esc(d.path)}</div>`;
      else document.getElementById('conflictBadge').innerHTML = '<div class="meta">No active draft to check.</div>';
    }
    async function pollLiveStatus() {
      try { renderLiveStatus(await fetch('/api/live-status', {cache:'no-store'}).then(r => r.json())); }
      catch (err) { document.getElementById('codexStatusBox').innerHTML = '<div class="warn">Live status unavailable.</div>'; }
    }
"""


def enhanced_html(data: Dict[str, Any]) -> str:
    html = wb.surface_html(data)
    html = html.replace("      <section>\n        <strong>Images</strong>", PANEL + "      <section>\n        <strong>Images</strong>")
    html = html.replace("    document.getElementById('refreshData').addEventListener('click', reload);\n    render();", "    document.getElementById('refreshData').addEventListener('click', async () => { await reload(); await pollLiveStatus(); });\n" + SCRIPT + "\n    render();\n    pollLiveStatus();\n    setInterval(pollLiveStatus, 3000);")
    return html


class ThreadingServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True


def is_loopback(host: str) -> bool:
    return host in ("127.0.0.1", "localhost", "::1")


def make_handler(work_id: str, work_root: Path, workspace: Path, session_key: str):
    base = wb.make_handler(work_id, work_root, workspace, session_key)

    class Handler(base):
        server_version = "TYFWorkbenchLive/0.1"

        def do_GET(self):  # noqa: N802
            parsed = urllib.parse.urlparse(self.path)
            if parsed.path in ("/", "/index.html", "/workbench-live.html"):
                self.html_response(enhanced_html(wb.collect_data(work_id, work_root, workspace, token=session_key)))
            elif parsed.path == "/api/live-status":
                self.json_response(200, status_model.live_status(work_id, work_root, workspace))
            else:
                super().do_GET()

    return Handler


def run(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="TYF live Workbench with Codex status and conflict badges")
    parser.add_argument("work", nargs="?", default=None)
    parser.add_argument("--serve", action="store_true")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--open", action="store_true")
    parser.add_argument("--allow-remote", action="store_true")
    args = parser.parse_args(argv)
    work_id, work_root, workspace = wb.resolve_work(args.work)
    wb.ensure_workbench_shape(work_root, workspace)
    session_key = secrets.token_urlsafe(24) if args.serve else ""
    data = wb.collect_data(work_id, work_root, workspace, token=session_key)
    out_dir = work_root / ".review" / "surface"
    out_dir.mkdir(parents=True, exist_ok=True)
    html_path = out_dir / "workbench-live.html"
    data_path = out_dir / "workbench-live-data.json"
    wb.atomic_write(html_path, enhanced_html(data))
    wb.write_json(data_path, data)
    wb.log_event(workspace, "workbench-live", work_id, html_path.relative_to(work_root).as_posix())
    print(f"TYF live Workbench: {html_path.relative_to(work_root).as_posix()}")
    print("No manuscript text was written. manuscript/ remains Gate-only.")
    if args.serve:
        if not args.allow_remote and not is_loopback(args.host):
            raise SystemExit("Refused: non-loopback host requires --allow-remote.")
        server = ThreadingServer((args.host, args.port), make_handler(work_id, work_root, workspace, session_key))
        url = f"http://{args.host}:{server.server_port}/"
        print(f"Serving TYF live Workbench at {url}")
        if args.open:
            webbrowser.open(url)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nStopped TYF live Workbench.")
    return 0


def main(argv: Optional[list[str]] = None) -> None:
    raise SystemExit(run(argv))


if __name__ == "__main__":
    main()
