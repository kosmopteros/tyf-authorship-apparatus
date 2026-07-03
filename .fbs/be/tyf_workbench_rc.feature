Feature: TYF Workbench and continuity RC surfaces

  @covers:tyf-workbench-local-desk-contract @bind-file:scripts/tyf.py @bind-file:scripts/tyf_workbench_v06.py @bind-file:tests/test_tyf.py @bind-file:tests/test_workbench_v06.py @tool-check:cli
  Scenario: Workbench collects multi-surface units and scaffolds the local desk
    When Run "python -m pytest -q tests/test_workbench_v06.py::WorkbenchV06Tests::test_collects_multi_surface_units_and_scaffold tests/test_tyf.py::CLIBehaviour::test_workbench_is_only_public_browser_command tests/test_tyf.py::CLIBehaviour::test_workbench_generates_static_review_bench_without_manuscript_write"
    Then Exit code is 0

  @covers:tyf-workbench-local-desk-contract @criterion:bad-outcome @criterion:edge @criterion:boundary @criterion:integration @criterion:security @bind-file:scripts/tyf_workbench_v06.py @bind-file:tests/test_workbench_v06.py @tool-check:cli
  Scenario: Workbench rejects stale draft saves with conflict evidence
    When Run "python -m pytest -q tests/test_workbench_v06.py::WorkbenchV06Tests::test_saves_draft_with_compare_and_swap tests/test_workbench_v06.py::WorkbenchV06Tests::test_parallel_draft_saves_produce_one_save_and_one_conflict tests/test_workbench_v06.py::WorkbenchV06Tests::test_static_html_has_unsaved_draft_guard_and_accessible_status"
    Then Exit code is 0

  @covers:tyf-workbench-local-desk-contract @criterion:bad-outcome @criterion:edge @criterion:boundary @criterion:integration @criterion:security @bind-file:scripts/tyf_workbench_v06.py @bind-file:tests/test_workbench_v06.py @tool-check:cli
  Scenario: Workbench notes footnotes Gate packets and context do not mutate manuscript
    When Run "python -m pytest -q tests/test_workbench_v06.py::WorkbenchV06Tests::test_notes_footnotes_gate_packets_and_context_do_not_touch_manuscript tests/test_workbench_v06.py::WorkbenchV06Tests::test_gate_packet_rejects_selection_not_in_saved_draft"
    Then Exit code is 0

  @covers:tyf-workbench-local-desk-contract @criterion:bad-outcome @criterion:edge @criterion:boundary @criterion:integration @bind-file:scripts/tyf_workbench_v06.py @bind-file:tests/test_workbench_v06.py @tool-check:cli
  Scenario: Workbench shows book style and image inventory on the author surface
    When Run "python -m pytest -q tests/test_workbench_v06.py::WorkbenchV06Tests::test_static_html_shows_book_style_and_image_inventory"
    Then Exit code is 0

  @covers:tyf-workbench-local-desk-contract @criterion:bad-outcome @criterion:edge @criterion:boundary @criterion:integration @criterion:security @bind-file:scripts/tyf_workbench_v06.py @bind-file:tests/test_workbench_v06.py @tool-check:cli
  Scenario: Workbench creates new draft units only through the draft surface
    When Run "python -m pytest -q tests/test_workbench_v06.py::WorkbenchV06Tests::test_can_create_new_draft_unit"
    Then Exit code is 0

  @covers:tyf-workbench-bridge-contract @bind-file:scripts/tyf_workbench_mcp.py @bind-file:tests/test_workbench_mcp.py @tool-check:cli
  Scenario: Workbench bridge lists scoped TYF tools and no raw file writer
    When Run "python -m pytest -q tests/test_workbench_mcp.py::WorkbenchMCPTests::test_lists_expected_tools_after_initialize tests/test_workbench_mcp.py::WorkbenchMCPTests::test_stdio_server_round_trips_like_codex_mcp_client"
    Then Exit code is 0

  @covers:tyf-workbench-bridge-contract @criterion:bad-outcome @criterion:edge @criterion:boundary @criterion:integration @criterion:security @bind-file:scripts/tyf.py @bind-file:scripts/tyf_workbench_mcp.py @bind-file:tests/test_tyf.py @bind-file:tests/test_workbench_mcp.py @tool-check:cli
  Scenario: Workbench writes Codex-recognized MCP config without leaking tools outside the book workspace
    When Run "python -m pytest -q tests/test_tyf.py::CLIBehaviour::test_workbench_writes_ready_codex_mcp_config tests/test_workbench_mcp.py::WorkbenchMCPTests::test_workspace_bound_server_exposes_no_tools_outside_workspace"
    Then Exit code is 0

  @covers:tyf-workbench-bridge-contract @criterion:bad-outcome @criterion:edge @criterion:boundary @criterion:integration @criterion:security @bind-file:scripts/tyf_workbench_mcp.py @bind-file:tests/test_workbench_mcp.py @tool-check:cli
  Scenario: Workbench bridge actions create review artifacts without manuscript writes
    When Run "python -m pytest -q tests/test_workbench_mcp.py::WorkbenchMCPTests::test_note_footnote_gate_graph_and_status_actions_do_not_touch_manuscript"
    Then Exit code is 0

  @covers:tyf-workbench-bridge-contract @criterion:bad-outcome @criterion:edge @criterion:boundary @criterion:integration @criterion:security @bind-file:scripts/tyf_workbench_mcp.py @bind-file:scripts/tyf_workbench_status.py @bind-file:scripts/tyf_codex_bridge.py @bind-file:scripts/tyf_codex_bridge_v07.py @bind-file:scripts/tyf_codex_approvals.py @bind-file:tests/test_workbench_mcp.py @bind-file:tests/test_workbench_status.py @bind-file:tests/test_codex_bridge_context.py @bind-file:tests/test_codex_approvals.py @tool-check:cli
  Scenario: Workbench bridge surfaces conflicts live status and approval state
    When Run "python -m pytest -q tests/test_workbench_mcp.py::WorkbenchMCPTests::test_conflict_detection tests/test_workbench_mcp.py::WorkbenchMCPTests::test_gate_packet_requires_explicit_base_hash_and_saved_selection tests/test_workbench_mcp.py::WorkbenchMCPTests::test_prepare_gate_packet_schema_requires_base_hash tests/test_workbench_status.py tests/test_codex_bridge_context.py tests/test_codex_approvals.py"
    Then Exit code is 0

  @covers:tyf-graph-storage-projection-contract @bind-file:scripts/tyf_graph_projection.py @bind-file:tests/test_graph_projection.py @tool-check:cli
  Scenario: Graph projection writes rebuildable graph outputs and JSONL audit
    When Run "python -m pytest -q tests/test_graph_projection.py::GraphProjectionTests::test_audits_jsonl_and_builds_graph_outputs"
    Then Exit code is 0

  @covers:tyf-graph-storage-projection-contract @criterion:bad-outcome @criterion:edge @criterion:boundary @criterion:integration @criterion:security @bind-file:scripts/tyf_architecture_contracts.py @bind-file:tests/test_architecture_contracts.py @tool-check:cli
  Scenario: Storage contract declares canonical ledgers records and caches distinctly
    When Run "python -m pytest -q tests/test_architecture_contracts.py::ArchitectureContractTests::test_storage_contract_has_required_classes"
    Then Exit code is 0

  @covers:tyf-graph-storage-projection-contract @criterion:bad-outcome @criterion:edge @criterion:boundary @criterion:integration @criterion:security @bind-file:scripts/tyf_architecture_contracts.py @bind-file:tests/test_architecture_contracts.py @tool-check:cli
  Scenario: Graph and storage architecture forbids accidental manuscript write routes
    When Run "python -m pytest -q tests/test_architecture_contracts.py::ArchitectureContractTests::test_no_forbidden_manuscript_routes"
    Then Exit code is 0

  @covers:tyf-derived-book-review-contract @bind-file:scripts/tyf_concept_review.py @bind-file:tests/test_concept_review.py @tool-check:cli
  Scenario: Concept review writes line-level review artifacts
    When Run "python -m pytest -q tests/test_concept_review.py::ConceptReviewTests::test_concept_review_finds_rename_and_drift"
    Then Exit code is 0

  @covers:tyf-derived-book-review-contract @criterion:bad-outcome @criterion:edge @criterion:boundary @criterion:integration @criterion:security @bind-file:scripts/tyf_concept_review.py @bind-file:tests/test_concept_review.py @tool-check:cli
  Scenario: Concept review flags retired names variants opposition and definitions
    When Run "python -m pytest -q tests/test_concept_review.py::ConceptReviewTests::test_concept_review_finds_rename_and_drift"
    Then Exit code is 0

  @covers:tyf-derived-book-review-contract @criterion:bad-outcome @criterion:edge @criterion:boundary @criterion:integration @criterion:security @bind-file:scripts/tyf_continuity_review.py @bind-file:docs/CONTINUITY_REVIEW.md @bind-file:tests/test_continuity_review.py @tool-check:cli
  Scenario: Continuity review flags promises open threads register scope and reader state
    When Run "python -m pytest -q tests/test_continuity_review.py::ContinuityReviewTests::test_continuity_review_detects_registry_issues"
    Then Exit code is 0

  @covers:tyf-derived-book-review-contract @criterion:bad-outcome @criterion:edge @criterion:boundary @criterion:integration @criterion:security @bind-file:scripts/tyf_continuity_decision.py @bind-file:scripts/tyf_polish_review.py @bind-file:tests/test_polish_and_decisions.py @tool-check:cli
  Scenario: Polish and continuity decisions remain review-only derived surfaces
    When Run "python -m pytest -q tests/test_polish_and_decisions.py"
    Then Exit code is 0

  @covers:tyf-private-rc-safety-contract @bind-file:scripts/tyf_rc_doctor.py @bind-file:tests/test_rc_recovery_doctor.py @tool-check:cli
  Scenario: RC doctor reports a passing private Workbench workspace
    When Run "python -m pytest -q tests/test_rc_recovery_doctor.py::RcRecoveryDoctorTests::test_rc_doctor_passes_and_live_html_has_markers"
    Then Exit code is 0

  @covers:tyf-private-rc-safety-contract @criterion:bad-outcome @criterion:edge @criterion:boundary @criterion:integration @criterion:security @bind-file:scripts/tyf_recovery.py @bind-file:tests/test_rc_recovery_doctor.py @tool-check:cli
  Scenario: RC recovery keeps browser text as copy and packet before reload
    When Run "python -m pytest -q tests/test_rc_recovery_doctor.py::RcRecoveryDoctorTests::test_recovery_copy_packet_and_reload"
    Then Exit code is 0

  @covers:tyf-private-rc-safety-contract @criterion:bad-outcome @criterion:edge @criterion:boundary @criterion:integration @criterion:security @bind-file:scripts/tyf_workbench_live.py @bind-file:tests/test_workbench_recovery_routes.py @tool-check:cli
  Scenario: RC recovery routes require loopback token and expose safe recovery actions
    When Run "python -m pytest -q tests/test_workbench_recovery_routes.py"
    Then Exit code is 0

  @covers:tyf-private-rc-safety-contract @criterion:bad-outcome @criterion:edge @criterion:boundary @criterion:integration @criterion:security @bind-file:scripts/tyf_workbench_slots.py @bind-file:scripts/tyf_architecture_contracts.py @bind-file:tests/test_architecture_contracts.py @tool-check:cli
  Scenario: RC architecture slots and manuscript route checks fail loudly
    When Run "python -m pytest -q tests/test_architecture_contracts.py"
    Then Exit code is 0

  @covers:tyf-review-command-wrapper-contract @bind-file:scripts/tyf_review.py @bind-file:scripts/tyf_graph_projection.py @bind-file:scripts/tyf_concept_review.py @bind-file:scripts/tyf_continuity_review.py @bind-file:scripts/tyf_polish_review.py @bind-file:tests/test_review_wrapper.py @bind-file:pyproject.toml @tool-check:cli
  Scenario: Review wrapper dispatches graph concept continuity and polish
    When Run "python -m pytest -q tests/test_review_wrapper.py::ReviewWrapperTests::test_wrapper_dispatches_graph_concept_continuity_and_polish"
    Then Exit code is 0

  @covers:tyf-review-command-wrapper-contract @criterion:bad-outcome @criterion:edge @criterion:boundary @criterion:integration @bind-file:scripts/tyf_review.py @bind-file:scripts/tyf_graph_projection.py @bind-file:scripts/tyf_rc_doctor.py @bind-file:tests/test_review_wrapper.py @tool-check:cli
  Scenario: Review wrapper dispatches doctor and graph sqlite variants
    When Run "python -m pytest -q tests/test_review_wrapper.py::ReviewWrapperTests::test_wrapper_dispatches_doctor_and_graph_sqlite"
    Then Exit code is 0

  @covers:tyf-review-command-wrapper-contract @criterion:bad-outcome @criterion:edge @criterion:boundary @criterion:integration @bind-file:scripts/tyf_review.py @bind-file:pyproject.toml @tool-check:cli
  Scenario: Review wrapper exposes canonical subcommand help
    When Run "python scripts/tyf_review.py --help"
    Then Exit code is 0
