"Trusted internal DuckPGQ mappings for the Workbench public row projection."

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable, Mapping
import hashlib
from itertools import batched
from typing import Any

from ..graph_import_projection import add_import_projection
from ..index_delta import MaterializationDelta
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.\
    sources.inventory.inventory__shared import (
        canonical,
    )  # fmt: skip
from .._graph_state import (
    _EDGE_KEYS,
    Edge,
    GraphState,
    Reference,
    graph_delta_state,
    graph_state,
    quote_identifier,
)


def _hash(payload: Mapping[str, object]) -> str:
    return hashlib.sha256(canonical(payload).encode("utf-8")).hexdigest()


def _insert_batches(
    connection: Any,
    statement: str,
    rows: Iterable[tuple[str | bool, ...]],
) -> None:
    for batch in batched(rows, 1000):
        columns = [list(column) for column in zip(*batch, strict=True)]
        connection.execute(statement, columns)


def _insert_references(
    connection: Any, references: Iterable[Reference]
) -> None:
    _insert_batches(
        connection,
        "INSERT INTO internal.reference SELECT "
        "unnest(?::VARCHAR[]), unnest(?::VARCHAR[]), unnest(?::VARCHAR[])",
        (
            (kind, ref, _hash({"kind": kind, "ref": ref}))
            for kind, ref in references
        ),
    )


def _insert_edges(connection: Any, table: str, edges: Iterable[Edge]) -> None:
    _insert_batches(
        connection,
        f"INSERT INTO internal.{table} SELECT "
        "unnest(?::VARCHAR[]), unnest(?::VARCHAR[]), unnest(?::VARCHAR[]), "
        "unnest(?::VARCHAR[]), unnest(?::VARCHAR[]), unnest(?::BOOLEAN[]), "
        "unnest(?::VARCHAR[])",
        (
            (*edge, _hash(dict(zip(_EDGE_KEYS, edge, strict=True))))
            for edge in edges
        ),
    )


def graph_relations(
    connection: Any, *, has_edges: bool
) -> dict[tuple[str, str], dict[str, list[dict[str, object]]]]:
    "Read outgoing facts from the native graph without exposing its tables."
    if not has_edges:
        return {}
    descriptions = connection.execute(
        "SELECT label FROM describe_property_graph('anechoic') "
        "WHERE NOT is_vertex_table AND schema = 'internal' ORDER BY label"
    ).fetchall()
    outgoing: dict[tuple[str, str], dict[str, list[dict[str, object]]]] = (
        defaultdict(dict)
    )
    for (relation_type,) in descriptions:
        rows = connection.execute(
            "FROM GRAPH_TABLE (anechoic "
            f"MATCH (source:Reference)-[edge:{quote_identifier(relation_type)}]->(target:Reference) "
            "COLUMNS (source.kind AS source_kind, source.ref AS source_ref, "
            "target.kind AS target_kind, target.ref AS target_ref, edge.derived AS derived)) "
            "ORDER BY source_kind, source_ref, target_kind, target_ref, derived"
        ).fetchall()
        for source_kind, source_ref, target_kind, target_ref, derived in rows:
            outgoing[(source_kind, source_ref)].setdefault(
                relation_type, []
            ).append(
                {
                    "kind": target_kind,
                    "reference": target_ref,
                    "derived": derived,
                }
            )
    return {source: dict(relations) for source, relations in outgoing.items()}


def build_graph(
    connection: Any,
    atom_rows: Iterable[Mapping[str, object]],
    scope_rows: Iterable[Mapping[str, object]],
    relation_types: set[str] | None = None,
) -> GraphState:
    "Create the disposable typed-reference graph over materialized row facts."
    state = graph_state(atom_rows, scope_rows, relation_types)
    connection.execute("CREATE SCHEMA internal")
    connection.execute(
        "CREATE TABLE internal.reference(kind VARCHAR, ref VARCHAR, hash VARCHAR NOT NULL, "
        "PRIMARY KEY(kind, ref))"
    )
    _insert_references(connection, sorted(state.references))
    for relation_type, table in state.tables.items():
        connection.execute(
            f"CREATE TABLE internal.{table}(source_kind VARCHAR, source_ref VARCHAR, "
            "target_kind VARCHAR, target_ref VARCHAR, relation_type VARCHAR NOT NULL, "
            "derived BOOLEAN NOT NULL, hash VARCHAR NOT NULL)"
        )
        _insert_edges(connection, table, state.edges[relation_type])
    register_graph(connection, state)
    columns = ", ".join(_EDGE_KEYS)
    sources = [
        f"SELECT {columns} FROM internal.{table}"
        for table in state.tables.values()
    ]
    if not sources:
        sources = [
            "SELECT NULL::VARCHAR AS source_kind, NULL::VARCHAR AS source_ref, "
            "NULL::VARCHAR AS target_kind, NULL::VARCHAR AS target_ref, "
            "NULL::VARCHAR AS relation_type, NULL::BOOLEAN AS derived WHERE FALSE"
        ]
    connection.execute(
        "CREATE OR REPLACE VIEW main.relations AS "
        + " UNION ALL ".join(sources)
    )
    return state


