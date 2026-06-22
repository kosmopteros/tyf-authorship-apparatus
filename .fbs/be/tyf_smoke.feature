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
    When Run "python tests/test_tyf.py CLIBehaviour.test_start_records_explicit_writing_language CLIBehaviour.test_user_yaml_values_are_safely_quoted -v"
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
