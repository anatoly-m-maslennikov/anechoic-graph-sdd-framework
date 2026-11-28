"""Project native declaration constraints."""

from collections.abc import Mapping

from ..primitives.primitives__shared import _named_property_count, _record
from ...claims.helpers.helpers__shared import _native_count


def _native_entity(declaration, source, block, result):
    args = declaration["arguments"]
    row = _entity_class(declaration, args, source, block, result)
    _entity_axes(args, source, block, result)
    if args.get("qualification_property_path") == "Projection.Form" and row[
        "bases"
    ] == ("Projection",):
        result.append(
            _record(
                source,
                block,
                "allowed_literal",
                group="model",
                property_selector="Projection.Form",
                literal=args["entity_name"],
            )
        )
    if "instance_population_cardinality" in args:
        result.append(
            _record(
                source,
                block,
                "native_population_constraint",
                group="instances",
                cardinality=_native_count(
                    args["instance_population_cardinality"]
                ),
                scope=args.get("instance_population_scope"),
            )
        )
    _native_entity_dependents(args, source, block, result)
    _native_entity_population(args, source, block, result)
    return result


def _native_entity_dependents(args, source, block, result):
    if "dependent_property_cardinality" in args:
        count = _native_count(args["dependent_property_cardinality"])
        names = args.get("allowed_dependent_property_names")
        if names is not None and (
            not isinstance(names, (tuple, list))
            or any(not isinstance(name, str) or not name for name in names)
        ):
            raise ValueError(
                "allowed dependent Property names must be strings"
            )
        name_format = args.get("dependent_property_name_format")
        if names is not None:
            name_format = f"{name_format or 'string'},in({','.join(names)})"
        result.append(
            _record(
                source,
                block,
                "property_constraint",
                group="model",
                property_selector=args["entity_name"],
                selection="immediate_dependents",
                name_format=name_format,
                occurrence_cardinality=count,
                effective_occurrence_cardinality=count,
                occurrence_conflict=False,
                value_format=None,
                value_cardinality=None,
                allowed_names=names,
            )
        )


def _native_entity_population(args, source, block, result):
    _entity_unique(args, source, block, result)
    for path, constraint in args.get(
        "instance_property_constraints", {}
    ).items():
        count = _native_count(constraint.get("value_cardinality"))
        if count is not None:
            result.append(
                _record(
                    source,
                    block,
                    "property_constraint",
                    group="instances",
                    property_selector=(
                        f"{args['entity_name']}//$instance.{path}"
                    ),
                    selection="values",
                    name_format=None,
                    occurrence_cardinality=None,
                    effective_occurrence_cardinality=_named_property_count(
                        None, count
                    ),
                    value_format=""
                    if count == {"minimum": 0, "maximum": 0}
                    else None,
                    value_cardinality=count,
                )
            )


def _entity_class(declaration, args, source, block, result):
    row = next(
        (
            row
            for row in declaration["classes"]
            if row["name"] == args["entity_class"]
        ),
        None,
    )
    if row is None:
        raise ValueError("declared entity class is unavailable")
    result.append(
        _record(
            source,
            block,
            "native_class",
            group="model",
            entity_name=args["entity_name"],
            class_name=row["name"],
            bases=row["bases"],
            qualification_property_path=args.get(
                "qualification_property_path"
            ),
            fields=row["fields"],
            arguments=args,
        )
    )
    return row


def _entity_axes(args, source, block, result):
    axes = args.get("axes", {})
    if not isinstance(axes, Mapping) or any(
        not axis.strip() or type(value) not in (str, int, float, bool)
        for axis, value in axes.items()
    ):
        raise ValueError("axes must map names to literal values")
    for axis, value in axes.items():
        result.append(
            _record(
                source,
                block,
                "axis_condition",
                group="model",
                subject_selector=args["entity_name"],
                axis=axis,
                operator="==",
                value=str(value),
            )
        )


def _entity_unique(args, source, block, result):
    for rule in args.get("population_unique_constraints", ()):
        result.append(
            _record(
                source,
                block,
                "population_unique_constraint",
                group="instances",
                population_selector=args.get(
                    "population_entity_path", args["entity_name"]
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
