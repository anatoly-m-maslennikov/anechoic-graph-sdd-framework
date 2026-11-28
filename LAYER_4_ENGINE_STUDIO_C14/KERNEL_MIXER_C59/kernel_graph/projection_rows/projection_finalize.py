"""Finalize projection snapshots and report changed rows."""

from .projection_types import ProjectionSnapshot, ProjectionChange
from .projection_keys import _changed_reference
from .public_rows import _snapshot_atom


def _finish_delta(
    previous,
    current,
    next_graph,
    header_schema,
    content_schema,
    delta,
    changed_atoms,
    deleted_atoms,
    deleted_scopes,
    inserted_atoms,
    inserted_scopes,
    graph_rows,
):
    for key in current.atoms if delta is None else changed_atoms:
        if key in current.atoms:
            current.atoms[key] = _snapshot_atom(current.atoms[key])
    current = ProjectionSnapshot(
        current.atoms,
        current.scopes,
        next_graph,
        header_schema,
        content_schema,
        current.atom_sources,
    )
    reference = _changed_reference(previous, current, changed_atoms)
    return current, ProjectionChange(
        deleted_atoms,
        deleted_scopes,
        inserted_atoms,
        inserted_scopes,
        graph_rows,
        reference,
    )
