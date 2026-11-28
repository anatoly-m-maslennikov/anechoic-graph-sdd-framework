"""Index and update relation facts and their contributors."""

from __future__ import annotations

from typing import Mapping

from . import incremental_relation_state as runtime


def _fact_contributors(
    scopes: list[dict],
    registry: runtime.RelationRegistry,
    direct: Mapping[str, tuple[tuple, ...]],
) -> dict[tuple, frozenset[tuple[str, str]]]:
    contributors: dict[tuple, set[tuple[str, str]]] = {}
    for fact in runtime._scope_facts(scopes, registry):
        contributors.setdefault(fact, set()).add(("scope", fact[1]))
    for path, facts in direct.items():
        for fact in facts:
            contributors.setdefault(fact, set()).add(("atom", path))
    return {fact: frozenset(owners) for fact, owners in contributors.items()}


def _facts_by_endpoint(
    contributors: Mapping[tuple, object],
) -> dict[tuple[str, str], frozenset[tuple]]:
    indexed: dict[tuple[str, str], set[tuple]] = {}
    for fact in contributors:
        for endpoint in (fact[:2], fact[3:]):
            indexed.setdefault(endpoint, set()).add(fact)
    return {endpoint: frozenset(facts) for endpoint, facts in indexed.items()}


def _index_fact(
    indexed: dict[tuple[str, str], frozenset[tuple]],
    fact: tuple,
    *,
    add: bool,
) -> None:
    for endpoint in {fact[:2], fact[3:]}:
        facts = set(indexed.get(endpoint, ()))
        if add:
            facts.add(fact)
        else:
            facts.discard(fact)
        if facts:
            indexed[endpoint] = frozenset(facts)
        else:
            indexed.pop(endpoint, None)


def _refresh_support(
    support: dict[tuple[str, str], frozenset[tuple]],
    fact: tuple,
    registry: runtime.RelationRegistry,
    present: set[tuple[str, str]],
    *,
    active: bool,
) -> set[tuple[str, str]]:
    """Replace this fact's support edges without scanning unrelated facts."""
    inverse = registry.inverse.get(fact[2])
    if inverse is None:
        return set()
    reverse = (fact[3], fact[4], inverse, fact[0], fact[1])
    affected: set[tuple[str, str]] = set()
    for owner in (fact[:2], reverse[:2]):
        before = support.get(owner)
        if before is None:
            continue
        edges = set(before)
        edges.discard((*fact, False))
        edges.discard((*reverse, True))
        if edges:
            support[owner] = frozenset(edges)
        else:
            support.pop(owner, None)
        if before != frozenset(edges):
            affected.add(owner)
    for owner, edges in (
        runtime._support_for_fact(fact, registry, present).items()
        if active
        else ()
    ):
        before = support.get(owner, frozenset())
        current = set(before)
        current.update(edges)
        support[owner] = frozenset(current)
        if before != support[owner]:
            affected.add(owner)
    return affected


def _duplicate_membership(
    atoms: list[dict],
) -> tuple[frozenset[str], frozenset[str]]:
    paths_by_ref: dict[str, set[str]] = {}
    first_paths: dict[str, str] = {}
    for row in atoms:
        ref, path = row.get("ref"), row.get("source_path")
        if isinstance(ref, str) and isinstance(path, str):
            paths_by_ref.setdefault(ref, set()).add(path)
            first_paths.setdefault(ref, path)
    duplicate_refs = frozenset(
        ref for ref, paths in paths_by_ref.items() if len(paths) > 1
    )
    return (
        frozenset(
            path
            for ref, paths in paths_by_ref.items()
            if ref in duplicate_refs
            for path in paths
            if path != first_paths[ref]
        ),
        duplicate_refs,
    )


def _add(
    outgoing: dict[tuple[str, str], set[tuple]],
    fact: tuple,
    inverse: Mapping[str, str],
) -> set[tuple[str, str]]:
    affected = {fact[:2]}
    outgoing.setdefault(fact[:2], set()).add((*fact, False))
    if fact[2] in inverse:
        reverse = (fact[3], fact[4], inverse[fact[2]], fact[0], fact[1])
        outgoing.setdefault(reverse[:2], set()).add((*reverse, True))
        affected.add(reverse[:2])
    return affected


def _remove(
    outgoing: dict[tuple[str, str], set[tuple]],
    fact: tuple,
    inverse: Mapping[str, str],
) -> set[tuple[str, str]]:
    affected = {fact[:2]}
    outgoing.get(fact[:2], set()).discard((*fact, False))
    if fact[2] in inverse:
        reverse = (fact[3], fact[4], inverse[fact[2]], fact[0], fact[1])
        outgoing.get(reverse[:2], set()).discard((*reverse, True))
        affected.add(reverse[:2])
    return affected


def _delta_edge(
    outgoing: dict[tuple[str, str], frozenset[tuple]],
    fact: tuple,
    inverse: Mapping[str, str],
    *,
    add: bool,
) -> set[tuple[str, str]]:
    affected = {fact[:2]}
    edges = set(outgoing.get(fact[:2], ()))
    (edges.add if add else edges.discard)((*fact, False))
    if edges:
        outgoing[fact[:2]] = frozenset(edges)
    else:
        outgoing.pop(fact[:2], None)
    if fact[2] in inverse:
        reverse = (fact[3], fact[4], inverse[fact[2]], fact[0], fact[1])
        edges = set(outgoing.get(reverse[:2], ()))
        (edges.add if add else edges.discard)((*reverse, True))
        if edges:
            outgoing[reverse[:2]] = frozenset(edges)
        else:
            outgoing.pop(reverse[:2], None)
        affected.add(reverse[:2])
    return affected


def _full_rows(
    raw_by_path, graph_paths, aliases, registry, outgoing, support, scopes
):
    atom_rows = {}
    for path, row in raw_by_path.items():
        graph = path in graph_paths
        facts = (
            tuple(
                sorted(
                    (
                        *outgoing.get((runtime.ATOM, row["ref"]), ()),
                        *support.get((runtime.ATOM, row["ref"]), ()),
                    )
                )
            )
            if graph
            else runtime._carrier_facts(row, aliases, registry)
        )
        materialized = runtime._materialized_atom(row, facts, graph=graph)
        if materialized is not None:
            atom_rows[path] = materialized
    scope_rows = {}
    for row in scopes:
        facts = tuple(
            sorted(
                (
                    *outgoing.get((runtime.SCOPE, row["name"]), ()),
                    *support.get((runtime.SCOPE, row["name"]), ()),
                )
            )
        )
        materialized = runtime._materialized_row(runtime.SCOPE, row, facts)
        if materialized is not None:
            scope_rows[row["name"]] = materialized
    return atom_rows, scope_rows
