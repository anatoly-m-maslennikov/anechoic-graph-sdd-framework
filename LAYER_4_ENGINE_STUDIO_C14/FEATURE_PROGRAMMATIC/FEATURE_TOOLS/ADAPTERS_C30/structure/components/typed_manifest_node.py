"""Statically read the initial typed node manifest syntax."""

import ast

NODE_LINK_PREFIX = "=>"

_DOTTED_FIELDS = {
    "identity",
    "axes",
    "classifications",
    "ssot_carrier",
    "creation_enabled",
    "template",
    "tier",
    "lens",
    "container_type",
    "lens_path",
    "control_flow",
    "parts",
    "alternatives",
    "aliases",
}


def parse_typed_manifest_node(text):
    "Read a node and its value rules without executing the authored source."
    try:
        tree = ast.parse(text)
    except SyntaxError as error:
        raise ValueError(f"invalid typed manifest: {error.msg}") from error
    if len(tree.body) == 1 and isinstance(tree.body[0], ast.Expr):
        return _marker(tree.body[0].value)
    imports, node = _imports_and_node(tree)
    if (
        node is None
        or node.decorator_list
        or node.keywords
        or any(not isinstance(base, ast.Name) for base in node.bases)
    ):
        raise ValueError("typed node requires one plain base class")
    bases = tuple(base.id for base in node.bases)
    if any(imports.get(base) != "anechoic.model" for base in bases):
        raise ValueError("typed node bases must be imported")
    values, identity, axes, metadata = _node_values(node, imports)
    return {
        "name": node.name,
        "bases": bases,
        "identity": identity,
        "values": values,
        "axes": axes,
        **metadata,
    }


def _imports_and_node(tree):
    imports, node = {}, None
    for item in tree.body:
        if (
            isinstance(item, ast.ImportFrom)
            and item.level == 0
            and item.module in {"anechoic.model", "anechoic.formal_claims"}
        ):
            for alias in item.names:
                if alias.asname or alias.name == "*" or alias.name in imports:
                    raise ValueError(
                        "typed manifest imports must be distinct and unaliased"
                    )
                imports[alias.name] = item.module
        elif isinstance(item, ast.ClassDef) and node is None:
            node = item
        else:
            raise ValueError(
                "typed manifest allows only imports and one class"
            )
    return imports, node


def _marker(call):
    if (
        not isinstance(call, ast.Call)
        or not isinstance(call.func, ast.Name)
        or call.func.id != "node"
        or call.keywords
        or not call.args
        or any(not isinstance(arg, ast.Name) for arg in call.args)
    ):
        raise ValueError(
            "typed node marker requires a name and optional bases"
        )
    name, *bases = (arg.id for arg in call.args)
    if len(bases) != len(set(bases)) or set(bases) & {
        "Property",
        "Relation",
        "NodeConstraints",
    }:
        raise ValueError("invalid typed node bases")
    return {
        "name": name,
        "bases": tuple(bases),
        "identity": None,
        "values": {},
        "axes": None,
    }


def _node_values(node, imports):
    values, identity, axes, metadata = {}, None, None, {}
    for item in node.body:
        if isinstance(item, ast.Pass) and len(node.body) == 1:
            continue
        if not isinstance(item, ast.Assign) or len(item.targets) != 1:
            raise ValueError("typed node body requires value assignments")
        name = _assignment_name(item.targets[0])
        call = item.value
        if name in {"parts", "alternatives", "aliases"}:
            if name in metadata or not isinstance(
                item.targets[0], ast.Attribute
            ):
                raise ValueError(f"duplicate or invalid node.{name}")
            metadata[name] = _node_metadata(name, call, imports)
            continue
        if name in {"axes", "classifications"}:
            if axes is not None:
                raise ValueError(
                    "axes requires a nonempty literal text mapping"
                )
            axes = _axes(call)
            continue
        if name == "identity":
            if identity is not None or not (
                isinstance(call, ast.Attribute)
                and call.attr == "atom_id"
                and isinstance(call.value, ast.Name)
                and call.value.id == "header"
            ):
                raise ValueError("unsupported identity path")
            identity = "Header.Atom ID"
            continue
        values[name] = _value_assignment(name, call, values, imports)
    return values, identity, axes, metadata


def _value_assignment(name, call, values, imports):
    if imports.get("value") != "anechoic.formal_claims":
        raise ValueError("value must be imported")
    if (
        name in values
        or not isinstance(call, ast.Call)
        or not isinstance(call.func, ast.Name)
        or call.func.id != "value"
        or call.args
        or len(call.keywords) != 1
        or call.keywords[0].arg not in {"fixed", "default"}
    ):
        raise ValueError("value requires one fixed or default argument")
    return _decode_value(call, imports)


