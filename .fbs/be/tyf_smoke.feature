Feature: TYF helper smoke suite

  @covers:tyf-helper-current-contract @bind-file:scripts/tyf.py @bind-file:tests/test_tyf.py @tool-check:cli
  Scenario: helper happy path supports first writing session
    When Run "python tests/test_tyf.py CLIBehaviour.test_start_is_plain_language_front_door_for_new_book CLIBehaviour.test_write_with_decision_copies_and_logs -v"
    Then Exit code is 0

  @covers:tyf-helper-current-contract @bind-file:scripts/tyf.py @bind-file:tests/test_solo_oracles.py @tool-check:cli
  Scenario: helper command surface stays visible
    When Run "python tests/test_solo_oracles.py helper"
    Then Exit code is 0

  @covers:tyf-helper-current-contract @criterion:bad-outcome @criterion:edge @criterion:boundary @criterion:integration @criterion:security @bind-file:scripts/tyf.py @bind-file:tests/test_tyf.py @bind-file:tests/test_solo_oracles.py @tool-check:cli
  Scenario: helper enforces proposal audit decision write gate
    When Run "python tests/test_solo_oracles.py gate"
    Then Exit code is 0

  @covers:tyf-work-state-machine-contract @bind-file:scripts/tyf.py @bind-file:tests/test_tyf.py @bind-file:tests/test_solo_oracles.py @tool-check:cli
  Scenario: helper advances work status through proposal audit accept write
    When Run "python tests/test_tyf.py CLIBehaviour.test_gate_updates_work_status_across_transitions -v"
    Then Exit code is 0

  @covers:tyf-work-state-machine-contract @criterion:bad-outcome @criterion:edge @criterion:boundary @criterion:integration @criterion:security @bind-file:scripts/tyf.py @bind-file:tests/test_tyf.py @bind-file:tests/test_solo_oracles.py @tool-check:cli
  Scenario: helper refuses acceptance before audited state
    When Run "python tests/test_tyf.py CLIBehaviour.test_accept_refuses_before_passing_audit_state -v"
    Then Exit code is 0

  @covers:tyf-work-state-machine-contract @criterion:bad-outcome @criterion:edge @criterion:boundary @criterion:integration @criterion:security @bind-file:scripts/tyf.py @bind-file:tests/test_tyf.py @bind-file:tests/test_solo_oracles.py @tool-check:cli
  Scenario: helper refuses acceptance after failed audit state
    When Run "python tests/test_tyf.py CLIBehaviour.test_accept_refuses_after_failed_audit_state -v"
    Then Exit code is 0

  @covers:tyf-work-state-machine-contract @criterion:bad-outcome @criterion:edge @criterion:boundary @criterion:integration @criterion:security @bind-file:scripts/tyf.py @bind-file:tests/test_tyf.py @bind-file:tests/test_solo_oracles.py @tool-check:cli
  Scenario: helper refuses acceptance using another proposal audit
    When Run "python tests/test_tyf.py CLIBehaviour.test_accept_requires_audit_for_the_same_proposal -v"
    Then Exit code is 0

  @covers:tyf-work-state-machine-contract @criterion:bad-outcome @criterion:edge @criterion:boundary @criterion:integration @criterion:security @bind-file:scripts/tyf.py @bind-file:tests/test_tyf.py @bind-file:tests/test_solo_oracles.py @tool-check:cli
  Scenario: helper refuses write outside accepted state
    When Run "python tests/test_tyf.py CLIBehaviour.test_write_refuses_when_work_status_is_not_accepted -v"
    Then Exit code is 0

  @covers:tyf-amanuensis-entry-contract @bind-file:scripts/tyf.py @bind-file:tests/test_tyf.py @bind-file:tests/test_solo_oracles.py @tool-check:cli
  Scenario: amanuensis entry structural oracle remains wired
    When Run "python tests/test_solo_oracles.py amanuensis-entry"
    Then Exit code is 0

  @covers:tyf-amanuensis-entry-contract @criterion:bad-outcome @criterion:edge @criterion:boundary @criterion:integration @bind-file:scripts/tyf.py @bind-file:tests/test_tyf.py @tool-check:cli
  Scenario: helper starts without a title and keeps fresh intake non-blocking
    When Run "python tests/test_tyf.py CLIBehaviour.test_start_allows_no_title_and_keeps_intake_non_blocking -v"
    Then Exit code is 0

  @covers:tyf-amanuensis-entry-contract @criterion:bad-outcome @criterion:edge @criterion:boundary @criterion:integration @bind-file:scripts/tyf.py @bind-file:tests/test_tyf.py @tool-check:cli
  Scenario: first-session evidence is source evidence not draft prose
    When Run "python tests/test_tyf.py CLIBehaviour.test_begin_creates_first_session_packet_without_manuscript_text -v"
    Then Exit code is 0

  @covers:tyf-amanuensis-entry-contract @criterion:bad-outcome @criterion:edge @criterion:boundary @criterion:integration @criterion:security @bind-file:scripts/tyf.py @bind-file:tests/test_tyf.py @bind-file:skills/ingesting-sources/SKILL.md @tool-check:cli
  Scenario: import preserves chat and bundle arrivals without manuscript writes
    When Run "python tests/test_tyf.py CLIBehaviour.test_import_chat_preserves_raw_input_creates_titleless_work_and_fragment CLIBehaviour.test_import_zip_preserves_bundle_without_manuscript_write -v"
    Then Exit code is 0

  @covers:tyf-portable-workspace-contract @criterion:bad-outcome @criterion:edge @criterion:boundary @criterion:integration @bind-file:scripts/tyf.py @bind-file:tests/test_tyf.py @bind-file:skills/ingesting-sources/SKILL.md @tool-check:cli
  Scenario: text and zip arrivals stay portable without manuscript writes
    When Run "python tests/test_tyf.py CLIBehaviour.test_import_chat_preserves_raw_input_creates_titleless_work_and_fragment CLIBehaviour.test_import_zip_preserves_bundle_without_manuscript_write -v"
    Then Exit code is 0

  @covers:tyf-amanuensis-entry-contract @criterion:bad-outcome @criterion:edge @criterion:boundary @criterion:integration @criterion:security @bind-file:scripts/tyf.py @bind-file:tests/test_tyf.py @bind-file:skills/ingesting-sources/SKILL.md @tool-check:cli
  Scenario: folder dumps and TYF-shaped zips stay contained until organized
    When Run "python tests/test_tyf.py CLIBehaviour.test_import_folder_preserves_tree_and_lists_without_live_merge CLIBehaviour.test_import_tyf_shaped_zip_is_detected_without_merging -v"
    Then Exit code is 0

  @covers:tyf-portable-workspace-contract @criterion:bad-outcome @criterion:edge @criterion:boundary @criterion:integration @bind-file:scripts/tyf.py @bind-file:tests/test_tyf.py @bind-file:skills/ingesting-sources/SKILL.md @tool-check:cli
  Scenario: folder dumps and TYF-shaped zips stay portable until organized
    When Run "python tests/test_tyf.py CLIBehaviour.test_import_folder_preserves_tree_and_lists_without_live_merge CLIBehaviour.test_import_tyf_shaped_zip_is_detected_without_merging -v"
    Then Exit code is 0

  @covers:tyf-amanuensis-entry-contract @criterion:bad-outcome @criterion:edge @criterion:boundary @criterion:integration @bind-file:scripts/tyf.py @bind-file:tests/test_tyf.py @tool-check:cli
  Scenario: source fragments are reusable workspace memory
    When Run "python tests/test_tyf.py CLIBehaviour.test_source_fragments_are_workspace_owned_and_reusable_across_works -v"
    Then Exit code is 0

  @covers:tyf-amanuensis-entry-contract @criterion:bad-outcome @criterion:edge @criterion:boundary @criterion:integration @criterion:security @bind-file:scripts/tyf.py @bind-file:tests/test_tyf.py @bind-file:skills/controlling-manuscript-writes/SKILL.md @tool-check:cli
  Scenario: author direct manuscript edits can be adopted as the next base
    When Run "python tests/test_tyf.py CLIBehaviour.test_adopt_author_manuscript_edit_updates_base_for_next_decision -v"
    Then Exit code is 0

  @covers:tyf-amanuensis-entry-contract @criterion:bad-outcome @criterion:edge @criterion:integration @bind-file:scripts/tyf.py @bind-file:tests/test_tyf.py @tool-check:cli
  Scenario: resume reports active work continuity and next move
    When Run "python tests/test_tyf.py CLIBehaviour.test_resume_reports_active_work_state_and_next_useful_move -v"
    Then Exit code is 0

  @covers:tyf-today-mode-contract @bind-file:scripts/tyf.py @bind-file:tests/test_tyf.py @bind-file:tests/test_solo_oracles.py @tool-check:cli
  Scenario: today mode structural oracle remains wired
    When Run "python tests/test_solo_oracles.py today-mode"
    Then Exit code is 0

  @covers:tyf-today-mode-contract @bind-file:scripts/tyf.py @bind-file:tests/test_tyf.py @bind-file:tests/test_solo_oracles.py @tool-check:cli
  Scenario: today mode opens a titleless writing runway
    When Run "python tests/test_tyf.py CLIBehaviour.test_today_without_arrival_opens_titleless_writing_runway -v"
    Then Exit code is 0

  @covers:tyf-today-mode-contract @criterion:bad-outcome @criterion:edge @criterion:boundary @criterion:integration @bind-file:scripts/tyf.py @bind-file:tests/test_tyf.py @bind-file:skills/using-tyf/SKILL.md @tool-check:cli
  Scenario: today mode preserves a cold-start scaffold before drafting
    When Run "python tests/test_tyf.py CLIBehaviour.test_today_with_folder_arrival_preserves_scaffold_and_opens_runway -v"
    Then Exit code is 0

  @covers:tyf-today-mode-contract @criterion:bad-outcome @criterion:edge @criterion:boundary @criterion:integration @bind-file:scripts/tyf.py @bind-file:tests/test_tyf.py @tool-check:cli
  Scenario: today mode inherits titleless nonblocking start
    When Run "python tests/test_tyf.py CLIBehaviour.test_start_allows_no_title_and_keeps_intake_non_blocking -v"
    Then Exit code is 0

  @covers:tyf-today-mode-contract @criterion:bad-outcome @criterion:edge @criterion:boundary @criterion:integration @bind-file:scripts/tyf.py @bind-file:tests/test_tyf.py @tool-check:cli
  Scenario: today mode inherits containment for unorganized arrivals
    When Run "python tests/test_tyf.py CLIBehaviour.test_import_folder_preserves_tree_and_lists_without_live_merge CLIBehaviour.test_import_tyf_shaped_zip_is_detected_without_merging -v"
    Then Exit code is 0

  @covers:tyf-doc-drift-command-contract @bind-file:scripts/tyf.py @bind-file:tests/test_tyf.py @tool-check:cli
  Scenario: documentation check accepts the current repo pack
    When Run "python tests/test_tyf.py DocCheck.test_repo_pack_is_clean -v"
    Then Exit code is 0

  @covers:tyf-doc-drift-command-contract @criterion:bad-outcome @criterion:edge @criterion:boundary @criterion:integration @bind-file:scripts/tyf.py @bind-file:tests/test_tyf.py @tool-check:cli
  Scenario: documentation check flags retired manuscript confirmation command
    When Run "python tests/test_tyf.py DocCheck.test_check_flags_retired_write_confirm_command -v"
    Then Exit code is 0

  @covers:tyf-doc-drift-command-contract @criterion:bad-outcome @criterion:edge @criterion:boundary @criterion:integration @bind-file:scripts/tyf.py @bind-file:tests/test_tyf.py @tool-check:cli
  Scenario: documentation check flags stale ledger memory paths
    When Run "python tests/test_tyf.py DocCheck.test_check_flags_legacy_ledger_path -v"
    Then Exit code is 0

  @covers:tyf-doc-drift-command-contract @criterion:bad-outcome @criterion:edge @criterion:boundary @criterion:integration @bind-file:scripts/tyf.py @bind-file:tests/test_tyf.py @tool-check:cli
  Scenario: documentation check flags stale role terminology
    When Run "python tests/test_tyf.py DocCheck.test_check_flags_role_terminology_drift -v"
    Then Exit code is 0

  @covers:tyf-portable-workspace-contract @criterion:bad-outcome @criterion:edge @criterion:boundary @criterion:integration @bind-file:scripts/tyf.py @bind-file:tests/test_tyf.py @bind-file:tests/test_solo_oracles.py @bind-file:docs/PORTABILITY.md @bind-file:docs/WORKSPACE_CONTRACT.md @tool-check:cli
  Scenario: workspace initializes a portable text-first bundle marker
    When Run "python tests/test_tyf.py CLIBehaviour.test_init_creates_portable_workspace_marker -v"
    Then Exit code is 0

  @covers:tyf-portable-workspace-contract @bind-file:scripts/tyf.py @bind-file:tests/test_solo_oracles.py @bind-file:docs/PORTABILITY.md @bind-file:docs/WORKSPACE_CONTRACT.md @tool-check:cli
  Scenario: portable workspace structural oracle remains wired
    When Run "python tests/test_solo_oracles.py portability"
    Then Exit code is 0

  @covers:tyf-helper-current-contract @criterion:bad-outcome @criterion:edge @criterion:boundary @criterion:integration @criterion:security @bind-file:scripts/tyf.py @bind-file:tests/test_tyf.py @bind-file:tests/test_solo_oracles.py @tool-check:cli
  Scenario: helper refuses tampered Gate review records
    When Run "python tests/test_tyf.py CLIBehaviour.test_write_refuses_tampered_decision_record CLIBehaviour.test_write_refuses_tampered_audit_record CLIBehaviour.test_doctor_flags_tampered_gate_record CLIBehaviour.test_doctor_flags_missing_gate_record_seal -v"
    Then Exit code is 0

  @covers:tyf-helper-current-contract @criterion:bad-outcome @criterion:edge @criterion:boundary @criterion:integration @criterion:security @bind-file:scripts/tyf.py @bind-file:tests/test_tyf.py @bind-file:tests/test_solo_oracles.py @tool-check:cli
  Scenario: helper locks manuscript units during controlled writes
    When Run "python tests/test_tyf.py CLIBehaviour.test_write_refuses_existing_manuscript_unit_lock CLIBehaviour.test_doctor_flags_manuscript_unit_lock -v"
    Then Exit code is 0

  @covers:tyf-helper-current-contract @criterion:bad-outcome @criterion:edge @criterion:boundary @criterion:integration @criterion:security @bind-file:scripts/tyf.py @bind-file:tests/test_tyf.py @bind-file:tests/test_solo_oracles.py @tool-check:cli
  Scenario: helper applies only accepted source line ranges
    When Run "python tests/test_tyf.py CLIBehaviour.test_accept_line_ranges_writes_only_selected_lines CLIBehaviour.test_accept_line_ranges_refuses_invalid_or_out_of_range_selection -v"
    Then Exit code is 0

  @covers:tyf-patch-acceptance-contract @bind-file:scripts/tyf.py @bind-file:tests/test_tyf.py @bind-file:tests/test_solo_oracles.py @tool-check:cli
  Scenario: helper applies an exact accepted patch
    When Run "python tests/test_tyf.py CLIBehaviour.test_accept_patch_applies_exact_unified_diff_to_manuscript_base -v"
    Then Exit code is 0

  @covers:tyf-patch-acceptance-contract @criterion:bad-outcome @criterion:edge @criterion:boundary @criterion:integration @criterion:security @bind-file:scripts/tyf.py @bind-file:tests/test_tyf.py @bind-file:tests/test_solo_oracles.py @tool-check:cli
  Scenario: helper refuses mixed line and patch acceptance
    When Run "python tests/test_tyf.py CLIBehaviour.test_accept_patch_refuses_mixed_line_scope -v"
    Then Exit code is 0

  @covers:tyf-patch-acceptance-contract @criterion:bad-outcome @criterion:edge @criterion:boundary @criterion:integration @criterion:security @bind-file:scripts/tyf.py @bind-file:tests/test_tyf.py @bind-file:tests/test_solo_oracles.py @tool-check:cli
  Scenario: helper refuses malformed accepted patch hunk counts
    When Run "python tests/test_tyf.py CLIBehaviour.test_accept_patch_refuses_hunk_count_mismatch -v"
    Then Exit code is 0

  @covers:tyf-patch-acceptance-contract @criterion:bad-outcome @criterion:edge @criterion:boundary @criterion:integration @criterion:security @bind-file:scripts/tyf.py @bind-file:tests/test_tyf.py @bind-file:tests/test_solo_oracles.py @tool-check:cli
  Scenario: helper refuses accepted patch tampering at write time
    When Run "python tests/test_tyf.py CLIBehaviour.test_write_refuses_tampered_accepted_patch_file -v"
    Then Exit code is 0

  @covers:tyf-patch-acceptance-contract @criterion:bad-outcome @criterion:edge @criterion:boundary @criterion:integration @criterion:security @bind-file:scripts/tyf.py @bind-file:tests/test_tyf.py @bind-file:tests/test_solo_oracles.py @tool-check:cli
  Scenario: helper doctor reports missing accepted patch files
    When Run "python tests/test_tyf.py CLIBehaviour.test_doctor_flags_missing_accepted_patch_file -v"
    Then Exit code is 0

  @covers:tyf-helper-current-contract @criterion:bad-outcome @criterion:edge @criterion:boundary @criterion:integration @criterion:security @bind-file:scripts/tyf.py @bind-file:tests/test_tyf.py @tool-check:cli
  Scenario: helper refuses unsafe or out-of-workspace writes
    When Run "python tests/test_tyf.py CLIBehaviour.test_write_refuses_without_decision CLIBehaviour.test_new_work_refuses_symlinked_works_root_escape CLIBehaviour.test_propose_refuses_symlinked_manuscript_escape CLIBehaviour.test_snapshot_scopes_commit_to_workspace_inside_parent_repo -v"
    Then Exit code is 0

  @covers:tyf-helper-current-contract @criterion:bad-outcome @criterion:edge @criterion:boundary @criterion:integration @bind-file:scripts/tyf.py @bind-file:tests/test_tyf.py @tool-check:cli
  Scenario: helper keeps first-day setup source-first and recoverable
    When Run "python tests/test_tyf.py CLIBehaviour.test_start_is_plain_language_front_door_for_new_book CLIBehaviour.test_capture_records_author_source_without_touching_manuscript CLIBehaviour.test_snapshot_commits_workspace_changes_when_git_repo -v"
    Then Exit code is 0

  @covers:tyf-helper-current-contract @criterion:bad-outcome @criterion:edge @criterion:boundary @criterion:integration @bind-file:scripts/tyf.py @bind-file:tests/test_tyf.py @bind-file:tests/test_solo_oracles.py @tool-check:cli
  Scenario: helper records explicit writing language for multilingual works
    When Run "python tests/test_tyf.py CLIBehaviour.test_start_accepts_non_latin_title_with_stable_generated_id CLIBehaviour.test_start_records_explicit_writing_language CLIBehaviour.test_gate_preserves_utf8_manuscript_text_for_declared_language CLIBehaviour.test_user_yaml_values_are_safely_quoted -v"
    Then Exit code is 0

  @covers:tyf-canonical-event-journal-contract @bind-file:scripts/tyf.py @bind-file:tests/test_tyf.py @bind-file:tests/test_solo_oracles.py @tool-check:cli
  Scenario: helper records a canonical hash-chained event journal
    When Run "python tests/test_tyf.py CLIBehaviour.test_canonical_event_journal_records_core_actions_with_hash_chain -v"
    Then Exit code is 0

  @covers:tyf-canonical-event-journal-contract @criterion:bad-outcome @criterion:edge @criterion:boundary @criterion:integration @criterion:security @bind-file:scripts/tyf.py @bind-file:tests/test_tyf.py @bind-file:tests/test_solo_oracles.py @tool-check:cli
  Scenario: doctor detects a rewritten event by hash-chain mismatch
    When Run "python tests/test_tyf.py CLIBehaviour.test_doctor_flags_tampered_canonical_event_journal -v"
    Then Exit code is 0

  @covers:tyf-canonical-event-journal-contract @criterion:bad-outcome @criterion:edge @criterion:boundary @criterion:integration @criterion:security @bind-file:scripts/tyf.py @bind-file:tests/test_tyf.py @bind-file:tests/test_solo_oracles.py @tool-check:cli
  Scenario: doctor detects a deleted event journal before trusting history
    When Run "python tests/test_tyf.py CLIBehaviour.test_doctor_flags_missing_canonical_event_journal -v"
    Then Exit code is 0

  @covers:tyf-canonical-event-journal-contract @criterion:bad-outcome @criterion:edge @criterion:boundary @criterion:integration @criterion:security @bind-file:scripts/tyf.py @bind-file:tests/test_tyf.py @bind-file:tests/test_solo_oracles.py @tool-check:cli
  Scenario: doctor detects an invalid JSON line in the event journal
    When Run "python tests/test_tyf.py CLIBehaviour.test_doctor_flags_malformed_canonical_event_journal -v"
    Then Exit code is 0

  @covers:tyf-canonical-event-journal-contract @criterion:bad-outcome @criterion:edge @criterion:boundary @criterion:integration @criterion:security @bind-file:scripts/tyf.py @bind-file:tests/test_tyf.py @bind-file:tests/test_solo_oracles.py @tool-check:cli
  Scenario: mutation refuses to recreate a lost event history
    When Run "python tests/test_tyf.py CLIBehaviour.test_mutating_command_refuses_missing_canonical_event_journal -v"
    Then Exit code is 0

  @covers:tyf-source-provenance-contract @bind-file:scripts/tyf.py @bind-file:tests/test_tyf.py @bind-file:skills/ingesting-sources/SKILL.md @bind-file:skills/controlling-manuscript-writes/SKILL.md @tool-check:cli
  Scenario: source fragments carry through proposal decision and write records
    When Run "python tests/test_tyf.py CLIBehaviour.test_source_capture_fragment_survives_proposal_decision_and_write -v"
    Then Exit code is 0

  @covers:tyf-source-provenance-contract @criterion:bad-outcome @criterion:edge @criterion:boundary @criterion:integration @criterion:security @bind-file:scripts/tyf.py @bind-file:tests/test_tyf.py @tool-check:cli
  Scenario: source provenance refuses missing or file-tampered fragments
    When Run "python tests/test_tyf.py CLIBehaviour.test_propose_refuses_missing_or_tampered_source_fragment -v"
    Then Exit code is 0

  @covers:tyf-source-provenance-contract @criterion:bad-outcome @criterion:edge @criterion:boundary @criterion:integration @criterion:security @bind-file:scripts/tyf.py @bind-file:tests/test_tyf.py @tool-check:cli
  Scenario: source provenance refuses index and fragment rewrites under an old id
    When Run "python tests/test_tyf.py CLIBehaviour.test_propose_refuses_fragment_file_and_index_rewritten_under_same_id -v"
    Then Exit code is 0

  @covers:tyf-source-provenance-contract @criterion:bad-outcome @criterion:edge @criterion:boundary @criterion:integration @criterion:security @bind-file:scripts/tyf.py @bind-file:tests/test_tyf.py @bind-file:tests/test_solo_oracles.py @tool-check:cli
  Scenario: accepted source provenance remains enforced by write and doctor
    When Run "python tests/test_tyf.py CLIBehaviour.test_write_and_doctor_refuse_tampered_source_fragment_after_decision -v"
    Then Exit code is 0

  @covers:tyf-source-provenance-contract @bind-file:scripts/tyf.py @bind-file:tests/test_solo_oracles.py @tool-check:cli
  Scenario: source provenance structural oracle remains wired
    When Run "python tests/test_solo_oracles.py provenance"
    Then Exit code is 0

  @covers:tyf-public-onboarding-contract @bind-file:README.md @bind-file:docs/START_HERE.md @bind-file:skills/using-tyf/SKILL.md @bind-file:skills/initializing-a-workspace/SKILL.md @bind-file:cowork/SETUP.md @bind-file:tests/test_solo_oracles.py @tool-check:cli
  Scenario: public onboarding has paste-ready author prompts
    When Run "python tests/test_solo_oracles.py onboarding"
    Then Exit code is 0

  @covers:tyf-public-onboarding-contract @bind-file:README.md @bind-file:docs/START_HERE.md @bind-file:tests/test_solo_oracles.py @tool-check:cli
  Scenario: public onboarding entrypoint is visible from the README
    When Run "python tests/test_solo_oracles.py onboarding-entry"
    Then Exit code is 0

  @covers:tyf-public-onboarding-contract @criterion:bad-outcome @criterion:edge @criterion:boundary @criterion:integration @bind-file:README.md @bind-file:docs/START_HERE.md @bind-file:skills/using-tyf/SKILL.md @bind-file:skills/initializing-a-workspace/SKILL.md @bind-file:cowork/SETUP.md @bind-file:tests/test_solo_oracles.py @tool-check:cli
  Scenario: public onboarding does not make the author operate the CLI first
    When Run "python tests/test_solo_oracles.py onboarding"
    Then Exit code is 0

  @covers:tyf-public-onboarding-contract @criterion:bad-outcome @criterion:edge @criterion:boundary @criterion:integration @bind-file:README.md @bind-file:docs/START_HERE.md @bind-file:skills/using-tyf/SKILL.md @bind-file:skills/initializing-a-workspace/SKILL.md @bind-file:cowork/SETUP.md @bind-file:tests/test_solo_oracles.py @tool-check:cli
  Scenario: public onboarding stays linked into the active skills
    When Run "python tests/test_solo_oracles.py onboarding"
    Then Exit code is 0

  @covers:tyf-codex-plugin-valid @bind-file:.codex-plugin/plugin.json @bind-file:skills/ @tool-check:cli
  Scenario: Codex plugin happy path validates
    When Run "python C:/Users/maste/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py ."
    Then Exit code is 0

  @covers:tyf-codex-plugin-valid @bind-file:.codex-plugin/plugin.json @bind-file:skills/ @bind-file:tests/test_solo_oracles.py @tool-check:cli
  Scenario: Codex plugin manifest has independent structural shape
    When Run "python tests/test_solo_oracles.py plugin"
    Then Exit code is 0

  @covers:tyf-codex-plugin-valid @criterion:bad-outcome @criterion:edge @criterion:boundary @criterion:integration @bind-file:.codex-plugin/plugin.json @bind-file:skills/ @tool-check:cli
  Scenario: Codex plugin catches invalid manifest or skill metadata
    When Run "python C:/Users/maste/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py ."
    Then Exit code is 0

  @covers:tyf-codex-plugin-valid @criterion:bad-outcome @criterion:edge @criterion:boundary @criterion:integration @bind-file:.codex-plugin/plugin.json @bind-file:skills/ @tool-check:cli
  Scenario: Codex plugin remains installable as a writing apparatus
    When Run "python C:/Users/maste/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py ."
    Then Exit code is 0

  @covers:tyf-codex-skill-book-repo @bind-file:.codex-plugin/plugin.json @bind-file:skills/using-tyf/SKILL.md @bind-file:skills/using-tyf/agents/openai.yaml @bind-file:scripts/install.sh @bind-file:AGENTS.md @bind-file:CLAUDE.md @bind-file:GEMINI.md @bind-file:docs/PORTABILITY.md @bind-file:tests/test_solo_oracles.py @tool-check:cli
  Scenario: Codex skill surface routes book repos through Today Mode
    When Run "python tests/test_solo_oracles.py codex-skill"
    Then Exit code is 0

  @covers:tyf-codex-skill-book-repo @criterion:bad-outcome @criterion:edge @criterion:boundary @criterion:integration @bind-file:scripts/tyf.py @bind-file:scripts/install.sh @bind-file:tests/test_tyf.py @tool-check:cli
  Scenario: Codex skill doc honesty catches stale install and title routing
    When Run "python tests/test_tyf.py DocCheck.test_check_flags_title_gated_today_mode_drift Installer.test_codex_install_targets_current_skill_root -v"
    Then Exit code is 0

  @covers:tyf-codex-skill-book-repo @criterion:bad-outcome @criterion:edge @criterion:boundary @criterion:integration @bind-file:skills/using-tyf/SKILL.md @bind-file:skills/using-tyf/agents/openai.yaml @tool-check:cli
  Scenario: Codex dispatcher skill validates as a skill
    When Run "python C:/Users/maste/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/using-tyf"
    Then Exit code is 0

  @covers:tyf-codex-skill-book-repo @criterion:bad-outcome @criterion:edge @criterion:boundary @criterion:integration @bind-file:scripts/tyf.py @bind-file:AGENTS.md @bind-file:CLAUDE.md @bind-file:GEMINI.md @bind-file:tests/test_tyf.py @tool-check:cli
  Scenario: Codex book-repo contexts stay Today Mode aligned
    When Run "python tests/test_tyf.py CLIBehaviour.test_init_creates_workspace_context_contracts DocCheck.test_repo_pack_is_clean -v"
    Then Exit code is 0
