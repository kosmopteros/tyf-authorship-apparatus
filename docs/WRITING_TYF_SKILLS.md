# Writing a TYF skill

TYF is open to expansion. New skills are welcome when they serve one of the five roles (interviewer, amanuensis, first reader, faithful editor, redactor) and respect the commitments. This guide keeps additions consistent with the discipline.

## A skill is a reusable discipline

A TYF skill is a reference for a proven authorial discipline, not a narrative about one project and not a project convention (those go in the workspace router). If a rule is mechanically enforceable, put it in the helper or a hook rather than in prose.

## Required shape

Every skill is a directory under `skills/` with a `SKILL.md`. The frontmatter has two fields:

- `name`: matches the directory, 64 characters or fewer.
- `description`: starts with "Use when", describes only the triggering conditions, third person, 1024 characters or fewer. Never summarize the workflow in the description; a summary becomes a shortcut that lets the agent skip reading the body.

The body, for any discipline skill:

1. **Overview**: what the discipline is and which pass or substrate it serves.
2. **The disciplined move**: the concrete behavior, including any preconditions that justify refusing.
3. **Rationalization table**: the excuse the agent will tell itself, the reality, and what to do instead. This is the load-bearing section. A discipline without it gets eaten under pressure.
4. **Red flags**: the catch-yourself list.
5. **Output shape or commands**: the artifact the skill produces.
6. **Next**: the downstream and upstream skills.

## Respect the substrates

If your skill touches prose, it reads the voice registers and the redactor canon. Voice governs how the work sounds; the redactor governs whether it holds together across body scales. Do not duplicate those checks; reference `managing-voice` and `keeping-the-redactor-canon`.

## Respect the controlled write

If your skill produces anything that could enter a manuscript, it writes a candidate or a proposal, never the manuscript. The only writer into `manuscript/` is `tyf write`. State this in the skill.

## Cover the failure modes, not just the happy path

A skill that only works on clean input is a demo. Before submitting, write its acceptance criteria (what correct means beyond the happy path) and two to five break cases: empty input, adversarial input, ambiguity, contradiction, missing preconditions, and injection where relevant. Add them as an `## Acceptance and edge cases` section in the skill and, for high-stakes skills, as RED/GREEN scenarios in `tests/pressure-scenarios.md`. See `tests/acceptance-and-edge-cases.md` for the existing review and house style.

## Test it: RED then GREEN

Writing a skill is test-driven. Write a pressure scenario first (see `tests/pressure-scenarios.md`): combine at least three pressures, force a concrete choice, allow no easy out. Run it against a subagent without the skill and watch it fail (RED). Add the skill and watch it comply (GREEN). When the subagent finds a new rationalization that slips past, add it to the table and re-run. That is the refactor step.

A skill that has not been watched failing without it does not yet teach the right thing.

## Prose conventions

Follow TYF's own anti-patterns in the skill prose: no em-dashes (the one exception is the canonical `[AUTHOR: needed — what]` token), no stacked-negation triads, no "Not X. Y." fragments. The pack audits for exactly these, so it should hold itself to them.

## A new skill is a structural change

Adding or renaming a skill changes the pack's structure, so it triggers `keeping-documentation-honest`. Before you call it done, walk that skill's checklist: the README skill table, the three context files, the dispatcher selection table, the manifests, the install scripts, VALIDATION, and the tests must all reflect the new skill and the new count. Prefer counts that are computed rather than written.

## Submit

Run the validation in `VALIDATION.md`, add your pressure scenario, and open a pull request describing the role the skill serves and the RED baseline you observed.
