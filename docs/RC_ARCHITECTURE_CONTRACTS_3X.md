# RC architecture contracts: 3 improvement iterations per critique point

Status: implemented architecture hardening after `docs/RC_ARCHITECTURE_RED_TEAM.md`.

This file records three concrete improvement iterations for each converged architecture critique point.

## Point 1: Storage semantics are implicit

### Iteration 1

Added `docs/STORAGE_CONTRACT.md` to classify TYF files by authority:

- canonical prose
- canonical author records
- mutable record stores
- hash-chain ledger
- append logs
- generated review artifacts
- rebuildable caches
- recovery artifacts

### Iteration 2

Added `scripts/tyf_architecture_contracts.py` with a machine-readable `STORAGE_CLASSES` map.

### Iteration 3

Added tests that assert required storage classes exist and wired architecture checks into `tyf-rc-doctor`.

## Point 2: Workbench HTML composition is brittle

### Iteration 1

Added `scripts/tyf_workbench_slots.py` with named anchors for Workbench extension points.

### Iteration 2

Updated `scripts/tyf_workbench_live.py` to use `apply_workbench_slots()` instead of spreading anonymous string replacements through the module.

### Iteration 3

Added tests that make missing Workbench slot anchors fail loudly and verify live Workbench markers remain present.

## Point 3: Command surface is fragmented

### Iteration 1

Kept existing standalone commands for compatibility.

### Iteration 2

Added `scripts/tyf_review.py` as a canonical review wrapper:

```bash
tyf-review graph
tyf-review concept
tyf-review continuity
tyf-review polish
tyf-review doctor
```

### Iteration 3

Exposed `tyf-review` in `pyproject.toml` alongside the standalone commands. This is a safer step before a larger `scripts/tyf.py` parser rewrite.

## Point 4: Recovery routes need runtime tests

### Iteration 1

Added `tests/test_workbench_recovery_routes.py` with a real loopback server in a temp workspace.

### Iteration 2

Tested token enforcement for side-effecting recovery routes.

### Iteration 3

Tested route-level behavior for:

- reload disk draft
- save browser version as copy
- prepare recovery packet

No Selenium or browser automation was added.

## Point 5: Safety invariants need executable guards

### Iteration 1

Added forbidden route marker scanning in `tyf_architecture_contracts.py`.

### Iteration 2

Added conservative direct manuscript-write scanning outside known Gate helpers.

### Iteration 3

Integrated those architecture checks into `tyf-rc-doctor`, so the private RC doctor now reports architectural safety drift as part of the workspace check.

## Remaining architectural debt

Still intentionally not done in this slice:

- full package refactor away from scripts
- direct `tyf review ...` subparser inside the large `scripts/tyf.py`
- full Workbench template refactor in `tyf_workbench_v06.py`
- browser automation
- remote server support

## Verdict

This moves the architecture from “private RC viable” toward “private RC maintainable.”

The most important gain is that architectural doctrine is now executable enough to fail tests or doctor checks instead of living only in prose.
