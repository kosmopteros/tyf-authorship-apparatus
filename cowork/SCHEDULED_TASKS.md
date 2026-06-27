# Cowork scheduled-task templates

Paste-ready prompts for the TYF ongoing-work cadence. Create each with `/schedule` in a Cowork task, or from the Scheduled sidebar. Each scheduled task runs in its own session with access to your files and skills, so it can run the full skill, not just answer a question. Use cloud Routines for cadences that should run while the laptop is closed.

Every template below assumes the book folder is the single work, with root-level `drafts/`, `manuscript/`, `.review/`, and `.proposals/`. It observes and reports. None of the templates edits a manuscript. That is by design.

## Daily: doctor and digest
> In my TYF workspace at <PATH>, run `tyf doctor`. Then load `using-tyf` and produce a short digest: open findings in `.review/`, anything in `.proposals/` awaiting my commit, and any manuscript change without a matching write-log entry. Write the digest to `.proposals/daily-digest.md`. Do not edit any manuscript.

## On save or hourly: AI-tell and fence scan
> In my TYF workspace at <PATH>, find chapters in `drafts/` or `manuscript/` changed in the last hour. Load `managing-voice` and run an AI-tell scan and a register-fence check on each. Write findings to `.review/`. Propose nothing into the manuscript.

## Weekly: re-audit units marked ready
> In my TYF workspace at <PATH>, read `.review/ready.md`. For every unit marked ready since the last run, load `auditing-adversarially` and run the full adversarial audit, including the redactor integrity checks against the running style sheet. Write findings to `.review/`. Mark no unit done; that is the author's call.

## Weekly: voice-drift scan
> In my TYF workspace at <PATH>, load `managing-voice` and compare recent manuscript prose against the work's declared registers and exemplar passages. Report drift to `.review/voice-drift.md`. Change nothing.

## Return after idle: re-orientation
> In my TYF workspace at <PATH>, run `tyf resume` first, then load `working-the-workspace` and `scheduling-ongoing-work`. Produce a re-orientation digest: the active band, open gates, the most recent `.review/` findings, and the next decision waiting on me. Write it to `.proposals/reorientation.md`.

## Daily: the attentive amanuensis (deterministic, zero tokens)
> In my TYF workspace at <PATH>, run `tyf notice --save`. This surfaces gaps I left to fill, lines that trail off unfinished, claims with no source, a style sheet lagging its manuscript, and unused registers, then appends a dated digest to `.proposals/notices.md`. Do not modify anything; just hand me the list. If `tyf reconcile` shows old open items, include a one-line reminder of how many are still open.

## Daily: check for a newer TYF release (notify-only, zero tokens)
> Run `tyf update`. It reports whether a newer TYF release is out and the one-line command to update through this harness. It pulls nothing and changes nothing. If a new version is available, tell me the version and how to update; otherwise say nothing needs doing.

## Optional, opt-in: the semantic Learn pass (spends tokens; off by default)
> Only if I have explicitly enabled it (see docs/LEARN_PASS.md). Read only the manuscript units changed since your last run. For each, ask the four semantic questions in docs/LEARN_PASS.md: contradiction with a logged claim or another passage, argument moved past the outline, register drift, or tacit knowledge not yet recorded. Append any findings to `.proposals/notices.md` as questions for me. Modify nothing. If no unit changed, do nothing and spend no tokens.
