"""Admit source-backed Property contracts and resolve their effective formats."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping
from dataclasses import replace
import re

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30 import subject_notation__pub as notation

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.contract_graph_common import _source_ref
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.declaration_evidence import Record


def _source_rows(entries: list[Record]) -> tuple[list[Record], list[str]]:
    sources = [dict(entry["source"]) for entry in entries]
    return sources, sorted({_source_ref(source) for source in sources})


def _formal_claims(entries: list[Record]) -> list[Record]:
    return [
        {"source": dict(entry["source"]), "block": block["block"],
         **({"label": block["label"]} if "label" in block else {})}
        for entry in entries for block in [*entry["cfel_blocks"], *entry.get("python_blocks", [])]
    ]


def _property_parts(target: str) -> tuple[str, str] | None:
    try:
        expression = notation.parse_subject_expression(target, subject_profile="approved").expression
    except notation.SubjectNotationError:
        return None
    if not isinstance(expression, notation.Path):
        return None
    for index, step in enumerate(expression.steps):
        if step.operator == ".":
            origin = replace(expression, steps=expression.steps[:index], value_format=None, value_cardinality=None)
            suffix = replace(expression, head=step.operand, steps=expression.steps[index + 1:],
                             value_format=None, value_cardinality=None)
            return notation.render_subject(origin), notation.render_subject(suffix)
    return None


def _property_record(row: Record) -> Record | None:
    parts = _property_parts(row["target"])
    if parts is None:
        return None
    sources, refs = _source_rows(row["own"])
    scopes = {
        name for entry in row["own"] for clause in entry["clauses"]
        for name in (clause.get("applicable_entity_classes") or ())
    }
    return {
        "identity": row["target"], "relative_name": parts[1], "origin_entity": parts[0],
        "inherited": False, "source_refs": sources, "declaration_refs": refs,
        **({"multiple_applicable": True} if len(refs) > 1 else {}),
        **({"applicable_entity_classes": sorted(scopes)} if scopes else {}),
        "contracts": [
            clause for entry in row["own"] for clause in entry["clauses"]
            if clause.get("kind") in {"property_constraint", "property_value_bound", "allowed_literal"}
            or (clause.get("kind") == "relation_cardinality" and clause.get("relation") == "IS_ORDERED_RIGHT_BEFORE")
        ],
        "formal_claims": _formal_claims(row["own"]),
        "instance_constraints": [clause for entry in row["own"] for clause in entry["instance_clauses"]],
    }


def _applicable_formats(property: Record, candidates: list[Record], entries: list[Record]) -> list[Record]:
    identity = property["identity"]
    matches = []
    for clause in candidates:
        selector, selection = clause.get("property_selector"), clause.get("selection")
        if not isinstance(selector, str):
            continue
        suffix = identity[len(selector) + 1:] if identity.startswith(selector + ".") else None
        applies = (selection in {"property", "values"} and selector == identity
                   or selection in {"recursive_dependents", "recursive_dependent_values"} and suffix is not None
                   or selection in {"immediate_dependents", "immediate_dependent_values"} and suffix is not None and "." not in suffix)
        if applies:
            matches.append(clause)
    if not matches and property.get("applicable_entity_classes"):
        for entry in entries:
            for block in entry["cfel_blocks"]:
                for match in re.finditer(
                    r"(?m)^\s*([A-Za-z][A-Za-z0-9_. ]*)\.\*\*\s*::\s*\[([A-Za-z][A-Za-z0-9_]*)\]",
                    block["block"],
                ):
                    if identity.startswith(match[1].strip() + "."):
                        matches.append({"value_format": match[2], "source": block["source"]})
    return matches


def _bind_value_formats(
    identity: str, matches: list[Record], class_bindings: Mapping[str, list[tuple[str, Record]]],
    diagnostics: list[Record],
) -> list[Record] | None:
    resolved = []
    unresolved = False
    for clause in matches:
        cls = clause.get("model_value_format")
        if cls is None:
            resolved.append(clause)
            continue
        found = class_bindings.get(cls, [])
        if len(found) != 1:
            diagnostics.append({
                "code": "unresolved_model_value_format",
                "message": f"Model class {cls} has {len(found)} declaring bindings for {identity}.",
                "sources": [dict(clause["source"]), *[source for _, source in found]],
            })
            unresolved = True
            continue
        resolved.append({**clause, "value_format": found[0][0] + "//", "format_binding_source": found[0][1]})
    return None if unresolved else resolved


def _apply_effective_format(property: Record, matches: list[Record], diagnostics: list[Record]) -> None:
    identity = property["identity"]
    authority_modes = "Project.Settings.Authority Modes"
    authority_children = {authority_modes + ".Default Scope Unit Authority Mode",
                          authority_modes + ".Project Authority Mode"}
    formats = {
        "string" if (identity in authority_children
                     and clause.get("property_selector") == authority_modes
                     and clause.get("selection") in {"immediate_dependents", "immediate_dependent_values"}
                     and clause["value_format"] == "str") else clause["value_format"]
        for clause in matches
    }
    if len(formats) == 1:
        property["effective_value_format"] = next(iter(formats))
        property["effective_value_format_sources"] = [dict(clause["source"]) for clause in matches]
        bindings = [dict(clause["format_binding_source"]) for clause in matches if clause.get("format_binding_source")]
        if bindings:
            property["effective_value_format_binding_sources"] = bindings
    elif len(formats) > 1:
        refs = sorted({_source_ref(clause["source"]) for clause in matches})
        diagnostics.append({"code": "conflicting_property_value_formats",
                            "message": f"Conflicting applicable value formats for {identity}: {', '.join(sorted(formats))} ({', '.join(refs)}).",
                            "sources": [dict(clause["source"]) for clause in matches]})


def _resolve_property_formats(properties: list[Record], entries: list[Record]) -> list[Record]:
    candidates = [clause for entry in entries for clause in entry["clauses"]
                  if clause.get("kind") == "property_constraint" and clause.get("value_format") is not None
                  and not (clause["value_format"] == "" and (clause.get("value_cardinality") or {}).get("maximum") == 0)]
    diagnostics = []
    class_bindings = defaultdict(list)
    for entry in entries:
        for clause in entry.get("clauses", []):
            if clause.get("kind") == "native_class":
                class_bindings[clause["class_name"]].append((entry["target"], dict(clause["source"])))
    for property in properties:
        applicable = _applicable_formats(property, candidates, entries)
        resolved = _bind_value_formats(property["identity"], applicable, class_bindings, diagnostics)
        if resolved is not None:
            _apply_effective_format(property, resolved, diagnostics)
    return diagnostics
