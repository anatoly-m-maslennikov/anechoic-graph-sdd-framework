import ast


_FIELDS = {
    "contract": ("delimiter", "line_endings"),
    "solution": ("opening_prefixes", "closing_prefixes"),
}


def _validate(claim, role):
    if (
        role not in _FIELDS
        or not isinstance(claim, dict)
        or set(claim) != set(_FIELDS[role])
    ):
        raise ValueError("invalid framing role or fields")
    result = {}
    for name in _FIELDS[role]:
        value = claim[name]
        patterns = [value] if name == "delimiter" else value
        if not isinstance(patterns, (list, tuple)) or not patterns:
            raise ValueError("expected nonempty patterns")
        normalized = []
        for pattern in patterns:
            if (
                not isinstance(pattern, (list, tuple))
                or not pattern
                or any(
                    type(b) is not int or not 0 <= b <= 255 for b in pattern
                )
            ):
                raise ValueError("expected nonempty byte pattern")
            normalized.append(tuple(pattern))
        if len(set(normalized)) != len(normalized):
            raise ValueError("duplicate pattern")
        result[name] = (
            normalized[0] if name == "delimiter" else tuple(normalized)
        )
    return result


def _literal_list(node):
    if not isinstance(node, ast.List):
        raise TypeError("expected list literal")
    return [
        _literal_list(n) if isinstance(n, ast.List) else _literal_byte(n)
        for n in node.elts
    ]


def _literal_byte(node):
    if not isinstance(node, ast.Constant) or type(node.value) is not int:
        raise ValueError("expected byte literal")
    return node.value


def parse_framing(source, role):
    "Parse exactly one literal framing declaration; never execute the source."
    if role not in _FIELDS:
        raise ValueError("invalid framing role")
    try:
        tree = ast.parse(source)
        if len(tree.body) != 1 or not isinstance(tree.body[0], ast.Expr):
            raise ValueError("expected one declaration")
        call = tree.body[0].value
        if (
            not isinstance(call, ast.Call)
            or not isinstance(call.func, ast.Name)
            or call.func.id != "declare_framing_" + role
            or call.args
        ):
            raise ValueError("invalid framing declaration")
        names = [item.arg for item in call.keywords]
        if (
            None in names
            or len(set(names)) != len(names)
            or set(names) != set(_FIELDS[role])
        ):
            raise ValueError("invalid framing keywords")

        return _validate(
            {item.arg: _literal_list(item.value) for item in call.keywords},
            role,
        )
    except (SyntaxError, TypeError) as exc:
        raise ValueError("invalid framing source") from exc
