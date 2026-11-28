"""Compile a validated, fingerprinted snapshot of native Project Structure."""

import os
from pathlib import Path

from ...FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
    CEILINGS,
    ReadContext,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.settings.project.project__shared import (
    manifest_inputs,
    manifest_purpose,
    select_manifest_carriers,
)
from ...FEATURE_TOOLS.ADAPTERS_C30.structure.lens_scopes__pub import (
    compile_lens_groups,
    validate_lens_whitelist,
)
from ...FEATURE_TOOLS.ADAPTERS_C30.sources.inventory.source_row__pub import (
    json_value,
)
from .LAYER_2_PROJECT_STRUCTURE_C93__manifests import (
    _validation_fields,
)
from .LAYER_2_PROJECT_STRUCTURE_C93__walk import (
    _COMPONENT_DIR as _COMPONENT_DIR,
    _directories,
    _record_carrier as _record_carrier,
    _walk_structure,
)


def _select_project(selection, model, control, root, reader):
    sources = select_manifest_carriers(reader, root, control)
    selected = next(sources, None)
    if selected is None or next(sources, None) is not None:
        raise ValueError("Expected exactly one active Project Manifest")
    manifest_path, carrier = selected
    project_fields, project_parent = manifest_inputs(manifest_path, carrier)
    manifest_sha256 = reader.fingerprints[str(manifest_path)]
    if (
        manifest_path != Path(os.path.abspath(selection.manifest_path))
        or manifest_sha256 != selection.manifest_sha256
        or project_fields["ref_id"] != selection.manifest_ref
    ):
        raise ValueError("Selected Project Manifest pin changed")
    if project_parent != "C00":
        raise ValueError("Invalid Project Manifest parent")
    model.validate_manifest(
        _validation_fields(project_fields, carrier, model, "Project Manifest"),
        project_parent,
    )
    return project_fields, manifest_sha256, carrier


def compile_structure(selection, model) -> dict:
    """Compile the selected Project and its active Component Manifests."""
    control = Path(os.path.abspath(selection.control_root))
    root = control.parent
    reader = ReadContext(roots=[str(root)], limits=dict(CEILINGS))
    project_fields, manifest_sha256, carrier = _select_project(
        selection, model, control, root, reader
    )
    components = {}
    packages = {}
    atoms = {project_fields["atom_id"]}
    inventories = {}
    absent = set()
    directory_ids = set()
    pending = [(control, "C00")]
    _walk_structure(
        reader,
        pending,
        inventories,
        absent,
        directory_ids,
        project_fields,
        model,
        control,
        atoms,
        packages,
        components,
    )
    return _finish_structure(
        model,
        project_fields,
        manifest_sha256,
        components,
        packages,
        reader,
        inventories,
        absent,
        project_purpose=manifest_purpose(carrier.body),
    )


def _validate_lenses(project_fields, components):
    groups = compile_lens_groups(project_fields.get("parameters"))
    for component in components.values():
        try:
            validate_lens_whitelist(
                component["fields"].get("lens_whitelist"), groups
            )
        except ValueError as error:
            raise ValueError(f"{component['source_path']}: {error}") from error


def _finish_structure(
    model,
    project_fields,
    manifest_sha256,
    components,
    packages,
    reader=None,
    inventories=None,
    absent=None,
    *,
    project_purpose=None,
):
    _validate_lenses(project_fields, components)
    if reader is not None and (
        reader.currentness()["state"] != "unchanged"
        or any(
            _directories(reader, root) != names
            for root, names in inventories.items()
        )
        or any(path.exists() or path.is_symlink() for path in absent)
    ):
        raise ValueError("Structure sources changed during compilation")
    parameters = project_fields.get("parameters", {}).get("project", {})
    layout = (
        {"project": {"folder_layout": parameters["folder_layout"]}}
        if "folder_layout" in parameters
        else {}
    )
    return json_value(
        {
            "model_sha256": model.fingerprint,
            "project": {
                "ref": project_fields["ref_id"],
                "sha256": manifest_sha256,
                "parameters": layout,
                **({"purpose": project_purpose} if project_purpose else {}),
            },
            "components": components,
            "packages": packages,
        }
    )
