"""Continue a Local Release from verified phase outputs."""
import sys

from LAYER_1_RUNTIME_IMAGES_C81.LAYER_1_RUNTIME_IMAGES_C81__shared import (
    LocalReleaseError,
    _git_checkpoint,
    _installation_lock,
    _verify_package,
    read_release_selection,
)

from . import local_release_package_phases as package_phases
from .local_release_delivery import (
    COPY_PHASES,
    INSTALL_PHASES,
    check_targets,
    launcher_lock,
    verify_recorded_targets,
)
from .local_release_progress import BUILD, CANARY, COPY, IMAGE, IMAGE_TEST, STATIC, ReleaseProgress
from .local_release_state import PHASES, Journal, completed_result
from .release_support import _build_predecessor

_VERSION = "bump candidate version"
_PUBLISH = "start mcp"


class ResumableRelease(ReleaseProgress):
    def _execute(self):
        self.failed_step = "installation_lock"
        self.lock_fd = self.installation_lock.enter_context(_installation_lock(self.root, self.selection))
        self.failed_step = "resume" if self.resume else "validate_inputs"
        options = [self.image_mode, list(self.test_modules) if self.test_modules is not None else None]
        self.journal = Journal(self.root, self.run_id, self.selection, options, self.resume,
                               source_binding=self._source_binding())
        self._bind_target()
        self._phase_input_cache = {}
        if self.resume:
            self._restore_options()
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

    def _restore_options(self):
        mode, modules = self.journal.data["options"]
        selected = list(self.test_modules) if self.test_modules is not None else None
        if (mode not in ("refresh", "existing")
                or (self.requested_image_mode is not None and self.image_mode != mode)
                or (selected is not None and selected != modules)):
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
            data.update(previous_image=previous, prior_image=previous or self._observe_launcher_image())
            self.journal.save()
        self.previous_image, self.prior_image = data["previous_image"], data["prior_image"]
        self.prior_project = self.selection.instance_id if self.prior_image is not None else None

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
            settings = self.selection.parameters.get("project_mcp")
            if not isinstance(settings, dict) or settings.get("http_port") != self.production_port:
                raise LocalReleaseError("local-release-resume-port-changed")
        self.test_log_paths = data["logs"].copy()
        self._restore_log_path()
        self.canary_endpoint, self.endpoint = data.get("canary"), data.get("endpoint")
        if _VERSION in data["done"]:
            self._assert_version()

    def _checkpoint_refreshed_inputs(self):
        return _git_checkpoint(self.root, self.runner, "resume inputs", (".",), None)

    def _lock_launcher(self):
        if not getattr(self, "_launcher_locked", False):
            launcher_lock(self)
            self._launcher_locked = True

    def _run_phase(self, phase):
        print(f"Local release phase START: {self._phase_label(phase)}", file=sys.stderr, flush=True)
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
            return {"package_identity": self.package_identity, "product_identity": self.product_identity,
                    "build_source_sha": self._phase_source()}
        if phase == IMAGE:
            return {"image_id": self.candidate_image, "fingerprint": self.candidate_fingerprint}
        if phase == _PUBLISH:
            return {"endpoint": self.endpoint, "evidence": self._receipt_evidence()}
        return {"logs": self.test_log_paths, "canary": self.canary_endpoint}

    def _declared_provenance(self):
        return package_phases.release_image_provenance(self.root, self.selection, self.cleanup_runner)

    def _image_provenance(self):
        data = self.journal.data
        if data.get("provenance") is None:
            provenance = self._declared_provenance()
            data["provenance"] = {**provenance, "head_commit": data["build_source_sha"]}
            self.journal.save()
        self._check_image_provenance(data["provenance"])
        return data["provenance"]

    def _check_image_provenance(self, provenance):
        data = self.journal.data
        if not isinstance(provenance, dict) or provenance.get("head_commit") != data.get("build_source_sha"):
            raise LocalReleaseError("local-release-resume-image-provenance-changed")

    def _load_reusable_artifacts(self):
        data = self.journal.data
        try:
            self._restore_artifacts()
        except (LocalReleaseError, OSError, RuntimeError):
            if data.get("delivery") is not None:
                raise
            first = IMAGE if self._package_matches() else BUILD
            self._invalidate(set(PHASES[PHASES.index(first):]))
            self.journal.save()

    def _package_matches(self):
        if self.package is None or any(path.is_symlink() for path in (self.package, self.prepared_product)):
            return False
        try:
            _verify_package(self.package, self.package_identity)
            _verify_package(self.prepared_product, self.product_identity)
            return True
        except (LocalReleaseError, OSError):
            return False

    def _restore_artifacts(self, *, completed=False):
        data = self.journal.data
        if BUILD not in data["done"]:
            return
        self.staging = self.journal.staging()
        if completed:
            self.package, self.prepared_product = self.runtime, self.installed
        else:
            if self.staging is None or not self.staging.is_dir():
                raise LocalReleaseError("local-release-resume-staging-missing")
            self.package, self.prepared_product = self.staging / "package", self.staging / "framework"
        for path in (self.package, self.prepared_product):
            if not path.is_dir() or path.is_symlink():
                raise LocalReleaseError("local-release-resume-staging-invalid")
        self.package_identity = {name: tuple(value) for name, value in data["package_identity"].items()}
        self.product_identity = {name: tuple(value) for name, value in data["product_identity"].items()}
        _verify_package(self.package, self.package_identity)
        if not completed:
            _verify_package(self.prepared_product, self.product_identity)
        if IMAGE in data["done"]:
            self._restore_image(data, self.runtime.parent if completed else self.staging)

    def _restore_image(self, data, build_root):
        self._check_image_provenance(data["provenance"])
        self.candidate_image, self.candidate_fingerprint = data["image_id"], data["fingerprint"]
        self.manager = package_phases.restore_image(self.root, build_root, self.package, data["provenance"],
                                                    self.candidate_image, self.candidate_fingerprint)

    def _verify_installed(self):
        for phase in INSTALL_PHASES:
            if phase in self.journal.data["done"]:
                check_targets(self, phase)

    def _resume_cleanup(self):
        data = self.journal.data
        self._verify_installed()
        self._adopt_running()
        data["evidence"] = self._receipt_evidence()
        if "final" in data["done"]:
            data["done"].remove("final")
            self.journal.save()

    def _completed_result(self):
        return completed_result(self)
