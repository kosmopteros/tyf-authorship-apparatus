# RC architecture red-team critique

Status: architecture/code red-team after private-RC gap closure.

Scope: architecture, code shape, storage semantics, safety boundaries, local-first assumptions, module coupling, testability, and operational failure modes. This is deliberately less product-facing than the previous critique rounds.

## Current architectural spine

TYF now has these major local components:

- local Workbench server and browser surface
- CAS-protected draft saves
- read-only manuscript preview
- MCP server for safe amanuensis access
- Codex app-server bridge scaffolds
- status/approval/hook records
- SSE live status
- recovery copies and conflict packets
- graph projection and JSONL audit
- concept review
- continuity review
- continuity decision writer
- polish review
- RC doctor

The architecture is coherent enough for private-RC use, but it has started to accumulate small modules, parallel command entry points, and string-injected browser UI. The red-team concern is no longer “does the idea make sense?” It is: can this structure remain maintainable, predictable, and safe when used on a real book folder for weeks?

## Ten red-team reviewers

### 1. Storage semantics reviewer

**Attack:** The repository now has many local record types: Markdown, JSON, JSONL, SQLite cache, review packets, event logs, mutable record stores, generated reports. The architecture depends on the author and amanuensis knowing which files are truth, which files are cache, and which files are review artifacts.

**Risk:** Codex or a future tool may treat generated `.md` reports as source doctrine, or treat mutable JSONL as append-only ledger, or treat SQLite cache as truth.

**Convergence:** Add a machine-readable storage contract.

Suggested file:

```text
.tyf/storage-contract.json
```

or repo-level template:

```text
docs/STORAGE_CONTRACT.md
```

It should classify paths:

```text
canonical-prose
canonical-author-record
hash-chain-ledger
append-log
mutable-record-store
generated-review
rebuildable-cache
recovery-artifact
```

### 2. Module-boundary reviewer

**Attack:** The system is split into many standalone scripts. This helped move fast and preserve stdlib-only simplicity, but the architecture now risks becoming a script constellation rather than a coherent library.

**Risk:** Shared concepts like `work_root`, path safety, JSONL parse, issue keys, severity counts, report paths, and source-line iteration will drift across modules.

**Convergence:** Introduce a small internal library package or shared modules before adding more features.

Minimum:

```text
scripts/tyf_core_paths.py
scripts/tyf_core_jsonl.py
scripts/tyf_core_reports.py
scripts/tyf_core_issues.py
```

Not a framework. Just shared primitives.

### 3. Browser-surface reviewer

**Attack:** The live Workbench modifies the v0.6 HTML through string replacement. This was acceptable for slices, but it is fragile for RC.

**Risk:** A small upstream HTML text change can silently remove the dashboard, SSE, or recovery buttons. Static tests reduce this risk but do not make the architecture clean.

**Convergence:** Replace string injection with explicit template slots or split the Workbench HTML into composable sections.

Minimum next refactor:

```text
surface_base_html(data, extra_panels="", extra_script="")
```

Then `tyf_workbench_live.py` can pass panels/scripts without brittle `replace()` calls.

### 4. Local server security reviewer

**Attack:** The Workbench is loopback by default and side-effecting routes use a session token. Good. But recovery routes now accept browser text and write files. That is safe enough locally, but the route surface needs a clearer security contract.

**Risk:** If someone binds to a non-loopback host, recovery endpoints become more sensitive than read-only status endpoints.

**Convergence:** Keep `--allow-remote` hard-gated and add a server startup warning that recovery/write routes are enabled. Longer term, split read-only server mode from write-enabled server mode.

Possible modes:

```text
--serve-readonly
--serve-write-enabled
```

For private RC, loopback + token is acceptable.

### 5. Recovery architecture reviewer

**Attack:** Recovery is correct in doctrine: no auto-merge, preserve both sides. But reload disk version currently replaces browser text after user action; that action should always require explicit confirmation in the browser and should recommend saving a copy first.

**Risk:** Recovery UI accidentally becomes the place where author loses unsaved browser text.

**Convergence:** The recovery architecture should privilege copy/packet first, reload second.

Preferred button order:

```text
Save my version as copy
Prepare conflict packet
Reload disk version
```

Reload should be visually secondary.

### 6. Test architecture reviewer

**Attack:** Tests mostly target pure helpers and generated markers. That is good for stdlib-only speed, but route behavior and browser recovery flows are only indirectly covered.

**Risk:** A route may call the wrong helper or fail token validation unexpectedly; a static HTML marker test may pass while runtime POST fails.

**Convergence:** Add lightweight HTTP-handler tests using `http.client` against a local loopback server in a temporary workspace.

