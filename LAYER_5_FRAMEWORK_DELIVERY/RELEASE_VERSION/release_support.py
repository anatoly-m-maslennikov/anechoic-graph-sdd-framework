
"""Filesystem and package support for the direct local-release runner."""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import tempfile
import tomllib
from collections.abc import Mapping
from pathlib import Path, PurePosixPath
from typing import Any

import yaml

from release_assets import LocalReleaseError
from release_cleanup_images import read_ready_images
from release_images import ImageManager, RETIRED_ASSETS, TOOL_REGISTRY, ready_predecessor
from release_inputs import read_atom_header


_GENERATED_ASSETS = frozenset({TOOL_REGISTRY})
_BOOTSTRAP = Path("LAYER_3_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/docker/start_mcp.py")

_DEFAULT_PRODUCT = "LAYER_1_FRAMEWORK_METHODOLOGY"
_PRESERVED_NAMES = frozenset(
    {
        "settings.toml",
        "config.toml",
        "project_settings.toml",
        "anechoic_framework_settings.toml",
        "operators_registry.toml",
        "operator_registry",
    }
)
_RUN_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*\Z")
_NON_SOURCE_DIRECTORIES = frozenset({"01_draft", "02_ready", "09_archived", "000_draft", "099_archived", "_journal", "_projection"})


def _relative(value: object, *, label: str) -> Path:
    if not isinstance(value, str) or not value or "\x00" in value:
        raise LocalReleaseError(f"local-release-{label}-invalid")
    path = PurePosixPath(value)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        raise LocalReleaseError(f"local-release-{label}-invalid")
    return Path(*path.parts)


def _root(value: Path | str) -> Path:
    supplied = Path(value)
    try:
        root = supplied.resolve(strict=True)
    except OSError as error:
        raise LocalReleaseError("local-release-project-root-invalid") from error
    if supplied.is_symlink() or not root.is_dir() or root == Path(root.anchor):
        raise LocalReleaseError("local-release-project-root-invalid")
    return root


def _project_path(root: Path, relative: Path, *, label: str, require_exists: bool = False) -> Path:
    candidate = root / relative
    try:
        resolved = candidate.resolve(strict=require_exists)
        resolved.relative_to(root)
    except (OSError, ValueError) as error:
        raise LocalReleaseError(f"local-release-{label}-unsafe") from error
    current = root
    for component in relative.parts:
        current /= component
        if os.path.lexists(current) and current.is_symlink():
            raise LocalReleaseError(f"local-release-{label}-unsafe")
    return candidate


def _ignored(name: str) -> bool:
    return name == ".DS_Store" or name.startswith(".env") or name.endswith(".env")


def _walk_regular_files(root: Path, *, excluded_directories: frozenset[str] = frozenset(),
                        excluded_root_prefix: tuple[str, ...] = (),
                        excluded_root_directories: frozenset[str] = frozenset(),
                        excluded_root_files: frozenset[str] = frozenset()) -> list[Path]:
    def fail(error: OSError) -> None:
        raise LocalReleaseError("local-release-source-read-failed") from error

    collected: list[Path] = []
    for directory, directories, names in os.walk(root, followlinks=False, onerror=fail):
        base = Path(directory)
        directories[:] = [name for name in directories if not _ignored(name)
                          and name.casefold() not in excluded_directories
                          and (base != root or name.casefold() not in excluded_root_directories)
                          and (base != root or not excluded_root_prefix or not name.casefold().startswith(excluded_root_prefix))]
        for name in directories:
            child = base / name
            if child.is_symlink():
                raise LocalReleaseError("local-release-source-link-unsafe")
        for name in names:
            if _ignored(name) or (base == root and name in excluded_root_files):
                continue
            child = base / name
            try:
                mode = child.lstat().st_mode
            except OSError as error:
                raise LocalReleaseError("local-release-source-read-failed") from error
            if stat.S_ISLNK(mode) or not stat.S_ISREG(mode):
                raise LocalReleaseError("local-release-source-entry-unsafe")
            collected.append(child)
    return sorted(collected)


