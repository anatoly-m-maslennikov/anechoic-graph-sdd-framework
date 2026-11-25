
"""Trusted internal DuckPGQ mappings for the Workbench public row projection."""

from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Iterable, Mapping
from pydantic import ConfigDict, WrapValidator
from pydantic.dataclasses import dataclass
import hashlib
from typing import Annotated, Any, TypeVar

from .graph_import_projection import add_import_projection
from .index_delta import MaterializationDelta
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import canonical


_EDGE_KEYS = (
    "source_kind", "source_ref", "target_kind", "target_ref", "relation_type", "derived",
)
_EDGE_FIELDS = frozenset(_EDGE_KEYS)
Edge = tuple[str, str, str, str, str, bool]
Reference = tuple[str, str]
T = TypeVar("T")


def _preserve(value, handler):
    handler(value)
    return value


@dataclass(config=ConfigDict(strict=True, extra="forbid", hide_input_in_errors=True), frozen=True)
class GraphState:
    references: Annotated[frozenset[Reference], WrapValidator(_preserve)]
    edges: Annotated[dict[str, frozenset[Edge]], WrapValidator(_preserve)]
    tables: Annotated[dict[str, str], WrapValidator(_preserve)]
    reference_counts: Annotated[dict[Reference, int], WrapValidator(_preserve)]
    edge_counts: Annotated[dict[Edge, int], WrapValidator(_preserve)]


def quote_identifier(name: str) -> str:
    if not isinstance(name, str) or not name or "\x00" in name:
        raise ValueError("invalid generated identifier")
    return '"' + name.replace('"', '""') + '"'


def _hash(payload: Mapping[str, object]) -> str:
    return hashlib.sha256(canonical(payload).encode("utf-8")).hexdigest()


def edge_records(rows: Iterable[Mapping[str, object]]) -> list[tuple[str, str, str, str, str, bool]]:
    records = []
    for row in rows:
        if row.get("_graph_excluded"):
            continue
        edges = row.get("relation_edges_json", [])
        if not isinstance(edges, list):
            raise ValueError("relation_edges_json must be a list")
        for edge in edges:
            if not isinstance(edge, Mapping) or set(edge) != _EDGE_FIELDS:
                raise ValueError("relation edge must contain exactly the declared fields")
            relation_type = edge["relation_type"]
            endpoint_values = (edge["source_kind"], edge["source_ref"], edge["target_kind"], edge["target_ref"])
            if not isinstance(relation_type, str) or not relation_type or not all(isinstance(value, str) for value in endpoint_values):
                raise ValueError("relation edge endpoints and type must be non-empty strings")
            if not all(endpoint_values) or type(edge["derived"]) is not bool:
                raise ValueError("relation edge endpoints must be non-empty and derived must be boolean")
            records.append((*endpoint_values, relation_type, edge["derived"]))
    return records


def _contribution_counts(
    atoms: Iterable[Mapping[str, object]], scopes: Iterable[Mapping[str, object]], edges: Iterable[Edge],
) -> tuple[Counter[Reference], Counter[Edge]]:
    """Count node and edge contributions without collapsing duplicate source facts."""
    references: Counter[Reference] = Counter()
    for row in atoms:
        if row.get("_graph_excluded"):
            continue
        references.update(row.get("_graph_references", ()))
        if isinstance(ref := row.get("ref"), str):
            references[("Atom", ref)] += 1
    for row in scopes:
        if isinstance(name := row.get("name"), str):
            references[("Scope Unit", name)] += 1
    edge_counts: Counter[Edge] = Counter(edges)
    for source_kind, source_ref, target_kind, target_ref, _, _ in edge_counts.elements():
        references[(source_kind, source_ref)] += 1
        references[(target_kind, target_ref)] += 1
    return references, edge_counts


def graph_relations(connection: Any, *, has_edges: bool) -> dict[tuple[str, str], dict[str, list[dict[str, object]]]]:
    """Read outgoing facts from the native graph without exposing its tables."""
    if not has_edges:
        return {}
    descriptions = connection.execute(
        "SELECT label FROM describe_property_graph('anechoic') "
        "WHERE NOT is_vertex_table AND schema = 'internal' ORDER BY label"
    ).fetchall()
    outgoing: dict[tuple[str, str], dict[str, list[dict[str, object]]]] = defaultdict(dict)
    for (relation_type,) in descriptions:
        rows = connection.execute(
            "FROM GRAPH_TABLE (anechoic "
            f"MATCH (source:Reference)-[edge:{quote_identifier(relation_type)}]->(target:Reference) "
            "COLUMNS (source.kind AS source_kind, source.ref AS source_ref, "
            "target.kind AS target_kind, target.ref AS target_ref, edge.derived AS derived)) "
            "ORDER BY source_kind, source_ref, target_kind, target_ref, derived"
        ).fetchall()
        for source_kind, source_ref, target_kind, target_ref, derived in rows:
            outgoing[(source_kind, source_ref)].setdefault(relation_type, []).append({
                "kind": target_kind,
                "reference": target_ref,
                "derived": derived,
            })
    return {source: dict(relations) for source, relations in outgoing.items()}


