"""Validate explicit logical operation outcome declarations."""


def _effects(key, values):
    if not isinstance(values, (tuple, list)) or not values:
        raise ValueError('Effect constraints must be nonempty sequences')
    names = values
    if key == 'must_effect':
        if any(not isinstance(value, (tuple, list)) or len(value) != 2 for value in values):
            raise ValueError('Required effects must be pairs')
        values = [tuple(value) for value in values]
        names = [name for effect in values for name in effect]
    if any(not isinstance(name, str) or not name.strip() for name in names):
        raise ValueError('Effect names must be nonblank strings')
    if len(set(values)) != len(values):
        raise ValueError('Duplicate effect constraint')
    return values


def _outcome(action, output, constraints):
    if not isinstance(output, str) or not output.strip() or not isinstance(constraints, dict):
        raise ValueError('Each logical outcome needs a nonblank name and constraints')
    if not constraints or set(constraints) - {'must_effect', 'forbid_effect'}:
        raise ValueError('Logical outcome needs only effect constraints')
    effects = {key: _effects(key, values) for key, values in constraints.items()}
    if {target for target, _ in effects.get('must_effect', [])} & set(effects.get('forbid_effect', [])):
        raise ValueError('Required and forbidden effects contradict')
    return {'action': action, 'output': output, **effects}


def outcome_cases(boundaries):
    if not isinstance(boundaries, dict) or not isinstance(boundaries.get('io'), dict):
        return [], False
    io = boundaries['io']
    servers = io.get('server')
    if not isinstance(servers, dict):
        return [], False
    cases, complete = [], set(io) == {'server'} and bool(servers)
    for action, declaration in servers.items():
        if not isinstance(declaration, dict) or 'outcomes' not in declaration:
            complete = False
            continue
        if not isinstance(action, str) or not action.strip():
            raise ValueError('Logical action must have a nonblank name')
        if set(declaration) != {'outcomes'}:
            complete = False
        outcomes = declaration['outcomes']
        if not isinstance(outcomes, dict) or not outcomes:
            raise ValueError('Logical outcomes must be a nonempty mapping')
        cases.extend(_outcome(action, output, constraints) for output, constraints in outcomes.items())
    return cases, complete
