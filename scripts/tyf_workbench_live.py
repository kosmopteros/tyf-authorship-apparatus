#!/usr/bin/env python3
"""Live TYF Workbench wrapper with near-real-time status and recovery actions."""

from __future__ import annotations

import argparse
import http.server
import json
from pathlib import Path
import secrets
import socketserver
import sys
import time
import urllib.parse
import webbrowser
from typing import Any, Dict, Optional

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import tyf_recovery as recovery  # noqa: E402
import tyf_workbench_slots as slots  # noqa: E402
import tyf_workbench_v06 as wb  # noqa: E402
import tyf_workbench_status as status_model  # noqa: E402

DEFAULT_PORT = 8767
MAX_POST_BYTES = 4 * 1024 * 1024
LIVE_EVENT_INTERVAL_SEC = 1.0
LIVE_EVENT_LIMIT = 180

PANEL = """      <section>
        <strong>Assistant status</strong>
        <div id="codexStatusBox" class="note-card"><div class="meta">No assistant status recorded yet.</div></div>
      </section>
      <section>
        <strong>Save safety</strong>
        <div id="conflictBadge" class="note-card"><div class="meta">Draft state not checked yet.</div></div>
      </section>
      <section>
        <strong>Review dashboard</strong>
        <div id="reviewDashboardBox" class="note-card"><div class="meta">Run continuity/polish reviews to see a summary here.</div></div>
      </section>
      <section>
        <strong>Needs your approval</strong>
        <div id="approvalBox" class="note-card"><div class="meta">No pending approval request.</div></div>
      </section>
"""

SCRIPT = r"""
    let liveStatusTimer = null;
    function objectSummary(obj) {
      if (!obj || Object.keys(obj).length === 0) return '<div class="meta">none</div>';
      const label = obj.status || obj.method || obj.type || obj.kind || 'recorded';
      const when = obj.created_at || obj.updated_at || '';
      const summary = obj.summary || obj.message || obj.title || obj.method || '';
      const paths = Array.isArray(obj.changed_paths) && obj.changed_paths.length ? `<div class="meta">${esc(obj.changed_paths.join(', '))}</div>` : '';
      return `<div><strong>${esc(label)}</strong></div><div class="body">${esc(summary)}</div><div class="meta">${esc(when)}</div>${paths}`;
    }
    function reviewLine(name, item) {
      if (!item || !item.exists) return `<div class="meta">${esc(name)}: not run</div>`;
      const counts = item.counts || {};
      const total = counts.total || 0;
      const likely = counts['likely-fix'] || 0;
      const review = counts.review || 0;
      const low = counts.low || 0;
      return `<div><strong>${esc(name)}</strong>: ${total}</div><div class="meta">${likely} likely fixes · ${review} review · ${low} low</div><div class="meta">${esc(item.path || '')}</div>`;
    }
    function renderReviewDashboard(dashboard) {
      dashboard = dashboard || {};
      document.getElementById('reviewDashboardBox').innerHTML = [
        reviewLine('Continuity', dashboard.continuity),
        reviewLine('Polish', dashboard.polish),
        reviewLine('Concepts', dashboard.concept),
        dashboard.graph && dashboard.graph.exists ? `<div><strong>Graph</strong>: ${dashboard.graph.nodes || 0} nodes · ${dashboard.graph.edges || 0} edges</div><div class="meta">${esc(dashboard.graph.path || '')}</div>` : '<div class="meta">Graph: not run</div>'
      ].join('<hr>');
    }
    async function postRecovery(url, payload) {
      const response = await fetch(url, {method:'POST', headers:{'Content-Type':'application/json','X-TYF-Token':data.token || ''}, body: JSON.stringify(payload || {})});
      const result = await response.json();
      if (!response.ok) throw result;
      return result;
    }
    function wireRecoveryButtons(d) {
      const reloadBtn = document.getElementById('reloadDiskDraft');
      const copyBtn = document.getElementById('saveBrowserCopy');
      const packetBtn = document.getElementById('prepareConflictPacket');
      if (reloadBtn) reloadBtn.onclick = async () => {
        if (!confirm('Replace the browser text with the current disk draft? Save your version as a copy first if unsure.')) return;
        try {
          const r = await postRecovery('/api/reload-disk', {path: d.path});
          draft.value = r.text || '';
          draft.dataset.baseHash = r.sha256 || '';
          d.text = r.text || '';
          d.sha256 = r.sha256 || '';
          setStatus('Reloaded disk version. Your browser text was replaced by the current disk draft.', 'ok');
          await pollLiveStatus();
        } catch (err) { setStatus(err.message || 'Could not reload disk version.', 'warn'); }
      };
      if (copyBtn) copyBtn.onclick = async () => {
        try {
          const r = await postRecovery('/api/save-browser-copy', {path: d.path, browser_text: draft.value, note: 'Saved from Workbench recovery action'});
          setStatus('Saved browser version as copy: ' + r.copy_path, 'ok');
        } catch (err) { setStatus(err.message || 'Could not save browser copy.', 'warn'); }
      };
      if (packetBtn) packetBtn.onclick = async () => {
        try {
          const r = await postRecovery('/api/conflict-packet', {path: d.path, loaded_sha256: d.sha256 || draft.dataset.baseHash || '', browser_text: draft.value, note: 'Prepared from Workbench recovery action'});
          setStatus('Prepared conflict packet: ' + r.report, 'ok');
        } catch (err) { setStatus(err.message || 'Could not prepare conflict packet.', 'warn'); }
      };
    }
    function renderLiveStatus(live) {
      const codex = live.codex || {};
      const bridge = live.bridge || {};
      const approval = live.approval || {};
      document.getElementById('codexStatusBox').innerHTML = objectSummary(Object.keys(codex).length ? codex : bridge);
      document.getElementById('approvalBox').innerHTML = Object.keys(approval).length ? `<div><strong>${esc(approval.status || 'pending')}</strong></div><div class="body">${esc(approval.title || approval.method || 'Approval requested')}</div><div class="meta">${esc(approval.id || '')}</div>` : '<div class="meta">No pending approval request.</div>';
      renderReviewDashboard(live.review_dashboard || {});
      const d = activeDraft();
      const row = d ? (live.drafts || []).find(x => x.path === d.path) : null;
      const stale = !!(row && d && d.sha256 && row.sha256 && row.sha256 !== d.sha256);
      if (stale) {
        document.getElementById('conflictBadge').innerHTML = `<div class="warn"><strong>Changed outside this window</strong></div><div class="meta">${esc(d.path)}</div><div style="margin-top:8px"><button id="saveBrowserCopy">Save my version as copy</button> <button id="prepareConflictPacket">Prepare conflict packet</button> <button id="reloadDiskDraft">Reload disk version</button></div>`;
        wireRecoveryButtons(d);
      }
      else if (d && row) document.getElementById('conflictBadge').innerHTML = `<div class="ok"><strong>Safe to save</strong></div><div class="meta">${esc(d.path)}</div>`;
      else document.getElementById('conflictBadge').innerHTML = '<div class="meta">No active draft to check.</div>';
    }
    async function pollLiveStatus() {
      try { renderLiveStatus(await fetch('/api/live-status', {cache:'no-store'}).then(r => r.json())); }
      catch (err) { document.getElementById('codexStatusBox').innerHTML = '<div class="warn">Live status unavailable.</div>'; }
    }
    function startLivePolling() {
      if (liveStatusTimer) return;
      pollLiveStatus();
      liveStatusTimer = setInterval(pollLiveStatus, 3000);
    }
    function connectLiveStatus() {
      if (!window.EventSource) { startLivePolling(); return; }
      const stream = new EventSource('/api/live-events');
      stream.onmessage = event => {
        try { renderLiveStatus(JSON.parse(event.data)); }
        catch (err) { startLivePolling(); }
      };
      stream.onerror = () => {
        stream.close();
        startLivePolling();
      };
    }
"""


