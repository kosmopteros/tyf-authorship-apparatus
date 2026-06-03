# TYF

*The Yours Faithfully. A faithful apparatus for authorship.*

TYF is not a writing assistant. TYF is not a productivity system. TYF is not a knowledge-management tool.

TYF is a faithful apparatus for authorship. Its job is to preserve source, elicit knowledge, protect register, propose edits, and enforce the controlled write. The author is the source. TYF is the interviewer, the amanuensis, the first reader, the faithful editor, and the redactor. It never becomes the writer.

It is a contextual skill pack in the Superpowers tradition, built for authorship rather than software. It does not generate a book from a prompt. It helps a person write a complete body of work on their topic, in their voice.

## What sits where

```
TYF skills          the core
tyf helper          enforcement (the single writer into manuscript/)
workspace contract  state, in plain files
Cowork              one strong runtime
other harnesses     portability targets, not yet all tested
```

## How it works

The moment a task touches source material, voice, claims, or a manuscript, the agent checks the TYF skills and loads the earliest applicable one instead of jumping to drafting. The skills enforce the commitments mechanically: the author is the source, the system proposes but never disposes, gaps are marked instead of confabulated, voice is read on every pass, the same operation runs at every zoom level, nothing is done until it has been attacked, and the controlled write is the only path into the manuscript.

## The sixteen skills

**Lifecycle**

| Skill | What it does |
|---|---|
| `initializing-a-workspace` | Scaffold a new workspace, then run intake |
| `working-the-workspace` | File and repo discipline; read-only zones; the controlled write path |
| `scheduling-ongoing-work` | Hooks and Cowork scheduled tasks for the iterative phase |
| `keeping-documentation-honest` | After any structural change, check that the routing docs are still true |

**Editorial apparatus**

| Skill | What it does |
|---|---|
| `using-tyf` | Dispatcher; routes to the earliest applicable skill |
| `ingesting-sources` | Preserve raw material; extract structured candidates |
| `interviewing-the-author` | Interview the author; sharpen the thesis |
| `structuring-knowledge` | Concepts, claims, argument spine, claims index, gaps |
| `composing-as-amanuensis` | Draft candidate text from supplied material, under write control |
| `reading-sympathetically` | Report the reading experience; read-only |
| `diagnosing-text` | Diagnose at any band; read-only |
| `editing-faithfully` | Propose edits, then controlled revise |
| `auditing-adversarially` | Adversarial audit before done |
| `controlling-manuscript-writes` | The only path into the manuscript |

**Cross-cutting substrates** (read by every Diagnose, Propose, Revise, and Audit pass at every band)

| Skill | What it does |
|---|---|
| `managing-voice` | How the work sounds: registers, fences, anti-patterns, AI-tell |
| `keeping-the-redactor-canon` | Whether it holds together: terminology, logic, composition, apparatus, finish, across micro, macro, and meta |

## The pipeline

```
init → ingest → interview → structure → voice + redactor → compose → read / diagnose → edit → audit → controlled write → schedule
```

Each step has a skill. Voice and Redactor are not steps; they are substrates every pass consults. The discipline is not to skip upstream when the work is still source, knowledge, voice, structure, or audit. Audit shows once in the line, but it also runs again after the controlled write, because the write itself can introduce issues; see `controlling-manuscript-writes`.

## Install

**Cowork is the primary deployment target for v1**, because it gives TYF local files, drop-in skills, a plugin that bundles them, and a native scheduler for the ongoing-work cadence. It is one strong runtime, not the center of the project; the core is the skills, the helper, and the workspace contract, which outlive any one runtime. See `cowork/SETUP.md` for the full path, `cowork/PROJECT_INSTRUCTIONS.md` for the standing instructions to paste into a project, and `cowork/SCHEDULED_TASKS.md` for paste-ready schedule templates.

**Other harnesses (portability targets, not all tested yet).** The same skills run on Claude Code, Codex, Cursor, Gemini CLI, and OpenCode. The skills are plain SKILL.md and portable without change; the per-harness plugin manifests still need validating against each harness's current plugin docs before publishing there. See `docs/PORTABILITY.md`. Manual install for any harness:

```
bash scripts/install.sh claude     # or: codex | cursor | <explicit path>
```

Then place the matching context file (`CLAUDE.md` / `AGENTS.md` / `GEMINI.md`) where your harness reads session context.

## The helper

`tyf` performs the concrete file operations so the agent does not freelance, and it is the single writer into `manuscript/`. Put it on your PATH with `scripts/install.sh` (which links `bin/tyf`), by adding this repo's `bin/` directory to PATH, or with `pipx install .`. Workspace commands are run from the workspace root; `tyf check` inspects the pack and is run from a repo clone (or with `TYF_PACK_ROOT` set).

