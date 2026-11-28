"""Bind reusable Local Release phase evidence to its inputs and source."""

from LAYER_1_RUNTIME_IMAGES_C81.LAYER_1_RUNTIME_IMAGES_C81__shared import (
    LocalReleaseError,
    _walk_regular_files,
)
from LAYER_1_RUNTIME_IMAGES_C81.input_selection.input_selection__shared import (
    read_release_selection,
)

from .local_release_package_phases import container_settings
from ..local_release_delivery import verify_recorded_targets
from ..local_release_gates import _ROOT as COMMAND_ROOT
from ..local_release_git import ReleaseGitCheckpoints
from .local_release_proofs import (
    PREFLIGHT,
    STATIC,
    COPY,
    BUILD,
    IMAGE as IMAGE,
    IMAGE_TEST,
    CANARY,
    _GATES,
    _tree_digest,
    _target_canary_files,
    _proof_inputs,
    _proved_phases,
    _canary_matches,
    ReleaseProofRecords,
)
from ..local_release_state import PHASES, source_identity
from ..prepare_test_environment import (
    check_locked_engine,
    ensure_test_environment,
)
from ..release_phase_inputs import phase_inputs
from ..snapshot_inputs import target_runtime_digest


class ReleaseProgress(ReleaseProofRecords, ReleaseGitCheckpoints):
    def _target_binding(self):
        binding = [
            self.selection.manifest_sha256,
            target_runtime_digest(self.root),
        ]
        settings = container_settings(self.root)
        if settings is not None:
            binding.append(settings)
        return binding

    def _bind_target(self):
        target = self._target_binding()
        if (
            read_release_selection(self.root) != self.selection
            or self.journal.data.setdefault("target_binding", target) != target
        ):
            raise LocalReleaseError("local-release-resume-binding-changed")

    def _input_identity(self):
        return phase_inputs(
            self.root,
            COMMAND_ROOT,
            external=self.default_runner,
            cache=self._phase_input_cache,
        )

    def _target_canary_identity(self):
        data = self.journal.data
        files = (
            _walk_regular_files(self.installed)
            if self.installed.exists()
            else []
        )
        original = (data.get("canary_inputs") or {}).get("target_install")
        installed = (
            original
            if data.get("delivery") is not None
            else _tree_digest(self.root, files)
        )
        authoring = _target_canary_files(
            self.root, self.selection.control_root, self.installed, files
        )
        return {
            "target": _tree_digest(self.root, authoring),
            "target_install": installed,
        }

    def _phase_source(self):
        return self.head

    def _assert_resume_source(self):
        pass

    def _verify_release_inputs(self):
        if self._target_binding() != self.journal.data["target_binding"]:
            raise LocalReleaseError(
                "local-release-target-runtime-settings-changed"
            )
        if "bump candidate version" in self.journal.data["done"]:
            self._assert_version()
        if self._input_identity() != self.journal.data.get("inputs"):
            raise LocalReleaseError("local-release-gate-inputs-changed")

    def _new_proof(self, phase, inputs, source, *, legacy=False):
        data = self.journal.data
        proof = {
            "source_sha": source,
            "inputs": _proof_inputs(phase, data, inputs),
            "log_path": self.test_log_paths.get(_GATES[phase][0]),
        }
        if proof["log_path"] is not None and not legacy:
            proof["log_identity"] = self._log_identity(proof["log_path"])
        if phase == CANARY:
            proof["endpoint"] = self.canary_endpoint
        if legacy:
            proof[
                "legacy_combined"
                if phase in (IMAGE_TEST, CANARY)
                else "legacy"
            ] = True
        return proof

    def _run_verified_gate(self, phase):
        self.failed_step = "validate_gate_inputs"
        self._verify_release_inputs()
        data = self.journal.data
        legacy_image = (
            phase == IMAGE_TEST
            and self.default_runner
            and self._test_gate_options().get("source_root") is not None
        )
        checks_target = phase == CANARY or (
            legacy_image and CANARY not in data["done"]
        )
        target = self._target_canary_identity() if checks_target else None
        if phase == CANARY and target != data.get("canary_inputs"):
            self.canary_endpoint = None
        observed_endpoint = self._run_tests(phase)
        self.failed_step = "validate_project_selection"
        if read_release_selection(self.root) != self.selection:
            raise LocalReleaseError("local-release-project-selection-changed")
        self.failed_step = "validate_gate_inputs"
        self._check_resume_head()
        self._verify_release_inputs()
        if checks_target and (
            phase == CANARY or observed_endpoint is not None
        ):
            if target != self._target_canary_identity():
                raise LocalReleaseError("local-release-canary-inputs-changed")
            data["canary_inputs"] = target
            if phase == IMAGE_TEST:
                self.canary_endpoint = observed_endpoint
        data["proofs"][phase] = self._new_proof(
            phase, data["inputs"], self._phase_source()
        )

    def _canary_inputs_match(self):
        expected = self.journal.data.get("canary_inputs")
        return (
            expected is not None and expected == self._target_canary_identity()
        )

    def _verify_canary_inputs(self):
        data = self.journal.data
        legacy = data["proofs"].get(CANARY, {}).get("legacy_combined")
        if not self._canary_inputs_match() and not (
            legacy and data.get("delivery") is not None
        ):
            raise LocalReleaseError("local-release-canary-inputs-changed")

    def _ensure_preflight(self):
        data = self.journal.data
        if self.default_runner and not self._checked_test_environment:
            self.failed_step = "preflight_tests"
            source = self._test_gate_options().get("source_root", self.root)
            ensure_test_environment(source, self.journal)
            check_locked_engine(source)
            self._checked_test_environment = True
        if data.get("preflight"):
            return
        if data.get("inputs") is None:
            self.failed_step = "validate_gate_inputs"
            data["inputs"] = self._input_identity()
            self.journal.save()
        self._run_verified_gate(PREFLIGHT)
        data.update(preflight=True, logs=self.test_log_paths)
        self.journal.save()

    def _legacy_identity(self, legacy, current):
        if (
            isinstance(legacy, str)
            and source_identity(
                self.root, COMMAND_ROOT, external=self.default_runner
            )
            == legacy
        ):
            return current
        return None

    def _legacy_proofs(self, current):
        data = self.journal.data
        if "legacy_inputs" not in data:
            return False
        previous = self._legacy_identity(data["legacy_inputs"], current)
        if previous is None:
            if data.get("delivery") is not None:
                raise LocalReleaseError("local-release-gate-inputs-changed")
            data.pop("legacy_inputs")
            return True
        if CANARY in data["done"]:
            if not _canary_matches({"endpoint": self.canary_endpoint}, data):
                raise LocalReleaseError("local-release-resume-journal-invalid")
            if "image" in self.test_log_paths:
                self.test_log_paths.setdefault(
                    "canary", self.test_log_paths["image"]
                )
                data["logs"].update(self.test_log_paths)
        data.pop("legacy_inputs")
        data["inputs"] = previous
        if BUILD in data["done"] and not data.get("build_source_sha"):
            data["build_source_sha"] = data.get("accepted_source_sha")
        for phase in _proved_phases(data):
            source = data.get("accepted_source_sha")
            if not data.get("source_binding") and phase not in (
                IMAGE_TEST,
                CANARY,
            ):
                source = None
            data["proofs"][phase] = self._new_proof(
                phase, previous, source, legacy=True
            )
        data["legacy_proofs"] = data["proofs"].copy()
        return False

    def _refresh_inputs(self):
        data = self.journal.data
        self._assert_resume_source()
        if "start mcp" in data["done"] and "legacy_inputs" in data:
            if not _canary_matches({"endpoint": self.canary_endpoint}, data):
                raise LocalReleaseError("local-release-resume-journal-invalid")
            self._reconcile_legacy_source()
            return
        current = self._input_identity()
        legacy_changed = self._legacy_proofs(current)
        previous = data.get("inputs")
        if "start mcp" in data["done"] and previous is not None:
            current["environment"] = previous["environment"]
        changed = (
            legacy_changed or previous is not None and current != previous
        )
        rebuild = (
            legacy_changed
            or previous is not None
            and previous["runtime"] != current["runtime"]
        )
        invalid = self._invalid_gate_proofs(current)
        if data.get("delivery") is not None:
            self._check_claimed_inputs(changed or invalid)
            return
        if data.get("canary") and (
            changed
            and CANARY not in data["done"]
            or not self._canary_inputs_match()
        ):
            invalid.add(CANARY)
        self._check_resume_head(allow_fix=changed)
        if COPY in data.get("targets", {}) and (
            changed or COPY in data["done"]
        ):
            verify_recorded_targets(self, COPY)
        if changed:
            self._accept_input_fix()
        self._finish_refresh(data, current, changed, rebuild, invalid)

    def _finish_refresh(self, data, current, changed, rebuild, invalid):
        if rebuild:
            invalid.update(PHASES[PHASES.index(STATIC) :])
            invalid.add(PREFLIGHT)
        if (
            changed
            or invalid
            or self._phase_source() != data.get("accepted_source_sha")
        ):
            self._invalidate(invalid)
            data.update(
                inputs=current, accepted_source_sha=self._phase_source()
            )
        self.journal.save()

    def _reconcile_legacy_source(self):
        if self.head is None:
            raise LocalReleaseError("local-release-resume-head-changed")
        self._check_resume_head()
