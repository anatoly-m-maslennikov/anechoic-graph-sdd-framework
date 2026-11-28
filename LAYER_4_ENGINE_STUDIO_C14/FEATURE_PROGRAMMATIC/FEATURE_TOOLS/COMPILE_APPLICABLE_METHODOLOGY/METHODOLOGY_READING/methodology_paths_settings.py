"""Private helpers for Methodology paths."""

from __future__ import annotations

import tomllib
from collections.abc import Mapping
from pathlib import Path

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.settings.settings__shared import (
    read_settings_carrier,
)
from .methodology_conflicts import sha256_bytes
from .methodology_paths_sources import MethodologyPaths, source_layer_paths
from .methodology_source_parsing import CompileError


DEFAULT_SETTINGS_NAME = "anechoic_framework_default_settings.toml"
INSTANCE_SETTINGS_RELATIVE = Path(
    "000_ANECHOIC_framework/anechoic_framework_settings.toml"
)


def parse_toml(path: Path, code: str) -> dict[str, object]:
    try:
        value = read_settings_carrier(path)
    except (OSError, UnicodeDecodeError, tomllib.TOMLDecodeError) as error:
        raise CompileError(
            code,
            "Framework Settings must be valid UTF-8 TOML",
            path=path.as_posix(),
        ) from error
    if not isinstance(value, dict):
        raise CompileError(
            code,
            "Framework Settings must decode to a table",
            path=path.as_posix(),
        )
    return value


def framework_settings_carriers(
    root: Path, places: MethodologyPaths
) -> tuple[Path, Path]:
    "Return the default and one D359-authoritative instance Settings Carriers."
    layers = source_layer_paths(root, places)
    return (
        root / layers["CORE_META_MODEL"] / DEFAULT_SETTINGS_NAME,
        root / places.control_root / INSTANCE_SETTINGS_RELATIVE,
    )


def safe_framework_settings_carrier(root: Path, path: Path) -> bool:
    "Return whether an optional carrier is present, refusing symlink escapes."
    try:
        relative = path.relative_to(root)
    except ValueError as error:
        raise CompileError(
            "framework-settings-invalid",
            "Framework Settings Carrier escapes the Project",
            path=path.as_posix(),
        ) from error
    ancestor = root
    for part in relative.parts:
        ancestor /= part
        if ancestor.is_symlink():
            raise CompileError(
                "framework-settings-invalid",
                "Framework Settings Carrier cannot be a symlink "
                "or have a symlink ancestor",
                path=repo_relative(root, path),
            )
    if not path.exists():
        return False
    if not path.is_file():
        raise CompileError(
            "framework-settings-invalid",
            "Framework Settings Carrier must be a regular file",
            path=repo_relative(root, path),
        )
    return True


def framework_settings(
    root: Path, places: MethodologyPaths
) -> tuple[dict[str, object], dict[str, str]]:
    """Read only governed settings Carriers, retaining their byte bindings."""
    merged: dict[str, object] = {}
    bindings: dict[str, str] = {}
    for path in framework_settings_carriers(root, places):
        if not safe_framework_settings_carrier(root, path):
            continue
        raw = path.read_bytes()
        parsed = parse_toml(path, "framework-settings-invalid")
        merged.update(parsed)
        bindings[repo_relative(root, path)] = sha256_bytes(raw)
    return (merged, bindings)


def _extension_records(section):
    records: list[tuple[str | None, Mapping[str, object]]] = []
    if isinstance(section, Mapping):
        for identity, value in section.items():
            if isinstance(value, Mapping):
                records.append((str(identity), value))
    elif isinstance(section, list):
        for value in section:
            if isinstance(value, Mapping):
                identity = value.get(
                    "id", value.get("extension_id", value.get("name"))
                )
                records.append(
                    (identity if isinstance(identity, str) else None, value)
                )
    return records


def extension_selections(settings: Mapping[str, object]) -> dict[str, str]:
    """Return explicit enabled Extension identity/revision selections.

    Accept two TOML table forms; never infer activation from installation or
    retained configuration. Source authority fixes enabled plus revision.
    """
    selections: dict[str, str] = {}
    raw_sections = [
        settings.get(name)
        for name in (
            "extensions",
            "installed_extensions",
            "extension_selections",
        )
    ]
    for section in raw_sections:
        for fallback_identity, record in _extension_records(section):
            enabled = record.get("enabled", record.get("active"))
            identity = record.get(
                "id", record.get("extension_id", fallback_identity)
            )
            revision = record.get("revision", record.get("selected_revision"))
            if enabled is not True:
                continue
            if (
                not isinstance(identity, str)
                or not identity
                or (not isinstance(revision, (str, int)))
                or (not str(revision))
            ):
                raise CompileError(
                    "extension-selection-invalid",
                    "Enabled Extension requires an identity "
                    "and selected revision",
                )
            chosen = str(revision)
            if identity in selections and selections[identity] != chosen:
                raise CompileError(
                    "extension-selection-ambiguous",
                    "Extension has more than one active selected revision",
                    extension_id=identity,
                )
            selections[identity] = chosen
    return dict(sorted(selections.items()))


def repo_relative(root: Path, path: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError as error:
        raise CompileError(
            "path-outside-project",
            "Carrier is outside the Project root",
            path=path.as_posix(),
        ) from error
