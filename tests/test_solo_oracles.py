#!/usr/bin/env python3
"""Small independent SOLO oracles for TYF's immediate feature claims.

These complement the broad unittest smoke suite and the Codex plugin validator
with direct structural checks, so SOLO can see more than one executable oracle.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys


ROOT = pathlib.Path(__file__).resolve().parents[1]


def check_helper() -> None:
    source = (ROOT / "scripts" / "tyf.py").read_text(encoding="utf-8")
    required = {
        "start", "begin", "import", "capture", "resume", "reflexes", "snapshot", "propose",
        "audit", "review", "accept", "adopt", "write", "doctor", "check", "structure", "character",
        "consult-character",
    }
    missing = sorted(
        command for command in required
        if f'add_parser("{command}"' not in source
    )
    assert not missing, f"missing TYF commands: {missing}"
    for handler in ("cmd_start", "cmd_begin", "cmd_import", "cmd_capture", "cmd_structure", "cmd_character",
                    "cmd_consult_character", "cmd_resume",
                    "cmd_reflexes", "cmd_snapshot", "cmd_propose", "cmd_review", "cmd_accept",
                    "cmd_adopt"):
        assert f"def {handler}(" in source, f"missing {handler}"
        assert f"fn={handler}" in source, f"{handler} is not wired into argparse"
    assert "--language" in source, "work creation must expose writing-language metadata"
    assert "language:" in source, "work.yaml must store writing-language metadata"
    for token in ("events.jsonl", "_event_record_hash", "_event_journal_problems",
                  "previous_hash", "hash chain"):
        assert token in source, f"canonical event journal missing {token}"
    tests = (ROOT / "tests" / "test_tyf.py").read_text(encoding="utf-8")
    assert "test_start_records_non_latin_title_without_id_gate" in tests
    assert "test_start_allows_no_title_and_keeps_intake_non_blocking" in tests
    assert "test_init_creates_portable_workspace_marker" in tests
    assert "test_import_chat_preserves_raw_input_creates_titleless_work_and_fragment" in tests
    assert "test_resume_reports_active_work_state_and_next_useful_move" in tests
    assert "test_gate_preserves_utf8_manuscript_text_for_declared_language" in tests
    assert "test_canonical_event_journal_records_core_actions_with_hash_chain" in tests
    assert "test_doctor_flags_tampered_canonical_event_journal" in tests
    assert "test_doctor_flags_missing_canonical_event_journal" in tests
    assert "test_doctor_flags_malformed_canonical_event_journal" in tests
    assert "test_mutating_command_refuses_missing_canonical_event_journal" in tests


def check_gate() -> None:
    source = (ROOT / "scripts" / "tyf.py").read_text(encoding="utf-8")
    tests = (ROOT / "tests" / "test_tyf.py").read_text(encoding="utf-8")
    controlling = (ROOT / "skills" / "controlling-manuscript-writes" / "SKILL.md").read_text(encoding="utf-8")

    for token in ("cmd_propose", "cmd_review", "cmd_accept", "--decision", "--lines", "base_sha256",
                  "src_sha256", "acceptance_evidence", "accepted_ranges",
                  "--patch", "accepted_patch", "_apply_unified_patch",
                  "_require_patch_file", "_accepted_patch_problems",
                  "_passing_audit_for", "_require_record_integrity", "_write_audit_report",
                  "_write_author_review_packet", "_author_review_for", "author_review_packet",
                  "record-seals.jsonl", "_acquire_unit_lock", "_release_unit_lock",
                  ".lock.json", "atomic_write", "_set_work_status",
                  "_require_work_status", "ready-for-audit", "needs-revision",
                  "drafting", "audited", "accepted", "written"):
        assert token in source, f"Gate runtime missing {token}"
    assert "naked --confirm is retired" in source
    assert "test_write_refuses_without_decision" in tests
    assert "test_write_decision_refuses_out_of_band_edit_after_acceptance" in tests
    assert "test_adopt_author_manuscript_edit_updates_base_for_next_decision" in tests
    assert "test_accept_line_ranges_writes_only_selected_lines" in tests
    assert "test_accept_line_ranges_refuses_invalid_or_out_of_range_selection" in tests
    assert "test_accept_patch_applies_exact_unified_diff_to_manuscript_base" in tests
    assert "test_accept_patch_refuses_mixed_line_scope" in tests
    assert "test_accept_patch_refuses_hunk_count_mismatch" in tests
    assert "test_write_refuses_tampered_accepted_patch_file" in tests
    assert "test_doctor_flags_missing_accepted_patch_file" in tests
    assert "test_write_refuses_tampered_decision_record" in tests
    assert "test_write_refuses_tampered_audit_record" in tests
    assert "test_doctor_flags_tampered_gate_record" in tests
    assert "test_doctor_flags_missing_gate_record_seal" in tests
    assert "test_write_refuses_existing_manuscript_unit_lock" in tests
    assert "test_doctor_flags_manuscript_unit_lock" in tests
    assert "test_gate_updates_work_status_across_transitions" in tests
    assert "test_audit_record_writes_inspectable_editorial_note" in tests
    assert "test_accept_refuses_before_passing_audit_state" in tests
    assert "test_accept_refuses_after_failed_audit_state" in tests
    assert "test_accept_requires_audit_for_the_same_proposal" in tests
    assert "test_accept_requires_author_review_packet" in tests
    assert "test_write_and_doctor_refuse_tampered_author_review_packet" in tests
    assert "test_write_refuses_when_work_status_is_not_accepted" in tests
    assert "proposal record" in controlling.lower()
    assert "author review packet" in controlling.lower()
    assert "decision record" in controlling.lower()
    assert "record-seals.jsonl" in controlling
    assert "lock" in controlling.lower()
    assert "--lines" in controlling
    assert "--patch" in controlling
    assert "tyf adopt" in controlling


def check_provenance() -> None:
    source = (ROOT / "scripts" / "tyf.py").read_text(encoding="utf-8")
    tests = (ROOT / "tests" / "test_tyf.py").read_text(encoding="utf-8")
    ingesting = (ROOT / "skills" / "ingesting-sources" / "SKILL.md").read_text(encoding="utf-8")
    controlling = (ROOT / "skills" / "controlling-manuscript-writes" / "SKILL.md").read_text(encoding="utf-8")

    for token in ("sources/fragments", "fragments.jsonl", "source_refs",
                  "--source-ref", "_mint_source_fragment",
                  "_resolve_source_refs", "_source_fragment_integrity_problem"):
        assert token in source, f"source provenance runtime missing {token}"
    assert "test_source_capture_fragment_survives_proposal_decision_and_write" in tests
    assert "test_source_fragments_are_workspace_owned_and_reusable_across_works" in tests
    assert "test_propose_refuses_missing_or_tampered_source_fragment" in tests
    assert "test_propose_refuses_fragment_file_and_index_rewritten_under_same_id" in tests
    assert "test_write_and_doctor_refuse_tampered_source_fragment_after_decision" in tests
    assert "id hash mismatch" in source
    assert "origin_work" in source
    assert "source fragment" in ingesting.lower()
    assert "source ref" in controlling.lower() or "source_refs" in controlling

def check_amanuensis_entry() -> None:
    source = (ROOT / "scripts" / "tyf.py").read_text(encoding="utf-8")
    tests = (ROOT / "tests" / "test_tyf.py").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    workspace = (ROOT / "docs" / "WORKSPACE_CONTRACT.md").read_text(encoding="utf-8")
    ingesting = (ROOT / "skills" / "ingesting-sources" / "SKILL.md").read_text(encoding="utf-8")

    for token in ("title_status", "_untitled_work_id", "sources/imports",
                  "sources/interviews", "cmd_import", "cmd_resume", "cmd_adopt",
                  "Analysis Pass For The Agent", "Containment", "_looks_tyf_shaped"):
        assert token in source, f"amanuensis entry runtime missing {token}"
    for test_name in (
        "test_start_allows_no_title_and_keeps_intake_non_blocking",
        "test_import_chat_preserves_raw_input_creates_titleless_work_and_fragment",
        "test_import_zip_preserves_bundle_without_manuscript_write",
        "test_import_folder_preserves_tree_and_lists_without_live_merge",
        "test_import_tyf_shaped_zip_is_detected_without_merging",
        "test_source_fragments_are_workspace_owned_and_reusable_across_works",
        "test_adopt_author_manuscript_edit_updates_base_for_next_decision",
        "test_resume_reports_active_work_state_and_next_useful_move",
    ):
        assert test_name in tests, f"missing test {test_name}"
    assert "title optional" in readme.lower() or "without a title" in readme.lower()
    assert "containment-first" in readme.lower()
    assert "sources/interviews" in workspace
    assert "sources/imports" in workspace
    assert "orientation packet" in ingesting.lower()
    assert "organization principle" in ingesting.lower()


def check_writing_runway() -> None:
    source = (ROOT / "scripts" / "tyf.py").read_text(encoding="utf-8")
    tests = (ROOT / "tests" / "test_tyf.py").read_text(encoding="utf-8")
    using = (ROOT / "skills" / "using-tyf" / "SKILL.md").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    for token in ("cmd_start", "_write_start_runway", "Writing runway",
                  "candidate-draft.md", "No manuscript text was written",
                  "let the Gate come later", "sources/interviews"):
        assert token in source, f"writing runway runtime missing {token}"
    assert "cmd_today" not in source, "today command must not survive as an alias"
    assert '"today"' not in source.replace('"tyf today"', ""), "today must not be event-journal protected"
    assert "test_start_without_arrival_opens_titleless_writing_runway" in tests
    assert "test_start_updates_root_title_language_and_evidence_packet" in tests
    assert "test_start_with_folder_arrival_preserves_scaffold_and_opens_runway" in tests
    assert "test_today_command_is_removed" in tests
    assert "tyf start" in using
    assert "tyf start" in readme
    assert "tyf today" not in using
    assert "tyf today" not in readme
    assert "write today" in readme.lower() or "writing today" in readme.lower()


def check_portability() -> None:
    source = (ROOT / "scripts" / "tyf.py").read_text(encoding="utf-8")
    tests = (ROOT / "tests" / "test_tyf.py").read_text(encoding="utf-8")
    portability = (ROOT / "docs" / "PORTABILITY.md").read_text(encoding="utf-8")
    workspace = (ROOT / "docs" / "WORKSPACE_CONTRACT.md").read_text(encoding="utf-8")

    for token in ("tyf.portable.json", "tyf-workspace", "canonical_text_state",
                  "derived_disposable_state", ".tyf/events.jsonl", ".tyf/ledger.db",
                  '"git": "optional"'):
        assert token in source, f"portable marker runtime missing {token}"
    assert "test_init_creates_portable_workspace_marker" in tests
    assert "test_import_folder_preserves_tree_and_lists_without_live_merge" in tests
    assert "test_import_tyf_shaped_zip_is_detected_without_merging" in tests
    assert "text-first author-work bundle" in portability
    assert "Markdown, YAML, and JSONL are the durable truth" in portability
    assert "tyf.portable.json" in workspace


def check_single_work() -> None:
    source = (ROOT / "scripts" / "tyf.py").read_text(encoding="utf-8")
    tests = (ROOT / "tests" / "test_tyf.py").read_text(encoding="utf-8")
    public_files = [
        ROOT / "README.md",
        ROOT / "docs" / "WORKSPACE_CONTRACT.md",
        ROOT / "docs" / "PORTABILITY.md",
        ROOT / "skills" / "using-tyf" / "SKILL.md",
        ROOT / "skills" / "initializing-a-workspace" / "SKILL.md",
        ROOT / "skills" / "working-the-workspace" / "SKILL.md",
        ROOT / "cowork" / "PROJECT_INSTRUCTIONS.md",
        ROOT / "cowork" / "SCHEDULED_TASKS.md",
        ROOT / "TYF-manifesto-and-architecture.md",
    ]

    for token in (
        "single_work",
        '"format_version": "0.5.0"',
        '"work.yaml"',
        '"drafts/"',
        '"manuscript/"',
        "ROOT_WORK_ID",
        "test_init_creates_single_work_root_layout",
        "test_start_without_arrival_opens_titleless_writing_runway",
    ):
        assert token in source or token in tests, f"single-work runtime/test missing {token}"

    for path in public_files:
        text = path.read_text(encoding="utf-8")
        assert "single work" in text.lower() or "book folder" in text.lower(), f"{path} does not describe the single-work beta surface"
        assert "drafts/candidate-draft.md" in text or "drafts/" in text, f"{path} does not point to root drafts"
        assert "works/<id>" not in text, f"{path} still exposes works/<id> as public beta shape"
        assert "works/*/drafts" not in text, f"{path} still exposes multi-work draft glob"
        assert "works/*/" not in text, f"{path} still exposes multi-work scheduled-task glob"


def check_plugin() -> None:
    manifest_path = ROOT / ".codex-plugin" / "plugin.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["name"] == "tyf"
    assert manifest["skills"] == "./skills/"
    assert manifest["author"]["name"]
    interface = manifest["interface"]
    assert interface["displayName"]
    assert "writing" in " ".join(manifest.get("keywords", [])).lower()
    assert (ROOT / "skills").is_dir()


def check_codex_skill() -> None:
    manifest = json.loads((ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))
    install = (ROOT / "scripts" / "install.sh").read_text(encoding="utf-8")
    portability = (ROOT / "docs" / "PORTABILITY.md").read_text(encoding="utf-8")
    using = (ROOT / "skills" / "using-tyf" / "SKILL.md").read_text(encoding="utf-8")
    openai_yaml = ROOT / "skills" / "using-tyf" / "agents" / "openai.yaml"
    contexts = [(ROOT / name).read_text(encoding="utf-8") for name in ("AGENTS.md", "CLAUDE.md", "GEMINI.md")]

    assert manifest["version"] == "0.5.0"
    assert manifest["skills"] == "./skills/"
    assert '${CODEX_HOME:-$HOME/.codex}/skills' in install
    assert "~/.codex/skills/" in portability
    assert "$CODEX_HOME/skills" in portability
    assert openai_yaml.is_file()
    metadata = openai_yaml.read_text(encoding="utf-8")
    assert "display_name:" in metadata
    assert "default_prompt:" in metadata
    assert "$using-tyf" in metadata
    assert "tyf start" in using
    assert all("tyf start" in text for text in contexts)
    assert "tyf today" not in using
    assert not any("tyf today" in text for text in contexts)
    assert not any('tyf start "Working Title"' in text for text in contexts)
    assert not any("after getting a title" in text for text in contexts)


def check_onboarding() -> None:
    start_here = (ROOT / "docs" / "START_HERE.md").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    using = (ROOT / "skills" / "using-tyf" / "SKILL.md").read_text(encoding="utf-8")
    init = (ROOT / "skills" / "initializing-a-workspace" / "SKILL.md").read_text(encoding="utf-8")
    cowork = (ROOT / "cowork" / "SETUP.md").read_text(encoding="utf-8")

    assert "## Paste Into Codex" in start_here
    assert "## Paste Into Claude Cowork" in start_here
    assert "do not block on a title" in start_here.lower()
    assert "tyf start <path>" in start_here
    assert "[docs/START_HERE.md]" in readme
    assert "do not hand them a command list" in using.lower()
    assert "tyf start" in init
    assert "tyf import <path>" in init
    assert "Use TYF to help me start writing my new book today" in cowork
    assert "writing language" in start_here.lower()
    assert "writing language" in init.lower()


def check_onboarding_entry() -> None:
    start_here = (ROOT / "docs" / "START_HERE.md").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "Paste Into Codex" in start_here
    assert "Paste Into Claude Cowork" in start_here
    assert "Do not write manuscript text yet" in start_here
    assert "start with a paste prompt" in readme
    assert "You should not need to learn the helper commands" in readme


def check_character_consultation() -> None:
    source = (ROOT / "scripts" / "tyf.py").read_text(encoding="utf-8")
    tests = (ROOT / "tests" / "test_tyf.py").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    contract = (ROOT / "docs" / "WORKSPACE_CONTRACT.md").read_text(encoding="utf-8")
    using = (ROOT / "skills" / "using-tyf" / "SKILL.md").read_text(encoding="utf-8")
    composing = (ROOT / "skills" / "composing-as-amanuensis" / "SKILL.md").read_text(encoding="utf-8")
    voice = (ROOT / "skills" / "managing-voice" / "SKILL.md").read_text(encoding="utf-8")
    cowork = (ROOT / "cowork" / "PROJECT_INSTRUCTIONS.md").read_text(encoding="utf-8")

    for token in (
        "def cmd_character(",
        "def cmd_consult_character(",
        "knowledge-base/characters",
        "voice/characters",
        "character-consults",
        "hidden amanuensis machinery",
        "candidate dramatic insight",
        "Ground only in this character dossier",
        "not evidence, not manuscript, not a source",
    ):
        assert token in source, f"character consultation runtime missing {token}"
    for name in (
        "test_character_dossier_and_consultation_stay_contained",
        "test_character_consultation_refuses_missing_dossier",
        "test_character_dossier_supports_non_latin_names",
    ):
        assert name in tests, f"missing {name}"
    assert "what would Mark say" in readme
    assert "candidate dramatic insight" in readme
    assert "character-consults" in contract
    assert "what would Mark say here" in using
    assert "Character consultation" in composing
    assert "voice/characters/" in voice
    assert "hidden amanuensis machinery" in cowork


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "oracle",
        choices=("helper", "plugin", "codex-skill", "onboarding", "onboarding-entry", "gate", "provenance", "character-consultation", "amanuensis-entry", "writing-runway", "portability", "single-work"),
    )
    args = parser.parse_args(argv)
    if args.oracle == "helper":
        check_helper()
    elif args.oracle == "plugin":
        check_plugin()
    elif args.oracle == "codex-skill":
        check_codex_skill()
    elif args.oracle == "provenance":
        check_provenance()
    elif args.oracle == "amanuensis-entry":
        check_amanuensis_entry()
    elif args.oracle == "writing-runway":
        check_writing_runway()
    elif args.oracle == "portability":
        check_portability()
    elif args.oracle == "single-work":
        check_single_work()
    elif args.oracle == "onboarding":
        check_onboarding()
    elif args.oracle == "onboarding-entry":
        check_onboarding_entry()
    elif args.oracle == "character-consultation":
        check_character_consultation()
    else:
        check_gate()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
