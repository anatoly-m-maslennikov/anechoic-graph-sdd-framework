"""Project native declaration constraints."""

from ..primitives.primitives__shared import _record
from ...claims.helpers.helpers__shared import _native_count


def _native_relation(declaration, source, block, result):
    args = declaration["arguments"]
    name = args["relation_name"]
    result.append(
        _record(
            source,
            block,
            "native_relation_declaration",
            group="model",
            relation=name,
            arguments={
                **args,
                **(
                    {"derivation": "Derived"} if "derived_from" in args else {}
                ),
            },
        )
    )
    _relation_axes(args, source, block, result, name)
    _relation_endpoints(args, source, block, result, name)
    _relation_aliases(args, source, block, result, name)


def _relation_axes(args, source, block, result, name):
    for key, relation in (
        ("axes", name),
        ("inverse_axes", args.get("inverse_alias")),
    ):
        for axis, value in args.get(key, {}).items():
            subject = f"Relation//{relation}"
            result.append(
                _record(
                    source,
                    f"{subject} >| {axis} == {value}",
                    "axis_condition",
                    group="model",
                    subject_selector=subject,
                    axis=axis,
                    operator="==",
                    value=value,
                )
            )
    if base := args.get("derived_from"):
        result.append(
            _record(
                source,
                block,
                "relation_cardinality",
                group="model",
                source_selector=f"Relation//{name}",
                relation="IS_DERIVED_RELATION_OF",
                target_selector=f"Relation//{base}",
                source_cardinality=None,
                target_cardinality=None,
                written_direction="forward",
            )
        )


def _relation_endpoints(args, source, block, result, name):
    for selector, direction in (
        (args.get("source_endpoint"), "source"),
        (args.get("target_endpoint"), "target"),
    ):
        if isinstance(selector, dict):
            result.append(
                _record(
                    source,
                    block,
                    "relation_endpoint",
                    group="model",
                    relation=name,
                    direction=direction,
                    endpoint=selector,
                    targets_per_source=_native_count(
                        args.get("targets_per_source")
                    ),
                    sources_per_target=_native_count(
                        args.get("sources_per_target")
                    ),
                )
            )
    for pair in args.get("endpoint_pairs", ()):
        result.append(
            _record(
                source,
                block,
                "relation_endpoint_pair",
                group="model",
                relation=name,
                source_endpoint=pair["source_endpoint"],
                target_endpoint=pair["target_endpoint"],
                targets_per_source=_native_count(
                    args.get("targets_per_source")
                ),
                sources_per_target=_native_count(
                    args.get("sources_per_target")
                ),
            )
        )


def _relation_aliases(args, source, block, result, name):
    if inverse := args.get("inverse_alias"):
        from ....ADAPTERS_C30.model.legacy_relation__pub import (
            emits_instance_inverse,
        )

        is_inverse = emits_instance_inverse(args)
        result.append(
            _record(
                source,
                block,
                "relation_cardinality",
                group="model",
                source_selector=f"Relation//{name if is_inverse else inverse}",
                relation="HAS_INVERSE"
                if is_inverse
                else "IS_INVERSE_ALIAS_FOR",
                target_selector=f"Relation//{inverse if is_inverse else name}",
                source_cardinality=None,
                target_cardinality=None,
                written_direction="forward",
            )
        )
    if alias := args.get("written_alias"):
        result.append(
            _record(
                source,
                block,
                "relation_alias",
                group="model",
                relation=name,
                glyph=alias,
            )
        )
