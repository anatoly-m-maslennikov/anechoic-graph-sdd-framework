"""Ordered phases for the direct local Release."""

from __future__ import annotations

import subprocess
import sys
import tempfile
from contextlib import ExitStack
from functools import partial
from pathlib import Path
from typing import Any

from .release_cleanup import cleanup_obsolete_images, cleanup_stopped_containers  # noqa: E402
from LAYER_1_RUNTIME_IMAGES_C81.LAYER_1_RUNTIME_IMAGES_C81__shared import image_labels  # noqa: E402
from .release_cleanup_images import record_ready_images  # noqa: E402
from .release_cleanup_tmp import prune_temporary_files  # noqa: E402
from LAYER_1_RUNTIME_IMAGES_C81.LAYER_1_RUNTIME_IMAGES_C81__shared import (
    find_release_container, reconcile_release_container, start_container, verify_release_container,
)  # noqa: E402
from LAYER_1_RUNTIME_IMAGES_C81.LAYER_1_RUNTIME_IMAGES_C81__shared import read_release_selection  # noqa: E402
from .local_release_gates import run_gate  # noqa: E402
from .local_release_recovery import FAST_LIMIT_SECONDS, FAST_TARGET_SECONDS, ResumableRelease
from .local_release_state import failure_evidence, release_evidence
from .local_release_previous import previous_container  # noqa: E402
from . import local_release_package_phases as package_phases  # noqa: E402
from . import local_release_reports as reports  # noqa: E402
from LAYER_1_RUNTIME_IMAGES_C81.LAYER_1_RUNTIME_IMAGES_C81__shared import _new_staging_directory  # noqa: E402
from .local_release_test_process import run_logged_test_process  # noqa: E402
from LAYER_1_RUNTIME_IMAGES_C81.LAYER_1_RUNTIME_IMAGES_C81__shared import (  # noqa: E402
    LocalReleaseError, _RUN_ID, _cleanup_staging, _project_path, _root, _target, _verify_package,
)
from .release_support import (  # noqa: E402
    _DEFAULT_PRODUCT,
    _launcher_image,
    _read_version,
    _failed_test_output as _support_failed_test_output,
)

_TEST_GATES = {
    "preflight tests": "preflight",
    "static tests": "static",
    "functional tests": "functional",
    "verify candidate image": "image-tests",
    "verify candidate canary": "canary",
}


def _failed_test_output(root: Path, run_id: str, result: Any, *, log_path: str | None = None) -> str:
    return _support_failed_test_output(
        root, run_id, result, log_path=log_path, named_temporary_file=tempfile.NamedTemporaryFile,
    )


