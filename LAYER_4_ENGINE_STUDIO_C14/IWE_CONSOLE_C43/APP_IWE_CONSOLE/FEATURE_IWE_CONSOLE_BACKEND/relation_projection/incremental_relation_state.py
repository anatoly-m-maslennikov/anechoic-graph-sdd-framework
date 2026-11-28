"""Copy-on-write relation materialization for an incremental source batch."""

from __future__ import annotations

from typing import Mapping

from ._relation_fact_index import (
    _fact_contributors as _fact_contributors,
    _full_rows,
    _facts_by_endpoint as _facts_by_endpoint,
    _index_fact as _index_fact,
    _refresh_support as _refresh_support,
    _duplicate_membership as _duplicate_membership,
    _add as _add,
    _remove as _remove,
    _delta_edge as _delta_edge,
)

from pydantic import ConfigDict, InstanceOf
from pydantic.dataclasses import dataclass

from KERNEL_MIXER_C59.KERNEL_MIXER_C59__shared import (
    ATOM as ATOM,
    SCOPE as SCOPE,
    _atom_facts,
    _materialized_row as _materialized_row,
    _scope_facts as _scope_facts,
    _scope_references,
    _support_facts,
    _support_for_fact as _support_for_fact,
    _graph_sources,
    _carrier_facts as _carrier_facts,
    _materialized_atom as _materialized_atom,
)
from KERNEL_MIXER_C59.KERNEL_MIXER_C59__shared import (
    RelationRegistry,
    RegistryCompilation,
    RegistryContribution,
    _unambiguous_aliases,
    _warn_colliding_uses,
    compile_registry,
    registry_contribution,
    registry_from_contributions,
)


@dataclass(
    frozen=True,
    config=ConfigDict(
        strict=True, extra="forbid", arbitrary_types_allowed=True
    ),
)
class RelationState:
    raw_by_path: InstanceOf[dict[str, dict]]
    refs: InstanceOf[dict[str, str]]
    direct_facts: InstanceOf[dict[str, tuple[tuple, ...]]]
    outgoing: InstanceOf[dict[tuple[str, str], frozenset[tuple]]]
    atom_rows: InstanceOf[dict[str, dict]]
    atom_order: InstanceOf[tuple[str, ...]]
    scope_rows: InstanceOf[dict[str, dict]]
    scope_order: InstanceOf[tuple[str, ...]]
    scope_signature: InstanceOf[tuple[tuple[str, str | None, str | None], ...]]
    registered: InstanceOf[frozenset[str]]
    inverse: InstanceOf[dict[str, str]]
    aliases: InstanceOf[dict[str, str]]
    excluded_paths: InstanceOf[frozenset[str]]
    duplicate_refs: InstanceOf[frozenset[str]]
    registry_contributions: InstanceOf[dict[str, RegistryContribution]]
    collisions: InstanceOf[frozenset[str]]
    fact_contributors: InstanceOf[dict[tuple, frozenset[tuple[str, str]]]]
    facts_by_endpoint: InstanceOf[dict[tuple[str, str], frozenset[tuple]]]
    support: InstanceOf[dict[tuple[str, str], frozenset[tuple]]]
    static_registry: bool


def _scope_signature(
    scopes: list[dict],
) -> tuple[tuple[str, str | None, str | None], ...]:
    return tuple(
        (row["name"], row.get("scope_unit_id"), row.get("parent_name"))
        for row in scopes
    )


def _registry(
    contributions: Mapping[str, RegistryContribution],
) -> RelationRegistry:
    names, inverse, collisions = registry_from_contributions(contributions)
    return RelationRegistry(
        frozenset(names),
        inverse,
        _unambiguous_aliases(contributions, names),
        frozenset(collisions),
    )


def _full_state(
    atoms: list[dict],
    scopes: list[dict],
    compilation: RegistryCompilation | None = None,
    registry: RelationRegistry | None = None,
) -> RelationState:
    excluded_paths, duplicate_refs = _duplicate_membership(atoms)
    graph_atoms = _graph_sources(atoms)
    registry, contributions, static_registry = _full_registry(
        graph_atoms, compilation, registry
    )
    _warn_colliding_uses(graph_atoms, registry.collisions)
    aliases = _scope_references(scopes)
    raw_by_path = {
        row["source_path"]: row
        for row in atoms
        if isinstance(row.get("source_path"), str)
    }
    graph_paths = {row.get("source_path") for row in graph_atoms}
    direct, contributors, facts_by_endpoint, outgoing, support = (
        _full_fact_indexes(
            raw_by_path, graph_paths, graph_atoms, aliases, registry, scopes
        )
    )
    atom_rows, scope_rows = _full_rows(
        raw_by_path, graph_paths, aliases, registry, outgoing, support, scopes
    )
    return _assembled_state(
        raw_by_path,
        graph_atoms,
        direct,
        outgoing,
        atom_rows,
        scope_rows,
        scopes,
        registry,
        excluded_paths,
        duplicate_refs,
        contributions,
        contributors,
        facts_by_endpoint,
        support,
        static_registry,
    )


