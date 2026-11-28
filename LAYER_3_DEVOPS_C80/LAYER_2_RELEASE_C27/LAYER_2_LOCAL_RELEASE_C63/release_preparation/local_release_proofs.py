"""Identify inputs and validate evidence for Local Release gates."""

import json
from pathlib import Path
from hashlib import sha256

from LAYER_1_RUNTIME_IMAGES_C81.LAYER_1_RUNTIME_IMAGES_C81__shared import (
    LocalReleaseError,
    _file_identity,
    _project_path,
    _walk_regular_files,
)

from ..local_release_delivery import PRESERVE_FRAMEWORK
from ..local_release_gates import _LOGS, _canary_endpoint
from ..release_support import _ROOT_PROJECT_GOAL
from ..snapshot_inputs import _COMMIT

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
        digest.update(
            json.dumps(
                (path.relative_to(root).as_posix(), _file_identity(path))
            ).encode("ascii")
        )
    return digest.hexdigest()


def _target_canary_files(root, control, installed, installed_files):
    files = _walk_regular_files(
        control,
        excluded_root_directories=frozenset({installed.name.casefold()}),
    )
    files += [
        path
        for path in installed_files
        if path.relative_to(installed).parts[0] in PRESERVE_FRAMEWORK
    ]
    goals = sorted(
        path
        for path in root.iterdir()
        if _ROOT_PROJECT_GOAL.fullmatch(path.name)
    )
    if any(path.is_symlink() or not path.is_file() for path in goals):
        raise LocalReleaseError("local-release-source-entry-unsafe")
    return files + goals


def _proof_inputs(phase, data, inputs):
    fields = {key: inputs[key] for key in _GATES[phase][1]}
    if phase in (IMAGE_TEST, CANARY):
        fields["artifact"] = [
            data.get(key)
            for key in ("image_id", "fingerprint", "build_source_sha")
        ]
    if phase == CANARY:
        fields["target"] = data.get("canary_inputs")
    return fields


def _proved_phases(data):
    return [
        phase
        for phase in _GATES
        if phase in data["done"]
        or (phase == PREFLIGHT and data.get("preflight"))
    ]


def _canary_matches(proof, data):
    endpoint = proof.get("endpoint")
    if endpoint != data.get("canary") or not isinstance(endpoint, str):
        return False
    try:
        return (
            _canary_endpoint(f"ANECHOIC_CANARY_ENDPOINT {endpoint}")
            == endpoint
        )
    except LocalReleaseError:
        return False


def _proof_matches(phase, proof, data, inputs):
    if not isinstance(proof, dict) or proof.get("inputs") != _proof_inputs(
        phase, data, inputs
    ):
        return False
    source = proof.get("source_sha")
    valid_source = (
        isinstance(source, str) and _COMMIT.fullmatch(source) is not None
    )
    if not valid_source and not (source is None and proof.get("legacy")):
        return False
    if proof.get("log_path") != data["logs"].get(_GATES[phase][0]):
        return False
    return phase != CANARY or _canary_matches(proof, data)


class ReleaseProofRecords:
    def _log_identity(self, value):
        if not isinstance(value, str) or not Path(value).is_relative_to(_LOGS):
            raise LocalReleaseError("local-release-test-log-path-invalid")
        path = _project_path(
            self.root,
            Path(value),
            label="resume-test-log",
            require_exists=True,
        )
        if not path.is_file():
            raise LocalReleaseError("local-release-test-log-path-invalid")
        return list(_file_identity(path))

    def _log_matches(self, proof):
        if (
            proof.get("log_path") is None
            or proof.get("legacy")
            or proof.get("legacy_combined")
        ):
            return True
        try:
            return self._log_identity(proof["log_path"]) == proof.get(
                "log_identity"
            )
        except LocalReleaseError, OSError:
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
        if set(
            _proved_phases(data)
        ) != _GATES.keys() or self._invalid_gate_proofs(data["inputs"]):
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
        if (
            data.get("port") is not None
            and data["port"] != self.production_port
        ):
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
        self.test_log_path = next(
            (
                self.test_log_paths[log]
                for log, _ in reversed(tuple(_GATES.values()))
                if log in self.test_log_paths
            ),
            None,
        )
