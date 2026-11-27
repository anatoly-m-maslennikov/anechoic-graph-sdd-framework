"""Resolve Subject targets and source-backed definitions."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import replace

from ..ADAPTERS_C30.ADAPTERS_C30__shared import (
    Name as _subject_Name,
    Path as _subject_Path,
    Qualification as _subject_Qualification,
    RelationChain as _subject_RelationChain,
    SubjectNotationError as _subject_SubjectNotationError,
    matches_named_value,
    parse_subject_expression as _subject_parse_subject_expression,
    render_subject as _subject_render_subject,
)
from .contract_graph_targets import _target as _contract_target
from .current_subject_common import (
    _has_selection,
    _model_target,
    _target_kind,
    namespace_local_expression,
)
from .declaration_evidence import Record, _view
from .subject_audit_occurrences import _authored_subjects, _canonical, _source


def _local_target(subject: str) -> tuple[str, str] | None:
    """Return an existing declaration-shaped target; never expand selectors."""

    expression = _subject_parse_subject_expression(
        subject, subject_profile="approved"
    ).expression
    expression = namespace_local_expression(expression) or expression
    if _has_selection(expression):
        return None
    if (
        isinstance(expression, _subject_Path)
        and isinstance(expression.head, _subject_Name)
        and expression.head.value in {"ANECHOIC_MODEL", "ANECHOIC_STRUCTURE"}
        and not expression.steps
    ):
        return None
    target = _contract_target(expression)
    if target is not None:
        return target
    if not isinstance(expression, _subject_Path):
        return None
    if isinstance(
        expression.head, _subject_Name
    ) and expression.head.value in {"CFEL", "Carrier", "Term"}:
        return "component", _model_target(expression)
    kind = _target_kind(expression)
    if kind in {"primary_node", "property", "instance", "relation"}:
        return kind, _model_target(expression)
    return None


def _entity_target(subject: str) -> tuple[str, str] | None:
    """Keep a direct entity target or the last path in a context chain."""

    expression = _subject_parse_subject_expression(
        subject, subject_profile="approved"
    ).expression
    if isinstance(expression, _subject_RelationChain):
        if not expression.links or any(
            link.operator != "<+" or link.relation_type is not None
            for link in expression.links
        ):
            return None
        expression = expression.endpoints[-1]
    if not isinstance(expression, _subject_Path):
        return None
    if any(
        step.operator in {":", ":="}
        or isinstance(step.operand, _subject_Qualification)
        for step in expression.steps
    ):
        return None
    rendered = _subject_render_subject(expression)
    return _local_target(rendered)


def _property_parts(target: str) -> tuple[str, str] | None:
    expression = _subject_parse_subject_expression(
        target, subject_profile="approved"
    ).expression
    if not isinstance(expression, _subject_Path):
        return None
    for index, step in enumerate(expression.steps):
        if step.operator == ".":
            origin = replace(
                expression,
                steps=expression.steps[:index],
                value_format=None,
                value_cardinality=None,
            )
            suffix = replace(
                expression,
                head=step.operand,
                steps=expression.steps[index + 1 :],
                value_format=None,
                value_cardinality=None,
            )
            return _subject_render_subject(origin), _subject_render_subject(
                suffix
            )
    return None


def _entity_definitions(carriers: list[Record]) -> dict[str, list[Record]]:
    rows: dict[str, list[Record]] = defaultdict(list)
    for carrier in carriers:
        view = _view(carrier)
        if not matches_named_value(
            view.get("content_role"), "Requirement"
        ) or not matches_named_value(view.get("type"), "Entity Definition"):
            continue
        subjects = _authored_subjects(carrier)
        if subjects is None:
            continue
        values = subjects.get("active", subjects.get("governs"))
        values = values if isinstance(values, list) else [values]
        if len(values) != 1 or not isinstance(values[0], str):
            continue
        canonical, error = _canonical(values[0])
        if canonical is not None and error is None:
            rows[canonical].append(_source(carrier))
    return rows


def _term_identity(subject: str) -> str | None:
    expression = _subject_parse_subject_expression(
        subject, subject_profile="approved"
    ).expression
    expression = namespace_local_expression(expression) or expression
    if (
        not isinstance(expression, _subject_Path)
        or not isinstance(expression.head, _subject_Name)
        or expression.head.value != "Term"
        or len(expression.steps) != 1
        or expression.steps[0].operator != "//"
        or not isinstance(expression.steps[0].operand, _subject_Name)
        or expression.value_format is not None
        or expression.value_cardinality is not None
    ):
        return None
    return _subject_render_subject(expression)


def _term_definitions(carriers: list[Record]) -> dict[str, list[Record]]:
    rows: dict[str, list[Record]] = defaultdict(list)
    for carrier in carriers:
        view = _view(carrier)
        if (
            not matches_named_value(view.get("content_role"), "Method")
            or not matches_named_value(view.get("type"), "Term Definition")
            or not str(_source(carrier).get("atom_id", "")).startswith("CA-M-")
        ):
            continue
        subjects = _authored_subjects(carrier)
        if subjects is None:
            continue
        values = subjects.get("active", subjects.get("governs"))
        values = values if isinstance(values, list) else [values]
        if len(values) != 1 or not isinstance(values[0], str):
            continue
        try:
            identity = _term_identity(values[0])
        except _subject_SubjectNotationError:
            continue
        if identity is not None:
            rows[identity].append(_source(carrier))
    return rows
