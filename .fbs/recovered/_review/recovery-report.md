# Recovery report

- **Total extracted:** 68
- **Round-trip faithful:** 0
- **Confidence:** no-roundtrip-faithful-be
- **Confidence signals:** llm-hypothesis:tyf, pytest:tyf, signature:tyf
- **Candidates (round-trip fail/error):** 0
- **Stubs (signature, no behavioural verification):** 63
- **Hypotheses (LLM-proposed, unverified):** 5
- **Degraded stages:** 0
- **LLM/sub-agent evidence records:** 1

## LLM/sub-agent evidence

*Compact provenance only: request/prompt/response hashes and usage, not raw prompts or transcripts.*

- stage=proposer; surface=subagent; status=ok; prompt_chars=62546; prompt_hash=6387075ebbfe; request_id=d672c305f26145118259a0d7236d7c0d; response_hash=7d13d836ded4; response_kind=hypotheses

## Stubs (signature-derived)

*Type-level contracts from the public API. Round-trip does not apply — a stub does not predict behaviour, only the signature.*

- `CLIBehaviour_test_init_creates_and_is_idempotent` — test_tyf.py::CLIBehaviour::test_init_creates_and_is_idempotent
- `CLIBehaviour_test_write_refuses_without_confirm` — test_tyf.py::CLIBehaviour::test_write_refuses_without_confirm
- `CLIBehaviour_test_write_with_confirm_copies_and_logs` — test_tyf.py::CLIBehaviour::test_write_with_confirm_copies_and_logs
- `CLIBehaviour_test_doctor_flags_unlogged_manuscript_file` — test_tyf.py::CLIBehaviour::test_doctor_flags_unlogged_manuscript_file
- `CLIBehaviour_test_new_work_requires_workspace` — test_tyf.py::CLIBehaviour::test_new_work_requires_workspace
- `CLIBehaviour_test_write_requires_workspace` — test_tyf.py::CLIBehaviour::test_write_requires_workspace
- `CLIBehaviour_test_new_work_rejects_absolute_id` — test_tyf.py::CLIBehaviour::test_new_work_rejects_absolute_id
- `CLIBehaviour_test_new_work_rejects_parent_traversal` — test_tyf.py::CLIBehaviour::test_new_work_rejects_parent_traversal
- `CLIBehaviour_test_new_work_rejects_separator_in_id` — test_tyf.py::CLIBehaviour::test_new_work_rejects_separator_in_id
- `CLIBehaviour_test_write_rejects_traversal_work` — test_tyf.py::CLIBehaviour::test_write_rejects_traversal_work
- `CLIBehaviour_test_write_rejects_source_outside_drafts` — test_tyf.py::CLIBehaviour::test_write_rejects_source_outside_drafts
- `CLIBehaviour_test_write_refuses_silent_overwrite` — test_tyf.py::CLIBehaviour::test_write_refuses_silent_overwrite
- `CLIBehaviour_test_doctor_detects_out_of_band_edit` — test_tyf.py::CLIBehaviour::test_doctor_detects_out_of_band_edit
- `CLIBehaviour_test_mark_ready_requires_workspace` — test_tyf.py::CLIBehaviour::test_mark_ready_requires_workspace
- `CLIBehaviour_test_mark_ready_rejects_traversal` — test_tyf.py::CLIBehaviour::test_mark_ready_rejects_traversal
- `CLIBehaviour_test_open_rejects_traversal` — test_tyf.py::CLIBehaviour::test_open_rejects_traversal
- `CLIBehaviour_test_status_requires_workspace` — test_tyf.py::CLIBehaviour::test_status_requires_workspace
- `CLIBehaviour_test_init_refuses_nonempty_foreign_dir` — test_tyf.py::CLIBehaviour::test_init_refuses_nonempty_foreign_dir
- `CLIBehaviour_test_write_refuses_symlinked_work_escape` — test_tyf.py::CLIBehaviour::test_write_refuses_symlinked_work_escape
- `CLIBehaviour_test_write_force_refuses_out_of_band_edit` — test_tyf.py::CLIBehaviour::test_write_force_refuses_out_of_band_edit
- `CLIBehaviour_test_write_force_allows_clean_rewrite` — test_tyf.py::CLIBehaviour::test_write_force_allows_clean_rewrite
- `CLIBehaviour_test_mark_ready_requires_existing_work` — test_tyf.py::CLIBehaviour::test_mark_ready_requires_existing_work
- `CLIBehaviour_test_open_requires_existing_work` — test_tyf.py::CLIBehaviour::test_open_requires_existing_work
- `CLIBehaviour_test_audit_requires_existing_work` — test_tyf.py::CLIBehaviour::test_audit_requires_existing_work
- `CLIBehaviour_test_new_work_rejects_spaces_in_id` — test_tyf.py::CLIBehaviour::test_new_work_rejects_spaces_in_id
- `DocCheck_test_min_pack_is_clean` — test_tyf.py::DocCheck::test_min_pack_is_clean
- `DocCheck_test_repo_pack_is_clean` — test_tyf.py::DocCheck::test_repo_pack_is_clean
- `DocCheck_test_check_flags_legacy_ledger_path` — test_tyf.py::DocCheck::test_check_flags_legacy_ledger_path
- `DocCheck_test_check_flags_role_terminology_drift` — test_tyf.py::DocCheck::test_check_flags_role_terminology_drift
- `PackRoot_test_pack_root_env_override` — test_tyf.py::PackRoot::test_pack_root_env_override
- `Installer_test_bin_shim_runs_check` — test_tyf.py::Installer::test_bin_shim_runs_check
- `UpdateCheck_test_version_tuple_compares` — test_tyf.py::UpdateCheck::test_version_tuple_compares
- `UpdateCheck_test_should_check_throttle` — test_tyf.py::UpdateCheck::test_should_check_throttle
- `UpdateCheck_test_update_reports_newer_version` — test_tyf.py::UpdateCheck::test_update_reports_newer_version
- `UpdateCheck_test_update_reports_up_to_date` — test_tyf.py::UpdateCheck::test_update_reports_up_to_date
- `UpdateCheck_test_update_never_writes_to_the_pack` — test_tyf.py::UpdateCheck::test_update_never_writes_to_the_pack
- `signature_tyf_read_state` — tyf.py::read_state
- `signature_tyf_get` — tyf.py::get
- `signature_tyf_now` — tyf.py::now
- `signature_tyf_write` — tyf.py::write
- `signature_tyf_append` — tyf.py::append
- `signature_tyf_mkdirs` — tyf.py::mkdirs
- `signature_tyf_run_doc_check` — tyf.py::run_doc_check
- `signature_tyf_gather_notices` — tyf.py::gather_notices
- `signature_tyf_log_event` — tyf.py::log_event
- `signature_tyf_reconcile_notices` — tyf.py::reconcile_notices
- `signature_tyf_dismiss_notice` — tyf.py::dismiss_notice
- `signature_tyf_ledger_summary` — tyf.py::ledger_summary
- `signature_tyf_export_ledger_markdown` — tyf.py::export_ledger_markdown
- `signature_tyf_cmd_init` — tyf.py::cmd_init
- `signature_tyf_cmd_new_work` — tyf.py::cmd_new_work
- `signature_tyf_cmd_open` — tyf.py::cmd_open
- `signature_tyf_cmd_status` — tyf.py::cmd_status
- `signature_tyf_cmd_mark_ready` — tyf.py::cmd_mark_ready
- `signature_tyf_cmd_audit` — tyf.py::cmd_audit
- `signature_tyf_cmd_write` — tyf.py::cmd_write
- `signature_tyf_cmd_doctor` — tyf.py::cmd_doctor
- `signature_tyf_cmd_check` — tyf.py::cmd_check
- `signature_tyf_cmd_notice` — tyf.py::cmd_notice
- `signature_tyf_cmd_dismiss` — tyf.py::cmd_dismiss
- `signature_tyf_cmd_reconcile` — tyf.py::cmd_reconcile
- `signature_tyf_cmd_update` — tyf.py::cmd_update
- `signature_tyf_main` — tyf.py::main

## Hypotheses (LLM-proposed)

*Implicit invariants the LLM believes are derivable from the code but are not covered by tests or signatures. **Unverified** — each one requires manual review before promotion into `be/`.*

- `hypothesis_tyf_peek-notice-leaves-ledger-unchanged` — Peek notice leaves ledger unchanged
- `hypothesis_tyf_dismiss-accepts-unique-hash-prefix` — Dismiss accepts unique hash prefix
- `hypothesis_tyf_dismiss-rejects-ambiguous-hash-prefix` — Dismiss rejects ambiguous hash prefix
- `hypothesis_tyf_reconcile-export-mirrors-ledger` — Reconcile export mirrors ledger
- `hypothesis_tyf_mutating-command-doc-check-is-warn-only` — Mutating command doc check is warn only
