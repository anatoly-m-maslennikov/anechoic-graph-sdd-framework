"""Compile Project Structure from ingested Carrier rows."""

from collections import defaultdict
import os
from pathlib import Path
import re
from typing import Any

from pydantic import BaseModel, ConfigDict

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.\
    ADAPTERS_C30__shared import (  # fmt: skip
        manifest_inputs, manifest_purpose, native_header_view, spec_folder_layout,
    )
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.\
    atom_reference__pub import derive_atom_ref  # fmt: skip

from .LAYER_2_PROJECT_STRUCTURE_C93__shared import (
    _COMPONENT_DIR, _finish_structure, _record_carrier, _validation_fields,
)


class _Carrier(BaseModel):
    model_config = ConfigDict(frozen=True)

    metadata: dict[str, Any]
    body: str


class _Reader(BaseModel):
    fingerprints: dict[str, str]


def _row_inputs(project_root, control_root_name, rows):
    root = Path(os.path.abspath(project_root))
    if (
        not isinstance(control_root_name, str)
        or not control_root_name
        or Path(control_root_name).name != control_root_name
        or control_root_name in {".", ".."}
    ):
        raise ValueError("Invalid control root name")
    control = root / control_root_name
    carriers, fingerprints = {}, {}
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("Invalid structure row")
        source, digest = row.get("source_path"), row.get("sha256")
        if (
            not isinstance(source, str)
            or not source
            or "\\" in source
            or Path(source).is_absolute()
            or any(part in {"", ".", ".."} for part in source.split("/"))
            or not isinstance(digest, str)
            or not re.fullmatch(r"[0-9a-f]{64}", digest)
            or not isinstance(row.get("metadata"), dict)
            or not isinstance(row.get("body"), str)
        ):
            raise ValueError("Invalid structure row")
        path = root / source
        if path in carriers:
            raise ValueError('Duplicate structure source path')
        carrier = _Carrier.model_construct(metadata=row['metadata'],
                                           body=row['body'])
        header = native_header_view(carrier.metadata)
        identity, state = header.get('identity'), header.get('state')
        if (not isinstance(identity, dict) or not isinstance(state, dict)
                or row.get('exact_ref') != derive_atom_ref(
                    identity.get('atom_id'), state.get('version'), state.get('status'))):
            raise ValueError('Invalid structure row reference')
        carriers[path], fingerprints[str(path)] = carrier, digest
    return root, control, carriers, _Reader.model_construct(
        fingerprints=fingerprints,
    )


def _row_manifest(
    root, control, carriers, reader, manifest_sha256, manifest_path, model
):
    if not isinstance(manifest_sha256, str) or not re.fullmatch(
        r"[0-9a-f]{64}", manifest_sha256
    ):
        raise ValueError("Invalid Project Manifest pin")
    root_candidates = any(
        path.parent == root and "-PROJECT_MANIFEST--" in path.name
        for path in carriers
    )
    candidates = []
    for path, carrier in carriers.items():
        header = native_header_view(carrier.metadata)
        context, state = header.get("context"), header.get("state")
        if (
            isinstance(context, dict)
            and context.get("template") == "project_manifest"
            and isinstance(state, dict)
            and state.get("status") == "active"
        ):
            if path.parent not in {root, control} or (
                path.parent == root and "-PROJECT_MANIFEST--" not in path.name
            ):
                raise ValueError("Invalid Project Manifest location")
            candidates.append((path, carrier))
    if len(candidates) != 1:
        raise ValueError('Expected exactly one active Project Manifest')
    path, carrier = candidates[0]
    if (
        path.parent != (root if root_candidates else control)
        or (
            manifest_path is not None
            and path.relative_to(root).as_posix() != manifest_path
        )
        or reader.fingerprints[str(path)] != manifest_sha256
    ):
        raise ValueError("Selected Project Manifest pin changed")
    fields, parent = manifest_inputs(path, carrier)
    if parent != "C00":
        raise ValueError("Invalid Project Manifest parent")
    model.validate_manifest(
        _validation_fields(fields, carrier, model, "Project Manifest"), parent
    )
    return fields, manifest_purpose(carrier.body)


def _inventory(control, carriers):
    members = defaultdict(list)
    directories = {control}
    for path in sorted(carriers):
        if path.is_relative_to(control):
            members[path.parent].append(path)
            directories.update(
                parent
                for parent in path.parents
                if parent.is_relative_to(control)
            )
    children = defaultdict(list)
    for directory in sorted(directories):
        if match := _COMPONENT_DIR.fullmatch(directory.name):
            children[directory.parent].append((match.group(1), directory))
    return members, children


def _walk_rows(control, carriers, reader, project_fields, model):
    tier_one = spec_folder_layout(project_fields.get("parameters"))["1"]
    template = getattr(model, "fixed_property_value", lambda *_: None)(
        "Component Manifest", "template"
    )
    if template is None:
        template = 'component_manifest'
    if not isinstance(template, str) or not template or template == 'component_seed_manifest':
        raise ValueError('Invalid Component Manifest Template in Model')
    templates = {'component_manifest': template, 'component_seed_manifest': 'component_seed_manifest'}
    members, children = _inventory(control, carriers)
    atoms, packages, components, directory_ids = {project_fields['atom_id']}, {}, {}, set()
    pending = [(control, 'C00')]
    while pending:
        root, parent = pending.pop()
        child_dirs = {}
        for cid, directory in children[root]:
            if cid in directory_ids:
                raise ValueError(f'Duplicate Component directory {cid}')
            directory_ids.add(cid)
            child_dirs[cid] = directory
        for directory, allowed in (
            (root, templates),
            (root / "_SPEC", templates),
            (root / tier_one, {"component_manifest": template}),
        ):
            for path in members[directory]:
                _record_carrier(
                    path,
                    reader,
                    None,
                    parent,
                    project_fields,
                    model,
                    control,
                    atoms,
                    packages,
                    components,
                    pending,
                    child_dirs,
                    allowed,
                    carriers[path],
                )
        pending.extend((child, None) for child in child_dirs.values())
    return components, packages


class StructureAdmissionError(Exception):
    """A failed captured carrier belongs to the admitted Structure."""


def compile_structure_rows(
    project_root,
    control_root_name,
    manifest_sha256,
    model,
    rows,
    *,
    manifest_path=None,
    alias_issues=(),
) -> dict:
    """Compile Structure from already-ingested, fingerprinted Carrier rows."""
    root, control, carriers, reader = _row_inputs(
        project_root, control_root_name, rows
    )
    fields, purpose = _row_manifest(
        root, control, carriers, reader, manifest_sha256, manifest_path, model
    )
    template = getattr(model, "fixed_property_value", lambda *_: None)(
        "Component Manifest", "template"
    )
    template = "component_manifest" if template is None else template
    for issue in alias_issues:
        if issue["template"] in {template, "component_seed_manifest"}:
            raise StructureAdmissionError(
                "Structure source ingestion failed: " + issue["relative_path"]
            )
    components, packages = _walk_rows(control, carriers, reader, fields, model)
    return _finish_structure(
        model, fields, manifest_sha256, components, packages,
        project_purpose=purpose,
    )
