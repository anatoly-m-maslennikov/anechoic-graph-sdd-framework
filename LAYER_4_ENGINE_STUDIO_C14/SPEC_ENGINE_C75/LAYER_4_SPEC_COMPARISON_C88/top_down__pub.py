"""Compare explicit, source-pinned obligations with Lean."""

import json
from ..LAYER_1_DIAGNOSTICS_C90.diagnostics__pub import verdict
from ..LAYER_3_LEAN_TRANSLATOR_C84.lean_check__pub import run_lean_json
from ..LAYER_3_LEAN_TRANSLATOR_C84.lean_values__pub import lean_string


_DIRECTIONS = (('manifest', 'contract'), ('manifest', 'solution'), ('contract', 'solution'))


def _literal(facts):
    return '[' + ', '.join(
        f'({lean_string(key)}, {lean_string(json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False, separators=(",", ":")))})'
        for key, value in sorted(facts.items())) + ']'


def _program(obligations, directions, roles):
    declarations = '\n'.join(f'def {role} : List (String × String) := {_literal(obligations[role])}'
                             for role in roles)
    calls = ', '.join(f'compare {left} {right}' for left, right in directions)
    return f'''import Lean
{declarations}
def compare (left right : List (String × String)) : List String :=
  left.map fun fact =>
    match right.find? (fun candidate => candidate.1 == fact.1) with
    | none => "unresolved"
    | some candidate => if candidate.2 == fact.2 then "matched" else "conflicting"
#eval IO.println (Lean.toJson [{calls}]).compress
'''


def _compare(sources, obligations, pairs, lean):
    roles = dict.fromkeys(role for pair in pairs for role in pair)
    if any(role not in sources or role not in obligations or not isinstance(obligations[role], dict)
           or any(not isinstance(key, str) for key in obligations[role]) for role in roles):
        raise ValueError('sources and obligation dictionaries must contain each comparison role')
    output = run_lean_json(_program(obligations, pairs, roles), lean)
    if (not isinstance(output, list) or len(output) != len(pairs) or
            any(not isinstance(rows, list) or len(rows) != len(obligations[left]) or
                any(status not in ('matched', 'conflicting', 'unresolved') for status in rows)
                for (left, _), rows in zip(pairs, output))):
        raise ValueError('unexpected Lean comparison output')
    directions = {}
    for (left, right), statuses in zip(pairs, output):
        facts = [{'key': key, 'left': value, 'right': obligations[right].get(key), 'status': status}
                 for (key, value), status in zip(sorted(obligations[left].items()), statuses)]
        directions[f'{left}_{right}'] = {'status': verdict(statuses), 'facts': facts}
    return {'status': verdict([direction['status'] for direction in directions.values()]),
            'sources': sources, 'directions': directions}


def compare_obligations(sources, obligations, *, lean='lean'):
    """Compare Manifest, Contract, and Solution obligations."""
    return _compare(sources, obligations, _DIRECTIONS, lean)


def compare_delegation(sources, obligations, *, lean='lean'):
    """Compare caller obligations with the provider's three formal declarations."""
    pairs = (('caller', 'manifest'), ('caller', 'contract'), ('caller', 'solution'))
    return _compare(sources, obligations, pairs, lean)
