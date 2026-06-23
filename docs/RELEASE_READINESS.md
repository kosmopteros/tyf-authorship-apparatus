# TYF Release Readiness Review

This page is the maintainer-facing acceptance checklist for the current beta
round. It is not a marketing page and not a release blessing by itself. It
separates what is locally proven from what still needs real author use.

## Current Verdict

TYF is ready for a local-first beta start of a single book folder.

The proved launch promise is narrow and useful: preserve existing material,
start without a final title, keep candidate prose in `drafts/`, keep
`manuscript/` behind the Gate, recover the live writing context with `tyf
resume`, and keep the helper, skills, author context, and installer surfaces in
step.

## Evidence-Green

- `163` stdlib helper, documentation, installer, and packaging tests pass.
- `128/128` internal acceptance scenarios have current direct RED proof.
- CI passes on the pull request for install, Python 3.9, and Python 3.12.
- Public TYF-visible surfaces do not require private development context.
- The exported author package excludes workshop debris and keeps clean author
  context templates.
- The single-work beta surface is root-first: `work.yaml`, `drafts/`,
  `.review/`, and `manuscript/`.
- Arrival from chat, text, folder, zip, binary, unreadable, and oversized
  material preserves source before any drafting claim.
- The Gate uses proposal, audit, review, decision, and write records rather than
  a bare confirmation flag.
- `tyf doctor --repair` heals missing ordinary structure without clobbering
  authored files, while refusing to recreate lost canonical event history.

## Not Claimed Yet

- Production-bulletproof cross-runtime behavior.
- Large-scale author usage across many books.
- A mature auto-update path beyond notify-only `tyf update`.
- A mature parallel-agent writing workflow.
- Real Cowork app validation beyond repository-level instructions, templates,
  packaging, and local helper checks.
- A complete semantic engine for contradiction graphs, retrieval, or citation
  confidence.

## Maintainer Acceptance Checklist

Before calling the beta release accepted, run or confirm:

- The pull request CI is green.
- `python tests/test_tyf.py -v` passes locally.
- `python scripts/tyf.py check --strict` reports no documentation drift.
- The public/private boundary scan finds no private development context in
  TYF-visible surfaces.
- A fresh install can create a separate book workspace, preserve an arrival
  scaffold, open `.review/writing-runway.md`, and leave `manuscript/` empty.
- At least one small real writing session starts from `docs/START_HERE.md`
  without the author needing to operate the helper command list.

## First Real Use

The first beta use should be treated as validation, not ceremony. Start a real
book folder, preserve the cold-start scaffold, write one candidate passage in
`drafts/candidate-draft.md`, run `tyf resume`, run `tyf notice --peek`, and pass
one tiny accepted unit through the Gate only if the author actually accepts it.

Record any friction as a release finding rather than smoothing it over in prose.
