"""Read the Release fields of one native Project Manifest without executing its claim.

This is a narrow Release input contract, not validation against the compiled Model.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import os
from pathlib import Path
import re
import stat

import yaml

from ._release_manifest_parser import _claim, read_atom_header


_RESERVED = {prefix + name for prefix in (".anechoic_", "_anechoic_")
             for name in ("new", "legacy", "legacy_archive", "runtime", "tmp")}
_PROTECTED = {".ssh", ".aws", ".gnupg"}
_MAX_FILE = 64 * 1024 * 1024


@dataclass(frozen=True)
class ReleaseSelection:
    root: Path
    control_root: Path
    control_relative: Path
    instance_id: str
    project_name: str
    project_prefix: str
    manifest_path: Path
    manifest_ref: str
    manifest_sha256: str
    parameters: dict[str, object]

    @property
    def launcher_state(self) -> Path:
        return self.root / ".anechoic_runtime/runtime/project_mcp" / self.instance_id


def _protected(path: Path) -> bool:
    return any(part in _PROTECTED or part == ".env" or part.startswith(".env.") or part.endswith(".env")
               for part in path.parts)


def _directory(path: Path) -> int:
    fd = os.open("/", os.O_RDONLY | os.O_DIRECTORY)
    try:
        for part in path.parts[1:]:
            child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            os.close(fd)
            fd = child
        return fd
    except BaseException:
        os.close(fd)
        raise


def _version(info: os.stat_result) -> tuple[int, ...]:
    return info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns, info.st_ctime_ns


def _read(fd: int, name: str) -> tuple[bytes, tuple[int, ...]]:
    descriptor = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=fd)
    with os.fdopen(descriptor, "rb") as stream:
        before = os.fstat(stream.fileno())
        if not stat.S_ISREG(before.st_mode) or before.st_size > _MAX_FILE:
            raise ValueError("Manifest source is not a bounded regular file")
        raw = stream.read(_MAX_FILE + 1)
        if len(raw) != before.st_size or _version(before) != _version(os.fstat(stream.fileno())):
            raise ValueError("Manifest source changed during read")
        return raw, _version(before)


def _names(fd: int, *, controls: bool, ignore_control_symlinks: bool = False) -> tuple[str, ...]:
    with os.scandir(fd) as entries:
        names = []
        for index, entry in enumerate(entries, 1):
            if index > 1_000_000:
                raise ValueError("Project inventory exceeds the host ceiling")
            if controls:
                if not entry.name.startswith((".anechoic_", "_anechoic_")) or entry.name in _RESERVED:
                    continue
                if entry.is_symlink():
                    if ignore_control_symlinks:
                        continue
                    raise ValueError("Project control candidates must not be symlinks")
                if entry.is_dir(follow_symlinks=False):
                    names.append(entry.name)
                    if len(names) > 64:
                        raise ValueError("Project control candidates exceed the host ceiling")
            elif entry.name.endswith(".md"):
                names.append(entry.name)
        return tuple(sorted(names))


def _manifest_control(parameters: dict, project_name: str, relative: Path | None,
                      controls: tuple[str, ...], explicit: Path | None) -> Path:
    project = parameters.get("project", {})
    project_root = project.get("root", {}) if isinstance(project, dict) else {}
    if relative is None:
        matches = {f".anechoic_{project_name.casefold()}", f"_anechoic_{project_name.casefold()}"}
        if isinstance(project_root, dict) and "prefix" in project_root:
            marker = {"dot": ".", "underscore": "_"}.get(project_root["prefix"])
            if marker is None:
                raise ValueError("Invalid Project root prefix")
            matches = {f"{marker}anechoic_{project_name.casefold()}"}
        existing = matches.intersection(controls)
        if len(existing) != 1:
            raise ValueError("Expected one matching Project control root")
        relative = Path(existing.pop())
        if explicit is not None and relative != explicit:
            raise ValueError("Project control root contradicts the selection")
    if relative.name not in {f".anechoic_{project_name.casefold()}", f"_anechoic_{project_name.casefold()}"}:
        raise ValueError("Project Manifest identity contradicts the selected control root")
    if isinstance(project_root, dict) and "prefix" in project_root:
        marker = {"dot": ".", "underscore": "_"}.get(project_root["prefix"])
        if marker is None or relative.name != f"{marker}anechoic_{project_name.casefold()}":
            raise ValueError("Project root prefix contradicts the selection")
    paths = parameters.get("paths", {})
    if isinstance(paths, dict) and "control_root" in paths and paths["control_root"] != relative.as_posix():
        raise ValueError("Project control_root contradicts the selection")
    return relative


def _manifest(metadata: dict, body: str, name: str, relative: Path | None, digest: str, root: Path,
              controls: tuple[str, ...] = (), explicit: Path | None = None) -> ReleaseSelection:
    context, state = metadata.get("context"), metadata.get("state")
    if not isinstance(context, dict) or not isinstance(state, dict):
        raise ValueError("Manifest context and state are required")
    flat = "atom_family" in metadata
    identity = metadata.get("atom_id") if flat else (metadata.get("identity") or {}).get("atom_id")
    container = metadata.get("container") if flat else context.get("container")
    tier = metadata.get("tier") if flat else context.get("tier")
    version = state.get("version")
    if (context.get("template") != "project_manifest" or state.get("status") != "active"
            or container != {"component": "C00"} or type(tier) is not int or tier != -1
            or type(version) is not int or version < 1 or not isinstance(identity, str)
            or re.fullmatch(r"[A-Z]+-S-[0-9]+", identity) is None
            or not name.startswith(identity + "-") or (flat and metadata.get("atom_family") != "SPEC")):
        raise ValueError("Invalid Active Project Manifest header")
    fields = _claim(body)
    project_name, prefix = fields["name"], fields["prefix"]
    parameters = fields.get("parameters", {})
    if (not isinstance(project_name, str) or not project_name.strip() or not isinstance(prefix, str)
            or re.fullmatch(r"[A-Z]+", prefix) is None or not identity.startswith(prefix + "-S-")
            or not isinstance(parameters, dict)):
        raise ValueError("Project Manifest identity contradicts the selected control root")
    manifest_at_root = relative is None
    relative = _manifest_control(parameters, project_name, relative, controls, explicit)
    instance = sha256(f"{root}\0{relative.as_posix()}".encode("utf-8")).hexdigest()
    return ReleaseSelection(root, root / relative, relative, instance, project_name, prefix,
                            root / name if manifest_at_root else root / relative / name,
                            f"{identity}@{version}", digest, parameters)


def _scan_control(root_fd: int, control: str, root: Path, total_bytes: int,
                  controls: tuple[str, ...] = (), explicit: Path | None = None):
    selection = None
    fd = os.dup(root_fd) if control == "." else os.open(
        control, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=root_fd)
    try:
        control_identity = (os.fstat(fd).st_dev, os.fstat(fd).st_ino)
        names = _names(fd, controls=False)
        records = []
        candidates = []
        has_manifest = False
        for name in names:
            if control == "." and not re.match(r"[A-Z]+-S-", name) and "PROJECT_MANIFEST" not in name:
                continue
            raw, version = _read(fd, name)
            total_bytes += len(raw)
            if total_bytes > 1024 * 1024 * 1024:
                raise ValueError("Project inventory exceeds the read ceiling")
            digest = sha256(raw).hexdigest()
            records.append((name, version, digest))
            try:
                metadata, body = read_atom_header(raw.decode("utf-8"))
            except (ValueError, UnicodeError, yaml.YAMLError, RecursionError):
                if ((control != "." and re.match(r"[A-Z]+-S-", name))
                        or (control == "." and "PROJECT_MANIFEST" in name)):
                    raise
                continue
            context = metadata.get("context")
            if isinstance(context, dict) and context.get("template") == "project_manifest":
                has_manifest = True
                if isinstance(metadata.get("state"), dict) and metadata["state"].get("status") == "active":
                    candidates.append(_manifest(metadata, body, name, None if control == "." else Path(control),
                                                digest, root, controls, explicit))
            elif "atom_family" not in metadata and "PROJECT_MANIFEST" in name:
                has_manifest = True
        if has_manifest:
            if len(candidates) != 1:
                raise ValueError("Expected one Active Project Manifest")
            selection = candidates[0]
        snapshot = (control, control_identity, names, records)
    finally:
        os.close(fd)
    return selection, snapshot, total_bytes


def _verify_snapshots(root_fd: int, snapshots, total_bytes: int) -> None:
    for control, identity, names, records in snapshots:
        fd = os.dup(root_fd) if control == "." else os.open(
            control, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=root_fd)
        try:
            info = os.fstat(fd)
            if (info.st_dev, info.st_ino) != identity or _names(fd, controls=False) != names:
                raise ValueError("Project control changed during selection")
            for name, version, digest in records:
                raw, current = _read(fd, name)
                total_bytes += len(raw)
                if total_bytes > 1024 * 1024 * 1024:
                    raise ValueError("Project inventory exceeds the read ceiling")
                if current != version or sha256(raw).hexdigest() != digest:
                    raise ValueError("Project carriers changed during selection")
            if _names(fd, controls=False) != names:
                raise ValueError("Project control changed during selection")
        finally:
            os.close(fd)


def _canonical_root(project_root: str | Path) -> Path:
    raw_root = Path(project_root).expanduser()
    if ".." in raw_root.parts or _protected(raw_root):
        raise ValueError("Project root is unsafe")
    root = Path(os.path.abspath(raw_root))
    if root == Path(root.anchor) or root.resolve(strict=True) != root:
        raise ValueError("Project root must be a non-symlink directory")
    return root


def _control_identity(root_fd: int, relative: Path) -> tuple[int, int]:
    fd = os.open(relative.name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=root_fd)
    try:
        info = os.fstat(fd)
        return info.st_dev, info.st_ino
    finally:
        os.close(fd)


def _verify_selection(root: Path, root_fd: int, root_identity, selection: ReleaseSelection,
                      controls, check_controls: bool, snapshots, total_bytes: int, control_identity) -> None:
    if check_controls and _names(root_fd, controls=True) != controls:
        raise ValueError("Project control candidates changed during selection")
    _verify_snapshots(root_fd, snapshots, total_bytes)
    if check_controls and _names(root_fd, controls=True) != controls:
        raise ValueError("Project control candidates changed during selection")
    if control_identity is not None and _control_identity(root_fd, selection.control_relative) != control_identity:
        raise ValueError("Project control changed during selection")
    current_root = _directory(root)
    try:
        info = os.fstat(current_root)
        if (info.st_dev, info.st_ino) != root_identity:
            raise ValueError("Project root changed during selection")
    finally:
        os.close(current_root)


def read_release_selection(project_root: str | Path, control_relative: str | Path | None = None) -> ReleaseSelection:
    """Select one active native Project Manifest and pin the inputs read during selection."""
    try:
        root = _canonical_root(project_root)
        root_fd = _directory(root)
        try:
            root_identity = (os.fstat(root_fd).st_dev, os.fstat(root_fd).st_ino)
            explicit = None
            if control_relative is not None:
                explicit = Path(control_relative)
                if (len(explicit.parts) != 1 or str(control_relative) != explicit.as_posix()
                        or not explicit.name.startswith((".anechoic_", "_anechoic_"))
                        or explicit.name in {".anechoic_", "_anechoic_"} or _protected(explicit)):
                    raise ValueError("Control root must be a normalized direct Project child")
            controls = _names(root_fd, controls=True, ignore_control_symlinks=explicit is not None)
            selection, root_snapshot, total_bytes = _scan_control(
                root_fd, ".", root, 0, controls, explicit)
            if selection is not None and explicit is not None:
                controls = _names(root_fd, controls=True)
            check_controls = selection is not None or explicit is None
            snapshots = [root_snapshot]
            control_identity = None
            if selection is not None:
                control_identity = _control_identity(root_fd, selection.control_relative)
            if selection is None:
                legacy_controls = controls if explicit is None else (explicit.name,)
                selections = []
                for control in legacy_controls:
                    candidate, snapshot, total_bytes = _scan_control(root_fd, control, root, total_bytes)
                    if candidate is not None:
                        selections.append(candidate)
                    snapshots.append(snapshot)
                if len(selections) != 1:
                    raise ValueError("A unique native Project Manifest is required")
                selection = selections[0]
            _verify_selection(root, root_fd, root_identity, selection, controls, check_controls,
                              snapshots, total_bytes, control_identity)
            return selection
        finally:
            os.close(root_fd)
    except (OSError, RuntimeError, TypeError, ValueError, AttributeError, yaml.YAMLError, RecursionError) as error:
        raise ValueError("Project Manifest is unavailable, invalid, or unsafe") from error
