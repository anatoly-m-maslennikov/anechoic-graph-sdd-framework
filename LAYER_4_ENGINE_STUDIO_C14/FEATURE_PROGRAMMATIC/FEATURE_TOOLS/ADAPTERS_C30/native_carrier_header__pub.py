"""Read and write the native Atom Header in its authored order."""

from datetime import datetime as datetime
import re

from .native_carrier_header_validation import (
    _CONCERN as _CONCERN,
    _CONCERN_LOCATOR as _CONCERN_LOCATOR,
    _CONTEXT as _CONTEXT,
    _FAMILIES as _FAMILIES,
    _HEADER as _HEADER,
    _STATE as _STATE,
    _container as _container,
    _family as _family,
    _locator as _locator,
    _text as _text,
    _ticket_ref as _ticket_ref,
    _validate_concern as _validate_concern,
    _validate_context_state as _validate_context_state,
    _validate_header as _validate_header,
    _validate_ticket_concern as _validate_ticket_concern,
)


def native_header_view(metadata):
    "Expose compatibility lookups to existing readers"
    "without altering the carrier."
    if not {"atom_family", "atom_id", "structure", "container"}.intersection(
        metadata
    ):
        return metadata
    _validate_header(metadata)
    structure = metadata.get(
        "structure",
        {
            name: metadata[name]
            for name in ("container", "tier", "priority")
            if name in metadata
        },
    )
    return {
        **metadata,
        "atom_family": _family(metadata["atom_id"]),
        "identity": {"atom_id": metadata["atom_id"]},
        "context": {**structure, **metadata["context"]},
    }


def native_header_model_fields(metadata):
    """Supply the flat generated Model with the Header's authored values."""
    view = native_header_view(metadata)
    context = view["context"]
    family = _family(view["identity"]["atom_id"])
    fields = {"atom_family": family, "container": context["container"]}
    fields.update(
        {key: context[key] for key in (*_CONTEXT, "tier") if key in context}
    )
    if family == "TKT":
        fields["priority"] = context.get("priority", 2)
    concern = view.get("concern")
    if family == "TKT":
        if concern is not None:
            fields["concern"] = _canonical_concern(view, family)
    else:
        fields.update(
            {name: (concern or {}).get(name) for name in _CONCERN_LOCATOR}
        )
    if "relations" in view:
        fields["relations"] = view["relations"]
    return fields


def _canonical_ticket_concern(concern):
    if isinstance(concern, dict):
        if set(concern) != {"components"}:
            raise ValueError(
                "Ticket Concern locator cannot be converted to typed "
                "references"
            )
        components = concern["components"]
        if (
            not isinstance(components, list)
            or not components
            or any(
                not isinstance(value, str)
                or not re.fullmatch(r"C[0-9]+", value)
                for value in components
            )
            or len(components) != len(set(components))
        ):
            raise ValueError(
                "Native Concern requires a nonempty list of distinct "
                "Component IDs"
            )
        concern = [f"component(id={component})" for component in components]
    if not isinstance(concern, list):
        raise ValueError("Native Ticket Concern requires a list of locators")
    result = []
    for ref in concern:
        if _locator(ref):
            result.append({name: ref[name] for name in _CONCERN_LOCATOR})
        elif isinstance(ref, str) and re.fullmatch(
            r"component\(id=C[0-9]+\)", ref
        ):
            result.append(
                {
                    "subject": ref[13:-1],
                    "path": "Project Structure.components",
                    "relation": "affects",
                }
            )
        else:
            raise ValueError(
                "Ticket Concern reference cannot be converted to a locator"
            )
    return result


def _canonical_concern(metadata, family):
    if "concern" in metadata:
        concern = metadata["concern"]
        if family == "TKT":
            return _canonical_ticket_concern(concern)
        if isinstance(concern, dict) and "components" in concern:
            raise ValueError("Component Concern is only available for Tickets")
        if not isinstance(concern, dict) or set(concern) - set(
            _CONCERN_LOCATOR
        ):
            raise ValueError(
                "Non-Ticket Concern requires only Subject, Path, and Relation"
            )
        return {
            name: concern[name] for name in _CONCERN_LOCATOR if name in concern
        }


def _check_package_id(context):
    if "package_id" in context:
        raise ValueError(
            "Move the Package ID to the Formal Claim before "
            "rewriting the Header"
        )


def canonical_native_header(metadata):
    "Render ordered, authored fields for new native"
    "carriers and migration."
    view = native_header_view(metadata)
    context = view.get("context", {})
    _check_package_id(context)
    if set(view) - _HEADER - {"identity"} or set(context) - {
        *_CONTEXT,
        "container",
        "tier",
        "priority",
    }:
        raise ValueError(
            "Native Header conversion would discard unrecognized data"
        )
    identity = view.get("identity", {})
    if set(identity) != {"atom_id"}:
        raise ValueError(
            "Native Header conversion requires one authored Atom ID"
        )
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
    header["context"] = {
        name: context[name] for name in _CONTEXT if name in context
    }
    if "relations" in view:
        header["relations"] = view["relations"]
    header["state"] = {name: view["state"][name] for name in _STATE}
    _validate_header(header)
    return header
