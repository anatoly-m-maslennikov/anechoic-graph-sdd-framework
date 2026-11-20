"""Select a validated legacy or native Project for normal runtime startup."""

from __future__ import annotations

import json
import os
from pathlib import Path
import re

from native_project_selection import manifest_paths, resolve_native_project
from project_selection import (
    SETTINGS_FILENAME, ProjectSelectionError, _control_candidates, _control_relative,
    _project_root, _read_toml, resolve_project,
)
from VALIDATE_ATOMS.validate_atoms_workers.parsing import parse_carrier
from VALIDATE_ATOMS.validate_atoms_workers.read_io import ReadContext, open_regular
from VALIDATE_ATOMS.validate_atoms_workers.settings import CEILINGS


_RESERVED = {".anechoic_new", ".anechoic_legacy", ".anechoic_legacy_archive",
             ".anechoic_runtime", ".anechoic_tmp"}


def _has_manifest(reader: ReadContext, control: Path) -> bool:
    for path in manifest_paths(reader, control):
        carrier = parse_carrier(reader.read(path), path)
        context = carrier.metadata.get("context")
        if (isinstance(context, dict) and context.get("template") == "project_manifest"):
            return True
        if "PROJECT_MANIFEST" in path.name:
            return True
    return False


def select_runtime_project(project_root, control_root=None, *, validate_manifest=None):
    """Return exactly one selected Project, using the reviewed native Model when needed."""
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
            relative = _control_relative(control_root)
            if _has_manifest(reader, root / relative):
                selected = native(relative)
                if os.path.lexists(root / relative / SETTINGS_FILENAME):
                    try:
                        resolve_project(root, relative)
                    except ProjectSelectionError:
                        pass
                    else:
                        raise ProjectSelectionError("Project control root is ambiguous")
                return finish(selected)
            if os.path.lexists(root / relative / SETTINGS_FILENAME):
                return finish(resolve_project(root, relative))
            return finish(native(relative))

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
        legacy = []
        stale = []
        legacy_roots = _control_candidates(root)
        for relative in legacy_roots:
            try:
                legacy.append(resolve_project(root, relative))
            except ProjectSelectionError as error:
                if (relative != Path(".anechoic_legacy")
                        or str(error) != "Project Settings control_root contradicts the selection"):
                    raise
                settings = _read_toml(reader, root / relative / SETTINGS_FILENAME)
                stale.append(settings.get("paths", {}).get("control_root"))
        if stale and (len(natives) != 1 or stale != [natives[0].control_relative.as_posix()]):
            raise ProjectSelectionError("Retained Project Settings do not match the selected native control")
        selections = legacy + natives
        if len(selections) != 1:
            raise ProjectSelectionError("Project control root is missing or ambiguous")
        selected = finish(selections[0])
        if control_roots() != controls or _control_candidates(root) != legacy_roots:
            raise ProjectSelectionError("Project control candidates changed during selection")
        return selected
    except ProjectSelectionError:
        raise
    except (OSError, RuntimeError, TypeError, ValueError, AttributeError) as error:
        raise ProjectSelectionError("Project discovery is unavailable, invalid, or unsafe") from error


def load_native_inputs(selection, *, model=None):
    """Bind the reviewed Model and the migration's existing alias-map format."""
    from FEATURE_MODEL.FEATURE_FORMAL_MODEL_GENERATOR.native_manifest_model import load_native_model
    from native_query import NativeQueryInputs

    if model is None:
        model = load_native_model()
    alias_path = selection.control_root / "_migration" / "native-aliases.json"
    aliases = ()
    if os.path.lexists(alias_path):
        reader = ReadContext(roots=[str(selection.root)], limits=dict(CEILINGS))
        try:
            rows = json.loads(reader.read(alias_path))
            if not isinstance(rows, list) or any(
                not isinstance(row, list) or len(row) != 3
                or row[0] is not None and not isinstance(row[0], str)
                or not isinstance(row[1], str) or not isinstance(row[2], str)
                for row in rows
            ):
                raise ValueError("Expected legacy reference, original path, and native exact reference rows")
            if reader.currentness()["state"] != "unchanged":
                raise ValueError("Native alias map changed during startup")
        except (OSError, RuntimeError, ValueError) as error:
            raise ProjectSelectionError("Native alias map is unavailable, invalid, or unsafe") from error
        aliases = tuple(map(tuple, rows))
    elif os.path.lexists(selection.root / ".anechoic_legacy"):
        raise ProjectSelectionError("The migrated Project requires its verified native alias map")
    return NativeQueryInputs(model.validate_manifest, model.relation_types, model.inverses, aliases)