def _native_release_sources(selection) -> dict[Path, Path]:
    """Select Active Specs from the native Meta-ontology Component."""
    root, control = selection.root, selection.control_root
    ontology = control / "LAYER_1_META_ONTOLOGY_C9"
    selected, identities = {}, set()
    prefix = f"{selection.project_prefix}-S-"
    try:
        manifest = _project_path(root, selection.manifest_path.relative_to(root), label="manifest", require_exists=True)
        if _file_identity(manifest)[0] != selection.manifest_sha256:
            raise ValueError("Project Manifest changed")
        _project_path(root, ontology.relative_to(root), label="meta-ontology", require_exists=True)
        if not ontology.is_dir():
            raise ValueError("Meta-ontology Component is missing")
        members = _walk_regular_files(ontology, excluded_directories=_NON_SOURCE_DIRECTORIES)
        for path in members:
            if path.suffix != ".md" or not path.name.startswith(prefix):
                continue
            try:
                metadata, _ = read_atom_header(path.read_text(encoding="utf-8"))
            except (UnicodeError, ValueError, yaml.YAMLError) as error:
                raise ValueError(f"{path}: invalid Spec header") from error
            if metadata.get("atom_family") != "SPEC":
                raise ValueError(f"{path}: invalid Spec family")
            state = metadata.get("state")
            if not isinstance(state, dict) or not isinstance(state.get("status"), str):
                raise ValueError(f"{path}: missing Spec status")
            if state["status"] != "active":
                continue
            atom_id = metadata.get("atom_id")
            if (not isinstance(atom_id, str) or not re.fullmatch(rf"{re.escape(prefix)}[0-9]+", atom_id)
                    or atom_id in identities or not path.name.startswith(atom_id + "-")):
                raise ValueError(f"{path}: duplicate Current identity or mismatched Spec filename")
            identities.add(atom_id)
            selected[path.relative_to(control)] = path
        if not selected:
            raise ValueError("No Active Meta-ontology Specs were selected")
        return selected
    except (OSError, ValueError) as error:
        raise LocalReleaseError(f"local-release-native-sources-invalid: {error}") from error


def _clear_target(target: Path, *, root: Path, preserve: frozenset[str], label: str) -> None:
    if target == root or target.parent == target:
        raise LocalReleaseError(f"local-release-{label}-unsafe")
    if target.exists():
        if target.is_symlink() or not target.is_dir():
            raise LocalReleaseError(f"local-release-{label}-unsafe")
    else:
        target.mkdir(parents=True, exist_ok=False)
    for child in target.iterdir():
        if child.name in preserve or _ignored(child.name):
            continue
        _clear_owned(child, label=label)


def _clear_owned(path: Path, *, label: str) -> None:
    """Clear one owned entry while retaining ignored descendants unchanged."""

    try:
        mode = path.lstat().st_mode
    except OSError as error:
        raise LocalReleaseError(f"local-release-{label}-unsafe") from error
    if stat.S_ISLNK(mode):
        raise LocalReleaseError(f"local-release-{label}-unsafe")
    if stat.S_ISREG(mode):
        path.unlink()
        return
    if not stat.S_ISDIR(mode):
        raise LocalReleaseError(f"local-release-{label}-unsafe")
    for child in path.iterdir():
        if _ignored(child.name):
            continue
        _clear_owned(child, label=label)
    try:
        path.rmdir()
    except OSError:
        return


def _target(root: Path, relative: Path, *, label: str) -> Path:
    target = _project_path(root, relative, label=label)
    if target == root or target.parent == target or (target.parent == root and target.name.startswith((".anechoic_", "_anechoic_"))):
        raise LocalReleaseError("local-release-target-invalid")
    if target.exists() and (target.is_symlink() or not target.is_dir()):
        raise LocalReleaseError(f"local-release-{label}-unsafe")
    return target


def _copy_tree(source: Path, destination: Path, *, preserve: frozenset[str]) -> None:
    if source.is_symlink() or not source.is_dir() or destination.is_symlink() or not destination.is_dir():
        raise LocalReleaseError("local-release-copy-unsafe")
    for directory, directories, names in os.walk(source, followlinks=False):
        base = Path(directory)
        relative_directory = base.relative_to(source)
        directories[:] = [
            name for name in directories if not _ignored(name) and not (base == source and name in preserve)
        ]
        for name in directories:
            if (base / name).is_symlink():
                raise LocalReleaseError("local-release-copy-unsafe")
        if relative_directory != Path("."):
            target_directory = destination / relative_directory
            if target_directory.exists() and target_directory.is_symlink():
                raise LocalReleaseError("local-release-copy-unsafe")
            target_directory.mkdir(parents=True, exist_ok=True)
            shutil.copystat(base, target_directory, follow_symlinks=False)
        for name in names:
            if _ignored(name):
                continue
            entry = base / name
            if entry.relative_to(source).parts[0] in preserve:
                continue
            try:
                mode = entry.lstat().st_mode
            except OSError as error:
                raise LocalReleaseError("local-release-copy-unsafe") from error
            if stat.S_ISLNK(mode) or not stat.S_ISREG(mode):
                raise LocalReleaseError("local-release-copy-unsafe")
            relative = entry.relative_to(source)
            target = destination / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists() and target.is_symlink():
                raise LocalReleaseError("local-release-copy-unsafe")
            shutil.copy2(entry, target)


