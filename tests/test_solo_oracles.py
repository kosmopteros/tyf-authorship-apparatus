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
        "start", "begin", "capture", "reflexes", "snapshot", "propose",
        "audit", "accept", "write", "doctor", "check",
    }
    missing = sorted(
        command for command in required
        if f'add_parser("{command}"' not in source
    )
    assert not missing, f"missing TYF commands: {missing}"
    for handler in ("cmd_start", "cmd_begin", "cmd_capture", "cmd_reflexes",
                    "cmd_snapshot", "cmd_propose", "cmd_accept"):
        assert f"def {handler}(" in source, f"missing {handler}"
        assert f"fn={handler}" in source, f"{handler} is not wired into argparse"
    assert "--language" in source, "work creation must expose writing-language metadata"
    assert "language:" in source, "work.yaml must store writing-language metadata"
    tests = (ROOT / "tests" / "test_tyf.py").read_text(encoding="utf-8")
    assert "test_start_accepts_non_latin_title_with_stable_generated_id" in tests
    assert "test_gate_preserves_utf8_manuscript_text_for_declared_language" in tests


def check_gate() -> None:
    source = (ROOT / "scripts" / "tyf.py").read_text(encoding="utf-8")
    tests = (ROOT / "tests" / "test_tyf.py").read_text(encoding="utf-8")
    controlling = (ROOT / "skills" / "controlling-manuscript-writes" / "SKILL.md").read_text(encoding="utf-8")

    for token in ("cmd_propose", "cmd_accept", "--decision", "--lines", "base_sha256",
                  "src_sha256", "acceptance_evidence", "accepted_ranges",
                  "--patch", "accepted_patch", "_apply_unified_patch",
                  "_require_patch_file", "_accepted_patch_problems",
                  "_passing_audit_for", "_require_record_integrity",
                  "record-seals.jsonl", "_acquire_unit_lock", "_release_unit_lock",
                  ".lock.json", "atomic_write"):
        assert token in source, f"Gate runtime missing {token}"
    assert "naked --confirm is retired" in source
    assert "test_write_refuses_without_decision" in tests
    assert "test_write_decision_refuses_out_of_band_edit_after_acceptance" in tests
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
    assert "proposal record" in controlling.lower()
    assert "decision record" in controlling.lower()
    assert "record-seals.jsonl" in controlling
    assert "lock" in controlling.lower()
    assert "--lines" in controlling
    assert "--patch" in controlling


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
    assert "test_propose_refuses_missing_or_tampered_source_fragment" in tests
    assert "test_propose_refuses_fragment_file_and_index_rewritten_under_same_id" in tests
    assert "test_write_and_doctor_refuse_tampered_source_fragment_after_decision" in tests
    assert "id hash mismatch" in source
    assert "source fragment" in ingesting.lower()
    assert "source ref" in controlling.lower() or "source_refs" in controlling


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


def check_onboarding() -> None:
    start_here = (ROOT / "docs" / "START_HERE.md").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    using = (ROOT / "skills" / "using-tyf" / "SKILL.md").read_text(encoding="utf-8")
    init = (ROOT / "skills" / "initializing-a-workspace" / "SKILL.md").read_text(encoding="utf-8")
    cowork = (ROOT / "cowork" / "SETUP.md").read_text(encoding="utf-8")

    assert "## Paste Into Codex" in start_here
    assert "## Paste Into Claude Cowork" in start_here
    assert 'tyf start "<working title>"' in start_here
    assert "[docs/START_HERE.md]" in readme
    assert "do not hand them a command list" in using.lower()
    assert 'tyf start "Working Title"' in init
    assert "Use TYF to start my new book" in cowork
    assert "writing language" in start_here.lower()
    assert "writing language" in init.lower()


def check_onboarding_entry() -> None:
    start_here = (ROOT / "docs" / "START_HERE.md").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "Paste Into Codex" in start_here
    assert "Paste Into Claude Cowork" in start_here
    assert "Do not draft manuscript prose yet" in start_here
    assert "start with a paste prompt" in readme
    assert "You should not need to learn the helper commands" in readme


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "oracle",
        choices=("helper", "plugin", "onboarding", "onboarding-entry", "gate", "provenance"),
    )
    args = parser.parse_args(argv)
    if args.oracle == "helper":
        check_helper()
    elif args.oracle == "plugin":
        check_plugin()
    elif args.oracle == "provenance":
        check_provenance()
    elif args.oracle == "onboarding":
        check_onboarding()
    elif args.oracle == "onboarding-entry":
        check_onboarding_entry()
    else:
        check_gate()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
