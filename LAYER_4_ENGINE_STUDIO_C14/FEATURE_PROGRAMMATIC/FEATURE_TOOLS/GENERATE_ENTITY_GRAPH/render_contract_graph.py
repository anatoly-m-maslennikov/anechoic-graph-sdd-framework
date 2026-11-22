#!/usr/bin/env -S python3 -B
"""Render a source-bound formal-contract graph to standard output only.

Usage: render_contract_graph.py source-folder [--repository REPOSITORY]
"""

from __future__ import annotations

import argparse
from pathlib import Path

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.contract_graph import compose_contract_graph
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.contract_graph_render import render_contract_graph
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.current_carriers__pub import read_current_carriers
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.subject_audit_occurrences import select_model_subjects


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_folder", type=Path)
    parser.add_argument("--repository", type=Path, default=Path.cwd())
    parser.add_argument("--model-draft-manifest", type=Path,
                        help="Preview Model Drafts over their exact Current predecessors")
    args = parser.parse_args(argv)
    repository = args.repository.resolve()
    carriers = read_current_carriers(
        args.source_folder, repository, model_draft_manifest=args.model_draft_manifest,
    )
    if args.model_draft_manifest is not None:
        carriers, _ = select_model_subjects(carriers)
    rendered = render_contract_graph(compose_contract_graph(carriers))
    if args.model_draft_manifest is not None:
        print("> **Draft preview.** Model declarations are selected by the supplied manifest.\n")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
