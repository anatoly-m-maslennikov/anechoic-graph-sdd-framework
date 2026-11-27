"""Lower common action outcome clauses to canonical trace obligations."""

import ast
import json
from graphlib import CycleError, TopologicalSorter

from .contract_literals import _literal_string
from .performance_model__pub import parse_performance
from .trace_manifest__pub import _effects

_CASE_FIELDS = {
    "must_effect",
    "forbid_effect",
    "must_precede",
    "performance",
    "same_values",
    "value_types",
}
TRACE_FIELDS = {*_CASE_FIELDS, "output", "cases", "invariant", "effects"}


def _forbidden_effects(targets):
    if not isinstance(targets, ast.Tuple) or not targets.elts:
        raise ValueError("expected nonempty forbidden effect tuple")
    values = [_literal_string(target) for target in targets.elts]
    if any(not value.strip() for value in values) or len(set(values)) != len(
        values
    ):
        raise ValueError("empty or duplicate forbidden effect")
    return values


def _effect_detail(node):
    if not isinstance(node, ast.Dict):
        raise ValueError("Expected a literal effect detail mapping")
    keys = [_literal_string(key) for key in node.keys]
    if len(keys) != len(set(keys)):
        raise ValueError("Duplicate required effect detail key")
    if any(
        isinstance(value, ast.Dict) and len(value.keys) != 1
        for value in node.values
    ):
        raise ValueError("Expected a single upper-bound predicate")
    return {
        key: ast.literal_eval(value) for key, value in zip(keys, node.values)
    }


def _effect_row(effect):
    if not isinstance(effect, ast.Tuple) or len(effect.elts) not in (2, 3):
        raise ValueError("invalid required effect tuple")
    names = tuple(_literal_string(item) for item in effect.elts[:2])
    return (
        (*names, _effect_detail(effect.elts[2]))
        if len(effect.elts) == 3
        else names
    )


def _effect_rows(effects, aliases):
    if not isinstance(effects, ast.Tuple) or not effects.elts:
        raise ValueError("expected nonempty effect tuple")
    rows = []
    for effect in effects.elts:
        if isinstance(effect, ast.Constant) and isinstance(effect.value, str):
            name = _literal_string(effect)
            if name not in aliases:
                raise ValueError(f"unknown effect alias {name!r}")
            rows.append(aliases[name])
        else:
            rows.append(_effect_row(effect))
    return _effects("must_effect", rows)


def _pair(node):
    if not isinstance(node, ast.Tuple) or len(node.elts) != 2:
        raise ValueError("expected an observation pair")
    return node.elts


def _reference(node):
    reference = tuple(_literal_string(field) for field in _pair(node))
    if any(not field.strip() for field in reference):
        raise ValueError("expected a named event and field")
    return reference


def _value_types(node):
    if not isinstance(node, ast.Dict) or not node.keys:
        raise ValueError("expected nonempty value_types mapping")
    rows = [
        (_reference(key), _literal_string(value))
        for key, value in zip(node.keys, node.values)
    ]
    kinds = {
        "null",
        "boolean",
        "string",
        "nonempty_string",
        "number",
        "integer",
        "array",
        "nonempty_array",
        "object",
    }
    if len(dict(rows)) != len(rows) or any(
        kind not in kinds for _, kind in rows
    ):
        raise ValueError("duplicate observation or unsupported value type")
    return rows


def _same_values(node):
    if not isinstance(node, ast.Tuple) or not node.elts:
        raise ValueError("expected nonempty same_values tuple")
    rows = [
        tuple(_reference(reference) for reference in _pair(row))
        for row in node.elts
    ]
    if any(left == right for left, right in rows):
        raise ValueError("same_values requires distinct named event fields")
    if len({frozenset(row) for row in rows}) != len(rows):
        raise ValueError("duplicate same_values comparison")
    return rows


