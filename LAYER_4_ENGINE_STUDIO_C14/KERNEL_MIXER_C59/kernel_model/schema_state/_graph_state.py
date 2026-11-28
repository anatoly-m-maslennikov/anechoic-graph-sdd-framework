"""Build Graph snapshots and apply in-memory contributions."""

from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Iterable, Mapping
from typing import Annotated, TypeVar

from pydantic import ConfigDict, WrapValidator
from pydantic.dataclasses import dataclass

from .index_delta import MaterializationDelta

_EDGE_KEYS = (
    "source_kind",
    "source_ref",
    "target_kind",
    "target_ref",
    "relation_type",
    "derived",
)

_EDGE_FIELDS = frozenset(_EDGE_KEYS)

Edge = tuple[str, str, str, str, str, bool]

Reference = tuple[str, str]

T = TypeVar("T")


def _preserve(value, handler):
    handler(value)
    return value


@dataclass(
    config=ConfigDict(strict=True, extra="forbid", hide_input_in_errors=True),
    frozen=True,
)
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


def edge_records(
    rows: Iterable[Mapping[str, object]],
) -> list[tuple[str, str, str, str, str, bool]]:
    records = []
    for row in rows:
        if row.get("_graph_excluded"):
            continue
        edges = row.get("relation_edges_json", [])
        if not isinstance(edges, list):
            raise ValueError("relation_edges_json must be a list")
        for edge in edges:
            if not isinstance(edge, Mapping) or set(edge) != _EDGE_FIELDS:
                raise ValueError(
                    "relation edge must contain exactly the declared fields"
                )
            relation_type = edge["relation_type"]
            endpoint_values = (
                edge["source_kind"],
                edge["source_ref"],
                edge["target_kind"],
                edge["target_ref"],
            )
            if (
                not isinstance(relation_type, str)
                or not relation_type
                or not all(isinstance(value, str) for value in endpoint_values)
            ):
                raise ValueError(
                    (
                        "relation edge endpoints and type must be non-empty "
                        "strings"
                    )
                )
            if not all(endpoint_values) or type(edge["derived"]) is not bool:
                raise ValueError(
                    (
                        "relation edge endpoints must be non-empty and "
                        "derived must be boolean"
                    )
                )
            records.append((*endpoint_values, relation_type, edge["derived"]))
    return records


def _contribution_counts(
    atoms: Iterable[Mapping[str, object]],
    scopes: Iterable[Mapping[str, object]],
    edges: Iterable[Edge],
) -> tuple[Counter[Reference], Counter[Edge]]:
    "Count node and edge contributions without collapsing duplicate source facts."
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
    for (
        source_kind,
        source_ref,
        target_kind,
        target_ref,
        _,
        _,
    ) in edge_counts.elements():
        references[(source_kind, source_ref)] += 1
        references[(target_kind, target_ref)] += 1
    return references, edge_counts


def graph_state(
    atom_rows: Iterable[Mapping[str, object]],
    scope_rows: Iterable[Mapping[str, object]],
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
    tables = {
        relation_type: quote_identifier(f"edge_{index}")
        for index, relation_type in enumerate(sorted(by_type), start=1)
    }
    return GraphState(
        frozenset(reference_counts),
        {name: frozenset(records) for name, records in by_type.items()},
        tables,
        dict(reference_counts),
        dict(edge_counts),
    )


def _adjust_counts(
    previous: Mapping[T, int],
    old: Mapping[T, int],
    new: Mapping[T, int],
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
    previous: GraphState,
    delta: MaterializationDelta,
    relation_types: set[str],
) -> tuple[GraphState, set[Reference], set[Reference], set[Edge], set[Edge]]:
    "Build a next graph state from only the materialized owners in one delta."
    if set(previous.edges) != relation_types:
        raise ValueError(
            "relation type layout changed; full graph rebuild is required"
        )
    references, relations = _updated_counts(previous, delta)
    reference_counts, removed_references, added_references = references
    edge_counts, removed_edges, added_edges = relations
    edges = dict(previous.edges)
    for relation_type in {edge[4] for edge in removed_edges | added_edges}:
        records = set(previous.edges[relation_type])
        records.difference_update(
            edge for edge in removed_edges if edge[4] == relation_type
        )
        records.update(
            edge for edge in added_edges if edge[4] == relation_type
        )
        edges[relation_type] = frozenset(records)
    candidate = GraphState(
        frozenset(reference_counts),
        edges,
        dict(previous.tables),
        reference_counts,
        edge_counts,
    )
    return (
        candidate,
        removed_references,
        added_references,
        removed_edges,
        added_edges,
    )


def _updated_counts(previous, delta):
    old_edges = edge_records(
        [*delta.old_atoms.values(), *delta.old_scopes.values()]
    )
    new_edges = edge_records(
        [*delta.new_atoms.values(), *delta.new_scopes.values()]
    )
    old_references, old_edge_counts = _contribution_counts(
        delta.old_atoms.values(),
        delta.old_scopes.values(),
        old_edges,
    )
    new_references, new_edge_counts = _contribution_counts(
        delta.new_atoms.values(),
        delta.new_scopes.values(),
        new_edges,
    )
    references = _adjust_counts(
        previous.reference_counts, old_references, new_references
    )
    relations = _adjust_counts(
        previous.edge_counts, old_edge_counts, new_edge_counts
    )
    return references, relations
