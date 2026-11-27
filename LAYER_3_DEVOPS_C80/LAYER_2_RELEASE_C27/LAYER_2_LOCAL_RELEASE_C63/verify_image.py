"""Verify an immutable candidate image from the selected source checkout."""

import json
from functools import partial
from pathlib import Path
from subprocess import SubprocessError
from tempfile import NamedTemporaryFile

from LAYER_1_RUNTIME_IMAGES_C81.LAYER_1_RUNTIME_IMAGES_C81__shared import (
    _RUN_ID,
    LocalReleaseError,
    _cleanup_staging,
    _installation_lock,
    _new_staging_directory,
    _project_path,
    _root,
    _target,
    _verify_package,
    read_release_selection,
)

from . import local_release_package_phases as package_phases
from .local_release_gates import run_gate
from .local_release_state import atomic_write, source_identity
from .local_release_test_process import run_logged_test_process
from .prepare_test_environment import check_locked_engine
from .release_support import _failed_test_output

_REPORTS = Path(".anechoic_runtime/simple_local_release/reports/verify-image")
_LOGS = Path(".anechoic_tmp/simple_local_release/verify-image")


def verify_image(
    project_root: Path | str, *, run_id: str, runner=None
) -> dict[str, object]:
    """Run preflight, the required image suite, and its packaged canary."""
    root = _root(project_root)
    if not isinstance(run_id, str) or not _RUN_ID.fullmatch(run_id):
        raise LocalReleaseError("local-release-run-id-invalid")
    result = {
        "outcome": "failed",
        "failed_step": "validate_project_selection",
        "run_id": run_id,
        "project_root": str(root),
        "effects": [],
        "test_log_paths": {},
    }
    try:
        selection = read_release_selection(root)
    except ValueError:
        return _failure(
            result,
            LocalReleaseError("local-release-project-selection-invalid"),
        )
    result.update(
        failed_step="installation_lock",
        project_id=selection.instance_id,
        control_root=selection.control_relative.as_posix(),
        manifest_ref=selection.manifest_ref,
        manifest_sha256=selection.manifest_sha256,
    )
    try:
        with _installation_lock(root, selection) as lock_fd:
            return _verify_locked(
                root, selection, run_id, runner, lock_fd, result
            )
    except (
        OSError,
        ValueError,
        RuntimeError,
        SubprocessError,
        KeyboardInterrupt,
    ) as error:
        return _failure(result, error)


def _write_report(report, result):
    try:
        atomic_write(
            report, json.dumps(result, sort_keys=True, indent=2) + "\n"
        )
    except OSError as error:
        result.pop("report_path")
        result["report_error"] = str(error)
        if result["outcome"] == "completed":
            result["failed_step"] = "write_report"
            _failure(result, error)


def _verify_locked(root, selection, run_id, runner, lock_fd, result):
    result["failed_step"] = "reserve_report"
    directory = _project_path(
        root, _REPORTS / run_id, label="image-verification-report"
    )
    directory.parent.mkdir(parents=True, exist_ok=True)
    try:
        directory.mkdir(mode=0o700)
    except FileExistsError as error:
        raise LocalReleaseError("verify-image-run-id-exists") from error
    report = directory / "result.json"
    result["report_path"] = report.relative_to(root).as_posix()
    gate = partial(
        run_gate,
        runner=runner,
        log_paths=result["test_log_paths"],
        verify=_verify_package,
        target=_target,
        named_file=NamedTemporaryFile,
        logged_process=partial(run_logged_test_process, lock_fd=lock_fd),
        failed_output=_failed_test_output,
        source_bound=True,
        log_directory=_LOGS / run_id,
    )
    try:
        _verify_candidate(root, selection, run_id, runner, result, gate)
    except (
        OSError,
        ValueError,
        RuntimeError,
        SubprocessError,
        KeyboardInterrupt,
    ) as error:
        _failure(result, error)
    else:
        result.update(outcome="completed", failed_step=None)
    _write_report(report, result)
    return result


def _prepare_candidate(root, selection, run_id, runner, result, provenance):
    result["failed_step"] = "build_package"
    package_phases.validate_package_inputs(root, selection)
    staging = _new_staging_directory(root, f"{run_id}-verify-image-")
    result["staging_path"] = staging.relative_to(root).as_posix()
    product, product_identity, package, package_identity = (
        package_phases.build_package(
            root,
            selection,
            None,
            staging,
            active_sources=True,
        )
    )
    result["failed_step"] = "prepare_candidate_image"
    _, image, fingerprint = package_phases.prepare_image(
        root,
        selection,
        staging,
        package,
        package_identity,
        product,
        product_identity,
        runner,
        provenance=provenance,
    )
    result.update(image_id=image, fingerprint=fingerprint)
    result["effects"].append("prepared_candidate_image")
    return staging, package, package_identity, image


def _verify_candidate(root, selection, run_id, runner, result, gate):
    result["failed_step"] = "validate_project_selection"
    if read_release_selection(root) != selection:
        raise LocalReleaseError("local-release-project-selection-changed")
    result["failed_step"] = "validate_inputs"
    provenance = package_phases.release_image_provenance(
        root, selection, runner
    )
    inputs = source_identity(root, root)
    result.update(
        source_revision=provenance["head_commit"], source_sha256=inputs
    )
    result["failed_step"] = "preflight_tests"
    if (
        runner is None
        and (root / "LAYER_4_ENGINE_STUDIO_C14/.venv-dev/bin/python").is_file()
    ):
        check_locked_engine(root)
    gate(root, "preflight", None, None, {}, selection, run_id)
    staging, package, package_identity, image = _prepare_candidate(
        root, selection, run_id, runner, result, provenance
    )
    result["failed_step"] = "verify_candidate_image"
    endpoint = gate(
        root, "image", image, package, package_identity, selection, run_id
    )
    _verify_package(package, package_identity)
    if (
        source_identity(root, root) != inputs
        or read_release_selection(root) != selection
        or package_phases.release_image_provenance(root, selection, runner)
        != provenance
    ):
        raise LocalReleaseError("local-release-gate-inputs-changed")
    result["canary_endpoint"] = endpoint
    result["effects"].append("verified_candidate_image")
    result["failed_step"] = "cleanup_staging"
    if _cleanup_staging(root, staging):
        raise LocalReleaseError("local-release-staging-cleanup-failed")
    result.pop("staging_path")


def _failure(result, error):
    result.update(
        outcome="failed",
        error_type=type(error).__name__,
        error=str(error)[:8500],
    )
    if getattr(error, "__notes__", ()):
        result["error_notes"] = list(error.__notes__)
    return result