def graph_state(
    atom_rows: Iterable[Mapping[str, object]], scope_rows: Iterable[Mapping[str, object]],
    relation_types: set[str] | None = None,
) -> GraphState:
    """Describe the graph facts without changing the database."""
    atoms, scopes = list(atom_rows), list(scope_rows)
    edges = edge_records([*atoms, *scopes])
    reference_counts, edge_counts = _contribution_counts(atoms, scopes, edges)

    by_type: dict[str, set[Edge]] = defaultdict(set)
    for edge in edge_counts:
        by_type[edge[4]].add(edge)
    if relation_types is not None:
        for relation_type in relation_types:
            by_type[relation_type]
    tables = {relation_type: quote_identifier(f"edge_{index}")
              for index, relation_type in enumerate(sorted(by_type), start=1)}
    return GraphState(
        frozenset(reference_counts), {name: frozenset(records) for name, records in by_type.items()}, tables,
        dict(reference_counts), dict(edge_counts),
    )


def build_graph(
    connection: Any, atom_rows: Iterable[Mapping[str, object]], scope_rows: Iterable[Mapping[str, object]],
    relation_types: set[str] | None = None,
) -> GraphState:
    """Create the disposable typed-reference graph over materialized row facts."""
    state = graph_state(atom_rows, scope_rows, relation_types)
    connection.execute("CREATE SCHEMA internal")
    connection.execute(
        "CREATE TABLE internal.reference(kind VARCHAR, ref VARCHAR, hash VARCHAR NOT NULL, "
        "PRIMARY KEY(kind, ref))"
    )
    if state.references:
        connection.executemany(
            "INSERT INTO internal.reference VALUES (?, ?, ?)",
        [(kind, ref, _hash({"kind": kind, "ref": ref})) for kind, ref in sorted(state.references)],
        )
    for relation_type, table in state.tables.items():
        connection.execute(
            f"CREATE TABLE internal.{table}(source_kind VARCHAR, source_ref VARCHAR, "
            "target_kind VARCHAR, target_ref VARCHAR, relation_type VARCHAR NOT NULL, "
            "derived BOOLEAN NOT NULL, hash VARCHAR NOT NULL)"
        )
        if state.edges[relation_type]:
            connection.executemany(
                f"INSERT INTO internal.{table} VALUES (?, ?, ?, ?, ?, ?, ?)",
                [(*edge, _hash(dict(zip(_EDGE_KEYS, edge)))) for edge in state.edges[relation_type]],
            )
    register_graph(connection, state)
    columns = ", ".join(_EDGE_KEYS)
    sources = [f"SELECT {columns} FROM internal.{table}" for table in state.tables.values()]
    if not sources:
        sources = ["SELECT NULL::VARCHAR AS source_kind, NULL::VARCHAR AS source_ref, "
                   "NULL::VARCHAR AS target_kind, NULL::VARCHAR AS target_ref, "
                   "NULL::VARCHAR AS relation_type, NULL::BOOLEAN AS derived WHERE FALSE"]
    connection.execute("CREATE OR REPLACE VIEW main.relations AS " + " UNION ALL ".join(sources))
    return state


def register_graph(connection: Any, state: GraphState) -> None:
    """Register the current Atom graph and any published import projection."""
    vertices = ["internal.reference LABEL Reference"]
    edges = [
        f"internal.{table} SOURCE KEY(source_kind, source_ref) "
        "REFERENCES internal.reference(kind, ref) "
        "DESTINATION KEY(target_kind, target_ref) REFERENCES internal.reference(kind, ref) "
        f"LABEL {quote_identifier(relation_type)}"
        for relation_type, table in state.tables.items()
    ]
    add_import_projection(connection, vertices, edges)
    sql = "CREATE PROPERTY GRAPH anechoic VERTEX TABLES (" + ", ".join(vertices) + ")"
    if edges:
        sql += " EDGE TABLES (" + ", ".join(edges) + ")"
    connection.execute(sql)


