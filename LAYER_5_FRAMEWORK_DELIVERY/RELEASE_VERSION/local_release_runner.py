
"""Ordered phases for the direct local Release."""

from __future__ import annotations

import subprocess
import sys
import tempfile
from contextlib import ExitStack
from pathlib import Path
from typing import Any

from .release_cleanup import cleanup_obsolete_images, cleanup_stopped_containers  # noqa: E402
from .release_cleanup_identity import image_labels  # noqa: E402
from .release_cleanup_images import record_ready_images  # noqa: E402
from .release_container import start_container  # noqa: E402
from .release_inputs import read_release_selection  # noqa: E402
from .local_release_gates import run_gate  # noqa: E402
from .local_release_previous import previous_container  # noqa: E402
from . import local_release_package_phases as package_phases  # noqa: E402
from . import local_release_reports as reports  # noqa: E402
from .local_release_safety import _git_checkpoint, _installation_lock, _new_staging_directory  # noqa: E402
from .local_release_test_process import run_logged_test_process  # noqa: E402
from .release_support import (  # noqa: E402
    LocalReleaseError,
    _DEFAULT_PRODUCT,
    _RUN_ID,
    _build_predecessor,
    _cleanup_staging,
    _launcher_image,
    _project_path,
    _read_version,
    _root,
    _target,
    _verify_package,
    _failed_test_output as _support_failed_test_output,
)


def _failed_test_output(root: Path, run_id: str, result: Any, *, log_path: str | None = None) -> str:
    return _support_failed_test_output(
        root, run_id, result, log_path=log_path, named_temporary_file=tempfile.NamedTemporaryFile,
    )


