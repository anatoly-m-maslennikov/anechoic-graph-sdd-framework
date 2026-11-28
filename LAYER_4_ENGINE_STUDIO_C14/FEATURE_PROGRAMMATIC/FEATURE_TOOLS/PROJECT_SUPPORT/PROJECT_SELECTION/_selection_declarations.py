"""Validate selected declarations and retain source provenance."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from . import project_selection as runtime


def _selected_declarations(
    root: Path,
    relative: Path,
    control: Path,
    reader: runtime.ReadContext,
    indexed_declarations: runtime.ScopeUnitDeclarations | None,
    project_name: str,
) -> runtime.ScopeUnitDeclarations:
    declarations = indexed_declarations
    if declarations is None:
        declarations = runtime.read_scope_unit_declarations(
            root, relative, reader=reader
        )
    elif (
        not isinstance(declarations, runtime.ScopeUnitDeclarations)
        or not declarations.paths
        or any(
            not path.is_absolute() or not path.is_relative_to(control)
            for path in declarations.paths
        )
    ):
        raise runtime.ProjectSelectionError(
            "Indexed declarations belong to another Project"
        )
    if declarations.root.name != project_name:
        raise runtime.ProjectSelectionError(
            "Project root declaration contradicts Project Settings name"
        )
    return declarations


def _selection_provenance(
    root: Path,
    settings_path: Path,
    settings: dict[str, Any],
    reader: runtime.ReadContext,
    declarations: runtime.ScopeUnitDeclarations,
) -> dict[str, Any]:
    provenance = {
        path.relative_to(root).as_posix(): {
            "sha256": reader.fingerprints[str(path)],
            "size": reader.sizes[str(path)],
            "schema_version": document.get("schema_version"),
        }
        for path, document in ((settings_path, settings),)
    }
    provenance.update(
        {path: dict(pin) for path, pin in declarations.source_pins.items()}
    )
    return provenance
