"""Pin and revalidate Project declaration boundaries."""
from collections.abc import Iterable, Mapping
from dataclasses import field
import hashlib
from pathlib import Path
from types import MappingProxyType
from typing import Any

from pydantic import ConfigDict
from pydantic.dataclasses import dataclass

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import CEILINGS, ReadContext
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import ProjectSelectionError
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import parse_settings_carrier
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.project_selection_paths import SETTINGS_FILENAME, _control_relative, _instance_id, _project_root


@dataclass(
    frozen=True,
    config=ConfigDict(strict=True, extra="forbid", arbitrary_types_allowed=True),
)
class _DeclarationBoundaryProof:
    root: Path
    marker_pins: Mapping[str, str | None]
    _reader: ReadContext = field(repr=False, compare=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "marker_pins", MappingProxyType(dict(self.marker_pins)))

    def revalidate(self, *, reader: ReadContext | None = None) -> None:
        """Reopen the original marker set without replacing any captured pin."""
        reader = reader if reader is not None else ReadContext(roots=[str(self.root)], limits=dict(CEILINGS))
        for relative, expected in self.marker_pins.items():
            try:
                raw = reader.read(self.root / relative, remember=False)
            except FileNotFoundError:
                if expected is None:
                    continue
                raise ProjectSelectionError("Declaration boundary Settings disappeared") from None
            except (OSError, RuntimeError, ValueError) as error:
                raise ProjectSelectionError("Declaration boundary evidence is unavailable or unsafe") from error
            if expected is None or hashlib.sha256(raw).hexdigest() != expected:
                raise ProjectSelectionError("Declaration boundary evidence changed")



def _marker(root: Path, directory: Path, reader: ReadContext, pins: dict[str, str | None]) -> dict[str, Any] | None:
    path = directory / SETTINGS_FILENAME
    key = path.relative_to(root).as_posix()
    try:
        raw = reader.read(path)
    except FileNotFoundError:
        if str(path) in reader.fingerprints:
            raise ProjectSelectionError("Declaration boundary evidence changed") from None
        pins[key] = None
        return None
    except (OSError, RuntimeError, ValueError) as error:
        raise ProjectSelectionError("Declaration boundary Settings are unavailable or unsafe") from error
    digest = hashlib.sha256(raw).hexdigest()
    if reader.fingerprints[str(path)] != digest:
        raise ProjectSelectionError("Declaration boundary evidence changed")
    pins[key] = digest
    try:
        settings = parse_settings_carrier(raw)
        project, paths = settings.get("project"), settings.get("paths")
        name = project.get("name") if isinstance(project, dict) else None
        declared = paths.get("control_root") if isinstance(paths, dict) else None
        if not isinstance(name, str) or not name.strip() or name != name.strip():
            raise ProjectSelectionError("Declaration boundary Settings lack exact Project identity")
        if not isinstance(declared, str) or _control_relative(declared) != Path(directory.name):
            raise ProjectSelectionError("Declaration boundary Settings contradict their control root")
    except (UnicodeError, ValueError) as error:
        raise ProjectSelectionError("Declaration boundary Settings are invalid or contradictory") from error
    return settings


def _declaration_directories(root: Path, declarations: Iterable[Mapping[str, Any]], reader: ReadContext, directories: set[Path]) -> None:
    for row in declarations:
        if not isinstance(row, Mapping):
            raise ProjectSelectionError("Scope Unit Declaration is invalid")
        for field_name in ("authority_path", "delivery_path"):
            value = row.get(field_name)
            if not isinstance(value, str) or not value or "\\" in value or "\x00" in value:
                raise ProjectSelectionError(f"Scope Unit Declaration {field_name} is unsafe")
            if field_name == "delivery_path" and value == ".":
                continue
            relative = Path(value.rstrip("/"))
            if relative.is_absolute() or not relative.parts or ".." in relative.parts or relative.as_posix() != value.rstrip("/"):
                raise ProjectSelectionError(f"Scope Unit Declaration {field_name} is unsafe")
            directory = reader.allowed(root / relative)
            while directory != root:
                directories.add(directory)
                directory = directory.parent


def _declaration_boundary_proof(
    project_root: str | Path, control_root: str | Path,
    declarations: Iterable[Mapping[str, Any]], *, reader: ReadContext | None = None,
) -> _DeclarationBoundaryProof:
    """Pin Settings-defined boundaries along only the supplied declaration paths.

    This private refusal check neither resolves logical Settings Revisions nor
    selects another Project.  Callers retain its proof through their final check.
    """
    root = _project_root(project_root)
    control = root / _control_relative(control_root)
    reader = reader if reader is not None else ReadContext(roots=[str(root)], limits=dict(CEILINGS))
    pins: dict[str, str | None] = {}


    if _marker(root, control, reader, pins) is None:
        raise ProjectSelectionError("Owning Project Settings are unavailable")
    directories = {control}
    try:
        _declaration_directories(root, declarations, reader, directories)
        for directory in sorted(directories):
            if directory == control:
                continue
            settings = _marker(root, directory, reader, pins)
            if settings is not None:
                if _instance_id(directory.parent, Path(directory.name)) != _instance_id(root, control.relative_to(root)):
                    raise ProjectSelectionError("Scope Unit Declaration path crosses another Project control root")
        proof = _DeclarationBoundaryProof(root, pins, reader)
        proof.revalidate(reader=reader)
        return proof
    except ProjectSelectionError:
        raise
    except (OSError, RuntimeError, TypeError, ValueError) as error:
        raise ProjectSelectionError("Project declaration boundary evidence is unavailable or unsafe") from error

