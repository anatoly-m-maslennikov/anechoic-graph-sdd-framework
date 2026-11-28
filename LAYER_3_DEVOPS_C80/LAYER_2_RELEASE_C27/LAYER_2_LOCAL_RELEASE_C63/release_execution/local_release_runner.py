"""Ordered phases for the direct local Release."""

from __future__ import annotations

import subprocess
import sys
import tempfile
from contextlib import ExitStack
from functools import partial as partial
from pathlib import Path
from typing import Any

from ..release_cleanup import (
    cleanup_obsolete_images as cleanup_obsolete_images,
    cleanup_stopped_containers as cleanup_stopped_containers,
)
from LAYER_1_RUNTIME_IMAGES_C81.LAYER_1_RUNTIME_IMAGES_C81__shared import (
    image_labels as image_labels,
)
from ..release_cleanup_images import record_ready_images as record_ready_images
from ..release_cleanup_tmp import prune_temporary_files as prune_temporary_files
from LAYER_1_RUNTIME_IMAGES_C81.image_container.image_container__shared import (
    find_release_container as find_release_container,
    reconcile_release_container as reconcile_release_container,
    start_container as start_container,
    verify_release_container as verify_release_container,
)
from LAYER_1_RUNTIME_IMAGES_C81.input_selection.input_selection__shared import (
    read_release_selection,
)
from .local_release_runner_phases import RunnerPhases
from .local_release_runner_delivery import RunnerDelivery
from ..local_release_gates import run_gate as run_gate
from .local_release_recovery import (
    FAST_LIMIT_SECONDS as FAST_LIMIT_SECONDS,
    FAST_TARGET_SECONDS as FAST_TARGET_SECONDS,
    ResumableRelease,
)
from ..local_release_state import (
    failure_evidence,
    release_evidence as release_evidence,
)
from ..local_release_previous import previous_container as previous_container
from .. import local_release_package_phases as local_release_package_phases
from .. import local_release_reports as reports

from LAYER_1_RUNTIME_IMAGES_C81.LAYER_1_RUNTIME_IMAGES_C81__shared import (
    _new_staging_directory as _new_staging_directory,
)
from ..local_release_test_process import (
    run_logged_test_process as run_logged_test_process,
)
from LAYER_1_RUNTIME_IMAGES_C81.LAYER_1_RUNTIME_IMAGES_C81__shared import (
    LocalReleaseError,
    _RUN_ID,
    _cleanup_staging,
    _project_path as _project_path,
    _root,
    _target,
    _verify_package as _verify_package,
)
from ..release_support import (
    _DEFAULT_PRODUCT,
    _launcher_image,
    _read_version as _read_version,
    _failed_test_output as _support_failed_test_output,
)

package_phases = local_release_package_phases

_TEST_GATES = {
    "preflight tests": "preflight",
    "static tests": "static",
    "functional tests": "functional",
    "verify candidate image": "image-tests",
    "verify candidate canary": "canary",
}


def _failed_test_output(
    root: Path, run_id: str, result: Any, *, log_path: str | None = None
) -> str:
    return _support_failed_test_output(
        root,
        run_id,
        result,
        log_path=log_path,
        named_temporary_file=tempfile.NamedTemporaryFile,
    )


