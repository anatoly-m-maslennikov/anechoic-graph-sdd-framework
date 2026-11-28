"""Discover native Project control and Manifest candidates."""

from __future__ import annotations

from . import native_project_selection as runtime


def _has_manifest(reader: runtime.ReadContext, control: runtime.Path) -> bool:
    for path, carrier in runtime.manifest_sources(reader, control):
        context = runtime.native_header_view(carrier.metadata).get("context")
        if (
            isinstance(context, dict)
            and context.get("template") == "project_manifest"
        ):
            return True
        if (
            "atom_family" not in carrier.metadata
            and "PROJECT_MANIFEST" in path.name
        ):
            return True
    return False


def _control_roots(root, reader):
    descriptor = runtime.open_regular(root, directory=True)
    try:
        with runtime.os.scandir(descriptor) as entries:
            controls = []
            for entry in entries:
                reader.checkpoint()
                if (
                    not runtime.is_native_control_name(entry.name)
                    or entry.name in runtime._RESERVED
                ):
                    continue
                if entry.is_symlink():
                    raise runtime.ProjectSelectionError(
                        "Project control candidates must not be symlinks"
                    )
                if entry.is_dir(follow_symlinks=False):
                    controls.append(runtime.Path(entry.name))
                    if len(controls) > 64:
                        raise runtime.ProjectSelectionError(
                            "Project control candidates exceed "
                            "the host ceiling"
                        )
        return sorted(controls)
    finally:
        runtime.os.close(descriptor)


def _root_manifest_matches(reader, root, controls):
    sources = runtime.active_manifest_carriers(
        reader, root, root_candidates=True
    )
    candidate = next(sources, None)
    if candidate is None or next(sources, None) is not None:
        raise runtime.ProjectSelectionError(
            "A unique native Project Manifest is required"
        )
    fields, _ = runtime.manifest_inputs(*candidate)
    name = fields["name"].casefold()
    parameters = fields.get("parameters", {})
    project = (
        parameters.get("project") if isinstance(parameters, dict) else None
    )
    root_settings = project.get("root") if isinstance(project, dict) else None
    markers = [".", "_"]
    if isinstance(root_settings, dict) and "prefix" in root_settings:
        marker = {"dot": ".", "underscore": "_"}.get(root_settings["prefix"])
        if marker is None:
            raise runtime.ProjectSelectionError(
                "Project Manifest root prefix contradicts the selection"
            )
        markers = [marker]
    return [
        relative
        for relative in controls
        if relative.name in {f"{marker}anechoic_{name}" for marker in markers}
    ]


def _validate_manifest_paths(fields, parameters, relative, manifest):
    for values in (fields.get("parameters", {}), parameters):
        project = values.get("project") if isinstance(values, dict) else None
        project_root = (
            project.get("root") if isinstance(project, dict) else None
        )
        if isinstance(project_root, dict) and "prefix" in project_root:
            marker = {"dot": ".", "underscore": "_"}.get(
                project_root["prefix"]
            )
            if (
                marker is None
                or relative.name
                != f"{marker}anechoic_{manifest.name.casefold()}"
            ):
                raise runtime.ProjectSelectionError(
                    "Project Manifest root prefix contradicts the selection"
                )
        paths = values.get("paths") if isinstance(values, dict) else None
        if (
            isinstance(paths, dict)
            and "control_root" in paths
            and paths["control_root"] != relative.as_posix()
        ):
            raise runtime.ProjectSelectionError(
                "Project Manifest control_root contradicts the selection"
            )