def _assignment_name(target):
    match target:
        case ast.Name(id=name):
            return name
        case ast.Attribute(value=ast.Name(id="node"), attr=name) if (
            name in _DOTTED_FIELDS
        ):
            return name
        case _:
            raise ValueError("typed node body requires value assignments")


def _decode_value(call, imports):
    expression = call.keywords[0].value
    if isinstance(expression, ast.Constant) and type(expression.value) in (
        str,
        int,
        float,
        bool,
        type(None),
    ):
        decoded = expression.value
    elif (
        isinstance(expression, ast.UnaryOp)
        and isinstance(expression.op, (ast.UAdd, ast.USub))
        and isinstance(expression.operand, ast.Constant)
        and type(expression.operand.value) in (int, float)
    ):
        decoded = ast.literal_eval(expression)
    elif (
        isinstance(expression, ast.Name)
        and imports.get(expression.id) == "anechoic.model"
    ):
        decoded = ("type", expression.id)
    elif (
        isinstance(expression, ast.Attribute)
        and isinstance(expression.value, ast.Name)
        and expression.value.id == "Lens"
        and imports.get("Lens") == "anechoic.model"
        and expression.attr == "SPEC"
    ):
        decoded = "SPEC"
    else:
        raise ValueError("unsupported typed manifest value")
    return call.keywords[0].arg, decoded


def _axes(call):
    if (
        not isinstance(call, ast.Dict)
        or not call.keys
        or any(
            not isinstance(key, ast.Constant)
            or not isinstance(key.value, str)
            or not key.value.strip()
            for key in call.keys
        )
        or any(
            not isinstance(value, ast.Constant)
            or not isinstance(value.value, str)
            or not value.value.strip()
            for value in call.values
        )
    ):
        raise ValueError("axes requires a nonempty literal text mapping")
    keys = [key.value for key in call.keys]
    if len(keys) != len(set(keys)):
        raise ValueError("duplicate axis")
    return dict(zip(keys, (value.value for value in call.values), strict=True))


def _node_metadata(name, expression, imports):
    def target(value):
        if (
            not isinstance(value, ast.Name)
            or imports.get(value.id) != "anechoic.model"
        ):
            raise ValueError(
                f"node.{name} targets must be imported Model classes"
            )
        return value.id

    if name == "aliases":
        return _aliases(expression)
    if name == "parts":
        if not isinstance(expression, ast.Dict) or not expression.keys:
            raise ValueError("node.parts requires a nonempty literal mapping")
        labels = [
            key.value if isinstance(key, ast.Constant) else None
            for key in expression.keys
        ]
        names = [
            label.removeprefix(NODE_LINK_PREFIX)
            if isinstance(label, str)
            else ""
            for label in labels
        ]
        if any(
            not name
            or name != name.strip()
            or any(char in name for char in "/\n\r@=>")
            for name in names
        ) or len(labels) != len(set(labels)):
            raise ValueError("node.parts requires distinct valid labels")
        return dict(
            zip(
                labels,
                (target(value) for value in expression.values),
                strict=True,
            )
        )
    return _alternatives(expression)


def _aliases(expression):
    if (
        not isinstance(expression, (ast.Tuple, ast.List))
        or not expression.elts
    ):
        raise ValueError(
            "node.aliases requires nonempty distinct ordinary names"
        )
    names = [
        value.value if isinstance(value, ast.Constant) else None
        for value in expression.elts
    ]
    if any(
        not isinstance(value, str)
        or not value
        or value != value.strip()
        or any(char in value for char in "/\n\r@=>")
        for value in names
    ) or len(names) != len(set(names)):
        raise ValueError(
            "node.aliases requires nonempty distinct ordinary names"
        )
    return tuple(names)


def _alternatives(expression):
    if (
        not isinstance(expression, (ast.Tuple, ast.List))
        or not expression.elts
    ):
        raise ValueError("node.alternatives requires nonempty groups")
    groups = []
    for group in expression.elts:
        if not isinstance(group, (ast.Tuple, ast.List)) or not group.elts:
            raise ValueError("node.alternatives requires nonempty groups")
        if any(
            not isinstance(value, ast.Constant)
            or not isinstance(value.value, str)
            or not value.value
            for value in group.elts
        ):
            raise ValueError("node.alternatives members must be part labels")
        members = tuple(value.value for value in group.elts)
        if len(members) != len(set(members)) or frozenset(members) in map(
            frozenset, groups
        ):
            raise ValueError(
                "node.alternatives requires distinct groups and members"
            )
        groups.append(members)
    return tuple(groups)
