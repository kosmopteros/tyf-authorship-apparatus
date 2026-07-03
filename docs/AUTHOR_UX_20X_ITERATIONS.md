# Author UX 20x implementation log

Status: implementation notes for the 10/10 non-technical author UX direction.

The target is not a better command list. The target is that a non-technical author can say “let’s work on the book,” and the desktop agent runs TYF, opens the local Workbench, preserves boundaries, and asks one useful material question.

## Pass 01 — desktop assumption

Code/docs decision: document that the intended workplace is a PC or Mac running Codex Desktop or Claude Code Desktop.

Critique: local helper servers are allowed; the boundary is local-first authority, not server absence.

## Pass 02 — author does not operate terminal

Code/docs decision: `using-tyf` now says the agent runs TYF commands and opens local browser surfaces.

Critique: this must be skill doctrine, not optional etiquette.

## Pass 03 — visual desk command

Code decision: `tyf workbench --open` is the happy path and implies served mode in the live Workbench parser.

Critique: asking a non-technical author to choose static vs served mode is bad UX.

## Pass 04 — static mode demotion

Code/docs decision: static mode is documented as inspection-only; served mode is used for browser editing.

Critique: a `file://` Workbench that cannot save drafts should never be mistaken for the real WebUI.

## Pass 05 — no compatibility command sprawl

Code decision: keep `tyf workbench` as the single public Workbench command rather than restoring `tyf-workbench`.

Critique: compatibility aliases help operators but confuse author-facing doctrine.

## Pass 06 — agent runbook

Docs decision: add `docs/DESKTOP_AGENT_RUNBOOK.md` for Codex Desktop and Claude Code Desktop operators.

Critique: the agent needs instructions, but the author should not see a checklist of commands.

## Pass 07 — Start Here prompt

Docs decision: update `docs/START_HERE.md` prompts to say the agent may run local helpers, local MCP, and the local browser Workbench.

Critique: the paste prompt must encode the whole author experience, not only installation.

## Pass 08 — initialization skill

Skill decision: update `initializing-a-workspace` so setup is agent-operated and non-technical authors are not asked to manage work ids or commands.

Critique: project init is the first UX impression; it must feel like help, not DevOps.

## Pass 09 — Workbench runbook language

Docs decision: update `WORKBENCH_RUNBOOK.md` so the agent runs the Workbench and gives the author a localhost URL only if browser opening fails.

Critique: “copy this URL” is acceptable fallback; “run these commands” is not.

## Pass 10 — tests for skill doctrine

Test decision: add tests that assert the skills mention Codex Desktop, Claude Code Desktop, `tyf workbench --open`, and agent-operated commands.

Critique: UX doctrine should fail tests when it drifts.

## Pass 11 — tests for runbooks

Test decision: add tests that assert Start Here and the desktop runbook teach the same governed flow.

Critique: docs must stay aligned with skill behavior.

## Pass 12 — manuscript boundary preserved

Doctrine decision: every author-facing flow repeats that `manuscript/` remains read-only / Gate-protected.

Critique: better UX must not weaken the safety model.

## Pass 13 — local server boundary

Doctrine decision: local servers are fine; remote authority is not.

Critique: do not let “Node/Next is possible” become “cloud app is required.”

## Pass 14 — one useful question

Skill decision: after setup, the agent asks one substantive question or gives one candidate move.

Critique: a 10/10 author experience avoids both terminal ceremony and questionnaire ceremony.

## Pass 15 — existing material first

Skill decision: arrivals are preserved before analysis and before Workbench use.

Critique: non-technical authors often bring messy folders; preserving first builds trust.

## Pass 16 — browser failure fallback

Runbook decision: if browser launch fails, give the local URL in plain language.

Critique: this is the only operational fallback the author should see.

## Pass 17 — review commands stay agent tools

Runbook decision: `tyf-review continuity`, `tyf-review polish`, and `tyf-review doctor` are agent-operated near-final book tools.

Critique: review power should not become author homework.

## Pass 18 — no silent commits

Doctrine decision: the agent may use git only with explicit recovery points and no silent commits.

Critique: local-first does not mean surprising version-control behavior.

## Pass 19 — no hidden manuscript writes

Doctrine decision: the UI, agent, and helper commands may help draft and review, but manuscript changes remain Gate-only.

Critique: the Workbench must feel powerful without becoming a manuscript editor.

## Pass 20 — 10/10 target statement

Target: the author says “let’s work on the book”; the agent creates or enters the workspace, preserves arrivals, opens the Workbench, and asks one useful material question without making the author operate TYF.

## Remaining after this PR

- Dogfood the updated flow on a real PC/Mac with Codex Desktop or Claude Code Desktop.
- Consider a future local app shell only after the governed Python Workbench loop proves useful.
- Add a tiny short-lived server smoke test if CI runtime permits it.
