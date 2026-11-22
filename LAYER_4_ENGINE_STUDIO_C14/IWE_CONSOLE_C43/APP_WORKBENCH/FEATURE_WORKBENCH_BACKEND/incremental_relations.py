"""Copy-on-write relation materialization for an incremental source batch."""

from __future__ import annotations

from typing import Mapping

from KERNEL_MIXER_C59.index_delta import MaterializationDelta
from KERNEL_MIXER_C59.KERNEL_MIXER_C59__shared import (
    ATOM, SCOPE, _atom_facts, _carrier_facts, _materialized_atom, _materialized_row,
    _scope_references,
)
from KERNEL_MIXER_C59.relation_registry import RelationRegistry, RegistryCompilation, _warn_colliding_uses
from .incremental_relation_state import (
    RelationState, _delta_edge, _full_state, _index_fact, _next_registry, _refresh_support,
    _requires_full, _rows,
)

def _remove_changed_facts(changes, raw, refs, direct, contributors, facts_by_endpoint, outgoing, inverse, touched_refs, changed_facts, affected):
    for path in changes:
        old = raw.get(path)
        if old is not None and old.get("ref") is not None and refs.get(old["ref"]) == path:
            refs.pop(old["ref"])
            touched_refs.add(old["ref"])
        for fact in direct.pop(path, ()):
            owners = set(contributors.get(fact, ()))
            owners.discard(("atom", path))
            if owners:
                contributors[fact] = frozenset(owners)
            else:
                contributors.pop(fact, None)
                _index_fact(facts_by_endpoint, fact, add=False)
                changed_facts.add(fact)
                affected.update(_delta_edge(outgoing, fact, inverse, add=False))
        raw.pop(path, None)


def _add_changed_facts(changes, raw, refs, direct, contributors, facts_by_endpoint, outgoing, aliases, registry, touched_refs, changed_facts, affected):
    for path, new in changes.items():
        if new is not None:
            raw[path] = new
            graph = new.get("status_group") != "Archived"
            facts = tuple(_atom_facts(new, aliases, registry)) if graph else ()
            direct[path] = facts
            for fact in facts:
                owners = set(contributors.get(fact, ()))
                if not owners:
                    _index_fact(facts_by_endpoint, fact, add=True)
                    changed_facts.add(fact)
                    affected.update(_delta_edge(outgoing, fact, registry.inverse, add=True))
                owners.add(("atom", path))
                contributors[fact] = frozenset(owners)
            if graph and new.get("ref") is not None:
                affected.add((ATOM, new["ref"]))
                refs[new["ref"]] = path
                touched_refs.add(new["ref"])
            _warn_colliding_uses([new], registry.collisions)


def _updated_atom_rows(previous_state, changed_paths, raw, refs, affected, aliases, registry, outgoing, support):
    atom_rows = dict(previous_state.atom_rows)
    old_atoms = {path: previous_state.atom_rows[path] for path in changed_paths if path in previous_state.atom_rows}
    new_atoms: dict[str, dict] = {}
    atom_paths = {refs[ref] for kind, ref in affected if kind == ATOM and ref in refs} | {path for path in changed_paths if path in raw}
    for path in atom_paths:
        if path in atom_rows:
            old_atoms.setdefault(path, atom_rows[path])
        ref = raw[path].get("ref")
        graph = raw[path].get("status_group") != "Archived"
        facts = (_carrier_facts(raw[path], aliases, registry) if not graph else
                 (() if ref is None else tuple(sorted(
                     (*outgoing.get((ATOM, ref), ()), *support.get((ATOM, ref), ())),
                 ))))
        row = _materialized_atom(raw[path], facts, graph=graph)
        if row is not None:
            atom_rows[path] = row
            new_atoms[path] = row
    for path in changed_paths:
        if path not in raw:
            atom_rows.pop(path, None)

    return atom_rows, old_atoms, new_atoms


def _updated_scope_rows(previous_state, scopes, affected, outgoing, support):
    scope_rows = dict(previous_state.scope_rows)
    old_scopes: dict[str, dict] = {}
    new_scopes: dict[str, dict] = {}
    scope_sources = {row["name"]: row for row in scopes}
    for kind, name in affected:
        if kind != SCOPE or name not in scope_sources:
            continue
        if name in scope_rows:
            old_scopes[name] = scope_rows[name]
        facts = tuple(sorted((*outgoing.get((SCOPE, name), ()), *support.get((SCOPE, name), ()))))
        row = _materialized_row(SCOPE, scope_sources[name], facts)
        if row is not None:
            scope_rows[name] = row
            new_scopes[name] = row

    return scope_rows, old_scopes, new_scopes


