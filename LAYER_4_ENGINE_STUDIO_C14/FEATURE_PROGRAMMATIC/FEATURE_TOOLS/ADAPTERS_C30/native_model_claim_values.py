"""Read Python Model Declarations without importing or executing authored code."""

from __future__ import annotations

import ast
from typing import Any


class NativeModelClaimError(ValueError):
    """A native Model Claim cannot be read safely."""


_DECLARATIONS = {"declare_entity": "entity", "declare_relation": "relation"}
_BUILTINS = {"str", "int", "bool", "float", "bytes", "list", "tuple", "dict", "set", "object"}
_IMPORTS = {
    "anechoic.formal_claims": {"declare_entity", "declare_relation", "Cardinality"},
    "datetime": {"date", "datetime", "time", "timedelta"},
    "dataclasses": {"dataclass", "field"},
    "typing": {"Annotated", "ClassVar", "Literal", "Optional"},
    "__future__": {"annotations"},
}
_COUNT_KEYS = {
    "property_occurrence_cardinality", "value_cardinality",
    "dependent_property_cardinality", "dependent_property_value_cardinality",
    "recursive_dependent_property_cardinality", "instance_population_cardinality",
    "targets_per_source", "sources_per_target",
}
_ENDPOINT_KEYS = {
    "level", "entity_paths", "reference_form", "dependency", "axis",
    "ephemeral", "address_form",
}
_ENDPOINT_LEVELS = {"model_entities", "instances", "model_entities_or_instances"}

_DECLARATION_KEYS = {
    "declare_entity": {
        "entity_name", "entity_class", "ssot_carrier_path", "creation_enabled", "instance", "instance_check", "qualification_property_path", "incoming_model_relations", "structure_paths", "aspect_memberships",
        "entity_kind", "identity_properties", "field_options", "derived_from_properties", "constraints_for",
        "relation_name", "base_path", "value_format", "value_cardinality", "property_occurrence_cardinality",
        "dependent_property_cardinality", "dependent_property_name_format", "dependent_property_value_format",
        "dependent_property_value_cardinality",
        "recursive_dependent_property_cardinality", "recursive_dependent_property_name_format",
        "recursive_dependent_property_value_format", "ordered_dependent_property_roles",
        "allowed_dependent_property_names", "ordered_dependent_property_pairs", "allowed_values", "allowed_relation_names",
        "minimum_value", "applies_to_entity_classes",
        "instance_population_cardinality", "instance_population_scope", "population_entity_path", "population_functional_dependencies", "population_unique_constraints", "axes", "allowed_axis_values", "fallback_property_name", "fallback_value", "fallback_chain", "maximum_value",
        "required_instance_property_values", "instance_property_constraints", "model_relation_constraints",
        "instance_relation_constraints", "status_order_numbers", "applies_to_role", "applies_to_forms", "status_groups",
        "form_roles", "form_content", "project_form_content",
    },
    "declare_relation": {
        "relation_name", "source_endpoint", "target_endpoint", "endpoint_pairs", "inverse_alias", "written_alias", "derived_from",
        "reverse_written_alias", "targets_per_source", "sources_per_target", "acyclic",
        "same_immediate_bearer", "swap_endpoints", "swap_endpoint_cardinalities",
        "axes", "inverse_axes", "forbidden_status_pairs",
    },
}
_RELATION_CONSTRAINT_KEYS = {"target_entity_paths", "targets_per_source", "sources_per_target"}
_PROPERTY_CONSTRAINT_KEYS = {"value_cardinality"}


def _fail(node: ast.AST, message: str) -> None:
    raise NativeModelClaimError(
        f"line {getattr(node, 'lineno', 1)}, column {getattr(node, 'col_offset', 0) + 1}: {message}"
    )


def _keywords(call: ast.Call) -> dict[str, ast.AST]:
    if call.args:
        _fail(call, "only named arguments are supported")
    result: dict[str, ast.AST] = {}
    for keyword in call.keywords:
        if keyword.arg is None:
            _fail(keyword, "expanded keyword arguments are unsupported")
        if keyword.arg in result:
            _fail(keyword, f"duplicate argument: {keyword.arg}")
        result[keyword.arg] = keyword.value
    return result


