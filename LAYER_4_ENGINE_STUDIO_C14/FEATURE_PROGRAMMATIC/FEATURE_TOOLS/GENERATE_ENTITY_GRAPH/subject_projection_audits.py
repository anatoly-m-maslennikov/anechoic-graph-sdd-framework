"""Small, source-bound audits for selected Subject expressions."""

from __future__ import annotations

from collections import defaultdict


from ._subject_audit_render import render_subject_audit as render_subject_audit
from ._subject_audit_entities import (
    Mapping as Mapping,
    Any as Any,
    _subject_SubjectNotationError as _subject_SubjectNotationError,
    matches_named_value as matches_named_value,
    _view as _view,
    _entity_target as _entity_target,
    _property_parts as _property_parts,
    _term_identity as _term_identity,
    _pin as _pin,
    _source as _source,
    _entity_summary as _entity_summary,
    _inherited_definition_refs as _inherited_definition_refs,
    _is_defining as _is_defining,
)
from .declaration_evidence import (
    Record,
)
from .subject_audit_coverage import (
    _coverage,
    _entity_definitions,
    _term_definitions,
)
from .subject_audit_occurrences import (
    _occurrences,
)
from .subject_projection_data import (
    build_subject_projection_data,
)


def _provenance(rows: list[Record]) -> Record:
    occurrences = sorted(
        rows, key=lambda row: (row["pin"], row["source_key"], row["raw_value"])
    )
    return {
        "raw_values": sorted({row["raw_value"] for row in rows}),
        "pins": sorted({row["pin"] for row in rows}),
        "occurrences": occurrences,
    }


def _passive_only_subjects(
    occurrences: list[Record],
    diagnostics: list[Record],
    unresolved_subjects: int,
    unresolved_occurrences: int,
) -> Record:
    active, passive_rows = _passive_subject_rows(occurrences)
    return {
        "kind": "passive_only_subjects",
        "subjects": sorted(passive_rows, key=lambda row: row["subject"]),
        "diagnostics": diagnostics,
        "coverage": {
            "subject_occurrences": len(occurrences),
            "parsed_subjects": len(
                {
                    row["subject"]
                    for row in occurrences
                    if row["subject"] is not None
                }
            ),
            "unresolved_subjects": unresolved_subjects,
            "unresolved_occurrences": unresolved_occurrences,
            "active_subjects": len(active),
            "passive_only_subjects": len(passive_rows),
        },
    }


def build_subject_audits(
    carriers: list[Record],
    data: Record | None = None,
    *,
    scope_diagnostics: list[Record] | None = None,
) -> Record:
    """Build selected-frontier Subject audits without admitting new Nodes."""

    data = build_subject_projection_data(carriers) if data is None else data
    occurrences, diagnostics = _occurrences(carriers)
    definitions = _entity_definitions(carriers)
    term_definitions = _term_definitions(carriers)
    coverage_rows, unresolved = [], []
    unresolved, unresolved_rows, scope_groups = _unresolved_groups(
        occurrences, scope_diagnostics
    )
    diagnostics.extend(scope_diagnostics or [])
    _collect_coverage(
        occurrences,
        data,
        definitions,
        term_definitions,
        coverage_rows,
        unresolved,
    )
    return {
        "passive_only_subjects": _passive_only_subjects(
            occurrences,
            diagnostics,
            len(unresolved_rows) + len(scope_groups),
            sum(row["subject"] is None for row in occurrences)
            + len(scope_diagnostics or []),
        ),
        "subjects_without_declaration_coverage": _declaration_audit(
            coverage_rows, unresolved, diagnostics
        ),
        "entity_definition_summary": _entity_summary(
            carriers, occurrences, data
        ),
    }


def _passive_subject_rows(occurrences):
    active = {
        row["subject"]
        for row in occurrences
        if row["role"] == "active" and row["subject"] is not None
    }
    active_raw = {
        row["raw_value"].strip()
        for row in occurrences
        if row["role"] == "active"
    }
    passive: dict[str, list[Record]] = defaultdict(list)
    for row in occurrences:
        if row["role"] != "passive":
            continue
        key = (
            row["subject"]
            if row["subject"] is not None
            else "raw:" + row["raw_value"].strip()
        )
        passive[key].append(row)
    passive_rows = [
        {
            "subject": rows[0]["subject"] or rows[0]["raw_value"],
            "unresolved": rows[0]["subject"] is None,
            **_provenance(rows),
        }
        for subject, rows in passive.items()
        if (
            subject not in active
            if rows[0]["subject"] is not None
            else rows[0]["raw_value"].strip() not in active_raw
        )
    ]
    return active, passive_rows


def _unresolved_groups(occurrences, scope_diagnostics):
    unresolved_rows: dict[str, list[Record]] = defaultdict(list)
    for row in occurrences:
        if row["subject"] is None:
            unresolved_rows[row["raw_value"].strip()].append(row)
    unresolved = []
    for raw, rows in sorted(unresolved_rows.items()):
        unresolved.append(
            {
                "subject": rows[0]["raw_value"],
                "status": "unresolved",
                "message": f"Unsupported Subject: {rows[0]['parse_error']}",
                **_provenance(rows),
            }
        )
    scope_groups: dict[str, list[Record]] = defaultdict(list)
    for diagnostic in scope_diagnostics or []:
        scope_groups[str(diagnostic["raw_value"])].append(diagnostic)
    for value, rows in sorted(scope_groups.items()):
        unresolved.append(
            {
                "subject": value,
                "status": "unresolved",
                "message": rows[0]["message"],
                **_provenance(rows),
            }
        )
    return unresolved, unresolved_rows, scope_groups


def _collect_coverage(
    occurrences, data, definitions, term_definitions, coverage_rows, unresolved
):
    for subject in sorted(
        {row["subject"] for row in occurrences if row["subject"] is not None}
    ):
        result = _coverage(subject, data, definitions, term_definitions)
        row = {
            "subject": subject,
            **result,
            **_provenance(
                [row for row in occurrences if row["subject"] == subject]
            ),
        }
        (
            unresolved if result["status"] == "unresolved" else coverage_rows
        ).append(row)


def _declaration_audit(coverage_rows, unresolved, diagnostics):
    return {
        "kind": "subjects_without_declaration_coverage",
        "subjects": [
            row for row in coverage_rows if row["status"] == "missing"
        ],
        "informational": [
            row
            for row in coverage_rows
            if row["status"] == "outside_required_scope"
        ],
        "unresolved": unresolved,
        "diagnostics": diagnostics,
        "coverage": {
            "known_missing": sum(
                (row["status"] == "missing" for row in coverage_rows)
            ),
            "unresolved": len(unresolved),
        },
    }
