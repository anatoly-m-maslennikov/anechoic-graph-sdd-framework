"""Resolve and bind one Project without repository or sibling fallback.

Selection is read-only.  Project Settings and the current Scope Unit
Declaration Atoms are read through the bounded, non-following reader.
Container startup may explicitly retain the host identity; ambient environment
variables never select a Project or replace its identity here.
"""

from __future__ import annotations

from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from dataclasses import field, replace
import os
from pathlib import Path
import re
from pydantic import ConfigDict
from pydantic.dataclasses import dataclass
from types import MappingProxyType
from typing import Any

from ...ADAPTERS_C30.ADAPTERS_C30__shared import (
    CEILINGS,
    ReadContext,
    open_regular,
    protected,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.settings.project.project__shared import (
    ProjectSelectionError,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.structure.scope.scope__shared import (
    ScopeDeclarationError,
    ScopeUnitDeclarations,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.settings.settings__shared import (
    bind_settings_selection,
    bound_selection,
    read_settings_carrier,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.structure.scope.units.units__shared import (
    read_scope_unit_declarations as read_scope_unit_declarations,
)


from ._selection_declarations import (
    _selected_declarations,
    _selection_provenance,
)

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.\
    PROJECT_SUPPORT.PROJECT_SELECTION.\
    project_selection_boundary import (
    _DeclarationBoundaryProof,
    _declaration_boundary_proof,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.\
    PROJECT_SUPPORT.PROJECT_SELECTION.\
    project_selection_paths import (
    SETTINGS_FILENAME,
    _control_candidates,
    _control_relative,
    _instance_id,
    _project_root,
)

_IDENTITY = re.compile(r"[0-9a-f]{64}\Z")


def _freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType(
            {key: _freeze(item) for key, item in value.items()}
        )
    if isinstance(value, (list, tuple)):
        return tuple(_freeze(item) for item in value)
    return value


@dataclass(frozen=True, config=ConfigDict(strict=True, extra="forbid"))
class ProjectSelection:
    root: Path
    control_root: Path
    control_relative: Path
    instance_id: str
    settings: Mapping[str, Any]
    structure: Mapping[str, Any]
    declaration_paths: tuple[Path, ...]
    declaration_source_pins: Mapping[str, Mapping[str, Any]]
    declaration_digest: str
    provenance: Mapping[str, Any] = field(default_factory=dict)
    host_root: Path | None = None
    _boundary_proof: _DeclarationBoundaryProof | None = field(
        default=None, repr=False, compare=False
    )
    root_declaration_path: Path | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "settings", _freeze(self.settings))
        object.__setattr__(self, "structure", _freeze(self.structure))
        object.__setattr__(
            self,
            "declaration_source_pins",
            _freeze(self.declaration_source_pins),
        )
        object.__setattr__(self, "provenance", _freeze(self.provenance))

    @property
    def settings_path(self) -> Path:
        return self.control_root / SETTINGS_FILENAME

    def _revalidate_boundary(
        self, *, reader: ReadContext | None = None
    ) -> None:
        if self._boundary_proof is None:
            raise ProjectSelectionError(
                "Selected Project declaration boundary proof is unavailable"
            )
        self._boundary_proof.revalidate(reader=reader)

    @property
    def installed_state(self) -> Path:
        return self.launcher_state

    @property
    def compose_project(self) -> str:
        return "anechoic-mcp-" + self.instance_id[:24]

    @property
    def launcher_state(self) -> Path:
        return (
            self.root
            / ".anechoic_runtime"
            / "runtime"
            / "project_mcp"
            / self.instance_id
        )


def _read_toml(reader: ReadContext, path: Path) -> dict[str, Any]:
    try:
        return read_settings_carrier(path, read_bytes=reader.read)
    except (OSError, RuntimeError, UnicodeError, ValueError) as error:
        raise ProjectSelectionError(
            f"Required Project carrier is unavailable or invalid: {path.name}"
        ) from error


def _validate_settings(settings: dict[str, Any], relative: Path) -> str:
    paths = settings.get("paths")
    if not isinstance(paths, dict):
        raise ProjectSelectionError(
            "Project Settings must contain a paths table"
        )
    declared = paths.get("control_root")
    if (
        not isinstance(declared, str)
        or _control_relative(declared) != relative
    ):
        raise ProjectSelectionError(
            "Project Settings control_root contradicts the selection"
        )
    project = settings.get("project")
    if (
        not isinstance(project, dict)
        or not isinstance(project.get("name"), str)
        or not project["name"].strip()
    ):
        raise ProjectSelectionError(
            "Project Settings must contain a non-empty Project name"
        )
    return project["name"]


def _read_selected_settings(root, control_root):
    if control_root is None:
        candidates = _control_candidates(root)
        if len(candidates) != 1:
            raise ProjectSelectionError(
                "Project control root is missing or ambiguous"
            )
        relative = candidates[0]
    else:
        relative = _control_relative(control_root)
    control = root / relative
    descriptor = open_regular(control, directory=True)
    os.close(descriptor)
    reader = ReadContext(roots=[str(root)], limits=dict(CEILINGS))
    settings_path = control / SETTINGS_FILENAME
    settings = _read_toml(reader, settings_path)
    project_name = _validate_settings(settings, relative)
    return relative, control, reader, settings_path, settings, project_name


def resolve_project(
    project_root: str | Path,
    control_root: str | Path | None = None,
    *,
    indexed_declarations: ScopeUnitDeclarations | None = None,
) -> ProjectSelection:
    """Read exactly one local Project selection before any runtime effects."""
    root = _project_root(project_root)
    try:
        relative, control, reader, settings_path, settings, project_name = (
            _read_selected_settings(root, control_root)
        )
        declarations = _selected_declarations(
            root, relative, control, reader, indexed_declarations, project_name
        )
        structure = declarations.as_structure()
        boundary_proof = _declaration_boundary_proof(
            root, relative, structure["scope_units"], reader=reader
        )
        if reader.currentness()["state"] != "unchanged":
            raise ProjectSelectionError(
                "Project carriers changed during selection"
            )
        provenance = _selection_provenance(
            root, settings_path, settings, reader, declarations
        )
        return _make_selection(
            root,
            control,
            relative,
            settings,
            declarations,
            structure,
            boundary_proof,
            provenance,
        )
    except ProjectSelectionError:
        raise
    except ScopeDeclarationError as error:
        raise ProjectSelectionError(str(error)) from error
    except (OSError, RuntimeError, TypeError, ValueError) as error:
        raise ProjectSelectionError(
            "Selected Project control is unavailable or unsafe"
        ) from error


def _make_selection(
    root,
    control,
    relative,
    settings,
    declarations,
    structure,
    boundary_proof,
    provenance,
):
    return ProjectSelection(
        root=root,
        control_root=control,
        control_relative=relative,
        instance_id=_instance_id(root, relative),
        settings=settings,
        structure=structure,
        declaration_paths=declarations.paths,
        declaration_source_pins=declarations.source_pins,
        declaration_digest=declarations.digest,
        provenance=provenance,
        host_root=root,
        _boundary_proof=boundary_proof,
        root_declaration_path=declarations.root.source,
    )


@contextmanager
def bind_selection(selection: ProjectSelection) -> Iterator[ProjectSelection]:
    "Bind an already selected context for this startup/task and restore it."
    if not isinstance(selection, ProjectSelection):
        raise ProjectSelectionError(
            "Only a validated ProjectSelection can be bound"
        )
    with bind_settings_selection(selection, _validate_bound_root):
        yield selection


def _validate_bound_root(
    selection: ProjectSelection, root: str | Path
) -> None:
    if selection.root != _project_root(root):
        raise ProjectSelectionError(
            "Active Project selection belongs to another root"
        )


def active_selection(root: str | Path) -> ProjectSelection:
    "Use the bound selection, refusing foreign roots; otherwise resolve once."
    selection = bound_selection(root)
    return selection if selection is not None else resolve_project(root)


def rebind_selection(
    selection: ProjectSelection,
    instance_id: str,
    *,
    host_root: str | Path | None = None,
) -> ProjectSelection:
    """Retain an explicitly admitted host identity after container translation.

    Only startup callers transport this value.  When the canonical host root is
    carried too, verify its identity formula.  Existing host directories must
    use canonical non-symlink spelling; an unmounted host path need not exist
    inside the container.  This helper never reads an environment variable.
    """
    if (
        not isinstance(selection, ProjectSelection)
        or not isinstance(instance_id, str)
        or not _IDENTITY.fullmatch(instance_id)
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


__all__ = [
    "ProjectSelection",
    "ProjectSelectionError",
    "resolve_project",
    "bind_selection",
    "bound_selection",
    "active_selection",
    "rebind_selection",
]
