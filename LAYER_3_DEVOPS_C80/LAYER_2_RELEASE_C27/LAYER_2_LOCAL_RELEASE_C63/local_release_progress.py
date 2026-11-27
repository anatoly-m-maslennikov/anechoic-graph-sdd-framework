"""Bind reusable Local Release phase evidence to its inputs and source."""

import json
from dataclasses import asdict
from hashlib import sha256
from pathlib import Path

from LAYER_1_RUNTIME_IMAGES_C81.LAYER_1_RUNTIME_IMAGES_C81__shared import (
    LocalReleaseError,
    _file_identity,
    _project_path,
    _walk_regular_files,
    read_release_selection,
)

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.container_settings__pub import (
    read_container_settings,
)

from .local_release_delivery import PRESERVE_FRAMEWORK, verify_recorded_targets
from .local_release_gates import _LOGS, _ROOT as COMMAND_ROOT, _canary_endpoint
from .local_release_git import ReleaseGitCheckpoints
from .local_release_state import PHASES, source_identity
from .prepare_test_environment import check_locked_engine, ensure_test_environment
from .release_phase_inputs import phase_inputs
from .release_support import _ROOT_PROJECT_GOAL
from .snapshot_inputs import _COMMIT, target_runtime_digest

PREFLIGHT = "preflight tests"
STATIC = "static tests"
COPY = "copy active sources"
BUILD = "build package"
IMAGE = "prepare candidate image"
IMAGE_TEST = "verify candidate image"
CANARY = "verify candidate canary"
_GATES = {
    PREFLIGHT: ("preflight", ("runtime", "environment")),
    STATIC: ("static", ("runtime", "image", "canary", "environment")),
    "functional tests": ("functional", ("runtime", "environment")),
    IMAGE_TEST: ("image", ("runtime", "image", "environment")),
    CANARY: ("canary", ("runtime", "canary", "environment")),
}


def _tree_digest(root, files):
    digest = sha256()
    for path in files:
        digest.update(json.dumps((path.relative_to(root).as_posix(), _file_identity(path))).encode("ascii"))
    return digest.hexdigest()


def _target_canary_files(root, control, installed, installed_files):
    files = _walk_regular_files(control, excluded_root_directories=frozenset({installed.name.casefold()}))
    files += [path for path in installed_files if path.relative_to(installed).parts[0] in PRESERVE_FRAMEWORK]
    goals = sorted(path for path in root.iterdir() if _ROOT_PROJECT_GOAL.fullmatch(path.name))
    if any(path.is_symlink() or not path.is_file() for path in goals):
        raise LocalReleaseError("local-release-source-entry-unsafe")
    return files + goals


def _proof_inputs(phase, data, inputs):
    fields = {key: inputs[key] for key in _GATES[phase][1]}
    if phase in (IMAGE_TEST, CANARY):
        fields["artifact"] = [data.get(key) for key in ("image_id", "fingerprint", "build_source_sha")]
    if phase == CANARY:
        fields["target"] = data.get("canary_inputs")
    return fields


def _proved_phases(data):
    return [phase for phase in _GATES if phase in data["done"] or (phase == PREFLIGHT and data.get("preflight"))]


def _canary_matches(proof, data):
    endpoint = proof.get("endpoint")
    if endpoint != data.get("canary") or not isinstance(endpoint, str):
        return False
    try:
        return _canary_endpoint(f"ANECHOIC_CANARY_ENDPOINT {endpoint}") == endpoint
    except LocalReleaseError:
        return False


def _proof_matches(phase, proof, data, inputs):
    if not isinstance(proof, dict) or proof.get("inputs") != _proof_inputs(phase, data, inputs):
        return False
    source = proof.get("source_sha")
    valid_source = isinstance(source, str) and _COMMIT.fullmatch(source) is not None
    if not valid_source and not (source is None and proof.get("legacy")):
        return False
    if proof.get("log_path") != data["logs"].get(_GATES[phase][0]):
        return False
    return phase != CANARY or _canary_matches(proof, data)


