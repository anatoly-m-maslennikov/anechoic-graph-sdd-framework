"""Decode literal dataclass field contracts from parsed Model Claims."""
from collections.abc import Mapping
import re
from typing import Any


def has_dataclass_field_contracts(declaration: Mapping[str, Any]) -> bool:
    keys = {"property_occurrence_cardinality", "value_cardinality"}
    classes = declaration.get("classes", ())
    if not isinstance(classes, (tuple, list)):
        return False
    for cls in classes:
        if not isinstance(cls, Mapping):
            continue
        for field in cls.get("fields", ()):
            if not isinstance(field, Mapping) or not isinstance(field.get("field"), Mapping):
                continue
            metadata = field["field"].get("metadata")
            if isinstance(metadata, Mapping) and keys.intersection(metadata):
                return True
    return False


def validate_field_contracts(declaration):
    if not has_dataclass_field_contracts(declaration):
        return
    classes = declaration["classes"]
    keys = {"property_occurrence_cardinality", "value_cardinality"}
    args = declaration["arguments"]
    if set(args) - {"entity_name", "entity_class", "incoming_model_relations"} or not {"entity_name", "entity_class"} <= set(args):
        raise ValueError("unsupported dataclass field contract declaration")
    if (len(classes) != 1 or classes[0]["name"] != args["entity_class"]
            or classes[0]["bases"] or classes[0]["dataclass"] is None):
        raise ValueError("field contracts require the declared dataclass with no base")

    for field in classes[0]["fields"]:
        options = field.get("field", {})
        if set(options) != {"metadata"}:
            raise ValueError("unsupported dataclass field contract")
        metadata = options["metadata"]
        if not isinstance(metadata, dict) or set(metadata) != keys:
            raise ValueError("field contracts require occurrence and value cardinalities")
        _name(args["entity_name"])
        _name(field["name"])
        _cardinality(metadata["property_occurrence_cardinality"])
        if field["annotation"] not in {"str", "int", "float", "bool", "datetime", "markdown", "atom_id"}:
            raise ValueError(f"unsupported compiler format: {field['annotation']!r}")
        _cardinality(metadata["value_cardinality"])
    _validate_incoming(args)


def _validate_incoming(args):
    incoming = args.get("incoming_model_relations", ())
    if not isinstance(incoming, tuple):
        raise ValueError("incoming model relations must be a tuple")
    for relation in incoming:
        if not isinstance(relation, dict) or set(relation) != {"source", "relation", "source_cardinality", "target_cardinality"}:
            raise ValueError("invalid incoming model relation")
        _name(relation["source"])
        _cardinality(relation["source_cardinality"])
        _name(relation["relation"], relation=True)
        _cardinality(relation["target_cardinality"])
        _name(args["entity_name"])


def _name(value, *, relation=False):
    pattern = r"[A-Za-z_][A-Za-z_0-9]*" if relation else r"[A-Za-z_][A-Za-z_0-9 .-]*"
    if not isinstance(value, str) or not re.fullmatch(pattern, value) or value != value.strip():
        raise ValueError(f"unsupported compiler name: {value!r}")


def _cardinality(value):
    if type(value) is int and value >= 0:
        return
    if (not isinstance(value, dict) or set(value) != {"minimum", "maximum"}
            or type(value["minimum"]) is not int or value["minimum"] < 0
            or (value["maximum"] is not None and
                (type(value["maximum"]) is not int or value["maximum"] < value["minimum"]))):
        raise ValueError(f"unsupported cardinality: {value!r}")
