"""Lower the bounded C45 HTTP Contract to a Lean value without executing it."""

import ast
import json
from pathlib import Path

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.structure.components.components__shared import (
    component_contract_fences,
    parse_component_manifest,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.content.content__shared import (
    parse_carrier,
)

_OUTCOMES = {"success", "invalid_input", "internal_error"}
_KINDS = {"result", "typed_error"}
_CATEGORIES = {
    "interface",
    "input_format",
    "output_format",
    "error_handling",
    "preconditions",
    "guarantees",
    "effects",
}


def _call(source):
    try:
        tree = ast.parse(source)
    except SyntaxError as error:
        raise ValueError("invalid Contract syntax") from error
    if (
        len(tree.body) != 1
        or not isinstance(tree.body[0], ast.Expr)
        or not isinstance(tree.body[0].value, ast.Call)
    ):
        raise ValueError("expected one declare_contract call")
    call = tree.body[0].value
    if (
        not isinstance(call.func, ast.Name)
        or call.func.id != "declare_contract"
        or call.args
        or len(call.keywords) != len({item.arg for item in call.keywords})
        or {item.arg for item in call.keywords}
        not in ({"operation", "outcomes"}, {"operation", "outcomes", "checks"})
    ):
        raise ValueError("unsupported Contract call")
    return {item.arg: item.value for item in call.keywords}


def _rows(args):
    try:
        operation = ast.literal_eval(args["operation"])
    except (ValueError, TypeError) as error:
        raise ValueError("operation must be literal") from error
    if operation != "POST /tools" or not isinstance(
        args["outcomes"], ast.Dict
    ):
        raise ValueError("unsupported operation or outcomes")
    rows = []
    try:
        for key, value in zip(args["outcomes"].keys, args["outcomes"].values):
            name, row = ast.literal_eval(key), ast.literal_eval(value)
            if (
                name not in _OUTCOMES
                or type(row) is not tuple
                or len(row) != 2
                or type(row[0]) is not int
                or not 100 <= row[0] <= 599
                or row[1] not in _KINDS
            ):
                raise ValueError("unsupported outcome")
            rows.append((name, row[0], row[1]))
    except (ValueError, TypeError) as error:
        raise ValueError("invalid outcome literal") from error
    if {row[0] for row in rows} != _OUTCOMES or len(rows) != len(_OUTCOMES):
        raise ValueError("outcomes must have unique keys")
    return rows


def _literal_string(node):
    if not isinstance(node, ast.Constant) or type(node.value) is not str:
        raise ValueError("expected a literal string")
    if any(0xD800 <= ord(char) <= 0xDFFF for char in node.value):
        raise ValueError("invalid Unicode scalar")
    return node.value


def _checks(args):
    if "checks" not in args:
        return []
    checks = args["checks"]
    if type(checks) is not ast.Dict:
        raise ValueError("unsupported checks expression")
    categories = set()
    result = []
    for category_node, facts in zip(checks.keys, checks.values):
        category = _literal_string(category_node)
        if (
            category not in _CATEGORIES
            or category in categories
            or not isinstance(facts, ast.Dict)
        ):
            raise ValueError("unsupported or duplicate checks category")
        categories.add(category)
        names = set()
        for name_node, value in zip(facts.keys, facts.values):
            name = _literal_string(name_node)
            if not name or name in names:
                raise ValueError("empty or duplicate check name")
            names.add(name)
            if isinstance(value, ast.Tuple):
                values = [_literal_string(item) for item in value.elts]
                if len(values) != len(set(values)):
                    raise ValueError("duplicate check value")
                values.sort()
            else:
                values = [_literal_string(value)]
                if not values[0]:
                    raise ValueError("empty check value")
            result.append((category + "." + name, values))
    return sorted(result)


def _lean_string(value):
    if not value or value.isprintable():
        return json.dumps(value, ensure_ascii=False)
    return (
        "String.ofList ["
        + ", ".join(f"Char.ofNat {ord(char)}" for char in value)
        + "]"
    )


def contract_to_lean(path: Path) -> str:
    "Read the active C45 Contract and lower its one supported formal claim."
    parsed = parse_carrier(path.read_bytes(), path)
    meta = parsed.metadata
    state = meta.get("state", {})
    if (
        meta.get("atom_id") != "AN-S-3059"
        or meta.get("atom_family") != "SPEC"
        or meta.get("container", {}).get("component") != "C43"
        or meta.get("tier") != 1
        or meta.get("context", {}).get("template") != "component_manifest"
        or state.get("status") != "active"
        or type(state.get("version")) is not int
    ):
        raise ValueError("invalid Contract identity or state")
    if (
        parse_component_manifest(parsed.body, tier=1)[0].get("component_id")
        != "C45"
    ):
        raise ValueError("Manifest does not declare C45")
    fences = list(component_contract_fences(parsed.body) or ())
    if len(fences) != 1 or fences[0][0] != "python contract":
        raise ValueError("expected exactly one python contract formal claim")
    args = _call(fences[0][1])
    rows = _rows(args)
    return _render_contract(rows, _checks(args))


def _render_contract(rows, checks):
    values = ", ".join(
        f'("{name}", {status}, "{kind}")' for name, status, kind in rows
    )
    check_values = ", ".join(
        (
            "("
            f"{_lean_string(name)}"
            ", ["
            f"{', '.join((_lean_string(value) for value in items))}"
            "])"
        )
        for name, items in checks
    )
    return (
        "namespace BackendHttpContract\n"
        f"def expected : List (String × Nat × String) := [{values}]\n"
        "def expectedChecks : List (String × List String) := "
        f"[{check_values}]\n"
        "end BackendHttpContract\n"
    )
