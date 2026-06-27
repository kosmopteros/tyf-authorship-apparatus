# Workbench external critique council

Status: simulated external-style review across 12 independent product, authoring, security, and implementation lenses.

The goal of this review is not to create theater. The goal is to compare the target promise against the current PR and identify where independent critical readers converge.

## Target promise under review

The Workbench promise is:

- the author writes in a local multi-unit desk
- Codex knows the active unit and selection without copy-paste
- notes and footnote candidates are durable plain files
- manuscript remains protected by the Gate
- browser-native Codex chat is optional and must not bypass TYF discipline
- the author experiences continuity, not machinery

## The 12 lenses

### 1. Author workflow reviewer

**Concern:** The Workbench is useful only if the author can stay in the desk while writing. If Codex status and conflicts remain invisible, the author returns to command-line vigilance.

**Finding:** Draft writing, notes, and packets are usable. Codex visibility exists as files, but browser presentation is still missing.

### 2. Manuscript Gate reviewer

**Concern:** Any bridge to Codex can accidentally become a second manuscript writer.

**Finding:** No implemented route writes `manuscript/`. This invariant currently holds across Workbench, MCP, hooks, and bridge.

### 3. Local-first reviewer

**Concern:** App-server and WebSocket language can quietly turn a local apparatus into a networked service.

**Finding:** The stack stays local by default. The bridge uses stdio to `codex app-server`, and non-loopback serving requires explicit opt-in. Good.

### 4. MCP protocol reviewer

**Concern:** MCP should expose TYF actions, not file tools wearing a TYF label.

**Finding:** The MCP tool list is well-shaped: context, selection, unit context, notes, footnotes, Gate packets, graph-lite, conflicts, and status. There is no raw write tool.

### 5. Codex app-server reviewer

**Concern:** App-server is a rich-client transport, not the first thing to expose to the browser.

**Finding:** The bridge is correctly behind TYF and scaffolded as optional. It should not be advertised as complete until approval mirroring exists.

### 6. Security-boundary reviewer

**Concern:** Capability tokens and loopback are useful but not a security product. The docs should avoid overclaiming.

**Finding:** The docs now describe tokens as local misuse guards, not internet security. Good.

### 7. State-file reviewer

**Concern:** If status, turns, notes, and graph outputs are not plain files, the author cannot inspect or recover the work.

**Finding:** Status and bridge files are plain JSON/JSONL under `.review/surface/`; notes remain JSONL; packets remain Markdown and JSON. Good.

### 8. Test reviewer

**Concern:** The PR was growing architecture faster than tests.

**Finding:** Workbench and MCP already had tests. Hook and bridge tests were added after the critique. App-server live integration still requires local Codex validation.

### 9. UX reviewer

**Concern:** A four-panel desk can still feel like machinery if the right panel becomes a dump of raw artifacts.

**Finding:** The immediate UI is acceptable for v0.6, but browser status cards and conflict badges are needed before daily writing use feels calm.

### 10. Product-scope reviewer

**Concern:** The PR risks pretending to implement v0.8 while still in v0.6.

**Finding:** The docs now draw a clear line: MCP is usable; app-server bridge is scaffold; browser-native chat is not complete.

### 11. Maintenance reviewer

**Concern:** Standalone scripts can drift from `tyf.py` and become a parallel product.

**Finding:** This is acceptable for a reviewable PR, but command wiring should be the next integration step: `tyf workbench` or `tyf surface --v06`.

### 12. Red-team author reviewer

**Concern:** The apparatus could protect the manuscript but still fail the author by requiring too much ceremony.

**Finding:** The Workbench reduces ceremony substantially, but status and approval surfaces must become visible in the browser to fully meet the promise.

## Convergence

The independent lenses converge on five points.

### Convergence 1: The core Workbench is directionally right

The local desk, multi-unit drafts, read-only manuscript preview, notes, footnote candidates, and Gate packets match the target promise.

### Convergence 2: The MCP bridge is the correct immediate bridge

MCP solves the copy-paste problem without forcing browser-native chat too early. Codex can know the active selection and create TYF-safe records without raw file tools.

### Convergence 3: App-server must remain behind a TYF bridge

A direct browser-to-Codex app-server path would bypass too much of TYF's context, event, and trust boundary discipline. The bridge scaffold is the right shape.

### Convergence 4: Browser visibility is now the main missing product slice

The status files exist, but the browser does not yet present them. This is now the top product gap.

### Convergence 5: Approval mirroring is the hard blocker for embedded chat

Until app-server approval events can be shown and answered in the Workbench, browser-native chat should remain scaffolded and not marketed as complete.

## Improvements made after the critique

- Added `scripts/tyf_codex_bridge.py` as a local app-server bridge scaffold.
- Added `scripts/tyf_codex_hook.py` for tolerant Codex hook status recording.
- Added `scripts/tyf_codex_schema.py` for local app-server schema compatibility artifacts.
- Added `docs/CODEX_HOOKS.sample.toml`.
- Added `tests/test_codex_hook_recorder.py`.
- Added `tests/test_codex_bridge_context.py`.
- Updated `docs/WORKBENCH_TWO_WAY_MACHINERY.md` with implementation status.
- Updated `docs/WORKBENCH_V06_IMPLEMENTATION.md` with the new bridge and schema files.
- Updated `docs/WORKBENCH_PROTOTYPE_REVIEW.md` with fixed and remaining issues.

## Remaining next round

The next round should be narrower and more UI-oriented:

1. Add Codex status polling to the Workbench side panel.
2. Add visible conflict badges when browser draft state is stale.
3. Add an approval-event model for app-server notifications.
4. Validate hook config against a real local Codex install.
5. Wire the workbench into the main `tyf` command surface.

## Verdict

The PR now satisfies the local-first Workbench plus MCP promise better than the previous version. It does not yet satisfy the browser-native Codex chat promise, and the docs now say so explicitly.
