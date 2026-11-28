"""Replay the migration-pinned witness using the shared SPEC translator."""

import importlib.util
from pathlib import Path

path = (
    Path(__file__).resolve().parent.parent
    / ("first-spec-publication")
    / ("analyze.py")
)
spec = importlib.util.spec_from_file_location(
    ("spec_publication_analyzer"), path
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

if __name__ == "__main__":
    raise SystemExit(
        module.main(pinned=True, case=("migration-pinned-spec-publication"))
    )
