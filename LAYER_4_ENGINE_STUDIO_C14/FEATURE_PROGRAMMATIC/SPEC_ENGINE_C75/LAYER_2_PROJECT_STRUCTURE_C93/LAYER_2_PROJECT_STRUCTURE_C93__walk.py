"""Walk Component directories and collect their Structure records."""

import os
import re

from ...FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
    open_regular,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.header.header__shared import (
    spec_folder_layout,
)
from .LAYER_2_PROJECT_STRUCTURE_C93__manifests import (
    _component_inputs,
    _record_seed,
    _structure_carrier,
    _validation_fields,
)

_COMPONENT_DIR = re.compile(r"(?!__).+_(C[0-9]+)$")


def _directories(reader, root):
    root = reader.allowed(root)
    fd = open_regular(root, directory=True)
    try:
        with os.scandir(fd) as entries:
            result = sorted(
                entry.name
                for entry in entries
                if _COMPONENT_DIR.fullmatch(entry.name)
            )
    finally:
        os.close(fd)
    return result


def _record_carrier(
    path,
    reader,
    directory_fd,
    parent,
    project_fields,
    model,
    control,
    atoms,
    packages,
    components,
    pending,
    child_dirs,
    templates,
    supplied=None,
):
    if not re.match(r"[A-Z]+-S-", path.name):
        return
    carrier, template = _structure_carrier(
        path, reader, directory_fd, templates, supplied
    )
    if template not in templates.values():
        return
    if template == "component_seed_manifest":
        _record_seed(
            path,
            carrier,
            parent,
            project_fields["prefix"],
            model,
            control,
            atoms,
            packages,
            reader.fingerprints[str(path)],
        )
        return
    if template != templates.get("component_manifest"):
        return
    context = (path, reader, parent, project_fields, model, control)
    context += (atoms, components, pending, child_dirs)
    _record_component(context, carrier)


def _record_component(context, carrier):
    (
        path,
        reader,
        parent,
        project_fields,
        model,
        control,
        atoms,
        components,
        pending,
        child_dirs,
    ) = context
    inputs = _component_inputs(path, carrier, parent, project_fields["prefix"])
    if inputs is None:
        return
    fields, purpose = inputs
    atom, cid = fields["atom_id"], fields.get("component_id")
    if (
        not isinstance(cid, str)
        or not re.fullmatch(r"C[0-9]+", cid)
        or cid == "C00"
        or cid in components
        or atom in atoms
    ):
        raise ValueError(f"Duplicate or invalid Component or Atom ID: {path}")
    model.validate_component_manifest(
        _validation_fields(fields, carrier, model, "Component Manifest"),
        parent,
    )
    components[cid] = {
        "parent": parent,
        "ref": fields["ref_id"],
        "sha256": reader.fingerprints[str(path)],
        "fields": fields,
        "source_path": path.relative_to(control).as_posix(),
    }
    if purpose is not None:
        components[cid]["purpose"] = purpose
    atoms.add(atom)
    if cid in child_dirs:
        pending.append((child_dirs.pop(cid), cid))


def _walk_structure(
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
):
    tier_one = spec_folder_layout(project_fields.get("parameters"))["1"]
    component_template = getattr(
        model, "fixed_property_value", lambda *_: None
    )("Component Manifest", "template")
    if component_template is None:
        component_template = "component_manifest"
    if (
        not isinstance(component_template, str)
        or not component_template
        or component_template == "component_seed_manifest"
    ):
        raise ValueError("Invalid Component Manifest Template in Model")
    templates = {
        "component_manifest": component_template,
        "component_seed_manifest": "component_seed_manifest",
    }
    context = (reader, pending, inventories, absent, directory_ids)
    context += (project_fields, model, control, atoms, packages, components)
    while pending:
        _visit_structure(context, templates, tier_one, component_template)


def _visit_structure(context, templates, tier_one, component_template):
    reader, pending, inventories, _, directory_ids, *_ = context
    root, parent = pending.pop()
    directories = _directories(reader, root)
    inventories[root] = directories
    child_dirs = {}
    for name in directories:
        cid = _COMPONENT_DIR.fullmatch(name).group(1)
        if cid in directory_ids:
            raise ValueError(f"Duplicate Component directory {cid}")
        directory_ids.add(cid)
        child_dirs[cid] = root / name
    for directory, allowed in (
        (root, templates),
        (root / "_SPEC", templates),
        (root / tier_one, {"component_manifest": component_template}),
    ):
        _visit_directory(directory, allowed, context, parent, child_dirs)
    pending.extend((child, None) for child in child_dirs.values())


def _visit_directory(directory, allowed, context, parent, child_dirs):
    (
        reader,
        pending,
        _,
        absent,
        _,
        project_fields,
        model,
        control,
        atoms,
        packages,
        components,
    ) = context
    if directory.exists() or directory.is_symlink():
        paths = reader.inventory_shallow(directory)
        descriptor = open_regular(reader.allowed(directory), directory=True)
        try:
            for path in paths:
                _record_carrier(
                    path,
                    reader,
                    descriptor,
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
                )
        finally:
            os.close(descriptor)
    else:
        absent.add(directory)
