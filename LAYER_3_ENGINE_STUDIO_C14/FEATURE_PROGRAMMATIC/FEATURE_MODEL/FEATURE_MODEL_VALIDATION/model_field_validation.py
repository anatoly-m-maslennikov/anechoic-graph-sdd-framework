"""Validate generated dataclass field contracts before an instance write."""

from collections.abc import Mapping
from dataclasses import MISSING, fields, is_dataclass
from typing import get_type_hints

from pydantic import TypeAdapter, ValidationError

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.cardinality__pub import cardinality_bounds


def _check_count(name, label, count, cardinality):
    minimum, maximum = cardinality_bounds(cardinality)
    if count < minimum or (maximum is not None and count > maximum):
        raise ValueError(f"{name}: {label} count {count} violates {minimum}..{maximum}")


def _same_types(original, validated):
    if type(original) is not type(validated):
        return False
    if isinstance(original, Mapping):
        return all(_same_types(key, new_key) and _same_types(value, validated[new_key])
                   for (key, value), new_key in zip(original.items(), validated, strict=True))
    if isinstance(original, (list, tuple)):
        return all(_same_types(old, new) for old, new in zip(original, validated, strict=True))
    if isinstance(original, (set, frozenset)):
        return all(any(_same_types(old, new) and old == new for new in validated) for old in original)
    return True


def _validate_nested(value, ancestors):
    if not (is_dataclass(value) or isinstance(value, (Mapping, list, tuple, set, frozenset))):
        return
    if id(value) in ancestors:
        raise ValueError("Dependent Properties contain a cycle")
    branch = ancestors | {id(value)}
    if is_dataclass(value) and not isinstance(value, type):
        values = dict(getattr(value, "__dict__", {}))
        for field in fields(value):
            if hasattr(value, field.name):
                values[field.name] = getattr(value, field.name)
        _validate_fields(type(value), values, branch)
    elif isinstance(value, Mapping):
        for child in value.values():
            _validate_nested(child, branch)
    elif isinstance(value, (list, tuple, set, frozenset)):
        for child in value:
            _validate_nested(child, branch)


def _validate_fields(model_class, values, ancestors):
    model_fields = {field.name: field for field in fields(model_class)}
    unknown = values.keys() - model_fields.keys()
    if unknown:
        raise ValueError(f"Undeclared properties: {', '.join(sorted(map(str, unknown)))}")
    types = get_type_hints(model_class)
    for name, field in model_fields.items():
        present = name in values
        occurrence = field.metadata.get("property_occurrence_cardinality")
        cardinality = field.metadata.get("value_cardinality")
        if "property_occurrence_cardinality" not in field.metadata:
            required = (cardinality_bounds(cardinality)[0] > 0 if cardinality is not None
                        else field.default is MISSING and field.default_factory is MISSING)
            occurrence = 1 if required else {"minimum": 0, "maximum": 1}
        _check_count(name, "occurrence", int(present), occurrence)
        if "value_cardinality" in field.metadata:
            cardinality_bounds(cardinality)
        if not present:
            continue
        _validate_present_field(field, types[name], values[name], ancestors)


def _validate_present_field(field, field_type, value, ancestors):
    metadata = field.metadata
    dependents = metadata.get("dependent_property_cardinality")
    if dependents is not None and is_dataclass(field_type):
        try:
            dependent_count, value_count = _validate_group(field_type, value, ancestors, metadata)
        except ValueError as error:
            raise ValueError(f"{field.name}.{error}") from error
        _check_count(field.name, "dependent Property", dependent_count, dependents)
        _check_count(field.name, "value", value_count, metadata["value_cardinality"])
    elif dependents is not None and isinstance(value, Mapping):
        _check_count(field.name, "dependent Property", len(value), dependents)
        _check_count(field.name, "value", 0, metadata["value_cardinality"])
        if (count := metadata.get("dependent_property_value_cardinality")) is not None:
            for key, child in value.items():
                _check_count(f"{field.name}.{key}", "value", len(child) if isinstance(child, list) else 1, count)
        _validate_nested(value, ancestors)
        _validate_field_value(field.name, field_type, value, metadata)
    else:
        _validate_direct_value(field, field_type, value, ancestors)


def _validate_group(field_type, value, ancestors, metadata):
    mixed = cardinality_bounds(metadata["value_cardinality"])[1] != 0
    if isinstance(value, field_type):
        values = dict(getattr(value, "__dict__", {}))
        for child in fields(value):
            if not hasattr(value, child.name):
                continue
            field_value = getattr(value, child.name)
            if field_value is None and child.default is None:
                values.pop(child.name, None)
            else:
                values[child.name] = field_value
    elif isinstance(value, Mapping):
        values = value
    else:
        raise ValueError("expected a dependent Property group")
    if id(value) in ancestors:
        raise ValueError("Dependent Properties contain a cycle")
    _validate_fields(field_type, values, ancestors | {id(value)})
    direct = int(mixed and "value" in values)
    return len(values) - direct, direct


def _validate_direct_value(field, field_type, value, ancestors):
    metadata = field.metadata
    if (cardinality := metadata.get("value_cardinality")) is not None:
        count = len(value) if isinstance(value, (list, tuple, set, frozenset, Mapping)) else 1
        _check_count(field.name, "value", count, cardinality)
    _validate_nested(value, ancestors)
    _validate_field_value(field.name, field_type, value, metadata)


def _validate_field_value(name, field_type, value, metadata):
    try:
        validated = TypeAdapter(field_type).validate_python(value, strict=True)
    except ValidationError as error:
        message = error.errors(include_input=False, include_url=False)[0]["msg"]
        raise ValueError(f"{name}: {message}") from error
    if not _same_types(value, validated):
        raise ValueError(f"{name}: value requires type conversion")
    values = value if isinstance(value, (list, tuple)) else (value,)
    if "allowed_values" in metadata and any(item not in metadata["allowed_values"] for item in values):
        raise ValueError(f"{name}: value must be one of {', '.join(map(str, metadata['allowed_values']))}")
    if "minimum_value" in metadata and not value >= metadata["minimum_value"]:
        raise ValueError(f"{name}: value must be at least {metadata['minimum_value']}")
    if "maximum_value" in metadata and not value <= metadata["maximum_value"]:
        raise ValueError(f"{name}: value must be at most {metadata['maximum_value']}")


def validate_model_fields(model_class, values):
    """Validate a proposed mapping and its nested Model dataclass fields."""
    if not isinstance(model_class, type) or not is_dataclass(model_class):
        raise TypeError("Model class must be a dataclass")
    if not isinstance(values, Mapping):
        raise TypeError("Model instance must be a mapping")
    _validate_fields(model_class, values, {id(values)})
