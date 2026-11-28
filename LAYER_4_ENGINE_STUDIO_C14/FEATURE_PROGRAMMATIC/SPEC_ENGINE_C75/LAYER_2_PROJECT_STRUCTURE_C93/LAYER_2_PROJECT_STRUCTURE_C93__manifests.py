"""Read and validate Component and Seed Manifests for Structure compilation."""

import re

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.content.content__shared import (
    CarrierError,
)
from ...FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
    LimitReached,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.settings.project.project__shared import (
    manifest_state_fields,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.header.header__shared import (
    native_header_view,
)
from ...FEATURE_TOOLS.ADAPTERS_C30.carriers.content.atom_reference__pub import (
    COMPONENT_MANIFEST_FILENAME,
    derive_atom_ref,
)
from ...FEATURE_TOOLS.ADAPTERS_C30.carriers.content.carrier_read__pub import (
    parse_carrier,
)
from ...FEATURE_TOOLS.ADAPTERS_C30.structure.code_access_rules__pub import (
    parse_code_access,
)
from ...FEATURE_TOOLS.ADAPTERS_C30.structure.components.component_manifest__pub import (
    parse_component_manifest,
)
from ...FEATURE_TOOLS.ADAPTERS_C30.structure.components.component_seed_manifest__pub import (
    read_component_seed_manifest,
)
from ...FEATURE_TOOLS.ADAPTERS_C30.settings.project.project_manifest__pub import (
    manifest_summary_fields,
)

_COMPONENT_FIELDS = {
    "component_id",
    "name",
    "layer",
    "lens_whitelist",
    "boundaries",
}


def _component_inputs(path, carrier, parent, prefix):
    header = native_header_view(carrier.metadata)
    context, state, identity = (
        header.get(name) for name in ("context", "state", "identity")
    )
    if not all(
        isinstance(group, dict) for group in (context, state, identity)
    ):
        raise ValueError(f"Invalid Component Manifest header: {path}")
    if state.get("status") != "active":
        return None
    atom, version = identity.get("atom_id"), state.get("version")
    if (
        parent is None
        or context.get("lens") != "SPEC"
        or type(context.get("tier")) is not int
        or context["tier"] not in {1, 4}
        or context.get("container") != {"component": parent}
        or not isinstance(atom, str)
        or not re.fullmatch(rf"{re.escape(prefix)}-S-[0-9]+", atom)
        or (
            "atom_family" not in carrier.metadata
            and not path.name.startswith(atom + "-")
        )
        or type(version) is not int
        or version < 1
    ):
        raise ValueError(
            f"Invalid Component Manifest identity or parent: {path}"
        )
    fields, purpose = parse_component_manifest(
        carrier.body, tier=context["tier"]
    )
    if fields.keys() - _COMPONENT_FIELDS:
        raise ValueError(f"Invalid Component Manifest fields: {path}")
    parse_code_access(fields.get("boundaries"))
    return {
        "atom_id": atom,
        "ref_id": derive_atom_ref(atom, version, state["status"]),
        "version": version,
        "tier": context["tier"],
        **fields,
    }, purpose


def _validation_fields(fields, carrier, model, name):
    if model.requires_atom_state:
        fields = fields | manifest_state_fields(
            carrier, include_header=model.requires_atom_header
        )
    if (
        name == "Component Manifest"
        and "template" not in fields
        and getattr(model, "declares_property", lambda *_: False)(
            name, "template"
        )
    ):
        fields = fields | {
            "template": native_header_view(carrier.metadata)["context"].get(
                "template"
            )
        }
    if getattr(model, "declares_summary", lambda _name: False)(name):
        fields = fields | manifest_summary_fields(
            carrier, use_title=name == "Component Seed Manifest"
        )
    return fields


def _structure_carrier(path, reader, directory_fd, templates, supplied=None):
    match = COMPONENT_MANIFEST_FILENAME.fullmatch(path.name)
    if match and match[1].lower() not in templates:
        return None, None
    carrier = supplied
    if carrier is None:
        try:
            carrier = parse_carrier(
                reader.read(path, directory_fd=directory_fd), path
            )
        except (CarrierError, LimitReached, OSError) as error:
            if (
                match
                or isinstance(error, LimitReached)
                and error.limit != "max_file_bytes"
            ):
                raise
            return None, None
    if "atom_family" not in carrier.metadata:
        return carrier, templates[match[1].lower()] if match else None
    context = carrier.metadata.get("context")
    template = context.get("template") if isinstance(context, dict) else None
    if match or isinstance(template, str) and template in templates.values():
        return carrier, native_header_view(carrier.metadata)["context"].get(
            "template"
        )
    return None, None


def _record_seed(
    path, carrier, parent, prefix, model, control, atoms, packages, digest
):
    fields = read_component_seed_manifest(path, carrier, parent, prefix)
    if fields is None:
        return
    atom, package_id = fields["atom_id"], fields["component_seed_id"]
    if atom in atoms or package_id in packages:
        raise ValueError(f"Duplicate Component Seed or Atom ID: {path}")
    model.validate_component_seed_manifest(
        _validation_fields(fields, carrier, model, "Component Seed Manifest"),
        parent,
    )
    atoms.add(atom)
    packages[package_id] = {
        "component": parent,
        "ref": fields["ref_id"],
        "fields": fields,
        "sha256": digest,
        "source_path": path.relative_to(control).as_posix(),
    }
