# Recovery Operator Plan

Review-only advisory artifact. No requirements were promoted into the state of record.

## Proved
- Recovery source: `C:\Users\maste\Documents\TYF`
- Review output: `C:\Users\maste\Documents\TYF\.fbs\recovered`
- docs: 46 (33 intent / 11 assessment / 2 noise, 0 legacy), 38 orphan(s), 0 with broken link(s), 4 discrepancy(ies); 212 requirement + 18 recommendation hypotheses; 0 TODO/FIXME; 0 undocumented module(s), 0 drift candidate(s), 6 large function(s); 4 prioritised Be gap(s)

## Suspected
- Recovered confidence: `no-roundtrip-faithful-be` (llm-hypothesis:tyf, pytest:tyf, signature:tyf)
- 5 hypothesis Be item(s) need triage

## Noisy
- 63 static stub(s) need review or execution opt-in

## Next 48h Actions
- Inspect `_review/doc-archaeology.md` before promoting any recovered claim.
- Use `fbs state --no-run` on promoted artifacts to inspect R/F/Be links.
- Run executable recovery only with explicit ownership and `--allow-exec`.

## Advisory R suggestions
- Review candidate: --confirm
- Review candidate: all-or-nothing
- Review candidate: pass
- Review candidate: stale
- Review candidate: cloud
- Review candidate: consent
- Review candidate: tyf
- Review candidate: using-tyf
- Review candidate: docs/LEARN_PASS.md
- Review candidate: init

No requirements were promoted; use `fbs requirements add` only after human review.
