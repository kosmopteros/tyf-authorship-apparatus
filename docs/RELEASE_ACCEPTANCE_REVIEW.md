# TYF 0.6.3 Release Acceptance Review

Date: 2026-07-03

This note reviews whether TYF 0.6.3 satisfies the declared local-first
single-book beta promise. It is a product disposition aid, not a substitute for
the maintainer's acceptance decision.

## Recommendation

Accept TYF 0.6.3 as a product-ready local-first single-book beta release
candidate.

Do not score it as a mature mass-market product or as the complete long-term
Workbench vision. The correct release claim is narrower: an author can bring
material, begin a sitting, preserve source and voice, produce candidate prose,
return later, inspect and work with the draft surface, and move accepted text
into `manuscript/` through the Gate without TYF becoming the writer.

## Evidence Reviewed

- `fbs finish --version-impact "docs: add TYF 0.6.3 release acceptance review"` passed.
- `fbs prove-red` reported all `178` Be carry current bound RED proof.
- `fbs test` executed `178` Be with `178` passing and no gaps.
- `fbs release-check` reported package and plugin version `0.6.3`.
- `fbs be auth status` reported `178/178` current authorized execution-sensitive Be.
- `python -m pytest -q` passed `240` aggregate pytest cases.
- `python scripts/tyf.py check --strict` reported no documentation drift.
- `python scripts/validate_codex_plugin.py .` passed.

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

The second residual risk is disposition drift. The evidence record correctly
shows all open requirements as evidence-strong but review-required. Closing them
as `done` should be a maintainer product decision after reviewing this evidence,
not an automatic side effect of a green gate.

## Acceptance Decision

Recommended decision:

`ship candidate for real author use`

If accepted, record the product decision in the release process, then use real
writing sessions as the next validation source. Do not reopen the beta for
speculative later-workbench improvements unless they become concrete defects in
the declared beta promise.
