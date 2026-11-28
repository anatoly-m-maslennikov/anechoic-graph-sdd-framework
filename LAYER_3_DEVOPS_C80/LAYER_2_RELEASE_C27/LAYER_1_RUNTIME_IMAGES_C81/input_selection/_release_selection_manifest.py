"""Validate native Project Manifest identity and release selection paths."""

from hashlib import sha256
import os
from pathlib import Path
import re
from pydantic import ConfigDict
from pydantic.dataclasses import dataclass
from ._release_manifest_parser import _claim

_PROTECTED = {".ssh", ".aws", ".gnupg"}


@dataclass(frozen=True, config=ConfigDict(strict=True, extra="forbid"))
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
        return (
            self.root
            / ".anechoic_runtime/runtime/project_mcp"
            / self.instance_id
        )


def _protected(path: Path) -> bool:
    return any(
        part in _PROTECTED
        or part == ".env"
        or part.startswith(".env.")
        or part.endswith(".env")
        for part in path.parts
    )


def _check_manifest_control(parameters, project_name, relative, project_root):
    if relative.name not in {
        f".anechoic_{project_name.casefold()}",
        f"_anechoic_{project_name.casefold()}",
    }:
        raise ValueError(
            "Project Manifest identity contradicts the selected control root"
        )
    if isinstance(project_root, dict) and "prefix" in project_root:
        marker = {"dot": ".", "underscore": "_"}.get(project_root["prefix"])
        if (
            marker is None
            or relative.name != f"{marker}anechoic_{project_name.casefold()}"
        ):
            raise ValueError("Project root prefix contradicts the selection")
    paths = parameters.get("paths", {})
    if (
        isinstance(paths, dict)
        and "control_root" in paths
        and paths["control_root"] != relative.as_posix()
    ):
        raise ValueError("Project control_root contradicts the selection")


def _manifest_control(
    parameters: dict,
    project_name: str,
    relative: Path | None,
    controls: tuple[str, ...],
    explicit: Path | None,
) -> Path:
    project = parameters.get("project", {})
    project_root = project.get("root", {}) if isinstance(project, dict) else {}
    if relative is None:
        matches = {
            f".anechoic_{project_name.casefold()}",
            f"_anechoic_{project_name.casefold()}",
        }
        if isinstance(project_root, dict) and "prefix" in project_root:
            marker = {"dot": ".", "underscore": "_"}.get(
                project_root["prefix"]
            )
            if marker is None:
                raise ValueError("Invalid Project root prefix")
            matches = {f"{marker}anechoic_{project_name.casefold()}"}
        existing = matches.intersection(controls)
        if len(existing) != 1:
            raise ValueError("Expected one matching Project control root")
        relative = Path(existing.pop())
        if explicit is not None and relative != explicit:
            raise ValueError("Project control root contradicts the selection")
    _check_manifest_control(parameters, project_name, relative, project_root)
    return relative


def _manifest_identity(metadata, name):
    context, state = metadata.get("context"), metadata.get("state")
    if not isinstance(context, dict) or not isinstance(state, dict):
        raise ValueError("Manifest context and state are required")
    flat = "atom_family" in metadata
    identity = (
        metadata.get("atom_id")
        if flat
        else (metadata.get("identity") or {}).get("atom_id")
    )
    container = metadata.get("container") if flat else context.get("container")
    tier = metadata.get("tier") if flat else context.get("tier")
    version = state.get("version")
    if (
        context.get("template") != "project_manifest"
        or state.get("status") != "active"
        or container != {"component": "C00"}
        or type(tier) is not int
        or tier != -1
        or type(version) is not int
        or version < 1
        or not isinstance(identity, str)
        or re.fullmatch(r"[A-Z]+-S-[0-9]+", identity) is None
        or not name.startswith(identity + "-")
        or (flat and metadata.get("atom_family") != "SPEC")
    ):
        raise ValueError("Invalid Active Project Manifest header")
    return identity, version


def _manifest_fields(fields, identity):
    project_name, prefix = fields["name"], fields["prefix"]
    parameters = fields.get("parameters", {})
    if (
        not isinstance(project_name, str)
        or not project_name.strip()
        or not isinstance(prefix, str)
        or re.fullmatch(r"[A-Z]+", prefix) is None
        or not identity.startswith(prefix + "-S-")
        or not isinstance(parameters, dict)
    ):
        raise ValueError(
            "Project Manifest identity contradicts the selected control root"
        )
    for key in ("root", "folder_layout"):
        if key not in parameters:
            continue
        project = parameters.setdefault("project", {})
        if not isinstance(project, dict) or key in project:
            raise ValueError(f"Invalid or duplicate Project Manifest {key}")
        project[key] = parameters.pop(key)
    return project_name, prefix, parameters


def _manifest(
    metadata: dict,
    body: str,
    name: str,
    relative: Path | None,
    digest: str,
    root: Path,
    controls: tuple[str, ...] = (),
    explicit: Path | None = None,
) -> ReleaseSelection:
    identity, version = _manifest_identity(metadata, name)
    project_name, prefix, parameters = _manifest_fields(_claim(body), identity)
    manifest_at_root = relative is None
    relative = _manifest_control(
        parameters, project_name, relative, controls, explicit
    )
    instance = sha256(
        f"{root}\0{relative.as_posix()}".encode("utf-8")
    ).hexdigest()
    return ReleaseSelection(
        root,
        root / relative,
        relative,
        instance,
        project_name,
        prefix,
        root / name if manifest_at_root else root / relative / name,
        f"{identity}@{version}",
        digest,
        parameters,
    )


def _manifest_status(metadata: dict, name: str) -> tuple[bool, bool]:
    context = metadata.get("context")
    if (
        isinstance(context, dict)
        and context.get("template") == "project_manifest"
    ):
        state = metadata.get("state")
        return True, isinstance(state, dict) and state.get(
            "status"
        ) == "active"
    return "atom_family" not in metadata and "PROJECT_MANIFEST" in name, False


def _canonical_root(project_root: str | Path) -> Path:
    raw_root = Path(project_root).expanduser()
    if ".." in raw_root.parts or _protected(raw_root):
        raise ValueError("Project root is unsafe")
    root = Path(os.path.abspath(raw_root))
    if root == Path(root.anchor) or root.resolve(strict=True) != root:
        raise ValueError("Project root must be a non-symlink directory")
    return root


def _control_identity(root_fd: int, relative: Path) -> tuple[int, int]:
    fd = os.open(
        relative.name,
        os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
        dir_fd=root_fd,
    )
    try:
        info = os.fstat(fd)
        return info.st_dev, info.st_ino
    finally:
        os.close(fd)


def _directory(path: Path) -> int:
    fd = os.open("/", os.O_RDONLY | os.O_DIRECTORY)
    try:
        for part in path.parts[1:]:
            child = os.open(
                part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd
            )
            os.close(fd)
            fd = child
        return fd
    except BaseException:
        os.close(fd)
        raise


def _version(info: os.stat_result) -> tuple[int, ...]:
    return (
        info.st_dev,
        info.st_ino,
        info.st_size,
        info.st_mtime_ns,
        info.st_ctime_ns,
    )
