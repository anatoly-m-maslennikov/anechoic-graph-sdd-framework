#!/usr/bin/env python3

"""Compile an Applicable Methodology projection for local release."""

from __future__ import annotations


import os
import re
import shutil
import tempfile
from pathlib import Path

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carrier_compat__pub import carrier_status_folder
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.COMPILE_APPLICABLE_METHODOLOGY.methodology_paths__shared import (
    LAYERS, ROLES, ROLE_BY_DIRECTORY, ROLE_ORDER, RELATION_KINDS, MethodologyPaths,
    methodology_paths, source_layer_paths,
    framework_settings,
    extension_selections, source_state_snapshot, repo_relative,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.COMPILE_APPLICABLE_METHODOLOGY.methodology_candidate import (
    Candidate,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.COMPILE_APPLICABLE_METHODOLOGY.methodology_source_parsing import (
    CompileError, relations_digest, split_frontmatter, top_scalar, relation_targets, derive_atom_id, definition_subject,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.COMPILE_APPLICABLE_METHODOLOGY.methodology_conflicts import (
    sha256_bytes, candidate_sort_key, frontier_digest, detect_conflicts,
)


def selected_sort_key(candidate: Candidate) -> tuple[object, ...]:
    return (ROLE_ORDER[candidate.role_directory], candidate.atom_id, candidate.source_path)


def _collect_role(root, places, candidates, diagnostics, exclude, layer, order, role_root, extension_id=None, extension_revision=None):
    if not role_root.exists():
        return
    if not role_root.is_dir() or role_root.is_symlink():
        raise CompileError("source-role-not-directory", "Source role Carrier must be a directory", path=repo_relative(root, role_root))
    for path in sorted(role_root.rglob("*.md")):
        relative_within_role = path.relative_to(role_root)
        relative = repo_relative(root, path)
        if {"archived", "draft", "done", "canceled"}.intersection(
            carrier_status_folder(part) for part in relative_within_role.parts[:-1]
        ):
            exclude(path, "inactive-location")
            continue
        if not path.is_file() or path.is_symlink():
            exclude(path, "not-regular")
            continue
        try:
            data = path.read_bytes()
            frontmatter, _ = split_frontmatter(data, relative)
            if re.search(r"(?m)^projection:\s*(?:$|\{)", frontmatter):
                raise CompileError("source-projection-metadata-present", "Authoritative Source Carrier cannot contain projection metadata", path=relative)
            status = top_scalar(frontmatter, "status")
            if status not in {"Active", "active"}:
                exclude(path, "inactive" if status else "status-missing", status=status)
                continue
            version_raw = top_scalar(frontmatter, "version")
            if version_raw is None or not re.fullmatch(r"[1-9][0-9]*", version_raw):
                raise CompileError("source-version-invalid", "Selected Source Atom revision requires a positive integer version", path=relative)
            defined_term, definition_subject_path, definition_namespace = definition_subject(frontmatter, relative)
            candidates.append(Candidate(
                layer=layer, layer_order=order, role=ROLE_BY_DIRECTORY[role_root.name], role_directory=role_root.name,
                atom_id=derive_atom_id(path, frontmatter), version=int(version_raw), source_path=relative,
                source_sha256=sha256_bytes(data), basename=path.name, priority=top_scalar(frontmatter, "priority"),
                priority_group=top_scalar(frontmatter, "applicable_methodology_priority_group"),
                replacements=relation_targets(frontmatter, RELATION_KINDS["replacement"]),
                incompatibilities=relation_targets(frontmatter, RELATION_KINDS["incompatible"]),
                definition_term=defined_term, definition_subject_path=definition_subject_path,
                definition_namespace=definition_namespace,
                output_relative=places.output.as_posix(), extension_id=extension_id, extension_revision=extension_revision,
                original_relations_sha256=relations_digest(frontmatter),
            ))
        except CompileError as error:
            diagnostics.append({**error.record(), "path": relative})



def _collect_extensions(root, places, layers, selected_extensions, candidates, diagnostics, exclude):
    installed = root / layers["INSTALLED_EXTENSIONS"]
    observed_revisions: set[tuple[str, str]] = set()
    for extension_root in sorted(path for path in installed.iterdir() if path.is_dir() and not path.is_symlink()):
        extension_id = extension_root.name
        for revision_root in sorted(path for path in extension_root.iterdir() if path.is_dir() and not path.is_symlink()):
            revision = revision_root.name
            observed_revisions.add((extension_id, revision))
            selected_revision = selected_extensions.get(extension_id)
            for _, role_directory in ROLES:
                role_root = revision_root / role_directory
                if selected_revision != revision:
                    for path in sorted(role_root.rglob("*.md")) if role_root.is_dir() else []:
                        exclude(path, "extension-revision-unselected", extension_id=extension_id, extension_revision=revision)
                    continue
                _collect_role(root, places, candidates, diagnostics, exclude, "INSTALLED_EXTENSIONS", 1, role_root, extension_id, revision)
    for extension_id, revision in selected_extensions.items():
        if (extension_id, revision) not in observed_revisions:
            diagnostics.append({"code": "activated-extension-revision-missing", "extension_id": extension_id, "extension_revision": revision})
        elif not any(candidate.extension_id == extension_id and candidate.extension_revision == revision for candidate in candidates):
            diagnostics.append({"code": "activated-extension-has-no-current-carriers", "extension_id": extension_id, "extension_revision": revision})



def discover_candidates(root: Path, places: MethodologyPaths | None = None) -> tuple[list[Candidate], list[dict[str, object]], dict[str, str]]:
    """Read the complete governed frontier without deriving activation from files."""
    places = places or methodology_paths(root)
    source_root = root / places.source
    diagnostics: list[dict[str, object]] = []
    if not source_root.is_dir():
        raise CompileError("source-root-missing", "Applicable Methodology source root is missing", path=places.source.as_posix())
    layers = source_layer_paths(root, places)
    root_role_directories = {directory for _, directory in ROLES}
    observed_layers = sorted(path.name for path in source_root.iterdir() if path.is_dir() and path.name not in root_role_directories)
    expected_layers = sorted(path.name for path in layers.values())
    if observed_layers != expected_layers:
        raise CompileError("source-layer-topology-mismatch", "Structural Source Layers differ from the governed topology", expected=expected_layers, observed=observed_layers)

    settings, _ = framework_settings(root, places)
    selected_extensions = extension_selections(settings)
    candidates: list[Candidate] = []
    snapshot = source_state_snapshot(root, places)

    def exclude(path: Path, reason: str, **details: object) -> None:
        diagnostics.append({"code": "source-excluded", "source_carrier_path": repo_relative(root, path), "reason": reason, **details})

    for layer, order, _ in (LAYERS[0], LAYERS[2]):
        for _, role_directory in ROLES:
            _collect_role(root, places, candidates, diagnostics, exclude, layer, order, root / layers[layer] / role_directory)

    _collect_extensions(root, places, layers, selected_extensions, candidates, diagnostics, exclude)

    candidates.sort(key=candidate_sort_key)
    if not candidates:
        diagnostics.append({"code": "empty-source-frontier", "message": "No eligible current active RMEDO Source Atom revisions were found"})
    return candidates, diagnostics, snapshot


def output_plan(candidates: list[Candidate]) -> list[dict[str, object]]:
    return [candidate.report_record() for candidate in sorted(candidates, key=selected_sort_key)]


def projection_metadata_bytes(source_relative_from_output: str, candidate: Candidate) -> bytes:
    """Render the one canonical projection metadata insertion verbatim."""
    return (
        "\nprojection:\n"
        f"  source_carrier_path: {source_relative_from_output}\n"
        f"  source_atom_id: {candidate.atom_id}\n"
        f"  source_atom_revision: {candidate.version}\n"
        f"  source_sha256: {candidate.source_sha256}\n"
        f"  original_relations_sha256: {candidate.original_relations_sha256}"
    ).encode("utf-8")


def projection_bytes(source: bytes, source_relative_from_output: str, candidate: Candidate) -> bytes:
    path = candidate.source_path
    frontmatter, _ = split_frontmatter(source, path)
    if re.search(r"(?m)^projection:\s*(?:$|\{)", frontmatter):
        raise CompileError("source-projection-metadata-present", "Authoritative Source Carrier cannot contain projection metadata", path=path)
    boundary = source.find(b"\n---\n", 4)
    return source[:boundary] + projection_metadata_bytes(source_relative_from_output, candidate) + source[boundary:]


def validate_projection_source_preservation(
    source: bytes,
    projected: bytes,
    source_relative_from_output: str,
    candidate: Candidate,
) -> None:
    """Require a projection to preserve its source bytes apart from canonical metadata."""
    path = candidate.source_path
    frontmatter, _ = split_frontmatter(source, path)
    if re.search(r"(?m)^projection:\s*(?:$|\{)", frontmatter):
        raise CompileError("source-projection-metadata-present", "Authoritative Source Carrier cannot contain projection metadata", path=path)
    boundary = source.find(b"\n---\n", 4)
    metadata = projection_metadata_bytes(source_relative_from_output, candidate)
    prefix = source[:boundary]
    suffix = source[boundary:]
    if not projected.startswith(prefix + metadata) or projected[len(prefix + metadata):] != suffix:
        raise CompileError(
            "projection-source-preservation-invalid",
            "Projected Carrier must preserve source bytes except for canonical projection metadata",
            path=path,
        )


def stage_outputs(root: Path, candidates: list[Candidate], source_snapshot: dict[str, str], places: MethodologyPaths | None = None) -> Path:
    output_root = root / (places or methodology_paths(root)).output
    temporary_staging = root / ".anechoic_runtime/compile_applicable_methodology"
    temporary_staging.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix="transaction-", dir=temporary_staging))
    new_root = staging / "new"
    for _, role_directory in ROLES:
        (new_root / role_directory).mkdir(parents=True)
    try:
        for candidate in candidates:
            source_path = root / candidate.source_path
            target_parent = output_root / candidate.role_directory
            relative_source = Path(os.path.relpath(source_path, start=target_parent)).as_posix()
            projected = projection_bytes(source_path.read_bytes(), relative_source, candidate)
            target = new_root / candidate.role_directory / candidate.basename
            target.write_bytes(projected)
        _, current_diagnostics, current_snapshot = discover_candidates(root, places)
        if any(item.get("code") not in {"source-excluded"} for item in current_diagnostics) or current_snapshot != source_snapshot:
            raise CompileError("source-frontier-changed", "Source frontier changed while outputs were staged")
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


def replace_outputs_atomically(root: Path, staging: Path, places: MethodologyPaths | None = None) -> None:
    output_root = root / (places or methodology_paths(root)).output
    new_root = staging / "new"
    output_root.mkdir(parents=True, exist_ok=True)
    existing: dict[Path, bytes] = {}
    expected: set[Path] = set()
    for _, role_directory in ROLES:
        target_directory = output_root / role_directory
        target_directory.mkdir(parents=True, exist_ok=True)
        existing.update({path: path.read_bytes() for path in target_directory.rglob("*.md") if path.is_file()})
        expected.update(target_directory / path.name for path in (new_root / role_directory).iterdir() if path.is_file())
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
            "atomic-replacement-uncertain" if rollback_failed else "atomic-replacement-failed",
            "Generated RMEDO output replacement has an uncertain recovery state" if rollback_failed else "Generated RMEDO output replacement rolled back",
            error=type(error).__name__,
        ) from error
    finally:
        shutil.rmtree(staging, ignore_errors=True)


def compile_report(root: Path, places: MethodologyPaths | None = None) -> tuple[dict[str, object], list[Candidate], dict[str, str]]:
    places = places or methodology_paths(root)
    candidates, diagnostics, source_snapshot = discover_candidates(root, places)
    digest = frontier_digest(candidates)
    conflicts = detect_conflicts(candidates)
    selected = sorted(candidates, key=selected_sort_key)
    report: dict[str, object] = {
        "structural_source_layers": [name for name, _, _ in LAYERS],
        "contributing_source_layers": ["CORE_META_MODEL", "INSTALLED_EXTENSIONS", "PROJECT_CONFIGURATION"],
        "source_frontier_digest": digest,
        "eligible_candidate_count": len(candidates),
        "conflict_count": len(conflicts),
        "unresolved_conflict_count": len(conflicts),
        "conflicts": conflicts,
        "diagnostics": diagnostics,
        "excluded_candidates": [item for item in diagnostics if item.get("code") == "source-excluded"],
        "selected_candidate_count": len(selected),
        "output_plan": output_plan(selected),
        "can_apply": not any(
            item.get("code") not in {"source-excluded"} for item in diagnostics
        ) and not conflicts,
    }
    return report, selected, source_snapshot
