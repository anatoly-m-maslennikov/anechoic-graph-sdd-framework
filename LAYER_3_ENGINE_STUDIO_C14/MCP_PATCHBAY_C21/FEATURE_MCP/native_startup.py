"""Select a validated native Project for runtime startup."""

from __future__ import annotations

import os
from pathlib import Path

from native_carrier_header import native_header_view
from native_project_selection import manifest_sources, resolve_native_project
from project_selection import ProjectSelectionError, _control_relative, _project_root
from VALIDATE_ATOMS.validate_atoms_workers.read_io import ReadContext, open_regular
from VALIDATE_ATOMS.validate_atoms_workers.settings import CEILINGS


_RESERVED = {".anechoic_new", ".anechoic_legacy", ".anechoic_legacy_archive",
             ".anechoic_runtime", ".anechoic_tmp"}


def _has_manifest(reader: ReadContext, control: Path) -> bool:
    for path, carrier in manifest_sources(reader, control):
        context = native_header_view(carrier.metadata).get("context")
        if (isinstance(context, dict) and context.get("template") == "project_manifest"):
            return True
        if "atom_family" not in carrier.metadata and "PROJECT_MANIFEST" in path.name:
            return True
    return False


def select_runtime_project(project_root, control_root=None, *, validate_manifest=None):
    """Return one native Project with an active Project Manifest."""
    root = _project_root(project_root)
    reader = ReadContext(roots=[str(root)], limits=dict(CEILINGS))

    def native(relative):
        nonlocal validate_manifest
        if validate_manifest is None:
            from FEATURE_MODEL.FEATURE_FORMAL_MODEL_GENERATOR.native_manifest_model import load_native_model
            validate_manifest = load_native_model().validate_manifest
        return resolve_native_project(root, relative, validate_manifest=validate_manifest)

    def finish(selection):
        if reader.currentness()["state"] != "unchanged":
            raise ProjectSelectionError("Project carriers changed during selection")
        return selection

    try:
        if control_root is not None:
            return finish(native(_control_relative(control_root)))

        def control_roots():
            descriptor = open_regular(root, directory=True)
            try:
                with os.scandir(descriptor) as entries:
                    controls = []
                    for entry in entries:
                        reader.checkpoint()
                        if entry.name.startswith(".anechoic_") and entry.name not in _RESERVED:
                            if entry.is_symlink():
                                raise ProjectSelectionError("Project control candidates must not be symlinks")
                            if entry.is_dir(follow_symlinks=False):
                                controls.append(_control_relative(entry.name))
                                if len(controls) > 64:
                                    raise ProjectSelectionError("Project control candidates exceed the host ceiling")
                return sorted(controls)
            finally:
                os.close(descriptor)

        controls = control_roots()
        natives = [native(relative) for relative in controls if _has_manifest(reader, root / relative)]
        if len(natives) != 1:
            raise ProjectSelectionError("A unique native Project Manifest is required")
        selected = finish(natives[0])
        if control_roots() != controls:
            raise ProjectSelectionError("Project control candidates changed during selection")
        return selected
    except ProjectSelectionError:
        raise
    except (OSError, RuntimeError, TypeError, ValueError, AttributeError) as error:
        raise ProjectSelectionError("Project discovery is unavailable, invalid, or unsafe") from error


def load_native_inputs(selection, *, model=None):
    """Bind the reviewed native Model."""
    from FEATURE_MODEL.FEATURE_FORMAL_MODEL_GENERATOR.native_manifest_model import load_native_model
    from native_query import NativeQueryInputs

    if model is None:
        model = load_native_model()
    return NativeQueryInputs(model.validate_manifest, model.relation_types, model.inverses,
                             require_atom_state=model.requires_atom_state,
                             require_atom_header=model.requires_atom_header,
                             ticket_labels=model.ticket_labels)
