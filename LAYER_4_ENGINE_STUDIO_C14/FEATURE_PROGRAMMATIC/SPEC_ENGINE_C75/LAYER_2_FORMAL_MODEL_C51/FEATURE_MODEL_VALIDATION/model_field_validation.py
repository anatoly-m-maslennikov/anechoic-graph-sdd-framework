"""Validate generated dataclass field contracts before an instance write."""

from collections.abc import Mapping
from dataclasses import MISSING, fields, is_dataclass
from typing import get_type_hints

from pydantic import TypeAdapter, ValidationError
from pydantic.dataclasses import is_pydantic_dataclass

from ....FEATURE_TOOLS.ADAPTERS_C30.carriers.content.atom_reference__pub import (
    is_native_atom_reference,
)
from ....FEATURE_TOOLS.ADAPTERS_C30.model.cardinality__pub import (
    cardinality_bounds,
)

from ._model_field_types import _same_types


_SCALAR_ADAPTERS = {
    kind: TypeAdapter(kind) for kind in (bool, int, float, str)
}


def _check_count(name, label, count, cardinality):
    minimum, maximum = cardinality_bounds(cardinality)
    if count < minimum or (maximum is not None and count > maximum):
        raise ValueError(
            f"{name}: {label} count {count} violates {minimum}..{maximum}"
        )


def _validate_nested(value, ancestors):
    if not (
        is_dataclass(value)
        or isinstance(value, (Mapping, list, tuple, set, frozenset))
    ):
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


def _validate_fields(
    model_class, values, ancestors, construct_groups=False, typed_parent=False
):
    model_fields = {field.name: field for field in fields(model_class)}
    admitted = dict(values) if construct_groups else None
    unknown = values.keys() - model_fields.keys()
    if unknown:
        raise ValueError(
            f"Undeclared properties: {', '.join(sorted(map(str, unknown)))}"
        )
    types = get_type_hints(model_class)
    for name, field in model_fields.items():
        present = name in values
        _validate_occurrence(name, field, present)
        if not present:
            continue
        field_type = types[name]
        if (
            typed_parent
            and field.metadata.get("dependent_property_cardinality")
            is not None
            and is_pydantic_dataclass(field_type)
            and not isinstance(values[name], field_type)
        ):
            raise ValueError(
                f"{name}: expected a constructed dependent Property group"
            )
        value = _validate_present_field(
            field,
            field_type,
            values[name],
            ancestors,
            construct_groups,
            typed_parent,
        )
        if construct_groups:
            admitted[name] = value
    return admitted


def _validate_present_field(
    field, field_type, value, ancestors, construct_groups, typed_parent
):
    metadata = field.metadata
    dependents = metadata.get("dependent_property_cardinality")
    if dependents is not None and is_dataclass(field_type):
        try:
            dependent_count, value_count, children = _validate_group(
                field_type,
                value,
                ancestors,
                metadata,
                construct_groups,
                typed_parent,
            )
        except ValueError as error:
            raise ValueError(f"{field.name}.{error}") from error
        _check_count(
            field.name, "dependent Property", dependent_count, dependents
        )
        _check_count(
            field.name, "value", value_count, metadata["value_cardinality"]
        )
        if children is not None:
            try:
                value = field_type(**children)
            except ValidationError as error:
                item = error.errors(include_input=False, include_url=False)[0]
                path = ".".join(map(str, item["loc"]))
                raise ValueError(
                    f"{field.name}.{path}: {item['msg']}"
                    if path
                    else f"{field.name}: {item['msg']}"
                ) from error
    elif dependents is not None and isinstance(value, Mapping):
        _validate_mapping(field, field_type, value, ancestors)
    else:
        _validate_direct_value(field, field_type, value, ancestors)
    return value


def _validate_relation_names(name, value, metadata):
    if names := metadata.get("allowed_relation_names"):
        for relation, targets in value.items():
            if relation not in names:
                raise ValueError(
                    f"{name}.{relation}: undeclared authored Relation"
                )
            if any(not is_native_atom_reference(target) for target in targets):
                raise ValueError(
                    f"{name}.{relation}: expected Atom references"
                )
            if len(set(targets)) != len(targets):
                raise ValueError(
                    f"{name}.{relation}: duplicate Atom reference"
                )


