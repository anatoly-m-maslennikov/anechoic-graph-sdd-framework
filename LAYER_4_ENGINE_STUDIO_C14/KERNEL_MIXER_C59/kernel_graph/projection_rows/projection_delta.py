"""Apply the materialized source delta to the public Workbench projection."""

from __future__ import annotations


from typing import Any

from .projection_snapshot_delta import _delta_snapshot
from .projection_finalize import _finish_delta
from .projection_keys import _delta_keys
from .projection_types import ProjectionSnapshot as ProjectionSnapshot
from .projection_types import ProjectionChange as ProjectionChange
from ...graph_store import (
    apply_graph_delta,
    graph_state,
    update_graph,
)
from ...content_schema import ContentSchema
from ...header_columns import HeaderSchema
from ...index_delta import MaterializationDelta
from .public_rows import (
    SCOPE_FIELDS,
    _snapshot_atom,
    atom_fields,
    insert_public_rows,
    projected_rows,
)


def snapshot(
    atom_rows: list[dict[str, Any]],
    scope_rows: list[dict[str, Any]],
    relation_types: set[str] | None,
    header_schema: HeaderSchema,
    content_schema: ContentSchema,
    previous: ProjectionSnapshot | None = None,
    *,
    public_rows: tuple[list[dict[str, Any]], list[dict[str, Any]]]
    | None = None,
) -> ProjectionSnapshot:
    if public_rows is None:
        reuse = None
        if (
            previous is not None
            and previous.header_schema == header_schema
            and previous.content_schema == content_schema
        ):
            reuse = {
                key: (source, previous.atoms[key])
                for key, source in previous.atom_sources.items()
                if key in previous.atoms
                and previous.atoms[key].get("status_group") != "Archived"
            }
        public_rows = projected_rows(
            atom_rows,
            scope_rows,
            header_schema,
            content_schema,
            previous_atoms=reuse,
        )
    public_atoms, public_scopes = public_rows
    atom_sources = {
        (row["relative_path"], row["filename"]): source
        for row, source in zip(public_atoms, atom_rows, strict=True)
    }
    return ProjectionSnapshot(
        {(row["relative_path"], row["filename"]): row for row in public_atoms},
        {row["name"]: row for row in public_scopes},
        graph_state(atom_rows, scope_rows, relation_types),
        header_schema,
        content_schema,
        atom_sources,
    )


def _changed_keys(
    previous: dict[Any, dict[str, Any]],
    current: dict[Any, dict[str, Any]],
) -> set[Any]:
    return {
        key
        for key in set(previous) | set(current)
        if previous.get(key, {}).get("hash")
        != current.get(key, {}).get("hash")
    }


def _write_public_delta(
    connection: Any,
    previous: ProjectionSnapshot,
    current: ProjectionSnapshot,
    changed_atoms: set[tuple[str, str]] | None = None,
    changed_scopes: set[str] | None = None,
) -> tuple[set[tuple[str, str]], set[str], int, int]:
    changed_atoms = (
        changed_atoms
        if changed_atoms is not None
        else _changed_keys(previous.atoms, current.atoms)
    )
    changed_scopes = (
        changed_scopes
        if changed_scopes is not None
        else _changed_keys(previous.scopes, current.scopes)
    )
    deleted_atoms, deleted_scopes = _delete_public_rows(
        connection, previous, changed_atoms, changed_scopes
    )
    insert_public_rows(
        connection,
        "atoms",
        atom_fields(current.header_schema, current.content_schema),
        [current.atoms[key] for key in changed_atoms if key in current.atoms],
        json_fields=current.header_schema.json_names | {"header.relations"},
    )
    insert_public_rows(
        connection,
        "scope_units",
        SCOPE_FIELDS,
        [
            current.scopes[key]
            for key in changed_scopes
            if key in current.scopes
        ],
        json_fields=frozenset({"relations"}),
    )
    return changed_atoms, changed_scopes, deleted_atoms, deleted_scopes


def _prepare_delta(
    previous,
    atom_rows,
    scope_rows,
    relation_types,
    header_schema,
    content_schema,
    delta,
):
    current = (
        _delta_snapshot(previous, delta, header_schema, content_schema)
        if delta is not None
        else snapshot(
            atom_rows,
            scope_rows,
            relation_types,
            header_schema,
            content_schema,
            previous,
        )
    )
    changed_atoms, changed_scopes = (
        _changed_delta_keys(previous, current, delta)
        if delta is not None
        else (
            _changed_keys(previous.atoms, current.atoms),
            _changed_keys(previous.scopes, current.scopes),
        )
    )
    return current, changed_atoms, changed_scopes


