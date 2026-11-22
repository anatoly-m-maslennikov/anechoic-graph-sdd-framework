
"""Filesystem and package support for the direct local-release runner."""

from __future__ import annotations

import json
import os
import re
import shutil
import tempfile
import tomllib
from pathlib import Path
from typing import Any

import yaml

from .release_assets import LocalReleaseError
from .release_cleanup_images import read_ready_images
from .release_images import ImageManager, RETIRED_ASSETS, TOOL_REGISTRY, ready_predecessor
from .release_inputs import read_atom_header
from .release_package_files import (
    _relative as _relative, _root as _root, _project_path, _ignored as _ignored, _walk_regular_files,
    _clear_target as _clear_target, _clear_owned, _target, _copy_tree as _copy_tree, _file_identity,
    _verify_package, _install_bootstrap as _install_bootstrap,
)


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


def _package_sources(root: Path, product: Path, package: Path, excluded: frozenset[str]):
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
    return sources, inventories


def _prepare_package(root: Path, product: Path, package: Path, *,
                     control_relative: Path) -> dict[str, tuple[str, int]]:
    if (len(control_relative.parts) != 1
            or not control_relative.name.startswith((".anechoic_", "_anechoic_"))):
        raise LocalReleaseError("local-release-project-selection-invalid")
    control_root = _project_path(root, control_relative, label="control-root", require_exists=True)
    if not control_root.is_dir():
        raise LocalReleaseError("local-release-project-selection-invalid")
    excluded = frozenset({control_relative.name.casefold(), ".anechoic_runtime", ".anechoic_tmp", ".runtime", ".git", ".pytest_cache", "__pycache__", ".mypy_cache", ".ruff_cache", ".venv", ".vite", "node_modules"})
    sources, inventories = _package_sources(root, product, package, excluded)
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
    child_inputs = tuple(
        f"{child}/{name}"
        for child in ("LAYER_3_ENGINE_STUDIO_C14", "LAYER_5_FRAMEWORK_DELIVERY", "RUNTIME_SETUP")
        for name in ("pyproject.toml", "uv.lock")
    )
    for relative in (
        "version.toml", *child_inputs,
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
