---
name: scheduling-ongoing-work
description: Use when authorship is iterative and ongoing rather than a single session: setting up recurring audits, voice-drift scans, return-after-time digests, proposal review, or any hook that should fire on save, on open, or on a cadence
---

# Scheduling ongoing work

## Overview

After intake, authorship is iterative, not a pipeline. The author drafts, revises, walks away, returns, changes their mind about chapter three. The cadence handles this phase with a harness: small named hooks, efficient context loading, and controlled self-extension. On Cowork it is implemented with scheduled tasks and Routines; on other harnesses with the hook definitions in `manifest.yaml`.

The cadence keeps the iterative phase tractable without turning it into a workflow.

## The three responsibilities

- **Contextual hooks.** Events fire small, named, inspectable actions. Saving a chapter fires an AI-tell scan and a register-fence check. Opening a chapter loads only the relevant registers, the claims that touch this chapter, the redactor style sheet, and the latest `.review/`. Marking a unit ready fires the adversarial audit.
- **Efficient context.** A workspace does not fit in one context window. Load only what the active band, pass, and work need. Progressive disclosure is the default; the author can override.
- **Gated self-extension.** The harness observes which proposals the author accepts and rejects, which findings recur, which questions they keep answering by hand. From that it proposes, never applies, new entries: an anti-pattern, a register fence, a terminology rule, a new skill. It writes to `.proposals/`, never to `voice/`, `redactor-canon/`, or the skills directory.

## On Cowork

Scheduled tasks run as their own session with access to your files, skills, and plugins. Use them for the standing cadence:

| Cadence | What it runs |
|---|---|
| On save (or hourly) | AI-tell scan and register-fence check on changed chapters |
| Daily | `tyf doctor`; a digest of open `.review/` findings and `.proposals/` |
| Weekly | re-audit of units marked ready since last run; voice-drift scan |
| Return after N idle days | a re-orientation digest: where the work was left, open gates, open findings |

Set them with `/schedule` in a Cowork task, or from the Scheduled sidebar. Use cloud Routines for cadences that should run while the laptop is closed. See `cowork/SCHEDULED_TASKS.md` for paste-ready templates.

## The attentive amanuensis loop

The most useful recurring task surfaces what the author may have forgotten, and modifies nothing. `tyf notice` is deterministic and spends no tokens, and it is ledger-backed so it surfaces only what is genuinely new or resurfaced rather than re-nagging (see `docs/ATTENTIVENESS.md`): it surfaces gaps left to fill, lines that trail off, claims with no source, a style sheet lagging its manuscript, and unused registers. Schedule it (daily is typical) with `--save` so a dated digest lands in `.proposals/notices.md`, then work through it with `tyf reconcile`. A second, opt-in semantic layer (the Learn pass, see `docs/LEARN_PASS.md`) reads only the diff and asks a model the few questions code cannot answer, again surfacing only. Both obey the rule below: they notice and hand back; they never heal on their own.

## The disciplined move

Hooks observe and propose. They never apply a change to a manuscript or to the substrate. A scheduled audit writes findings to `.review/`; it does not fix. A self-extension proposal goes to `.proposals/`; the author commits it. The cadence makes the iterative phase regular without making it autonomous.

## Rationalization table

| What you will tell yourself | The reality | Do instead |
|---|---|---|
| "A scheduled task may as well fix what it finds." | Autonomous fixes are the prompt-to-manuscript anti-pattern on a timer. | Write findings to `.review/`; the author decides. |
| "Self-extension should update the canon directly." | Direct writes to the substrate remove the author's commit. | Write proposals to `.proposals/`; never to the canon or skills. |
| "Load the whole workspace so nothing is missed." | Loading everything wastes context and buries the active work. | Load only what the active band, pass, and work need. |
| "More hooks is better." | Hook sprawl makes the harness unreadable. | Keep the minimal set: save, open, mark-ready, daily, weekly, return. |

## Red flags: stop if you catch yourself

- A scheduled task editing a manuscript.
- Self-extension writing to `voice/`, `redactor-canon/`, or `skills/`.
- Hydrating the whole workspace for one chapter's work.
- Adding hooks beyond the minimal taxonomy without reason.

## Next

Hooks fire the existing passes: `auditing-adversarially`, `managing-voice`, `keeping-the-redactor-canon`. Anything a hook proposes still enters the work only through `controlling-manuscript-writes`.
