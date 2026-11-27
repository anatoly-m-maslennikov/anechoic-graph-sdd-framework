"""Resolve Methodology source, settings and declaration frontiers."""

from __future__ import annotations

import re
from collections.abc import Mapping
from pathlib import Path

import tomllib
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
    ProjectSelectionError,
    read_settings_carrier,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.COMPILE_APPLICABLE_METHODOLOGY.methodology_candidate import (
    DEFAULT_CONTROL_ROOT,
    OUTPUT_RELATIVE,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.COMPILE_APPLICABLE_METHODOLOGY.methodology_conflicts import (
    sha256_bytes,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.COMPILE_APPLICABLE_METHODOLOGY.methodology_source_parsing import (
    CompileError,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.FEATURE_TOOLS__shared import (
    SETTINGS_PATH,
    active_selection,
)
from pydantic import ConfigDict
from pydantic.dataclasses import dataclass

SOURCE_RELATIVE = OUTPUT_RELATIVE / "000_APPLICABLE_MTHD_sources"
LAYERS = (("CORE_META_MODEL", 0, True), ("INSTALLED_EXTENSIONS", 1, True), ("PROJECT_CONFIGURATION", 2, True))

ROLES = (("REQUIREMENT", "04_requirement"), ("METHOD", "05_method"),
         ("EVALUATION", "06_evaluation"), ("DELIVERY", "07_delivery"), ("OPERATIONS", "09_operations"))

ROLE_BY_DIRECTORY = {directory: role for role, directory in ROLES}
ROLE_ORDER = {directory: index for index, (_, directory) in enumerate(ROLES)}
IGNORED_INSTALLED_EXTENSION_FILES = {".gitkeep"}
RELATION_KINDS = {"replacement": {"replacement_of", "replaces"},
                  "incompatible": {"incompatible_with", "incompatibility_with"}}
DEFAULT_SETTINGS_NAME = "anechoic_framework_default_settings.toml"
INSTANCE_SETTINGS_RELATIVE = Path("000_ANECHOIC_framework/anechoic_framework_settings.toml")

@dataclass(config=ConfigDict(strict=True, extra="forbid", hide_input_in_errors=True), frozen=True)
class MethodologyPaths:
    source: Path = SOURCE_RELATIVE
    output: Path = OUTPUT_RELATIVE
    declaration_digest: str | None = None
    control_root: Path = DEFAULT_CONTROL_ROOT

def configured_control_root(root: Path) -> Path:
    """Resolve the one Project-local control root from Project Settings."""
    settings_path = root / SETTINGS_PATH
    if not settings_path.is_file() or settings_path.is_symlink():
        raise CompileError("project-settings-missing", "Project Settings Carrier is required", path=SETTINGS_PATH.as_posix())
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
        raise CompileError("project-control-root-missing", "Project Settings requires paths.control_root")
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
        units = [row for row in declared if isinstance(row, Mapping) and row.get("scope_unit_name") == "METHODOLOGY_SOURCES"]
    else:
        raise CompileError("scope-declarations-invalid", "Scope Unit Declarations must derive Scope Unit rows")
    if len(units) != 1:
        raise CompileError("source-unit-cardinality", "Scope Unit Declarations must declare exactly one METHODOLOGY_SOURCES unit")
    unit = units[0]
    if not isinstance(unit, Mapping):
        raise CompileError("source-unit-cardinality", "Scope Unit Declarations must declare exactly one METHODOLOGY_SOURCES unit")
    return unit

def _methodology_places(unit):
    value = unit.get("authority_path")
    if not isinstance(value, str) or not value:
        raise CompileError("source-unit-place-missing", "Methodology source unit has no declared authority place", property="authority_path")
    source = Path(value)
    if source.is_absolute() or ".." in source.parts or source == Path("."):
        raise CompileError("source-unit-place-invalid", "Methodology source place must be repository-relative", property="authority_path")
    output_value = unit.get("delivery_path")
    if not isinstance(output_value, str) or not output_value:
        raise CompileError("output-unit-place-invalid", "Methodology delivery place must be a non-empty repository-relative path", property="delivery_path")
    output = Path(output_value)
    if output.is_absolute() or ".." in output.parts or output == Path("."):
        raise CompileError("output-unit-place-invalid", "Methodology delivery place must be repository-relative", property="delivery_path")
    return source, output

def methodology_paths(root: Path) -> MethodologyPaths:
    """Resolve source and delivery places from current Scope Unit Declarations.

    Applicable Methodology defaults to the Project Framework folder, not ``_projection``.
    An explicit source-unit delivery binding remains authoritative.
    """
    control = configured_control_root(root)
    try:
        selection = active_selection(root)
    except ProjectSelectionError as error:
        raise CompileError("scope-declarations-invalid", "Cannot resolve methodology places from Scope Unit Declarations") from error
    if selection.control_relative != control:
        raise CompileError("project-control-root-invalid", "Project Settings disagree with selected Scope Unit Declarations")
    unit = _methodology_source_unit(selection)
    source, output = _methodology_places(unit)
    source_place = (root / source).resolve()
    output_place = (root / output).resolve()
    if not source_place.is_relative_to(root.resolve()):
        raise CompileError("source-unit-place-invalid", "Methodology source place resolves outside the Project", property="authority_path")
    if not output_place.is_relative_to(root.resolve()):
        raise CompileError("output-unit-place-invalid", "Methodology delivery place resolves outside the Project", property="delivery_path")
    if output_place.is_relative_to(source_place) or any(
        source_place.is_relative_to((output_place / role_directory).resolve()) for _, role_directory in ROLES
    ):
        raise CompileError("source-output-overlap", "Generated output cannot replace the authoritative source place")
    digest = getattr(selection, "declaration_digest", None)
    if not isinstance(digest, str) or not digest:
        raise CompileError("scope-declarations-invalid", "Scope Unit Declaration frontier has no digest")
    return MethodologyPaths(source, output, digest, control)

def declaration_source_pins(root: Path, places: MethodologyPaths) -> dict[str, str]:
    """Return the current declaration-Atom frontier as path-to-byte-digest pins."""
    if configured_control_root(root) != places.control_root:
        raise CompileError("source-frontier-changed", "Project control root changed after declaration discovery")
    try:
        selection = active_selection(root)
    except ProjectSelectionError as error:
        raise CompileError("scope-declarations-invalid", "Cannot read Scope Unit Declaration frontier") from error
    if selection.control_relative != places.control_root:
        raise CompileError("source-frontier-changed", "Project control root changed after declaration discovery")
    digest = getattr(selection, "declaration_digest", None)
    raw_pins = getattr(selection, "declaration_source_pins", None)
    if digest != places.declaration_digest or not isinstance(raw_pins, Mapping):
        raise CompileError("source-frontier-changed", "Scope Unit Declaration frontier changed after discovery")
    pins: dict[str, str] = {}
    for path, pin in raw_pins.items():
        if not isinstance(path, str) or not isinstance(pin, Mapping):
            raise CompileError("scope-declarations-invalid", "Scope Unit Declaration frontier pins are invalid")
        sha256 = pin.get("sha256")
        if not isinstance(sha256, str) or not re.fullmatch(r"[0-9a-f]{64}", sha256):
            raise CompileError("scope-declarations-invalid", "Scope Unit Declaration frontier pins are invalid", path=path)
        pins[path] = sha256
    return dict(sorted(pins.items()))

def _source_layer_authorities(names, by_name, places):
    paths: dict[str, Path] = {}
    for name in names:
        row = by_name[name]
        value = row.get("authority_path")
        path = Path(value) if isinstance(value, str) else None
        if path is None or path.is_absolute() or ".." in path.parts or path == Path("."):
            raise CompileError("source-layer-authority-invalid", "Source Layer authority path is unsafe", scope_unit_name=name)
        if path.parent != places.source:
            raise CompileError("source-layer-authority-invalid",
                "Source Layer authority must be an immediate child of METHODOLOGY_SOURCES",
                scope_unit_name=name, authority_path=path.as_posix())
        paths[name] = path
    return paths

def source_layer_paths(root: Path, places: MethodologyPaths) -> dict[str, Path]:
    """Resolve the three physical source-layer roots from current declarations."""
    if configured_control_root(root) != places.control_root:
        raise CompileError("source-frontier-changed", "Project control root changed after declaration discovery")
    try:
        selection = active_selection(root)
    except ProjectSelectionError as error:
        raise CompileError("scope-declarations-invalid", "Cannot read Source Layer declarations") from error
    if selection.control_relative != places.control_root:
        raise CompileError("source-frontier-changed", "Project control root changed after declaration discovery")
    if selection.declaration_digest != places.declaration_digest:
        raise CompileError("source-frontier-changed", "Scope Unit Declaration frontier changed after discovery")
    rows = selection.structure.get("scope_units")
    if not isinstance(rows, (list, tuple)):
        raise CompileError("scope-declarations-invalid", "Scope Unit Declarations must derive source-layer rows")
    by_name = {row.get("scope_unit_name"): row for row in rows
               if isinstance(row, Mapping) and isinstance(row.get("scope_unit_name"), str)}
    names = [name for name, _, _ in LAYERS]
    if any(name not in by_name for name in names):
        raise CompileError("source-layer-declaration-missing", "Scope Unit Declarations must declare every Methodology Source Layer")
    paths = _source_layer_authorities(names, by_name, places)
    if len({path.name for path in paths.values()}) != len(paths):
        raise CompileError("source-layer-authority-invalid", "Source Layer authorities must have distinct physical paths")
    return paths

def parse_toml(path: Path, code: str) -> dict[str, object]:
    try:
        value = read_settings_carrier(path)
    except (OSError, UnicodeDecodeError, tomllib.TOMLDecodeError) as error:
        raise CompileError(code, "Framework Settings must be valid UTF-8 TOML", path=path.as_posix()) from error
    if not isinstance(value, dict):
        raise CompileError(code, "Framework Settings must decode to a table", path=path.as_posix())
    return value

def framework_settings_carriers(root: Path, places: MethodologyPaths) -> tuple[Path, Path]:
    """Return the default and one D359-authoritative instance Settings Carriers."""
    layers = source_layer_paths(root, places)
    return (root / layers["CORE_META_MODEL"] / DEFAULT_SETTINGS_NAME,
            root / places.control_root / INSTANCE_SETTINGS_RELATIVE)

def safe_framework_settings_carrier(root: Path, path: Path) -> bool:
    """Return whether an optional carrier is present, refusing symlink escapes."""
    try:
        relative = path.relative_to(root)
    except ValueError as error:
        raise CompileError("framework-settings-invalid", "Framework Settings Carrier escapes the Project", path=path.as_posix()) from error
    ancestor = root
    for part in relative.parts:
        ancestor /= part
        if ancestor.is_symlink():
            raise CompileError("framework-settings-invalid", "Framework Settings Carrier cannot be a symlink or have a symlink ancestor", path=repo_relative(root, path))
    if not path.exists():
        return False
    if not path.is_file():
        raise CompileError("framework-settings-invalid", "Framework Settings Carrier must be a regular file", path=repo_relative(root, path))
    return True

def framework_settings(root: Path, places: MethodologyPaths) -> tuple[dict[str, object], dict[str, str]]:
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
    return merged, bindings

def _extension_records(section):
    records: list[tuple[str | None, Mapping[str, object]]] = []
    if isinstance(section, Mapping):
        for identity, value in section.items():
            if isinstance(value, Mapping):
                records.append((str(identity), value))
    elif isinstance(section, list):
        for value in section:
            if isinstance(value, Mapping):
                identity = value.get("id", value.get("extension_id", value.get("name")))
                records.append((identity if isinstance(identity, str) else None, value))
    return records

def extension_selections(settings: Mapping[str, object]) -> dict[str, str]:
    """Return explicit enabled Extension identity/revision selections.

    Accept two TOML table forms; never infer activation from installation or
    retained configuration. Source authority fixes enabled plus revision.
    """
    selections: dict[str, str] = {}
    raw_sections = [settings.get(name) for name in ("extensions", "installed_extensions", "extension_selections")]
    for section in raw_sections:
        records = _extension_records(section)
        for fallback_identity, record in records:
            enabled = record.get("enabled", record.get("active"))
            identity = record.get("id", record.get("extension_id", fallback_identity))
            revision = record.get("revision", record.get("selected_revision"))
            if enabled is not True:
                continue
            if not isinstance(identity, str) or not identity or not isinstance(revision, (str, int)) or not str(revision):
                raise CompileError("extension-selection-invalid", "Enabled Extension requires an identity and selected revision")
            rendered_revision = str(revision)
            if (
                identity in selections
                and selections[identity] != rendered_revision
            ):
                raise CompileError(
                    "extension-selection-ambiguous",
                    "Extension has more than one active selected revision",
                    extension_id=identity,
                )
            selections[identity] = rendered_revision
    return dict(sorted(selections.items()))

def source_state_snapshot(root: Path, places: MethodologyPaths | None = None) -> dict[str, str]:
    """Capture every governed source/settings byte so new input also invalidates staging."""
    places = places or methodology_paths(root)
    source_root = root / places.source
    if not source_root.is_dir():
        raise CompileError("source-root-missing", "Applicable Methodology source root is missing", path=places.source.as_posix())
    snapshot: dict[str, str] = {}
    for path in sorted(source_root.rglob("*")):
        if path.name == ".DS_Store" and path.is_file() and not path.is_symlink():
            continue
        if path.is_file() and not path.is_symlink():
            snapshot[repo_relative(root, path)] = sha256_bytes(path.read_bytes())
    snapshot.update(declaration_source_pins(root, places))
    project_settings = root / places.control_root / "anechoic_project_settings.toml"
    if project_settings.is_file() and not project_settings.is_symlink():
        snapshot[repo_relative(root, project_settings)] = sha256_bytes(project_settings.read_bytes())
    for settings_carrier in framework_settings_carriers(root, places):
        if safe_framework_settings_carrier(root, settings_carrier):
            snapshot[repo_relative(root, settings_carrier)] = sha256_bytes(settings_carrier.read_bytes())
    return snapshot

def repo_relative(root: Path, path: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError as error:
        raise CompileError("path-outside-project", "Carrier is outside the Project root", path=path.as_posix()) from error
