"""Compile a validated, fingerprinted snapshot of native Project Structure."""

import json
import os
from pathlib import Path
import re

from markdown_it import MarkdownIt

from FEATURE_FORMAL_MODEL_ENGINE.native_model_claim import parse_native_model_claim
from FEATURE_FORMAL_MODEL_ENGINE.scope_callback_asset import formal_claim
from FEATURE_MODEL.FEATURE_MODEL_VALIDATION.code_access import parse_code_access
from native_atom_reference import derive_atom_ref
from native_project_selection import _manifest_carriers, _manifest_inputs, manifest_state_fields
from VALIDATE_ATOMS.validate_atoms_workers.parsing import parse_carrier
from VALIDATE_ATOMS.validate_atoms_workers.read_io import ReadContext, open_regular
from VALIDATE_ATOMS.validate_atoms_workers.settings import CEILINGS

from .package_spec_sources import read_package_spec

_COMPONENT_DIR = re.compile(r'.+_(C[0-9]+)$')
_MANIFEST_FILE = re.compile(r'[A-Z]+-S-[0-9]+-SPEC-COMPONENT_MANIFEST--.+\.md$')
_PACKAGE_SPEC_FILE = re.compile(r'[A-Z]+-S-[0-9]+-SPEC-PKG--.+\.md$')


def _directories(reader, root):
    root = reader.allowed(root)
    fd = open_regular(root, directory=True)
    try:
        with os.scandir(fd) as entries:
            result = sorted(entry.name for entry in entries if _COMPONENT_DIR.fullmatch(entry.name))
    finally:
        os.close(fd)
    return result


def _fields(body):
    tokens = MarkdownIt('commonmark').parse(body)
    if any(token.type == 'heading_open' and tokens[i + 1].content.strip().casefold() == 'formal claim'
           for i, token in enumerate(tokens)):
        claim = parse_native_model_claim(formal_claim(body))
        args = claim['arguments'] if claim and claim['kind'] == 'entity' else {}
        instance = args.get('instance', {})
        if set(args) != {'entity_name', 'instance'} or args['entity_name'] != 'Component Manifest' or instance.get('type') != 'ComponentManifest':
            raise ValueError('Expected one formal ComponentManifest instance')
        return instance['fields']
    sections = {}
    in_claim = False
    for i, token in enumerate(tokens):
        if token.type != 'heading_open':
            continue
        title = tokens[i + 1].content.strip()
        level = int(token.tag[1:])
        if level == 2:
            in_claim = title == 'Claim'
        elif in_claim and level == 3:
            key = {'Component ID': 'component_id', 'Name': 'name', 'Layer': 'layer',
                   'Lens Whitelist': 'lens_whitelist'}.get(title)
            if key is None or key in sections:
                raise ValueError('Unknown or duplicate Component Manifest field')
            start = token.map[1]
            end = next((t.map[0] for t in tokens[i + 1:] if t.type == 'heading_open'), len(body.splitlines()))
            value = '\n'.join(body.splitlines()[start:end]).strip()
            sections[key] = json.loads(value) if key in {'layer', 'lens_whitelist'} else value
    if not {'component_id', 'name'} <= sections.keys():
        raise ValueError('Missing Component Manifest fields')
    return sections


def _component_inputs(path, carrier, parent, prefix):
    header = carrier.metadata
    context, state, identity = (header.get(name) for name in ("context", "state", "identity"))
    if not all(isinstance(group, dict) for group in (context, state, identity)):
        raise ValueError(f"Invalid Component Manifest header: {path}")
    if state.get("status") != "active":
        return None
    atom, version = identity.get("atom_id"), state.get("version")
    if (parent is None or context.get("template") != "component_manifest" or context.get("lens") != "SPEC"
            or type(context.get("tier")) is not int or context["tier"] != 0
            or context.get("container") != {"component": parent}
            or not isinstance(atom, str) or not re.fullmatch(rf"{re.escape(prefix)}-S-[0-9]+", atom)
            or not path.name.startswith(atom + "-") or type(version) is not int or version < 1):
        raise ValueError(f"Invalid Component Manifest identity or parent: {path}")
    fields = _fields(carrier.body)
    if fields.keys() - {"component_id", "name", "layer", "lens_whitelist", "boundaries"}:
        raise ValueError(f"Invalid Component Manifest fields: {path}")
    parse_code_access(fields.get("boundaries"))
    return {"atom_id": atom, "ref_id": derive_atom_ref(atom, version, state["status"]), "version": version, "tier": 0, **fields}


def _validation_fields(fields, carrier, model):
    return fields | manifest_state_fields(carrier) if model.requires_atom_state else fields


def compile_structure(selection, model) -> dict:  # noqa: C901
    """Compile the selected Project and its active Component Manifests."""
    control = Path(os.path.abspath(selection.control_root))
    reader = ReadContext(roots=[str(control)], limits=dict(CEILINGS))
    sources = _manifest_carriers(reader, control)
    selected = next(sources, None)
    if selected is None or next(sources, None) is not None:
        raise ValueError('Expected exactly one active Project Manifest')
    manifest_path, carrier = selected
    project_fields, project_parent = _manifest_inputs(manifest_path, carrier)
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
        for path in reader.inventory_shallow(root):
            if _PACKAGE_SPEC_FILE.fullmatch(path.name):
                carrier = parse_carrier(reader.read(path), path)
                fields = read_package_spec(path, carrier, parent, project_fields["prefix"])
                if fields is not None:
                    atom, package_id = fields["atom_id"], fields["package_id"]
                    if atom in atoms or package_id in packages:
                        raise ValueError(f"Duplicate Package or Atom ID: {path}")
                    model.validate_package_spec(_validation_fields(fields, carrier, model), parent)
                    atoms.add(atom)
                    packages[package_id] = {
                        "component": parent, "ref": fields["ref_id"], "fields": fields,
                        "sha256": reader.fingerprints[str(path)], "source_path": path.relative_to(control).as_posix(),
                    }
                continue
            if not _MANIFEST_FILE.fullmatch(path.name):
                continue
            carrier = parse_carrier(reader.read(path), path)
            fields = _component_inputs(path, carrier, parent, project_fields["prefix"])
            if fields is None:
                continue
            atom, cid = fields["atom_id"], fields.get("component_id")
            if not isinstance(cid, str) or not re.fullmatch(r'C[0-9]+', cid) or cid == 'C00' or cid in components or atom in atoms:
                raise ValueError(f'Duplicate or invalid Component or Atom ID: {path}')
            model.validate_component_manifest(_validation_fields(fields, carrier, model), parent)
            components[cid] = {'parent': parent, 'ref': fields['ref_id'], 'sha256': reader.fingerprints[str(path)], 'fields': fields, 'source_path': path.relative_to(control).as_posix()}
            atoms.add(atom)
            if cid in child_dirs:
                pending.append((child_dirs.pop(cid), cid))
        pending.extend((child, None) for child in child_dirs.values())
    if reader.currentness()['state'] != 'unchanged' or any(_directories(reader, root) != names for root, names in inventories.items()):
        raise ValueError('Structure sources changed during compilation')
    return {
        "model_sha256": model.fingerprint,
        "project": {"ref": project_fields["ref_id"], "sha256": manifest_sha256},
        "components": components,
        "packages": packages,
    }