class LocalReleaseRun:

    def __init__(self, project_root, run_id, runner, test_modules, image_mode):
        self.project_root = project_root
        self.run_id = run_id
        self.runner = runner
        self.test_modules = test_modules
        self.image_mode = image_mode
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
        self.product = _target(self.root, Path(_DEFAULT_PRODUCT), label='product-root')
        self.installed = _target(self.root, self.selection.control_relative / '000_ANECHOIC_framework', label='installed-root')

    def _setup_state(self):
        self.package: Path | None = None
        self.prepared_product: Path | None = None
        self.staging: Path | None = None
        self.package_identity: dict[str, tuple[str, int]] = {}
        self.product_identity: dict[str, tuple[str, int]] = {}
        self.candidate_image: str | None = None
        self.candidate_fingerprint: str | None = None
        self.production_port: int | None = None
        self.runtime = _target(self.root, Path('.anechoic_runtime/simple_local_release/package'), label='simple-runtime')
        if self.product == self.installed:
            raise LocalReleaseError('local-release-target-invalid')
        self.failed_step = 'validate_inputs'
        self.endpoint: str | None = None
        self.canary_endpoint: str | None = None
        self.receipt_path: str | None = None
        self.test_log_path: str | None = None
        self.test_log_paths: dict[str, str] = {}
        self.cleanup_note = 'No proven superseded Project-owned image identity was available; none was removed.'
        self.cleanup_pending = False
        self.cleanup = None
        self.test_scope = 'static and unit'
        self.selected_test_modules = None
        self.test_selection = 'configured required tests'
        self.phases = ('validate inputs',
                        'bump candidate version', 'static tests', 'unit tests', 'copy active sources', 'build package',
                        'prepare candidate image', 'verify candidate image',
                        'copy product to installed framework', 'install project runtime', 'start mcp', 'final')
        self.checkpoint_paths = {'validate inputs': ('.',), 'static tests': ('version.toml',), 'build package': ('LAYER_1_META_ONTOLOGY_C9', 'LAYER_2_META_METHODOLOGY_C58'), 'install project runtime': (self.installed.relative_to(self.root).as_posix(),), 'start mcp': ('.agents/skills/ane',)}

    def _execute(self):
        self.failed_step = 'installation_lock'
        self.installation_lock.enter_context(_installation_lock(self.root, self.selection))
        self.failed_step = 'validate_inputs'
        try:
            self.previous_image = _build_predecessor(self.selection)
        except LocalReleaseError:
            if self.image_mode != 'existing':
                raise
            self.previous_image = None
        self.prior_image = self.previous_image or _launcher_image(self.selection)
        self.prior_project = self.selection.instance_id if self.prior_image is not None else None
        self.head = None
        for phase in self.phases:
            print(f'Local release phase START: {phase}', file=sys.stderr, flush=True)
            self.failed_step = 'validate_project_selection'
            if read_release_selection(self.root) != self.selection:
                raise LocalReleaseError('local-release-project-selection-changed')
            self.failed_step = f"git_before_{phase.replace(' ', '_')}"
            self.head = _git_checkpoint(self.root, self.runner, phase, self.checkpoint_paths.get(phase, ()), self.head)
            if phase == 'final':
                continue
            self._phase(phase)

    def _phase(self, phase):
        if phase == 'validate inputs':
            self._validate_inputs(phase)
        elif phase == 'bump candidate version':
            self._bump_version(phase)
        elif phase in {'static tests', 'unit tests', 'verify candidate image'}:
            self._run_tests(phase)
        elif phase == 'copy active sources':
            self._copy_sources(phase)
        elif phase == 'copy product to installed framework':
            self._copy_product(phase)
        elif phase == 'build package':
            self._build_package(phase)
        elif phase == 'prepare candidate image':
            self._prepare_image(phase)
        elif phase == 'install project runtime':
            self._install_runtime(phase)
        else:
            self._start_mcp()

    def _validate_inputs(self, phase):
        self.failed_step = 'validate_inputs'
        self.production_port = package_phases.validate_inputs(self.root, self.selection, self.product, self.installed, self.runtime)

    def _bump_version(self, phase):
        self.failed_step = 'bump_candidate_version'
        version_path, next_version_text = _read_version(self.root)
        version_path.write_text(next_version_text, encoding='utf-8')

    def _run_tests(self, phase):
        self.failed_step = phase.replace(' ', '_')
        suite_phase = 'image' if phase == 'verify candidate image' else phase.split()[0]
        self.test_log_path = None
        try:
            observed_endpoint = run_gate(self.root, phase, self.candidate_image, self.package, self.package_identity, self.selection, self.run_id, None if self.default_runner else self.runner, self.test_log_paths, verify=_verify_package, target=_target, named_file=tempfile.NamedTemporaryFile, logged_process=run_logged_test_process, failed_output=_failed_test_output)
        finally:
            self.test_log_path = self.test_log_paths.get(suite_phase)
        if suite_phase == 'image':
            self.canary_endpoint = observed_endpoint

    def _copy_sources(self, phase):
        self.failed_step = 'copy_active_sources'
        package_phases.copy_sources(self.root, self.selection, self.run_id, self.product)

    def _copy_product(self, phase):
        self.failed_step = 'copy_product_to_installed_framework'
        package_phases.copy_product(self.root, self.selection, self.installation_lock, self.package, self.package_identity, self.prepared_product, self.product_identity, self.installed)

    def _build_package(self, phase):
        self.failed_step = 'build_package'
        self.staging = _new_staging_directory(self.root, f'{self.run_id}-')
        self.prepared_product, self.product_identity, self.package, self.package_identity = package_phases.build_package(self.root, self.selection, self.product, self.staging)

    def _prepare_image(self, phase):
        self.failed_step = 'prepare_candidate_image'
        self.manager, self.candidate_image, self.candidate_fingerprint = package_phases.prepare_image(self.root, self.selection, self.staging, self.package, self.package_identity, self.prepared_product, self.product_identity, self.cleanup_runner)

    def _install_runtime(self, phase):
        self.failed_step = 'install_project_runtime'
        package_phases.install_runtime(self.root, self.package, self.package_identity, self.runtime, self.candidate_image, self.candidate_fingerprint)

    def _start_mcp(self):
        self.failed_step = 'start_mcp'
        existing_container = None
        self.cleanup = cleanup_stopped_containers(self.root, self.selection.instance_id, self.selection.control_relative.as_posix(), self.candidate_image, self.candidate_fingerprint, self.cleanup_runner)
        if self.prior_image is not None:
            self.cleanup.images.add(self.prior_image)
        existing_container, self.cleanup_note, self.cleanup_pending = previous_container(self.root, self.selection, self.prior_project, self.candidate_image, self.cleanup, self.runner, self.cleanup_runner, image_labels, self.cleanup_note)
        self.endpoint = start_container(self.root, self.selection, self.candidate_image, self.candidate_fingerprint, self.production_port, self.cleanup_runner, existing_container=existing_container)
        self._after_start()

    def _after_start(self):
        try:
            self.manager.mark_production_image(self.candidate_image)
        except RuntimeError:
            self.cleanup.pending = True
            self.cleanup.notes.append('Production image display tag failed: Runtime image operation failed')
        cleanup_stopped_containers(self.root, self.selection.instance_id, self.selection.control_relative.as_posix(), self.candidate_image, self.candidate_fingerprint, self.cleanup_runner, cleanup=self.cleanup)
        try:
            history = _project_path(self.root, Path('.anechoic_runtime/simple_local_release/ready-images.json'), label='simple-image-history')
            previous_images = record_ready_images(history, self.selection.instance_id, self.candidate_image, self.prior_image)
        except (OSError, ValueError, LocalReleaseError):
            self.cleanup.pending = True
            self.cleanup.notes.append('Image history unavailable. Retained existing images.')
        else:
            if self.prior_image == self.candidate_image:
                self.cleanup.notes.append('Image reused. Retained existing rollback images.')
            else:
                cleanup_obsolete_images(self.root, self.candidate_image, self.candidate_fingerprint, self.cleanup, self.cleanup_runner, previous_images=previous_images)
        if self.prior_image is not None and self.previous_image is None and (self.prior_image != self.candidate_image):
            self.cleanup.pending = True
            self.cleanup.notes.append('Prior image retained: readiness evidence unavailable.')
        self.cleanup_pending |= self.cleanup.pending
        self.cleanup_note = '\n'.join([self.cleanup_note, *self.cleanup.notes])
        receipt = reports.receipt_path(self.root, self.run_id)
        staging_note = _cleanup_staging(self.root, self.staging)
        self.staging = None
        self.receipt_path = reports.write_receipt(self.root, receipt, self.run_id, self.image_mode, self.test_scope, self.test_selection, self.canary_endpoint, self.endpoint, self.test_log_paths, self.cleanup_note, staging_note)

    def run(self):
        try:
            self._execute()
        except (Exception, KeyboardInterrupt) as error:
            if self.failed_step == 'installation_lock':
                print(f'Local release installation lock failed: {error}', file=sys.stderr, flush=True)
            staging_note = _cleanup_staging(self.root, self.staging)
            report_path = reports.write_failure(self.root, self.run_id, self.failed_step, self.image_mode, self.test_scope, self.test_selection, error, self.test_log_paths, self.endpoint, self.cleanup_note, self.cleanup, staging_note)
            return {'outcome': 'failed',
                    'failed_step': self.failed_step,
                    'report_path': report_path,
                    'error_type': type(error).__name__,
                    'test_log_path': self.test_log_path,
                    'test_log_paths': self.test_log_paths,
                    'endpoint': self.endpoint,
                    'canary_endpoint': self.canary_endpoint,
                    'test_scope': self.test_scope,
                    'test_modules': self.selected_test_modules,
                    'image_mode': self.image_mode}
        finally:
            self.installation_lock.close()
        return {'outcome': 'completed_with_cleanup_pending' if self.cleanup_pending else 'completed',
                    'failed_step': None,
                    'report_path': None,
                    'receipt_path': self.receipt_path,
                    'test_log_path': self.test_log_path,
                    'test_log_paths': self.test_log_paths,
                    'endpoint': self.endpoint,
                    'canary_endpoint': self.canary_endpoint,
                    'test_scope': self.test_scope,
                    'test_modules': self.selected_test_modules,
                    'image_mode': self.image_mode}
