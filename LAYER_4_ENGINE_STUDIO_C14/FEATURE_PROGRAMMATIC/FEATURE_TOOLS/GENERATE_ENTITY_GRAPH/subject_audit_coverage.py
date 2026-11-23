"""Match Subject occurrences to admitted declarations and definitions."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping
from dataclasses import replace
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
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import matches_named_value
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.contract_graph_bindings import _conditional_target
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.contract_graph_targets import _target as _contract_target
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.current_subject_common import _has_selection, _model_target, _target_kind, namespace_local_expression
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.declaration_evidence import Record, _view
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.subject_audit_occurrences import _authored_subjects, _canonical, _pin, _source


def _local_target(subject: str) -> tuple[str, str] | None:
    """Return an existing declaration-shaped target; never expand selectors."""

    expression = _subject_parse_subject_expression(subject, subject_profile="approved").expression
    expression = namespace_local_expression(expression) or expression
    if _has_selection(expression):
        return None
    if (isinstance(expression, _subject_Path) and isinstance(expression.head, _subject_Name)
            and expression.head.value in {"ANECHOIC_MODEL", "ANECHOIC_STRUCTURE"} and not expression.steps):
        return None
    target = _contract_target(expression)
    if target is not None:
        return target
    if not isinstance(expression, _subject_Path):
        return None
    if isinstance(expression.head, _subject_Name) and expression.head.value in {"CFEL", "Carrier", "Term"}:
        return "component", _model_target(expression)
    kind = _target_kind(expression)
    if kind in {"primary_node", "property", "instance", "relation"}:
        return kind, _model_target(expression)
    return None


def _entity_target(subject: str) -> tuple[str, str] | None:
    """Keep a direct entity target or the last path in a plain context chain."""

    expression = _subject_parse_subject_expression(subject, subject_profile="approved").expression
    if isinstance(expression, _subject_RelationChain):
        if not expression.links or any(link.operator != "<+" or link.relation_type is not None for link in expression.links):
            return None
        expression = expression.endpoints[-1]
    if not isinstance(expression, _subject_Path):
        return None
    if any(step.operator in {":", ":="} or isinstance(step.operand, _subject_Qualification) for step in expression.steps):
        return None
    rendered = _subject_render_subject(expression)
    return _local_target(rendered)


def _property_parts(target: str) -> tuple[str, str] | None:
    expression = _subject_parse_subject_expression(target, subject_profile="approved").expression
    if not isinstance(expression, _subject_Path):
        return None
    for index, step in enumerate(expression.steps):
        if step.operator == ".":
            origin = replace(expression, steps=expression.steps[:index], value_format=None, value_cardinality=None)
            suffix = replace(expression, head=step.operand, steps=expression.steps[index + 1:],
                             value_format=None, value_cardinality=None)
            return _subject_render_subject(origin), _subject_render_subject(suffix)
    return None


def _entity_definitions(carriers: list[Record]) -> dict[str, list[Record]]:
    rows: dict[str, list[Record]] = defaultdict(list)
    for carrier in carriers:
        view = _view(carrier)
        if not matches_named_value(view.get("content_role"), "Requirement") or not matches_named_value(view.get("type"), "Entity Definition"):
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
    expression = _subject_parse_subject_expression(subject, subject_profile="approved").expression
    expression = namespace_local_expression(expression) or expression
    if (not isinstance(expression, _subject_Path) or not isinstance(expression.head, _subject_Name)
            or expression.head.value != "Term" or len(expression.steps) != 1
            or expression.steps[0].operator != "//" or not isinstance(expression.steps[0].operand, _subject_Name)
            or expression.value_format is not None or expression.value_cardinality is not None):
        return None
    return _subject_render_subject(expression)


def _term_definitions(carriers: list[Record]) -> dict[str, list[Record]]:
    rows: dict[str, list[Record]] = defaultdict(list)
    for carrier in carriers:
        view = _view(carrier)
        if (not matches_named_value(view.get("content_role"), "Method") or not matches_named_value(view.get("type"), "Term Definition")
                or not str(_source(carrier).get("atom_id", "")).startswith("CA-M-")):
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


def _declaration_catalog(data: Mapping[str, Any]) -> dict[tuple[str, str], list[Record]]:
    declarations = data["declarations"]
    catalog = {("primary_node", identity): rows for identity, rows in declarations.get("primary_nodes", {}).items()}
    for kind_name, key in (("property", "properties"), ("instance", "instances"),
                           ("relation", "relations"), ("component", "components")):
        catalog.update({(kind_name, identity): rows for identity, rows in declarations.get(key, {}).items()})
    return catalog


def _conditional_coverage(subject: str, catalog: Mapping[tuple[str, str], list[Record]]) -> Record | None:
    expression = _subject_parse_subject_expression(subject, subject_profile="approved").expression
    expression = namespace_local_expression(expression) or expression
    conditional = _conditional_target(expression, catalog)
    if conditional is None:
        return None
    bound, binding, _ = conditional
    return {"status": "covered", "base_target": bound[1], "binding": binding,
            "declaration_refs": [_pin(row["source"]) for row in catalog[bound]]}


def _inherited_property_coverage(identity: str, data: Mapping[str, Any]) -> Record | None:
    parts = _property_parts(identity)
    if parts is None:
        return None
    origin, relative = parts
    entity = next((row for row in data["entities"] if row["identity"] == origin), None)
    if entity is None:
        return None
    inherited = [row for row in entity["inherited_properties"] if row["relative_name"] == relative]
    if not inherited:
        return None
    return {"status": "covered", "target": identity, "inherited": True,
            "declaration_refs": sorted({ref for row in inherited for ref in row["declaration_refs"]})}


def _instance_coverage(identity: str, declarations: Mapping[str, Any]) -> Record | None:
    expression = _subject_parse_subject_expression(identity, subject_profile="approved").expression
    assert isinstance(expression, _subject_Path)
    index = next((i for i, step in enumerate(expression.steps) if step.operator == "//"), None)
    if index is not None:
        base = _subject_render_subject(replace(expression, steps=expression.steps[:index], value_format=None, value_cardinality=None))
        declared = declarations["primary_nodes"].get(base)
        if declared:
            return {"status": "covered", "target": identity, "base_target": base,
                    "declaration_refs": [_pin(row["source"]) for row in declared]}
    return None


def _coverage(subject: str, data: Mapping[str, Any], definitions: Mapping[str, list[Record]],
              term_definitions: Mapping[str, list[Record]]) -> Record:
    declarations = data["declarations"]
    known = _declaration_catalog(data)
    target = _local_target(subject)
    if target is None:
        conditional = _conditional_coverage(subject, known)
        return ({**conditional, "target": conditional["base_target"]} if conditional is not None else
                {"status": "unresolved", "message": "Subject is not one direct known target; review required."})
    kind, identity = target
    catalog = {"primary_node": "primary_nodes", "property": "properties", "instance": "instances",
               "relation": "relations", "component": "components"}.get(kind)
    keys = [identity, identity.removeprefix("Relation//")] if kind == "relation" else [identity]
    direct = next((declarations.get(catalog, {}).get(key) for key in keys if declarations.get(catalog, {}).get(key)), None)
    if direct:
        return {"status": "covered", "target": identity, "declaration_refs": [
            _pin(row["source"]) for row in direct
        ]}
    if kind == "property":
        inherited = _inherited_property_coverage(identity, data)
        if inherited is not None:
            return inherited
    if kind == "instance":
        inherited = _instance_coverage(identity, declarations)
        if inherited is not None:
            return inherited
    conditional = _conditional_coverage(subject, known)
    if conditional is not None:
        return {**conditional, "target": identity}
    term_identity = _term_identity(subject)
    if term_identity is not None and term_identity in term_definitions:
        return {"status": "outside_required_scope", "target": identity,
                "message": "Term has a Method / Term Definition; outside Requirement Declaration scope",
                "term_definition_refs": [_pin(source) for source in term_definitions[term_identity]]}
    definition_refs = definitions.get(subject, [])
    if kind == "component" and definition_refs:
        return {"status": "outside_required_scope", "target": identity,
                "message": "no Requirement Declaration; existing Entity Definition; outside R2469 required scope",
                "entity_definition_refs": [_pin(source) for source in definition_refs]}
    return {"status": "missing", "target": identity,
            "message": "No effective Requirement / Declaration coverage in the selected sources."}