Do not add Selenium. Do not add heavy browser automation. But do test:

```text
GET /api/live-status
GET /api/live-events first event
POST /api/save-browser-copy
POST /api/conflict-packet
POST /api/reload-disk
```

### 7. Command-surface reviewer

**Attack:** There are many executable commands:

```text
tyf-workbench
tyf-graph
tyf-concept-review
tyf-continuity-review
tyf-continuity-decision
tyf-polish-review
tyf-recovery
tyf-rc-doctor
```

This is useful for development but not architecturally elegant for RC.

**Risk:** The author has to remember too many entry points; future scripts may duplicate setup and option handling.

**Convergence:** Keep the scripts, but add a canonical `tyf review` and `tyf workbench` command surface in `scripts/tyf.py`.

Target:

```bash
tyf workbench
tyf review graph
tyf review concept
tyf review continuity
tyf review polish
tyf review doctor
tyf decision continuity <issue_key> --status intentional
```

The standalone commands can remain package shortcuts.

### 8. Ledger/integrity reviewer

**Attack:** `.tyf/events.jsonl` is hash-chain audited, but most important review decisions are not hash-chained. That is okay if they are append logs, but the architecture should state whether decisions need tamper evidence.

**Risk:** If decisions become important author doctrine, mutable or unaudited decision logs may later feel less trustworthy than the event ledger.

**Convergence:** Do not overbuild now, but record every decision into `.tyf/events.jsonl` as already done for many actions. Longer term, create a generic append-log checker that verifies every decision line has stable ids and timestamps, even if not hash-chained.

### 9. Performance/scalability reviewer

**Attack:** Many review commands scan all draft/manuscript lines from scratch. For a normal book, this is fine. For huge projects, appendices, and multiple works, repeated full scans may become sluggish.

**Risk:** The Workbench dashboard may encourage frequent review runs, and full scans could become a UX drag.

**Convergence:** Do not optimize prematurely. But keep SQLite as optional cache and add build report timings before adding any persistent index complexity.

Minimum:

```text
started_at
finished_at
duration_ms
source_files_scanned
source_lines_scanned
```

in every review report.

### 10. Architectural doctrine reviewer

**Attack:** The architecture’s strongest invariant is “TYF never silently rewrites manuscript.” But this invariant is distributed across docs, PR bodies, and scripts rather than centralized as executable policy.

**Risk:** A future feature may accidentally add a manuscript write route, direct manuscript mutation helper, or model-suggested patch writer without triggering alarms.

**Convergence:** Add a small architecture guard test that scans scripts for forbidden manuscript-write route names and direct writes under `manuscript/`, allowing only known Gate paths.

This should be a test, not only prose.

## Converged architectural risks

The ten reviewers converge on five architecture risks:

1. **Storage semantics are still implicit.** The system needs a storage contract so generated reports, ledgers, mutable records, caches, and canonical prose are not confused.
2. **Workbench HTML composition is brittle.** String replacement was good enough for slices, but RC wants explicit template slots.
3. **Command surface is too fragmented.** Standalone commands are fine internally, but `tyf workbench` and `tyf review ...` should become canonical.
4. **Recovery routes need runtime tests.** Helper tests are not enough for confidence in the live server surface.
5. **Safety invariants need executable guards.** “No manuscript writes outside Gate” should be tested mechanically.

## Non-blocking for private RC

These are concerns, but not private-RC blockers:

- no multi-user concurrency model
- no Git integration
- no heavy browser automation
- no graph database
- no semantic model adjudication
- no remote deployment support

The current single-author local-first architecture is appropriate.

## Recommended next architecture PR

Title:

```text
Harden RC architecture contracts
```

Scope:

1. Add `docs/STORAGE_CONTRACT.md`.
2. Add an executable architecture guard test for no non-Gate manuscript writes.
3. Add explicit Workbench template extension slots.
4. Add route-level tests for recovery endpoints.
5. Add canonical `tyf workbench` and `tyf review ...` command aliases.

Out of scope:

- replacing all scripts with a package
- adding a database as truth
- browser automation
- Git-aware workflows
- remote server mode

## Verdict

The architecture is private-RC viable, but not architecture-clean yet.

The core safety model is right:

```text
single author
local files
hash-guarded draft writes
recovery copies
review packets
no auto-merge
no manuscript writes outside Gate
```

The main architectural debt is now not conceptual. It is consolidation debt:

```text
make storage semantics explicit
make UI extension explicit
make command surface canonical
make safety invariants executable
```

That is the path from “private RC candidate” to “clean RC architecture.”
