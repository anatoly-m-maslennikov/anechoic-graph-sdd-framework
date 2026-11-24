"""Read and write the native Atom Header in its authored order."""

from datetime import datetime
import re


_FAMILIES = {"S": "SPEC", "T": "TKT", "P": "PROJECT_CONFIG", "C": "PROJECT_CONFIG"}
_HEADER = {"atom_family", "atom_id", "concern", "structure", "container", "tier", "priority", "context", "relations", "state"}
_STATE = ("status", "version", "updated_at")
_CONCERN_LOCATOR = ("subject", "path", "relation")
_CONCERN = (*_CONCERN_LOCATOR, "components")
_CONTEXT = ("template", "label", "lens")


def _family(atom_id):
    match = re.fullmatch(r"[A-Z]+-([STPC])-[0-9]+", atom_id) if isinstance(atom_id, str) else None
    if not match:
        raise ValueError("Invalid native Atom ID")
    return _FAMILIES[match[1]]


def _text(value):
    return isinstance(value, str) and bool(value.strip())


def _container(value):
    return (isinstance(value, dict) and len(value) == 1
            and next(iter(value)) in {"atom", "component"} and _text(next(iter(value.values()))))


def _locator(value):
    return isinstance(value, dict) and set(value) == set(_CONCERN_LOCATOR) and all(
        _text(value[name]) for name in _CONCERN_LOCATOR)


def _ticket_ref(value):
    return (isinstance(value, str) and re.fullmatch(r"[a-z][a-z0-9_]*\(id=[A-Za-z0-9_-]+\)", value)
            and (not value.startswith("component(") or re.fullmatch(r"component\(id=C[0-9]+\)", value)))


def _validate_ticket_concern(concern):
    if not isinstance(concern, list) or not concern:
        raise ValueError("Native Ticket Concern requires a nonempty list of locators")
    seen = set()
    for ref in concern:
        if not (_locator(ref) or _ticket_ref(ref)):
            raise ValueError("Native Ticket Concern requires complete locators or legacy references")
        key = tuple(ref[name] for name in _CONCERN_LOCATOR) if isinstance(ref, dict) else ref
        if key in seen:
            raise ValueError("Native Ticket Concern requires distinct entries")
        seen.add(key)


def _validate_context_state(family, context, state):
    incomplete_draft = family == "PROJECT_CONFIG" and isinstance(state, dict) and state.get("status") == "draft"
    if (not isinstance(context, dict) or set(context) - set(_CONTEXT)
            or any(not _text(value) for value in context.values())
            or (family != "SPEC" and "lens" in context)
            or (family != "TKT" and "label" in context)
            or (family != "SPEC" and "template" not in context and not incomplete_draft)):
        raise ValueError("Native Context has an invalid Template, Label, or Lens")
    if (not isinstance(state, dict) or set(state) != set(_STATE) or not _text(state["status"])
            or type(state["version"]) is not int or state["version"] < 1):
        raise ValueError("Native State requires Status, Version, and Updated At")
    if (state["status"] == "in_progress"
            or (state["status"] == "ready" and family != "SPEC")
            or (state["status"] in {"in_queue", "complete"} and family != "TKT")):
        raise ValueError("Status is unavailable for the authored Atom Family")
    updated_at = state["updated_at"]
    if isinstance(updated_at, str):
        updated_at = datetime.fromisoformat(updated_at)
    if not isinstance(updated_at, datetime):
        raise ValueError("Native State requires a datetime Updated At")


def _validate_concern(metadata, family):
    if "concern" in metadata:
        concern = metadata["concern"]
        if family == "TKT" and "structure" not in metadata and not isinstance(concern, list):
            raise ValueError("Native Ticket Concern requires a list of locators")
        if family == "TKT" and isinstance(concern, list):
            _validate_ticket_concern(concern)
        elif not isinstance(concern, dict) or not concern or set(concern) - set(_CONCERN):
            raise ValueError("Native Concern requires Components or a Subject, Path, and Relation")
        if isinstance(concern, dict) and any(name in concern for name in _CONCERN_LOCATOR) and not all(
                _text(concern.get(name)) for name in _CONCERN_LOCATOR):
            raise ValueError("Native Concern requires Subject, Path, and Relation together")
        if isinstance(concern, dict) and "components" in concern:
            if family != "TKT" and metadata.get("state", {}).get("status") != "archived":
                raise ValueError("Component Concern is only available for Tickets")
            components = concern["components"]
            if (not isinstance(components, list) or not components
                    or any(not isinstance(value, str) or not re.fullmatch(r"C[0-9]+", value) for value in components)
                    or len(components) != len(set(components))):
                raise ValueError("Native Concern requires a nonempty list of distinct Component IDs")


