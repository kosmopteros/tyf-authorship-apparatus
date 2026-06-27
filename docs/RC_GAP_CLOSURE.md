# Private RC gap closure

Status: implemented as the focused RC-gap slice after the single-author workspace clarification.

TYF is a single-author, local-first workspace. It does not assume Git and it does not implement multiplayer editing. The only realistic concurrency is the author in the Workbench and a local amanuensis/Codex process touching the same files.

## What this slice adds

### 1. Single-author draft recovery

New command/module:

```bash
tyf-recovery
```

New helper module:

```text
scripts/tyf_recovery.py
```

Recovery actions:

- reload current disk draft
- save browser version as a local recovery copy
- prepare a recovery packet with disk and browser versions

Outputs:

```text
drafts/.recovery-copies/*.md
.review/conflicts/<id>/disk.md
.review/conflicts/<id>/browser.md
.review/conflicts/<id>/conflict.md
.review/conflicts/<id>/conflict.json
```

No auto-merge. No manuscript write.

### 2. Workbench recovery actions

The live Workbench now shows recovery actions when the active draft changed outside the browser window:

```text
Reload disk version
Save my version as copy
Prepare conflict packet
```

This turns stale-state detection into safe author choices.

### 3. Workbench review dashboard

The live status model now includes review summaries for:

- continuity review
- polish review
- concept review
- graph build report

The Workbench side panel now shows a compact Review dashboard instead of requiring the author to manually inspect `.review/surface/`.

### 4. RC doctor

New command:

```bash
tyf-rc-doctor
```

New helper module:

```text
scripts/tyf_rc_doctor.py
```

It checks:

- required workspace files and directories
- JSONL parse health
- event ledger hash-chain verification
- graph projection build
- concept review build
- continuity review build
- polish review build
- live Workbench HTML generation with RC markers

Outputs:

```text
.review/surface/rc-doctor.json
.review/surface/rc-doctor.md
```

## Product boundary

This is not Git. This is not multi-user editing. This is not CRDT. This is not auto-merge.

The safety model is:

- local content hashes
- atomic writes
- stale-save refusal
- visible changed-outside-window state
- recovery copies
- recovery packets
- event records

## Private RC impact

This closes the pure RC blockers identified in the narrowed review:

- conflict recovery choices
- Workbench review dashboard
- RC doctor / smoke check

Remaining before a stronger public-ish RC:

- decision-aware grouping in continuity/polish reports
- direct `tyf workbench` and `tyf review` subcommands inside the main parser
- real-book signal/noise calibration
- optional minimal line-edit candidate packets

## Rule

TYF should help the author recover from local amanuensis concurrency without pretending to be a collaborative editor.

When in doubt, TYF should preserve both versions and ask the author.
