"""Discover governed Applicable Methodology candidates."""

from __future__ import annotations

from pathlib import Path

# fmt: off
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.\
    COMPILE_APPLICABLE_METHODOLOGY.methodology_paths__shared import (
    ROLES,
    methodology_paths,
    source_state_snapshot,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.\
    COMPILE_APPLICABLE_METHODOLOGY.METHODOLOGY_READING.METHODOLOGY_READING__shared import (
    LAYERS,
    MethodologyPaths,
    source_layer_paths,
    framework_settings,
    extension_selections,
    repo_relative,
)
# fmt: on
# fmt: off
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.\
    COMPILE_APPLICABLE_METHODOLOGY.METHODOLOGY_READING.METHODOLOGY_READING__shared import (
    Candidate,
)
# fmt: on
# fmt: off
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.\
    COMPILE_APPLICABLE_METHODOLOGY.METHODOLOGY_READING.METHODOLOGY_READING__shared import (
    CompileError,
)
# fmt: on
# fmt: off
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.\
    COMPILE_APPLICABLE_METHODOLOGY.METHODOLOGY_READING.METHODOLOGY_READING__shared import (
    candidate_sort_key,
)
# fmt: on

# fmt: off
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.\
    COMPILE_APPLICABLE_METHODOLOGY.methodology_discovery_roles import (
    _collect_role,
)
# fmt: on


def _extension_diagnostics(
    selected_extensions, observed_revisions, candidates, diagnostics
):
    for extension_id, revision in selected_extensions.items():
        if (extension_id, revision) not in observed_revisions:
            diagnostics.append(
                {
                    "code": "activated-extension-revision-missing",
                    "extension_id": extension_id,
                    "extension_revision": revision,
                }
            )
        elif not any(
            candidate.extension_id == extension_id
            and candidate.extension_revision == revision
            for candidate in candidates
        ):
            diagnostics.append(
                {
                    "code": "activated-extension-has-no-current-carriers",
                    "extension_id": extension_id,
                    "extension_revision": revision,
                }
            )


def _collect_extension_roles(
    root,
    places,
    candidates,
    diagnostics,
    exclude,
    revision_root,
    selected_revision,
    extension_id,
    revision,
):
    for _, role_directory in ROLES:
        role_root = revision_root / role_directory
        if selected_revision != revision:
            for path in (
                sorted(role_root.rglob("*.md")) if role_root.is_dir() else []
            ):
                exclude(
                    path,
                    "extension-revision-unselected",
                    extension_id=extension_id,
                    extension_revision=revision,
                )
            continue
        _collect_role(
            root,
            places,
            candidates,
            diagnostics,
            exclude,
            "INSTALLED_EXTENSIONS",
            1,
            role_root,
            extension_id,
            revision,
        )


def _collect_extensions(
    root, places, layers, selected_extensions, candidates, diagnostics, exclude
):
    installed = root / layers["INSTALLED_EXTENSIONS"]
    observed_revisions: set[tuple[str, str]] = set()
    for extension_root in sorted(
        path
        for path in installed.iterdir()
        if path.is_dir() and not path.is_symlink()
    ):
        extension_id = extension_root.name
        for revision_root in sorted(
            path
            for path in extension_root.iterdir()
            if path.is_dir() and not path.is_symlink()
        ):
            revision = revision_root.name
            observed_revisions.add((extension_id, revision))
            selected_revision = selected_extensions.get(extension_id)
            _collect_extension_roles(
                root,
                places,
                candidates,
                diagnostics,
                exclude,
                revision_root,
                selected_revision,
                extension_id,
                revision,
            )
    _extension_diagnostics(
        selected_extensions, observed_revisions, candidates, diagnostics
    )


def _source_layers(root, places):
    source_root = root / places.source
    if not source_root.is_dir():
        raise CompileError(
            "source-root-missing",
            "Applicable Methodology source root is missing",
            path=places.source.as_posix(),
        )
    layers = source_layer_paths(root, places)
    root_role_directories = {directory for _, directory in ROLES}
    observed_layers = sorted(
        path.name
        for path in source_root.iterdir()
        if path.is_dir() and path.name not in root_role_directories
    )
    expected_layers = sorted(path.name for path in layers.values())
    if observed_layers != expected_layers:
        raise CompileError(
            "source-layer-topology-mismatch",
            "Structural Source Layers differ from the governed topology",
            expected=expected_layers,
            observed=observed_layers,
        )

    return layers


def _collect_base_layers(
    root, places, layers, candidates, diagnostics, exclude
):
    for layer, order, _ in (LAYERS[0], LAYERS[2]):
        for _, role_directory in ROLES:
            _collect_role(
                root,
                places,
                candidates,
                diagnostics,
                exclude,
                layer,
                order,
                root / layers[layer] / role_directory,
            )


def discover_candidates(
    root: Path, places: MethodologyPaths | None = None
) -> tuple[list[Candidate], list[dict[str, object]], dict[str, str]]:
    """Read the governed frontier without deriving activation from files."""
    places = places or methodology_paths(root)
    layers = _source_layers(root, places)
    diagnostics: list[dict[str, object]] = []

    settings, _ = framework_settings(root, places)
    selected_extensions = extension_selections(settings)
    candidates: list[Candidate] = []
    snapshot = source_state_snapshot(root, places)

    def exclude(path: Path, reason: str, **details: object) -> None:
        diagnostics.append(
            {
                "code": "source-excluded",
                "source_carrier_path": repo_relative(root, path),
                "reason": reason,
                **details,
            }
        )

    _collect_base_layers(
        root, places, layers, candidates, diagnostics, exclude
    )

    _collect_extensions(
        root,
        places,
        layers,
        selected_extensions,
        candidates,
        diagnostics,
        exclude,
    )

    candidates.sort(key=candidate_sort_key)
    if not candidates:
        diagnostics.append(
            {
                "code": "empty-source-frontier",
                "message": "No eligible current active RMEDO Source Atom "
                "revisions were found",
            }
        )
    return candidates, diagnostics, snapshot
