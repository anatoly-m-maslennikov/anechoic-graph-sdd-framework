"""Apply relation changes and assemble a materialization delta."""

from . import incremental_relations as runtime


def _finish_incremental(
    previous_state, changes, registry, contributions, data, rows_data, delta
):
    state = _incremental_state(
        previous_state, changes, registry, contributions, data, rows_data
    )
    old_atoms, new_atoms, old_scopes, new_scopes = delta
    rows, scope_output = runtime._rows(state)
    return (
        rows,
        scope_output,
        set(state.registered),
        dict(state.inverse),
        state,
        runtime.MaterializationDelta(
            old_atoms, new_atoms, old_scopes, new_scopes
        ),
    )


def _incremental_state(
    previous_state, changes, registry, contributions, data, rows_data
):
    raw, refs, direct, contributors, facts_by_endpoint, outgoing = data[:6]
    atom_rows, scope_rows, support = rows_data
    order = tuple(
        path for path in previous_state.atom_order if path in raw
    ) + tuple(
        path
        for path in changes
        if path in raw and path not in previous_state.raw_by_path
    )
    state = runtime.RelationState(
        raw,
        refs,
        direct,
        outgoing,
        atom_rows,
        order,
        scope_rows,
        previous_state.scope_order,
        previous_state.scope_signature,
        registry.names,
        dict(registry.inverse),
        dict(registry.aliases),
        previous_state.excluded_paths,
        previous_state.duplicate_refs,
        contributions,
        registry.collisions,
        contributors,
        facts_by_endpoint,
        support,
        previous_state.static_registry,
    )
    return state


def _updated_support(previous_state, scopes, registry, data):
    (
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
    ) = data
    changed_endpoints = {
        (runtime.ATOM, ref)
        for ref in touched_refs
        if (ref in previous_state.refs) != (ref in refs)
    }
    for endpoint in changed_endpoints:
        changed_facts.update(
            previous_state.facts_by_endpoint.get(endpoint, ())
        )
        changed_facts.update(facts_by_endpoint.get(endpoint, ()))
    scope_names = {row["name"] for row in scopes}
    present = {
        endpoint
        for fact in changed_facts
        for endpoint in (fact[:2], fact[3:])
        if (endpoint[0] == runtime.ATOM and endpoint[1] in refs)
        or (endpoint[0] == runtime.SCOPE and endpoint[1] in scope_names)
    }
    support = dict(previous_state.support)
    for fact in changed_facts:
        affected.update(
            runtime._refresh_support(
                support, fact, registry, present, active=fact in contributors
            )
        )

    return support


def _change_facts(previous_state, changes, registry, data):
    (
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
    ) = data
    runtime._remove_changed_facts(
        changes,
        raw,
        refs,
        direct,
        contributors,
        facts_by_endpoint,
        outgoing,
        previous_state.inverse,
        touched_refs,
        changed_facts,
        affected,
    )
    runtime._add_changed_facts(
        changes,
        raw,
        refs,
        direct,
        contributors,
        facts_by_endpoint,
        outgoing,
        aliases,
        registry,
        touched_refs,
        changed_facts,
        affected,
    )
