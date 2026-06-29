# Recovery Operator Plan

Review-only advisory artifact. No requirements were promoted into the state of record.

## Proved
- Recovery source: `C:\Users\maste\Documents\TYF`
- Review output: `C:\Users\maste\Documents\TYF\.fbs\recovered`
- docs: 80 (50 intent / 27 assessment / 3 noise, 0 legacy), 70 orphan(s), 0 with broken link(s), 13 discrepancy(ies); 376 requirement + 80 recommendation hypotheses; 0 TODO/FIXME; 4 undocumented module(s), 0 drift candidate(s), 68 large function(s); 14 prioritised Be gap(s)

## Suspected
- Recovered confidence: `no-roundtrip-faithful-be` (pytest:architecture_contracts, pytest:codex_approvals, pytest:codex_bridge_context, pytest:codex_hook_recorder, pytest:concept_review, pytest:continuity_review, pytest:graph_projection, pytest:polish_and_decisions, pytest:rc_recovery_doctor, pytest:tyf, pytest:workbench_mcp, pytest:workbench_recovery_routes, pytest:workbench_status, pytest:workbench_v06, signature:tyf, signature:tyf_architecture_contracts, signature:tyf_codex_approvals, signature:tyf_codex_bridge, signature:tyf_codex_bridge_v07, signature:tyf_codex_hook, signature:tyf_codex_hook_validate, signature:tyf_codex_schema, signature:tyf_concept_review, signature:tyf_continuity_decision, signature:tyf_continuity_review, signature:tyf_graph_projection, signature:tyf_polish_review, signature:tyf_pressure_eval, signature:tyf_rc_doctor, signature:tyf_recovery, signature:tyf_review, signature:tyf_workbench_live, signature:tyf_workbench_mcp, signature:tyf_workbench_slots, signature:tyf_workbench_status, signature:tyf_workbench_v06, signature:validate_codex_plugin)

## Noisy
- llm proposer timeout: fbs: no sub-agent serviced the review query within 5s at .fbs\store\agent_io\queries\q-b9916b32122acca6-bca30c259dba4bc2a2f0b972046cc336.response.json. A review-mode Be needs an LLM sub-agent to judge it; this path is NOT deterministic. To proceed: (1) run inside Claude Code or Codex, which services this transport; (2) set FBS_LLM_BACKEND=sdk with ANTHROPIC_API_KEY for a direct SDK reviewer; or (3) cover the behaviour with a hard @tool-check Be (cli/file/http/ansi) instead of review mode. Set FBS_NO_SUBAGENT=1 to fail fast instead of waiting.
- 547 static stub(s) need review or execution opt-in

## Next 48h Actions
- Inspect `_review/doc-archaeology.md` before promoting any recovered claim.
- Use `fbs state --no-run` on promoted artifacts to inspect R/F/Be links.
- Run executable recovery only with explicit ownership and `--allow-exec`.

## Advisory R suggestions
- Review candidate: tyf
- Review candidate: pass
- Review candidate: .review/
- Review candidate: manuscript/
- Review candidate: prompt
- Review candidate: ide
- Review candidate: able
- Review candidate: init
- Review candidate: doctor
- Review candidate: tyf start

No requirements were promoted; use `fbs requirements add` only after human review.
