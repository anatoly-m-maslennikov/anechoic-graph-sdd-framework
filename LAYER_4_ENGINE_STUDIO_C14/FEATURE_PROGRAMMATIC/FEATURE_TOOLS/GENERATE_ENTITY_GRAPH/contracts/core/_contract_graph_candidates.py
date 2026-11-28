"""Collect source-bound graph candidates."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping
from typing import Any

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.model.notation.notation__shared import (
    Path as _subject_Path,
    RelationChain as _subject_RelationChain,
    SubjectNotationError as _subject_SubjectNotationError,
    parse_subject_expression as _subject_parse_subject_expression,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.content.content__shared import (
    carrier_read_view,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.carriers__shared import (
    matches_named_value,
)
from ...claims.claims__shared import (
    extract_claim_constraints,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.claims.primitives.primitives__shared import (
    claim_fenced_blocks,
    claim_python_blocks,
    claim_prose,
    has_prose_claim,
    section_text,
)
from ...contracts.contracts__shared import _declaration_target

Record = dict[str, Any]
Candidate = tuple[
    Record,
    Mapping[str, Any],
    str | None,
    _subject_Path | _subject_RelationChain | None,
]

_RMED = {"Requirement", "Method", "Evaluation", "Delivery"}
_DECLARATION_FORMS = {
    "Declaration",
    "Relation Declaration",
    "Relation Definition",
    "Entity Definition",
}


def _view(carrier: Mapping[str, Any]) -> Mapping[str, Any]:
    view = carrier.get("read_view")
    if isinstance(view, Mapping):
        return view
    metadata = carrier.get("metadata")
    return (
        carrier_read_view(dict(metadata))
        if isinstance(metadata, Mapping)
        else {}
    )


def _active(carrier: Mapping[str, Any]) -> str | None:
    subjects = carrier.get("subjects")
    if not isinstance(subjects, Mapping):
        return None
    value = carrier_read_view({"subjects": dict(subjects)})["subjects"].get(
        "governs"
    )
    values = value if isinstance(value, list) else [value]
    return (
        values[0]
        if len(values) == 1
        and isinstance(values[0], str)
        and values[0].strip()
        else None
    )


def _entry(
    carrier: Mapping[str, Any], subject: str, target: str, kind: str
) -> Record:
    clauses, diagnostics = extract_claim_constraints(carrier)
    source = dict(carrier["source"])
    entry = {
        "source": source,
        "subject": subject,
        "target": target,
        "kind": kind,
        "blocks": claim_fenced_blocks(carrier),
        "clauses": [row for row in clauses if row.get("group") != "instances"],
        "instance_clauses": [
            row for row in clauses if row.get("group") == "instances"
        ],
        "prose": claim_prose(carrier),
        "prose_claim": has_prose_claim(carrier),
        "claim_scope": section_text(carrier, "Claim Scope"),
        "semantics": section_text(carrier, "Semantics"),
        "details": section_text(carrier, "Details"),
        "diagnostics": [
            {**row, "source": row.get("source", source)} for row in diagnostics
        ],
    }
    python_blocks = claim_python_blocks(carrier)
    if python_blocks:
        entry["python_blocks"] = python_blocks
    return entry


def _gap(
    carrier: Mapping[str, Any], message: str, subject: str | None = None
) -> Record:
    return {
        **_entry(carrier, subject or "", "", "unbound"),
        "message": message,
    }


def _is_declaration(view: Mapping[str, Any]) -> bool:
    return matches_named_value(
        view.get("content_role"), "Requirement"
    ) and any(
        matches_named_value(view.get("type"), name)
        for name in _DECLARATION_FORMS
    )


def _native_class_kind(subject, identity, kind, entry, carrier, gaps):
    native_classes = [
        clause
        for clause in entry["clauses"]
        if clause.get("kind") == "native_class"
    ]
    if native_classes:
        from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.model.model__shared import (
            model_class_target,
        )

        if (
            len(native_classes) != 1
            or model_class_target(
                subject,
                native_classes[0].get("entity_name"),
                require_namespace=False,
            )
            != identity
        ):
            gaps.append(
                _gap(
                    carrier,
                    "Native class requires a matching declared "
                    "Model Entity Subject.",
                    subject,
                )
            )
            return None
        if (
            kind == "instance"
            and identity.startswith("Node/")
            and "//" in identity
        ):
            kind = "primary_node"
            entry["kind"] = kind
    return kind


def _collect_candidate(
    carrier, catalog, declaration_carriers, candidates, gaps
):
    try:
        view, subject = _view(carrier), _active(carrier)
    except ValueError as error:
        gaps.append(_gap(carrier, f"Carrier aliases conflict: {error}"))
        return
    if not any(
        matches_named_value(view.get("content_role"), name) for name in _RMED
    ):
        return
    if subject is None:
        gaps.append(_gap(carrier, "Expected exactly one active Subject."))
        return
    try:
        expression = _subject_parse_subject_expression(
            subject, subject_profile="approved"
        ).expression
    except _subject_SubjectNotationError as error:
        gaps.append(_gap(carrier, str(error), subject))
        return
    candidates.append((carrier, view, subject, expression))
    if not _is_declaration(view):
        return
    target, message = _declaration_target(expression)
    if target is None:
        gaps.append(_gap(carrier, message, subject))
        return
    kind, identity = target
    entry = _entry(carrier, subject, identity, kind)
    kind = _native_class_kind(subject, identity, kind, entry, carrier, gaps)
    if kind is None:
        return
    catalog[(kind, identity)].append(entry)
    if kind != "relation" and any(
        matches_named_value(view.get("type"), name)
        for name in {"Declaration", "Entity Definition"}
    ):
        declaration_carriers.append(carrier)


def _collect_candidates(carriers):
    catalog: dict[tuple[str, str], list[Record]] = defaultdict(list)
    declaration_carriers: list[Record] = []
    candidates: list[Candidate] = []
    gaps: list[Record] = []
    for carrier in carriers:
        _collect_candidate(
            carrier, catalog, declaration_carriers, candidates, gaps
        )

    return catalog, declaration_carriers, candidates, gaps
