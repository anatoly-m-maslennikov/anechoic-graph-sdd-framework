"""Read authored Subject occurrences and select MODEL Subjects."""

from __future__ import annotations

from collections.abc import Mapping
import re
from typing import Any

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.model.notation.\
    notation__shared import (
    Name as _subject_Name,
    Path as _subject_Path,
    Qualification as _subject_Qualification,
    RelationChain as _subject_RelationChain,
    SelectionGroup as _subject_SelectionGroup,
    SubjectNotationError as _subject_SubjectNotationError,
    namespace_local_expression as _subject_namespace_local_expression,
    parse_subject_expression as _subject_parse_subject_expression,
    render_subject as _subject_render_subject,
)  # fmt: skip
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.\
    contracts.contracts__shared \
    import _target as _contract_target  # fmt: skip

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.\
    declarations.declarations__shared \
    import Record  # fmt: skip


_ACTIVE = ("active", "governs")
_PASSIVE = ("passive", "depends_on")
_MODEL_DESCRIPTORS = {"Relation", "Operator", "Format", "Term"}


def _subject_namespace(
    expr: _subject_Path | _subject_RelationChain,
) -> str | None:
    if isinstance(expr, _subject_RelationChain):
        first = expr.endpoints[0]
        if isinstance(first.head, _subject_Name) and first.head.value in {
            "ANECHOIC_MODEL",
            "ANECHOIC_STRUCTURE",
        }:
            return (
                first.head.value
                if _subject_namespace_local_expression(expr) is not None
                else None
            )
        if (
            isinstance(first.head, _subject_Name)
            and first.head.value == "ANECHOIC"
            and len(expr.endpoints) > 1
            and isinstance(expr.endpoints[1].head, _subject_Name)
            and _subject_namespace_local_expression(expr) is not None
        ):
            return "ANECHOIC_" + expr.endpoints[1].head.value
        return None
    return (
        _subject_namespace(expr.head)
        if isinstance(expr.head, (_subject_Path, _subject_RelationChain))
        else None
    )


def _has_concrete_instance(expr: object) -> bool:
    if isinstance(expr, _subject_SelectionGroup):
        return any(_has_concrete_instance(member) for member in expr.members)
    if isinstance(expr, _subject_Qualification):
        return _has_concrete_instance(expr.relative_path)
    if isinstance(expr, _subject_RelationChain):
        return any(
            _has_concrete_instance(endpoint) for endpoint in expr.endpoints
        )
    if not isinstance(expr, _subject_Path):
        return False
    if _has_concrete_instance(expr.head):
        return True
    prior = expr.head.value if isinstance(expr.head, _subject_Name) else None
    for step in expr.steps:
        if step.operator == "//" and prior not in _MODEL_DESCRIPTORS:
            return True
        if _has_concrete_instance(step.operand):
            return True
        if isinstance(step.operand, _subject_Name):
            prior = step.operand.value
    return False


def _scope_subject(value: str) -> str:
    "Classify explicit MODEL Subjects by their declared kinds only."
    try:
        expression = _subject_parse_subject_expression(
            value, subject_profile="approved"
        ).expression
    except _subject_SubjectNotationError:
        if re.match(
            r"^\s*(?:ANECHOIC_STRUCTURE|ANECHOIC\s*<\+\s*STRUCTURE)\s*<\+",
            value,
        ):
            return "structure"
        return (
            "model"
            if re.match(
                r"^\s*(?:ANECHOIC_MODEL|ANECHOIC\s*<\+\s*MODEL)\s*<\+", value
            )
            else "unresolved"
        )

    namespace = _subject_namespace(expression)
    if namespace == "ANECHOIC_STRUCTURE":
        return "structure"
    if namespace != "ANECHOIC_MODEL":
        return _unqualified_scope(expression)

    return "instance" if _has_concrete_instance(expression) else "model"


def _unqualified_scope(expression: object) -> str:
    if isinstance(expression, _subject_Path) and isinstance(
        expression.head, _subject_Name
    ):
        if expression.head.value == "ANECHOIC_MODEL" and expression.steps:
            target = _contract_target(expression)
            if target is not None and target[0] == "relation":
                return "model"
        if expression.steps:
            return "unresolved"
        if expression.head.value == "ANECHOIC_MODEL":
            return "model"
        if expression.head.value == "ANECHOIC_STRUCTURE":
            return "structure"
    return "unresolved"


