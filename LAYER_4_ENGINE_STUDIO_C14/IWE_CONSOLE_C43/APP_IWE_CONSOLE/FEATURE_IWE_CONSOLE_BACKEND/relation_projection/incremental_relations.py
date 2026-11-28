"""Copy-on-write relation materialization for an incremental source batch."""

from __future__ import annotations

from typing import Mapping

from ._incremental_apply_helpers import (
    _change_facts,
    _finish_incremental,
    _updated_support,
)
from ._incremental_changed_rows import (
    _remove_changed_facts as _remove_changed_facts,
    _add_changed_facts as _add_changed_facts,
    _updated_atom_rows as _updated_atom_rows,
    _updated_scope_rows as _updated_scope_rows,
)

from KERNEL_MIXER_C59.index_delta import MaterializationDelta
from KERNEL_MIXER_C59.KERNEL_MIXER_C59__shared import (
    ATOM as ATOM,
    SCOPE as SCOPE,
    _atom_facts as _atom_facts,
    _carrier_facts as _carrier_facts,
    _materialized_atom as _materialized_atom,
    _materialized_row as _materialized_row,
    _scope_references,
)
from KERNEL_MIXER_C59.KERNEL_MIXER_C59__shared import (
    RelationRegistry,
    RegistryCompilation,
    _warn_colliding_uses as _warn_colliding_uses,
)
from .incremental_relation_state import (
    RelationState,
    _delta_edge as _delta_edge,
    _full_state,
    _index_fact as _index_fact,
    _next_registry,
    _refresh_support as _refresh_support,
    _requires_full,
    _rows,
)


def _apply_incremental(
    previous_state, scopes, changes, contributions, registry
):
    data = _change_state(previous_state, scopes)
    changed_paths = set(changes)
    _change_facts(previous_state, changes, registry, data)
    support = _updated_support(previous_state, scopes, registry, data)
    raw, refs = data[0], data[1]
    outgoing, aliases, affected = data[5], data[6], data[9]

    atom_rows, old_atoms, new_atoms = _updated_atom_rows(
        previous_state,
        changed_paths,
        raw,
        refs,
        affected,
        aliases,
        registry,
        outgoing,
        support,
    )

    scope_rows, old_scopes, new_scopes = _updated_scope_rows(
        previous_state, scopes, affected, outgoing, support
    )

    return _finish_incremental(
        previous_state,
        changes,
        registry,
        contributions,
        data,
        (atom_rows, scope_rows, support),
        (old_atoms, new_atoms, old_scopes, new_scopes),
    )


def _change_state(previous_state, scopes):
    aliases = _scope_references(scopes)
    raw = dict(previous_state.raw_by_path)
    direct = dict(previous_state.direct_facts)
    contributors = dict(previous_state.fact_contributors)
    facts_by_endpoint = dict(previous_state.facts_by_endpoint)
    outgoing = dict(previous_state.outgoing)
    refs = dict(previous_state.refs)
    affected: set[tuple[str, str]] = set()
    changed_facts: set[tuple] = set()
    touched_refs: set[str] = set()
    data = (
        raw,
        refs,
        direct,
        contributors,
        facts_by_endpoint,
        outgoing,
        aliases,
        touched_refs,
        changed_facts,
        affected,
    )
    return data


def materialize_delta(  # noqa: C901
    atoms: list[dict],
    scopes: list[dict],
    previous_state: RelationState | None = None,
    changes: Mapping[str, dict | None] | None = None,
    initial_compilation: RegistryCompilation | None = None,
    registry: RelationRegistry | None = None,
) -> tuple[
    list[dict],
    list[dict],
    set[str],
    dict[str, str],
    RelationState,
    MaterializationDelta | None,
]:
    "Return a full build or changed-source delta without source mutation."
    if previous_state is not None and previous_state.static_registry:
        registry = _static_registry(previous_state)
    if (
        previous_state is None
        or changes is None
        or _requires_full(previous_state, scopes, changes)
    ):
        state = _full_state(
            atoms,
            scopes,
            initial_compilation if previous_state is None else None,
            registry,
        )
        return _full_output(state)

    if previous_state.static_registry:
        contributions = previous_state.registry_contributions
        registry = _static_registry(previous_state)
    else:
        contributions, registry = _next_registry(previous_state, changes)
    if _registry_changed(registry, previous_state):
        return _full_output(_full_state(atoms, scopes))

    return _apply_incremental(
        previous_state, scopes, changes, contributions, registry
    )


def _static_registry(state):
    return RelationRegistry(
        state.registered, state.inverse, state.aliases, state.collisions
    )


def _full_output(state):
    rows, scope_rows = _rows(state)
    return (
        rows,
        scope_rows,
        set(state.registered),
        dict(state.inverse),
        state,
        None,
    )


def _registry_changed(registry, previous_state):
    return (
        registry.names,
        registry.inverse,
        registry.aliases,
        registry.collisions,
    ) != (
        previous_state.registered,
        previous_state.inverse,
        previous_state.aliases,
        previous_state.collisions,
    )
