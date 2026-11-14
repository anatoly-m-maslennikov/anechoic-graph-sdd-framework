"""Resolve the HAS_ACTIVE_SUBJECT link represented by an Atom's Topics."""

import subject_notation as notation

from FEATURE_MODEL import FEATURE_GENERATED_MODEL as generated
from carrier_aliases import matches_named_value
from header_groups import header_value
from .common import InputError
from .header_relation_rules import model_endpoint_context, validate_resolved_relation
from .subject_aspects import resolve_aspect
from .subject_selections import resolve_named_selection

RELATION = "HAS_ACTIVE_SUBJECT"


def validate_main_subject_relation(selection, model, view, *, require_resolution, body=None):
    rules = getattr(getattr(model, "candidate_schema", None), "header_relation_rules", None)
    if not rules or "subjects" not in rules or RELATION not in rules["endpoints"]:
        return
    try:
        _, subject = header_value(view, "topics.main_subject")
        if isinstance(subject, dict):
            values = [item for group in subject.values() for item in (group if isinstance(group, list) else [group])]
            subject = values[0] if len(values) == 1 else None
        context = model_endpoint_context(rules, view)
        typed_target = "target_entity_paths" in context[2].get(RELATION, {})
        strict = require_resolution or typed_target
        try:
            defining = matches_named_value(view.get("role"), "Requirement") and matches_named_value(
                view.get("form"), "Declaration")
            target = _resolve_subject(selection, rules, context[0], subject, strict=strict,
                                      proposed_body=body if defining else None)
        except notation.SubjectNotationError:
            if require_resolution or typed_target:
                raise
            return
        if target is None:
            # Historical unbound Topics remain editable while their declaring sources migrate.
            if strict:
                raise ValueError("Main Subject does not resolve to one declared endpoint")
            return
        if matches_named_value(view.get("form"), "Scope Unit Declaration") and target[1] != "instances":
            raise ValueError("Main Subject must identify a Scope Unit instance")
        validate_resolved_relation(rules, context, RELATION, [target])
    except ValueError as error:
        raise InputError("main_subject", str(error)) from error


def _resolve_subject(selection, rules, model_types, subject, *, strict, proposed_body):
    if not isinstance(subject, str) or not subject.strip():
        return None
    expression = notation.parse_subject_expression(subject, subject_profile="approved").expression
    local = notation.namespace_local_expression(expression) or expression
    address = notation.render_subject(local)
    namespace = _namespace(expression)
    if (isinstance(expression, notation.Path) and isinstance(expression.head, notation.Name)
            and expression.head.value == "CAPRMEDIO_STRUCTURE"
            and expression.value_format is None and expression.value_cardinality is None
            and all(step.operator == "/" and isinstance(step.operand, notation.Name) for step in expression.steps)):
        return _resolve_structure_scope(selection, tuple(step.operand.value for step in expression.steps))
    if _is_scope_unit(local):
        if namespace in {"CAPRMEDIO_MODEL", "MODEL"}:
            return None
        kind = _resolve_scope_unit(selection, local.head.value, local.steps[0].operand.value)
        return kind, "instances"
    if namespace in {"CAPRMEDIO_STRUCTURE", "PROJECT STRUCTURE", "STRUCTURE"}:
        if strict:
            aspect = resolve_aspect(selection, expression, proposed_body=proposed_body)
            if aspect is not None:
                return (generated.Aspect, "instances") if aspect else None
            named_selection = resolve_named_selection(selection, expression)
            if named_selection is not None:
                return (generated.NamedSelection, "instances") if named_selection else None
        if _is_project_structure(selection, expression):
            return generated.ProjectStructure, "instances"
        return None
    kind = model_types.get(address)
    if kind is None and (class_name := rules["subjects"].get(address)):
        kind = getattr(generated, class_name)
    return (kind, "model_entities") if kind is not None else None


def _is_project_structure(selection, expression):
    if not isinstance(expression, notation.Path) or not isinstance(expression.head, notation.Name):
        return False
    project = selection.settings["project"]["name"]
    if expression.head.value == "CAPRMEDIO_STRUCTURE" and not expression.steps:
        return project.casefold() == "caprmedio"
    return (expression.head.value == "PROJECT STRUCTURE" and len(expression.steps) == 1
            and expression.steps[0].operator == "//" and isinstance(expression.steps[0].operand, notation.Name)
            and expression.steps[0].operand.value.casefold() == project.casefold())


def _namespace(expression):
    root = expression.endpoints[0] if isinstance(expression, notation.RelationChain) else expression
    if isinstance(root.head, notation.Name):
        if root.head.value == "CAPRMEDIO" and isinstance(expression, notation.RelationChain):
            legacy = expression.endpoints[1].head
            return legacy.value if isinstance(legacy, notation.Name) else None
        return root.head.value


def _is_scope_unit(expression):
    return (isinstance(expression, notation.Path) and isinstance(expression.head, notation.Name)
            and expression.head.value in {"Project", "Scope Unit"} and len(expression.steps) == 1
            and expression.steps[0].operator == "//" and isinstance(expression.steps[0].operand, notation.Name)
            and expression.value_format is None and expression.value_cardinality is None)


def _resolve_scope_unit(selection, kind, name):
    rows = [row for row in selection.structure["scope_units"] if name == row["scope_unit_name"]
            and (kind == "Scope Unit" or row["parent"] == "PROJECT")]
    if len(rows) != 1:
        raise ValueError("Main Subject Scope Unit is missing or ambiguous")
    return generated.Project if rows[0]["parent"] == "PROJECT" else generated.ScopeUnit


def _resolve_structure_scope(selection, path):
    rows = selection.structure["scope_units"]
    matches = [row for row in rows if row["parent"] == "PROJECT" and row["scope_unit_name"].casefold() == "caprmedio"]
    for name in path:
        if len(matches) != 1:
            break
        parent = matches[0]["scope_unit_name"]
        matches = [row for row in rows if row["parent"] == parent and row["scope_unit_name"] == name]
    if len(matches) != 1:
        return None
    return (generated.Project if not path else generated.ScopeUnit), "instances"
