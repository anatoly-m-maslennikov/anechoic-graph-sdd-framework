"""Group source-bound namespace and inherited rule context."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping
from typing import Any

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.model.notation.notation__shared import (
    Name as _subject_Name,
    Path as _subject_Path,
    RelationChain as _subject_RelationChain,
    SubjectNotationError as _subject_SubjectNotationError,
    namespace_local_expression as _subject_namespace_local_expression,
    parse_subject_expression as _subject_parse_subject_expression,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.content.content__shared import (
    carrier_read_view,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.carriers__shared import (
    matches_named_value,
)
from ...contracts.contracts__shared import _source_ref
from ...declarations.declarations__shared import Record, _view


def _detail_declarations(carriers: list[Record]) -> list[Record]:
    """Admit exact Current declaration role/form for Property detail."""

    return [
        carrier
        for carrier in carriers
        if matches_named_value(
            _view(carrier).get("content_role"), "Requirement"
        )
        and any(
            matches_named_value(_view(carrier).get("type"), form)
            for form in ("Declaration", "Relation Declaration")
        )
    ]


def _ancestors(tree: Mapping[str, Any]) -> dict[str, list[str]]:
    nodes = {row["id"]: row["identity"] for row in tree["nodes"]}
    parents: dict[str, list[str]] = defaultdict(list)
    for edge in tree["edges"]:
        parents[nodes[edge["relation_source"]]].append(
            nodes[edge["relation_target"]]
        )

    def collect(
        identity: str, seen: frozenset[str] = frozenset()
    ) -> list[str]:
        result: list[str] = []
        for parent in parents.get(identity, []):
            if parent not in seen:
                result.append(parent)
                result.extend(collect(parent, seen | {parent}))
        return list(dict.fromkeys(result))

    return {identity: collect(identity) for identity in nodes.values()}


def _rule_groups(
    identity: str, rules: list[Record], ancestors: Mapping[str, list[str]], key
) -> Record:
    """Group rules without selecting among unrelated inherited declarations."""
    grouped: Record = {
        "declared_here": [],
        "inherited": [],
        "overridden_here": [],
    }
    for rule in rules:
        origin = rule["origin_entity"]
        matching = [
            other
            for other in rules
            if key(other) == key(rule) and other["origin_entity"] != origin
        ]
        replaced = [
            other
            for other in matching
            if other["origin_entity"] in ancestors.get(origin, [])
        ]
        if any(
            origin in ancestors.get(other["origin_entity"], [])
            for other in matching
        ):
            continue
        item = _rule_with_replacements(rule, replaced)
        if origin == identity:
            group = "overridden_here" if replaced else "declared_here"
        else:
            group = "inherited"
        grouped[group].append(item)
    return grouped


def _namespace_contexts(carriers: list[Record]) -> list[Record]:
    """Keep one explicit ANECHOIC root context per namespace branch."""
    candidates: dict[str, list[tuple[int, Record]]] = defaultdict(list)
    for carrier in carriers:
        source = carrier.get("source")
        subjects = carrier.get("subjects")
        if not isinstance(source, Mapping) or not isinstance(
            subjects, Mapping
        ):
            continue
        try:
            normalized = carrier_read_view({"subjects": dict(subjects)})[
                "subjects"
            ]
        except ValueError:
            continue
        for role in ("governs", "depends_on"):
            values = normalized.get(role, [])
            for subject in values if isinstance(values, list) else [values]:
                if not isinstance(subject, str):
                    continue
                try:
                    expression = _subject_parse_subject_expression(
                        subject, subject_profile="approved"
                    ).expression
                except _subject_SubjectNotationError:
                    continue
                candidate = _namespace_candidate(expression, role)
                if candidate is not None:
                    root, priority = candidate
                    candidates[root].append((priority, dict(source)))
    return [
        {"subject": root, "source": source}
        for root, rows in sorted(candidates.items())
        for _, source in [
            min(
                rows,
                key=lambda row: (
                    row[0],
                    _source_ref(row[1]),
                    str(row[1].get("path", "")),
                ),
            )
        ]
    ]


def _namespace_candidate(expression, role):
    if (
        isinstance(expression, _subject_Path)
        and isinstance(expression.head, _subject_Name)
        and expression.head.value in {"ANECHOIC_MODEL", "ANECHOIC_STRUCTURE"}
        and not expression.steps
    ):
        return expression.head.value, 0 if role == "governs" else 1
    local = _subject_namespace_local_expression(expression)
    if local is None or not isinstance(expression, _subject_RelationChain):
        return None
    first = expression.endpoints[0]
    if isinstance(first.head, _subject_Name) and first.head.value in {
        "ANECHOIC_MODEL",
        "ANECHOIC_STRUCTURE",
    }:
        return first.head.value, 2
    namespace = expression.endpoints[1]
    if not isinstance(namespace.head, _subject_Name):
        return None
    root = f"ANECHOIC <+ {namespace.head.value}"
    direct = len(expression.endpoints) == 2
    priority = 0 if direct and role == "governs" else 1 if direct else 2
    return root, priority


def _rule_with_replacements(rule, replaced):
    item = {
        **rule,
        "replaces": [
            {
                "identity": old.get("identity"),
                "origin_entity": old["origin_entity"],
                "declaration_refs": old["declaration_refs"],
                "source_refs": old["source_refs"],
                "contract": old.get("contract"),
                "contracts": old.get("contracts"),
            }
            for old in replaced
        ],
    }
    return item
