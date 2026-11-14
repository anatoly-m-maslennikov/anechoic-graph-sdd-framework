"""Generate Python classes from the Current CAPRMEDIO_MODEL Declarations."""

import argparse
from pathlib import Path
import sys

if not __package__:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

PROGRAMMATIC = Path(__file__).resolve().parents[2]
sys.path[:0] = [
    str(PROGRAMMATIC / "FEATURE_TOOLS"),
    str(PROGRAMMATIC / "FEATURE_TOOLS" / "GENERATE_ENTITY_GRAPH"),
]

from artifact_metadata import atomic_write  # noqa: E402
from current_entity_sources import read_current_model_carriers  # noqa: E402
from project_selection import resolve_project  # noqa: E402
from FEATURE_MODEL.FEATURE_FORMAL_MODEL_GENERATOR.model_class_assembly import (  # noqa: E402
    build_model_class_source,
)


def build_project_model(project_root: Path) -> str:
    selection = resolve_project(project_root)
    authority = {selection.root / unit["authority_path"] for unit in selection.structure["scope_units"]}
    carriers = read_current_model_carriers(
        selection.control_root, selection.root,
        include_source=lambda path: path.parent.parent in authority,
    )
    return build_model_class_source(carriers)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        source = build_project_model(args.project_root)
        atomic_write(args.output.absolute(), source, mode=0o644)
    except (OSError, RuntimeError, TypeError, ValueError) as error:
        print(f"Cannot build Model: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
