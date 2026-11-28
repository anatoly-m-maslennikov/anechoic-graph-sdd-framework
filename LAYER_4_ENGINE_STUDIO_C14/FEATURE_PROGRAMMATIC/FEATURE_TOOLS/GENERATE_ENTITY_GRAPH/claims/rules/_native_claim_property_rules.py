"""Project native declaration constraints."""

from ..primitives.primitives__shared import _named_property_count, _record
from ...claims.helpers.helpers__shared import _native_count
from ._native_claim_property_ext import (
    _native_property_rules,
    _native_property_fallbacks,
)


def _native_property(declaration, source, block, result):
    args = declaration["arguments"]
    if not isinstance(args.get("base_path"), str) or not args["base_path"]:
        raise ValueError("Property declaration requires a base_path")
    if forms := args.get("applies_to_forms"):
        _property_forms(args, source, result, forms)
        return result
    _property_population(args, source, block, result)
    selector = f"{args['base_path']}.{args['entity_name']}"
    _native_property_scalar(declaration, args, source, block, result, selector)
    _native_property_dependents(args, source, block, result, selector)
    _native_property_rules(args, source, block, result, selector)
    _native_property_fallbacks(args, source, block, result, selector)
    return result


def _native_property_scalar(
    declaration, args, source, block, result, selector
):
    occurrence = _native_count(args.get("property_occurrence_cardinality"))
    values = _native_count(args.get("value_cardinality"))
    effective = _named_property_count(occurrence, values)
    if (
        not args.get("allowed_values")
        or occurrence is not None
        or values is not None
        or "value_format" in args
    ):
        result.append(
            _record(
                source,
                block,
                "property_constraint",
                group="model",
                property_selector=selector,
                selection="property",
                name_format=None,
                occurrence_cardinality=occurrence,
                effective_occurrence_cardinality=effective,
                occurrence_conflict=effective is None,
                value_format=args.get("value_format"),
                value_cardinality=values,
                **(
                    {"model_value_format": declaration["model_value_format"]}
                    if declaration.get("model_value_format")
                    else {}
                ),
                applicable_entity_classes=args.get(
                    "applies_to_entity_classes"
                ),
            )
        )


def _native_property_dependents(args, source, block, result, selector):
    dependent_value_count = _native_count(
        args.get("dependent_property_value_cardinality")
    )
    dependent_value_format = args.get("dependent_property_value_format")
    if "dependent_property_cardinality" in args or (
        "dependent_property_value_format" in args
        and dependent_value_count is None
    ):
        result.append(
            _record(
                source,
                block,
                "property_constraint",
                group="model",
                property_selector=selector,
                selection="immediate_dependents",
                name_format=args.get("dependent_property_name_format"),
                occurrence_cardinality=_native_count(
                    args.get("dependent_property_cardinality")
                ),
                effective_occurrence_cardinality=_native_count(
                    args.get("dependent_property_cardinality")
                ),
                occurrence_conflict=False,
                value_format=dependent_value_format
                if dependent_value_count is None
                else None,
                value_cardinality=None,
                allowed_names=args.get("allowed_dependent_property_names"),
            )
        )
    _dependent_values(
        source,
        block,
        result,
        selector,
        dependent_value_count,
        dependent_value_format,
    )
    _recursive_dependents(args, source, block, result, selector)


def _property_forms(args, source, result, forms):
    import json

    role = args["applies_to_role"]
    role = json.dumps(role) if " " in role else role
    for form in forms:
        selector = (
            f"Atom/(.Header.Context.Role in ({role}))/"
            f"(.Header.Context.Form in ({form})).Header.State.Status"
        )
        for value in args.get("allowed_values", ()):
            result.append(
                _record(
                    source,
                    f"{selector} :: {value}",
                    "allowed_literal",
                    group="model",
                    property_selector=selector,
                    literal=value,
                )
            )


def _property_population(args, source, block, result):
    for rule in args.get("population_unique_constraints", ()):
        result.append(
            _record(
                source,
                block,
                "population_unique_constraint",
                group="instances",
                population_selector=args.get(
                    "population_entity_path", args["base_path"]
                ),
                keys=rule["keys"],
                **(
                    {
                        "status": rule["status"],
                        "single_value_paths": rule["single_value_paths"],
                    }
                    if "status" in rule
                    else {}
                ),
            )
        )
    for dependency in args.get("population_functional_dependencies", ()):
        result.append(
            _record(
                source,
                block,
                "population_functional_dependency",
                group="instances",
                population_selector=args.get(
                    "population_entity_path", args["base_path"]
                ),
                keys=dependency["keys"],
                dependents=dependency["dependents"],
                **(
                    {"status_groups": dependency["status_groups"]}
                    if "status_groups" in dependency
                    else {}
                ),
            )
        )


def _recursive_dependents(args, source, block, result, selector):
    if "recursive_dependent_property_cardinality" in args:
        count = _native_count(args["recursive_dependent_property_cardinality"])
        result.append(
            _record(
                source,
                block,
                "property_constraint",
                group="model",
                property_selector=selector,
                selection="recursive_dependents",
                name_format=args.get(
                    "recursive_dependent_property_name_format"
                ),
                occurrence_cardinality=count,
                effective_occurrence_cardinality=count,
                occurrence_conflict=False,
                value_format=None,
                value_cardinality=None,
            )
        )
    if "recursive_dependent_property_value_format" in args:
        result.append(
            _record(
                source,
                block,
                "property_constraint",
                group="model",
                property_selector=selector,
                selection="recursive_dependent_values",
                name_format=None,
                occurrence_cardinality=None,
                value_format=args["recursive_dependent_property_value_format"],
                value_cardinality=None,
            )
        )


def _dependent_values(
    source,
    block,
    result,
    selector,
    dependent_value_count,
    dependent_value_format,
):
    if dependent_value_count is not None:
        result.append(
            _record(
                source,
                block,
                "property_constraint",
                group="model",
                property_selector=selector,
                selection="immediate_dependent_values",
                name_format=None,
                occurrence_cardinality=None,
                value_format=dependent_value_format,
                value_cardinality=dependent_value_count,
            )
        )
