#!/usr/bin/env python3
"""Canonical review command wrapper.

Standalone commands remain available for convenience, but this wrapper gives the
architecture a single author-facing review surface:

    tyf-review graph
    tyf-review concept
    tyf-review continuity
    tyf-review polish
    tyf-review doctor
"""

from __future__ import annotations

import argparse
import sys
from typing import List, Optional

import tyf_concept_review
import tyf_continuity_review
import tyf_graph_projection
import tyf_polish_review
import tyf_rc_doctor


def run(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Run TYF review surfaces from one command")
    sub = parser.add_subparsers(dest="cmd", required=True)
    for name in ("graph", "concept", "continuity", "polish", "doctor"):
        p = sub.add_parser(name)
        p.add_argument("work", nargs="?", default=None)
        if name == "graph":
            p.add_argument("--sqlite", action="store_true")
    args = parser.parse_args(argv)
    if args.cmd == "graph":
        argv2 = [args.work] if args.work else []
        if args.sqlite:
            argv2.append("--sqlite")
        return tyf_graph_projection.run(argv2)
    if args.cmd == "concept":
        return tyf_concept_review.run([args.work] if args.work else [])
    if args.cmd == "continuity":
        return tyf_continuity_review.run([args.work] if args.work else [])
    if args.cmd == "polish":
        return tyf_polish_review.run([args.work] if args.work else [])
    if args.cmd == "doctor":
        return tyf_rc_doctor.run([args.work] if args.work else [])
    return 2


def main() -> None:
    raise SystemExit(run(sys.argv[1:]))


if __name__ == "__main__":
    main()
