"""Support native snapshot projection."""

import re
import stat
from pathlib import Path, PurePosixPath
from pydantic import ConfigDict
from pydantic.dataclasses import dataclass
from ...ADAPTERS_C30__pub import CEILINGS, ReadContext
from ...carriers.header.native_carrier_placement__pub import (
    ARCHIVE_DIRECTORY,
    TICKET_DIRECTORY,
    project_goal_filename,
)
from ..capture.native_capture_types import (
    NativeCapture,
)

_FIELDS = {
    "root",
    "control_root",
    "manifest_path",
    "manifest_sha256",
    "project_prefix",
}
_TICKET_TREES = {TICKET_DIRECTORY, "001_TICKETS", "__TKT"}
_MAX_TICKET_DELTA_PATHS = 1024


@dataclass(frozen=True, config=ConfigDict(strict=True, extra="forbid"))
class _SnapshotSelection:
    root: Path
    control_root: Path
    manifest_path: Path
    manifest_sha256: str
    project_prefix: str


def _relative(value, *, direct=False):
    if not isinstance(value, str):
        raise ValueError("Invalid relative path")
    path = PurePosixPath(value)
    if (
        not value
        or path.is_absolute()
        or path.as_posix() != value
        or any(part in {".", ".."} for part in path.parts)
        or (direct and len(path.parts) != 1)
    ):
        raise ValueError("Invalid relative path")
    return path


def _selection(binding, *, manifest_admitted=False):
    if not isinstance(binding, dict) or set(binding) != _FIELDS:
        raise ValueError("Invalid binding fields")
    root_value = binding["root"]
    if not isinstance(root_value, str):
        raise ValueError("Invalid Project root")
    root = Path(root_value)
    if (
        not root.is_absolute()
        or root.as_posix() != root_value
        or ".." in root.parts
        or root.resolve(strict=True) != root
        or not root.is_dir()
    ):
        raise ValueError("Invalid Project root")
    control = root / _relative(binding["control_root"], direct=True)
    manifest_relative = _relative(binding["manifest_path"])
    manifest = root / manifest_relative
    if (
        not manifest_admitted
        and not manifest.exists()
        and len(manifest_relative.parts) == 1
    ):
        manifest = control / manifest_relative
    if manifest.parent != root and not manifest.is_relative_to(control):
        raise ValueError("Invalid Manifest path")
    if control.is_symlink() or not control.is_dir():
        raise ValueError("Invalid control root")
    digest, prefix = binding["manifest_sha256"], binding["project_prefix"]
    if (
        not isinstance(digest, str)
        or not re.fullmatch(r"[0-9a-f]{64}", digest)
        or not isinstance(prefix, str)
        or not re.fullmatch(r"[A-Z][A-Z0-9]*", prefix)
    ):
        raise ValueError("Invalid binding identity")
    return _SnapshotSelection(root, control, manifest, digest, prefix)


def _archive_directories(selection, directories):
    if not isinstance(directories, (list, tuple)):
        raise ValueError("Invalid deferred archive directories")
    installed = selection.control_root / "000_ANECHOIC_framework"
    paths = {selection.root / _relative(path) for path in directories}
    for path in paths:
        if (
            path == selection.control_root
            or not path.is_relative_to(selection.control_root)
            or path.is_relative_to(installed)
            or path.name != ARCHIVE_DIRECTORY
        ):
            raise ValueError(
                "Deferred archive directory is outside "
                "the selected native archive trees"
            )
    return tuple(sorted(paths))


def _partition_archived(capture):
    foreground = NativeCapture(
        [],
        [],
        capture.errors,
        ingestion_issues=capture.ingestion_issues,
        carrier_hashes=dict(capture.carrier_hashes),
        status_domains=capture.status_domains,
        classified_templates=capture.classified_templates,
    )
    archived = NativeCapture([], [], {}, status_domains=capture.status_domains)
    for row, edge in zip(capture.atoms, capture.containment, strict=True):
        target = archived if row["status_group"] == "Archived" else foreground
        target.atoms.append(row)
        target.containment.append(edge)
        if target is archived:
            path = row["source_path"]
            archived.carrier_hashes[path] = foreground.carrier_hashes.pop(path)
    return foreground, archived


def _ticket_paths(selection, paths):
    if (
        not isinstance(paths, (list, tuple))
        or not 0 < len(paths) <= _MAX_TICKET_DELTA_PATHS
    ):
        raise ValueError("Invalid Ticket delta path count")
    relatives = {_relative(path) for path in paths}
    for relative in relatives:
        if (
            len(relative.parts) < 3
            or relative.parts[0] != selection.control_root.name
            or relative.parts[1] not in _TICKET_TREES
            or relative.suffix != ".md"
            or selection.root / relative == selection.manifest_path
        ):
            raise ValueError(
                "Ticket delta path is outside the native Ticket trees"
            )
    return relatives


def _carrier_paths(selection, paths):
    if (
        not isinstance(paths, (list, tuple))
        or not 0 < len(paths) <= _MAX_TICKET_DELTA_PATHS
    ):
        raise ValueError("Invalid carrier delta path count")
    relatives = {_relative(path) for path in paths}
    for relative in relatives:
        path = selection.root / relative
        under_control = (
            len(relative.parts) >= 2
            and relative.parts[0] == selection.control_root.name
        )
        root_goal = len(relative.parts) == 1 and project_goal_filename(
            relative.name
        )
        if (
            relative.suffix != ".md"
            or not (under_control or root_goal)
            or path == selection.manifest_path
            or "-PROJECT_MANIFEST--" in relative.name
            or (
                under_control and relative.parts[1] == "000_ANECHOIC_framework"
            )
        ):
            raise ValueError(
                "Carrier delta path is outside the selected native carriers"
            )
    return relatives


def _ticket_versions(root, relatives):
    reader = ReadContext(roots=[str(root)], limits=dict(CEILINGS))
    versions = {}
    for relative in relatives:
        path = reader.allowed(root / relative)
        try:
            info = path.lstat()
        except FileNotFoundError:
            continue
        if not stat.S_ISREG(info.st_mode):
            raise ValueError("Ticket delta path is not a regular file")
        versions[str(path)] = reader.version(info)
    return versions
