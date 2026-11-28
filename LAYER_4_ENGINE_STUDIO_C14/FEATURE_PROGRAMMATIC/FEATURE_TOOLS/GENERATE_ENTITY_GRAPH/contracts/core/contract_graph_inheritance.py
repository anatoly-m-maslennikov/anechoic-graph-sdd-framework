"""Source-bound ancestor and property references."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from collections import defaultdict
from dataclasses import replace

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.model.notation.\
    notation__shared import (
    Path as _subject_Path,
    PathStep as _subject_PathStep,
    SubjectNotationError as _subject_SubjectNotationError,
    parse_subject_expression as _subject_parse_subject_expression,
    render_subject as _subject_render_subject,
)  # fmt: skip
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.\
    contracts.contracts__shared \
    import _source_ref  # fmt: skip

Record = dict[str, Any]


def _ancestor_rows(
    narrowing: Mapping[str, Any], declarations: Mapping[str, list[Record]]
) -> dict[str, list[Record]]:
    "Return transitive declared ancestors with source refs; never copy claims."

    nodes = {row["id"]: row for row in narrowing["nodes"]}
    immediate: dict[str, list[str]] = defaultdict(list)
    for edge in narrowing["edges"]:
        immediate[nodes[edge["relation_source"]]["identity"]].append(
            nodes[edge["relation_target"]]["identity"]
        )

    def collect(target: str, seen: frozenset[str] = frozenset()) -> list[str]:
        result = []
        for parent in immediate.get(target, []):
            if parent not in seen:
                result.append(parent)
                result.extend(collect(parent, seen | {parent}))
        return list(dict.fromkeys(result))

    return {
        target: [
            {
                "target": parent,
                "declaration_refs": sorted(
                    _source_ref(row["source"])
                    for row in declarations.get(parent, [])
                ),
            }
            for parent in collect(target)
        ]
        for target in set(immediate)
        | {row["identity"] for row in nodes.values()}
    }


def _property_parts(
    target: str,
) -> tuple[str, tuple[_subject_PathStep, ...]] | None:
    try:
        expression = _subject_parse_subject_expression(
            target, subject_profile="approved"
        ).expression
    except _subject_SubjectNotationError:
        return None
    if not isinstance(expression, _subject_Path):
        return None
    for index, step in enumerate(expression.steps):
        if step.operator == ".":
            bearer = replace(
                expression,
                steps=expression.steps[:index],
                value_format=None,
                value_cardinality=None,
            )
            return _subject_render_subject(bearer), expression.steps[index:]
    return None


def _inherited_property_rows(
    target: str,
    ancestors: Mapping[str, list[Record]],
    declarations: Mapping[str, list[Record]],
) -> list[Record]:
    parts = _property_parts(target)
    if parts is None:
        return []
    bearer, suffix = parts
    rows = []
    for ancestor in ancestors.get(bearer, []):
        try:
            parent = _subject_parse_subject_expression(
                ancestor["target"], subject_profile="approved"
            ).expression
        except _subject_SubjectNotationError:
            continue
        if not isinstance(parent, _subject_Path):
            continue
        inherited = _subject_render_subject(
            replace(
                parent,
                steps=parent.steps + suffix,
                value_format=None,
                value_cardinality=None,
            )
        )
        sources = declarations.get(inherited, [])
        if sources:
            rows.append(
                {
                    "target": inherited,
                    "declaration_refs": sorted(
                        _source_ref(row["source"]) for row in sources
                    ),
                }
            )
    return rows


def _instance_kind(target: str) -> str | None:
    """Return the declared Kind path for one explicitly declared instance."""

    try:
        expression = _subject_parse_subject_expression(
            target, subject_profile="approved"
        ).expression
    except _subject_SubjectNotationError:
        return None
    if not isinstance(expression, _subject_Path):
        return None
    for index, step in enumerate(expression.steps):
        if step.operator == "//":
            kind = replace(
                expression,
                steps=expression.steps[:index],
                value_format=None,
                value_cardinality=None,
            )
            return _subject_render_subject(kind)
    return None


def _ancestor_property_rows(
    target: str,
    ancestors: Mapping[str, list[Record]],
    declarations: Mapping[str, list[Record]],
) -> list[Record]:
    "Link Properties declared on ancestors without materializing child copies."

    rows = []
    for ancestor in ancestors.get(target, []):
        for property_target, sources in declarations.items():
            parts = _property_parts(property_target)
            if parts is not None and parts[0] == ancestor["target"]:
                rows.append(
                    {
                        "target": property_target,
                        "declaration_refs": sorted(
                            _source_ref(row["source"]) for row in sources
                        ),
                    }
                )
    return rows
