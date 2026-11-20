"""Read and write the native Atom Header in its authored order."""

from datetime import datetime
import re


_FAMILIES = {"S": "SPEC", "T": "TKT", "P": "PMETA"}
_HEADER = {"atom_family", "atom_id", "concern", "structure", "context", "relations", "state"}
_STATE = ("status", "version", "updated_at")
_CONCERN = ("subject", "path", "relation")


def _family(atom_id):
    match = re.fullmatch(r"[A-Z]+-([STP])-[0-9]+", atom_id) if isinstance(atom_id, str) else None
    if not match:
        raise ValueError("Invalid native Atom ID")
    return _FAMILIES[match[1]]


def _text(value):
    return isinstance(value, str) and bool(value.strip())


def _container(value):
    return (isinstance(value, dict) and len(value) == 1
            and next(iter(value)) in {"atom", "component"} and _text(next(iter(value.values()))))


def _validate_header(metadata):
    family = metadata.get("atom_family")
    if set(metadata) - _HEADER or family != _family(metadata.get("atom_id")):
        raise ValueError("Native Atom Family, ID, or Header keys are invalid")
    structure, context, state = (metadata.get(name) for name in ("structure", "context", "state"))
    if not isinstance(structure, dict) or not _container(structure.get("container")):
        raise ValueError("Native Structure requires one Container")
    if (set(structure) - {"container", "tier", "priority"}
            or ("tier" in structure and (family != "SPEC" or type(structure["tier"]) is not int))
            or ("priority" in structure) != (family == "TKT")
            or ("priority" in structure and type(structure["priority"]) is not int)):
        raise ValueError("Native Structure has an invalid Tier or Priority")
    incomplete_draft = family == "PMETA" and isinstance(state, dict) and state.get("status") == "draft"
    if (not isinstance(context, dict) or set(context) - {"template", "lens"}
            or any(not _text(value) for value in context.values())
            or (family != "SPEC" and "lens" in context)
            or (family != "SPEC" and "template" not in context and not incomplete_draft)):
        raise ValueError("Native Context has an invalid Template or Lens")
    if (not isinstance(state, dict) or set(state) != set(_STATE) or not _text(state["status"])
            or type(state["version"]) is not int or state["version"] < 1):
        raise ValueError("Native State requires Status, Version, and Updated At")
    updated_at = state["updated_at"]
    if isinstance(updated_at, str):
        updated_at = datetime.fromisoformat(updated_at)
    if not isinstance(updated_at, datetime):
        raise ValueError("Native State requires a datetime Updated At")
    if "concern" in metadata:
        concern = metadata["concern"]
        if not isinstance(concern, dict) or set(concern) != set(_CONCERN) or any(not _text(v) for v in concern.values()):
            raise ValueError("Native Concern requires Subject, Path, and Relation")
    if "relations" in metadata:
        relations = metadata["relations"]
        if (not isinstance(relations, dict) or not relations
                or any(not _text(name) or not isinstance(targets, list) or not targets
                       or any(not _text(target) for target in targets) for name, targets in relations.items())):
            raise ValueError("Native Relations require a nonempty map of target reference lists")


def native_header_view(metadata):
    """Expose compatibility lookups to existing readers without altering the carrier."""
    if not {"atom_family", "atom_id", "structure"}.intersection(metadata):
        return metadata
    _validate_header(metadata)
    return {**metadata, "identity": {"atom_id": metadata["atom_id"]},
            "context": {**metadata["structure"], **metadata["context"]}}


def native_header_model_fields(metadata):
    """Supply the flat generated Model with the Header's authored values."""
    view = native_header_view(metadata)
    context = view["context"]
    family = _family(view["identity"]["atom_id"])
    fields = {"atom_family": family, "container": context["container"]}
    fields.update({key: context[key] for key in ("template", "lens") if key in context})
    if family == "TKT":
        fields["priority"] = context.get("priority", 2)
    concern = view.get("concern", {})
    fields.update({name: concern.get(name) for name in _CONCERN})
    if "relations" in view:
        fields["relations"] = view["relations"]
    return fields


def canonical_native_header(metadata):
    """Render ordered, authored fields for new native carriers and migration."""
    view = native_header_view(metadata)
    context = view.get("context", {})
    if "package_id" in context:
        raise ValueError("Move the Package ID to the Formal Claim before rewriting the Header")
    if set(view) - _HEADER - {"identity"} or set(context) - {"container", "tier", "priority", "template", "lens"}:
        raise ValueError("Native Header conversion would discard unrecognized data")
    identity = view.get("identity", {})
    if set(identity) != {"atom_id"}:
        raise ValueError("Native Header conversion requires one authored Atom ID")
    atom_id = identity["atom_id"]
    family = _family(atom_id)
    header = {"atom_family": family, "atom_id": atom_id}
    if "concern" in view:
        header["concern"] = {name: view["concern"][name] for name in _CONCERN}
    structure = {"container": context.get("container")}
    if family == "TKT":
        structure["priority"] = context.get("priority", 2)
    elif family == "SPEC" and "tier" in context:
        structure["tier"] = context["tier"]
    header["structure"] = structure
    header["context"] = {name: context[name] for name in ("template", "lens") if name in context}
    if "relations" in view:
        header["relations"] = view["relations"]
    header["state"] = {name: view["state"][name] for name in _STATE}
    _validate_header(header)
    return header
