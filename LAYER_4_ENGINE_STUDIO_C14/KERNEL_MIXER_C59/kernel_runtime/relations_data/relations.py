"""Materialize authored references and declared inverse bindings."""

from __future__ import annotations

from collections.abc import Mapping
import hashlib
import sys
from typing import Any

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.\
    carriers.content.content__shared import (
        source_markdown,
    )  # fmt: skip
from ...relation_support import (
    _build_outgoing,
    _build_support,
    _support_for_fact as _support_for_fact,
)
from .relation_values import (
    _relation_name,
    _targets,
    _scope_references,
    _container,
    _edge,
    _timestamp,
)
from ...relation_registry import (
    RelationRegistry,
    _warn_colliding_uses,
    compile_relation_registry,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.\
    sources.inventory.inventory__shared import (
        canonical,
    )  # fmt: skip

ATOM = "Atom"
SCOPE = "Scope Unit"


def _graph_sources(atoms: list[dict]) -> list[dict]:
    selected = []
    seen = set()
    for atom in atoms:
        if atom.get("status_group") == "Archived":
            continue
        reference = atom.get("ref")
        if reference is not None and reference in seen:
            continue
        selected.append(atom)
        if reference is not None:
            seen.add(reference)
    return selected


def _carrier_facts(
    row: dict, aliases: Mapping[str, str], registry: RelationRegistry
) -> tuple[tuple, ...]:
    outgoing = _outgoing_facts(
        [],
        registry,
        {row["source_path"]: tuple(_atom_facts(row, aliases, registry))},
    )
    return tuple(sorted(outgoing.get((ATOM, row.get("ref")), ())))


def _materialized_atom(
    row: dict, facts: tuple[tuple, ...], *, graph: bool
) -> dict | None:
    if not graph:
        row = {
            **row,
            "_graph_excluded": True,
            "_carrier_relation_edges_json": [
                _edge(fact[:-1], fact[-1]) for fact in facts
            ],
        }
        facts = ()
    return _materialized_row(ATOM, row, facts)


def relation_registry(
    atoms: list[dict[str, Any]],
) -> tuple[set[str], dict[str, str]]:
    """Project literal Relation metadata without evaluating CFEL formulas."""
    registry = compile_relation_registry(atoms)
    _warn_colliding_uses(atoms, registry.collisions)
    return set(registry.names), dict(registry.inverse)


def _scope_facts(scopes: list[dict], registry: RelationRegistry):
    containment = _relation_name("IS_CONTAINED_BY", registry)
    for row in scopes:
        if containment and row["parent_name"]:
            relation, inverse = containment
            source = (SCOPE, row["name"])
            target = (SCOPE, row["parent_name"])
            yield (
                (*target, relation, *source)
                if inverse
                else (*source, relation, *target)
            )


def _atom_facts(
    row: dict, scope_references: Mapping[str, str], registry: RelationRegistry
):
    if row["ref"] is None:
        return
    containment = _relation_name("IS_CONTAINED_BY", registry)
    container_kind, container_ref = _container(row, scope_references)
    if (
        containment
        and container_kind is not None
        and container_ref is not None
    ):
        relation, inverse = containment
        source = (ATOM, row["ref"])
        target = (container_kind, container_ref)
        yield (
            (*target, relation, *source)
            if inverse
            else (*source, relation, *target)
        )
    relations = row["header_json"].get("relations", {})
    if not isinstance(relations, dict):
        return
    for name, values in relations.items():
        resolved = _relation_name(name, registry, row["source_path"])
        if resolved:
            relation, inverse = resolved
            for kind, ref in _targets(values, scope_references):
                source = (ATOM, row["ref"])
                target = (kind, ref)
                yield (
                    (*target, relation, *source)
                    if inverse
                    else (*source, relation, *target)
                )


def _materialized_row(
    kind: str, source: dict, facts: tuple[tuple, ...]
) -> dict | None:
    row = dict(source)
    row.pop("_project_root_header", None)
    row["relation_edges_json"] = [_edge(fact[:-1], fact[-1]) for fact in facts]
    if kind == ATOM:
        row["updated_at"] = _timestamp(row["updated_at"])
    try:
        payload = {
            key: value
            for key, value in row.items()
            if key not in {"hash", "_content_bytes"}
        }
        if "_content_bytes" in row:
            payload["content_markdown"] = source_markdown(row)
        row["hash"] = hashlib.sha256(
            canonical(payload).encode("utf-8")
        ).hexdigest()
        return row
    except (TypeError, ValueError) as error:
        path = row.get("source_path", row.get("declaration_source_path"))
        print(f"Workbench: {path}: {error}", file=sys.stderr)
        return None


def _direct_atom_facts(
    atoms: list[dict],
    scope_references: Mapping[str, str],
    registry: RelationRegistry,
    context: tuple,
    previous_atoms: Mapping[str, dict[str, Any]],
) -> dict[str, tuple[tuple, ...]]:
    result = {}
    for source in atoms:
        path = source.get("source_path")
        cached = previous_atoms.get(path) if isinstance(path, str) else None
        facts = (
            cached["direct_facts"]
            if cached is not None
            and cached["raw"] is source
            and cached.get("context") == context
            else tuple(_atom_facts(source, scope_references, registry))
        )
        if isinstance(path, str):
            result[path] = facts
    return result


def _outgoing_facts(scopes, registry, atom_direct_facts):
    return _build_outgoing(scopes, registry, atom_direct_facts, _scope_facts)


def _support_facts(atoms, scopes, registry, atom_direct_facts):
    return _build_support(
        atoms,
        scopes,
        registry,
        atom_direct_facts,
        _scope_facts,
        _support_for_fact,
    )


def _materialize_atoms(
    atoms: list[dict],
    outgoing: Mapping[tuple[str, str], set[tuple]],
    context: tuple,
    atom_direct_facts: Mapping[str, tuple[tuple, ...]],
    previous_atoms: Mapping[str, dict[str, Any]],
    support: Mapping[tuple[str, str], set[tuple]],
    graph_paths: set[str],
    aliases: Mapping[str, str],
    registry: RelationRegistry,
) -> tuple[list[dict], dict[str, dict[str, Any]]]:
    next_atoms: dict[str, dict[str, Any]] = {}
    rows = []
    for source in atoms:
        path = source.get("source_path")
        graph = path in graph_paths
        facts = _atom_outgoing(
            source, graph, outgoing, support, aliases, registry
        )
        cached = previous_atoms.get(path) if isinstance(path, str) else None
        row = (
            cached["row"]
            if cached is not None
            and cached["raw"] is source
            and cached["facts"] == facts
            and bool(cached["row"].get("_graph_excluded")) != graph
            else _materialized_atom(source, facts, graph=graph)
        )
        if row is not None:
            rows.append(row)
            if isinstance(path, str):
                next_atoms[path] = {
                    "raw": source,
                    "context": context,
                    "direct_facts": atom_direct_facts.get(path, ()),
                    "facts": facts,
                    "row": row,
                }
    return rows, next_atoms


def _atom_outgoing(source, graph, outgoing, support, aliases, registry):
    if not graph:
        return _carrier_facts(source, aliases, registry)
    return tuple(
        sorted(
            (
                *outgoing.get((ATOM, source["ref"]), ()),
                *support.get((ATOM, source["ref"]), ()),
            )
        )
    )


def materialize_with_registry(
    atoms: list[dict],
    scopes: list[dict],
    previous_atoms: Mapping[str, dict[str, Any]] | None = None,
) -> tuple[
    list[dict], list[dict], set[str], dict[str, str], dict[str, dict[str, Any]]
]:
    """Materialize an inventory and reuse unchanged Atom rows by identity."""
    graph_atoms = _graph_sources(atoms)
    registry = compile_relation_registry(graph_atoms)
    _warn_colliding_uses(graph_atoms, registry.collisions)
    scope_references = _scope_references(scopes)
    context = (
        tuple(sorted(registry.names)),
        tuple(sorted(registry.inverse.items())),
        tuple(sorted(registry.aliases.items())),
        tuple(sorted(scope_references.items())),
    )
    prior = previous_atoms or {}
    atom_direct_facts = _direct_atom_facts(
        graph_atoms, scope_references, registry, context, prior
    )
    outgoing = _outgoing_facts(scopes, registry, atom_direct_facts)
    support = _support_facts(graph_atoms, scopes, registry, atom_direct_facts)
    graph_paths = {row.get("source_path") for row in graph_atoms}
    atom_rows, next_atoms = _materialize_atoms(
        atoms,
        outgoing,
        context,
        atom_direct_facts,
        prior,
        support,
        graph_paths,
        scope_references,
        registry,
    )

    scope_rows = _materialize_scopes(scopes, outgoing, support)
    return (
        atom_rows,
        scope_rows,
        set(registry.names),
        dict(registry.inverse),
        next_atoms,
    )


def _materialize_scopes(scopes, outgoing, support):
    scope_rows = []
    for source in scopes:
        facts = tuple(
            sorted(
                (
                    *outgoing[(SCOPE, source["name"])],
                    *support.get((SCOPE, source["name"]), ()),
                )
            )
        )
        row = _materialized_row(SCOPE, source, facts)
        if row is not None:
            scope_rows.append(row)
    return scope_rows


def materialize(
    atoms: list[dict], scopes: list[dict]
) -> tuple[list[dict], list[dict]]:
    """Assign outgoing facts, then hash each row’s canonical data."""
    rows, scope_rows, _registered, _inverse, _cache = (
        materialize_with_registry(atoms, scopes)
    )
    return rows, scope_rows
