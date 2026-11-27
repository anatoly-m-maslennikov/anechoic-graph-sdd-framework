
"""Filesystem and package support for the direct local-release runner."""

from __future__ import annotations

import json
import re
import shutil
import stat
import tempfile
from pathlib import Path
from typing import Any

import tomllib
from LAYER_1_RUNTIME_IMAGES_C81.LAYER_1_RUNTIME_IMAGES_C81__shared import (
    _LAYER_NAMES,
    RETIRED_ASSETS,
    TOOL_REGISTRY,
    LocalReleaseError,
    _file_identity,
    _ignored,
    _project_path,
    _target,
    _verify_package,
    _walk_regular_files,
    ready_predecessor,
)

from .release_cleanup_images import read_ready_images

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
_ROOT_PACKAGE_EXCLUDES = frozenset(
    {
        ".anechoic_install",
        *map(str.casefold, (_DEFAULT_PRODUCT, *_LAYER_NAMES)),
    }
)
_ROOT_PROJECT_GOAL = re.compile(r"[A-Z]+-S-[0-9]+-SPEC-PROJECT_GOAL--.+\.md")


def _walk_package_tree(root, source, product, excluded, tracked):
    if tracked is not None and source != product:
        return _tracked_package_tree(root, source, excluded, tracked)
    return _walk_regular_files(
        source,
        excluded_directories=excluded,
        excluded_root_prefix=(".anechoic_", "_anechoic_")
        if source == root
        else (),
        excluded_root_directories=_ROOT_PACKAGE_EXCLUDES
        if source == root
        else frozenset(),
        excluded_root_files=frozenset({".git"})
        if source == root
        else frozenset(),
    )


def _tracked_package_tree(root, source, excluded, tracked):
    prefix = source.relative_to(root)
    result = []
    for relative in sorted(tracked):
        if not relative.is_relative_to(prefix):
            continue
        parts = relative.relative_to(prefix).parts
        if not parts or any(_ignored(part) for part in parts):
            continue
        parents = tuple(part.casefold() for part in parts[:-1])
        if set(parents) & excluded:
            continue
        if source == root and (
            parts == (".git",)
            or (
                parents
                and (
                    parents[0] in _ROOT_PACKAGE_EXCLUDES
                    or parents[0].startswith((".anechoic_", "_anechoic_"))
                )
            )
        ):
            continue
        path = _project_path(
            root, relative, label="package-source", require_exists=True
        )
        if not stat.S_ISREG(path.lstat().st_mode):
            raise LocalReleaseError("local-release-package-source-unavailable")
        result.append(path)
    return result


def _package_sources(root, product, package, excluded, manifest_path, tracked):
    trees = (
        (root, Path(".")),
        (product, Path(".")),
        (
            root
            / "LAYER_4_ENGINE_STUDIO_C14/FEATURE_AGENTIC/FEATURE_SKILLS/ane",
            Path("SKILLS/ane"),
        ),
    )
    sources: list[tuple[Path, Path]] = []
    inventories: list[tuple[Path, list[Path]]] = []
    for source, destination in trees:
        if source.is_symlink() or not source.is_dir():
            raise LocalReleaseError("local-release-package-source-unavailable")
        members = _walk_package_tree(root, source, product, excluded, tracked)
        if not members:
            raise LocalReleaseError("local-release-package-source-unavailable")
        inventories.append((source, members))
        (package / destination).mkdir(parents=True, exist_ok=True)
        sources.extend(
            (entry, destination / entry.relative_to(source))
            for entry in members
            if entry != manifest_path
            and not (
                entry.parent == root
                and _ROOT_PROJECT_GOAL.fullmatch(entry.name)
            )
            and (destination / entry.relative_to(source)).as_posix()
            not in RETIRED_ASSETS
        )
    return sources, inventories


