#!/usr/bin/env -S python3 -B

"""Compile an Applicable Methodology projection for local release."""

from __future__ import annotations


import os
import re
import shutil
import tempfile
from pathlib import Path

from pydantic import BaseModel, ConfigDict

# fmt: off
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.carriers__shared import (
    carrier_status_folder as carrier_status_folder,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.\
    COMPILE_APPLICABLE_METHODOLOGY.methodology_paths__shared import (
    ROLES,
    ROLE_BY_DIRECTORY as ROLE_BY_DIRECTORY,
    ROLE_ORDER,
    RELATION_KINDS as RELATION_KINDS,
    methodology_paths,
    source_state_snapshot as source_state_snapshot,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.\
    COMPILE_APPLICABLE_METHODOLOGY.METHODOLOGY_READING.METHODOLOGY_READING__shared import (
    LAYERS,
    MethodologyPaths,
    source_layer_paths as source_layer_paths,
    framework_settings as framework_settings,
    extension_selections as extension_selections,
    repo_relative as repo_relative,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.\
    COMPILE_APPLICABLE_METHODOLOGY.METHODOLOGY_READING.METHODOLOGY_READING__shared import (
    Candidate,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.\
    COMPILE_APPLICABLE_METHODOLOGY.METHODOLOGY_READING.METHODOLOGY_READING__shared import (
    CompileError,
    relations_digest as relations_digest,
    split_frontmatter,
    top_scalar as top_scalar,
    relation_targets as relation_targets,
    derive_atom_id as derive_atom_id,
    definition_subject as definition_subject,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.\
    COMPILE_APPLICABLE_METHODOLOGY.METHODOLOGY_READING.METHODOLOGY_READING__shared import (
    sha256_bytes as sha256_bytes,
    candidate_sort_key as candidate_sort_key,
    frontier_digest,
    detect_conflicts,
)

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.\
    COMPILE_APPLICABLE_METHODOLOGY.methodology_discovery import (
    _collect_extensions as _collect_extensions,
    _collect_role as _collect_role,
    discover_candidates as discover_candidates,
)

# fmt: on


class _CompilationReport(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    structural_source_layers: list[str]
    contributing_source_layers: list[str]
    source_frontier_digest: str
    eligible_candidate_count: int
    conflict_count: int
    unresolved_conflict_count: int
    conflicts: list[dict[str, object]]
    diagnostics: list[dict[str, object]]
    excluded_candidates: list[dict[str, object]]
    selected_candidate_count: int
    output_plan: list[dict[str, object]]
    can_apply: bool


def selected_sort_key(candidate: Candidate) -> tuple[object, ...]:
    return (
        ROLE_ORDER[candidate.role_directory],
        candidate.atom_id,
        candidate.source_path,
    )


def output_plan(candidates: list[Candidate]) -> list[dict[str, object]]:
    return [
        candidate.report_record()
        for candidate in sorted(candidates, key=selected_sort_key)
    ]


def projection_metadata_bytes(
    source_relative_from_output: str, candidate: Candidate
) -> bytes:
    """Render the one canonical projection metadata insertion verbatim."""
    return (
        "\nprojection:\n"
        f"  source_carrier_path: {source_relative_from_output}\n"
        f"  source_atom_id: {candidate.atom_id}\n"
        f"  source_atom_revision: {candidate.version}\n"
        f"  source_sha256: {candidate.source_sha256}\n"
        f"  original_relations_sha256: {candidate.original_relations_sha256}"
    ).encode("utf-8")


def projection_bytes(
    source: bytes, source_relative_from_output: str, candidate: Candidate
) -> bytes:
    path = candidate.source_path
    frontmatter, _ = split_frontmatter(source, path)
    if re.search(r"(?m)^projection:\s*(?:$|\{)", frontmatter):
        raise CompileError(
            "source-projection-metadata-present",
            "Authoritative Source Carrier cannot contain projection metadata",
            path=path,
        )
    boundary = source.find(b"\n---\n", 4)
    return (
        source[:boundary]
        + projection_metadata_bytes(source_relative_from_output, candidate)
        + source[boundary:]
    )


def validate_projection_source_preservation(
    source: bytes,
    projected: bytes,
    source_relative_from_output: str,
    candidate: Candidate,
) -> None:
    """Require source-byte preservation apart from canonical metadata."""
    path = candidate.source_path
    frontmatter, _ = split_frontmatter(source, path)
    if re.search(r"(?m)^projection:\s*(?:$|\{)", frontmatter):
        raise CompileError(
            "source-projection-metadata-present",
            "Authoritative Source Carrier cannot contain projection metadata",
            path=path,
        )
    boundary = source.find(b"\n---\n", 4)
    metadata = projection_metadata_bytes(
        source_relative_from_output, candidate
    )
    prefix = source[:boundary]
    suffix = source[boundary:]
    if (
        not projected.startswith(prefix + metadata)
        or projected[len(prefix + metadata) :] != suffix
    ):
        raise CompileError(
            "projection-source-preservation-invalid",
            "Projected Carrier must preserve source bytes except for "
            "canonical projection metadata",
            path=path,
        )


def _write_staged_outputs(root, candidates, output_root, new_root):
    for candidate in candidates:
        source_path = root / candidate.source_path
        target_parent = output_root / candidate.role_directory
        relative_source = Path(
            os.path.relpath(source_path, start=target_parent)
        ).as_posix()
        projected = projection_bytes(
            source_path.read_bytes(), relative_source, candidate
        )
        target = new_root / candidate.role_directory / candidate.basename
        target.write_bytes(projected)


def stage_outputs(
    root: Path,
    candidates: list[Candidate],
    source_snapshot: dict[str, str],
    places: MethodologyPaths | None = None,
) -> Path:
    output_root = root / (places or methodology_paths(root)).output
    temporary_staging = (
        root / ".anechoic_runtime/compile_applicable_methodology"
    )
    temporary_staging.mkdir(parents=True, exist_ok=True)
    staging = Path(
        tempfile.mkdtemp(prefix="transaction-", dir=temporary_staging)
    )
    new_root = staging / "new"
    for _, role_directory in ROLES:
        (new_root / role_directory).mkdir(parents=True)
    try:
        _write_staged_outputs(root, candidates, output_root, new_root)
        _, current_diagnostics, current_snapshot = discover_candidates(
            root, places
        )
        if (
            any(
                item.get("code") not in {"source-excluded"}
                for item in current_diagnostics
            )
            or current_snapshot != source_snapshot
        ):
            raise CompileError(
                "source-frontier-changed",
                "Source frontier changed while outputs were staged",
            )
        return staging
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        raise


def _rollback_outputs(installed, existing, expected):
    rollback_failed = False
    for target in reversed(installed):
        if target.exists() and target not in existing:
            try:
                target.unlink()
            except OSError:
                rollback_failed = True
    for target, data in existing.items():
        temporary = target.with_name(f".{target.name}.rollback.tmp")
        try:
            temporary.write_bytes(data)
            os.replace(temporary, target)
        except OSError:
            rollback_failed = True
            temporary.unlink(missing_ok=True)
    for target in set(expected).difference(existing):
        if target.exists():
            try:
                target.unlink()
            except OSError:
                rollback_failed = True
    return rollback_failed


def _existing_outputs(output_root, new_root, existing, expected):
    for _, role_directory in ROLES:
        target_directory = output_root / role_directory
        target_directory.mkdir(parents=True, exist_ok=True)
        existing.update(
            {
                path: path.read_bytes()
                for path in target_directory.rglob("*.md")
                if path.is_file()
            }
        )
        expected.update(
            target_directory / path.name
            for path in (new_root / role_directory).iterdir()
            if path.is_file()
        )


def replace_outputs_atomically(
    root: Path, staging: Path, places: MethodologyPaths | None = None
) -> None:
    output_root = root / (places or methodology_paths(root)).output
    new_root = staging / "new"
    output_root.mkdir(parents=True, exist_ok=True)
    existing: dict[Path, bytes] = {}
    expected: set[Path] = set()
    _existing_outputs(output_root, new_root, existing, expected)
    installed: list[Path] = []
    try:
        for _, role_directory in ROLES:
            target_directory = output_root / role_directory
            for replacement in sorted((new_root / role_directory).iterdir()):
                target = target_directory / replacement.name
                os.replace(replacement, target)
                installed.append(target)
        for stale in sorted(set(existing).difference(expected)):
            stale.unlink()
    except Exception as error:
        rollback_failed = _rollback_outputs(installed, existing, expected)
        raise CompileError(
            "atomic-replacement-uncertain"
            if rollback_failed
            else "atomic-replacement-failed",
            "Generated RMEDO output replacement has an uncertain "
            "recovery state"
            if rollback_failed
            else "Generated RMEDO output replacement rolled back",
            error=type(error).__name__,
        ) from error
    finally:
        shutil.rmtree(staging, ignore_errors=True)


def compile_report(
    root: Path, places: MethodologyPaths | None = None
) -> tuple[dict[str, object], list[Candidate], dict[str, str]]:
    places = places or methodology_paths(root)
    candidates, diagnostics, source_snapshot = discover_candidates(
        root, places
    )
    digest = frontier_digest(candidates)
    conflicts = detect_conflicts(candidates)
    selected = sorted(candidates, key=selected_sort_key)
    report = _CompilationReport(
        structural_source_layers=[name for name, _, _ in LAYERS],
        contributing_source_layers=[
            "CORE_META_MODEL",
            "INSTALLED_EXTENSIONS",
            "PROJECT_CONFIGURATION",
        ],
        source_frontier_digest=digest,
        eligible_candidate_count=len(candidates),
        conflict_count=len(conflicts),
        unresolved_conflict_count=len(conflicts),
        conflicts=conflicts,
        diagnostics=diagnostics,
        excluded_candidates=[
            item
            for item in diagnostics
            if item.get("code") == "source-excluded"
        ],
        selected_candidate_count=len(selected),
        output_plan=output_plan(selected),
        can_apply=not any(
            item.get("code") not in {"source-excluded"} for item in diagnostics
        )
        and not conflicts,
    )
    return report.model_dump(), selected, source_snapshot
