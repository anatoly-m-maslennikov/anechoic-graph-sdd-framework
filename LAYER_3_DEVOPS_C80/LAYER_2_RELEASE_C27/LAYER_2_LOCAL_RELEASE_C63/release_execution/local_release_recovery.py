"""Continue a Local Release from verified phase outputs."""

import sys
from time import time

from LAYER_1_RUNTIME_IMAGES_C81.LAYER_1_RUNTIME_IMAGES_C81__shared import (
    LocalReleaseError,
    _git_checkpoint,
    _installation_lock,
    _verify_package,
)
from LAYER_1_RUNTIME_IMAGES_C81.input_selection.input_selection__shared import (
    read_release_selection,
)

from .. import local_release_package_phases as package_phases
from ..local_release_delivery import (
    COPY_PHASES,
    INSTALL_PHASES,
    abort_lock,
    check_targets,
    launcher_lock,
    verify_recorded_targets,
)
from .local_release_recovery_artifacts import RecoveryArtifacts
from ..local_release_progress import (
    BUILD,
    CANARY,
    COPY,
    IMAGE,
    IMAGE_TEST,
    STATIC,
    ReleaseProgress,
)
from ..local_release_state import PHASES, Journal
from ..release_support import _build_predecessor

_VERSION = "bump candidate version"
_PUBLISH = "start mcp"
FAST_TARGET_SECONDS = 600
FAST_LIMIT_SECONDS = 900


