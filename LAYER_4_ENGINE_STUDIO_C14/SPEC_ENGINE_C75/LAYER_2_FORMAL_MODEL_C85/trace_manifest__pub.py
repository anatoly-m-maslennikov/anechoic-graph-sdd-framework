"""Validate explicit logical operation outcome declarations."""

import json


def _effect_detail(detail):
    if not isinstance(detail, dict) or not detail:
        raise ValueError('Required effect detail must be a nonempty mapping')
    for key, value in detail.items():
        bound = (isinstance(value, dict) and set(value) == {'at_most'}
                 and type(value['at_most']) is int and value['at_most'] >= 0)
        if not isinstance(key, str) or not key.strip() or (type(value) not in (str, int, bool, type(None)) and not bound):
            raise ValueError('Required effect detail needs nonblank keys and scalar values or upper bounds')
        key.encode('utf-8')
        if isinstance(value, str):
            value.encode('utf-8')
    return detail


def _effects(key, values):
    if not isinstance(values, (tuple, list)) or not values:
        raise ValueError('Effect constraints must be nonempty sequences')
    names = values
    if key == 'must_effect':
        if any(not isinstance(value, (tuple, list)) or len(value) not in (2, 3) for value in values):
            raise ValueError('Required effects need a target, outcome and optional detail')
        values = [tuple(value) if len(value) == 2 else (*value[:2], _effect_detail(value[2])) for value in values]
        names = [name for effect in values for name in effect[:2]]
    if any(not isinstance(name, str) or not name.strip() for name in names):
        raise ValueError('Effect names must be nonblank strings')
    if len({json.dumps(value, sort_keys=True) for value in values}) != len(values):
        raise ValueError('Duplicate effect constraint')
    return values


def _outcome(action, output, constraints):
    if not isinstance(output, str) or not output.strip() or not isinstance(constraints, dict):
        raise ValueError('Each logical outcome needs a nonblank name and constraints')
    if not constraints or set(constraints) - {'must_effect', 'forbid_effect'}:
        raise ValueError('Logical outcome needs only effect constraints')
    effects = {key: _effects(key, values) for key, values in constraints.items()}
    if {effect[0] for effect in effects.get('must_effect', [])} & set(effects.get('forbid_effect', [])):
        raise ValueError('Required and forbidden effects contradict')
    return {'action': action, 'output': output, **effects}


def outcome_cases(boundaries):
    if not isinstance(boundaries, dict) or not isinstance(boundaries.get('io'), dict):
        return [], False
    io = boundaries['io']
    servers = io.get('server')
    if not isinstance(servers, dict):
        return [], False
    cases, complete = [], set(io) == {'server'}
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