def _full_fact_indexes(
    raw_by_path, graph_paths, graph_atoms, aliases, registry, scopes
):
    direct = {
        path: tuple(_atom_facts(row, aliases, registry))
        for path, row in raw_by_path.items()
        if path in graph_paths
    }
    contributors = _fact_contributors(scopes, registry, direct)
    facts_by_endpoint = _facts_by_endpoint(contributors)
    outgoing: dict[tuple[str, str], set[tuple]] = {}
    for fact in contributors:
        _add(outgoing, fact, registry.inverse)
    support = _support_facts(graph_atoms, scopes, registry, direct)
    return direct, contributors, facts_by_endpoint, outgoing, support


def _full_registry(graph_atoms, compilation, registry):
    static_registry = registry is not None
    if registry is None:
        compiled = (
            compile_registry(graph_atoms)
            if compilation is None
            else compilation
        )
        contributions = compiled.contributions
        registry = compiled.registry
    else:
        contributions = {}
    return registry, contributions, static_registry


def _assembled_state(
    raw_by_path,
    graph_atoms,
    direct,
    outgoing,
    atom_rows,
    scope_rows,
    scopes,
    registry,
    excluded_paths,
    duplicate_refs,
    contributions,
    contributors,
    facts_by_endpoint,
    support,
    static_registry,
):
    return RelationState(
        raw_by_path,
        {
            row["ref"]: row["source_path"]
            for row in graph_atoms
            if row["ref"] is not None
        },
        direct,
        {key: frozenset(value) for key, value in outgoing.items()},
        atom_rows,
        tuple(raw_by_path),
        scope_rows,
        tuple(scope_rows),
        _scope_signature(scopes),
        registry.names,
        dict(registry.inverse),
        dict(registry.aliases),
        excluded_paths,
        duplicate_refs,
        contributions,
        registry.collisions,
        contributors,
        facts_by_endpoint,
        {key: frozenset(value) for key, value in support.items()},
        static_registry,
    )


def _requires_full(
    state: RelationState,
    scopes: list[dict],
    changes: Mapping[str, dict | None],
) -> bool:
    if state.scope_signature != _scope_signature(scopes):
        return True
    changed_refs, released_refs = _changed_references(state, changes)
    if any(len(paths) > 1 for paths in changed_refs.values()):
        return True
    for path, new in changes.items():
        old = state.raw_by_path.get(path)
        old_ref = (
            old.get("ref")
            if old and old.get("status_group") != "Archived"
            else None
        )
        new_ref = (
            new.get("ref")
            if new is not None and new.get("status_group") != "Archived"
            else None
        )
        if path in state.excluded_paths or any(
            isinstance(reference, str) and reference in state.duplicate_refs
            for reference in (old_ref, new_ref)
        ):
            return True
        owner = state.refs.get(new_ref) if isinstance(new_ref, str) else None
        if (
            old_ref != new_ref
            and owner is not None
            and owner != path
            and new_ref not in released_refs
        ):
            return True
        if (
            old_ref is not None
            and old_ref != new_ref
            and state.refs.get(old_ref) != path
        ):
            return True
    return False


def _changed_references(state, changes):
    changed_refs: dict[str, set[str]] = {}
    released_refs: set[str] = set()
    for path, new in changes.items():
        old = state.raw_by_path.get(path)
        old_ref = (
            old.get("ref")
            if old and old.get("status_group") != "Archived"
            else None
        )
        new_ref = (
            new.get("ref")
            if new and new.get("status_group") != "Archived"
            else None
        )
        if isinstance(new_ref, str):
            changed_refs.setdefault(new_ref, set()).add(path)
        if isinstance(old_ref, str) and old_ref != new_ref:
            released_refs.add(old_ref)
    return changed_refs, released_refs


def _next_registry(
    state: RelationState,
    changes: Mapping[str, dict | None],
) -> tuple[dict[str, RegistryContribution], RelationRegistry]:
    contributions = dict(state.registry_contributions)
    for path, row in changes.items():
        if row is None:
            contributions.pop(path, None)
        else:
            if row.get("status_group") != "Archived":
                contributions[path] = registry_contribution(row)
            else:
                contributions.pop(path, None)
    return contributions, _registry(contributions)


def _rows(state: RelationState) -> tuple[list[dict], list[dict]]:
    return (
        [
            state.atom_rows[path]
            for path in state.atom_order
            if path in state.atom_rows
        ],
        [
            state.scope_rows[name]
            for name in state.scope_order
            if name in state.scope_rows
        ],
    )
