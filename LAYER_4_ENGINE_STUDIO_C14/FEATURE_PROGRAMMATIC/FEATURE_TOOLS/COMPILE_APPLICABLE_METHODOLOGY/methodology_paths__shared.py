"""Resolve Methodology source, settings and declaration frontiers."""

from __future__ import annotations

from pathlib import Path

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.settings.project.project__shared import (
    ProjectSelectionError,
)
from .METHODOLOGY_READING.METHODOLOGY_READING__shared import (
    DEFAULT_CONTROL_ROOT as DEFAULT_CONTROL_ROOT,
    OUTPUT_RELATIVE as OUTPUT_RELATIVE,
)
from .METHODOLOGY_READING.METHODOLOGY_READING__shared import (
    sha256_bytes,
)
from .METHODOLOGY_READING.METHODOLOGY_READING__shared import (
    CompileError,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.FEATURE_TOOLS__shared import (
    SETTINGS_PATH as SETTINGS_PATH,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.\
    PROJECT_SUPPORT.PROJECT_SELECTION.\
    PROJECT_SELECTION__shared import (
    active_selection,
)
from .METHODOLOGY_READING.METHODOLOGY_READING__shared import (
    LAYERS as LAYERS,
    SOURCE_RELATIVE as SOURCE_RELATIVE,
    MethodologyPaths as MethodologyPaths,
    configured_control_root as configured_control_root,
    _methodology_places as _methodology_places,
    _methodology_source_unit as _methodology_source_unit,
    _source_layer_authorities as _source_layer_authorities,
    declaration_source_pins as declaration_source_pins,
    source_layer_paths as source_layer_paths,
)
from .METHODOLOGY_READING.METHODOLOGY_READING__shared import (
    DEFAULT_SETTINGS_NAME as DEFAULT_SETTINGS_NAME,
    INSTANCE_SETTINGS_RELATIVE as INSTANCE_SETTINGS_RELATIVE,
    _extension_records as _extension_records,
    extension_selections as extension_selections,
    framework_settings as framework_settings,
    framework_settings_carriers as framework_settings_carriers,
    parse_toml as parse_toml,
    repo_relative as repo_relative,
    safe_framework_settings_carrier as safe_framework_settings_carrier,
)

ROLES = (
    ("REQUIREMENT", "04_requirement"),
    ("METHOD", "05_method"),
    ("EVALUATION", "06_evaluation"),
    ("DELIVERY", "07_delivery"),
    ("OPERATIONS", "09_operations"),
)

ROLE_BY_DIRECTORY = {directory: role for role, directory in ROLES}
ROLE_ORDER = {directory: index for index, (_, directory) in enumerate(ROLES)}
IGNORED_INSTALLED_EXTENSION_FILES = {".gitkeep"}
RELATION_KINDS = {
    "replacement": {"replacement_of", "replaces"},
    "incompatible": {"incompatible_with", "incompatibility_with"},
}


def _validate_methodology_places(root: Path, source: Path, output: Path):
    source_place = (root / source).resolve()
    output_place = (root / output).resolve()
    if not source_place.is_relative_to(root.resolve()):
        raise CompileError(
            "source-unit-place-invalid",
            "Methodology source place resolves outside the Project",
            property="authority_path",
        )
    if not output_place.is_relative_to(root.resolve()):
        raise CompileError(
            "output-unit-place-invalid",
            "Methodology delivery place resolves outside the Project",
            property="delivery_path",
        )
    if output_place.is_relative_to(source_place) or any(
        source_place.is_relative_to((output_place / role_directory).resolve())
        for _, role_directory in ROLES
    ):
        raise CompileError(
            "source-output-overlap",
            "Generated output cannot replace the authoritative source place",
        )


def methodology_paths(root: Path) -> MethodologyPaths:
    """Resolve source and delivery places from current Scope Unit Declarations.

    Applicable Methodology defaults to the Project Framework folder, \
not ``_projection``.
    An explicit source-unit delivery binding remains authoritative.
    """
    control = configured_control_root(root)
    try:
        selection = active_selection(root)
    except ProjectSelectionError as error:
        raise CompileError(
            "scope-declarations-invalid",
            "Cannot resolve methodology places from Scope Unit Declarations",
        ) from error
    if selection.control_relative != control:
        raise CompileError(
            "project-control-root-invalid",
            "Project Settings disagree with selected Scope Unit Declarations",
        )
    unit = _methodology_source_unit(selection)
    source, output = _methodology_places(unit)
    _validate_methodology_places(root, source, output)
    digest = getattr(selection, "declaration_digest", None)
    if not isinstance(digest, str) or not digest:
        raise CompileError(
            "scope-declarations-invalid",
            "Scope Unit Declaration frontier has no digest",
        )
    return MethodologyPaths(source, output, digest, control)


def source_state_snapshot(
    root: Path, places: MethodologyPaths | None = None
) -> dict[str, str]:
    """Capture every governed source/settings byte so new input also \
invalidates staging."""
    places = places or methodology_paths(root)
    source_root = root / places.source
    if not source_root.is_dir():
        raise CompileError(
            "source-root-missing",
            "Applicable Methodology source root is missing",
            path=places.source.as_posix(),
        )
    snapshot: dict[str, str] = {}
    for path in sorted(source_root.rglob("*")):
        if (
            path.name == ".DS_Store"
            and path.is_file()
            and not path.is_symlink()
        ):
            continue
        if path.is_file() and not path.is_symlink():
            snapshot[repo_relative(root, path)] = sha256_bytes(
                path.read_bytes()
            )
    snapshot.update(declaration_source_pins(root, places))
    project_settings = (
        root / places.control_root / "anechoic_project_settings.toml"
    )
    if project_settings.is_file() and not project_settings.is_symlink():
        snapshot[repo_relative(root, project_settings)] = sha256_bytes(
            project_settings.read_bytes()
        )
    for settings_carrier in framework_settings_carriers(root, places):
        if safe_framework_settings_carrier(root, settings_carrier):
            snapshot[repo_relative(root, settings_carrier)] = sha256_bytes(
                settings_carrier.read_bytes()
            )
    return snapshot
