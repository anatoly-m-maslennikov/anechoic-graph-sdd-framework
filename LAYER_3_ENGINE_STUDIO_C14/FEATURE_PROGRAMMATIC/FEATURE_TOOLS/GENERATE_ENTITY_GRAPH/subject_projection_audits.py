"""Small, source-bound audits for selected Subject expressions."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping
from typing import Any

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30 import subject_notation__pub as notation
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carrier_compat__pub import matches_named_value

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.declaration_evidence import Record, _view
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.subject_audit_coverage import (
    _coverage,
    _entity_definitions,
    _entity_target,
    _property_parts,
    _term_definitions,
    _term_identity,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.subject_audit_occurrences import _occurrences, _pin, _source
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.subject_projection_data import build_subject_projection_data


def _provenance(rows: list[Record]) -> Record:
    occurrences = sorted(rows, key=lambda row: (row["pin"], row["source_key"], row["raw_value"]))
    return {"raw_values": sorted({row["raw_value"] for row in rows}),
            "pins": sorted({row["pin"] for row in rows}), "occurrences": occurrences}


def _is_defining(carrier: Mapping[str, Any], target: tuple[str, str]) -> bool:
    source = _source(carrier)
    atom_id = str(source.get("atom_id", ""))
    form = str(_view(carrier).get("type", ""))
    if atom_id.startswith("CA-R-") and (form.endswith("Declaration") or form.endswith("Definition")):
        return True
    return (atom_id.startswith("CA-M-") and matches_named_value(_view(carrier).get("content_role"), "Method")
            and matches_named_value(form, "Term Definition") and target[0] == "component"
            and _term_identity(target[1]) is not None)


def _inherited_definition_refs(target: tuple[str, str], data: Mapping[str, Any]) -> list[str]:
    if target[0] != "property":
        return []
    parts = _property_parts(target[1])
    if parts is None:
        return []
    origin, relative = parts
    entity = next((row for row in data["entities"] if row["identity"] == origin), None)
    if entity is None:
        return []
    return sorted({ref for row in entity["inherited_properties"] if row["relative_name"] == relative
                   for ref in row["declaration_refs"]})


def _entity_summary(carriers: list[Record], occurrences: list[Record], data: Mapping[str, Any]) -> Record:
    """Separate defining-carrier coverage from active Subject coverage."""

    source_index = {(str(_source(carrier).get("path", "")), _pin(_source(carrier))): carrier for carrier in carriers}
    rows: dict[tuple[str, str], Record] = {}
    for occurrence in occurrences:
        if occurrence["subject"] is None:
            continue
        try:
            target = _entity_target(occurrence["subject"])
        except notation.SubjectNotationError:
            target = None
        if target is None:
            continue
        row = rows.setdefault(target, {"identity": target[1], "kind": target[0],
                                       "defining_refs": set(), "active_refs": set(), "subjects": []})
        row["subjects"].append({key: occurrence[key] for key in ("raw_value", "pin", "source_key", "role", "source")})
        row["defining_refs"].update(_inherited_definition_refs(target, data))
        carrier = source_index.get((str(occurrence["source"].get("path", "")), occurrence["pin"]))
        if occurrence["role"] == "active":
            row["active_refs"].add(occurrence["pin"])
            if carrier is not None and _is_defining(carrier, target):
                row["defining_refs"].add(occurrence["pin"])
    entities = []
    for row in rows.values():
        defining_refs, active_refs = sorted(row["defining_refs"]), sorted(row["active_refs"])
        entities.append({**row, "defining_refs": defining_refs, "active_refs": active_refs,
                         "missing_definition": not defining_refs, "missing_active": not active_refs,
                         "subjects": sorted(row["subjects"], key=lambda item: (item["pin"], item["source_key"], item["raw_value"]))})
    entities.sort(key=lambda row: (row["kind"], row["identity"]))
    return {"kind": "entity_definition_summary", "entities": entities,
            "display_entities": [row for row in entities if row["missing_definition"] or row["missing_active"]],
            "coverage": {"entities": len(entities), "entities_with_any_missing": sum(
                row["missing_definition"] or row["missing_active"] for row in entities)}}


def _passive_only_subjects(
    occurrences: list[Record], diagnostics: list[Record],
    unresolved_subjects: int, unresolved_occurrences: int,
) -> Record:
    active = {row["subject"] for row in occurrences if row["role"] == "active" and row["subject"] is not None}
    active_raw = {row["raw_value"].strip() for row in occurrences if row["role"] == "active"}
    passive: dict[str, list[Record]] = defaultdict(list)
    for row in occurrences:
        if row["role"] != "passive":
            continue
        key = row["subject"] if row["subject"] is not None else "raw:" + row["raw_value"].strip()
        passive[key].append(row)
    passive_rows = [
        {"subject": rows[0]["subject"] or rows[0]["raw_value"],
         "unresolved": rows[0]["subject"] is None, **_provenance(rows)}
        for subject, rows in passive.items()
        if (subject not in active if rows[0]["subject"] is not None else rows[0]["raw_value"].strip() not in active_raw)
    ]
    return {
        "kind": "passive_only_subjects",
        "subjects": sorted(passive_rows, key=lambda row: row["subject"]),
        "diagnostics": diagnostics,
        "coverage": {
            "subject_occurrences": len(occurrences),
            "parsed_subjects": len({row["subject"] for row in occurrences if row["subject"] is not None}),
            "unresolved_subjects": unresolved_subjects,
            "unresolved_occurrences": unresolved_occurrences,
            "active_subjects": len(active),
            "passive_only_subjects": len(passive_rows),
        },
    }


def build_subject_audits(carriers: list[Record], data: Record | None = None, *, scope_diagnostics: list[Record] | None = None) -> Record:
    """Build both selected-frontier Subject audits without admitting new Nodes."""

    data = build_subject_projection_data(carriers) if data is None else data
    occurrences, diagnostics = _occurrences(carriers)
    definitions = _entity_definitions(carriers)
    term_definitions = _term_definitions(carriers)
    coverage_rows, unresolved = [], []
    unresolved_rows: dict[str, list[Record]] = defaultdict(list)
    for row in occurrences:
        if row["subject"] is None:
            unresolved_rows[row["raw_value"].strip()].append(row)
    for raw, rows in sorted(unresolved_rows.items()):
        unresolved.append({"subject": rows[0]["raw_value"], "status": "unresolved",
                           "message": f"Unsupported Subject: {rows[0]['parse_error']}", **_provenance(rows)})
    scope_groups: dict[str, list[Record]] = defaultdict(list)
    for diagnostic in scope_diagnostics or []:
        scope_groups[str(diagnostic["raw_value"])].append(diagnostic)
    for value, rows in sorted(scope_groups.items()):
        unresolved.append({"subject": value, "status": "unresolved", "message": rows[0]["message"],
                           **_provenance(rows)})
    diagnostics.extend(scope_diagnostics or [])
    for subject in sorted({row["subject"] for row in occurrences if row["subject"] is not None}):
        result = _coverage(subject, data, definitions, term_definitions)
        row = {"subject": subject, **result, **_provenance([row for row in occurrences if row["subject"] == subject])}
        (unresolved if result["status"] == "unresolved" else coverage_rows).append(row)
    return {
        "passive_only_subjects": _passive_only_subjects(
            occurrences, diagnostics,
            len(unresolved_rows) + len(scope_groups),
            sum(row["subject"] is None for row in occurrences) + len(scope_diagnostics or []),
        ),
        "subjects_without_declaration_coverage": {
            "kind": "subjects_without_declaration_coverage",
            "subjects": [row for row in coverage_rows if row["status"] == "missing"],
            "informational": [row for row in coverage_rows if row["status"] == "outside_required_scope"],
            "unresolved": unresolved, "diagnostics": diagnostics,
            "coverage": {"known_missing": sum(row["status"] == "missing" for row in coverage_rows),
                         "unresolved": len(unresolved)},
        },
        "entity_definition_summary": _entity_summary(carriers, occurrences, data),
    }


def render_subject_audit(audit: Mapping[str, Any], kind: str) -> str:
    """Render a body only; callers own projection frontmatter and wrapping."""

    report = audit[kind] if kind in audit else audit
    def evidence(row: Mapping[str, Any]) -> str:
        keys = sorted({item["source_key"] for item in row.get("occurrences", [])})
        return f"pins: {', '.join(row.get('pins', []))}; keys: {', '.join(keys)}"

    if report["kind"] == "passive_only_subjects":
        lines = ["# Subjects Used Only Passively", "", "## Subjects", ""]
        lines.extend(f"- `{row['subject']}` — {evidence(row)}"
                     + ("; unresolved syntax" if row["unresolved"] else "") for row in report["subjects"])
        lines.extend(["", f"## Diagnostics ({len(report['diagnostics'])})", ""])
        lines.extend(f"- `{row['raw_value']}` — {row['pin']}; {row['source_key']}; {row['message']}" for row in report["diagnostics"])
    elif report["kind"] == "subjects_without_declaration_coverage":
        lines = ["# Subjects Without Effective Requirement Declaration Coverage", "", "## Subjects", ""]
        lines.extend(f"- `{row['subject']}` — {row['message']}; {evidence(row)}" for row in report["subjects"])
        lines.extend(["", "## Informational outside required scope", ""])
        lines.extend(f"- `{row['subject']}` — {row['message']}; {evidence(row)}"
                     + (f"; Term Definition: {', '.join(row['term_definition_refs'])}" if row.get("term_definition_refs") else "")
                     for row in report["informational"])
        lines.extend(["", "## Unresolved coverage needing review", ""])
        lines.extend(f"- `{row['subject']}` — {row['message']}; {evidence(row)}" for row in report["unresolved"])
    else:
        lines = ["# Entity Definition Summary", "", "| Entity | Kind | Defining atom | Active Subject |", "| --- | --- | --- | --- |"]
        for row in report["display_entities"]:
            lines.append(f"| `{row['identity']}` | {row['kind']} | {'missing' if row['missing_definition'] else ', '.join(row['defining_refs'])} | {'missing' if row['missing_active'] else ', '.join(row['active_refs'])} |")
    if not any(line.startswith("- ") for line in lines):
        lines.append("- None.")
    return "\n".join(lines) + "\n"
