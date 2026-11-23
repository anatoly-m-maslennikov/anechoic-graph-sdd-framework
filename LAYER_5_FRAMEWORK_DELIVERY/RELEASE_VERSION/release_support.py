
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
_BOOTSTRAP = Path("LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/docker/start_mcp.py")

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
_LAYER_NAMES = ("LAYER_1_META_ONTOLOGY_C9", "LAYER_2_META_METHODOLOGY_C58")
_ROOT_PACKAGE_EXCLUDES = frozenset({".anechoic_install", *map(str.casefold, (_DEFAULT_PRODUCT, *_LAYER_NAMES))})
_ROOT_PROJECT_GOAL = re.compile(r"[A-Z]+-S-[0-9]+-SPEC-PROJECT_GOAL--.+\.md")
_NON_SOURCE_DIRECTORIES = frozenset({"01_draft", "02_ready", "09_archived", "000_draft", "099_archived", "_journal", "_projection"})
_DEFAULT_TIER_ONE_DIRECTORY = "01_TIER_1_ARCHITECTURE"


def _tier_one_directory(parameters):
    project = (parameters or {}).get("project", {})
    if not isinstance(project, dict) or "folder_layout" not in project:
        return _DEFAULT_TIER_ONE_DIRECTORY
    folders = project["folder_layout"]
    tiers = folders.get("active_spec_by_tier") if isinstance(folders, dict) else None
    if (not isinstance(tiers, dict) or tiers.keys() != {"0", "1", "2+"}
            or tiers["0"] != "." or tiers["2+"] != "_{lens}/{sublenses}"):
        raise ValueError("Invalid Active SPEC folders in Project Manifest")
    name = tiers["1"]
    if (not isinstance(name, str) or len(name) > 255 or not re.fullmatch(r"01_[A-Z][A-Z0-9_]*", name)
            or name.casefold() in _NON_SOURCE_DIRECTORIES or re.search(r"_C[0-9]+$", name)):
        raise ValueError("Invalid Tier 1 SPEC folder in Project Manifest")
    return name


def _release_candidates(root, control, tier_one):
    ontology, methodology = _LAYER_NAMES
    environments = "LAYER_3_ENVIRONMENTS_C72"
    scopes = [(control / ontology, ontology, None, control / ontology)]
    for name, component in ((methodology, None), (environments, "C72")):
        directory = control / name
        if os.path.lexists(directory):
            scopes.append((directory, methodology if component else name, component, directory))
    project_folders = (tier_one, "__DES", "__DEVOPS", "__QA", "__SWD")
    project_folders += tuple(path.name for path in control.iterdir()
                             if re.fullmatch(r"_[A-Z][A-Z0-9_]*", path.name) and path.name != "_PMETA")
    for name in dict.fromkeys(project_folders):
        directory = control / name
        if os.path.lexists(directory):
            scopes.append((directory, methodology, "C00", control))
    for directory, name, component, base in scopes:
        _project_path(root, directory.relative_to(root), label="delivery-source", require_exists=True)
        if not directory.is_dir():
            raise ValueError("Delivery source is not a directory")
        for path in _walk_regular_files(directory, excluded_directories=_NON_SOURCE_DIRECTORIES):
            yield path, name, component, base
    for path in control.iterdir():
        if path.is_file() or path.is_symlink():
            yield path, methodology, "C00", control


def _release_spec_header(path):
    if path.is_symlink():
        raise ValueError(f"{path}: unsafe Spec source")
    try:
        return read_atom_header(path.read_text(encoding="utf-8"))[0]
    except (UnicodeError, ValueError, yaml.YAMLError) as error:
        raise ValueError(f"{path}: invalid Spec header") from error


def _native_release_sources(selection) -> dict[Path, Path]:
    root, control = selection.root, selection.control_root
    selected, identities = {}, set()
    prefix = f"{selection.project_prefix}-S-"
    try:
        manifest = _project_path(root, selection.manifest_path.relative_to(root), label="manifest", require_exists=True)
        if _file_identity(manifest)[0] != selection.manifest_sha256:
            raise ValueError("Project Manifest changed")
        tier_one = _tier_one_directory(getattr(selection, "parameters", {}))
        for path, layer, component, base in _release_candidates(root, control, tier_one):
            if path.suffix != ".md" or not path.name.startswith(prefix):
                continue
            metadata = _release_spec_header(path)
            context = metadata.get("context", {})
            if component == "C00" and isinstance(context, dict) and context.get("template") in {
                "project_manifest", "project_goal", "component_manifest", "component_seed_manifest", "project_contract"
            }:
                continue
            if metadata.get("atom_family") != "SPEC":
                raise ValueError(f"{path}: invalid Spec family")
            if component is not None:
                container = metadata.get("container", {})
                if not isinstance(container, dict) or container.get("component") != component:
                    continue
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
            selected[Path(layer) / path.relative_to(base)] = path
        if not any(path.parts[0] == _LAYER_NAMES[0] for path in selected):
            raise ValueError("No Active Meta-ontology Specs were selected")
        return selected
    except (OSError, ValueError) as error:
        raise LocalReleaseError(f"local-release-native-sources-invalid: {error}") from error


