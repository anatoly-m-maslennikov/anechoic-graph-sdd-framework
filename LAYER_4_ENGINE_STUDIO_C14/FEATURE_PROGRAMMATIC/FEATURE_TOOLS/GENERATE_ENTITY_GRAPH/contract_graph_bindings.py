"""Bind selected Subjects to existing declared contract targets."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from ..ADAPTERS_C30.ADAPTERS_C30__shared import (
    Name as _subject_Name,
    Path as _subject_Path,
    RelationChain as _subject_RelationChain,
    SubjectNotationError as _subject_SubjectNotationError,
    parse_subject_expression as _subject_parse_subject_expression,
    render_subject as _subject_render_subject,
)

import re
from collections import defaultdict
from dataclasses import replace as replace

from ..ADAPTERS_C30.ADAPTERS_C30__shared import (
    matches_named_value,
)
from .current_subject_common import (
    _has_selection as _has_selection,
    namespace_local_expression,
)
from .contract_graph_targets import (
    _target as _target,
)

from ._contract_graph_qualification import (
    _subject_Qualification as _subject_Qualification,
    _conditional_target as _conditional_target,
    _multiple_qualification as _multiple_qualification,
    _inherited_qualification as _inherited_qualification,
    _single_qualification as _single_qualification,
)


Record = dict[str, Any]

Candidate = tuple[
    Record,
    Mapping[str, Any],
    str | None,
    _subject_Path | _subject_RelationChain | None,
]
_SCOPE_UNIT_DECLARATION_FORM = "Scope Unit Declaration"
_DECLARED_INSTANCE_KINDS = frozenset({"Scope Unit", "Project"})
_KNOWN_NAMED_CONTRACT_CONTEXTS = {
    "Projection//PROJECT_SCOPE_UNIT_GRAPH": "Projection",
    "NamedSelection//ExtensionSources": "Named Selection",
    "PROJECTSTRUCTURE//ANECHOIC": "PROJECT STRUCTURE",
}
_NAMESPACED_SELECTOR = re.compile(
    r"^\s*(?:ANECHOIC\s*<\+\s*(?:MODEL|STRUCTURE)|"
    r"ANECHOIC_(?:MODEL|STRUCTURE))\s*<\+\s*(.+?)\s*$"
)


def _local_raw_selector(subject: str) -> str:
    namespaced = _NAMESPACED_SELECTOR.match(subject)
    return namespaced.group(1) if namespaced else subject


def _root_name(
    expression: _subject_Path | _subject_RelationChain,
) -> str | None:
    expression = namespace_local_expression(expression) or expression
    path = (
        expression
        if isinstance(expression, _subject_Path)
        else expression.endpoints[0]
    )
    return path.head.value if isinstance(path.head, _subject_Name) else None


def _catalog_roots(
    catalog: Mapping[tuple[str, str], list[Record]],
) -> set[str]:
    roots = {"Relation" for (kind, _) in catalog if kind == "relation"}
    for kind, identity in catalog:
        if kind == "relation":
            continue
        try:
            expression = _subject_parse_subject_expression(
                identity, subject_profile="approved"
            ).expression
        except _subject_SubjectNotationError:
            continue
        root = _root_name(expression)
        if root is not None:
            roots.add(root)
    return roots


def _declared_instance_kind(
    expression: _subject_Path | _subject_RelationChain | None,
) -> str | None:
    """Return the generic Kind of one exact Scope Unit Declaration Subject."""

    if expression is not None:
        expression = namespace_local_expression(expression) or expression
    if not isinstance(expression, _subject_Path) or not isinstance(
        expression.head, _subject_Name
    ):
        return None
    if (
        expression.head.value not in _DECLARED_INSTANCE_KINDS
        or len(expression.steps) != 1
        or expression.value_format is not None
        or expression.value_cardinality is not None
    ):
        return None
    step = expression.steps[0]
    if step.operator != "//" or not isinstance(step.operand, _subject_Name):
        return None
    return expression.head.value


def _scope_unit_declaration_contexts(
    candidates: list[Candidate],
) -> dict[str, Record]:
    """Index unambiguous Current Scope Unit Declaration instance evidence."""

    contexts: dict[str, list[Record]] = defaultdict(list)
    for carrier, view, _, expression in candidates:
        if not matches_named_value(
            view.get("content_role"), "Requirement"
        ) or not matches_named_value(
            view.get("type"), _SCOPE_UNIT_DECLARATION_FORM
        ):
            continue
        kind = _declared_instance_kind(expression)
        if kind is not None:
            contexts[_subject_render_subject(expression)].append(
                {
                    "kind": kind,
                    "source": dict(carrier["source"]),
                }
            )
    return {
        selector: records[0]
        for selector, records in contexts.items()
        if len(records) == 1
    }


def _declared_instance_binding(
    expression: _subject_Path | _subject_RelationChain,
    catalog: Mapping[tuple[str, str], list[Record]],
    contexts: Mapping[str, Record],
) -> tuple[tuple[str, str], str, Record] | None:
    context = contexts.get(_subject_render_subject(expression))
    if context is None:
        return None
    target = ("primary_node", context["kind"])
    if target not in catalog:
        target = ("component", context["kind"])
    if target not in catalog:
        return None
    return (
        target,
        "scope_unit_declaration_context",
        {
            "instance_selector": _subject_render_subject(expression),
            "instance_kind": context["kind"],
            "existence_provenance": "current_scope_unit_declaration",
            "declaration_source": context["source"],
        },
    )


def _raw_selector_binding(
    subject: str,
    catalog: Mapping[tuple[str, str], list[Record]],
) -> tuple[tuple[str, str], str, Record] | None:
    """Handle the few admitted non-Path selectors without expanding them."""

    compact = re.sub(r"\s+", "", _local_raw_selector(subject))
    kind = _KNOWN_NAMED_CONTRACT_CONTEXTS.get(compact)
    if kind is not None:
        target = ("primary_node", kind)
        if target not in catalog:
            target = ("component", kind)
        if target in catalog:
            return (
                target,
                "known_instance_context",
                {
                    "instance_selector": subject,
                    "existence_provenance": "bounded_named_contract_context",
                },
            )
    return None


def _lexical_term_binding(
    expression: _subject_Path | _subject_RelationChain,
    catalog: Mapping[tuple[str, str], list[Record]],
) -> tuple[tuple[str, str], str, Record] | None:
    """Keep a Term//Name as lexical evidence under Term, never as a Node."""

    expression = namespace_local_expression(expression) or expression
    if _has_selection(expression):
        return None
    if not isinstance(expression, _subject_Path) or not isinstance(
        expression.head, _subject_Name
    ):
        return None
    if expression.head.value != "Term" or not any(
        step.operator == "//" for step in expression.steps
    ):
        return None
    target = ("component", "Term")
    if target not in catalog:
        return None
    return (
        target,
        "lexical_term_context",
        {"lexical_selector": _subject_render_subject(expression)},
    )
