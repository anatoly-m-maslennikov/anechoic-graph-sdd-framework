"""Validate the IS_CONTAINED_BY link represented by an Atom's Container."""

from FEATURE_MODEL import FEATURE_GENERATED_MODEL as generated
from .carrier import logical_view
from .common import InputError, logical_container
from .header_relation_rules import _atom_kind, model_endpoint_context, validate_resolved_relation
from .source import select_current_sources


def validate_container_relation(selection, model, view):
    """Resolve the Container and apply its declared endpoint constraints."""
    rules = getattr(getattr(model, "candidate_schema", None), "header_relation_rules", None)
    if not rules or "IS_CONTAINED_BY" not in rules.get("endpoints", {}) or "entity_rules" not in rules:
        return
    container = logical_container({}, view)
    try:
        context = model_endpoint_context(rules, view)
        kind = _container_kind(selection, model, container, context[0])
        validate_resolved_relation(rules, context, "IS_CONTAINED_BY", [(kind, "instances")])
    except ValueError as error:
        raise InputError("container", str(error)) from error


def _container_kind(selection, model, container, model_types):
    if "scope_unit" in container:
        ref = container["scope_unit"]
        prefix = selection.settings["artifacts"]["identity"]["project_prefix"]
        if ref == "CA-SU--1":
            return generated.ScopeUnit
        matches = [row for row in selection.structure["scope_units"]
                   if ref in (row["scope_unit_name"], row["scope_unit_id"])
                   or (row["parent"] == "PROJECT" and ref == f"{prefix}-SU-00")]
        if len(matches) != 1:
            raise ValueError("Container Scope Unit is missing or ambiguous")
        return generated.Project if matches[0]["parent"] == "PROJECT" else generated.ScopeUnit
    ref = container["atom"]
    if "@" in ref:
        raise ValueError("Containing Atom must use a Current reference")
    pin = select_current_sources(selection, [ref])[ref]
    return _atom_kind(logical_view(pin.metadata, model), model_types, generated.Atom)