def _package_sources(root: Path, product: Path, package: Path, excluded: frozenset[str], manifest_path: Path):
    trees = (
        (root, Path(".")),
        (product, Path(".")),
        (root / "LAYER_4_ENGINE_STUDIO_C14/FEATURE_AGENTIC/FEATURE_SKILLS/ane", Path("SKILLS/ane")),
    )
    sources: list[tuple[Path, Path]] = []
    inventories: list[tuple[Path, list[Path]]] = []
    for source, destination in trees:
        if source.is_symlink() or not source.is_dir():
            raise LocalReleaseError("local-release-package-source-unavailable")
        members = _walk_regular_files(source, excluded_directories=excluded,
                                      excluded_root_prefix=(".anechoic_", "_anechoic_") if source == root else (),
                                      excluded_root_directories=_ROOT_PACKAGE_EXCLUDES if source == root else frozenset())
        if not members:
            raise LocalReleaseError("local-release-package-source-unavailable")
        inventories.append((source, members))
        (package / destination).mkdir(parents=True, exist_ok=True)
        sources.extend((entry, destination / entry.relative_to(source)) for entry in members
                       if entry != manifest_path
                       and not (entry.parent == root and _ROOT_PROJECT_GOAL.fullmatch(entry.name))
                       and (destination / entry.relative_to(source)).as_posix() not in RETIRED_ASSETS)
    return sources, inventories


def _prepare_package(root: Path, product: Path, package: Path, *,
                     control_relative: Path, manifest_path: Path) -> dict[str, tuple[str, int]]:
    if (len(control_relative.parts) != 1
            or not control_relative.name.startswith((".anechoic_", "_anechoic_"))):
        raise LocalReleaseError("local-release-project-selection-invalid")
    control_root = _project_path(root, control_relative, label="control-root", require_exists=True)
    if not control_root.is_dir():
        raise LocalReleaseError("local-release-project-selection-invalid")
    excluded = frozenset({control_relative.name.casefold(), ".anechoic_runtime", ".anechoic_tmp", ".runtime", ".git", ".pytest_cache", "__pycache__", ".mypy_cache", ".ruff_cache", ".venv", ".vite", "node_modules"})
    sources, inventories = _package_sources(root, product, package, excluded, manifest_path)
    expected = {}
    for source, relative in sources:
        expected[relative.as_posix()] = _file_identity(source)
        destination = package / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
    for source, members in inventories:
        current = _walk_regular_files(source, excluded_directories=excluded,
                                      excluded_root_prefix=(".anechoic_", "_anechoic_") if source == root else (),
                                      excluded_root_directories=_ROOT_PACKAGE_EXCLUDES if source == root else frozenset())
        if current != members:
            raise LocalReleaseError("local-release-package-source-changed")
    for source, relative in sources:
        if _file_identity(source) != expected[relative.as_posix()]:
            raise LocalReleaseError("local-release-package-source-changed")
    child_inputs = tuple(
        f"{child}/{name}"
        for child in ("LAYER_3_ENVIRONMENTS_C72/engine", "LAYER_3_ENVIRONMENTS_C72/release", "LAYER_3_ENVIRONMENTS_C72/setup")
        for name in ("pyproject.toml", "uv.lock")
    )
    for relative in (
        "version.toml", *child_inputs,
        "SKILLS/ane/SKILL.md",
        "LAYER_4_ENGINE_STUDIO_C14/FEATURE_AGENTIC/FEATURE_SKILLS/ane/SKILL.md",
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
                   build_provenance: dict[str, str] | None = None, source_provider=None):
    return ImageManager(source, project_root=project_root, build_temp_root=temporary, build_provenance=build_provenance, source_provider=source_provider)


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
