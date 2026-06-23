Feature: TYF helper smoke suite

  @covers:tyf-helper-current-contract @bind-file:scripts/tyf.py @bind-file:tests/test_tyf.py @tool-check:cli
  Scenario: helper happy path supports first writing session
    When Run "python tests/test_tyf.py CLIBehaviour.test_start_without_arrival_opens_titleless_writing_runway CLIBehaviour.test_write_with_decision_copies_and_logs -v"
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

  @covers:tyf-work-state-machine-contract @covers:tyf-amanuensis-entry-contract @criterion:bad-outcome @criterion:edge @criterion:integration @bind-file:scripts/tyf.py @bind-file:tests/test_tyf.py @tool-check:cli
  Scenario: status reports the active work state from work yaml
    When Run "python tests/test_tyf.py CLIBehaviour.test_status_reports_active_work_status_from_work_yaml -v"
    Then Exit code is 0

  @covers:tyf-helper-current-contract @criterion:bad-outcome @criterion:edge @criterion:boundary @criterion:integration @bind-file:scripts/tyf.py @bind-file:tests/test_tyf.py @tool-check:cli
  Scenario: audit record writes an inspectable editorial note
    When Run "python tests/test_tyf.py CLIBehaviour.test_audit_record_writes_inspectable_editorial_note -v"
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

  @covers:tyf-amanuensis-entry-contract @covers:tyf-writing-runway-contract @bind-file:scripts/tyf.py @bind-file:tests/test_tyf.py @bind-file:skills/interviewing-the-author/SKILL.md @tool-check:cli
  Scenario: first-session packet offers a gentle attention deck
    When Run "python tests/test_tyf.py CLIBehaviour.test_start_first_session_packet_has_gentle_attention_deck -v"
    Then Exit code is 0

  @covers:tyf-amanuensis-entry-contract @criterion:bad-outcome @criterion:edge @criterion:boundary @criterion:integration @criterion:security @bind-file:scripts/tyf.py @bind-file:tests/test_tyf.py @bind-file:skills/ingesting-sources/SKILL.md @tool-check:cli
  Scenario: import preserves chat and bundle arrivals without manuscript writes
    When Run "python tests/test_tyf.py CLIBehaviour.test_import_chat_preserves_raw_input_creates_titleless_work_and_fragment CLIBehaviour.test_import_zip_preserves_bundle_without_manuscript_write -v"
    Then Exit code is 0

  @covers:tyf-amanuensis-entry-contract @criterion:bad-outcome @criterion:edge @criterion:boundary @criterion:integration @criterion:security @bind-file:scripts/tyf.py @bind-file:tests/test_tyf.py @bind-file:README.md @bind-file:docs/WORKSPACE_CONTRACT.md @bind-file:docs/START_HERE.md @bind-file:skills/ingesting-sources/SKILL.md @tool-check:cli
  Scenario: unreadable and huge arrivals are preserved with extraction-needed guidance
    When Run "python tests/test_tyf.py CLIBehaviour.test_import_unreadable_binary_marks_extraction_needed_without_fragment CLIBehaviour.test_import_large_text_marks_chunking_needed_without_implying_read DocCheck.test_import_docs_describe_unreadable_arrival_extraction_boundary -v"
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

  @covers:tyf-writing-runway-contract @bind-file:scripts/tyf.py @bind-file:tests/test_tyf.py @bind-file:tests/test_solo_oracles.py @tool-check:cli
  Scenario: writing runway structural oracle remains wired
    When Run "python tests/test_solo_oracles.py writing-runway"
    Then Exit code is 0

  @covers:tyf-writing-runway-contract @bind-file:scripts/tyf.py @bind-file:tests/test_tyf.py @bind-file:tests/test_solo_oracles.py @tool-check:cli
  Scenario: start opens a titleless writing runway
    When Run "python tests/test_tyf.py CLIBehaviour.test_start_without_arrival_opens_titleless_writing_runway -v"
    Then Exit code is 0

  @covers:tyf-writing-runway-contract @covers:tyf-amanuensis-entry-contract @criterion:bad-outcome @criterion:edge @criterion:integration @bind-file:scripts/tyf.py @bind-file:tests/test_tyf.py @tool-check:cli
  Scenario: start reruns preserve author runway notes
    When Run "python tests/test_tyf.py CLIBehaviour.test_start_rerun_preserves_existing_writing_runway_notes -v"
    Then Exit code is 0

  @covers:tyf-writing-runway-contract @covers:tyf-amanuensis-entry-contract @criterion:bad-outcome @criterion:edge @criterion:boundary @criterion:integration @bind-file:scripts/tyf.py @bind-file:tests/test_tyf.py @tool-check:cli
  Scenario: start preserves title language and first-session evidence
    When Run "python tests/test_tyf.py CLIBehaviour.test_start_updates_root_title_language_and_evidence_packet -v"
    Then Exit code is 0

  @covers:tyf-writing-runway-contract @criterion:bad-outcome @criterion:edge @criterion:boundary @criterion:integration @bind-file:scripts/tyf.py @bind-file:tests/test_tyf.py @bind-file:skills/using-tyf/SKILL.md @tool-check:cli
  Scenario: start preserves a cold-start scaffold before drafting
    When Run "python tests/test_tyf.py CLIBehaviour.test_start_with_folder_arrival_preserves_scaffold_and_opens_runway -v"
    Then Exit code is 0

  @covers:tyf-writing-runway-contract @criterion:bad-outcome @criterion:edge @criterion:boundary @criterion:integration @bind-file:scripts/tyf.py @bind-file:tests/test_tyf.py @tool-check:cli
  Scenario: writing runway inherits titleless nonblocking start
    When Run "python tests/test_tyf.py CLIBehaviour.test_start_allows_no_title_and_keeps_intake_non_blocking -v"
    Then Exit code is 0

  @covers:tyf-writing-runway-contract @criterion:bad-outcome @criterion:edge @criterion:boundary @criterion:integration @bind-file:scripts/tyf.py @bind-file:tests/test_tyf.py @tool-check:cli
  Scenario: writing runway inherits containment for unorganized arrivals
    When Run "python tests/test_tyf.py CLIBehaviour.test_import_folder_preserves_tree_and_lists_without_live_merge CLIBehaviour.test_import_tyf_shaped_zip_is_detected_without_merging -v"
    Then Exit code is 0

  @covers:tyf-single-work-beta-contract @bind-file:scripts/tyf.py @bind-file:tests/test_tyf.py @tool-check:cli
  Scenario: beta book folder is the single work
    When Run "python tests/test_tyf.py CLIBehaviour.test_init_creates_single_work_root_layout CLIBehaviour.test_init_without_name_scaffolds_current_book_folder CLIBehaviour.test_start_without_arrival_opens_titleless_writing_runway -v"
    Then Exit code is 0

  @covers:tyf-single-work-beta-contract @criterion:bad-outcome @criterion:edge @criterion:boundary @criterion:integration @bind-file:scripts/tyf.py @bind-file:tests/test_tyf.py @tool-check:cli
  Scenario: beta workspace init does not create a public works catalog
    When Run "python tests/test_tyf.py CLIBehaviour.test_init_creates_single_work_root_layout CLIBehaviour.test_init_creates_workspace_context_contracts -v"
    Then Exit code is 0

  @covers:tyf-single-work-beta-contract @criterion:bad-outcome @criterion:edge @criterion:boundary @criterion:integration @bind-file:scripts/tyf.py @bind-file:tests/test_tyf.py @tool-check:cli
  Scenario: beta start keeps cold-start arrivals in the root book folder
    When Run "python tests/test_tyf.py CLIBehaviour.test_beta_start_arrival_uses_root_book_folder CLIBehaviour.test_import_chat_preserves_raw_input_creates_titleless_work_and_fragment -v"
    Then Exit code is 0

  @covers:tyf-single-work-beta-contract @criterion:bad-outcome @criterion:edge @criterion:boundary @criterion:integration @bind-file:scripts/tyf.py @bind-file:tests/test_tyf.py @tool-check:cli
  Scenario: beta portability marker declares a single-work bundle
    When Run "python tests/test_tyf.py CLIBehaviour.test_beta_portable_marker_declares_single_work_bundle -v"
    Then Exit code is 0

  @covers:tyf-single-work-beta-contract @criterion:bad-outcome @criterion:edge @criterion:boundary @criterion:integration @bind-file:README.md @bind-file:docs/WORKSPACE_CONTRACT.md @bind-file:docs/PORTABILITY.md @bind-file:skills/using-tyf/SKILL.md @bind-file:skills/initializing-a-workspace/SKILL.md @bind-file:skills/working-the-workspace/SKILL.md @bind-file:cowork/PROJECT_INSTRUCTIONS.md @bind-file:cowork/SCHEDULED_TASKS.md @bind-file:TYF-manifesto-and-architecture.md @bind-file:tests/test_solo_oracles.py @tool-check:cli
  Scenario: beta public docs do not teach multi-work startup
    When Run "python tests/test_solo_oracles.py single-work"
    Then Exit code is 0

  @covers:tyf-single-work-beta-contract @covers:tyf-public-onboarding-contract @criterion:bad-outcome @criterion:edge @criterion:boundary @criterion:integration @bind-file:README.md @bind-file:docs/WORKSPACE_CONTRACT.md @bind-file:skills/initializing-a-workspace/SKILL.md @bind-file:skills/working-the-workspace/SKILL.md @bind-file:tests/test_tyf.py @tool-check:cli
  Scenario: today command is removed and start is the public beta front door
    When Run "python tests/test_tyf.py CLIBehaviour.test_start_positional_title_is_not_a_compatibility_alias CLIBehaviour.test_today_command_is_removed -v"
    Then Exit code is 0

  @covers:tyf-start-title-footgun-contract @covers:tyf-writing-runway-contract @criterion:bad-outcome @criterion:edge @criterion:boundary @criterion:integration @bind-file:scripts/tyf.py @bind-file:tests/test_tyf.py @tool-check:cli
  Scenario: start positional title mistake stays strict but points to title flag
    When Run "python tests/test_tyf.py CLIBehaviour.test_start_positional_title_is_not_a_compatibility_alias CLIBehaviour.test_start_positional_title_error_points_to_title_flag -v"
    Then Exit code is 0

  @covers:tyf-start-title-footgun-contract @bind-file:scripts/tyf.py @bind-file:tests/test_tyf.py @tool-check:cli
  Scenario: explicit title flag remains the title happy path
    When Run "python tests/test_tyf.py CLIBehaviour.test_start_records_non_latin_title_without_id_gate CLIBehaviour.test_start_records_explicit_writing_language -v"
    Then Exit code is 0

  @covers:tyf-start-title-footgun-contract @criterion:bad-outcome @criterion:edge @criterion:boundary @criterion:integration @bind-file:scripts/tyf.py @bind-file:tests/test_tyf.py @tool-check:cli
  Scenario: positional start title does not create a hidden work alias
    When Run "python tests/test_tyf.py CLIBehaviour.test_start_positional_title_is_not_a_compatibility_alias -v"
    Then Exit code is 0

  @covers:tyf-start-title-footgun-contract @criterion:bad-outcome @criterion:edge @criterion:boundary @criterion:integration @bind-file:scripts/tyf.py @bind-file:tests/test_tyf.py @tool-check:cli
  Scenario: positional start title error names the title flag recovery
    When Run "python tests/test_tyf.py CLIBehaviour.test_start_positional_title_error_points_to_title_flag -v"
    Then Exit code is 0

  @covers:tyf-start-title-footgun-contract @criterion:bad-outcome @criterion:edge @criterion:boundary @criterion:integration @bind-file:scripts/tyf.py @bind-file:tests/test_tyf.py @tool-check:cli
  Scenario: start keeps no legacy today fallback while guiding title recovery
    When Run "python tests/test_tyf.py CLIBehaviour.test_start_positional_title_error_points_to_title_flag CLIBehaviour.test_today_command_is_removed -v"
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

  @covers:tyf-doc-drift-command-contract @criterion:bad-outcome @criterion:edge @criterion:boundary @criterion:integration @bind-file:scripts/tyf.py @bind-file:tests/test_tyf.py @tool-check:cli
  Scenario: documentation check flags plugin manifest version divergence
    When Run "python tests/test_tyf.py DocCheck.test_check_flags_plugin_manifest_version_divergence -v"
    Then Exit code is 0

  @covers:tyf-doc-drift-command-contract @criterion:bad-outcome @criterion:edge @criterion:boundary @criterion:integration @bind-file:scripts/tyf.py @bind-file:cowork/PROJECT_INSTRUCTIONS.md @bind-file:cowork/SCHEDULED_TASKS.md @bind-file:TYF-manifesto-and-architecture.md @bind-file:tests/test_tyf.py @tool-check:cli
  Scenario: documentation check flags stale single-work path drift
    When Run "python tests/test_tyf.py DocCheck.test_check_flags_stale_single_work_path_drift DocCheck.test_check_flags_stale_multi_work_globs DocCheck.test_check_flags_today_inside_command_lists -v"
    Then Exit code is 0

  @covers:tyf-doc-drift-command-contract @criterion:bad-outcome @criterion:edge @criterion:boundary @criterion:integration @bind-file:scripts/tyf.py @bind-file:cowork/SETUP.md @bind-file:TYF-manifesto-and-architecture.md @bind-file:tests/test_tyf.py @tool-check:cli
  Scenario: documentation check flags stale Gate chains without review packets
    When Run "python tests/test_tyf.py DocCheck.test_check_flags_controlled_write_chain_without_review_packet -v"
    Then Exit code is 0

  @covers:tyf-doc-drift-command-contract @criterion:bad-outcome @criterion:edge @criterion:boundary @criterion:integration @bind-file:README.md @bind-file:VALIDATION.md @bind-file:CHANGELOG.md @bind-file:docs/COMPARISON_SUPERPOWERS.md @bind-file:tests/PRESSURE_RESULTS.md @bind-file:tests/test_tyf.py @tool-check:cli
  Scenario: README pressure status matches validation evidence
    When Run "python tests/test_tyf.py DocCheck.test_readme_pressure_status_matches_validation_evidence DocCheck.test_release_status_counts_match_current_evidence -v"
    Then Exit code is 0

  @covers:tyf-release-packaging-contract @criterion:bad-outcome @criterion:edge @criterion:boundary @criterion:integration @bind-file:author-context/AGENTS.md @bind-file:author-context/CLAUDE.md @bind-file:author-context/GEMINI.md @bind-file:scripts/install.sh @bind-file:docs/PORTABILITY.md @bind-file:tests/test_tyf.py @tool-check:cli
  Scenario: author context templates stay clean and install docs avoid dev context
    When Run "python tests/test_tyf.py DocCheck.test_author_context_templates_do_not_include_solo_development_reflex DocCheck.test_install_docs_route_author_workspaces_away_from_dev_context -v"
    Then Exit code is 0

  @covers:tyf-release-packaging-contract @bind-file:author-context/AGENTS.md @bind-file:author-context/CLAUDE.md @bind-file:author-context/GEMINI.md @bind-file:scripts/install.sh @bind-file:docs/PORTABILITY.md @bind-file:tests/test_tyf.py @tool-check:cli
  Scenario: release packaging has clean author context happy path
    When Run "python tests/test_tyf.py DocCheck.test_author_context_templates_do_not_include_solo_development_reflex DocCheck.test_install_docs_route_author_workspaces_away_from_dev_context -v"
    Then Exit code is 0

  @covers:tyf-release-packaging-contract @criterion:bad-outcome @criterion:edge @criterion:boundary @criterion:integration @bind-file:author-context/AGENTS.md @bind-file:author-context/CLAUDE.md @bind-file:author-context/GEMINI.md @bind-file:tests/test_tyf.py @tool-check:cli
  Scenario: author context templates contain no development reflex
    When Run "python tests/test_tyf.py DocCheck.test_author_context_templates_do_not_include_solo_development_reflex -v"
    Then Exit code is 0

  @covers:tyf-release-packaging-contract @criterion:bad-outcome @criterion:edge @criterion:boundary @criterion:integration @bind-file:scripts/install.sh @bind-file:docs/PORTABILITY.md @bind-file:tests/test_tyf.py @tool-check:cli
  Scenario: install and portability docs route book workspaces to generated context
    When Run "python tests/test_tyf.py DocCheck.test_install_docs_route_author_workspaces_away_from_dev_context -v"
    Then Exit code is 0

  @covers:tyf-release-packaging-contract @criterion:bad-outcome @criterion:edge @criterion:boundary @criterion:integration @bind-file:.gitattributes @bind-file:tests/test_tyf.py @tool-check:cli
  Scenario: release export ignores workshop debris
    When Run "python tests/test_tyf.py DocCheck.test_release_archive_excludes_workshop_debris DocCheck.test_release_archive_keeps_author_context_templates -v"
    Then Exit code is 0

  @covers:tyf-release-packaging-contract @covers:tyf-public-onboarding-contract @criterion:bad-outcome @criterion:edge @criterion:boundary @criterion:integration @bind-file:.opencode/INSTALL.md @bind-file:tests/test_tyf.py @tool-check:cli
  Scenario: OpenCode install routes through helper and clean author context
    When Run "python tests/test_tyf.py DocCheck.test_opencode_install_routes_to_helper_and_author_context -v"
    Then Exit code is 0

  @covers:tyf-windows-installer-contract @bind-file:scripts/install.ps1 @bind-file:tests/test_tyf.py @tool-check:cli
  Scenario: Windows installer installs Codex skills and helper launchers
    When Run "python tests/test_tyf.py Installer.test_powershell_installer_installs_codex_skills_and_helper -v"
    Then Exit code is 0

  @covers:tyf-windows-installer-contract @criterion:bad-outcome @criterion:edge @criterion:boundary @criterion:integration @bind-file:scripts/install.ps1 @bind-file:tests/test_tyf.py @tool-check:cli
  Scenario: Windows installer targets current Codex skill roots
    When Run "python tests/test_tyf.py Installer.test_codex_install_targets_current_skill_root -v"
    Then Exit code is 0

  @covers:tyf-windows-installer-contract @criterion:bad-outcome @criterion:edge @criterion:boundary @criterion:integration @bind-file:scripts/install.ps1 @bind-file:tests/test_tyf.py @tool-check:cli
  Scenario: Windows installer preserves pack-root launchers
    When Run "python tests/test_tyf.py Installer.test_powershell_installer_writes_pack_root_launchers -v"
    Then Exit code is 0

  @covers:tyf-windows-installer-contract @criterion:bad-outcome @criterion:edge @criterion:boundary @criterion:integration @bind-file:scripts/install.ps1 @bind-file:tests/test_tyf.py @bind-file:README.md @bind-file:docs/PORTABILITY.md @bind-file:docs/START_HERE.md @tool-check:cli
  Scenario: Windows installer docs expose no-bash path
    When Run "python tests/test_tyf.py Installer.test_powershell_installer_has_windows_author_contract DocCheck.test_install_docs_route_author_workspaces_away_from_dev_context -v"
    Then Exit code is 0

  @covers:tyf-helper-current-contract @covers:tyf-doc-drift-command-contract @criterion:edge @criterion:integration @bind-file:scripts/tyf.py @bind-file:tests/test_tyf.py @tool-check:cli
  Scenario: advertised strict check flag is accepted
    When Run "python tests/test_tyf.py DocCheck.test_check_accepts_advertised_strict_flag -v"
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

  @covers:tyf-helper-current-contract @criterion:bad-outcome @criterion:edge @criterion:boundary @criterion:integration @bind-file:scripts/tyf.py @bind-file:tests/test_tyf.py @bind-file:README.md @bind-file:skills/controlling-manuscript-writes/SKILL.md @tool-check:cli
  Scenario: author acceptance requires an author review packet
    When Run "python tests/test_tyf.py CLIBehaviour.test_accept_requires_author_review_packet CLIBehaviour.test_write_and_doctor_refuse_tampered_author_review_packet -v"
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
    When Run "python tests/test_tyf.py CLIBehaviour.test_start_positional_title_is_not_a_compatibility_alias CLIBehaviour.test_today_command_is_removed CLIBehaviour.test_capture_records_author_source_without_touching_manuscript CLIBehaviour.test_snapshot_commits_workspace_changes_when_git_repo -v"
    Then Exit code is 0

  @covers:tyf-attentive-notice-quality-contract @criterion:bad-outcome @criterion:edge @criterion:boundary @criterion:integration @bind-file:scripts/tyf.py @bind-file:docs/ATTENTIVENESS.md @bind-file:tests/test_tyf.py @tool-check:cli
  Scenario: clean controlled write does not create style-sheet lag noise
    When Run "python tests/test_tyf.py CLIBehaviour.test_notice_does_not_report_style_lag_after_clean_controlled_write -v"
    Then Exit code is 0

  @covers:tyf-attentive-notice-quality-contract @bind-file:scripts/tyf.py @bind-file:docs/ATTENTIVENESS.md @bind-file:tests/test_tyf.py @tool-check:cli
  Scenario: attentive notices distinguish clean controlled writes from style problems
    When Run "python tests/test_tyf.py CLIBehaviour.test_notice_does_not_report_style_lag_after_clean_controlled_write CLIBehaviour.test_notice_reports_style_lag_for_unlogged_manuscript_change -v"
    Then Exit code is 0

  @covers:tyf-attentive-notice-quality-contract @criterion:bad-outcome @criterion:edge @criterion:boundary @criterion:integration @bind-file:scripts/tyf.py @bind-file:docs/ATTENTIVENESS.md @bind-file:tests/test_tyf.py @tool-check:cli
  Scenario: unlogged manuscript changes still surface style-sheet lag
    When Run "python tests/test_tyf.py CLIBehaviour.test_notice_reports_style_lag_for_unlogged_manuscript_change -v"
    Then Exit code is 0

  @covers:tyf-helper-current-contract @criterion:bad-outcome @criterion:edge @criterion:boundary @criterion:integration @bind-file:scripts/tyf.py @bind-file:tests/test_tyf.py @bind-file:tests/test_solo_oracles.py @tool-check:cli
  Scenario: helper records explicit writing language for multilingual works
    When Run "python tests/test_tyf.py CLIBehaviour.test_start_records_non_latin_title_without_id_gate CLIBehaviour.test_start_records_explicit_writing_language CLIBehaviour.test_gate_preserves_utf8_manuscript_text_for_declared_language CLIBehaviour.test_user_yaml_values_are_safely_quoted -v"
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

  @covers:tyf-knowledge-structuring-contract @bind-file:scripts/tyf.py @bind-file:tests/test_tyf.py @tool-check:cli
  Scenario: source fragments structure into knowledge and an amanuensis brief
    When Run "python tests/test_tyf.py CLIBehaviour.test_structure_source_fragment_builds_knowledge_and_amanuensis_brief -v"
    Then Exit code is 0

  @covers:tyf-knowledge-structuring-contract @criterion:bad-outcome @criterion:edge @criterion:boundary @criterion:integration @criterion:security @bind-file:scripts/tyf.py @bind-file:tests/test_tyf.py @tool-check:cli
  Scenario: source fragment structuring is idempotent and tamper-resistant
    When Run "python tests/test_tyf.py CLIBehaviour.test_structure_source_fragment_builds_knowledge_and_amanuensis_brief CLIBehaviour.test_structure_source_fragment_is_idempotent CLIBehaviour.test_structure_refuses_tampered_source_fragment CLIBehaviour.test_import_text_orientation_points_to_structure_pass -v"
    Then Exit code is 0

  @covers:tyf-knowledge-structuring-contract @criterion:bad-outcome @criterion:edge @criterion:boundary @criterion:integration @criterion:security @bind-file:scripts/tyf.py @bind-file:tests/test_tyf.py @tool-check:cli
  Scenario: source fragment structuring refuses changed source material
    When Run "python tests/test_tyf.py CLIBehaviour.test_structure_refuses_tampered_source_fragment -v"
    Then Exit code is 0

  @covers:tyf-knowledge-structuring-contract @criterion:bad-outcome @criterion:edge @criterion:boundary @criterion:integration @criterion:security @bind-file:scripts/tyf.py @bind-file:tests/test_tyf.py @bind-file:tests/test_solo_oracles.py @tool-check:cli
  Scenario: source fragment orientation routes agents to structuring
    When Run "python tests/test_tyf.py CLIBehaviour.test_import_text_orientation_points_to_structure_pass -v"
    Then Exit code is 0

  @covers:tyf-character-consultation-contract @criterion:bad-outcome @criterion:edge @criterion:boundary @criterion:integration @criterion:security @bind-file:scripts/tyf.py @bind-file:tests/test_tyf.py @bind-file:tests/test_solo_oracles.py @bind-file:skills/using-tyf/SKILL.md @bind-file:skills/composing-as-amanuensis/SKILL.md @bind-file:skills/managing-voice/SKILL.md @bind-file:cowork/PROJECT_INSTRUCTIONS.md @tool-check:cli
  Scenario: character consultation stays contained as hidden amanuensis machinery
    When Run "python tests/test_tyf.py CLIBehaviour.test_character_dossier_and_consultation_stay_contained CLIBehaviour.test_character_consultation_refuses_missing_dossier CLIBehaviour.test_character_dossier_supports_non_latin_names -v"
    Then Exit code is 0

  @covers:tyf-character-consultation-contract @criterion:bad-outcome @criterion:edge @criterion:boundary @criterion:integration @criterion:security @bind-file:scripts/tyf.py @bind-file:tests/test_tyf.py @tool-check:cli
  Scenario: character consultation refuses missing dossiers
    When Run "python tests/test_tyf.py CLIBehaviour.test_character_consultation_refuses_missing_dossier -v"
    Then Exit code is 0

  @covers:tyf-character-consultation-contract @criterion:bad-outcome @criterion:edge @criterion:boundary @criterion:integration @criterion:security @bind-file:scripts/tyf.py @bind-file:tests/test_tyf.py @tool-check:cli
  Scenario: character consultation packets stay review-only
    When Run "python tests/test_tyf.py CLIBehaviour.test_character_dossier_and_consultation_stay_contained -v"
    Then Exit code is 0

  @covers:tyf-character-consultation-contract @bind-file:scripts/tyf.py @bind-file:tests/test_solo_oracles.py @bind-file:README.md @bind-file:docs/WORKSPACE_CONTRACT.md @tool-check:cli
  Scenario: character consultation structural oracle remains wired
    When Run "python tests/test_solo_oracles.py character-consultation"
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
  Scenario: Codex skill surface routes book repos through the writing runway
    When Run "python tests/test_solo_oracles.py codex-skill"
    Then Exit code is 0

  @covers:tyf-codex-skill-book-repo @criterion:bad-outcome @criterion:edge @criterion:boundary @criterion:integration @bind-file:scripts/tyf.py @bind-file:scripts/install.sh @bind-file:tests/test_tyf.py @tool-check:cli
  Scenario: Codex skill doc honesty catches stale install and title routing
    When Run "python tests/test_tyf.py DocCheck.test_check_flags_stale_writing_runway_routing Installer.test_codex_install_targets_current_skill_root -v"
    Then Exit code is 0

  @covers:tyf-codex-skill-book-repo @criterion:bad-outcome @criterion:edge @criterion:boundary @criterion:integration @bind-file:skills/using-tyf/SKILL.md @bind-file:skills/using-tyf/agents/openai.yaml @tool-check:cli
  Scenario: Codex dispatcher skill validates as a skill
    When Run "python C:/Users/maste/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/using-tyf"
    Then Exit code is 0

  @covers:tyf-codex-skill-book-repo @criterion:bad-outcome @criterion:edge @criterion:boundary @criterion:integration @bind-file:scripts/tyf.py @bind-file:AGENTS.md @bind-file:CLAUDE.md @bind-file:GEMINI.md @bind-file:tests/test_tyf.py @tool-check:cli
  Scenario: Codex book-repo contexts stay writing-runway aligned
    When Run "python tests/test_tyf.py CLIBehaviour.test_init_creates_workspace_context_contracts DocCheck.test_repo_pack_is_clean -v"
    Then Exit code is 0
