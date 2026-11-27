"""Find feasible terminal edges with literal string bindings and a bounded search."""

_CONFIGURATION_LIMIT = 10_000


def _advance(expect, bindings):
    detail = expect.get('detail', {})
    values = {}
    for key, alias in expect.get('same_as', {}).items():
        if alias not in bindings:
            return None
        value = bindings[alias]
        if key in detail and not isinstance(detail[key], str):
            return None
        if key in detail and detail[key] != value:
            return False
        if key in values and values[key] != value:
            return False
        values[key] = value
    updated = dict(bindings)
    for alias, key in expect.get('bind', {}).items():
        value = values.get(key, detail.get(key))
        if not isinstance(value, str):
            return None
        if alias in updated and updated[alias] != value:
            return False
        updated[alias] = value
    return updated


def feasible_terminals(claim):
    """Return unresolved for unknown bindings or more than the supported state space."""
    states = {state['name']: state for state in claim['states']}
    queue = [(claim['initial'], ())]
    seen = set(queue)
    terminals = set()
    for name, bindings in queue:
        for index, edge in enumerate(states[name]['transitions']):
            updated = _advance(edge['expect'], dict(bindings))
            if updated is None:
                return None
            if updated is False:
                continue
            target = edge['target']
            if states[target]['final']:
                terminals.add((name, index))
            item = (target, tuple(sorted(updated.items())))
            if item not in seen:
                if len(seen) >= _CONFIGURATION_LIMIT:
                    return None
                seen.add(item)
                queue.append(item)
    return terminals
