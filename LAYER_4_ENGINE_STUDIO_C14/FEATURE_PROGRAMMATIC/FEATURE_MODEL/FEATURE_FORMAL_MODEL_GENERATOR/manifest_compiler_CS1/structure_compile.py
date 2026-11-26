"""Compile a validated, fingerprinted snapshot of native Project Structure."""

import os
from pathlib import Path
import re

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.component_manifest__pub import parse_component_manifest_fields as _fields
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.code_access_rules__pub import parse_code_access
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.lens_scopes__pub import compile_lens_groups, validate_lens_whitelist
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.atom_reference__pub import derive_atom_ref
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import native_header_view
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import select_manifest_carriers, manifest_inputs, manifest_state_fields
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carrier_read__pub import parse_carrier
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.project_manifest__pub import manifest_summary_fields
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
    CEILINGS, CarrierError, LimitReached, ReadContext, open_regular,
)

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.component_seed_manifest__pub import read_component_seed_manifest

_COMPONENT_DIR = re.compile(r'(?!__).+_(C[0-9]+)$')
_MANIFEST_FILE = re.compile(r'[A-Z]+-S-[0-9]+-SPEC-(COMPONENT(?:_SEED)?_MANIFEST)--.+\.md$')
_MANIFEST_TEMPLATES = {"component_manifest", "component_seed_manifest"}


def _directories(reader, root):
    root = reader.allowed(root)
    fd = open_regular(root, directory=True)
    try:
        with os.scandir(fd) as entries:
            result = sorted(entry.name for entry in entries if _COMPONENT_DIR.fullmatch(entry.name))
    finally:
        os.close(fd)
    return result


def _component_inputs(path, carrier, parent, prefix):
    header = native_header_view(carrier.metadata)
    context, state, identity = (header.get(name) for name in ("context", "state", "identity"))
    if not all(isinstance(group, dict) for group in (context, state, identity)):
        raise ValueError(f"Invalid Component Manifest header: {path}")
    if state.get("status") != "active":
        return None
    atom, version = identity.get("atom_id"), state.get("version")
    if (parent is None or context.get("template") != "component_manifest" or context.get("lens") != "SPEC"
            or type(context.get("tier")) is not int or context["tier"] != 4
            or context.get("container") != {"component": parent}
            or not isinstance(atom, str) or not re.fullmatch(rf"{re.escape(prefix)}-S-[0-9]+", atom)
            or ("atom_family" not in carrier.metadata and not path.name.startswith(atom + "-")) or type(version) is not int or version < 1):
        raise ValueError(f"Invalid Component Manifest identity or parent: {path}")
    fields = _fields(carrier.body)
    if fields.keys() - {"component_id", "name", "layer", "lens_whitelist", "boundaries"}:
        raise ValueError(f"Invalid Component Manifest fields: {path}")
    parse_code_access(fields.get("boundaries"))
    return {"atom_id": atom, "ref_id": derive_atom_ref(atom, version, state["status"]), "version": version, "tier": context["tier"], **fields}


def _validation_fields(fields, carrier, model, name):
    if model.requires_atom_state:
        fields = fields | manifest_state_fields(carrier, include_header=model.requires_atom_header)
    if getattr(model, "declares_summary", lambda _name: False)(name):
        fields = fields | manifest_summary_fields(carrier, use_title=name == "Component Seed Manifest")
    return fields


def _structure_carrier(path, reader, directory_fd):
    match = _MANIFEST_FILE.fullmatch(path.name)
    try:
        carrier = parse_carrier(reader.read(path, directory_fd=directory_fd), path)
    except (CarrierError, LimitReached, OSError) as error:
        if match or isinstance(error, LimitReached) and error.limit != "max_file_bytes":
            raise
        return None, None
    if "atom_family" not in carrier.metadata:
        return carrier, match[1].lower() if match else None
    context = carrier.metadata.get("context")
    template = context.get("template") if isinstance(context, dict) else None
    if match or isinstance(template, str) and template in _MANIFEST_TEMPLATES:
        return carrier, native_header_view(carrier.metadata)["context"].get("template")
    return None, None


