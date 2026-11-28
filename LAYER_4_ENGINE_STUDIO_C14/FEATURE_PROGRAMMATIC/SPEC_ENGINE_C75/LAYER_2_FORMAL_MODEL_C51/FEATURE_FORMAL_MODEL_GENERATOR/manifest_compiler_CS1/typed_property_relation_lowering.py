"""Lower typed properties and relations without executing authored text."""

import ast
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.model.claims.claims__shared import (
    parse_native_model_claim,
)

from .typed._package__shared import (
    _endpoints,
    _field_assignments,
    _parse_field_body,
    _reference,
    _references,
)
from .typed._package__shared import _lower_axis, _lower_property_value


def typed_property_subject(text, addresses):
    """Derive an ordinary Property's scope from its name and bearer."""
    imports, _, _, cls = _parse_field_body(ast.parse(text))
    if cls is None:
        raise ValueError("expected one typed Property class")
    fields, name = _field_assignments(cls, "Property")
    if "axis" in fields or "bearer" not in fields:
        raise ValueError("expected an ordinary Property with a bearer")
    path = _reference(fields["bearer"], imports, addresses).value
    return f"MODEL//ANECHOIC <+ {path}.{name.value}"


def declared_relation_names(records, fields):
    """Collect explicit relation names from the same Model compilation."""
    names = set()
    for _, _, claim in records:
        declaration = parse_native_model_claim(claim)
        args = declaration["arguments"]
        if declaration["kind"] == "relation" and "derived_from" not in args:
            names.add(args["relation_name"])
    for _, _, text, kind in fields:
        if kind == "manifest_relation":
            _, _, _, cls = _parse_field_body(ast.parse(text))
            assignments, name = _field_assignments(cls, "Relation")
            if "derived_from" not in assignments:
                names.add(name.value)
    return tuple(sorted(names))


def _relation_selector(node, method):
    return (
        isinstance(node, ast.Call)
        and not node.args
        and not node.keywords
        and (
            isinstance(node.func, ast.Attribute)
            and node.func.attr == method
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "Relation"
        )
    )


def _lower_relation_domain(
    fields, name, base_path, imports, addresses, relation_names
):
    names = fields.get("allowed_dependent_property")
    children = fields.get("allowed_dependent_property_names")
    if names is None and isinstance(children, ast.Attribute):
        names = children
    targets = _relation_selector(
        fields.get("dependent_property_value_format"), "target_references"
    )
    if names is None and not targets:
        return
    if (
        not (
            isinstance(names, ast.Attribute)
            and names.attr == "name"
            and _relation_selector(names.value, "subclasses")
            and targets
            and "Relation" in imports
            and relation_names
        )
        or ("allowed_dependent_property" in fields and children is not None)
        or name.value != "Relations"
        or base_path.value != addresses.get("Atom.Header")
    ):
        raise ValueError(
            "Atom Relations requires both Relation selectors and a "
            "declared Relation catalog"
        )
    fields.pop("allowed_dependent_property", None)
    fields.pop("allowed_dependent_property_names", None)
    fields["allowed_relation_names"] = ast.Tuple(
        elts=[ast.Constant(item) for item in relation_names], ctx=ast.Load()
    )
    fields["dependent_property_value_format"] = ast.Constant("atom_reference")
    if "value_format" not in fields:
        _set_relation_value_format(fields)


def lower_typed_fields(kind, text, subject, addresses, *, relation_names=()):
    """Return one legacy declaration for validation by the static parser.

    Address-bearing fields require imported Model symbols. Dotted paths
    require exact aliases.
    """
    if kind not in {"manifest_property", "manifest_relation"}:
        raise ValueError(f"unsupported typed field kind: {kind}")
    try:
        tree = ast.parse(text)
    except SyntaxError as error:
        raise ValueError(f"invalid typed field: {error}") from error
    imports, auxiliary_imports, has_value_import, cls = _parse_field_body(tree)
    base = "Property" if kind == "manifest_property" else "Relation"
    if (
        cls is None
        or cls.decorator_list
        or cls.keywords
        or len(cls.bases) != 1
        or not isinstance(cls.bases[0], ast.Name)
        or cls.bases[0].id != base
        or base not in imports
    ):
        raise ValueError(f"expected a class with imported {base} base")
    fields, name = _field_assignments(cls, base)

    if base == "Property" and "axis" in fields:
        return _lower_axis(fields, name, subject, imports, addresses)

    function, args = _lower_field_arguments(
        base,
        fields,
        name,
        imports,
        addresses,
        has_value_import,
        relation_names,
    )
    args.update(fields)
    return _render_typed_fields(function, args, imports, auxiliary_imports)


def _render_typed_fields(function, args, imports, auxiliary_imports):
    model_names = [
        ast.alias(name=n) for n in imports if n not in {"Property", "Relation"}
    ]
    output = [
        ast.ImportFrom(
            module="anechoic.formal_claims",
            names=[ast.alias(name=function)],
            level=0,
        )
    ]
    output.extend(auxiliary_imports)
    if model_names:
        output.append(
            ast.ImportFrom(module="anechoic.model", names=model_names, level=0)
        )
    output.append(
        ast.Expr(
            value=ast.Call(
                func=ast.Name(id=function, ctx=ast.Load()),
                args=[],
                keywords=[
                    ast.keyword(arg=k, value=v) for k, v in args.items()
                ],
            )
        )
    )
    return (
        ast.unparse(
            ast.fix_missing_locations(ast.Module(body=output, type_ignores=[]))
        )
        + "\n"
    )


def _set_relation_value_format(fields):
    options = fields.get("field_options")
    optional = isinstance(options, ast.Dict) and any(
        isinstance(key, ast.Constant)
        and key.value == "default"
        and isinstance(value, ast.Constant)
        and value.value is None
        for key, value in zip(options.keys, options.values, strict=True)
    )
    annotation = (
        "dict[str, list[str]] | None" if optional else "dict[str, list[str]]"
    )
    fields["value_format"] = ast.parse(annotation, mode="eval").body


def _lower_field_arguments(
    base, fields, name, imports, addresses, has_value_import, relation_names
):
    if base == "Property":
        if "bearer" not in fields:
            raise ValueError("property requires bearer")
        base_path = _reference(fields.pop("bearer"), imports, addresses)
        args = {
            "entity_name": name,
            "entity_kind": ast.Constant("Property"),
            "relation_name": ast.Constant("IS_PROPERTY_OF"),
            "base_path": base_path,
        }
        _lower_property_value(fields, has_value_import)
        if isinstance(groups := fields.get("status_groups"), ast.Dict):
            fields.setdefault("allowed_values", ast.Tuple(elts=groups.keys))
        _lower_relation_domain(
            fields, name, base_path, imports, addresses, relation_names
        )
        if "applies_to_entity_classes" in fields:
            fields["applies_to_entity_classes"] = _references(
                fields["applies_to_entity_classes"], imports, addresses
            )
        function = "declare_entity"
    else:
        args = {"relation_name": name}
        for key in ("source_endpoint", "target_endpoint", "endpoint_pairs"):
            if key in fields:
                fields[key] = _endpoints(fields[key], imports, addresses)
        function = "declare_relation"
    return function, args
