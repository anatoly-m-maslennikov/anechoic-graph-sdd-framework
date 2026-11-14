"""Adapt Carrier values to generated Atom Header groups."""

from datetime import datetime
from dataclasses import fields

from FEATURE_MODEL.FEATURE_GENERATED_MODEL import (
    AtomConcernContext, AtomContainer, AtomContextFields, AtomDestination, AtomDestinationFile,
    AtomIdentity, AtomPlanContext, AtomState, AtomTier, AtomTopics,
)
from FEATURE_MODEL.FEATURE_MODEL_VALIDATION.model_field_validation import validate_model_fields
from carrier_aliases import matches_named_value
from header_groups import header_value
from .common import InputError, logical_container


def _validate_group(group, model_class, values):
    try:
        validate_model_fields(model_class, values)
    except ValueError as error:
        field = str(error).partition(":")[0]
        if field in {item.name for item in fields(model_class)}:
            field = "atom_id" if field == "id" else field
        else:
            field = group
        raise InputError(field, str(error)) from error


def validate_header_groups(view, timestamp: datetime):
    identity = {**view.get("identity", {}), "id": view["atom_id"], "ref_id": view["ref_id"]}
    identity.pop("atom_id", None)
    state = {**view.get("state", {}), "status": view["status"], "updated_at": timestamp}
    if "version" in view:
        state["version"] = view["version"]
    _validate_group("identity", AtomIdentity, identity)
    _validate_group("state", AtomState, state)
    if "destination" in view:
        _validate_destination(view["destination"])


def validate_context_fields(view):
    _validate_group("context", AtomContextFields, _context_values(view, AtomContextFields))
    if "container" in view:
        _validate_group("container", AtomContainer, logical_container({}, view))
    if "tier" in view:
        try:
            validate_model_fields(AtomTier, {"value": view["tier"]})
        except ValueError as error:
            raise InputError("tier", str(error)) from error
    _validate_topics(view)
    if matches_named_value(view["role"], "Plan"):
        _validate_group("context.plan", AtomPlanContext, _context_values(view, AtomPlanContext))
    elif matches_named_value(view["role"], "Concern") and "priority" in view:
        priority = view["priority"]
        (field,) = fields(AtomConcernContext)
        priority = next((value for value in field.metadata["allowed_values"]
                         if matches_named_value(priority, value)), priority)
        _validate_group("context.concern", AtomConcernContext, {"priority": priority})


def _validate_topics(view):
    if "topics" not in view:
        return  # Historical Subjects are validated by the existing schema.
    topics = view["topics"]
    if not isinstance(topics, dict):
        raise InputError("topics", "Topics must be a mapping")
    values = dict(topics)
    try:
        for name in ("main_subject", "dependencies"):
            present, value = header_value(view, f"topics.{name}")
            if present:
                values[name] = value
    except ValueError as error:
        raise InputError("topics", str(error)) from error
    _normalize_split_topics(values)
    _validate_group("topics", AtomTopics, values)


def _normalize_split_topics(values):
    for name in ("main_subject", "dependencies"):
        value = values.get(name)
        if isinstance(value, dict) and set(value) <= {"continuant", "occurrent"}:
            groups = (group if isinstance(group, list) else [group] for group in value.values())
            items = [item for group in groups for item in group]
            if name == "main_subject" and len(items) != 1:
                raise InputError("main_subject", "Topics must have one Main Subject")
            values[name] = items[0] if name == "main_subject" else items


def _context_values(view, model_class):
    return {field.name: view[field.name] for field in fields(model_class) if field.name in view}


def _validate_destination(destination):
    if not isinstance(destination, dict):
        raise InputError("destination", "Destination must be a mapping")
    values = dict(destination)
    if "file" in values:
        try:
            values["file"] = AtomDestinationFile(**values["file"])
        except TypeError as error:
            raise InputError("destination", f"Invalid Destination File: {error}") from error
    _validate_group("destination", AtomDestination, values)
