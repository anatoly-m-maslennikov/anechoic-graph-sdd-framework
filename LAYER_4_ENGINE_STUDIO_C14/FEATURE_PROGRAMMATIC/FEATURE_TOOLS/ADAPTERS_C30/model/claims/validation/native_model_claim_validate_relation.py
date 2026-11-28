"""Validate native Claim data in source order."""

from __future__ import annotations

import ast
import re

from ....model.claims.native_model_claim_values import (
    _PROPERTY_CONSTRAINT_KEYS,
    _RELATION_CONSTRAINT_KEYS,
    _fail,
    _validate_cardinalities,
    _validate_endpoint,
)


def _validate_forbidden_status_pairs(declaration):
    node = next(
        (
            keyword.value
            for keyword in declaration.keywords
            if keyword.arg == "forbidden_status_pairs"
        ),
        None,
    )
    if node is None:
        return
    message = (
        "forbidden_status_pairs requires distinct source/target pairs "
        "of nonempty trimmed status strings"
    )
    try:
        pairs = ast.literal_eval(node)
    except ValueError:
        _fail(node, message)
    if (
        not isinstance(pairs, (tuple, list))
        or not pairs
        or any(
            not isinstance(pair, (tuple, list))
            or len(pair) != 2
            or any(
                not isinstance(status, str)
                or not status
                or status != status.strip()
                for status in pair
            )
            for pair in pairs
        )
        or len({tuple(pair) for pair in pairs}) != len(pairs)
    ):
        _fail(node, message)


def _validate_relation(
    arguments,
    declaration,
    function,
    classes,
    functions,
    imports,
    property_manifest,
):
    if function == "declare_relation":
        _validate_forbidden_status_pairs(declaration)
        for field in ("axes", "inverse_axes"):
            if field in arguments:
                values = arguments[field]
                if (
                    not isinstance(values, dict)
                    or not values
                    or any(
                        not isinstance(item, str)
                        or not item
                        or item != item.strip()
                        for pair in values.items()
                        for item in pair
                    )
                ):
                    _fail(
                        declaration,
                        f"{field} must map nonempty trimmed "
                        "axis names to values",
                    )
        if "inverse_axes" in arguments and not arguments.get("inverse_alias"):
            _fail(declaration, "inverse_axes requires inverse_alias")
        if "derived_from" in arguments:
            base = arguments["derived_from"]
            if (
                not isinstance(base, str)
                or not re.fullmatch(r"[A-Za-z_][A-Za-z_0-9]*", base)
                or base == arguments["relation_name"]
            ):
                _fail(
                    declaration,
                    "derived_from requires a different Relation name",
                )
        _validate_relation_endpoints(arguments, declaration)


def _validate_constraints(
    arguments,
    declaration,
    function,
    classes,
    functions,
    imports,
    property_manifest,
):
    for field, allowed in (
        ("model_relation_constraints", _RELATION_CONSTRAINT_KEYS),
        ("instance_relation_constraints", _RELATION_CONSTRAINT_KEYS),
        ("instance_property_constraints", _PROPERTY_CONSTRAINT_KEYS),
    ):
        if field not in arguments:
            continue
        constraints = arguments[field]
        if not isinstance(constraints, dict) or any(
            not isinstance(value, dict) for value in constraints.values()
        ):
            target = (
                "Property paths"
                if field == "instance_property_constraints"
                else "Relation names"
            )
            _fail(
                declaration,
                f"{field} must map {target} to constraint mappings",
            )
        for constraint in constraints.values():
            if unknown := constraint.keys() - allowed:
                _fail(
                    declaration,
                    f"unsupported {field} keys: {', '.join(sorted(unknown))}",
                )
    _validate_cardinalities(arguments, declaration)


def _validate_relation_endpoints(arguments, declaration):
    if "endpoint_pairs" in arguments:
        pairs = arguments["endpoint_pairs"]
        if (
            not isinstance(pairs, (tuple, list))
            or not pairs
            or "source_endpoint" in arguments
            or "target_endpoint" in arguments
        ):
            _fail(
                declaration,
                "endpoint_pairs requires a nonempty collection "
                "and excludes single endpoints",
            )
        for pair in pairs:
            if not isinstance(pair, dict) or set(pair) != {
                "source_endpoint",
                "target_endpoint",
            }:
                _fail(
                    declaration,
                    "endpoint pair requires source_endpoint "
                    "and target_endpoint",
                )
            for key in ("source_endpoint", "target_endpoint"):
                _validate_endpoint(pair[key], key, declaration)
    else:
        for key in ("source_endpoint", "target_endpoint"):
            _validate_endpoint(arguments.get(key), key, declaration)
