"""Bind selected Subjects to existing declared contract targets."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
    Name as _subject_Name,
    Path as _subject_Path,
    Qualification as _subject_Qualification,
    RelationChain as _subject_RelationChain,
    SubjectNotationError as _subject_SubjectNotationError,
    parse_subject_expression as _subject_parse_subject_expression,
    render_subject as _subject_render_subject,
)

Record = dict[str, Any]


import re
from collections import defaultdict
from dataclasses import replace

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import matches_named_value
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.current_subject_common import _has_selection, namespace_local_expression
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.contract_graph_targets import _target

Candidate = tuple[Record, Mapping[str, Any], str | None, _subject_Path | _subject_RelationChain | None]
_SCOPE_UNIT_DECLARATION_FORM = "Scope Unit Declaration"
_DECLARED_INSTANCE_KINDS = frozenset({"Scope Unit", "Project"})
_KNOWN_NAMED_CONTRACT_CONTEXTS = {
    "Projection//PROJECT_SCOPE_UNIT_GRAPH": "Projection",
    "NamedSelection//ExtensionSources": "Named Selection",
    "PROJECTSTRUCTURE//ANECHOIC": "PROJECT STRUCTURE",
}
_NAMESPACED_SELECTOR = re.compile(r"^\s*(?:ANECHOIC\s*<\+\s*(?:MODEL|STRUCTURE)|ANECHOIC_(?:MODEL|STRUCTURE))\s*<\+\s*(.+?)\s*$")


def _local_raw_selector(subject: str) -> str:
    namespaced = _NAMESPACED_SELECTOR.match(subject)
    return namespaced.group(1) if namespaced else subject


def _conditional_target(
    expression: _subject_Path | _subject_RelationChain, catalog: Mapping[tuple[str, str], list[Record]],
) -> tuple[tuple[str, str], str, Record] | None:
    """Bind only known value or qualifier conditions to an existing target.

    The condition remains on the source entry.  It neither admits a qualified
    Node nor expands a selector over possible model targets.
    """

    expression = namespace_local_expression(expression) or expression
    if _has_selection(expression):
        return None
    if isinstance(expression, _subject_RelationChain):
        if len(expression.links) != 1 or expression.links[0].operator not in {">|", "|<"}:
            return None
        subject, axis = (
            (expression.endpoints[0], expression.endpoints[1])
            if expression.links[0].operator == ">|"
            else (expression.endpoints[1], expression.endpoints[0])
        )
        target = _target(subject)
        if target is not None and target in catalog:
            return target, "axis_context", {"axis": _subject_render_subject(axis)}
        return None
    if not isinstance(expression, _subject_Path):
        return None
    for index, step in enumerate(expression.steps):
        if step.operator not in {":", ":="}:
            continue
        base = replace(expression, steps=expression.steps[:index], value_format=None, value_cardinality=None)
        target = _target(base)
        if target is not None and target[0] == "property" and target in catalog:
            return target, "allowed_value_condition", {"condition": _subject_render_subject(expression)}

    return (_multiple_qualification(expression, catalog)
            or _inherited_qualification(expression, catalog)
            or _single_qualification(expression, catalog))


def _multiple_qualification(expression, catalog):
    qualifiers = [(index, step.operand) for index, step in enumerate(expression.steps)
                  if step.operator == "/" and isinstance(step.operand, _subject_Qualification)]
    if qualifiers and all(any(step.operator == ":" for step in qualifier.relative_path.steps) for _, qualifier in qualifiers):
        base = replace(expression, steps=tuple(step for step in expression.steps if not (
            step.operator == "/" and isinstance(step.operand, _subject_Qualification))), value_format=None, value_cardinality=None)
        target = _target(base)
        properties = []
        for index, qualifier in qualifiers:
            relative = qualifier.relative_path
            marker = next((i for i, step in enumerate(relative.steps) if step.operator == ":"), None)
            anchor_steps = tuple(step for step in expression.steps[:index] if not (
                step.operator == "/" and isinstance(step.operand, _subject_Qualification)))
            anchor = _target(replace(expression, steps=anchor_steps, value_format=None, value_cardinality=None))
            if marker is None or anchor is None or any(step.operator != ":" for step in relative.steps[marker:]):
                break
            path = replace(relative, steps=relative.steps[:marker], value_format=None, value_cardinality=None)
            properties.append(anchor[1] + "." + _subject_render_subject(path))
        if target in catalog and len(properties) == len(qualifiers) and all(("property", prop) in catalog for prop in properties):
            return target, "property_qualification", {"properties": properties, "condition": _subject_render_subject(expression)}
    if len(qualifiers) > 1 and [index for index, _ in qualifiers] == list(range(qualifiers[0][0], len(expression.steps))):
        base = replace(expression, steps=expression.steps[:qualifiers[0][0]], value_format=None, value_cardinality=None)
        target = _target(base)
        properties = []
        for _, qualifier in qualifiers:
            relative = qualifier.relative_path
            marker = next((i for i, step in enumerate(relative.steps) if step.operator == ":="), None)
            if marker is None or any(step.operator != ":=" for step in relative.steps[marker:]):
                break
            path = replace(relative, steps=relative.steps[:marker], value_format=None, value_cardinality=None)
            properties.append(target[1] + "." + _subject_render_subject(path) if target else "")
        if (target in catalog and target[0] in {"primary_node", "instance", "component"}
                and len(properties) == len(qualifiers)
                and all(("property", property) in catalog for property in properties)):
            return target, "property_qualification", {"properties": properties, "condition": _subject_render_subject(expression)}



def _inherited_qualification(expression, catalog):
    for index in range(len(expression.steps) - 1, 0, -1):
        step = expression.steps[index]
        if step.operator != "/" or not isinstance(step.operand, (_subject_Path, _subject_Qualification)):
            continue
        condition = (step.operand.relative_path
                     if isinstance(step.operand, _subject_Qualification) else step.operand)
        marker = next((position for position, item in enumerate(condition.steps) if item.operator == ":="), None)
        if marker is None or any(item.operator != ":=" for item in condition.steps[marker:]):
            continue
        base = replace(expression, steps=expression.steps[:index], value_format=None, value_cardinality=None)
        target = _target(base)
        if target is None or target not in catalog:
            continue
        root = replace(base, steps=(), value_format=None, value_cardinality=None)
        root_target = _target(root)
        property_path = replace(condition, steps=condition.steps[:marker], value_format=None, value_cardinality=None)
        if root_target is None:
            continue
        property_key = ("property", root_target[1] + "." + _subject_render_subject(property_path))
        if property_key in catalog:
            return target, "inherited_property_qualification", {
                "property": property_key[1], "condition": _subject_render_subject(condition),
            }


def _single_qualification(expression, catalog):
    qualifiers = [
        (index, step.operand) for index, step in enumerate(expression.steps)
        if step.operator == "/" and isinstance(step.operand, _subject_Qualification)
    ]
    if len(qualifiers) != 1:
        return None
    index, qualifier = qualifiers[0]
    base = replace(expression, steps=expression.steps[:index], value_format=None, value_cardinality=None)
    target = _target(base)
    if target is None or target not in catalog or target[0] not in {"primary_node", "instance", "component"}:
        return None
    relative = qualifier.relative_path
    conditional = next((position for position, step in enumerate(relative.steps) if step.operator == ":="), None)
    if conditional is None or any(step.operator not in {":="} for step in relative.steps[conditional:]):
        return None
    property_path = replace(relative, steps=relative.steps[:conditional], value_format=None, value_cardinality=None)
    property_target = target[1] + "." + _subject_render_subject(property_path)
    property_key = ("property", property_target)
    return ((target, "property_qualification", {
        "property": property_key[1], "condition": _subject_render_subject(relative),
    }) if property_key in catalog else None)


def _root_name(expression: _subject_Path | _subject_RelationChain) -> str | None:
    expression = namespace_local_expression(expression) or expression
    path = expression if isinstance(expression, _subject_Path) else expression.endpoints[0]
    return path.head.value if isinstance(path.head, _subject_Name) else None


def _catalog_roots(catalog: Mapping[tuple[str, str], list[Record]]) -> set[str]:
    roots = {"Relation" for (kind, _) in catalog if kind == "relation"}
    for kind, identity in catalog:
        if kind == "relation":
            continue
        try:
            expression = _subject_parse_subject_expression(identity, subject_profile="approved").expression
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
    if not isinstance(expression, _subject_Path) or not isinstance(expression.head, _subject_Name):
        return None
    if (expression.head.value not in _DECLARED_INSTANCE_KINDS or len(expression.steps) != 1
            or expression.value_format is not None or expression.value_cardinality is not None):
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
        if (not matches_named_value(view.get("content_role"), "Requirement")
                or not matches_named_value(view.get("type"), _SCOPE_UNIT_DECLARATION_FORM)):
            continue
        kind = _declared_instance_kind(expression)
        if kind is not None:
            contexts[_subject_render_subject(expression)].append({
                "kind": kind, "source": dict(carrier["source"]),
            })
    return {selector: records[0] for selector, records in contexts.items() if len(records) == 1}


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
    return target, "scope_unit_declaration_context", {
        "instance_selector": _subject_render_subject(expression),
        "instance_kind": context["kind"],
        "existence_provenance": "current_scope_unit_declaration",
        "declaration_source": context["source"],
    }


def _raw_selector_binding(
    subject: str, catalog: Mapping[tuple[str, str], list[Record]],
) -> tuple[tuple[str, str], str, Record] | None:
    """Handle the few admitted non-Path selectors without expanding them."""

    compact = re.sub(r"\s+", "", _local_raw_selector(subject))
    kind = _KNOWN_NAMED_CONTRACT_CONTEXTS.get(compact)
    if kind is not None:
        target = ("primary_node", kind)
        if target not in catalog:
            target = ("component", kind)
        if target in catalog:
            return target, "known_instance_context", {
                "instance_selector": subject,
                "existence_provenance": "bounded_named_contract_context",
            }
    return None


def _lexical_term_binding(
    expression: _subject_Path | _subject_RelationChain,
    catalog: Mapping[tuple[str, str], list[Record]],
) -> tuple[tuple[str, str], str, Record] | None:
    """Keep a Term//Name as lexical evidence under Term, never as a Node."""

    expression = namespace_local_expression(expression) or expression
    if _has_selection(expression):
        return None
    if not isinstance(expression, _subject_Path) or not isinstance(expression.head, _subject_Name):
        return None
    if expression.head.value != "Term" or not any(step.operator == "//" for step in expression.steps):
        return None
    target = ("component", "Term")
    if target not in catalog:
        return None
    return target, "lexical_term_context", {"lexical_selector": _subject_render_subject(expression)}