def _dictionary(node: ast.Dict, names: set[str]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in zip(node.keys, node.values, strict=True):
        if not isinstance(key, ast.Constant) or not isinstance(key.value, str):
            _fail(node, "dictionary keys must be literal strings")
        if key.value in result:
            _fail(key, f"duplicate dictionary key: {key.value}")
        result[key.value] = _value(value, names)
    return result


def _cardinality(node: ast.Call, names: set[str]) -> dict[str, int | None]:
    if "Cardinality" not in names:
        _fail(node, "Cardinality must be imported")
    arguments = _keywords(node)
    if set(arguments) != {"minimum", "maximum"}:
        _fail(node, "Cardinality requires minimum and maximum")
    minimum = _value(arguments["minimum"], names)
    maximum = _value(arguments["maximum"], names)
    if type(minimum) is not int or minimum < 0:
        _fail(node, "Cardinality minimum must be a nonnegative integer")
    if maximum is not None and (type(maximum) is not int or maximum < minimum):
        _fail(node, "Cardinality maximum must be at least minimum or None")
    return {"minimum": minimum, "maximum": maximum}


def _validate_cardinalities(value: Any, node: ast.AST) -> None:
    if isinstance(value, (tuple, list)):
        for item in value:
            _validate_cardinalities(item, node)
    elif isinstance(value, dict):
        for key, item in value.items():
            if key in _COUNT_KEYS:
                exact = type(item) is int and item >= 0
                bounded = (
                    isinstance(item, dict) and set(item) == {"minimum", "maximum"}
                    and type(item["minimum"]) is int and item["minimum"] >= 0
                    and (item["maximum"] is None or (
                        type(item["maximum"]) is int and item["maximum"] >= item["minimum"]
                    ))
                )
                if not (exact or bounded):
                    _fail(node, f"invalid {key} cardinality")
            else:
                _validate_cardinalities(item, node)


def _validate_endpoint(value: Any, label: str, node: ast.AST) -> None:
    if isinstance(value, dict) and "classification_axis" in value:
        if "axis" in value:
            _fail(node, f"{label} has duplicate axis flags")
        value["axis"] = value.pop("classification_axis")
    if not isinstance(value, dict) or set(value) - _ENDPOINT_KEYS:
        _fail(node, f"{label} must be a supported endpoint mapping")
    value.setdefault("level", "model_entities_or_instances")
    if value.get("level") not in _ENDPOINT_LEVELS:
        _fail(node, f"{label} requires an admitted level")
    if "entity_paths" in value:
        paths = value["entity_paths"]
        if (not isinstance(paths, (list, tuple)) or not paths
                or any(not isinstance(path, str) or not path.strip() or path != path.strip()
                       for path in paths)):
            _fail(node, f"{label} entity_paths must be nonempty paths")
    for key in ("reference_form", "dependency", "address_form"):
        if key in value and (not isinstance(value[key], str) or not value[key].strip()):
            _fail(node, f"{label} {key} must be a nonempty string")
    for key in ("axis", "ephemeral"):
        if key in value and type(value[key]) is not bool:
            _fail(node, f"{label} {key} must be a boolean")


def _value(node: ast.AST, names: set[str]) -> Any:  # noqa: C901
    if isinstance(node, ast.Constant):
        if node.value is None or type(node.value) in {str, int, float, bool}:
            return node.value
    if isinstance(node, ast.Name):
        if node.id in names or node.id in _BUILTINS:
            return node.id
        _fail(node, f"unbound symbol: {node.id}")
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        number = _value(node.operand, names)
        if type(number) in {int, float}:
            return -number
    if isinstance(node, (ast.Tuple, ast.List)):
        values = [_value(value, names) for value in node.elts]
        return tuple(values) if isinstance(node, ast.Tuple) else values
    if isinstance(node, ast.Dict):
        return _dictionary(node, names)
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "Cardinality":
        return _cardinality(node, names)
    _fail(node, "unsupported expression")


def _annotation(node: ast.AST, names: set[str]) -> str:
    """Validate and preserve an annotation without evaluating forward references."""
    if isinstance(node, ast.Name):
        if node.id not in names and node.id not in _BUILTINS:
            _fail(node, f"unbound annotation: {node.id}")
    elif isinstance(node, ast.Constant):
        if node.value is not None and not isinstance(node.value, (str, int, bool)):
            _fail(node, "unsupported annotation literal")
    elif isinstance(node, ast.Subscript):
        _annotation(node.value, names)
        _annotation(node.slice, names)
    elif isinstance(node, ast.Tuple):
        for part in node.elts:
            _annotation(part, names)
    elif isinstance(node, ast.BinOp) and isinstance(node.op, ast.BitOr):
        _annotation(node.left, names)
        _annotation(node.right, names)
    else:
        _fail(node, "unsupported annotation")
    return ast.unparse(node)


def _manifest_property_annotation(node, imports):
    if any(isinstance(part, ast.Constant) and part.value is not None for part in ast.walk(node)):
        _fail(node, "Property value formats must use types directly")
    names = {"datetime"} if imports.get("datetime") == "datetime" else set()
    return _annotation(node, names)


def _manifest_field_options(node):
    if not isinstance(node, ast.Dict):
        _fail(node, "field_options must be a literal mapping")
    options = _dictionary(node, set())
    if (options.keys() - {"default", "default_factory", "kw_only", "class_var"}
            or any(type(options[key]) is not bool for key in ("kw_only", "class_var") if key in options)
            or ("default_factory" in options and (
                options["default_factory"] not in ("dict", "list", "set", "tuple") or "default" in options))
            or (options.get("class_var") and (options.keys() - {"class_var", "default"} or "default" not in options))):
        _fail(node, "unsupported Property field options")
    return options


def _validate_manifest_arguments(arguments, node):
    kind = arguments.get("entity_kind")
    if "entity_kind" in arguments and kind not in ("Primary", "Property"):
        _fail(node, "entity_kind must be Primary or Property")
    if kind == "Property" and arguments.get("relation_name") != "IS_PROPERTY_OF":
        _fail(node, "Property must declare its bearer through IS_PROPERTY_OF")
    for key, required_kind in (("identity_properties", "Primary"), ("derived_from_properties", "Property")):
        if key not in arguments:
            continue
        items = arguments[key]
        if (kind != required_kind or not isinstance(items, tuple) or not items
                or any(not isinstance(item, str) or not item.strip() for item in items)
                or len(set(items)) != len(items)):
            _fail(node, f"{key} requires distinct Property paths on a {required_kind} declaration")
    if "creation_enabled" in arguments and (kind != "Primary" or type(arguments["creation_enabled"]) is not bool):
        _fail(node, "creation_enabled requires a boolean on a Primary declaration")
    if "field_options" in arguments and kind != "Property":
        _fail(node, "Only a Property can declare field_options")
    if "constraints_for" in arguments:
        owner = arguments["constraints_for"]
        if (not isinstance(owner, str) or not owner.strip() or kind is not None
                or set(arguments) - {"entity_name", "constraints_for", "instance_check",
                                     "model_relation_constraints", "instance_relation_constraints", "population_unique_constraints"}):
            _fail(node, "constraints_for requires a separate class constraint declaration")


