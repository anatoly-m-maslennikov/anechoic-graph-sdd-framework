"""Project native field and incoming-relation constraints."""

from ..primitives.primitives__shared import _named_property_count, _record
from ._native_claim_helper_primitives import (
    _count_text,
    _native_count,
    _native_relation,
)


def _project_field(field, args, source, rows):
    meta = field["field"]["metadata"]
    occurrence, values = (
        meta["property_occurrence_cardinality"],
        meta["value_cardinality"],
    )
    selector = f"{args['entity_name']}.{field['name']}"
    annotation = field["annotation"]
    fmt = {"str": "string", "atom_id": "atom id"}.get(annotation, annotation)
    occurrence, values = (
        _native_count(occurrence),
        _native_count(values),
    )
    expression = (
        f"{selector}{{::{_count_text(occurrence)}}} :: "
        f"[{fmt}]{{::{_count_text(values)}}}"
    )
    effective = _named_property_count(occurrence, values)
    rows.append(
        _record(
            source,
            expression,
            "property_constraint",
            property_selector=selector,
            selection="property",
            name_format=None,
            occurrence_cardinality=occurrence,
            effective_occurrence_cardinality=effective,
            occurrence_conflict=effective is None,
            value_format=fmt,
            value_cardinality=values,
            group="model",
        )
    )


def _project_incoming(rel, args, source, rows):
    left, right, name = (
        rel["source"],
        args["entity_name"],
        rel["relation"],
    )
    left_count = _native_count(rel["source_cardinality"])
    right_count = _native_count(rel["target_cardinality"])
    expression = (
        f"{left} {{::{_count_text(left_count)}}}(({name}))"
        f"{{::{_count_text(right_count)}}} {right}"
    )
    rows.append(
        _native_relation(
            source,
            left,
            right,
            relation=name,
            left_count=left_count,
            right_count=right_count,
            expression=expression,
            group="model",
        )
    )


def _native_special_fields(
    declaration, source, args, rows, validate_field_contracts
):
    if declaration.get("classes"):
        validate_field_contracts(declaration)
        for field in declaration["classes"][0]["fields"]:
            _project_field(field, args, source, rows)
        for rel in args.get("incoming_model_relations", ()):
            _project_incoming(rel, args, source, rows)
