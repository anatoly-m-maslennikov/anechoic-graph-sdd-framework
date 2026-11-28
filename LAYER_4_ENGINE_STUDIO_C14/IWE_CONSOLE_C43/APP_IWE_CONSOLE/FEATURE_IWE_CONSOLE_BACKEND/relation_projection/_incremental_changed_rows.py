"""Update changed relation facts and materialized rows."""

from . import incremental_relations as runtime


def _remove_changed_facts(
    changes,
    raw,
    refs,
    direct,
    contributors,
    facts_by_endpoint,
    outgoing,
    inverse,
    touched_refs,
    changed_facts,
    affected,
):
    for path in changes:
        old = raw.get(path)
        if (
            old is not None
            and old.get("ref") is not None
            and refs.get(old["ref"]) == path
        ):
            refs.pop(old["ref"])
            touched_refs.add(old["ref"])
        for fact in direct.pop(path, ()):
            owners = set(contributors.get(fact, ()))
            owners.discard(("atom", path))
            if owners:
                contributors[fact] = frozenset(owners)
            else:
                contributors.pop(fact, None)
                runtime._index_fact(facts_by_endpoint, fact, add=False)
                changed_facts.add(fact)
                affected.update(
                    runtime._delta_edge(outgoing, fact, inverse, add=False)
                )
        raw.pop(path, None)


def _add_changed_facts(
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
):
    for path, new in changes.items():
        if new is not None:
            raw[path] = new
            graph = new.get("status_group") != "Archived"
            facts = (
                tuple(runtime._atom_facts(new, aliases, registry))
                if graph
                else ()
            )
            direct[path] = facts
            for fact in facts:
                owners = set(contributors.get(fact, ()))
                if not owners:
                    runtime._index_fact(facts_by_endpoint, fact, add=True)
                    changed_facts.add(fact)
                    affected.update(
                        runtime._delta_edge(
                            outgoing, fact, registry.inverse, add=True
                        )
                    )
                owners.add(("atom", path))
                contributors[fact] = frozenset(owners)
            if graph and new.get("ref") is not None:
                affected.add((runtime.ATOM, new["ref"]))
                refs[new["ref"]] = path
                touched_refs.add(new["ref"])
            runtime._warn_colliding_uses([new], registry.collisions)


def _updated_atom_rows(
    previous_state,
    changed_paths,
    raw,
    refs,
    affected,
    aliases,
    registry,
    outgoing,
    support,
):
    atom_rows = dict(previous_state.atom_rows)
    old_atoms = {
        path: previous_state.atom_rows[path]
        for path in changed_paths
        if path in previous_state.atom_rows
    }
    new_atoms: dict[str, dict] = {}
    atom_paths = {
        refs[ref]
        for kind, ref in affected
        if kind == runtime.ATOM and ref in refs
    } | {path for path in changed_paths if path in raw}
    for path in atom_paths:
        if path in atom_rows:
            old_atoms.setdefault(path, atom_rows[path])
        ref = raw[path].get("ref")
        graph = raw[path].get("status_group") != "Archived"
        facts = _atom_row_facts(
            raw[path], graph, ref, aliases, registry, outgoing, support
        )
        row = runtime._materialized_atom(raw[path], facts, graph=graph)
        if row is not None:
            atom_rows[path] = row
            new_atoms[path] = row
    for path in changed_paths:
        if path not in raw:
            atom_rows.pop(path, None)

    return atom_rows, old_atoms, new_atoms


def _atom_row_facts(raw_row, graph, ref, aliases, registry, outgoing, support):
    facts = (
        runtime._carrier_facts(raw_row, aliases, registry)
        if not graph
        else (
            ()
            if ref is None
            else tuple(
                sorted(
                    (
                        *outgoing.get((runtime.ATOM, ref), ()),
                        *support.get((runtime.ATOM, ref), ()),
                    ),
                )
            )
        )
    )
    return facts


def _updated_scope_rows(previous_state, scopes, affected, outgoing, support):
    scope_rows = dict(previous_state.scope_rows)
    old_scopes: dict[str, dict] = {}
    new_scopes: dict[str, dict] = {}
    scope_sources = {row["name"]: row for row in scopes}
    for kind, name in affected:
        if kind != runtime.SCOPE or name not in scope_sources:
            continue
        if name in scope_rows:
            old_scopes[name] = scope_rows[name]
        facts = tuple(
            sorted(
                (
                    *outgoing.get((runtime.SCOPE, name), ()),
                    *support.get((runtime.SCOPE, name), ()),
                )
            )
        )
        row = runtime._materialized_row(
            runtime.SCOPE, scope_sources[name], facts
        )
        if row is not None:
            scope_rows[name] = row
            new_scopes[name] = row

    return scope_rows, old_scopes, new_scopes