def _file_identity(path: Path) -> tuple[str, int]:
    return hashlib.sha256(path.read_bytes()).hexdigest(), stat.S_IMODE(path.stat().st_mode)


def _verify_package(package: Path, expected: Mapping[str, tuple[str, int]], *,
                    preserve: frozenset[str] = frozenset()) -> None:
    actual = {entry.relative_to(package).as_posix(): _file_identity(entry)
              for entry in _walk_regular_files(package, excluded_root_directories=preserve,
                                                excluded_root_files=preserve)}
    if actual != expected:
        raise LocalReleaseError("local-release-package-verification-failed")


def _install_bootstrap(root: Path, package: Path, expected: Mapping[str, tuple[str, int]]) -> None:
    """Copy the verified restart script as data."""
    source = _project_path(root, (package / _BOOTSTRAP).relative_to(root), label="bootstrap-source")
    target = _project_path(root, Path(".anechoic_runtime/start_mcp.py"), label="bootstrap-target")
    if target.exists() and not target.is_file():
        raise LocalReleaseError("local-release-bootstrap-target-unsafe")
    digest, mode = expected[_BOOTSTRAP.as_posix()]
    if not source.is_file() or not mode & 0o111 or _file_identity(source) != (digest, mode):
        raise LocalReleaseError("local-release-bootstrap-source-invalid")
    with tempfile.NamedTemporaryFile(dir=target.parent, prefix=".start-mcp-", delete=False) as output:
        temporary = Path(output.name)
    try:
        shutil.copy2(source, temporary)
        if _file_identity(temporary) != (digest, mode):
            raise LocalReleaseError("local-release-bootstrap-source-changed")
        os.replace(temporary, target)
    finally:
        temporary.unlink(missing_ok=True)


def _prepare_package(root: Path, product: Path, package: Path, *,
                     control_relative: Path) -> dict[str, tuple[str, int]]:
    if (len(control_relative.parts) != 1
            or not control_relative.name.startswith((".anechoic_", "_anechoic_"))):
        raise LocalReleaseError("local-release-project-selection-invalid")
    control_root = _project_path(root, control_relative, label="control-root", require_exists=True)
    if not control_root.is_dir():
        raise LocalReleaseError("local-release-project-selection-invalid")
    excluded = frozenset({control_relative.name.casefold(), ".anechoic_runtime", ".anechoic_tmp", ".runtime", ".git", ".pytest_cache", "__pycache__", ".mypy_cache", ".ruff_cache", ".venv", ".vite", "node_modules"})
    trees = (
        (root, Path(".")),
        (product / "SUPERLAYER_1_METHODOLOGY_SOURCES", Path("METHODOLOGY/sources")),
        (root / "LAYER_3_ENGINE_STUDIO_C14/FEATURE_AGENTIC/FEATURE_SKILLS/ane", Path("SKILLS/ane")),
    )
    sources: list[tuple[Path, Path]] = []
    inventories: list[tuple[Path, list[Path]]] = []
    for source, destination in trees:
        if source.is_symlink() or not source.is_dir():
            raise LocalReleaseError("local-release-package-source-unavailable")
        members = _walk_regular_files(source, excluded_directories=excluded,
                                      excluded_root_prefix=(".anechoic_", "_anechoic_") if source == root else (),
                                      excluded_root_directories=frozenset({".anechoic_install"}) if source == root else frozenset())
        if not members:
            raise LocalReleaseError("local-release-package-source-unavailable")
        inventories.append((source, members))
        (package / destination).mkdir(parents=True, exist_ok=True)
        sources.extend((entry, destination / entry.relative_to(source)) for entry in members
                       if (destination / entry.relative_to(source)).as_posix() not in RETIRED_ASSETS)
    expected = {}
    for source, relative in sources:
        expected[relative.as_posix()] = _file_identity(source)
        destination = package / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
    for source, members in inventories:
        current = _walk_regular_files(source, excluded_directories=excluded,
                                      excluded_root_prefix=(".anechoic_", "_anechoic_") if source == root else (),
                                      excluded_root_directories=frozenset({".anechoic_install"}) if source == root else frozenset())
        if current != members:
            raise LocalReleaseError("local-release-package-source-changed")
    for source, relative in sources:
        if _file_identity(source) != expected[relative.as_posix()]:
            raise LocalReleaseError("local-release-package-source-changed")
    for relative in (
        "pyproject.toml", "uv.lock", "version.toml",
        "SKILLS/ane/SKILL.md",
        "LAYER_3_ENGINE_STUDIO_C14/FEATURE_AGENTIC/FEATURE_SKILLS/ane/SKILL.md",
        _BOOTSTRAP.as_posix(),
        *_GENERATED_ASSETS,
    ):
        if relative not in expected:
            raise LocalReleaseError("local-release-package-source-unavailable")
    _verify_package(package, expected)
    return expected