def _precedence(orders, aliases, required):
    if not isinstance(orders, ast.Tuple) or not orders.elts:
        raise ValueError("expected nonempty order tuple")
    pairs = [tuple(_effect_rows(order, aliases)) for order in orders.elts]
    endpoints = {json.dumps(row, sort_keys=True) for row in required}
    endpoints.update(json.dumps(row[:2]) for row in required)
    keys = [
        tuple(json.dumps(row, sort_keys=True) for row in pair)
        for pair in pairs
    ]
    if any(len(pair) != 2 or pair[1] not in endpoints for pair in keys) or len(
        set(keys)
    ) != len(keys):
        raise ValueError(
            "order requires two effects and a required second effect"
        )
    graph = TopologicalSorter()
    for before, after in keys:
        graph.add(after, before)
    try:
        graph.prepare()
    except CycleError as error:
        raise ValueError("cyclic must_precede constraints") from error
    return pairs


def _trace_fields(args, aliases):
    claim = {
        key: parse(args[key])
        for key, parse in (
            ("same_values", _same_values),
            ("value_types", _value_types),
            ("forbid_effect", _forbidden_effects),
        )
        if key in args
    }
    if "performance" in args:
        claim["performance"] = parse_performance(
            args["performance"], _literal_string
        )
    if "must_effect" not in args:
        if "must_precede" in args:
            raise ValueError("order requires a required second effect")
        return claim
    rows = _effect_rows(args["must_effect"], aliases)
    claim["must_effect"] = rows
    if "must_precede" in args:
        claim["must_precede"] = _precedence(
            args["must_precede"], aliases, rows
        )
    if _required_targets(claim).intersection(claim.get("forbid_effect", ())):
        raise ValueError("required and forbidden effects contradict")
    return claim


def _required_targets(case):
    return {row[0] for row in case.get("must_effect", ())} | {
        before[0] for before, _ in case.get("must_precede", ())
    }


def _named_fields(node, label):
    if not isinstance(node, ast.Dict):
        raise ValueError(f"expected a literal {label} mapping")
    fields = {}
    for key, value in zip(node.keys, node.values):
        name = _literal_string(key)
        if not name.strip() or name in fields:
            raise ValueError(f"empty or duplicate {label} name")
        fields[name] = value
    return fields


def _case_fields(name, node, aliases, action):
    fields = _named_fields(node, "outcome clause")
    if fields.keys() - _CASE_FIELDS:
        raise ValueError("unsupported outcome clause")
    return {"action": action, "output": name, **_trace_fields(fields, aliases)}


def _cases(args, aliases, action):
    legacy = {"output", *_CASE_FIELDS} & args.keys()
    if "cases" in args:
        if legacy:
            raise ValueError("declare cases or one output clause")
        cases = _named_fields(args["cases"], "outcome")
        if not cases:
            raise ValueError("expected at least one outcome case")
        return {
            "cases": [
                _case_fields(name, node, aliases, action)
                for name, node in cases.items()
            ]
        }
    if legacy:
        if (
            "output" not in args
            or not (_CASE_FIELDS - {"must_precede"}) & legacy
        ):
            raise ValueError("effects need a selected output")
        output = _literal_string(args["output"])
        if not output.strip():
            raise ValueError("expected nonempty output")
        return {"trace": {"output": output, **_trace_fields(args, aliases)}}
    return {}


def trace_profile(args, action):
    """Share effect clauses between transports and retain action-wide scope."""
    aliases = (
        {
            name: _effects("must_effect", [_effect_row(effect)])[0]
            for name, effect in _named_fields(
                args["effects"], "effect alias"
            ).items()
        }
        if "effects" in args
        else {}
    )
    profile = _cases(args, aliases, action)
    if "invariant" not in args:
        return profile
    invariant = _named_fields(args["invariant"], "invariant")
    if invariant.keys() != {"forbid_effect"}:
        raise ValueError("expected an action invariant with forbid_effect")
    forbidden = _forbidden_effects(invariant["forbid_effect"])
    if any(
        _required_targets(case).intersection(forbidden)
        for case in profile.get("cases", [profile.get("trace", {})])
    ):
        raise ValueError("outcome effects contradict the action invariant")
    return {**profile, "invariant": {"forbid_effect": forbidden}}