def enhanced_html(data: Dict[str, Any]) -> str:
    return slots.apply_workbench_slots(
        wb.surface_html(data),
        slots.WorkbenchSlots(
            aside_before_images=PANEL,
            script_before_render=SCRIPT,
            label_replacements=(
                ("Gate packet from selection", "Prepare for manuscript review"),
                ("Amanuensis context", "Share this moment"),
                ("Footnote candidate", "Make footnote candidate"),
            ),
        ),
    )


class ThreadingServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True


def is_loopback(host: str) -> bool:
    return host in ("127.0.0.1", "localhost", "::1")


def make_handler(work_id: str, work_root: Path, workspace: Path, session_key: str):
    base = wb.make_handler(work_id, work_root, workspace, session_key)

    class Handler(base):
        server_version = "TYFWorkbenchLive/0.4"

        def read_payload(self) -> Dict[str, Any]:
            size = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(min(size, MAX_POST_BYTES)).decode("utf-8")
            data = json.loads(raw or "{}")
            return data if isinstance(data, dict) else {}

        def send_live_events(self) -> None:
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream; charset=utf-8")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "keep-alive")
            self.end_headers()
            for _ in range(LIVE_EVENT_LIMIT):
                payload = status_model.live_status(work_id, work_root, workspace)
                body = f"data: {json.dumps(payload, ensure_ascii=False, separators=(',', ':'))}\n\n".encode("utf-8")
                try:
                    self.wfile.write(body)
                    self.wfile.flush()
                except (BrokenPipeError, ConnectionResetError):
                    break
                time.sleep(LIVE_EVENT_INTERVAL_SEC)

        def do_GET(self):  # noqa: N802
            parsed = urllib.parse.urlparse(self.path)
            if parsed.path in ("/", "/index.html", "/workbench-live.html"):
                self.html_response(enhanced_html(wb.collect_data(work_id, work_root, workspace, token=session_key)))
            elif parsed.path == "/api/live-status":
                self.json_response(200, status_model.live_status(work_id, work_root, workspace))
            elif parsed.path == "/api/live-events":
                self.send_live_events()
            else:
                super().do_GET()

        def do_POST(self):  # noqa: N802
            parsed = urllib.parse.urlparse(self.path)
            if parsed.path in ("/api/reload-disk", "/api/save-browser-copy", "/api/conflict-packet"):
                if not self.require_token():
                    return
                try:
                    payload = self.read_payload()
                    path = wb.one_line(payload.get("path"))
                    if parsed.path == "/api/reload-disk":
                        self.json_response(200, recovery.reload_disk_version(work_root, path))
                    elif parsed.path == "/api/save-browser-copy":
                        self.json_response(200, recovery.save_browser_copy(work_id, work_root, workspace, path, str(payload.get("browser_text") or ""), str(payload.get("note") or "")))
                    else:
                        self.json_response(200, recovery.write_conflict_packet(work_id, work_root, workspace, path, wb.one_line(payload.get("loaded_sha256")), str(payload.get("browser_text") or ""), str(payload.get("note") or "")))
                except ValueError as e:
                    self.json_response(400, {"status": "error", "message": str(e)})
                except Exception as e:  # noqa: BLE001
                    self.json_response(500, {"status": "error", "message": str(e)})
            else:
                super().do_POST()

    return Handler


def run(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="TYF live Workbench with assistant status, save-safety, recovery, and review dashboard")
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