def _record_carrier(path, reader, directory_fd, parent, project_fields, model, control, atoms, packages, components, pending, child_dirs):
    if not re.match(r'[A-Z]+-S-', path.name):
        return
    carrier, template = _structure_carrier(path, reader, directory_fd)
    if template == 'component_seed_manifest':
        fields = read_component_seed_manifest(path, carrier, parent, project_fields["prefix"])
        if fields is not None:
            atom, package_id = fields["atom_id"], fields["component_seed_id"]
            if atom in atoms or package_id in packages:
                raise ValueError(f"Duplicate Component Seed or Atom ID: {path}")
            model.validate_component_seed_manifest(_validation_fields(fields, carrier, model, "Component Seed Manifest"), parent)
            atoms.add(atom)
            packages[package_id] = {
                "component": parent, "ref": fields["ref_id"], "fields": fields,
                "sha256": reader.fingerprints[str(path)], "source_path": path.relative_to(control).as_posix(),
            }
        return
    if template != 'component_manifest':
        return
    fields = _component_inputs(path, carrier, parent, project_fields["prefix"])
    if fields is None:
        return
    atom, cid = fields["atom_id"], fields.get("component_id")
    if not isinstance(cid, str) or not re.fullmatch(r'C[0-9]+', cid) or cid == 'C00' or cid in components or atom in atoms:
        raise ValueError(f'Duplicate or invalid Component or Atom ID: {path}')
    model.validate_component_manifest(_validation_fields(fields, carrier, model, "Component Manifest"), parent)
    components[cid] = {'parent': parent, 'ref': fields['ref_id'], 'sha256': reader.fingerprints[str(path)], 'fields': fields, 'source_path': path.relative_to(control).as_posix()}
    atoms.add(atom)
    if cid in child_dirs:
        pending.append((child_dirs.pop(cid), cid))


def _walk_structure(reader, pending, inventories, directory_ids, project_fields, model, control, atoms, packages, components):
    while pending:
        root, parent = pending.pop()
        directories = _directories(reader, root)
        inventories[root] = directories
        child_dirs = {}
        for name in directories:
            cid = _COMPONENT_DIR.fullmatch(name).group(1)
            if cid in directory_ids:
                raise ValueError(f'Duplicate Component directory {cid}')
            directory_ids.add(cid)
            child_dirs[cid] = root / name
        for directory in (root, root / '_SPEC'):
            if directory.exists() or directory.is_symlink():
                paths = reader.inventory_shallow(directory)
                descriptor = open_regular(reader.allowed(directory), directory=True)
                try:
                    for path in paths:
                        _record_carrier(path, reader, descriptor, parent, project_fields, model, control, atoms, packages, components, pending, child_dirs)
                finally:
                    os.close(descriptor)
        pending.extend((child, None) for child in child_dirs.values())


def compile_structure(selection, model) -> dict:  # noqa: C901
    """Compile the selected Project and its active Component Manifests."""
    control = Path(os.path.abspath(selection.control_root))
    root = control.parent
    reader = ReadContext(roots=[str(root)], limits=dict(CEILINGS))
    sources = select_manifest_carriers(reader, root, control)
    selected = next(sources, None)
    if selected is None or next(sources, None) is not None:
        raise ValueError('Expected exactly one active Project Manifest')
    manifest_path, carrier = selected
    project_fields, project_parent = manifest_inputs(manifest_path, carrier)
    manifest_sha256 = reader.fingerprints[str(manifest_path)]
    if (manifest_path != Path(os.path.abspath(selection.manifest_path))
            or manifest_sha256 != selection.manifest_sha256
            or project_fields['ref_id'] != selection.manifest_ref):
        raise ValueError('Selected Project Manifest pin changed')
    if project_parent != 'C00':
        raise ValueError('Invalid Project Manifest parent')
    components = {}
    packages = {}
    atoms = {project_fields['atom_id']}
    inventories = {}
    directory_ids = set()
    pending = [(control, 'C00')]
    _walk_structure(reader, pending, inventories, directory_ids, project_fields, model, control, atoms, packages, components)
    groups = compile_lens_groups(project_fields.get('parameters'))
    for component in components.values():
        try:
            validate_lens_whitelist(component['fields'].get('lens_whitelist'), groups)
        except ValueError as error:
            raise ValueError(f"{component['source_path']}: {error}") from error
    if reader.currentness()['state'] != 'unchanged' or any(_directories(reader, root) != names for root, names in inventories.items()):
        raise ValueError('Structure sources changed during compilation')
    parameters = project_fields.get("parameters", {}).get("project", {})
    layout = {"project": {"folder_layout": parameters["folder_layout"]}} if "folder_layout" in parameters else {}
    return {
        "model_sha256": model.fingerprint,
        "project": {"ref": project_fields["ref_id"], "sha256": manifest_sha256, "parameters": layout},
        "components": components,
        "packages": packages,
    }
