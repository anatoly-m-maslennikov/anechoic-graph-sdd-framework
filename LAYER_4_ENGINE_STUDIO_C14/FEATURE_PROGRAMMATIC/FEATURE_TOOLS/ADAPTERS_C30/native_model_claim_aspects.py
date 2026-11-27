"""Validate native Aspect declaration addresses."""

from typing import Any


def _validate_aspect_tree(tree, args, notation):
    if not isinstance(tree, notation.RelationChain) or len(tree.endpoints) < 3:
        raise ValueError
    root, *rest = tree.endpoints
    if (
        not isinstance(root.head, notation.Name)
        or root.head.value != "PROJECT STRUCTURE"
        or root.value_format is not None
        or root.value_cardinality is not None
        or len(root.steps) != 1
        or root.steps[0].operator != "//"
        or not isinstance(root.steps[0].operand, notation.Name)
    ):
        raise ValueError
    if any(
        not isinstance(part.head, notation.Name)
        or part.steps
        or part.value_format is not None
        or part.value_cardinality is not None
        for part in rest
    ):
        raise ValueError
    if (
        rest[0].head.value != "Aspects"
        or rest[-1].head.value != args["entity_name"]
    ):
        raise ValueError
    if any(
        link.operator != "<+"
        or link.relation_type is not None
        or link.forward_cardinality is not None
        or link.reverse_cardinality is not None
        for link in tree.links
    ):
        raise ValueError


def validate_aspect_instance(args: dict[str, Any]) -> str:
    """Return the canonical full address of a bounded Aspect declaration."""
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30 import (
        subject_notation__pub as notation,
    )

    message = (
        "Aspect instance requires only entity_name and a matching "
        "full Project Structure address"
    )
    if not isinstance(args, dict) or set(args) != {"entity_name", "instance"}:
        raise ValueError(message)
    instance = args["instance"]
    if (
        not isinstance(instance, dict)
        or set(instance) != {"type", "fields"}
        or instance["type"] != "Aspect"
    ):
        raise ValueError(message)
    fields = instance["fields"]
    if (
        not isinstance(fields, dict)
        or set(fields) != {"address"}
        or not isinstance(fields["address"], str)
    ):
        raise ValueError(message)
    try:
        tree = notation.parse_subject_expression(
            fields["address"], subject_profile="approved"
        ).expression
        _validate_aspect_tree(tree, args, notation)
        return notation.render_subject(tree)
    except notation.SubjectNotationError, ValueError:
        raise ValueError(message) from None


def _normalize_aspect_paths(paths, notation):
    normalized = []
    for address in paths:
        try:
            tree = notation.parse_subject_expression(
                address, subject_profile="approved"
            ).expression
            if (
                not isinstance(tree, notation.RelationChain)
                or not tree.endpoints
                or not isinstance(tree.endpoints[-1].head, notation.Name)
            ):
                raise ValueError("invalid Aspect hierarchy address")
            leaf = tree.endpoints[-1].head.value
            normalized.append(
                validate_aspect_instance(
                    {
                        "entity_name": leaf,
                        "instance": {
                            "type": "Aspect",
                            "fields": {"address": address},
                        },
                    }
                )
            )
        except (
            notation.SubjectNotationError,
            ValueError,
            TypeError,
            AttributeError,
            IndexError,
        ):
            raise ValueError("invalid Aspect hierarchy address") from None
    return normalized


def validate_aspect_hierarchy(
    args: dict,
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30 import (
        subject_notation__pub as notation,
    )

    if (
        not isinstance(args, dict)
        or set(args)
        != {"entity_name", "structure_paths", "aspect_memberships"}
        or args.get("entity_name") != "Project Structure"
    ):
        raise ValueError("invalid Aspect hierarchy")
    result = []
    for key in ("structure_paths", "aspect_memberships"):
        paths = args[key]
        if (
            not isinstance(paths, tuple)
            or any(not isinstance(x, str) for x in paths)
            or len(set(paths)) != len(paths)
        ):
            raise ValueError(
                "Aspect hierarchy paths must be distinct tuples of text"
            )
        normalized = _normalize_aspect_paths(paths, notation)
        result.append(tuple(normalized))
    return tuple(result)