def _validate_group(
    field_type, value, ancestors, metadata, construct_groups, typed_parent
):
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
    construct = (
        construct_groups
        and isinstance(value, Mapping)
        and not isinstance(value, field_type)
        and is_pydantic_dataclass(field_type)
    )
    typed = (
        (construct_groups or typed_parent)
        and isinstance(value, field_type)
        and is_pydantic_dataclass(field_type)
    )
    children = _validate_fields(
        field_type, values, ancestors | {id(value)}, construct, typed
    )
    direct = int(mixed and "value" in values)
    return len(values) - direct, direct, children


def _validate_direct_value(field, field_type, value, ancestors):
    metadata = field.metadata
    if (cardinality := metadata.get("value_cardinality")) is not None:
        count = (
            len(value)
            if isinstance(value, (list, tuple, set, frozenset, Mapping))
            else 1
        )
        _check_count(field.name, "value", count, cardinality)
    _validate_nested(value, ancestors)
    _validate_field_value(field.name, field_type, value, metadata)


def _values_in_domain(values, domain):
    for value in values:
        if value not in domain:
            return False
    return True


def _validate_field_value(name, field_type, value, metadata):
    try:
        adapter = (
            _SCALAR_ADAPTERS.get(field_type)
            if type(field_type) is type
            else None
        )
        validated = (
            adapter if adapter is not None else TypeAdapter(field_type)
        ).validate_python(value, strict=True)
    except ValidationError as error:
        message = error.errors(include_input=False, include_url=False)[0][
            "msg"
        ]
        raise ValueError(f"{name}: {message}") from error
    if not _same_types(value, validated):
        raise ValueError(f"{name}: value requires type conversion")
    values = value if isinstance(value, (list, tuple)) else (value,)
    if "allowed_values" in metadata and not _values_in_domain(
        values, metadata["allowed_values"]
    ):
        raise ValueError(
            f"{name}: value must be one of "
            f"{', '.join(map(str, metadata['allowed_values']))}"
        )
    if "minimum_value" in metadata and not value >= metadata["minimum_value"]:
        raise ValueError(
            f"{name}: value must be at least {metadata['minimum_value']}"
        )
    if "maximum_value" in metadata and not value <= metadata["maximum_value"]:
        raise ValueError(
            f"{name}: value must be at most {metadata['maximum_value']}"
        )


def validate_model_fields(model_class, values, *, construct_groups=False):
    """Validate a proposed mapping and its nested Model dataclass fields."""
    if not isinstance(model_class, type) or not is_dataclass(model_class):
        raise TypeError("Model class must be a dataclass")
    if not isinstance(values, Mapping):
        raise TypeError("Model instance must be a mapping")
    return _validate_fields(
        model_class, values, {id(values)}, construct_groups
    )


def _validate_occurrence(name, field, present):
    occurrence = field.metadata.get("property_occurrence_cardinality")
    cardinality = field.metadata.get("value_cardinality")
    if "property_occurrence_cardinality" not in field.metadata:
        required = (
            cardinality_bounds(cardinality)[0] > 0
            if cardinality is not None
            else field.default is MISSING and field.default_factory is MISSING
        )
        occurrence = 1 if required else {"minimum": 0, "maximum": 1}
    _check_count(name, "occurrence", int(present), occurrence)
    if "value_cardinality" in field.metadata:
        cardinality_bounds(cardinality)


def _validate_mapping(field, field_type, value, ancestors):
    metadata = field.metadata
    dependents = metadata.get("dependent_property_cardinality")
    _check_count(field.name, "dependent Property", len(value), dependents)
    _check_count(field.name, "value", 0, metadata["value_cardinality"])
    if (
        count := metadata.get("dependent_property_value_cardinality")
    ) is not None:
        for key, child in value.items():
            _check_count(
                f"{field.name}.{key}",
                "value",
                len(child) if isinstance(child, list) else 1,
                count,
            )
    _validate_nested(value, ancestors)
    _validate_field_value(field.name, field_type, value, metadata)
    _validate_relation_names(field.name, value, metadata)