class LocalReleaseRun(ResumableRelease):
    def __init__(self, project_root, run_id, runner, test_modules, image_mode, *, resume=False, functional_suite=None, started_at=None):
        self.project_root = project_root
        self.run_id = run_id
        self.runner = runner
        self.test_modules = test_modules
        self.requested_image_mode, self.image_mode = image_mode, image_mode if image_mode is not None else "refresh"
        self.resume = resume
        self.release_started_at = started_at
        self._checked_test_environment = False
        self.requested_functional_suite = functional_suite
        self.journal = None
        self._setup_options()
        self._setup_state()

    def _setup_options(self):
        if not isinstance(self.run_id, str) or not _RUN_ID.fullmatch(self.run_id):
            raise LocalReleaseError('local-release-run-id-invalid')
        if self.image_mode not in ('refresh', 'existing'):
            raise LocalReleaseError('local-release-image-mode-invalid')
        if self.test_modules is not None and (not isinstance(self.test_modules, tuple)):
            raise LocalReleaseError('local-release-test-modules-invalid')
        if self.test_modules == ():
            raise LocalReleaseError('local-release-test-modules-empty')
        if self.test_modules is not None and any((not isinstance(module, str) for module in self.test_modules)):
            raise LocalReleaseError('local-release-test-modules-invalid')
        self.root = _root(self.project_root)
        self.installation_lock = ExitStack()
        try:
            self.selection = read_release_selection(self.root)
        except ValueError as error:
            raise LocalReleaseError('local-release-project-selection-invalid') from error
        self.cleanup_runner = self.runner
        self.default_runner = self.runner is None
        if self.runner is None:
            self.runner = lambda argv, cwd: subprocess.run(argv, cwd=cwd, text=True, capture_output=True, check=False)
        self.product = self._product_path()
        self.installed = _target(self.root, self.selection.control_relative / '000_ANECHOIC_framework', label='installed-root')

    def _product_path(self):
        return _target(self.root, Path(_DEFAULT_PRODUCT), label="product-root")

    def _setup_state(self):
        self.package = self.prepared_product = self.staging = None
        self.package_identity, self.product_identity, self.readiness = {}, {}, {}
        self.candidate_image = self.candidate_fingerprint = self.production_port = None
        self.runtime = _target(self.root, Path('.anechoic_runtime/simple_local_release/package'), label='simple-runtime')
        if self.product == self.installed:
            raise LocalReleaseError('local-release-target-invalid')
        self.failed_step = 'validate_inputs'
        self.endpoint = self.canary_endpoint = self.receipt_path = self.test_log_path = None
        self.test_log_paths: dict[str, str] = {}
        self.cleanup_note = 'No proven superseded Project-owned image identity was available; none was removed.'
        self.cleanup_pending, self.cleanup = False, None
        self.test_scope, self.test_selection = 'static and functional', 'configured required tests'
        self.selected_test_modules = None

    def _phase(self, phase):
        if phase == 'validate inputs':
            self._validate_inputs(phase)
        elif phase == 'bump candidate version':
            self._bump_version()
        elif phase in _TEST_GATES:
            self._run_tests(phase)
        elif phase == 'copy active sources':
            self._copy_sources()
        elif phase == 'copy product to installed framework':
            self._copy_product()
        elif phase == 'build package':
            self._build_package()
        elif phase == 'prepare candidate image':
            self._prepare_image()
        elif phase == 'install project runtime':
            self._install_runtime()
        else:
            self._start_mcp()

    def _validate_inputs(self, phase):
        self.failed_step = 'validate_inputs'
        self.production_port = package_phases.validate_inputs(self.root, self.selection, self.product, self.installed, self.runtime)
        if self._source_binding() is None:
            self.failed_step = "bump_candidate_version"
            _read_version(self.root)

    def _run_tests(self, phase):
        self.failed_step = phase.replace(' ', '_')
        suite_phase = _TEST_GATES[phase]
        log_phase = "image" if suite_phase == "image-tests" else suite_phase
        options = self._test_gate_options()
        options["functional_fast"] = self.functional_suite == "fast"
        if suite_phase == "canary" and self.canary_endpoint is not None:
            _verify_package(self.package, self.package_identity)
            if "image" in self.test_log_paths:
                self.test_log_paths.setdefault("canary", self.test_log_paths["image"])
            self.test_log_path = self.test_log_paths.get("canary")
            return
        try:
            observed_endpoint = run_gate(
                self.root, suite_phase, self.candidate_image, self.package, self.package_identity,
                self.selection, self.run_id, None if self.default_runner else self.runner,
                self.test_log_paths, verify=_verify_package, target=_target, named_file=tempfile.NamedTemporaryFile,
                logged_process=partial(run_logged_test_process, lock_fd=self.lock_fd, check_abort=self.journal.check_abort),
                failed_output=_failed_test_output, record_logs=self.journal.record_logs, **options,
            )
        finally:
            self.test_log_path = self.test_log_paths.get(log_phase)
        if observed_endpoint is not None and self.canary_endpoint is None:
            self.canary_endpoint = observed_endpoint
        return observed_endpoint

    def _test_gate_options(self):
        return {}

    def _copy_sources(self):
        self.failed_step = 'copy_active_sources'
        package_phases.copy_sources(self.root, self.selection, self.run_id, self.product)

    def _copy_product(self):
        self.failed_step = 'copy_product_to_installed_framework'
        package_phases.copy_product(self.root, self.selection, self.installation_lock, self.package, self.package_identity, self.prepared_product, self.product_identity, self.installed)

    def _build_package(self):
        self.failed_step = 'build_package'
        self.staging = _new_staging_directory(self.root, f'{self.run_id}-')
        self.journal.data["staging"] = self.staging.relative_to(self.root).as_posix()
        self.journal.save()
        self.prepared_product, self.product_identity, self.package, self.package_identity = package_phases.build_package(self.root, self.selection, self.product, self.staging)

    def _prepare_image(self):
        self.failed_step = 'prepare_candidate_image'
        self.manager, self.candidate_image, self.candidate_fingerprint = package_phases.prepare_image(
            self.root, self.selection, self.staging, self.package, self.package_identity,
            self.prepared_product, self.product_identity, self.cleanup_runner, provenance=self._image_provenance(),
        )

    def _install_runtime(self):
        self.failed_step = 'install_project_runtime'
        package_phases.install_runtime(self.root, self.package, self.package_identity, self.runtime, self.candidate_image, self.candidate_fingerprint)

    def _observe_launcher_image(self):
        return _launcher_image(self.selection)

    def _start_mcp(self):
        self.failed_step = 'start_mcp'
        existing = self._find_running() if self.resume else None
        if existing is not None:
            existing = reconcile_release_container(
                self.root, self.selection, self.candidate_image, self.candidate_fingerprint,
                self.production_port, existing, self.cleanup_runner, run_id=self.run_id,
            )
        self._prepare_cleanup()
        run_id = self.run_id
        if existing is None:
            existing, self.cleanup_note, self.cleanup_pending = previous_container(
                self.root, self.selection, self.prior_project, self.candidate_image, self.cleanup,
                self.runner, self.cleanup_runner, image_labels, self.cleanup_note,
            )
            if existing is not None:
                run_id = None
                self.journal.data["adopted_container"] = existing
                self.journal.save()
        self.endpoint = start_container(
            self.root, self.selection, self.candidate_image, self.candidate_fingerprint,
            self.production_port, self.cleanup_runner, existing_container=existing, run_id=run_id, evidence=self.readiness,
        )

    def _prepare_cleanup(self):
        self.cleanup = cleanup_stopped_containers(
            self.root, self.selection.instance_id, self.selection.control_relative.as_posix(),
            self.candidate_image, self.candidate_fingerprint, self.cleanup_runner,
        )
        if self.prior_image is not None:
            self.cleanup.images.add(self.prior_image)

    def _find_running(self):
        return find_release_container(self.root, self.selection, self.run_id, self.runner)

    def _adopt_running(self):
        adopted = self.journal.data.get("adopted_container")
        existing = adopted or self._find_running()
        if existing is None:
            raise LocalReleaseError("local-release-resume-container-missing")
        endpoint = verify_release_container(
            self.root, self.selection, self.candidate_image, self.candidate_fingerprint,
            self.production_port, existing, self.cleanup_runner, run_id=None if adopted else self.run_id,
            evidence=self.readiness,
        )
        if endpoint != self.endpoint:
            raise LocalReleaseError("local-release-resume-endpoint-changed")

    def _receipt_evidence(self):
        elapsed = self._release_seconds()
        return release_evidence(self) | {
            "functional_suite": self.functional_suite, "ready_seconds": elapsed,
            "fast_target_met": elapsed <= FAST_TARGET_SECONDS if elapsed is not None and self.functional_suite == "fast" else None,
            "fast_limit_met": elapsed <= FAST_LIMIT_SECONDS if elapsed is not None and self.functional_suite == "fast" else None,
        }

    def _after_start(self):
        if not self.journal.data.get("production_tagged"):
            self.failed_step = 'promote_candidate_image'
            try:
                self.manager.mark_production_image(self.candidate_image)
            except (RuntimeError, OSError):
                self.cleanup_pending = True
                self.cleanup_note += '\nProduction image tag failed. Cleanup deferred.'
                return reports.record_receipt(self)
            self.journal.data["production_tagged"] = True
            self.journal.save()
        self.failed_step = 'final'
        if self.cleanup is None:
            self._prepare_cleanup()
        cleanup_stopped_containers(self.root, self.selection.instance_id, self.selection.control_relative.as_posix(), self.candidate_image, self.candidate_fingerprint, self.cleanup_runner, cleanup=self.cleanup)
        try:
            history = _project_path(self.root, Path('.anechoic_runtime/simple_local_release/ready-images.json'), label='simple-image-history')
            previous_images = record_ready_images(history, self.selection.instance_id, self.candidate_image, self.prior_image)
        except (OSError, ValueError, LocalReleaseError):
            self.cleanup.pending = True
            self.cleanup.notes.append('Image history unavailable. Retained existing images.')
        else:
            cleanup_obsolete_images(self.root, self.candidate_image, self.candidate_fingerprint, self.cleanup, self.cleanup_runner, previous_images=previous_images)
        try:
            self.manager.prune_build_cache()
        except (OSError, RuntimeError):
            self.cleanup.pending = True
            self.cleanup.notes.append('Docker build cache cleanup failed.')
        if self.prior_image is not None and self.previous_image is None and (self.prior_image != self.candidate_image):
            self.cleanup.pending = True
            self.cleanup.notes.append('Prior image retained: readiness evidence unavailable.')
        try:
            removed, blocked = prune_temporary_files(self.root)
            self.cleanup.notes.append(f'Removed {removed} temporary paths older than 48 hours.')
            if blocked:
                self.cleanup.pending = True
                self.cleanup.notes.append(f'Temporary file cleanup blocked on {len(blocked)} paths. First error: {blocked[0]}')
        except (OSError, LocalReleaseError):
            self.cleanup.pending = True
            self.cleanup.notes.append('Temporary file cleanup failed.')
        self.cleanup_pending |= self.cleanup.pending
        self.cleanup_note = '\n'.join([self.cleanup_note, *self.cleanup.notes])
        reports.record_receipt(self)

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
            if self.failed_step == 'installation_lock':
                print(f'Local release installation lock failed: {error}', file=sys.stderr, flush=True)
            if self.journal is not None:
                self.journal.record_failure(self.failed_step, error, self.test_log_paths)
            staging_note = (f"Retained temporary staging: `{self.staging.relative_to(self.root).as_posix()}`.\n"
                            if self.staging is not None else "")
            report_path = reports.write_failure(self.root, self.run_id, self.failed_step, self.image_mode, self.test_scope, self.test_selection, error, self.test_log_paths, self.endpoint, self.cleanup_note, self.cleanup, staging_note)
            return {'outcome': 'failed',
                    'failed_step': self.failed_step,
                    'report_path': report_path,
                    'error_type': type(error).__name__,
                    'error': str(error)[:8500],
                    'test_log_path': self.test_log_path,
                    'test_log_paths': self.test_log_paths,
                    'endpoint': self.endpoint,
                    'canary_endpoint': self.canary_endpoint,
                    'test_scope': self.test_scope,
                    'test_modules': self.selected_test_modules,
                    'image_mode': self.image_mode, **failure_evidence(self.journal, error, self.production_port)}
        finally:
            self.installation_lock.close()