def update_graph(
    connection: Any, previous: GraphState, current: GraphState,
    atom_rows: Iterable[Mapping[str, object]], scope_rows: Iterable[Mapping[str, object]],
) -> GraphState:
    """Apply changed graph facts; a changed relation type layout needs a new graph declaration."""
    if set(previous.edges) != set(current.edges):
        connection.execute("DROP PROPERTY GRAPH anechoic")
        connection.execute("DROP SCHEMA internal CASCADE")
        return build_graph(connection, atom_rows, scope_rows, set(current.edges))
    for relation_type, table in current.tables.items():
        removed = previous.edges[relation_type] - current.edges[relation_type]
        if removed:
            connection.executemany(
                f"DELETE FROM internal.{table} WHERE hash = ?",
                [(_hash(dict(zip(_EDGE_KEYS, edge))),) for edge in removed],
            )
    for kind, ref in previous.references - current.references:
        connection.execute("DELETE FROM internal.reference WHERE kind = ? AND ref = ?", [kind, ref])
    for kind, ref in current.references - previous.references:
        connection.execute(
            "INSERT INTO internal.reference VALUES (?, ?, ?)",
            [kind, ref, _hash({"kind": kind, "ref": ref})],
        )
    for relation_type, table in current.tables.items():
        added = current.edges[relation_type] - previous.edges[relation_type]
        if added:
            connection.executemany(
                f"INSERT INTO internal.{table} VALUES (?, ?, ?, ?, ?, ?, ?)",
                [(*edge, _hash(dict(zip(_EDGE_KEYS, edge)))) for edge in added],
            )
    return current


def _adjust_counts(
    previous: Mapping[T, int], old: Mapping[T, int], new: Mapping[T, int],
) -> tuple[dict[T, int], set[T], set[T]]:
    """Return copy-on-write counts and entries whose presence changed."""
    candidate = dict(previous)
    removed: set[T] = set()
    added: set[T] = set()
    for value in set(old) | set(new):
        before = candidate.get(value, 0)
        after = before - old.get(value, 0) + new.get(value, 0)
        if after < 0:
            raise ValueError("graph contribution count underflow")
        if after:
            candidate[value] = after
        else:
            candidate.pop(value, None)
        if before and not after:
            removed.add(value)
        elif after and not before:
            added.add(value)
    return candidate, removed, added


def graph_delta_state(
    previous: GraphState, delta: MaterializationDelta, relation_types: set[str],
) -> tuple[GraphState, set[Reference], set[Reference], set[Edge], set[Edge]]:
    """Build a next graph state from only the materialized owners in one delta."""
    if set(previous.edges) != relation_types:
        raise ValueError("relation type layout changed; full graph rebuild is required")
    old_edges = edge_records([*delta.old_atoms.values(), *delta.old_scopes.values()])
    new_edges = edge_records([*delta.new_atoms.values(), *delta.new_scopes.values()])
    old_references, old_edge_counts = _contribution_counts(
        delta.old_atoms.values(), delta.old_scopes.values(), old_edges,
    )
    new_references, new_edge_counts = _contribution_counts(
        delta.new_atoms.values(), delta.new_scopes.values(), new_edges,
    )
    reference_counts, removed_references, added_references = _adjust_counts(
        previous.reference_counts, old_references, new_references,
    )
    edge_counts, removed_edges, added_edges = _adjust_counts(
        previous.edge_counts, old_edge_counts, new_edge_counts,
    )
    edges = dict(previous.edges)
    for relation_type in {edge[4] for edge in removed_edges | added_edges}:
        records = set(previous.edges[relation_type])
        records.difference_update(edge for edge in removed_edges if edge[4] == relation_type)
        records.update(edge for edge in added_edges if edge[4] == relation_type)
        edges[relation_type] = frozenset(records)
    candidate = GraphState(
        frozenset(reference_counts), edges, dict(previous.tables), reference_counts, edge_counts,
    )
    return candidate, removed_references, added_references, removed_edges, added_edges


def apply_graph_delta(
    connection: Any, previous: GraphState, delta: MaterializationDelta, relation_types: set[str],
) -> tuple[GraphState, int]:
    """Apply one materialized graph delta without scanning the unchanged graph."""
    candidate, removed_references, added_references, removed_edges, added_edges = graph_delta_state(
        previous, delta, relation_types,
    )
    for edge in removed_edges:
        table = candidate.tables[edge[4]]
        connection.execute(
            f"DELETE FROM internal.{table} WHERE hash = ?", [_hash(dict(zip(_EDGE_KEYS, edge)))],
        )
    for kind, ref in removed_references:
        connection.execute("DELETE FROM internal.reference WHERE kind = ? AND ref = ?", [kind, ref])
    for kind, ref in added_references:
        connection.execute(
            "INSERT INTO internal.reference VALUES (?, ?, ?)",
            [kind, ref, _hash({"kind": kind, "ref": ref})],
        )
    for edge in added_edges:
        table = candidate.tables[edge[4]]
        connection.execute(
            f"INSERT INTO internal.{table} VALUES (?, ?, ?, ?, ?, ?, ?)",
            [*edge, _hash(dict(zip(_EDGE_KEYS, edge)))],
        )
    return candidate, len(removed_references) + len(added_references) + len(removed_edges) + len(added_edges)