class ReleaseProgress(ReleaseGitCheckpoints):
    def _target_binding(self):
        binding = [self.selection.manifest_sha256, target_runtime_digest(self.root)]
        settings = read_container_settings(self.root)
        if settings is not None:
            binding.append(asdict(settings))
        return binding

    def _bind_target(self):
        target = self._target_binding()
        if read_release_selection(self.root) != self.selection or self.journal.data.setdefault("target_binding", target) != target:
            raise LocalReleaseError("local-release-resume-binding-changed")

    def _input_identity(self):
        return phase_inputs(self.root, COMMAND_ROOT, external=self.default_runner, cache=self._phase_input_cache)

    def _target_canary_identity(self):
        data = self.journal.data
        files = _walk_regular_files(self.installed) if self.installed.exists() else []
        original = (data.get("canary_inputs") or {}).get("target_install")
        installed = original if data.get("delivery") is not None else _tree_digest(self.root, files)
        authoring = _target_canary_files(self.root, self.selection.control_root, self.installed, files)
        return {"target": _tree_digest(self.root, authoring), "target_install": installed}

    def _phase_source(self):
        return self.head

    def _assert_resume_source(self):
        pass

    def _verify_release_inputs(self):
        if self._target_binding() != self.journal.data["target_binding"]:
            raise LocalReleaseError("local-release-target-runtime-settings-changed")
        if "bump candidate version" in self.journal.data["done"]:
            self._assert_version()
        if self._input_identity() != self.journal.data.get("inputs"):
            raise LocalReleaseError("local-release-gate-inputs-changed")

    def _new_proof(self, phase, inputs, source, *, legacy=False):
        data = self.journal.data
        proof = {"source_sha": source, "inputs": _proof_inputs(phase, data, inputs),
                 "log_path": self.test_log_paths.get(_GATES[phase][0])}
        if proof["log_path"] is not None and not legacy:
            proof["log_identity"] = self._log_identity(proof["log_path"])
        if phase == CANARY:
            proof["endpoint"] = self.canary_endpoint
        if legacy:
            proof["legacy_combined" if phase in (IMAGE_TEST, CANARY) else "legacy"] = True
        return proof

    def _run_verified_gate(self, phase):
        self.failed_step = "validate_gate_inputs"
        self._verify_release_inputs()
        data = self.journal.data
        legacy_image = (phase == IMAGE_TEST and self.default_runner
                        and self._test_gate_options().get("source_root") is not None)
        checks_target = phase == CANARY or (legacy_image and CANARY not in data["done"])
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
        if checks_target and (phase == CANARY or observed_endpoint is not None):
            if target != self._target_canary_identity():
                raise LocalReleaseError("local-release-canary-inputs-changed")
            data["canary_inputs"] = target
            if phase == IMAGE_TEST:
                self.canary_endpoint = observed_endpoint
        data["proofs"][phase] = self._new_proof(phase, data["inputs"], self._phase_source())

    def _canary_inputs_match(self):
        expected = self.journal.data.get("canary_inputs")
        return expected is not None and expected == self._target_canary_identity()

    def _verify_canary_inputs(self):
        data = self.journal.data
        legacy = data["proofs"].get(CANARY, {}).get("legacy_combined")
        if not self._canary_inputs_match() and not (legacy and data.get("delivery") is not None):
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
        if isinstance(legacy, str) and source_identity(self.root, COMMAND_ROOT, external=self.default_runner) == legacy:
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
                self.test_log_paths.setdefault("canary", self.test_log_paths["image"])
                data["logs"].update(self.test_log_paths)
        data.pop("legacy_inputs")
        data["inputs"] = previous
        if BUILD in data["done"] and not data.get("build_source_sha"):
            data["build_source_sha"] = data.get("accepted_source_sha")
        for phase in _proved_phases(data):
            source = data.get("accepted_source_sha")
            if not data.get("source_binding") and phase not in (IMAGE_TEST, CANARY):
                source = None
            data["proofs"][phase] = self._new_proof(phase, previous, source, legacy=True)
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
        changed = legacy_changed or previous is not None and current != previous
        rebuild = legacy_changed or previous is not None and previous["runtime"] != current["runtime"]
        invalid = self._invalid_gate_proofs(current)
        if data.get("delivery") is not None:
            self._check_claimed_inputs(changed or invalid)
            return
        if data.get("canary") and (changed and CANARY not in data["done"] or not self._canary_inputs_match()):
            invalid.add(CANARY)
        self._check_resume_head(allow_fix=changed)
        if COPY in data.get("targets", {}) and (changed or COPY in data["done"]):
            verify_recorded_targets(self, COPY)
        if changed:
            self._accept_input_fix()
        if rebuild:
            invalid.update(PHASES[PHASES.index(STATIC):])
            invalid.add(PREFLIGHT)
        if changed or invalid or self._phase_source() != data.get("accepted_source_sha"):
            self._invalidate(invalid)
            data.update(inputs=current, accepted_source_sha=self._phase_source())
        self.journal.save()

    def _reconcile_legacy_source(self):
        if self.head is None:
            raise LocalReleaseError("local-release-resume-head-changed")
        self._check_resume_head()

    def _log_identity(self, value):
        if not isinstance(value, str) or not Path(value).is_relative_to(_LOGS):
            raise LocalReleaseError("local-release-test-log-path-invalid")
        path = _project_path(self.root, Path(value), label="resume-test-log", require_exists=True)
        if not path.is_file():
            raise LocalReleaseError("local-release-test-log-path-invalid")
        return list(_file_identity(path))

    def _log_matches(self, proof):
        if proof.get("log_path") is None or proof.get("legacy") or proof.get("legacy_combined"):
            return True
        try:
            return self._log_identity(proof["log_path"]) == proof.get("log_identity")
        except (LocalReleaseError, OSError):
            return False

    def _invalid_gate_proofs(self, current):
        data = self.journal.data
        invalid = set()
        for phase in _proved_phases(data):
            proof = data["proofs"].get(phase)
            if not _proof_matches(phase, proof, data, current):
                invalid.add(phase)
            elif data.get("delivery") is None and not self._log_matches(proof):
                invalid.add(phase)
        return invalid

    def _verify_gate_proofs(self):
        data = self.journal.data
        if set(_proved_phases(data)) != _GATES.keys() or self._invalid_gate_proofs(data["inputs"]):
            raise LocalReleaseError("local-release-gate-evidence-unverified")

    def _check_claimed_inputs(self, invalid):
        if invalid:
            raise LocalReleaseError("local-release-gate-inputs-changed")
        self._check_resume_head()
        if "start mcp" not in self.journal.data["done"]:
            self._verify_canary_inputs()
        self.journal.save()

    def _accept_input_fix(self):
        data = self.journal.data
        self._validate_inputs("validate inputs")
        if data.get("port") is not None and data["port"] != self.production_port:
            raise LocalReleaseError("local-release-resume-port-changed")
        self.head = self._checkpoint_refreshed_inputs()
        data.update(head=self.head, working=None, checkpoint=None)

    def _invalidate(self, phases):
        data = self.journal.data
        if BUILD in phases:
            data.update(staging=None, build_source_sha=None)
            self.staging = self.package = self.prepared_product = None
            for key in ("package_identity", "product_identity"):
                data.pop(key, None)
        if IMAGE in phases:
            for key in ("image_id", "fingerprint", "provenance"):
                data.pop(key, None)
            self.candidate_image = self.candidate_fingerprint = None
        if COPY in phases:
            data.get("targets", {}).pop(COPY, None)
        if CANARY in phases:
            data["canary"] = self.canary_endpoint = None
            data.pop("canary_inputs", None)
        if PREFLIGHT in phases:
            data["preflight"] = False
        for phase in phases & _GATES.keys():
            data["proofs"].pop(phase, None)
            log = _GATES[phase][0]
            data["logs"].pop(log, None)
            self.test_log_paths.pop(log, None)
        data["done"] = [phase for phase in data["done"] if phase not in phases]
        if data.get("working") in phases:
            data.update(working=None, checkpoint=None)
        self._restore_log_path()

    def _restore_log_path(self):
        self.test_log_path = next((self.test_log_paths[log] for log, _ in reversed(tuple(_GATES.values()))
                                   if log in self.test_log_paths), None)
