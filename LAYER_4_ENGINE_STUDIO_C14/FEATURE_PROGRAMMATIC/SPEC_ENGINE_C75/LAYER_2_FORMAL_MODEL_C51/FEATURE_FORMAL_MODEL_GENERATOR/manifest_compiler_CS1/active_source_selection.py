"""Select claims from one active Model source."""

import re
from .....FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
    native_header_view,
    parse_content,
)
from .....FEATURE_TOOLS.ADAPTERS_C30.continuant_concern__pub import (
    CONTINUANT_LENS,
    continuant_model_subject,
    implicit_continuant_node,
    model_node_location,
    validate_continuant_variant,
)
from ..FEATURE_FORMAL_MODEL_GENERATOR__shared import (
    _native_claim,
)
from .active_source_claims import (
    _claim_subject,
    _custom_claims,
    _source_error,
    _typed_manifest,
)


def _append_source_claims(source, claims, subjects, records):
    for subject, claim in claims:
        if subject in subjects:
            raise _source_error(
                source,
                "duplicate_model_subject",
                subject,
                "duplicate Model Subject",
            )
        subjects.add(subject)
        records.append((source, subject, claim))


def _eligible_source(header, context, is_custom):
    if is_custom:
        if (
            header.get("atom_family") != "PROJECT_CONFIG"
            or context.get("template")
            not in {
                "model_manifest",
                "manifest_node",
                "manifest_property",
                "manifest_relation",
            }
            or context.get("container") != {"component": "C00"}
        ):
            return False
    elif context.get("container") != {"component": "C9"} or not (
        context.get("lens") == "SPEC"
        or (
            context.get("lens") == "DES"
            and context.get("template") == "manifest_property"
        )
        or context.get("lens") == CONTINUANT_LENS
    ):
        return False
    return True


def _admit_subject(subject, is_custom, template, body, source):
    if not is_custom and subject is None:
        if template in {"manifest_node", "manifest_relation"}:
            raise ValueError(
                f"{source}: typed Manifest requires a Model Claim scope"
            )
        if template != "manifest_property":
            return False
        if any(
            section["property_path"] == ["claim_scope"]
            for section in parse_content(body)
        ):
            raise ValueError(
                f"{source}: typed Manifest requires a Model Claim scope"
            )
    return True


def _source_subject(header, context, body, source, is_custom, node_locations):
    template = context.get("template")
    if (not is_custom and context.get("lens") == CONTINUANT_LENS) or (
        is_custom
        and template
        in {"manifest_node", "manifest_property", "manifest_relation"}
        and header.get("concern") is not None
    ):
        if template not in {
            "manifest_node",
            "manifest_property",
            "manifest_relation",
        }:
            raise ValueError(
                f"{source}: Continuant Declaration requires a typed "
                "Manifest template"
            )
        if any(
            section["property_path"] == ["claim_scope"]
            for section in parse_content(body)
        ):
            raise ValueError(
                f"{source}: Continuant Declaration cannot contain Claim scope"
            )
        subject = continuant_model_subject(header.get("concern"))
        if node_locations is not None and template == "manifest_node":
            node_locations[subject] = model_node_location(header["concern"])
    else:
        subject = (
            _claim_subject(body, source)
            if not is_custom
            or template in {"manifest_property", "manifest_relation"}
            else None
        )
    return subject, _admit_subject(subject, is_custom, template, body, source)


def _source_identity(header, state, metadata, path, source, is_custom):
    identity = header.get("identity")
    identifier = (
        identity.get("atom_id") if isinstance(identity, dict) else None
    )
    version = state.get("version")
    if (
        not isinstance(identifier, str)
        or not re.fullmatch(
            r"[A-Z]+-C-[0-9]+" if is_custom else r"[A-Z]+-S-[0-9]+", identifier
        )
        or (is_custom and not path.name.startswith(identifier + "-"))
        or (
            "atom_family" not in metadata
            and not re.fullmatch(
                re.escape(identifier) + r"-SPEC(?:-[A-Z_]+)?--.+\.md",
                path.name,
            )
        )
        or type(version) is not int
        or version < 1
    ):
        raise ValueError(
            f"{source}: invalid Model source identity, filename or version"
        )
    return identifier, version


def _admit_identifier(identifier, identifiers, source, subject):
    if identifier in identifiers:
        raise _source_error(
            source,
            "duplicate_model_source",
            subject,
            "duplicate Model source ID",
        )
    identifiers.add(identifier)


def _collect_active_source(
    path,
    is_custom,
    metadata,
    body,
    control,
    identifiers,
    subjects,
    records,
    typed,
    node_locations=None,
):
    header = native_header_view(metadata)
    context, state = header.get("context"), header.get("state")
    if not isinstance(context, dict) or not isinstance(state, dict):
        return
    if state.get("status") != "active":
        return
    if not _eligible_source(header, context, is_custom):
        return
    source = str(path.relative_to(control))
    subject, admitted = _source_subject(
        header, context, body, source, is_custom, node_locations
    )
    if not admitted:
        return
    identifier, version = _source_identity(
        header, state, metadata, path, source, is_custom
    )
    _admit_identifier(identifier, identifiers, source, subject)
    source = f"{source}@{version}"
    _collect_manifest_claims(
        body,
        is_custom,
        source,
        subject,
        context,
        subjects,
        records,
        typed,
        header.get("concern"),
    )


def _collect_typed_manifest(
    is_custom,
    context,
    typed_section,
    source,
    sections,
    subject,
    typed,
    concern,
):
    if (
        is_custom
        and context.get("template")
        in {"manifest_node", "manifest_property", "manifest_relation"}
    ) or (not is_custom and typed_section):
        if context.get("template") not in {
            "manifest_node",
            "manifest_property",
            "manifest_relation",
        }:
            raise ValueError(
                f"{source}: typed manifest requires a typed Template"
            )
        _typed_manifest(sections, source, subject, context, typed)
        try:
            validate_continuant_variant(
                concern, context.get("template"), typed[-1][2]
            )
        except ValueError as error:
            raise ValueError(f"{source}: {error}") from error
        return True
    return False


def _implicit_manifest(
    is_custom, context, typed_section, source, subject, typed, concern
):
    if (
        not typed_section
        and not is_custom
        and context.get("lens") == CONTINUANT_LENS
        and context.get("template") == "manifest_node"
    ):
        typed.append(
            (
                source,
                subject,
                implicit_continuant_node(concern),
                "manifest_node",
            )
        )
        return True
    if (
        not is_custom
        and context.get("template")
        in {"manifest_node", "manifest_property", "manifest_relation"}
        and not typed_section
    ):
        raise ValueError(
            f"{source}: typed Template requires a Formal Manifest"
        )
    return False


def _collect_manifest_claims(
    body,
    is_custom,
    source,
    subject,
    context,
    subjects,
    records,
    typed,
    concern=None,
):
    sections = parse_content(body)
    typed_section = any(
        section["property_path"] == ["formal_manifest"] for section in sections
    )
    if _implicit_manifest(
        is_custom, context, typed_section, source, subject, typed, concern
    ):
        return
    if _collect_typed_manifest(
        is_custom,
        context,
        typed_section,
        source,
        sections,
        subject,
        typed,
        concern,
    ):
        return
    claims = (
        _custom_claims(body, source)
        if is_custom
        else [(subject, _native_claim(body, source, subject))]
    )
    _append_source_claims(source, claims, subjects, records)
