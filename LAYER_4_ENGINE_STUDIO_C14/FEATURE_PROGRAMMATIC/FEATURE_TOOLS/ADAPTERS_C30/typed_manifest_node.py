"""Statically read the initial typed node manifest syntax."""

import ast

_DOTTED_FIELDS = {
    "identity", "classifications", "tier", "lens", "container_type", "lens_path", "control_flow",
}


def parse_typed_manifest_node(text):
    """Read a node and its value rules without executing the authored source."""
    try:
        tree = ast.parse(text)
    except SyntaxError as error:
        raise ValueError(f"invalid typed manifest: {error.msg}") from error
    imports, node = {}, None
    for item in tree.body:
        if isinstance(item, ast.ImportFrom) and item.level == 0 and item.module in {"anechoic.model", "anechoic.formal_claims"}:
            for alias in item.names:
                if alias.asname or alias.name == "*" or alias.name in imports:
                    raise ValueError("typed manifest imports must be distinct and unaliased")
                imports[alias.name] = item.module
        elif isinstance(item, ast.ClassDef) and node is None:
            node = item
        else:
            raise ValueError("typed manifest allows only imports and one class")
    if node is None or node.decorator_list or node.keywords or any(not isinstance(base, ast.Name) for base in node.bases):
        raise ValueError("typed node requires one plain base class")
    bases = tuple(base.id for base in node.bases)
    if any(imports.get(base) != "anechoic.model" for base in bases):
        raise ValueError("typed node bases must be imported")
    values, identity, classifications = _node_values(node, imports)
    return {"name": node.name, "bases": bases, "identity": identity, "values": values,
            "classifications": classifications}


def _node_values(node, imports):
    values, identity, classifications = {}, None, None
    for item in node.body:
        if isinstance(item, ast.Pass) and len(node.body) == 1:
            continue
        if not isinstance(item, ast.Assign) or len(item.targets) != 1:
            raise ValueError("typed node body requires value assignments")
        match item.targets[0]:
            case ast.Name(id=name):
                pass
            case ast.Attribute(value=ast.Name(id="node"), attr=name) if name in _DOTTED_FIELDS:
                pass
            case _:
                raise ValueError("typed node body requires value assignments")
        call = item.value
        if name == "classifications":
            if classifications is not None:
                raise ValueError("classifications requires a nonempty literal text mapping")
            classifications = _classifications(call)
            continue
        if name == "identity":
            if identity is not None or not (isinstance(call, ast.Attribute) and call.attr == "atom_id"
                    and isinstance(call.value, ast.Name) and call.value.id == "header"):
                raise ValueError("unsupported identity path")
            identity = "Header.Atom ID"
            continue
        if imports.get("value") != "anechoic.formal_claims":
            raise ValueError("value must be imported")
        if name in values or not isinstance(call, ast.Call) or not isinstance(call.func, ast.Name) or call.func.id != "value" or call.args or len(call.keywords) != 1 or call.keywords[0].arg not in {"fixed", "default"}:
            raise ValueError("value requires one fixed or default argument")
        expression = call.keywords[0].value
        if isinstance(expression, ast.Constant) and type(expression.value) in (str, int, float, bool, type(None)):
            decoded = expression.value
        elif (isinstance(expression, ast.UnaryOp) and isinstance(expression.op, (ast.UAdd, ast.USub))
              and isinstance(expression.operand, ast.Constant)
              and type(expression.operand.value) in (int, float)):
            decoded = ast.literal_eval(expression)
        elif isinstance(expression, ast.Name) and imports.get(expression.id) == "anechoic.model":
            decoded = ("type", expression.id)
        elif (isinstance(expression, ast.Attribute) and isinstance(expression.value, ast.Name)
              and expression.value.id == "Lens" and imports.get("Lens") == "anechoic.model"
              and expression.attr == "SPEC"):
            decoded = "SPEC"
        else:
            raise ValueError("unsupported typed manifest value")
        values[name] = (call.keywords[0].arg, decoded)
    return values, identity, classifications


def _classifications(call):
    if (not isinstance(call, ast.Dict) or not call.keys
            or any(not isinstance(key, ast.Constant) or not isinstance(key.value, str) or not key.value.strip()
                   for key in call.keys)
            or any(not isinstance(value, ast.Constant) or not isinstance(value.value, str) or not value.value.strip()
                   for value in call.values)):
        raise ValueError("classifications requires a nonempty literal text mapping")
    keys = [key.value for key in call.keys]
    if len(keys) != len(set(keys)):
        raise ValueError("duplicate classification axis")
    return dict(zip(keys, (value.value for value in call.values), strict=True))