def _apply_incremental(previous_state, scopes, changes, contributions, registry):
    aliases = _scope_references(scopes)
    raw = dict(previous_state.raw_by_path)
    direct = dict(previous_state.direct_facts)
    contributors = dict(previous_state.fact_contributors)
    facts_by_endpoint = dict(previous_state.facts_by_endpoint)
    outgoing = dict(previous_state.outgoing)
    refs = dict(previous_state.refs)
    affected: set[tuple[str, str]] = set()
    changed_paths = set(changes)
    changed_facts: set[tuple] = set()
    touched_refs: set[str] = set()
    _remove_changed_facts(changes, raw, refs, direct, contributors, facts_by_endpoint, outgoing,
                          previous_state.inverse, touched_refs, changed_facts, affected)
    _add_changed_facts(changes, raw, refs, direct, contributors, facts_by_endpoint, outgoing,
                       aliases, registry, touched_refs, changed_facts, affected)

    changed_endpoints = {(ATOM, ref) for ref in touched_refs if (ref in previous_state.refs) != (ref in refs)}
    for endpoint in changed_endpoints:
        changed_facts.update(previous_state.facts_by_endpoint.get(endpoint, ()))
        changed_facts.update(facts_by_endpoint.get(endpoint, ()))
    scope_names = {row["name"] for row in scopes}
    present = {
        endpoint for fact in changed_facts for endpoint in (fact[:2], fact[3:])
        if (endpoint[0] == ATOM and endpoint[1] in refs)
        or (endpoint[0] == SCOPE and endpoint[1] in scope_names)
    }
    support = dict(previous_state.support)
    for fact in changed_facts:
        affected.update(_refresh_support(support, fact, registry, present, active=fact in contributors))

    atom_rows, old_atoms, new_atoms = _updated_atom_rows(
        previous_state, changed_paths, raw, refs, affected, aliases, registry, outgoing, support,
    )

    scope_rows, old_scopes, new_scopes = _updated_scope_rows(previous_state, scopes, affected, outgoing, support)

    order = tuple(path for path in previous_state.atom_order if path in raw) + tuple(path for path in changes if path in raw and path not in previous_state.raw_by_path)
    state = RelationState(
        raw, refs, direct, outgoing, atom_rows, order, scope_rows, previous_state.scope_order,
        previous_state.scope_signature, registry.names, dict(registry.inverse), dict(registry.aliases),
        previous_state.excluded_paths, previous_state.duplicate_refs, contributions, registry.collisions,
        contributors, facts_by_endpoint,
        support, previous_state.static_registry,
    )
    rows, scope_output = _rows(state)
    return rows, scope_output, set(state.registered), dict(state.inverse), state, MaterializationDelta(old_atoms, new_atoms, old_scopes, new_scopes)


def materialize_delta(  # noqa: C901
    atoms: list[dict], scopes: list[dict], previous_state: RelationState | None = None,
    changes: Mapping[str, dict | None] | None = None,
    initial_compilation: RegistryCompilation | None = None,
    registry: RelationRegistry | None = None,
) -> tuple[list[dict], list[dict], set[str], dict[str, str], RelationState, MaterializationDelta | None]:
    """Return a full build or a changed-source relation delta without source mutation."""
    if previous_state is not None and previous_state.static_registry:
        registry = RelationRegistry(previous_state.registered, previous_state.inverse, previous_state.aliases, previous_state.collisions)
    if previous_state is None or changes is None or _requires_full(previous_state, scopes, changes):
        state = _full_state(atoms, scopes, initial_compilation if previous_state is None else None, registry)
        rows, scope_rows = _rows(state)
        return rows, scope_rows, set(state.registered), dict(state.inverse), state, None

    if previous_state.static_registry:
        contributions = previous_state.registry_contributions
        registry = RelationRegistry(previous_state.registered, previous_state.inverse, previous_state.aliases, previous_state.collisions)
    else:
        contributions, registry = _next_registry(previous_state, changes)
    if (registry.names, registry.inverse, registry.aliases, registry.collisions) != (
        previous_state.registered, previous_state.inverse, previous_state.aliases, previous_state.collisions,
    ):
        state = _full_state(atoms, scopes)
        rows, scope_rows = _rows(state)
        return rows, scope_rows, set(state.registered), dict(state.inverse), state, None

    return _apply_incremental(previous_state, scopes, changes, contributions, registry)
