import ast
import re


def _names(values, pattern, label):
    if (
        not isinstance(values, (list, tuple))
        or any(
            not isinstance(value, str) or not re.fullmatch(pattern, value)
            for value in values
        )
        or len(set(values)) != len(values)
    ):
        raise ValueError(f"invalid or duplicate {label}")
    return list(values)


def parse_group(source, role):
    tree = ast.parse(source)
    expected = {
        "contract": "declare_group_contract",
        "solution": "component_group",
    }.get(role)
    if len(tree.body) != 1 or not isinstance(tree.body[0], ast.Expr):
        raise ValueError("expected one group declaration")
    call = tree.body[0].value
    if (
        not isinstance(call, ast.Call)
        or not isinstance(call.func, ast.Name)
        or call.func.id != expected
        or call.args
        or "roles" not in {key.arg for key in call.keywords}
        or {key.arg for key in call.keywords}
        - {"roles", "entry_points", "current_record_count"}
        or len(call.keywords) != len({key.arg for key in call.keywords})
    ):
        raise ValueError(
            "expected roles and optional entry_points and current_record_count"
        )
    args = {key.arg: key.value for key in call.keywords}
    claim = _group_roles(args)
    if "entry_points" in args:
        claim["entry_points"] = _names(
            ast.literal_eval(args["entry_points"]),
            r"[A-Za-z][A-Za-z0-9_]*",
            "entry points",
        )
    if "current_record_count" in args:
        claim["current_record_count"] = _count(
            ast.literal_eval(args["current_record_count"])
        )
    return claim


def _group_roles(args):
    node = args["roles"]
    if not isinstance(node, ast.Dict) or any(key is None for key in node.keys):
        raise ValueError("roles must be a literal mapping")
    pairs = [
        (ast.literal_eval(key), ast.literal_eval(value))
        for key, value in zip(node.keys, node.values)
    ]
    names = _names(
        [key for key, _ in pairs], r"[A-Za-z][A-Za-z0-9_]*", "role names"
    )
    ids = [value for _, value in pairs]
    for value in ids:
        _names([value], r"C[0-9]+", "Component ID")
    claim = {"roles": dict(zip(names, ids))}
    return claim


def _count(value):
    if type(value) is not int or value < 0:
        raise ValueError("current_record_count must be a nonnegative integer")
    return value
