"""Generate Python classes from the Current ANECHOIC_MODEL Declarations."""

import argparse
from pathlib import Path
import sys

PROGRAMMATIC = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

# fmt: off
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.\
    FEATURE_TOOLS__shared import (  # noqa: E402
    atomic_write, resolve_project,
)
# fmt: on
# fmt: off
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.\
    ADAPTERS_C30__shared import (  # noqa: E402
        read_current_model_carriers,
    )
# fmt: on
# fmt: off
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_MODEL_C51.\
    FEATURE_FORMAL_MODEL_GENERATOR.model_class_assembly import (  # noqa: E402
        build_model_class_source,
    )
# fmt: on


def build_project_model(project_root: Path) -> str:
    selection = resolve_project(project_root)
    authority = {
        selection.root / unit["authority_path"]
        for unit in selection.structure["scope_units"]
    }
    carriers = read_current_model_carriers(
        selection.control_root,
        selection.root,
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
