"""Lower typed property values and classification axes."""

import ast

from ._typed_field_syntax import _reference


def _lower_axis(fields, name, subject, imports, addresses):
    axis = name.value
    bearer = fields.get("bearer")
    if (
        set(fields) != {"bearer", "axis", "allowed_values"}
        or not isinstance(fields["bearer"], ast.Name)
        or not isinstance(fields["axis"], ast.Constant)
        or fields["axis"].value is not True
    ):
        raise ValueError("invalid axis")
    path = _reference(bearer, imports, addresses).value
    values = fields["allowed_values"]
    if (
        not isinstance(values, ast.Tuple)
        or not values.elts
        or any(
            not isinstance(v, ast.Constant)
            or not isinstance(v.value, str)
            or not v.value.strip()
            for v in values.elts
        )
        or len({v.value for v in values.elts}) != len(values.elts)
    ):
        raise ValueError("invalid axis values")
    relation_axis = (bearer.id, path) == ("Relation", "Graph/Relation")
    node_axis = (bearer.id, path) in {
        ("Node", "Graph/Node"),
        ("Axis", "Graph/Axis"),
        ("Classification", "Graph/Classification"),
    }
    if (
        not (relation_axis or node_axis)
        or subject != f"MODEL//ANECHOIC <+ {path} >| {axis}"
    ):
        raise ValueError("invalid axis scope")
    return _render_axis(bearer, axis, fields)


def _lower_property_value(fields, has_value_import):
    if "value" in fields:
        rule = fields.pop("value")
        if (
            not has_value_import
            or not isinstance(rule, ast.Call)
            or not isinstance(rule.func, ast.Name)
            or rule.func.id != "value"
            or rule.args
            or len(rule.keywords) != 1
            or rule.keywords[0].arg not in {"fixed", "default"}
        ):
            raise ValueError(
                "value requires imported value(fixed=...) or "
                "value(default=...)"
            )
        choice = rule.keywords[0]
        if choice.arg == "fixed":
            singleton = ast.Tuple(elts=[choice.value], ctx=ast.Load())
            if "allowed_values" in fields and ast.dump(
                fields["allowed_values"], include_attributes=False
            ) != ast.dump(singleton, include_attributes=False):
                raise ValueError("fixed value conflicts with allowed_values")
            fields["allowed_values"] = singleton
        else:
            _set_property_default(fields, choice)


def _render_axis(bearer, axis, fields):
    declaration = ast.Call(
        func=ast.Name(id="declare_entity", ctx=ast.Load()),
        args=[],
        keywords=[
            ast.keyword(arg="entity_name", value=ast.Constant(bearer.id)),
            ast.keyword(
                arg="allowed_axis_values",
                value=ast.Dict(
                    keys=[ast.Constant(axis)],
                    values=[fields["allowed_values"]],
                ),
            ),
        ],
    )
    output = ast.Module(
        body=[
            ast.ImportFrom(
                module="anechoic.formal_claims",
                names=[ast.alias(name="declare_entity")],
                level=0,
            ),
            ast.Expr(value=declaration),
        ],
        type_ignores=[],
    )
    return ast.unparse(ast.fix_missing_locations(output)) + "\n"


def _set_property_default(fields, choice):
    options = fields.get("field_options", ast.Dict(keys=[], values=[]))
    if not isinstance(options, ast.Dict):
        raise ValueError("field_options must be a literal dictionary")
    keys = [
        k.value if isinstance(k, ast.Constant) else None for k in options.keys
    ]
    if (
        None in keys
        or len(keys) != len(set(keys))
        or "default_factory" in keys
    ):
        raise ValueError("invalid or conflicting field_options")
    if "default" in keys:
        current = options.values[keys.index("default")]
        if ast.dump(current, include_attributes=False) != ast.dump(
            choice.value, include_attributes=False
        ):
            raise ValueError("value default conflicts with field_options")
    else:
        options.keys.append(ast.Constant("default"))
        options.values.append(choice.value)
    fields["field_options"] = options