class ResumableRelease(RecoveryArtifacts, ReleaseProgress):
    def _execute(self):
        if self.release_started_at is None:
            self.release_started_at = time()
        self.failed_step = "installation_lock"
        self.lock_fd = self.installation_lock.enter_context(
            _installation_lock(self.root, self.selection)
        )
        self.failed_step = "resume" if self.resume else "validate_inputs"
        options = [
            self.image_mode,
            list(self.test_modules) if self.test_modules is not None else None,
        ]
        self.journal = Journal(
            self.root,
            self.run_id,
            self.selection,
            options,
            self.resume,
            source_binding=self._source_binding(),
            started_at=self.release_started_at,
        )
        self._select_functional_suite()
        self._bind_target()
        self._phase_input_cache = {}
        if self.resume:
            self._restore_options()
            with abort_lock(self.root, self.journal.path):
                self.journal.abort_path().unlink(missing_ok=True)
            recorded = self._resume()
            if recorded is not None:
                return recorded
        else:
            self.head = None
        self._select_previous()
        for phase in PHASES:
            if phase not in self.journal.data["done"]:
                self._run_phase(phase)
        return None

    def _source_binding(self):
        return None

    def _release_seconds(self):
        started_at = self.journal.data.get("release_started_at")
        return (
            None
            if started_at is None
            else round(max(0, time() - started_at), 3)
        )

    def _select_functional_suite(self):
        requested = self.requested_functional_suite
        recorded = self.journal.data.get("functional_suite", "full")
        self.functional_suite = (
            recorded if self.resume else requested or "full"
        )
        if self.functional_suite not in {"full", "fast"} or (
            self.resume and requested not in (None, recorded)
        ):
            raise LocalReleaseError("local-release-functional-suite-invalid")
        if self.functional_suite == "fast":
            self.test_selection = (
                "recently failing Test Packages and a sampled 10% of others"
            )
            if not self.resume:
                self.journal.data["functional_suite"] = self.functional_suite
                self.journal.save()

    def _restore_options(self):
        mode, modules = self.journal.data["options"]
        selected = (
            list(self.test_modules) if self.test_modules is not None else None
        )
        if (
            mode not in ("refresh", "existing")
            or (
                self.requested_image_mode is not None
                and self.image_mode != mode
            )
            or (selected is not None and selected != modules)
        ):
            raise LocalReleaseError("local-release-resume-options-changed")
        self.image_mode = mode
        self.test_modules = tuple(modules) if modules is not None else None

    def _select_previous(self):
        data = self.journal.data
        if "previous_image" not in data:
            self.failed_step = "validate_inputs"
            try:
                previous = _build_predecessor(self.selection)
            except LocalReleaseError:
                if self.image_mode != "existing":
                    raise
                previous = None
            data.update(
                previous_image=previous,
                prior_image=previous or self._observe_launcher_image(),
            )
            self.journal.save()
        self.previous_image, self.prior_image = (
            data["previous_image"],
            data["prior_image"],
        )
        self.prior_project = (
            self.selection.instance_id
            if self.prior_image is not None
            else None
        )

    def _resume(self):
        data = self.journal.data
        self.journal.delivery()
        self._restore_progress()
        self._refresh_inputs()
        result = data.get("result")
        if result is not None and result["outcome"] == "completed":
            self._lock_launcher()
            self._restore_artifacts(completed=True)
            self._verify_installed()
            return result
        self._load_reusable_artifacts()
        if data.get("delivery") is not None:
            self._lock_launcher()
        if _PUBLISH in data["done"]:
            self._resume_cleanup()
        else:
            self._verify_installed()
        return None

    def _restore_progress(self):
        data = self.journal.data
        self.head, self.production_port = data.get("head"), data.get("port")
        if self.production_port is not None:
            if (
                package_phases.project_port(self.root, self.selection)
                != self.production_port
            ):
                raise LocalReleaseError("local-release-resume-port-changed")
        self.test_log_paths = data["logs"].copy()
        self._restore_log_path()
        self.canary_endpoint, self.endpoint = (
            data.get("canary"),
            data.get("endpoint"),
        )
        if _VERSION in data["done"]:
            self._assert_version()

    def _checkpoint_refreshed_inputs(self):
        return _git_checkpoint(
            self.root, self.runner, "resume inputs", (".",), None
        )

    def _lock_launcher(self):
        if not getattr(self, "_launcher_locked", False):
            launcher_lock(self)
            self._launcher_locked = True

    def _run_phase(self, phase):
        self.failed_step = phase.replace(" ", "_")
        self.journal.check_abort()
        print(
            f"Local release phase START: {self._phase_label(phase)}",
            file=sys.stderr,
            flush=True,
        )
        self.failed_step = "validate_project_selection"
        if read_release_selection(self.root) != self.selection:
            raise LocalReleaseError("local-release-project-selection-changed")
        data = self.journal.data
        interrupted = self.resume and data["working"] == phase
        if phase == BUILD:
            self.failed_step = "build_package"
            self._verify_build_inputs()
        if phase == IMAGE:
            self._verify_release_inputs()
        self.journal.begin(phase)
        self._checkpoint_phase(phase, interrupted)
        if phase in (*INSTALL_PHASES, _PUBLISH):
            self._prepare_delivery_phase(phase)
        if phase in {STATIC, "functional tests", IMAGE_TEST, CANARY}:
            self._ensure_preflight()
            self._run_verified_gate(phase)
        elif phase == "final":
            self._after_start()
        elif phase not in COPY_PHASES or not self._verify_copy_intent(phase):
            self._phase(phase)
        if phase == "validate inputs":
            self._ensure_preflight()
        if phase in (BUILD, IMAGE, _PUBLISH):
            self._verify_release_inputs()
        self.journal.finish(phase, **self._phase_output(phase))
        self.journal.check_abort()

    def _prepare_delivery_phase(self, phase):
        self.failed_step = "validate_gate_inputs"
        data = self.journal.data
        first_claim = phase in INSTALL_PHASES and data.get("delivery") is None
        if first_claim:
            self._ensure_preflight()
        self._verify_release_inputs()
        self._lock_launcher()
        if first_claim:
            self._verify_gate_proofs()
            self._restore_artifacts()
        self._verify_canary_inputs()
        if phase in INSTALL_PHASES:
            self._before_delivery(phase)
            with abort_lock(self.root, self.journal.path):
                self.journal.check_abort()
                self.journal.delivery(claim=True)

    def _checkpoint_phase(self, phase, interrupted):
        data = self.journal.data
        self.failed_step = f"git_before_{phase.replace(' ', '_')}"
        if data.get("checkpoint") == phase:
            return
        self.head = self._run_git_checkpoint(phase, interrupted=interrupted)
        data.update(head=self.head, checkpoint=phase)
        if data.get("delivery") is None:
            data["accepted_source_sha"] = self._phase_source()
        self.journal.save()

    def _before_delivery(self, phase):
        pass

    def _phase_label(self, phase):
        return phase

    def _verify_build_inputs(self):
        self._verify_release_inputs()
        verify_recorded_targets(self, COPY)

    def _verify_copy_intent(self, phase):
        self.failed_step = phase.replace(" ", "_")
        if phase in INSTALL_PHASES:
            _verify_package(self.package, self.package_identity)
            _verify_package(self.prepared_product, self.product_identity)
        return check_targets(self, phase, intent=True)

    def _phase_output(self, phase):
        if phase == "validate inputs":
            return {"port": self.production_port}
        if phase == BUILD:
            return {
                "package_identity": self.package_identity,
                "product_identity": self.product_identity,
                "build_source_sha": self._phase_source(),
            }
        if phase == IMAGE:
            return {
                "image_id": self.candidate_image,
                "fingerprint": self.candidate_fingerprint,
            }
        if phase == _PUBLISH:
            return {
                "endpoint": self.endpoint,
                "evidence": self._receipt_evidence(),
            }
        return {"logs": self.test_log_paths, "canary": self.canary_endpoint}

    def _completed_result(self):
        return {
            "outcome": (
                "completed_with_cleanup_pending"
                if self.cleanup_pending
                else "completed"
            ),
            "failed_step": None,
            "report_path": None,
            "receipt_path": self.receipt_path,
            "test_log_path": self.test_log_path,
            "test_log_paths": self.test_log_paths,
            "endpoint": self.endpoint,
            "canary_endpoint": self.canary_endpoint,
            "test_scope": self.test_scope,
            "test_modules": self.selected_test_modules,
            "image_mode": self.image_mode,
            "evidence": self.journal.data["evidence"],
        }