def _cleanup_staging(root: Path, staging: Path | None) -> str:
    if staging is None:
        return ""
    try:
        _clear_owned(staging, label="temporary-package")
    except (LocalReleaseError, OSError):
        pass
    return f"Retained temporary staging: `{staging.relative_to(root).as_posix()}`.\n" if os.path.lexists(staging) else ""


def _image_manager(source: Path, temporary: Path | None = None, *, project_root: Path,
                   build_provenance: dict[str, str] | None = None):
    return ImageManager(source, project_root=project_root, build_temp_root=temporary, build_provenance=build_provenance)


def _launcher_image(selection) -> str | None:
    """Read only this selected instance's observation; never scan legacy state."""
    try:
        record = _project_path(selection.root, selection.launcher_state.relative_to(selection.root) / "last_launch.json",
                               label="project-launch-state")
        if not record.is_file():
            return None
        payload = json.loads(record.read_text(encoding="utf-8"))
        image = payload.get("image_id") if isinstance(payload, dict) else None
        if (isinstance(payload, dict) and payload.get("project_root") == str(selection.root)
                and payload.get("control_root") == str(selection.control_root)
                and payload.get("project_id") == selection.instance_id
                and isinstance(image, str) and re.fullmatch(r"sha256:[0-9a-f]{64}", image)):
            return image
    except (LocalReleaseError, OSError, UnicodeDecodeError, json.JSONDecodeError):
        pass
    return None


def _build_predecessor(selection) -> str | None:
    try:
        history = _project_path(
            selection.root, Path(".anechoic_runtime/simple_local_release/ready-images.json"),
            label="simple-image-history",
        )
        images = read_ready_images(history, selection.instance_id)
        if images:
            return images[0]
        _project_path(selection.root, selection.launcher_state.relative_to(selection.root) / "ready.json",
                      label="project-launch-state")
        return ready_predecessor(selection)
    except (OSError, ValueError, AttributeError) as error:
        raise LocalReleaseError("local-release-predecessor-receipt-invalid") from error


def _read_version(root: Path) -> tuple[Path, str]:
    version_path = _project_path(root, Path("version.toml"), label="version-path", require_exists=True)
    if not version_path.is_file():
        raise LocalReleaseError("local-release-version-invalid")
    try:
        version_text = version_path.read_text(encoding="utf-8")
        version = tomllib.loads(version_text)["framework"]["version"]
    except (OSError, KeyError, TypeError, UnicodeDecodeError, tomllib.TOMLDecodeError) as error:
        raise LocalReleaseError("local-release-version-invalid") from error
    match = re.fullmatch(r"([0-9]+)\.([0-9]+)\.([0-9]+)(?:\.([0-9]+))?", version) if isinstance(version, str) else None
    if match is None:
        raise LocalReleaseError("local-release-version-invalid")
    next_version = ".".join((*match.groups()[:3], str(int(match.group(4) or "0") + 1)))
    return version_path, version_text.replace(f'"{version}"', f'"{next_version}"', 1)


def _failed_test_output(
    root: Path,
    run_id: str,
    result: Any,
    *,
    log_path: str | None = None,
    named_temporary_file: Any = tempfile.NamedTemporaryFile,
) -> str:
    """Retain complete failed-suite output separately from the bounded report."""
    streams = {name: str(getattr(result, name, "") or "") for name in ("stdout", "stderr")}
    if log_path is not None:
        return f"Complete test output: `{log_path}`\n{streams['stdout'][-8000:]}"
    try:
        temporary = _target(root, Path(".anechoic_tmp/simple_local_release"), label="test-log")
        temporary.mkdir(parents=True, exist_ok=True)
        with named_temporary_file(
            mode="w", encoding="utf-8", prefix=f"{run_id}-tests-", suffix=".log",
            dir=temporary, delete=False,
        ) as log:
            log.write("\n".join(f"{name}:\n{value}" for name, value in streams.items()))
            location = Path(log.name).relative_to(root).as_posix()
        note = f"Complete test output: `{location}`"
    except (LocalReleaseError, OSError) as error:
        note = f"Complete test output could not be saved ({type(error).__name__})"
    detail = "\n".join(f"{name}:\n{value[-4000:]}" for name, value in streams.items())
    return f"{note}\n{detail}"
