"""Adapt a prepared Atom to the generated Header and Content shape."""

from datetime import datetime

from FEATURE_MODEL.FEATURE_GENERATED_MODEL import Atom, AtomConcernContext
from FEATURE_MODEL.FEATURE_MODEL_VALIDATION.model_field_validation import validate_model_fields
from FEATURE_WORKBENCH_BACKEND.content_schema import _records_by_path, _value_excluding_declared_children
from FEATURE_WORKBENCH_BACKEND.markdown_content import content_lines, parse_content
from carrier_aliases import matches_named_value
from .atom_header_validation import _normalize_split_topics
from .common import InputError, atom_summary, logical_container


def validate_atom_instance(view, body, content_schema):
    try:
        header = _header_values(view)
        content = _content_values(view, body, content_schema)
        validate_model_fields(Atom, {"header": header, "content": content})
    except ValueError as error:
        message = str(error)
        field = "body" if message.startswith("content") else "header"
        raise InputError(field, message) from error


def _header_values(view):
    header = {key: view[key] for key in ("relations", "destination") if key in view}
    if header.get("relations") == {}:
        header.pop("relations")
    identity = {**view.get("identity", {}), "id": view["atom_id"], "ref_id": view["ref_id"]}
    identity.pop("atom_id", None)
    header["identity"] = identity
    timestamp = view["updated_at"]
    if isinstance(timestamp, str):
        timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    header["state"] = {**view.get("state", {}), "status": view["status"],
                       "version": view["version"], "updated_at": timestamp}
    header["context"] = _context_values(view)
    return header


def _context_values(view):
    context = dict(view.get("context", {}))
    for key in ("role", "form", "label", "topics", "tier"):
        if key in view:
            context[key] = view[key]
    context["container"] = logical_container({}, view)
    if isinstance(context.get("topics"), dict):
        context["topics"] = dict(context["topics"])
        _normalize_split_topics(context["topics"])
    if "tier" in context:
        context["tier"] = {"value": context["tier"]}
    plan = {key: view[key] for key in ("work_sequence_number", "ai_agent_confidence_threshold") if key in view}
    if plan and matches_named_value(view["role"], "Plan"):
        context["plan"] = {**context.get("plan", {}), **plan}
    if "priority" in view and matches_named_value(view["role"], "Concern"):
        choices = AtomConcernContext.__dataclass_fields__["priority"].metadata["allowed_values"]
        priority = next((item for item in choices
                         if matches_named_value(view["priority"], item)), view["priority"])
        context["concern"] = {**context.get("concern", {}), "priority": priority}
    return context


def _content_values(view, body, schema):
    row = {"role": view["role"], "form": view["form"]}
    declared = {rule.path for rule in schema.rules if not rule.prohibited and rule.applies(row)
                and not any(part in {"*", "**"} for part in rule.path)}
    records = _records_by_path(parse_content(body, tolerate_duplicate_siblings=True))
    lines = content_lines(body)
    properties = {}
    for path in sorted(declared & records.keys()):
        if path[0] == "summary":
            continue
        children = frozenset(candidate for candidate in declared if candidate[:-1] == path)
        _, value = _value_excluding_declared_children(records[path][0], records, children, lines)
        group = properties
        for part in path:
            entry = group.setdefault(part, {"properties": {}})
            group = entry["properties"]
        if value is not None:
            entry["value"] = value
    return {"summary": atom_summary(body).group(1).strip(), "properties": properties}