def _validate_header(metadata):
    family = metadata.get("atom_family")
    if family == "PMETA":
        family = "PROJECT_CONFIG"
    if set(metadata) - _HEADER or family != _family(metadata.get("atom_id")):
        raise ValueError("Native Atom Family, ID, or Header keys are invalid")
    structure = metadata.get("structure")
    if structure is None:
        structure = {name: metadata[name] for name in ("container", "tier", "priority") if name in metadata}
    elif any(name in metadata for name in ("container", "tier", "priority")):
        raise ValueError("Native Structure cannot mix nested and top-level fields")
    context, state = (metadata.get(name) for name in ("context", "state"))
    if not isinstance(structure, dict) or not _container(structure.get("container")):
        raise ValueError("Native Structure requires one Container")
    if (set(structure) - {"container", "tier", "priority"}
            or ("tier" in structure and (family != "SPEC" or type(structure["tier"]) is not int))
            or ("structure" not in metadata and family == "SPEC" and "tier" not in structure)
            or ("priority" in structure) != (family == "TKT")
            or ("priority" in structure and type(structure["priority"]) is not int)):
        raise ValueError("Native Structure has an invalid Tier or Priority")
    _validate_context_state(family, context, state)
    _validate_concern(metadata, family)
    if "relations" in metadata:
        relations = metadata["relations"]
        if (not isinstance(relations, dict) or not relations
                or any(not _text(name) or not isinstance(targets, list) or not targets
                       or any(not _text(target) for target in targets) for name, targets in relations.items())):
            raise ValueError("Native Relations require a nonempty map of target reference lists")


def native_header_view(metadata):
    """Expose compatibility lookups to existing readers without altering the carrier."""
    if not {"atom_family", "atom_id", "structure", "container"}.intersection(metadata):
        return metadata
    _validate_header(metadata)
    structure = metadata.get("structure", {name: metadata[name] for name in ("container", "tier", "priority") if name in metadata})
    return {**metadata, "atom_family": _family(metadata["atom_id"]),
            "identity": {"atom_id": metadata["atom_id"]},
            "context": {**structure, **metadata["context"]}}


def native_header_model_fields(metadata):
    """Supply the flat generated Model with the Header's authored values."""
    view = native_header_view(metadata)
    context = view["context"]
    family = _family(view["identity"]["atom_id"])
    fields = {"atom_family": family, "container": context["container"]}
    fields.update({key: context[key] for key in (*_CONTEXT, "tier") if key in context})
    if family == "TKT":
        fields["priority"] = context.get("priority", 2)
    concern = view.get("concern")
    if family == "TKT":
        if concern is not None:
            fields["concern"] = _canonical_concern(view, family)
    else:
        fields.update({name: (concern or {}).get(name) for name in _CONCERN_LOCATOR})
    if "relations" in view:
        fields["relations"] = view["relations"]
    return fields


def _canonical_ticket_concern(concern):
    if isinstance(concern, dict):
        if set(concern) != {"components"}:
            raise ValueError("Ticket Concern locator cannot be converted to typed references")
        components = concern["components"]
        if (not isinstance(components, list) or not components
                or any(not isinstance(value, str) or not re.fullmatch(r"C[0-9]+", value) for value in components)
                or len(components) != len(set(components))):
            raise ValueError("Native Concern requires a nonempty list of distinct Component IDs")
        concern = [f"component(id={component})" for component in components]
    if not isinstance(concern, list):
        raise ValueError("Native Ticket Concern requires a list of locators")
    result = []
    for ref in concern:
        if _locator(ref):
            result.append({name: ref[name] for name in _CONCERN_LOCATOR})
        elif isinstance(ref, str) and re.fullmatch(r"component\(id=C[0-9]+\)", ref):
            result.append({"subject": ref[13:-1], "path": "Project Structure.components", "relation": "affects"})
        else:
            raise ValueError("Ticket Concern reference cannot be converted to a locator")
    return result


def _canonical_concern(metadata, family):
    if "concern" in metadata:
        concern = metadata["concern"]
        if family == "TKT":
            return _canonical_ticket_concern(concern)
        if isinstance(concern, dict) and "components" in concern:
            raise ValueError("Component Concern is only available for Tickets")
        if not isinstance(concern, dict) or set(concern) - set(_CONCERN_LOCATOR):
            raise ValueError("Non-Ticket Concern requires only Subject, Path, and Relation")
        return {name: concern[name] for name in _CONCERN_LOCATOR if name in concern}


def canonical_native_header(metadata):
    """Render ordered, authored fields for new native carriers and migration."""
    view = native_header_view(metadata)
    context = view.get("context", {})
    if "package_id" in context:
        raise ValueError("Move the Package ID to the Formal Claim before rewriting the Header")
    if set(view) - _HEADER - {"identity"} or set(context) - {*_CONTEXT, "container", "tier", "priority"}:
        raise ValueError("Native Header conversion would discard unrecognized data")
    identity = view.get("identity", {})
    if set(identity) != {"atom_id"}:
        raise ValueError("Native Header conversion requires one authored Atom ID")
    atom_id = identity["atom_id"]
    family = _family(atom_id)
    header = {"atom_family": family, "atom_id": atom_id}
    if "concern" in metadata:
        header["concern"] = _canonical_concern(metadata, family)
    structure = {"container": context.get("container")}
    if family == "TKT":
        structure["priority"] = context.get("priority", 2)
    elif family == "SPEC" and "tier" in context:
        structure["tier"] = context["tier"]
    if family == "PROJECT_CONFIG":
        header["structure"] = structure
    else:
        header.update(structure)
    header["context"] = {name: context[name] for name in _CONTEXT if name in context}
    if "relations" in view:
        header["relations"] = view["relations"]
    header["state"] = {name: view["state"][name] for name in _STATE}
    _validate_header(header)
    return header
