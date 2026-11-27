"""Check public equality obligations against independently observed event values."""

import json

from ..LAYER_1_DIAGNOSTICS_C90._package__shared import verdict
from ..LAYER_3_LEAN_TRANSLATOR_C84._package__shared import (
    _JSON_INTEGER_RULE,
    lean_string,
    run_lean_json,
)

_MISSING = object()
_PROGRAM = 'import Lean\n' + _JSON_INTEGER_RULE + """
partial def sameJson (left right : Lean.Json) : Bool :=
  match left, right with
  | .num a, .num b => a.normalize == b.normalize
  | .arr a, .arr b =>
    a.size == b.size && (a.zip b).all (fun (x, y) => sameJson x y)
  | .obj a, .obj b =>
    a.size == b.size && a.all (fun key x => (b.get? key).any (sameJson x))
  | _, _ => left == right

def compareFields (left right : String) : String :=
  match Lean.Json.parse left, Lean.Json.parse right with
  | .ok l, .ok r => if sameJson l r then "matched" else "conflicting"
  | _, _ => "unresolved"

def valueType (value : Lean.Json) : String :=
  match value with
  | .null => "null"
  | .bool _ => "boolean"
  | .str _ => "string"
  | .num _ => "number"
  | .arr _ => "array"
  | .obj _ => "object"

def isPythonWhitespace (character : Char) : Bool :=
  let code := character.toNat
  (9 <= code && code <= 13) || (28 <= code && code <= 32) ||
  (0x2000 <= code && code <= 0x200A) ||
  [0x85, 0xA0, 0x1680, 0x2028, 0x2029, 0x202F, 0x205F, 0x3000].contains code

def hasValueType (expected : String) (value : Lean.Json) : Bool :=
  match expected, value with
  | "integer", value => (exactInteger value).isSome
  | "nonempty_string", .str text => !text.all isPythonWhitespace
  | "nonempty_array", .arr items => !items.isEmpty
  | expected, value => valueType value == expected

def checkType (expected raw : String) : String :=
  match Lean.Json.parse raw with
  | .error _ => "unresolved"
  | .ok value => if hasValueType expected value then "matched" else "conflicting"
"""


def _value(events, reference):
    event, field = reference
    observed = []
    for row in events:
        if not isinstance(row, dict):
            return _MISSING
        if row.get('event') == event:
            observed.append(row.get('detail', {}))
    if len(observed) != 1 or not isinstance(observed[0], dict):
        return _MISSING
    return observed[0].get(field, _MISSING)


def _encoded(value):
    return lean_string(json.dumps(value, ensure_ascii=False, allow_nan=False, sort_keys=True))


def _equality(left, right):
    if left is _MISSING or right is _MISSING:
        return '"unresolved"'
    return f'compareFields {_encoded(left)} {_encoded(right)}'


def _type_check(value, kind):
    if value is _MISSING:
        return '"unresolved"'
    return f'checkType {lean_string(kind)} {_encoded(value)}'


def compare_trace_values(case, events, *, lean='lean'):
    """Compare named fields in one selected Contract outcome and concrete event trace."""
    pairs = case.get('same_values', [])
    types = case.get('value_types', [])
    expressions = [_equality(_value(events, left), _value(events, right)) for left, right in pairs]
    expressions.extend(_type_check(_value(events, field), kind) for field, kind in types)
    statuses = run_lean_json(
        _PROGRAM + '#eval IO.println (Lean.toJson (' +
        f'[{", ".join(expressions)}] : List String)).compress\n', lean,
    ) if expressions else []
    if (not isinstance(statuses, list) or len(statuses) != len(expressions)
            or any(status not in ('matched', 'conflicting', 'unresolved') for status in statuses)):
        raise ValueError('unexpected Lean trace value comparison output')
    facts = [{'key': 'same_values', 'left': left, 'right': right, 'status': status}
             for (left, right), status in zip(pairs, statuses[:len(pairs)], strict=True)]
    facts.extend({'key': 'value_types', 'field': field, 'expected': kind, 'status': status}
                 for (field, kind), status in zip(types, statuses[len(pairs):], strict=True))
    return {'status': verdict(statuses), 'action': case.get('action'),
            'output': case.get('output'), 'facts': facts}
