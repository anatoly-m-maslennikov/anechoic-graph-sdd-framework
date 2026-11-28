"""Parse typed field declarations and their address references."""

import ast


_PROPERTY_KEYS = {
    "name",
    "bearer",
    "axis",
    "value",
    "value_format",
    "field_options",
    "allowed_values",
    "status_groups",
    "status_group_names",
    "value_cardinality",
    "property_occurrence_cardinality",
    "minimum_value",
    "applies_to_entity_classes",
    "allowed_dependent_property",
    "allowed_dependent_property_names",
    "ordered_dependent_property_pairs",
    "derived_from_properties",
    "dependent_property_cardinality",
    "dependent_property_value_cardinality",
    "dependent_property_value_format",
    "dependent_property_name_format",
    "recursive_dependent_property_cardinality",
    "recursive_dependent_property_name_format",
    "recursive_dependent_property_value_format",
    "ordered_dependent_property_roles",
}


_RELATION_KEYS = {
    "name",
    "source_endpoint",
    "target_endpoint",
    "endpoint_pairs",
    "inverse_alias",
    "written_alias",
    "reverse_written_alias",
    "acyclic",
    "derived_from",
    "forbidden_status_pairs",
    "sources_per_target",
    "targets_per_source",
    "axes",
    "inverse_axes",
}


_PROPERTY_PATHS = {
    "property.cardinality": "property_occurrence_cardinality",
    "property.value.cardinality": "value_cardinality",
    "property.value.format": "value_format",
    "property.value.allowed": "allowed_values",
    "property.value.groups": "status_groups",
    "property.value.group_names": "status_group_names",
    "property.value.minimum": "minimum_value",
    "property.value.derived_from": "derived_from_properties",
    "property.applies_to": "applies_to_entity_classes",
    "property.axis": "axis",
    "property.classification": "axis",
    "property.dependent_property.name.allowed": (
        "allowed_dependent_property_names"
    ),
    "property.dependent_property.cardinality": (
        "dependent_property_cardinality"
    ),
    "property.dependent_property.name.format": (
        "dependent_property_name_format"
    ),
    "property.dependent_property.value.cardinality": (
        "dependent_property_value_cardinality"
    ),
    "property.dependent_property.value.format": (
        "dependent_property_value_format"
    ),
    "property.dependent_property.ordered_pairs": (
        "ordered_dependent_property_pairs"
    ),
    "property.dependent_property.ordered_roles": (
        "ordered_dependent_property_roles"
    ),
    "property.dependent_property.recursive.cardinality": (
        "recursive_dependent_property_cardinality"
    ),
    "property.dependent_property.recursive.name.format": (
        "recursive_dependent_property_name_format"
    ),
    "property.dependent_property.recursive.value.format": (
        "recursive_dependent_property_value_format"
    ),
}


_RELATION_PATHS = {f"relation.{key}": key for key in _RELATION_KEYS - {"name"}}


def _parse_field_body(tree):
    imports = {}
    auxiliary_imports = []
    has_value_import = False
    cls = None
    for node in tree.body:
        if (
            isinstance(node, ast.ImportFrom)
            and node.level == 0
            and node.module == "anechoic.model"
        ):
            for alias in node.names:
                if alias.name == "*" or alias.asname or alias.name in imports:
                    raise ValueError(
                        "Model imports must be unique, unaliased names"
                    )
                imports[alias.name] = True
        elif (
            isinstance(node, ast.ImportFrom)
            and node.level == 0
            and node.module == "anechoic.formal_claims"
        ):
            has_value_import = _formal_imports(
                node, auxiliary_imports, has_value_import
            )
        elif (
            isinstance(node, ast.ImportFrom)
            and node.level == 0
            and node.module == "datetime"
            and all(a.name == "datetime" and not a.asname for a in node.names)
        ):
            auxiliary_imports.append(node)
        elif isinstance(node, ast.ClassDef) and cls is None:
            cls = node
        else:
            raise ValueError(
                "expected Model imports and one typed field class"
            )
    return imports, auxiliary_imports, has_value_import, cls


def _field_assignments(cls, base):
    fields = {}
    for item in cls.body:
        if not isinstance(item, ast.Assign) or len(item.targets) != 1:
            raise ValueError(
                "typed field bodies contain only simple assignments"
            )
        target = item.targets[0]
        key = target.id if isinstance(target, ast.Name) else None
        if isinstance(target, ast.Attribute):
            paths = _PROPERTY_PATHS if base == "Property" else _RELATION_PATHS
            key = paths.get(ast.unparse(target))
        if key == "classification":
            key = "axis"
        if key in fields or key not in (
            _PROPERTY_KEYS if base == "Property" else _RELATION_KEYS
        ):
            raise ValueError(
                f"duplicate or unsupported typed field: {ast.unparse(target)}"
            )
        fields[key] = item.value
    if "name" in fields:
        name = fields.pop("name")
        if (
            not isinstance(name, ast.Constant)
            or not isinstance(name.value, str)
            or not name.value
        ):
            raise ValueError("name must be a nonempty string")
    else:
        name = ast.Constant(cls.name)
    return fields, name


def _reference(node, imports, addresses):
    parts = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if (
        not isinstance(node, ast.Name)
        or node.id not in imports
        or node.id not in addresses
    ):
        raise ValueError(
            "address references must use an imported, unambiguous Model name"
        )
    alias = ".".join([node.id, *reversed(parts)])
    address = addresses.get(alias)
    if not isinstance(address, str) or not address:
        raise ValueError(f"unknown or ambiguous Model reference: {alias}")
    return ast.Constant(address)


def _references(node, imports, addresses):
    if not isinstance(node, (ast.Tuple, ast.List)):
        raise ValueError("address references must be a tuple or list")
    return type(node)(
        elts=[_reference(item, imports, addresses) for item in node.elts],
        ctx=ast.Load(),
    )


def _endpoints(node, imports, addresses):
    if isinstance(node, (ast.Tuple, ast.List)):
        return type(node)(
            elts=[_endpoints(item, imports, addresses) for item in node.elts],
            ctx=ast.Load(),
        )
    if not isinstance(node, ast.Dict):
        raise ValueError("endpoints must be literal dictionaries")
    values = []
    for key, value in zip(node.keys, node.values):
        if not isinstance(key, ast.Constant) or not isinstance(key.value, str):
            raise ValueError("endpoint keys must be strings")
        if key.value == "entity_paths":
            value = _references(value, imports, addresses)
        elif key.value in {"source_endpoint", "target_endpoint"}:
            value = _endpoints(value, imports, addresses)
        values.append(value)
    return ast.Dict(keys=node.keys, values=values)


def _formal_imports(node, auxiliary_imports, has_value_import):
    for alias in node.names:
        if alias.asname or alias.name not in {"Cardinality", "value"}:
            raise ValueError("unsupported formal_claims import")
        if alias.name == "value":
            if has_value_import:
                raise ValueError("duplicate value import")
            has_value_import = True
        else:
            auxiliary_imports.append(
                ast.ImportFrom(module=node.module, names=[alias], level=0)
            )
    return has_value_import
