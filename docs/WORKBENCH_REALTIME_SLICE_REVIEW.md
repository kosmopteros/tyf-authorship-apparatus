# Workbench realtime slice review

Status: post-adversarial product improvement round.

## Why this slice

The adversarial product critique found that the architecture is now credible, but the author still risks feeling like an operator. The highest-leverage improvement is realtime visibility in the browser, because it answers: is the assistant active, is my draft safe, and does anything need my decision?

## Implemented

- `scripts/tyf_workbench_live.py` now exposes `/api/live-events` as a Server-Sent Events stream.
- The browser uses `EventSource('/api/live-events')` when available.
- Polling remains as a fallback if EventSource is unavailable or the stream errors.
- The side-panel language was softened:
  - `Codex status` -> `Assistant status`
  - `Draft state` -> `Save safety`
  - `Approval requests` -> `Needs your approval`
  - `Gate packet from selection` -> `Prepare for manuscript review`
  - `Amanuensis context` -> `Share this moment`
  - `Footnote candidate` -> `Make footnote candidate`
- Stale draft wording is now author-facing: `Changed outside this window`.
- Current draft wording is now `Safe to save`.
- `tests/test_workbench_status.py` now asserts static HTML markers for:
  - realtime SSE path
  - live connection function
  - side-panel cards
  - calm UI labels

## Product review

### Author workflow

Better. The Workbench now has a realtime lane before the user thinks to refresh. This matters more than more backend depth.

### Safety

Still good. The slice does not add a new write route and does not touch `manuscript/`.

### Concurrency

Improved visibility, not full merge management. The browser can now see stale state with much lower latency. Recovery actions are still next.

### UX language

Improved. Primary actions are less packet-first and more author-facing.

### Maintenance

Risk: `tyf_workbench_live.py` still injects into the v0.6 HTML by string replacement. The new static HTML tests reduce drift risk, but a future template-slot refactor is still warranted.

### Realtime implementation

SSE is a good middle ground:

- no websocket complexity
- keeps loopback/local shape
- browser-native
- simple fallback to polling

## Remaining after this PR

- Add conflict recovery choices:
  - reload disk version
  - save my version as copy
  - show both versions
- Show explicit assistant-context reassurance:
  - last context shared
  - last MCP/context read if recorded
- Wire `tyf workbench` directly into `scripts/tyf.py` once the command surface can be changed without a broad parser rewrite.
- Replace HTML string injection with named template slots.

## Verdict

This is the right immediate improvement from the adversarial critique. It makes the Workbench feel more alive without pretending browser-native Codex chat is complete.