class LocalReleaseRun(RunnerPhases, RunnerDelivery, ResumableRelease):
    def __init__(
        self,
        project_root,
        run_id,
        runner,
        test_modules,
        image_mode,
        *,
        resume=False,
        functional_suite=None,
        started_at=None,
    ):
        self.project_root = project_root
        self.run_id = run_id
        self.runner = runner
        self.test_modules = test_modules
        self.requested_image_mode, self.image_mode = (
            image_mode,
            image_mode if image_mode is not None else "refresh",
        )
        self.resume = resume
        self.release_started_at = started_at
        self._checked_test_environment = False
        self.requested_functional_suite = functional_suite
        self.journal = None
        self._setup_options()
        self._setup_state()

    def _setup_options(self):
        if not isinstance(self.run_id, str) or not _RUN_ID.fullmatch(
            self.run_id
        ):
            raise LocalReleaseError("local-release-run-id-invalid")
        if self.image_mode not in ("refresh", "existing"):
            raise LocalReleaseError("local-release-image-mode-invalid")
        if self.test_modules is not None and (
            not isinstance(self.test_modules, tuple)
        ):
            raise LocalReleaseError("local-release-test-modules-invalid")
        if self.test_modules == ():
            raise LocalReleaseError("local-release-test-modules-empty")
        if self.test_modules is not None and any(
            (not isinstance(module, str) for module in self.test_modules)
        ):
            raise LocalReleaseError("local-release-test-modules-invalid")
        self.root = _root(self.project_root)
        self.installation_lock = ExitStack()
        try:
            self.selection = read_release_selection(self.root)
        except ValueError as error:
            raise LocalReleaseError(
                "local-release-project-selection-invalid"
            ) from error
        self.cleanup_runner = self.runner
        self.default_runner = self.runner is None
        if self.runner is None:
            self.runner = lambda argv, cwd: subprocess.run(
                argv, cwd=cwd, text=True, capture_output=True, check=False
            )
        self.product = self._product_path()
        self.installed = _target(
            self.root,
            self.selection.control_relative / "000_ANECHOIC_framework",
            label="installed-root",
        )

    def _product_path(self):
        return _target(self.root, Path(_DEFAULT_PRODUCT), label="product-root")

    def _setup_state(self):
        self.package = self.prepared_product = self.staging = None
        self.package_identity, self.product_identity, self.readiness = (
            {},
            {},
            {},
        )
        self.candidate_image = self.candidate_fingerprint = (
            self.production_port
        ) = None
        self.runtime = _target(
            self.root,
            Path(".anechoic_runtime/simple_local_release/package"),
            label="simple-runtime",
        )
        if self.product == self.installed:
            raise LocalReleaseError("local-release-target-invalid")
        self.failed_step = "validate_inputs"
        self.endpoint = self.canary_endpoint = self.receipt_path = (
            self.test_log_path
        ) = None
        self.test_log_paths: dict[str, str] = {}
        self.cleanup_note = (
            "No proven superseded Project-owned image identity was available; "
            "none was removed."
        )
        self.cleanup_pending, self.cleanup = False, None
        self.test_scope, self.test_selection = (
            "static and functional",
            "configured required tests",
        )
        self.selected_test_modules = None

    def _observe_launcher_image(self):
        return _launcher_image(self.selection)

    def run(self):
        try:
            recorded = self._execute()
            if recorded is not None:
                return recorded
            result = self._completed_result()
            self.journal.data["result"] = result
            self.journal.save()
            if not self.cleanup_pending:
                _cleanup_staging(self.root, self.staging)
            return result
        except (Exception, KeyboardInterrupt) as error:
            return self._report_failure(error)
        finally:
            self.installation_lock.close()

    def _report_failure(self, error):
        if self.failed_step == "installation_lock":
            print(
                f"Local release installation lock failed: {error}",
                file=sys.stderr,
                flush=True,
            )
        if self.journal is not None:
            self.journal.record_failure(
                self.failed_step, error, self.test_log_paths
            )
        staging_note = self._failure_staging_note()
        report_path = reports.write_failure(
            self.root,
            self.run_id,
            self.failed_step,
            self.image_mode,
            self.test_scope,
            self.test_selection,
            error,
            self.test_log_paths,
            self.endpoint,
            self.cleanup_note,
            self.cleanup,
            staging_note,
        )
        return {
            "outcome": "failed",
            "failed_step": self.failed_step,
            "report_path": report_path,
            "error_type": type(error).__name__,
            "error": str(error)[:8500],
            "test_log_path": self.test_log_path,
            "test_log_paths": self.test_log_paths,
            "endpoint": self.endpoint,
            "canary_endpoint": self.canary_endpoint,
            "test_scope": self.test_scope,
            "test_modules": self.selected_test_modules,
            "image_mode": self.image_mode,
            **failure_evidence(self.journal, error, self.production_port),
        }

    def _failure_staging_note(self):
        return (
            f"Retained temporary staging: "
            f"`{self.staging.relative_to(self.root).as_posix()}`.\n"
            if self.staging is not None
            else ""
        )