def _check_native_imports(connection: Any, state: GraphState) -> None:
    if (
        any(
            records and name.casefold() == "imports"
            for name, records in state.edges.items()
        )
        and connection.execute(
            "SELECT 1 FROM information_schema.tables WHERE table_catalog = current_database() "
            "AND table_schema = 'main' AND table_name = 'import_nodes'"
        ).fetchone()
    ):
        raise ValueError(
            (
                "Native IMPORTS relations conflict with realization Imports "
                "graph label"
            )
        )


def register_graph(connection: Any, state: GraphState) -> None:
    """Register the current Atom graph and any published import projection."""
    _check_native_imports(connection, state)
    vertices = ["internal.reference LABEL Reference"]
    projected_edges: list[str] = []
    add_import_projection(connection, vertices, projected_edges)
    edges = [
        f"internal.{table} SOURCE KEY(source_kind, source_ref) "
        "REFERENCES internal.reference(kind, ref) "
        "DESTINATION KEY(target_kind, target_ref) REFERENCES internal.reference(kind, ref) "
        f"LABEL {quote_identifier(relation_type)}"
        for relation_type, table in state.tables.items()
        if not (projected_edges and relation_type.casefold() == "imports")
    ]
    edges.extend(projected_edges)
    sql = (
        "CREATE PROPERTY GRAPH anechoic VERTEX TABLES ("
        + ", ".join(vertices)
        + ")"
    )
    if edges:
        sql += " EDGE TABLES (" + ", ".join(edges) + ")"
    connection.execute(sql)


def update_graph(
    connection: Any,
    previous: GraphState,
    current: GraphState,
    atom_rows: Iterable[Mapping[str, object]],
    scope_rows: Iterable[Mapping[str, object]],
) -> GraphState:
    "Apply changed graph facts; a changed relation type layout needs a new graph declaration."
    _check_native_imports(connection, current)
    if set(previous.edges) != set(current.edges):
        connection.execute("DROP PROPERTY GRAPH anechoic")
        connection.execute("DROP SCHEMA internal CASCADE")
        return build_graph(
            connection, atom_rows, scope_rows, set(current.edges)
        )
    for relation_type, table in current.tables.items():
        removed = previous.edges[relation_type] - current.edges[relation_type]
        if removed:
            connection.executemany(
                f"DELETE FROM internal.{table} WHERE hash = ?",
                [
                    (_hash(dict(zip(_EDGE_KEYS, edge, strict=False))),)
                    for edge in removed
                ],
            )
    for kind, ref in previous.references - current.references:
        connection.execute(
            "DELETE FROM internal.reference WHERE kind = ? AND ref = ?",
            [kind, ref],
        )
    _insert_references(connection, current.references - previous.references)
    for relation_type, table in current.tables.items():
        _insert_edges(
            connection,
            table,
            current.edges[relation_type] - previous.edges[relation_type],
        )
    return current


def apply_graph_delta(
    connection: Any,
    previous: GraphState,
    delta: MaterializationDelta,
    relation_types: set[str],
) -> tuple[GraphState, int]:
    "Apply one materialized graph delta without scanning the unchanged graph."
    (
        candidate,
        removed_references,
        added_references,
        removed_edges,
        added_edges,
    ) = graph_delta_state(
        previous,
        delta,
        relation_types,
    )
    _check_native_imports(connection, candidate)
    for edge in removed_edges:
        table = candidate.tables[edge[4]]
        connection.execute(
            f"DELETE FROM internal.{table} WHERE hash = ?",
            [_hash(dict(zip(_EDGE_KEYS, edge, strict=False)))],
        )
    for kind, ref in removed_references:
        connection.execute(
            "DELETE FROM internal.reference WHERE kind = ? AND ref = ?",
            [kind, ref],
        )
    for kind, ref in added_references:
        connection.execute(
            "INSERT INTO internal.reference VALUES (?, ?, ?)",
            [kind, ref, _hash({"kind": kind, "ref": ref})],
        )
    for edge in added_edges:
        table = candidate.tables[edge[4]]
        connection.execute(
            f"INSERT INTO internal.{table} VALUES (?, ?, ?, ?, ?, ?, ?)",
            [*edge, _hash(dict(zip(_EDGE_KEYS, edge, strict=False)))],
        )
    return candidate, len(removed_references) + len(added_references) + len(
        removed_edges
    ) + len(added_edges)