def _update_projection_graph(
    connection, previous, current, atom_rows, scope_rows, delta, relation_types
):
    if delta is None:
        next_graph = update_graph(
            connection, previous.graph, current.graph, atom_rows, scope_rows
        )
        graph_rows = len(
            previous.graph.references ^ next_graph.references
        ) + sum(
            len(
                previous.graph.edges.get(name, frozenset())
                ^ next_graph.edges.get(name, frozenset())
            )
            for name in previous.graph.edges.keys() | next_graph.edges.keys()
        )
    else:
        next_graph, graph_rows = apply_graph_delta(
            connection, previous.graph, delta, relation_types
        )
    return next_graph, graph_rows


def _delete_public_rows(connection, previous, changed_atoms, changed_scopes):
    deleted_atoms = 0
    for path, filename in changed_atoms:
        if (path, filename) in previous.atoms:
            connection.execute(
                'DELETE FROM main.atoms WHERE "relative_path" = ? '
                "AND filename = ?",
                [path, filename],
            )
            deleted_atoms += 1
    deleted_scopes = 0
    for name in changed_scopes:
        if name in previous.scopes:
            connection.execute(
                "DELETE FROM main.scope_units WHERE name = ?", [name]
            )
            deleted_scopes += 1
    return deleted_atoms, deleted_scopes


def _changed_delta_keys(
    previous: ProjectionSnapshot,
    current: ProjectionSnapshot,
    delta: MaterializationDelta,
) -> tuple[set[tuple[str, str]], set[str]]:
    atom_keys, scope_names = _delta_keys(delta)
    return (
        {
            key
            for key in atom_keys
            if previous.atoms.get(key, {}).get("hash")
            != current.atoms.get(key, {}).get("hash")
        },
        {
            name
            for name in scope_names
            if previous.scopes.get(name, {}).get("hash")
            != current.scopes.get(name, {}).get("hash")
        },
    )


def apply(
    connection: Any,
    previous: ProjectionSnapshot,
    atom_rows: list[dict[str, Any]],
    scope_rows: list[dict[str, Any]],
    relation_types: set[str],
    header_schema: HeaderSchema,
    content_schema: ContentSchema,
    *,
    delta: MaterializationDelta | None = None,
) -> tuple[ProjectionSnapshot, ProjectionChange]:
    """Delete changed public rows, then insert replacements."""
    current, changed_atoms, changed_scopes = _prepare_delta(
        previous,
        atom_rows,
        scope_rows,
        relation_types,
        header_schema,
        content_schema,
        delta,
    )
    if (
        delta is None
        and not changed_atoms
        and not changed_scopes
        and previous.graph == current.graph
    ):
        return _unchanged_projection(current, header_schema, content_schema)
    return _apply_changed(
        connection,
        previous,
        current,
        (atom_rows, scope_rows),
        relation_types,
        (header_schema, content_schema),
        delta,
        (changed_atoms, changed_scopes),
    )


def _unchanged_projection(current, header_schema, content_schema):
    return ProjectionSnapshot(
        {key: _snapshot_atom(row) for key, row in current.atoms.items()},
        current.scopes,
        current.graph,
        header_schema,
        content_schema,
        current.atom_sources,
    ), ProjectionChange(0, 0, 0, 0, 0, None)


def _apply_changed(
    connection,
    previous,
    current,
    sources,
    relation_types,
    schemas,
    delta,
    changed,
):
    atom_rows, scope_rows = sources
    header_schema, content_schema = schemas
    changed_atoms, changed_scopes, deleted_atoms, deleted_scopes = (
        _write_public_delta(connection, previous, current, *changed)
    )
    inserted_atoms = sum(key in current.atoms for key in changed_atoms)
    inserted_scopes = sum(key in current.scopes for key in changed_scopes)
    next_graph, graph_rows = _update_projection_graph(
        connection,
        previous,
        current,
        atom_rows,
        scope_rows,
        delta,
        relation_types,
    )
    return _finish_delta(
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
    )
