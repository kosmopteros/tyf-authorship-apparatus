# TYF 0.6.5 Product Disposition

Date: 2026-07-03

This note reviews whether TYF 0.6.5 satisfies the declared local-first
single-book beta promise and records the product disposition for this release
scope.

## Decision

TYF 0.6.5 is accepted as a product-ready local-first single-book beta.

Do not score it as a mature mass-market product or as the complete long-term
Workbench vision. The correct release claim is narrower: an author can bring
material, begin a sitting, preserve source and voice, produce candidate prose,
return later, inspect and work with the draft surface, and move accepted text
into `manuscript/` through the Gate without TYF becoming the writer.

## Evidence Reviewed

- `fbs finish --version-impact "patch: release TYF 0.6.5 Product Disposition"` passes.
- `fbs prove-red` reported all `179` Be carry current bound RED proof.
- `fbs test` executed `179` Be with `179` passing and no gaps.
- `fbs release-check` reported package and plugin version `0.6.5`.
- `fbs be auth status` reported `179/179` current authorized execution-sensitive Be.
- `python -m pytest -q` passed `241` aggregate pytest cases.
- `python scripts/tyf.py check --strict` reported no documentation drift.
- `python scripts/validate_codex_plugin.py .` passed.
- `fbs r` reports no open requirements in the active view after the evidence-led
  requirements were explicitly dispositioned as `done`.

## Proven Beta Promise

- The book folder is the single work for the beta surface.
- `tyf start` works without a title and opens the writing runway without
  touching `manuscript/`.
- Arrivals from text, chat, folder, zip, unreadable, oversized, formatted, and
  illustrated material are preserved before any drafting claim.
- Source fragments, structure records, gentle attention packets, continuing
  sessions, diagnostics, feedback triage, character consultation, and
  typographic treatment are review-only surfaces until the author accepts a
  manuscript change.
- The Workbench provides the local multi-unit draft/manuscript surface while
  keeping draft saves conflict-protected and `manuscript/` Gate-only.
- Codex integration has a current skill/plugin path, workspace-bounded hooks,
  and a Codex-recognized Workbench MCP configuration path that exposes no tools
  outside the bound book workspace.
- The Gate uses proposal, audit, author review, decision, and controlled write
  records rather than a bare confirmation flag.
- Release packaging separates author context from contributor context and keeps
  private development machinery out of TYF-visible author surfaces.
- Documentation honesty, manifest version alignment, plugin validation, and
  release-count checks are current.

## Not Claimed

- Print-ready PDF, KDP preflight, publisher templates, or final production
  export.
- Mature longitudinal memory across months of author use.
- Broad multi-author or cross-harness usage proof.
- Production-bulletproof behavior in every host runtime.
- A mature auto-update path beyond the current local install/update surfaces.
- A complete semantic engine for contradiction graphs, retrieval, citation
  confidence, or multilingual evaluation.

These are roadmap items unless a real author session reveals that one blocks
the current beta promise.

## Residual Product Risk

The primary residual risk is field evidence, not repository evidence. The
apparatus is strong enough to start real writing, but the product still needs
live author sessions to reveal friction in pacing, question quality, Workbench
ergonomics, treatment depth, and Gate comprehension.

The second residual risk is scope creep after acceptance. The release is done
for the declared beta promise; future Workbench, print, longitudinal-memory, or
semantic-engine improvements should enter as new requirements rather than
reopening this beta unless real author use reveals a blocker in the accepted
scope.

## Acceptance Decision

Decision recorded:

`ship TYF 0.6.5 for real author use`

Use real writing sessions as the next validation source. Do not reopen this beta
for speculative later-workbench improvements unless they become concrete defects
in the declared beta promise.
