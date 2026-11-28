"""Bind an explicitly selected native Project to its one Active Manifest."""

from __future__ import annotations

from collections.abc import Callable
from copy import deepcopy
from dataclasses import field, replace
import os
from pathlib import Path
import re
from typing import Protocol

from pydantic import ConfigDict
from pydantic.dataclasses import dataclass

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.header.header__shared import (
    native_header_view as native_header_view,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.header.header__shared import (
    spec_folder_layout,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.settings.project.project__shared import (
    ProjectSelectionError,
    active_manifest_carriers as active_manifest_carriers,
    select_manifest_carriers,
    manifest_inputs,
    manifest_sources as manifest_sources,
    manifest_state_fields,
)
from ...ADAPTERS_C30.settings.project.project_manifest__pub import (
    manifest_summary_fields,
)
from ._native_discovery_paths import (
    _validate_manifest_paths,
    _control_roots,
    _has_manifest,
    _root_manifest_matches,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.\
    PROJECT_SUPPORT.PROJECT_SELECTION.\
    project_selection import (
    _instance_id,
    _project_root,
)
from ...ADAPTERS_C30.ADAPTERS_C30__shared import (
    CEILINGS,
    ReadContext,
    open_regular,
    protected,
)


def is_native_control_name(name: str) -> bool:
    return any(
        name.startswith(prefix) and len(name) > len(prefix)
        for prefix in (".anechoic_", "_anechoic_")
    )


class ManifestIdentity(Protocol):
    name: str
    prefix: str


@dataclass(frozen=True, config=ConfigDict(strict=True, extra="forbid"))
class NativeProjectSelection:
    root: Path
    control_root: Path
    control_relative: Path
    instance_id: str
    project_name: str
    project_prefix: str
    manifest_path: Path
    manifest_ref: str
    manifest_sha256: str
    parameters: dict[str, object] = field(default_factory=dict)
    host_root: Path | None = None
    structure_snapshot: Path | None = None

    @property
    def launcher_state(self) -> Path:
        return (
            self.root
            / ".anechoic_runtime/runtime/project_mcp"
            / self.instance_id
        )

    @property
    def compose_project(self) -> str:
        return "anechoic-mcp-" + self.instance_id[:24]


def rebind_native_selection(
    selection: NativeProjectSelection,
    instance_id: str,
    *,
    host_root: str | Path | None = None,
) -> NativeProjectSelection:
    """Retain the admitted host identity after container path translation."""
    if (
        not isinstance(selection, NativeProjectSelection)
        or not isinstance(instance_id, str)
        or not re.fullmatch(r"[0-9a-f]{64}", instance_id)
    ):
        raise ProjectSelectionError("Transported Project identity is invalid")
    host = (
        selection.host_root if instance_id == selection.instance_id else None
    )
    if host_root is not None:
        try:
            host = Path(host_root)
        except (TypeError, ValueError) as error:
            raise ProjectSelectionError(
                "Transported host root is invalid"
            ) from error
        if (
            not host.is_absolute()
            or ".." in host.parts
            or str(host_root) != host.as_posix()
            or host.as_posix().startswith("//")
            or protected(host)
            or _instance_id(host, selection.control_relative) != instance_id
        ):
            raise ProjectSelectionError(
                "Transported Project identity contradicts its host binding"
            )
        if os.path.lexists(host):
            _project_root(host)
    return replace(selection, instance_id=instance_id, host_root=host)


def _manifest_validation_fields(
    path, carrier, require_state, require_header, require_summary
):
    fields, component_id = manifest_inputs(path, carrier)
    if require_state or require_header:
        fields.update(
            manifest_state_fields(carrier, include_header=require_header)
        )
    if require_summary:
        fields.update(manifest_summary_fields(carrier))
    return fields, component_id


def _read_manifest(root, control_root):
    relative = Path(control_root)
    if (
        len(relative.parts) != 1
        or str(control_root) != relative.as_posix()
        or not is_native_control_name(relative.name)
        or protected(relative)
    ):
        raise ProjectSelectionError(
            "Native control root must name one explicit direct Project child"
        )
    control = root / relative
    descriptor = open_regular(control, directory=True)
    os.close(descriptor)
    reader = ReadContext(roots=[str(root)], limits=dict(CEILINGS))
    sources = select_manifest_carriers(reader, root, control)
    selected = next(sources, None)
    if selected is None or next(sources, None) is not None:
        raise ProjectSelectionError(
            "Expected one Active Tier -1 Project Manifest at Project root"
        )
    path, carrier = selected
    return relative, control, reader, path, carrier


def _validated_manifest(relative, path, carrier, validate_manifest, flags):
    fields, component_id = _manifest_validation_fields(
        path,
        carrier,
        *flags,
    )
    manifest = validate_manifest(fields, component_id)
    parameters = getattr(manifest, "parameters", fields.get("parameters", {}))
    if not isinstance(parameters, dict):
        raise ProjectSelectionError(
            "Validated Project Manifest parameters must be a mapping"
        )
    try:
        spec_folder_layout(parameters)
    except ValueError as error:
        raise ProjectSelectionError(str(error)) from error
    if relative.name not in {
        f".anechoic_{manifest.name.casefold()}",
        f"_anechoic_{manifest.name.casefold()}",
    }:
        raise ProjectSelectionError(
            "Project Manifest name contradicts the native control root"
        )
    _validate_manifest_paths(fields, parameters, relative, manifest)
    if not str(fields["atom_id"]).startswith(f"{manifest.prefix}-S-"):
        raise ProjectSelectionError(
            "Project Manifest prefix contradicts its Atom ID"
        )
    return fields, manifest, parameters


def resolve_native_project(
    project_root: str | Path,
    control_root: str | Path,
    *,
    validate_manifest: Callable[[dict[str, object], str], ManifestIdentity],
    require_atom_state: bool = False,
    require_atom_header: bool = False,
    require_manifest_summary: bool = False,
) -> NativeProjectSelection:
    """Validate the Manifest with the caller's model and Project container."""
    root = _project_root(project_root)
    try:
        relative, control, reader, path, carrier = _read_manifest(
            root, control_root
        )
        flags = (
            require_atom_state,
            require_atom_header,
            require_manifest_summary,
        )
        fields, manifest, parameters = _validated_manifest(
            relative, path, carrier, validate_manifest, flags
        )
        if reader.currentness()["state"] != "unchanged":
            raise ProjectSelectionError(
                "Project carriers changed during selection"
            )
        return NativeProjectSelection(
            root,
            control,
            relative,
            _instance_id(root, relative),
            manifest.name,
            manifest.prefix,
            path,
            str(fields["ref_id"]),
            reader.fingerprints[str(path)],
            deepcopy(parameters),
        )
    except ProjectSelectionError:
        raise
    except (OSError, RuntimeError, TypeError, ValueError) as error:
        raise ProjectSelectionError(
            "Native Project Manifest is unavailable, invalid, or unsafe"
        ) from error


_RESERVED = {
    ".anechoic_new",
    ".anechoic_legacy",
    ".anechoic_legacy_archive",
    ".anechoic_runtime",
    ".anechoic_tmp",
}
_RESERVED |= {"_" + name[1:] for name in _RESERVED}


def _discover_candidates(root, reader, native):
    controls = _control_roots(root, reader)
    root_candidates = any(
        "-PROJECT_MANIFEST--" in path.name
        for path in reader.inventory_shallow(root)
    )
    if root_candidates:
        matches = _root_manifest_matches(reader, root, controls)
        natives = [native(matches[0])] if len(matches) == 1 else []
    else:
        natives = [
            native(relative)
            for relative in controls
            if _has_manifest(reader, root / relative)
        ]
    return controls, natives


def discover_native_project(
    project_root, control_root=None, *, manifest_validator
):
    """Return one native Project with an active Project Manifest."""
    root = _project_root(project_root)
    reader = ReadContext(roots=[str(root)], limits=dict(CEILINGS))

    def native(relative):
        return resolve_native_project(
            root, relative, validate_manifest=manifest_validator()
        )

    def finish(selection):
        if reader.currentness()["state"] != "unchanged":
            raise ProjectSelectionError(
                "Project carriers changed during selection"
            )
        return selection

    try:
        if control_root is not None:
            return finish(native(control_root))

        controls, natives = _discover_candidates(root, reader, native)
        if len(natives) != 1:
            raise ProjectSelectionError(
                "A unique native Project Manifest is required"
            )
        selected = finish(natives[0])
        if _control_roots(root, reader) != controls:
            raise ProjectSelectionError(
                "Project control candidates changed during selection"
            )
        return selected
    except ProjectSelectionError:
        raise
    except (
        OSError,
        RuntimeError,
        TypeError,
        ValueError,
        AttributeError,
    ) as error:
        raise ProjectSelectionError(
            "Project discovery is unavailable, invalid, or unsafe"
        ) from error