def select_model_subjects(
    carriers: list[Record],
) -> tuple[list[Record], list[Record]]:
    "Filter a Projection's Subject occurrences and keep source records."
    selected, unresolved = [], []
    for carrier in carriers:
        subjects = _authored_subjects(carrier)
        if subjects is None:
            selected.append(carrier)
            continue
        kept = _model_subject_values(carrier, subjects, unresolved)
        copy = dict(carrier)
        copy["subjects"] = kept
        if isinstance(carrier.get("metadata"), Mapping):
            copy["metadata"] = {**carrier["metadata"], "subjects": kept}
        selected.append(copy)
    return selected, unresolved


def _model_subject_values(carrier, subjects, unresolved):
    kept = {}
    for role, keys in (("active", _ACTIVE), ("passive", _PASSIVE)):
        for key in keys:
            if key not in subjects:
                continue
            original = subjects[key]
            values = original if isinstance(original, list) else [original]
            values_kept = []
            for value in values:
                scope = (
                    _scope_subject(value)
                    if isinstance(value, str) and value.strip()
                    else "unresolved"
                )
                if scope == "model":
                    values_kept.append(value)
                elif scope == "unresolved":
                    source = _source(carrier)
                    unresolved.append(
                        {
                            "source": source,
                            "pin": _pin(source),
                            "role": role,
                            "source_key": key,
                            "raw_value": value
                            if isinstance(value, str)
                            else str(value),
                            "message": (
                                "Subject lacks an explicit "
                                "parseable MODEL namespace; "
                                "review required."
                            ),
                        }
                    )
            if values_kept:
                kept[key] = (
                    values_kept
                    if isinstance(original, list)
                    else values_kept[0]
                )
    return kept


def _source(carrier: Mapping[str, Any]) -> Record:
    return dict(carrier.get("source", {}))


def _pin(source: Mapping[str, Any]) -> str:
    return (
        f"{source.get('atom_id', 'unknown')}"
        "@"
        f"{source.get('version', 'unknown')}"
    )


def _authored_subjects(carrier: Mapping[str, Any]) -> Mapping[str, Any] | None:
    "Read source keys before compatibility aliases add duplicate spellings."

    metadata = carrier.get("metadata")
    if isinstance(metadata, Mapping) and isinstance(
        metadata.get("subjects"), Mapping
    ):
        return metadata["subjects"]
    subjects = carrier.get("subjects")
    return subjects if isinstance(subjects, Mapping) else None


def _canonical(value: str) -> tuple[str | None, str | None]:
    "Render approved syntax, retaining names and qualification values exactly."

    try:
        expression = _subject_parse_subject_expression(
            value, subject_profile="approved"
        ).expression
    except _subject_SubjectNotationError as error:
        return None, str(error)
    return _subject_render_subject(expression), None


def _occurrences(carriers: list[Record]) -> tuple[list[Record], list[Record]]:
    rows, diagnostics = [], []
    for carrier in carriers:
        source = _source(carrier)
        subjects = _authored_subjects(carrier)
        if subjects is None:
            continue
        for role, keys in (("active", _ACTIVE), ("passive", _PASSIVE)):
            for key in keys:
                if key not in subjects:
                    continue
                values = (
                    subjects[key]
                    if isinstance(subjects[key], list)
                    else [subjects[key]]
                )
                _collect_values(values, source, role, key, rows, diagnostics)
    return rows, diagnostics


def _collect_values(values, source, role, key, rows, diagnostics):
    for value in values:
        if not isinstance(value, str) or not value.strip():
            diagnostics.append(
                {
                    "source": source,
                    "pin": _pin(source),
                    "role": role,
                    "source_key": key,
                    "raw_value": value,
                    "message": "Subject must be non-empty text.",
                }
            )
            continue
        canonical, error = _canonical(value)
        row = {
            "role": role,
            "source": source,
            "pin": _pin(source),
            "source_key": key,
            "raw_value": value,
            "subject": canonical,
        }
        if error is not None:
            row["parse_error"] = error
            diagnostics.append(
                {**row, "message": f"Unsupported Subject: {error}"}
            )
        rows.append(row)
