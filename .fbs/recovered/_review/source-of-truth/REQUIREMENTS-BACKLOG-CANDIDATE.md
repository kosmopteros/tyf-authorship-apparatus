# Requirements And Backlog Candidate

Status: review-only candidate.

This file converts recovered intent into reviewable requirements and
backlog items. It is not a SOLO requirements register yet.

## Status Values

- `implemented-lock`: code mostly appears to implement the claim; promote Be to lock it.
- `gap-needs-Be`: intent appears plausible but executable behaviour is missing or weak.
- `contradiction-ruling-needed`: sources disagree; the operator must rule.
- `candidate-review`: plausible recovered or synthesized intent; not accepted.
- `stale-rewrite`: docs need rewrite or demotion before agents rely on them.

## Candidate Requirements

| ID | Requirement | Status | Confidence | Primary evidence |
| --- | --- | --- | --- | --- |
| R-001 | **Code first, model only where intelligence is required.** Every check that can be done deterministically already lives in `tyf notice`. | gap-needs-Be | 0.66 | docs/LEARN_PASS.md:13, scripts/tyf.py:883 |
| R-002 | **Command surface is too fragmented.** Standalone commands are fine internally, but `tyf workbench` and `tyf review ...` should become canonical. | gap-needs-Be | 0.66 | docs/RC_ARCHITECTURE_RED_TEAM.md:230, scripts/tyf.py:883 |
| R-003 | **Explicitly, hard-fail, as `tyf check`** (exit 1 on drift; | gap-needs-Be | 0.66 | skills/keeping-documentation-honest/SKILL.md:23, scripts/tyf.py:883 |
| R-004 | **Frame-lock.** The work assumes its own frame and never tests it. | gap-needs-Be | 0.66 | skills/auditing-adversarially/SKILL.md:16, scripts/tyf.py:5057 |
| R-005 | **Per-run (always).** Any time `tyf notice` runs, manually or on a schedule, it reconciles against the ledger. | gap-needs-Be | 0.66 | docs/ATTENTIVENESS.md:37, scripts/tyf.py:883 |
| R-006 | **Per-write (wired now).** Every `tyf write` updates the ledger and reports only genuinely new or resurfaced items, so a manuscript write never nags about things already seen. | gap-needs-Be | 0.66 | docs/ATTENTIVENESS.md:38, scripts/tyf.py:883 |
| R-007 | **Register inheritance semantics.** When a work overrides a workspace-level register, how does the override compose with the base: replace, merge, layer, or per-rule? `manifest.yaml` currently defaults to layer. | gap-needs-Be | 0.66 | TYF-manifesto-and-architecture.md:292, scripts/tyf.py:3927 |
| R-008 | **The attentive amanuensis loop.** `tyf notice` surfaces, and never modifies: gaps left to fill, lines that trail off, claims with no source, a style sheet lagging its manuscript, unused registers. | gap-needs-Be | 0.66 | TYF-manifesto-and-architecture.md:256, scripts/tyf.py:883 |
| R-009 | **The controlled write.** Entering the Revise column requires proposal, audit, author review packet, explicit author decision, and `tyf write --decision <id>`. | gap-needs-Be | 0.66 | TYF-manifesto-and-architecture.md:173, scripts/tyf.py:883 |
| R-010 | A runtime is a place TYF runs, never part of its doctrine. | gap-needs-Be | 0.66 | TYF-manifesto-and-architecture.md:248, scripts/tyf.py:883 |
| R-011 | A second, opt-in semantic layer (the Learn pass, `docs/LEARN_PASS.md`) reads only the diff and asks a model the few questions code cannot answer; | gap-needs-Be | 0.66 | TYF-manifesto-and-architecture.md:256, scripts/tyf.py:6210 |
| R-012 | A second, opt-in semantic layer (the Learn pass, see `docs/LEARN_PASS.md`) reads only the diff and asks a model the few questions code cannot answer, again surfacing only. | gap-needs-Be | 0.66 | skills/scheduling-ongoing-work/SKILL.md:35, scripts/tyf.py:6210 |
| R-013 | Added tests that assert required storage classes exist and wired architecture checks into `tyf-rc-doctor`. | gap-needs-Be | 0.66 | docs/RC_ARCHITECTURE_CONTRACTS_3X.md:28, scripts/tyf.py:883 |
| R-014 | An opt-in semantic layer that reads the diff and asks a model the few questions code cannot answer is specified, unwired, in `docs/LEARN_PASS.md`; | gap-needs-Be | 0.66 | README.md:162, scripts/tyf.py:6210 |
| R-015 | Ask the agent: "List the TYF skills you can see." It should return all nineteen, and it should route any authorship request through `using-tyf` first. | gap-needs-Be | 0.66 | .opencode/INSTALL.md:14, scripts/tyf.py:883 |
| R-016 | Be IDs must be unique | gap-needs-Be | 0.66 | .claude/commands/fbs-formulate.md:105, scripts/tyf.py:2236 |
| R-017 | Claude should load `using-tyf`, run `tyf init` if the folder is not a workspace yet, then run `tyf start` or `tyf start <path>` if a chat export, folder, old workspace, zip, or scaffold arrives. | gap-needs-Be | 0.66 | cowork/SETUP.md:25, scripts/tyf.py:883 |
| R-018 | Commands include `init` (idempotent: creates only missing structure, never clobbers), `start`, `begin`, `import`, `capture`, `attend`, `session`, `diagnose`, `treat`, `surface`, `resume`, `status`, `new-work`, `open`, `mark-ready`, `propose`, `audit`, `accept`, `adopt`, `write --decision`, `doctor [--repair]`, `check`, `notice`, `dismiss`, and `reconcile`. | gap-needs-Be | 0.66 | TYF-manifesto-and-architecture.md:236, scripts/tyf.py:883 |
| R-019 | Convergence:** Every next slice should be judged by time-to-writing and time-to-return-to-writing, not by architectural completeness. | gap-needs-Be | 0.66 | docs/WORKBENCH_ADVERSARIAL_PRODUCT_CRITIQUE_POST_PR5.md:152, scripts/tyf.py:6234 |
| R-020 | Convergence:** The amanuensis path should default to reading the active context automatically and proposing next actions, not asking the author to explicitly generate context packets. | gap-needs-Be | 0.66 | docs/WORKBENCH_ADVERSARIAL_PRODUCT_CRITIQUE_POST_PR5.md:56, scripts/tyf.py:5057 |
| R-021 | Convergence:** `tyf workbench` should become the canonical command. | gap-needs-Be | 0.66 | docs/WORKBENCH_ADVERSARIAL_PRODUCT_CRITIQUE_POST_PR5.md:132, scripts/tyf.py:883 |
| R-022 | Current repo evidence: 197 tests pass in the stdlib helper/doc/install suite, including exported release-tree `tyf check`, installer smoke coverage, release manifest context-path validation, a reproducible first-sitting rehearsal from `examples/first-sitting-arrival/scaffold.txt`, existing-work recovery packets for formatted and illustrated arrivals, language-neutral structure records for non-English source, answered-prompt resume handling, source-grounded `tyf attend` attention packets with transparent local retrieval, external-feedback triage, continuing-work session packets, resume return-context recovery, read-only session-start and message-sent hook contexts, Codex and Claude hook manifests with TYF-identifying status messages, doctor repair-boundary coverage, diagnostic-isolation packets, typographer-redactor treatment packets for existing body prose, Draft Review Workbench generation with draft-save conflict protection, private-context-free author/root/runtime surfaces, machine-checked pressure-eval honesty, local-only hidden tooling learning packets, and a fresh exported Codex install opening a separate book workspace from an arrival scaffold. | gap-needs-Be | 0.66 | README.md:174, scripts/tyf.py:883 |
| R-023 | For a domain without git, this is more than superpowers offers, and the attentive-amanuensis loop (surface-only, never modifies, dismissed-with-resurface) has no superpowers equivalent. | gap-needs-Be | 0.66 | docs/COMPARISON_SUPERPOWERS.md:39, scripts/tyf.py:3927 |
| R-024 | For the highest-stakes skills (`controlling-manuscript-writes`, `composing-as-amanuensis`, `auditing-adversarially`, `ingesting-sources`), turn these break cases into RED/GREEN pressure scenarios in `pressure-scenarios.md` and run them against a subagent: confirm the skill produces the "should" behavior, not the "break" behavior, under pressure. | gap-needs-Be | 0.66 | tests/acceptance-and-edge-cases.md:161, scripts/tyf.py:883 |
| R-025 | From that it proposes, never applies, new entries: an anti-pattern, a register fence, a terminology rule, a new skill. | gap-needs-Be | 0.66 | skills/scheduling-ongoing-work/SKILL.md:18, scripts/tyf.py:883 |
| R-026 | Hooks should not write `manuscript/`. | gap-needs-Be | 0.66 | docs/WORKBENCH_TWO_WAY_MACHINERY.md:99, scripts/tyf.py:883 |
| R-027 | If a changed draft hash conflicts with browser state, Workbench should show conflict before save. | gap-needs-Be | 0.66 | docs/WORKBENCH_TWO_WAY_MACHINERY.md:189, scripts/tyf.py:883 |
| R-028 | If stale, TYF returns a conflict. | gap-needs-Be | 0.66 | docs/WORKBENCH_TWO_WAY_MACHINERY.md:179, scripts/tyf.py:883 |
| R-029 | If the return context is thin or the author needs a fresh sitting, run `tyf session` or `tyf session work --focus "<focus>"`, read `.review/current-session.md`, and offer one small next move plus a stop condition. | gap-needs-Be | 0.66 | skills/using-tyf/SKILL.md:36, scripts/tyf.py:883 |
| R-030 | If you must copy it, set `TYF_PACK_ROOT` to this repo. | gap-needs-Be | 0.66 | cowork/SETUP.md:13, scripts/tyf.py:883 |
| R-031 | It may guide a candidate treatment in `drafts/` or editorial proposals in `.review/`, but it never authorizes a manuscript write. | gap-needs-Be | 0.66 | skills/typographer-redactor/SKILL.md:28, scripts/tyf.py:883 |
| R-032 | It never writes to `manuscript/`; | gap-needs-Be | 0.66 | README.md:156, scripts/tyf.py:883 |
| R-033 | It runs automatically warn-only after every mutating `tyf` command and hard-fails (exit 1) as a standalone command. | gap-needs-Be | 0.66 | VALIDATION.md:6, scripts/tyf.py:883 |
| R-034 | It should read the orientation packet before organizing anything, run `tyf structure work --source-ref <id>` for any minted text source fragment, show `.review/writing-runway.md` and `drafts/candidate-draft.md`, and tell you what files were created in plain language. | gap-needs-Be | 0.66 | cowork/SETUP.md:25, scripts/tyf.py:883 |
| R-035 | It should return all nineteen and route any authorship request through `using-tyf` first. | gap-needs-Be | 0.66 | docs/PORTABILITY.md:103, scripts/tyf.py:883 |
| R-036 | It should return all nineteen skills, route any authorship request through `using-tyf`, and refuse to write into `manuscript/` outside `tyf write --decision`. | gap-needs-Be | 0.66 | cowork/SETUP.md:39, scripts/tyf.py:883 |
| R-037 | Lineage matters for an open-source project, both for credit and because every keep and reject below is a decision a contributor should be able to challenge. | gap-needs-Be | 0.66 | TYF-manifesto-and-architecture.md:53, scripts/tyf.py:2522 |
| R-038 | Load `using-tyf` and `initializing-a-workspace`, create or enter the workspace, then run `tyf start` with no title required. | gap-needs-Be | 0.66 | AGENTS.md:11, scripts/tyf.py:883 |
| R-039 | MCP returns active unit, selected text, notes, style sheet, and related local passages. | gap-needs-Be | 0.66 | docs/WORKBENCH_TWO_WAY_MACHINERY.md:151, scripts/tyf.py:883 |
| R-040 | Manuscript writes must go through proposal, audit, author review packet, author decision, and `tyf write --decision <id>`. | gap-needs-Be | 0.66 | author-context/AGENTS.md:22, scripts/tyf.py:883 |

## P0 Promotion Candidates

No P0 candidates ranked; review the candidate table first.

## Rulings Needed Before Implementation Work

No contradiction-ruling-needed candidates were ranked.

## Backlog From Accepted Direction

1. tyf - It runs automatically warn-only after every mutating `tyf` command and hard-fails (exit 1) as a standalone command.
2. pass - scenario + source files and return `pass`/`fail`.
3. .review/ - Should: write findings to `.review/` only;
4. manuscript/ - Hooks should not write `manuscript/`.
5. prompt - Packet-writing or note-writing tools should stay `prompt` until usage proves they are calm.
6. ide - The same TYF tools should be available whether the author talks in the Codex CLI, IDE, or future Workbench chat.
7. able - never able to silently publish into manuscript.
8. init - Commands include `init` (idempotent: creates only missing structure, never clobbers), `start`, `begin`, `import`, `capture`, `attend`, `session`, `diagnose`, `treat`, `surface`, `resume`, `status`, `new-work`, `open`, `mark-ready`, `propose`, `audit`, `accept`, `adopt`, `write --decision`, `doctor [--repair]`, `check`, `notice`, `dismiss`, and `reconcile`.

## Suggested SOLO Promotion Shape

1. Add the R with exact reviewed wording.
2. Formulate one small F claim.
3. Add one executable Be that can fail.
4. Run prove-red before claiming coverage.
5. Run the relevant gate and doc-honesty checks.
