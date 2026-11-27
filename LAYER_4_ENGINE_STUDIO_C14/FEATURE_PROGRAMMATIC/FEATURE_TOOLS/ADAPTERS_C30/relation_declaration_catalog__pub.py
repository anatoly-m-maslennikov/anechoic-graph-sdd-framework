"""Assemble a catalog of declared Relations and inverse aliases."""

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30 import (
    subject_notation__pub as notation,
)

_CITATION_NAMES = frozenset(
    {"REFERENCES", "IS_REFERENCE", "HAS_REFERENCE", "IS_REFERENCE_FOR"}
)


def retired_archive_relations(status_group, declared_names):
    "Keep archived citation data readable after the Model retires citations."
    if status_group == "Archived" and _CITATION_NAMES.isdisjoint(
        declared_names
    ):
        return _CITATION_NAMES
    return ()


def _matches_subject(endpoint, name):
    return (
        isinstance(endpoint, notation.Path)
        and isinstance(endpoint.head, notation.Name)
        and (
            (endpoint.head.value == "Relation" and len(endpoint.steps) == 1)
            or (
                endpoint.head.value == "Graph"
                and len(endpoint.steps) == 2
                and endpoint.steps[0].operator == "/"
                and isinstance(endpoint.steps[0].operand, notation.Name)
                and endpoint.steps[0].operand.value == "Relation"
            )
        )
        and endpoint.steps[-1].operator == "//"
        and isinstance(endpoint.steps[-1].operand, notation.Name)
        and endpoint.steps[-1].operand.value == name
    )


def _validate_derivations(records, relations):
    for source, _, declaration in records:
        if (
            declaration["kind"] != "relation"
            or "derived_from" not in declaration["arguments"]
        ):
            continue
        args = declaration["arguments"]
        derived = args["derived_from"]
        if not isinstance(derived, str) or derived not in relations:
            raise ValueError(
                f"{source}: unknown derived_from Relation: {derived}"
            )
        if relations[derived][0] is args:
            raise ValueError(
                f"{source}: Relation cannot derive from itself: {derived}"
            )


def build_relation_declaration_catalog(records: list) -> dict:
    "Assemble canonical Relations and inverse aliases before Entity checks."
    relations = {}
    for source, subject, declaration in records:
        if declaration["kind"] != "relation":
            continue
        args = declaration["arguments"]
        local = notation.namespace_local_expression(
            notation.parse_subject_expression(subject).expression
        )
        endpoint = (
            local.endpoints[-1]
            if isinstance(local, notation.RelationChain)
            else local
        )
        if not _matches_subject(endpoint, args["relation_name"]):
            raise ValueError(
                f"{source}: declared Relation does not match its Main Subject"
            )
        for name, reverse in (
            (args["relation_name"], False),
            (args.get("inverse_alias"), True),
        ):
            if name is None:
                continue
            if name in relations:
                raise ValueError(f"{source}: duplicate Relation name: {name}")
            relations[name] = (args, reverse)
    _validate_derivations(records, relations)
    return relations