def _prepare_package(root: Path, product: Path, package: Path, *,
                     control_relative: Path, manifest_path: Path,
                     tracked: frozenset[Path] | None = None) -> dict[str, tuple[str, int]]:
    if (len(control_relative.parts) != 1
            or not control_relative.name.startswith((".anechoic_", "_anechoic_"))):
        raise LocalReleaseError("local-release-project-selection-invalid")
    control_root = _project_path(
        root, control_relative, label="control-root", require_exists=True
    )
    if not control_root.is_dir():
        raise LocalReleaseError("local-release-project-selection-invalid")
    excluded = frozenset({control_relative.name.casefold(), ".anechoic_runtime", ".anechoic_tmp", ".runtime", ".git", ".pytest_cache", "__pycache__", ".mypy_cache", ".ruff_cache", ".venv", ".vite", "node_modules"})
    sources, inventories = _package_sources(
        root, product, package, excluded, manifest_path, tracked
    )
    expected = {}
    for source, relative in sources:
        expected[relative.as_posix()] = _file_identity(source)
        destination = package / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
    for source, members in inventories:
        current = _walk_package_tree(root, source, product, excluded, tracked)
        if current != members:
            raise LocalReleaseError("local-release-package-source-changed")
    for source, relative in sources:
        if _file_identity(source) != expected[relative.as_posix()]:
            raise LocalReleaseError("local-release-package-source-changed")
    child_inputs = tuple(
        f"{child}/{name}"
        for child in ("LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72/engine", "LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72/release", "LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72/setup")
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


def _launcher_image(selection) -> str | None:
    """Read only this selected instance's observation; never scan legacy state."""
    try:
        record = _project_path(
            selection.root,
            selection.launcher_state.relative_to(selection.root)
            / "last_launch.json",
            label="project-launch-state",
        )
        if not record.is_file():
            return None
        payload = json.loads(record.read_text(encoding="utf-8"))
        image = payload.get("image_id") if isinstance(payload, dict) else None
        if (
            isinstance(payload, dict)
            and payload.get("project_root") == str(selection.root)
            and payload.get("control_root") == str(selection.control_root)
            and payload.get("project_id") == selection.instance_id
            and isinstance(image, str)
            and re.fullmatch(r"sha256:[0-9a-f]{64}", image)
        ):
            return image
    except (
        LocalReleaseError,
        OSError,
        UnicodeDecodeError,
        json.JSONDecodeError,
    ):
        pass
    return None


def _build_predecessor(selection) -> str | None:
    try:
        history = _project_path(
            selection.root,
            Path(".anechoic_runtime/simple_local_release/ready-images.json"),
            label="simple-image-history",
        )
        images = read_ready_images(history, selection.instance_id)
        if images:
            return images[0]
        _project_path(
            selection.root,
            selection.launcher_state.relative_to(selection.root)
            / "ready.json",
            label="project-launch-state",
        )
        return ready_predecessor(selection)
    except (OSError, ValueError, AttributeError) as error:
        raise LocalReleaseError(
            "local-release-predecessor-receipt-invalid"
        ) from error


def _read_version(
    root: Path, *, installed_version: str = ""
) -> tuple[Path, str]:
    version_path = _project_path(
        root, Path("version.toml"), label="version-path", require_exists=True
    )
    if not version_path.is_file():
        raise LocalReleaseError("local-release-version-invalid")
    try:
        version_text = version_path.read_text(encoding="utf-8")
        version = tomllib.loads(version_text)["framework"]["version"]
    except (
        OSError,
        KeyError,
        TypeError,
        UnicodeDecodeError,
        tomllib.TOMLDecodeError,
    ) as error:
        raise LocalReleaseError("local-release-version-invalid") from error
    match = (
        re.fullmatch(r"([0-9]+)\.([0-9]+)\.([0-9]+)(?:\.([0-9]+))?", version)
        if isinstance(version, str)
        else None
    )
    if match is None:
        raise LocalReleaseError("local-release-version-invalid")
    parts = (*map(int, match.groups()[:3]), int(match.group(4) or "0"))
    if installed_version:
        installed = tuple(map(int, installed_version.split(".")))
        parts = max(
            parts, (*installed, 0) if len(installed) == 3 else installed
        )
    next_version = ".".join(map(str, (*parts[:3], parts[3] + 1)))
    return version_path, version_text.replace(
        f'"{version}"', f'"{next_version}"', 1
    )


def _failed_test_output(
    root: Path,
    run_id: str,
    result: Any,
    *,
    log_path: str | None = None,
    named_temporary_file: Any = tempfile.NamedTemporaryFile,
) -> str:
    """Retain complete failed-suite output separately from the bounded report."""
    streams = {
        name: str(getattr(result, name, "") or "")
        for name in ("stdout", "stderr")
    }
    if log_path is not None:
        return (
            f"Complete test output: `{log_path}`\n{streams['stdout'][-8000:]}"
        )
    try:
        temporary = _target(
            root, Path(".anechoic_tmp/simple_local_release"), label="test-log"
        )
        temporary.mkdir(parents=True, exist_ok=True)
        with named_temporary_file(
            mode="w",
            encoding="utf-8",
            prefix=f"{run_id}-tests-",
            suffix=".log",
            dir=temporary,
            delete=False,
        ) as log:
            log.write(
                "\n".join(
                    f"{name}:\n{value}" for name, value in streams.items()
                )
            )
            location = Path(log.name).relative_to(root).as_posix()
        note = f"Complete test output: `{location}`"
    except (LocalReleaseError, OSError) as error:
        note = (
            f"Complete test output could not be saved ({type(error).__name__})"
        )
    detail = "\n".join(
        f"{name}:\n{value[-4000:]}" for name, value in streams.items()
    )
    return f"{note}\n{detail}"
