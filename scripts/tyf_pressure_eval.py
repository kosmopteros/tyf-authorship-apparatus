#!/usr/bin/env python3
"""Grade TYF prompt-pressure eval evidence.

This is a small deterministic grader for the human/agent pressure scenarios in
tests/. It does not run an LLM. It validates the case manifest and transcript
records produced by a harness run, then reports whether the evidence is strong
or still partial.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CASES = ROOT / "tests" / "pressure-cases.json"
DEFAULT_RUNS = ROOT / "tests" / "pressure-runs"


class EvalError(Exception):
    pass


def _load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - message path
        raise EvalError(f"{path}: cannot read JSON: {exc}") from exc


def load_cases(path: Path) -> dict[str, dict]:
    raw = _load_json(path)
    cases = raw.get("cases")
    if not isinstance(cases, list) or not cases:
        raise EvalError(f"{path}: expected non-empty cases list")
    by_id: dict[str, dict] = {}
    for case in cases:
        if not isinstance(case, dict):
            raise EvalError(f"{path}: every case must be an object")
        case_id = str(case.get("id", "")).strip()
        if not case_id:
            raise EvalError(f"{path}: case missing id")
        if case_id in by_id:
            raise EvalError(f"{path}: duplicate case id {case_id}")
        choices = case.get("choices")
        if not isinstance(choices, dict) or set(choices) != {"A", "B", "C"}:
            raise EvalError(f"{path}: case {case_id} must define A/B/C choices")
        pressures = case.get("pressures")
        if not isinstance(pressures, list) or len(pressures) < 3:
            raise EvalError(f"{path}: case {case_id} must name at least three pressures")
        green_choice = case.get("green_choice")
        if green_choice not in choices:
            raise EvalError(f"{path}: case {case_id} has invalid green_choice")
        red_choices = case.get("red_choices")
        if not isinstance(red_choices, list) or not red_choices:
            raise EvalError(f"{path}: case {case_id} must define red_choices")
        if any(choice not in choices for choice in red_choices):
            raise EvalError(f"{path}: case {case_id} has invalid red_choices")
        skills = case.get("expected_skills")
        if not isinstance(skills, list) or not skills:
            raise EvalError(f"{path}: case {case_id} must name expected skills")
        by_id[case_id] = case
    return by_id


def iter_run_records(path: Path):
    files = [path] if path.is_file() else sorted(path.glob("*.jsonl"))
    if not files:
        raise EvalError(f"{path}: no run JSONL files found")
    for file_path in files:
        for line_no, line in enumerate(file_path.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise EvalError(f"{file_path}:{line_no}: invalid JSONL record: {exc}") from exc
            yield file_path, line_no, record


def _transcript_is_present(record: dict) -> bool:
    transcript = record.get("transcript")
    if isinstance(transcript, list):
        return bool(transcript) and all(
            isinstance(turn, dict)
            and str(turn.get("role", "")).strip()
            and str(turn.get("content", "")).strip()
            for turn in transcript
        )
    return isinstance(transcript, str) and bool(transcript.strip())


def grade(cases: dict[str, dict], run_path: Path, red_threshold: float) -> dict:
    records = []
    errors = []
    for file_path, line_no, record in iter_run_records(run_path):
        if not isinstance(record, dict):
            errors.append(f"{file_path}:{line_no}: record must be an object")
            continue
        case_id = str(record.get("case_id", "")).strip()
        mode = str(record.get("mode", "")).strip().lower()
        choice = str(record.get("choice", "")).strip()
        if case_id not in cases:
            errors.append(f"{file_path}:{line_no}: unknown case_id {case_id!r}")
            continue
        if mode not in {"green", "red"}:
            errors.append(f"{file_path}:{line_no}: mode must be green or red")
            continue
        if choice not in {"A", "B", "C"}:
            errors.append(f"{file_path}:{line_no}: choice must be A, B, or C")
            continue
        if not _transcript_is_present(record):
            errors.append(f"{file_path}:{line_no}: transcript is required")
            continue
        record = dict(record)
        record["_source"] = f"{file_path}:{line_no}"
        records.append(record)
    if errors:
        raise EvalError("\n".join(errors))

    green_records = [r for r in records if r["mode"] == "green"]
    red_records = [r for r in records if r["mode"] == "red"]
    green_case_ids = {r["case_id"] for r in green_records}
    red_case_ids = {r["case_id"] for r in red_records}
    green_pass = []
    red_failure_observed = []
    green_skill_failures = []

    for record in green_records:
        case = cases[record["case_id"]]
        if record["choice"] == case["green_choice"]:
            green_pass.append(record)
        loaded = set(record.get("skills_loaded") or [])
        if not loaded.intersection(case["expected_skills"]):
            green_skill_failures.append(record["_source"])

    for record in red_records:
        if record["choice"] in cases[record["case_id"]]["red_choices"]:
            red_failure_observed.append(record)

    transcript_kinds = {str(r.get("transcript_kind", "full")) for r in records}
    red_rate = len(red_failure_observed) / len(red_records) if red_records else 0.0
    all_green_cases = len(green_case_ids) == len(cases)
    all_red_cases = len(red_case_ids) == len(cases)
    all_green_pass = len(green_pass) == len(green_records) and all_green_cases
    full_transcripts = transcript_kinds == {"full"}
    baseline_strong = bool(red_records) and all_red_cases and red_rate >= red_threshold
    proof = "strong" if all_green_pass and baseline_strong and full_transcripts and not green_skill_failures else "partial"

    return {
        "cases": len(cases),
        "green_trials": len(green_records),
        "green_cases": len(green_case_ids),
        "green_pass": len(green_pass),
        "red_trials": len(red_records),
        "red_cases": len(red_case_ids),
        "red_failures_observed": len(red_failure_observed),
        "red_failure_rate": red_rate,
        "red_threshold": red_threshold,
        "transcript_kinds": sorted(transcript_kinds),
        "green_skill_failures": green_skill_failures,
        "proof": proof,
        "limitations": [
            item for item, condition in (
                ("missing green coverage", not all_green_cases),
                ("green choice failure", not all_green_pass),
                ("missing red coverage", not all_red_cases),
                ("weak red baseline", not baseline_strong),
                ("partial transcripts", not full_transcripts),
                ("missing green skill evidence", bool(green_skill_failures)),
            )
            if condition
        ],
    }


def print_report(result: dict) -> None:
    print("TYF pressure eval")
    print(f"  cases: {result['cases']}")
    print(f"  green: {result['green_pass']}/{result['green_trials']} trials across {result['green_cases']}/{result['cases']} cases")
    print(
        "  red failures: "
        f"{result['red_failures_observed']}/{result['red_trials']} trials across "
        f"{result['red_cases']}/{result['cases']} cases "
        f"(rate {result['red_failure_rate']:.2f}, threshold {result['red_threshold']:.2f})"
    )
    print(f"  transcripts: {', '.join(result['transcript_kinds'])}")
    print(f"  proof: {result['proof']}")
    if result["limitations"]:
        print("  limitations:")
        for limitation in result["limitations"]:
            print(f"    - {limitation}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", default=str(DEFAULT_CASES), help="pressure case manifest JSON")
    parser.add_argument("--runs", default=str(DEFAULT_RUNS), help="run JSONL file or directory")
    parser.add_argument("--red-threshold", type=float, default=0.60,
                        help="minimum RED failure rate required for strong proof")
    parser.add_argument("--require-strong", action="store_true",
                        help="exit nonzero unless evidence is strong")
    parser.add_argument("--json", action="store_true", help="print machine-readable summary")
    args = parser.parse_args(argv)

    try:
        if not 0.0 <= args.red_threshold <= 1.0:
            raise EvalError("--red-threshold must be between 0 and 1")
        result = grade(load_cases(Path(args.cases)), Path(args.runs), args.red_threshold)
    except EvalError as exc:
        print(f"pressure-eval: {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print_report(result)
    if args.require_strong and result["proof"] != "strong":
        print("pressure-eval: strong prompt-level proof is not established", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
