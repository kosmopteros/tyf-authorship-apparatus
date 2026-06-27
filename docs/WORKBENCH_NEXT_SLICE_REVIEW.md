# Workbench next-slice review

Status: implementation and internal review for the post-v0.6 bridge visibility slice.

## Implemented slice

This branch builds on the merged local Workbench/MCP/Codex bridge baseline and adds:

1. `scripts/tyf_workbench_status.py`
   - read-only plain-file status model for the Workbench
   - exposes current draft hashes, Codex turn status, bridge status, and current approval state
   - includes stale-draft detection against a browser-loaded hash map

2. `scripts/tyf_workbench_live.py`
   - live Workbench wrapper around the v0.6 Workbench
   - injects a Codex status card into the side panel
   - injects a Draft state card that shows when the browser draft hash is stale
   - injects an Approval requests card
   - serves `/api/live-status` for browser polling
   - delegates all write routes to the existing v0.6 CAS-protected helpers

3. `scripts/tyf_codex_approvals.py`
   - approval request and decision model in plain JSON/JSONL
   - writes `.review/surface/codex-approval-current.json`
   - appends `.review/surface/codex-approval-events.jsonl`
   - never mutates draft or manuscript prose

4. `scripts/tyf_codex_bridge_v07.py`
   - approval-aware wrapper around the local Codex app-server bridge
   - records approval-like app-server notifications into the approval model
   - keeps app-server behind the TYF bridge

5. `scripts/tyf_codex_hook_validate.py`
   - local validator for the hook wiring sample
   - invokes the installed Codex command locally
   - writes `.review/surface/codex-hook-config-validation.json`
   - writes `.review/surface/codex-hook-config-validation.md`

6. `pyproject.toml`
   - exposes `tyf-workbench = "tyf_workbench_live:main"`
   - packages the new helper modules so installed users can run the live Workbench command

7. Tests
   - `tests/test_workbench_status.py`
   - `tests/test_codex_approvals.py`

## 12-lens review

### 1. Author workflow reviewer

Finding: The live status card reduces the need to inspect `.review/surface/` manually. This is the right next product slice.

Remaining: It is polling, not SSE. Fine for this slice.

### 2. Manuscript Gate reviewer

Finding: The live wrapper delegates to the existing safe write helpers and does not add a manuscript write route. The Gate boundary holds.

### 3. Concurrency reviewer

Finding: Existing CAS save protection remains the hard safety mechanism. The new status model adds browser-visible stale-draft detection by comparing the browser-loaded hash against disk hash. This is not a multi-user editor, but it solves the immediate stale-save visibility gap.

### 4. Browser integration reviewer

Finding: The side panel now has three visible cards: Codex status, draft state, approval requests. This closes the top gap from the external critique.

Risk: The wrapper relies on stable markers in the v0.6 HTML template. Acceptable for a slice, but eventually the Workbench should move to explicit template sections.

### 5. MCP reviewer

Finding: MCP remains the correct immediate bridge. This slice does not pollute MCP with raw file tools.

### 6. App-server reviewer

Finding: The bridge still stays behind TYF. Approval-like notifications are now modeled locally before browser-native chat is claimed complete.

Remaining: It records approval state but does not yet send decisions back to app-server. That should be a later bridge-action slice after the exact app-server approval schema is validated locally.

### 7. Hook reviewer

Finding: There is now a validator that checks the local Codex command and records a validation report. This is the right shape because exact Codex hook wiring must be validated on the installed local version.

Limitation: This PR cannot prove local Codex is installed in this remote GitHub context.

### 8. Security-boundary reviewer

Finding: No new remote surface is added by default. The live wrapper defaults to loopback and the bridge remains local. Good.

### 9. Package reviewer

Finding: `tyf-workbench` is exposed as an installed console command. This is not yet `tyf workbench`, but it gives authors a real command surface without rewriting the large existing `tyf.py` command parser in this PR.

Recommendation: Add `tyf workbench` as the next integration once the live wrapper is stable.

### 10. Test reviewer

Finding: Tests cover status shape, stale detection, approval record, approval decision, and file creation. Good for the new pure helpers.

Remaining: Browser JS and real app-server notification tests still require local/integration validation.

### 11. Maintenance reviewer

Finding: The live wrapper avoids a large risky rewrite of `tyf_workbench_v06.py`, but it depends on string injection. This is acceptable for proving the slice; it should become a real template boundary later.

### 12. Product-scope reviewer

Finding: The scope is still honest. This is Workbench visibility and approval-state modeling, not finished browser-native chat.

## Findings fixed during this round

- Fixed the live Workbench wrapper to delegate to `tyf_workbench_v06.make_handler(work_id, work_root, workspace, session_key)` instead of the wrong legacy arity.
- Split the status model out of the browser wrapper for testability.
- Added a pure stale-draft detector for tests and future UI use.
- Added an approval model independent of the app-server bridge so approval requests and decisions remain inspectable local state.
- Added `tyf-workbench` as an installable command while avoiding a risky invasive edit of `scripts/tyf.py`.

## Remaining after this PR

- Add true `tyf workbench` subcommand inside `scripts/tyf.py` once the live wrapper has real use.
- Add SSE or long-polling only if simple polling feels laggy.
- Validate the hook sample on an actual local Codex install.
- Wire approval decisions back into app-server after the local schema is confirmed.
- Replace HTML string injection with explicit template slots.

## Verdict

This slice closes the visible-browser-status and stale-draft-badge gap. It also creates a local approval-state model and a validation path for hook config. It is ready to merge as the next sequential slice, with browser-native chat still honestly deferred until approval round-tripping is implemented and locally verified.
