"""Private helpers for Methodology paths."""

from __future__ import annotations

import re
from collections.abc import Mapping
from pathlib import Path

import tomllib

from pydantic import ConfigDict
from pydantic.dataclasses import dataclass

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.settings.project.project__shared import (
    ProjectSelectionError,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.settings.settings__shared import (
    read_settings_carrier,
)
from .methodology_candidate import DEFAULT_CONTROL_ROOT, OUTPUT_RELATIVE
from .methodology_source_parsing import CompileError
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.FEATURE_TOOLS__shared import (
    SETTINGS_PATH,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.\
    PROJECT_SUPPORT.PROJECT_SELECTION.\
    PROJECT_SELECTION__shared import (
    active_selection,
)


SOURCE_RELATIVE = OUTPUT_RELATIVE / "000_APPLICABLE_MTHD_sources"
LAYERS = (
    ("CORE_META_MODEL", 0, True),
    ("INSTALLED_EXTENSIONS", 1, True),
    ("PROJECT_CONFIGURATION", 2, True),
)


@dataclass(
    config=ConfigDict(strict=True, extra="forbid", hide_input_in_errors=True),
    frozen=True,
)
class MethodologyPaths:
    source: Path = SOURCE_RELATIVE
    output: Path = OUTPUT_RELATIVE
    declaration_digest: str | None = None
    control_root: Path = DEFAULT_CONTROL_ROOT


def configured_control_root(root: Path) -> Path:
    """Resolve the one Project-local control root from Project Settings."""
    settings_path = root / SETTINGS_PATH
    if not settings_path.is_file() or settings_path.is_symlink():
        raise CompileError(
            "project-settings-missing",
            "Project Settings Carrier is required",
            path=SETTINGS_PATH.as_posix(),
        )
    try:
        settings = read_settings_carrier(settings_path)
    except (OSError, UnicodeDecodeError, tomllib.TOMLDecodeError) as error:
        raise CompileError(
            "project-settings-invalid",
            "Project Settings Carrier must be valid UTF-8 TOML",
            path=SETTINGS_PATH.as_posix(),
        ) from error
    value = (
        settings.get("paths", {}).get("control_root")
        if isinstance(settings.get("paths"), dict)
        else None
    )
    if not isinstance(value, str) or not value:
        raise CompileError(
            "project-control-root-missing",
            "Project Settings requires paths.control_root",
        )
    control = Path(value)
    if (
        control.is_absolute()
        or ".." in control.parts
        or control == Path(".")
        or not (root / control).resolve().is_relative_to(root.resolve())
    ):
        raise CompileError(
            "project-control-root-invalid",
            "paths.control_root must be a safe repository-relative path",
            value=value,
        )
    return control


def _methodology_source_unit(selection):
    declared = selection.structure.get("scope_units")
    if isinstance(declared, Mapping):
        units = [declared.get("METHODOLOGY_SOURCES")]
    elif isinstance(declared, (list, tuple)):
        units = [
            row
            for row in declared
            if isinstance(row, Mapping)
            and row.get("scope_unit_name") == "METHODOLOGY_SOURCES"
        ]
    else:
        raise CompileError(
            "scope-declarations-invalid",
            "Scope Unit Declarations must derive Scope Unit rows",
        )
    if len(units) != 1:
        raise CompileError(
            "source-unit-cardinality",
            "Scope Unit Declarations must declare exactly one "
            "METHODOLOGY_SOURCES unit",
        )
    unit = units[0]
    if not isinstance(unit, Mapping):
        raise CompileError(
            "source-unit-cardinality",
            "Scope Unit Declarations must declare exactly one "
            "METHODOLOGY_SOURCES unit",
        )
    return unit


def _methodology_places(unit):
    value = unit.get("authority_path")
    if not isinstance(value, str) or not value:
        raise CompileError(
            "source-unit-place-missing",
            "Methodology source unit has no declared authority place",
            property="authority_path",
        )
    source = Path(value)
    if source.is_absolute() or ".." in source.parts or source == Path("."):
        raise CompileError(
            "source-unit-place-invalid",
            "Methodology source place must be repository-relative",
            property="authority_path",
        )
    output_value = unit.get("delivery_path")
    if not isinstance(output_value, str) or not output_value:
        raise CompileError(
            "output-unit-place-invalid",
            "Methodology delivery place must be a non-empty "
            "repository-relative path",
            property="delivery_path",
        )
    output = Path(output_value)
    if output.is_absolute() or ".." in output.parts or output == Path("."):
        raise CompileError(
            "output-unit-place-invalid",
            "Methodology delivery place must be repository-relative",
            property="delivery_path",
        )
    return (source, output)


def _validated_pins(raw_pins):
    pins: dict[str, str] = {}
    for path, pin in raw_pins.items():
        if not isinstance(path, str) or not isinstance(pin, Mapping):
            raise CompileError(
                "scope-declarations-invalid",
                "Scope Unit Declaration frontier pins are invalid",
            )
        sha256 = pin.get("sha256")
        if not isinstance(sha256, str) or not re.fullmatch(
            "[0-9a-f]{64}", sha256
        ):
            raise CompileError(
                "scope-declarations-invalid",
                "Scope Unit Declaration frontier pins are invalid",
                path=path,
            )
        pins[path] = sha256
    return dict(sorted(pins.items()))


def declaration_source_pins(
    root: Path, places: MethodologyPaths
) -> dict[str, str]:
    "Return the current declaration-Atom frontier as path-to-byte-digest pins."
    if configured_control_root(root) != places.control_root:
        raise CompileError(
            "source-frontier-changed",
            "Project control root changed after declaration discovery",
        )
    try:
        selection = active_selection(root)
    except ProjectSelectionError as error:
        raise CompileError(
            "scope-declarations-invalid",
            "Cannot read Scope Unit Declaration frontier",
        ) from error
    if selection.control_relative != places.control_root:
        raise CompileError(
            "source-frontier-changed",
            "Project control root changed after declaration discovery",
        )
    digest = getattr(selection, "declaration_digest", None)
    raw_pins = getattr(selection, "declaration_source_pins", None)
    if digest != places.declaration_digest or not isinstance(
        raw_pins, Mapping
    ):
        raise CompileError(
            "source-frontier-changed",
            "Scope Unit Declaration frontier changed after discovery",
        )
    return _validated_pins(raw_pins)


def _source_layer_authorities(names, by_name, places):
    paths: dict[str, Path] = {}
    for name in names:
        row = by_name[name]
        value = row.get("authority_path")
        path = Path(value) if isinstance(value, str) else None
        if (
            path is None
            or path.is_absolute()
            or ".." in path.parts
            or (path == Path("."))
        ):
            raise CompileError(
                "source-layer-authority-invalid",
                "Source Layer authority path is unsafe",
                scope_unit_name=name,
            )
        if path.parent != places.source:
            raise CompileError(
                "source-layer-authority-invalid",
                "Source Layer authority must be an immediate child of "
                "METHODOLOGY_SOURCES",
                scope_unit_name=name,
                authority_path=path.as_posix(),
            )
        paths[name] = path
    return paths


def source_layer_paths(
    root: Path, places: MethodologyPaths
) -> dict[str, Path]:
    "Resolve the three physical source-layer roots from current declarations."
    if configured_control_root(root) != places.control_root:
        raise CompileError(
            "source-frontier-changed",
            "Project control root changed after declaration discovery",
        )
    try:
        selection = active_selection(root)
    except ProjectSelectionError as error:
        raise CompileError(
            "scope-declarations-invalid",
            "Cannot read Source Layer declarations",
        ) from error
    if selection.control_relative != places.control_root:
        raise CompileError(
            "source-frontier-changed",
            "Project control root changed after declaration discovery",
        )
    if selection.declaration_digest != places.declaration_digest:
        raise CompileError(
            "source-frontier-changed",
            "Scope Unit Declaration frontier changed after discovery",
        )
    rows = selection.structure.get("scope_units")
    if not isinstance(rows, (list, tuple)):
        raise CompileError(
            "scope-declarations-invalid",
            "Scope Unit Declarations must derive source-layer rows",
        )
    return _declared_layer_paths(rows, places)


def _declared_layer_paths(rows, places):
    by_name = {
        row.get("scope_unit_name"): row
        for row in rows
        if isinstance(row, Mapping)
        and isinstance(row.get("scope_unit_name"), str)
    }
    names = [name for name, _, _ in LAYERS]
    if any((name not in by_name for name in names)):
        raise CompileError(
            "source-layer-declaration-missing",
            "Scope Unit Declarations must declare every "
            "Methodology Source Layer",
        )
    paths = _source_layer_authorities(names, by_name, places)
    if len({path.name for path in paths.values()}) != len(paths):
        raise CompileError(
            "source-layer-authority-invalid",
            "Source Layer authorities must have distinct physical paths",
        )
    return paths
