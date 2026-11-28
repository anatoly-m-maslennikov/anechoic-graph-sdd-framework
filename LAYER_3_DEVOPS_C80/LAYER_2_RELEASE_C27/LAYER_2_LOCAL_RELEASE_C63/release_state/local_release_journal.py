"""Persist journal state and render Local Release evidence."""

from . import local_release_state as state


class Journal:
    def __init__(
        self,
        root,
        run_id,
        selection,
        options,
        resume,
        *,
        source_binding=None,
        started_at=None,
    ):
        self.root = root
        self.run_id = run_id
        self.path = state._project_path(
            root, state._RUNS / run_id / "state.json", label="resume-journal"
        )
        if resume:
            self._resume(selection, source_binding)
        else:
            self._create(selection, options, source_binding, started_at)

    def _resume(self, selection, source_binding):
        if not self.path.is_file():
            raise state.LocalReleaseError("local-release-resume-run-missing")
        self.data = state._checked(state._read(self.path), self.run_id)
        if "docker_context" in self.data and self.data[
            "docker_context"
        ] != state.os.environ.get("DOCKER_CONTEXT"):
            raise state.LocalReleaseError(
                "local-release-resume-docker-context-changed"
            )
        if self.data["binding"] != state.binding(
            selection
        ) or not state._same_source_binding(
            self.data.get("source_binding"), source_binding
        ):
            raise state.LocalReleaseError(
                "local-release-resume-binding-changed"
            )

    def _create(self, selection, options, source_binding, started_at):
        if self.path.exists():
            raise state.LocalReleaseError("local-release-run-id-exists")
        self.data = {
            "schema": 2,
            "run_id": self.run_id,
            "binding": state.binding(selection),
            "options": options,
            "source_binding": source_binding,
            "docker_context": state.os.environ.get("DOCKER_CONTEXT"),
            "done": [],
            "working": None,
            "logs": {},
            "proofs": {},
            "release_started_at": started_at,
        }
        self.data["delivery_seen"] = state._delivery_record(self.root)[1]
        self.save()

    def save(self):
        state._project_path(
            self.root, self.path.relative_to(self.root), label="resume-journal"
        )
        state.atomic_write(
            self.path, state.json.dumps(self.data, sort_keys=True) + "\n"
        )

    def abort_path(self):
        return state.abort_request_path(self.root, self.path)

    def check_abort(self):
        if self.abort_path().exists():
            raise state.LocalReleaseError("local-release-aborted")

    def begin(self, phase):
        self.data["working"] = phase
        self.save()

    def finish(self, phase, **values):
        self.data.update(values, working=None)
        self.data["done"] = [
            item
            for item in state.PHASES
            if item == phase or item in self.data["done"]
        ]
        self.save()

    def record_failure(self, phase, error, paths):
        self.data["logs"].update(paths)
        failure = {
            "phase": phase,
            "source_sha": self.data.get("accepted_source_sha"),
            "error": str(error)[:8500],
            "error_type": type(error).__name__,
            "logs": paths.copy(),
        }
        notes = state._startup_diagnostics(error)
        if notes:
            failure["diagnostics"] = notes
        self.data.setdefault("failures", []).append(failure)
        try:
            self.save()
        except OSError:
            pass

    def record_logs(self, paths):
        self.data["logs"].update(paths)
        self.save()

    def staging(self):
        value = self.data.get("staging")
        if value is None:
            return None
        if not isinstance(value, str):
            raise state.LocalReleaseError(
                "local-release-resume-staging-invalid"
            )
        path = state.Path(value)
        if path.parent != state._STAGES or not path.name.startswith(
            self.run_id + "-"
        ):
            raise state.LocalReleaseError(
                "local-release-resume-staging-invalid"
            )
        return state._project_path(self.root, path, label="resume-staging")

    def delivery(self, *, claim=False):
        path, latest = state._delivery_record(self.root)
        prior = self.data.get("delivery")
        self_record = {"run_id": self.run_id}
        if not state._current_delivery(self.data, latest):
            raise state.LocalReleaseError("local-release-resume-superseded")
        if not claim:
            return
        if prior is None:
            self.data["delivery"] = latest
            self.save()
        if latest != self_record:
            state.atomic_write(path, state.json.dumps(self_record) + "\n")


def release_evidence(run):
    version = state.tomllib.loads(
        (run.package / "version.toml").read_text(encoding="utf-8")
    )["framework"]["version"]
    data = run.journal.data
    build = data["provenance"]["head_commit"]
    details = {
        "source_sha": build,
        "image_build_sha": build,
        "accepted_source_sha": data["accepted_source_sha"],
        "verified_phases": data["proofs"],
        "failed_attempts": data.get("failures", []),
        "version": version,
        "project_instance": run.selection.instance_id,
        "project_root": str(run.root),
        "control_root": run.selection.control_relative.as_posix(),
        "port": run.production_port,
        "target_manifest_sha256": data["target_binding"][0],
        "target_runtime_settings_sha256": data["target_binding"][1],
        "image_id": run.candidate_image,
        "fingerprint": run.candidate_fingerprint,
        **run.readiness,
    }
    if "legacy_inputs" in data:
        details["legacy_gate_evidence"] = state._legacy_gate_evidence(data)
    if details.get("readiness") == "healthy":
        details["observed_at"] = state.datetime.now(
            state.timezone.utc
        ).isoformat(timespec="milliseconds")
    return details


def _legacy_gate_evidence(data):
    recorded = data["legacy_inputs"]
    digest = (
        recorded
        if isinstance(recorded, str)
        else state.sha256(state.json.dumps(recorded).encode()).hexdigest()
    )
    return {
        "recorded_inputs_sha256": digest,
        "source_sha": data["accepted_source_sha"],
        "combined_gate_log": data["logs"].get("image"),
        "canary_endpoint": data.get("canary"),
    }