```
tyf init <name>          tyf new-work <id> --type book --register <r>
tyf status               tyf open <work>          tyf mark-ready <work> <unit>
tyf audit <work> <unit>  tyf write <work> --from <draft> --confirm
tyf doctor [--repair]    # workspace integrity check; --repair heals missing structure
tyf check                # documentation-honesty check (zero tokens, deterministic)
tyf notice [--save] [--all] [--peek]   # attentive amanuensis: surface new/forgotten/stale items
tyf dismiss <hash>       # quiet an item; resurfaces if its context changes
tyf reconcile [--export] # show the ledger; --export mirrors it to Markdown
```

`tyf notice` is the attentive-amanuensis loop: it surfaces gaps you left to fill, lines that trail off, claims with no source, a style sheet lagging its manuscript, and unused registers, and it modifies nothing. Schedule it daily (`--save` records a digest to `.proposals/notices.md`) and work through it with `tyf reconcile`. It spends no tokens. It remembers what it has surfaced in a content-addressed ledger (`.tyf/ledger.db`), so it shows only genuinely new or resurfaced items rather than re-nagging, and it does this without git and without trusting timestamps; see `docs/ATTENTIVENESS.md`. When two authored passages conflict it never decides which wins; it surfaces the contradiction for you to adjudicate. An opt-in semantic layer that reads the diff and asks a model the few questions code cannot answer is specified, unwired, in `docs/LEARN_PASS.md`; it too only surfaces.

`tyf check` verifies the pack's own consistency: skill count, names, dead references, command drift, identical context files, valid JSON, no stray em-dashes. It runs automatically warn-only after every mutating command (so doc drift surfaces the moment structure changes, with no reliance on git or memory) and hard-fails as a standalone command for CI. This is the deterministic, zero-token half of the `keeping-documentation-honest` discipline; semantic drift still needs a reading pass.

## What is in this version

Sixteen skills, each carrying a rationalization table and a red-flag list, the device that keeps a commitment load-bearing under pressure rather than polite. The Milchin redactor discipline runs as a substrate and threads through the diagnosis pass, the editor, and the adversarial audit at every band. A documentation-honesty discipline keeps the routing docs from going stale after a structural change, on the principle that in an agentic system the docs are behavioral law. The pack ships Cowork packaging (plugin, project instructions, schedule templates), plugin and extension manifests for the other harnesses, three mirrored context files, the `tyf` helper, an example workspace, the workspace contract, a contributor guide, and RED/GREEN pressure scenarios, plus a product-lens acceptance-and-edge-case review (`tests/acceptance-and-edge-cases.md`) of how each skill breaks beyond the happy path.

## Status and testing

This is v0.1. Before treating it as production-bulletproof, run `tests/pressure-scenarios.md` against subagents in your harness: once with skills absent (expect the baseline failure) and once with skills present (expect compliance). Add any new rationalization that slips through to the relevant skill's table and re-run.

## Docs

- `TYF-manifesto-and-architecture.md`: the design doc; why TYF exists, the commitments, the four engines, the Zoom x Pass matrix, the redactor tradition, resolved decisions and open questions
- `docs/TYF_FOUNDATION.md`: roles, the single vocabulary, the Zoom x Pass matrix
- `docs/WORKSPACE_CONTRACT.md`: the author's workspace state files
- `docs/ATTENTIVENESS.md`: the notice ledger, memory without git, the discrepancy stance
- `docs/LEARN_PASS.md`: the opt-in, unwired semantic layer
- `docs/PORTABILITY.md`: per-harness install and the manifest-schema caveat
- `docs/WRITING_TYF_SKILLS.md`: contributor guide for new skills
- `docs/COMPARISON_SUPERPOWERS.md`: benchmark against the reference pack

## How it compares

`docs/COMPARISON_SUPERPOWERS.md` maps TYF skill-by-skill against `obra/superpowers`, the established reference, through a how-it-breaks lens. Short version: TYF's state, memory, and write-boundary design are ahead of superpowers for a no-git authored-prose domain, but superpowers has real usage and three disciplines TYF lacks (execution-to-completion, debugging/isolation, receiving critique). The honest gap is testing: TYF's RED/GREEN scenarios have not yet been run against a subagent.

## License

MIT. The design takes patterns, not code, from the projects in its provenance; every borrowed primitive is reimplemented clean so the license stays unambiguous.

*Authored with TYF.*
