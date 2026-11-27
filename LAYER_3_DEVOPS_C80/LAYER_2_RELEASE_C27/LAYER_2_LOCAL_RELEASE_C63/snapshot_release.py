"""Install a pinned source revision into a separate Project."""

from LAYER_1_RUNTIME_IMAGES_C81.LAYER_1_RUNTIME_IMAGES_C81__shared import (
    LocalReleaseError,
    _RUN_ID,
    _new_staging_directory,
    _project_path,
    _root,
    read_release_selection,
)

from . import local_release_package_phases as package_phases
from .local_release_delivery import INSTALL_PHASES, _observed, desired_targets
from .local_release_runner import LocalReleaseRun
from .local_release_state import _RUNS, _checked, _read, test_environment

from .release_phase_inputs import phase_inputs
from .snapshot_inputs import (
    _assert_source_clean,
    _source_tree,
    _source_version,
    _target_git,
    target_runtime_digest,
)


class SnapshotReleaseRun(LocalReleaseRun):
    def __init__(
        self,
        source_root,
        target_root,
        source_revision,
        run_id,
        runner,
        test_modules,
        image_mode,
        *,
        resume,
        functional_suite=None,
        started_at=None,
    ):
        self.source_root = _root(source_root)
        target_root = _root(target_root)
        if self.source_root.is_relative_to(
            target_root
        ) or target_root.is_relative_to(self.source_root):
            raise LocalReleaseError("local-release-source-target-overlap")
        self.source_revision = source_revision
        self.tracked = _source_tree(self.source_root, source_revision)
        try:
            self.source_selection = read_release_selection(self.source_root)
        except ValueError as error:
            raise LocalReleaseError(
                "local-release-source-selection-invalid"
            ) from error
        if (
            self.source_selection.manifest_path.relative_to(self.source_root)
            not in self.tracked
        ):
            raise LocalReleaseError("local-release-untracked-source-manifest")
        self.source_version = _source_version(self.source_root)
        self.target_runtime_digest = target_runtime_digest(target_root)
        super().__init__(
            target_root,
            run_id,
            runner,
            test_modules,
            image_mode,
            resume=resume,
            functional_suite=functional_suite,
            started_at=started_at,
        )

    def _product_path(self):
        return None

    def _source_binding(self):
        return [
            str(self.source_root),
            self.source_revision,
            self.source_version,
            self.selection.manifest_sha256,
            self.target_runtime_digest,
        ]

    def _assert_runtime_settings(self):
        if target_runtime_digest(self.root) != self.target_runtime_digest:
            raise LocalReleaseError(
                "local-release-target-runtime-settings-changed"
            )

    def _run_phase(self, phase):
        self.failed_step = "validate_target_binding"
        self._assert_runtime_settings()
        super()._run_phase(phase)

    def _validate_inputs(self, phase):
        self.failed_step = "validate_inputs"
        self._check_source()
        self.production_port = package_phases.validate_inputs(
            self.root,
            self.selection,
            None,
            self.installed,
            self.runtime,
            source_root=self.source_root,
            source_selection=self.source_selection,
        )

    def _check_source(self):
        _assert_source_clean(self.source_root, self.source_revision)
        if read_release_selection(self.source_root) != self.source_selection:
            raise LocalReleaseError("local-release-source-selection-changed")

    def _phase_label(self, phase):
        return {
            "bump candidate version": "pin source version",
            "copy active sources": "select source snapshot",
        }.get(
            phase,
            phase,
        )

    def _run_git_checkpoint(self, phase, *, interrupted):
        return None

    def _bump_version(self):
        self.failed_step = "pin_source_version"
        self._assert_version()

    def _assert_version(self):
        if _source_version(self.source_root) != self.source_version:
            raise LocalReleaseError("local-release-source-version-changed")

    def _copy_sources(self):
        self._verify_build_inputs()

    def _verify_build_inputs(self):
        self.failed_step = "validate_gate_inputs"
        self._verify_release_inputs()

    def _verify_copy_intent(self, phase):
        return phase != "copy active sources" and super()._verify_copy_intent(
            phase
        )

    def _before_delivery(self, phase):
        for target_phase in (
            INSTALL_PHASES if phase == INSTALL_PHASES[0] else (phase,)
        ):
            self.failed_step = target_phase.replace(" ", "_")
            self._guard_target_changes(target_phase)

    def _guard_target_changes(self, phase):
        targets = desired_targets(self, phase)
        tracked, changes = _target_git(self.root, targets)
        if any(status[0] != " " for status in changes.values()):
            raise LocalReleaseError(
                "local-release-target-managed-files-staged"
            )
        if phase in self.journal.data.get("targets", {}):
            return
        observed = {
            path: _observed(path, preserve)
            for path, (_, preserve) in targets.items()
        }
        if self._known_delivery(phase, observed):
            return
        unchanged = tracked - changes.keys()
        runtime_targets = {
            self.runtime,
            self.root / ".anechoic_runtime/start_mcp.py",
        }
        for path, (incoming, _) in targets.items():
            if path in runtime_targets and not any(
                changed.is_relative_to(path) for changed in changes
            ):
                continue
            actual = observed[path] or {}
            for name, identity in actual.items():
                entry = path / name
                if entry not in unchanged and tuple(identity) != incoming.get(
                    name
                ):
                    raise LocalReleaseError(
                        "local-release-target-managed-files-changed"
                    )
            if any(
                path / name in changes and name not in actual
                for name in incoming
            ):
                raise LocalReleaseError(
                    "local-release-target-managed-files-changed"
                )

    def _known_delivery(self, phase, observed):
        data = self.journal.data
        prior = (data.get("delivery") or data["delivery_seen"]).get("run_id")
        if not isinstance(prior, str) or not _RUN_ID.fullmatch(prior):
            return False
        path = _project_path(
            self.root, _RUNS / prior / "state.json", label="resume-journal"
        )
        if not path.is_file():
            return False
        previous = _checked(_read(path), prior)
        if (
            phase not in previous["done"]
            or previous["binding"] != data["binding"]
        ):
            return False
        after = previous["targets"][phase]["after"]
        return all(
            identity == after.get(path.relative_to(self.root).as_posix())
            for path, identity in observed.items()
        )

    def _phase_source(self):
        return self.source_revision

    def _assert_resume_source(self):
        data = self.journal.data
        accepted = data.get("accepted_source_sha") or data["source_binding"][1]
        if (
            data.get("delivery") is not None
            and accepted != self.source_revision
        ):
            raise LocalReleaseError(
                "local-release-resume-source-revision-changed"
            )

    def _reconcile_legacy_source(self):
        self._check_source()

    def _input_identity(self):
        self._check_source()
        return self._snapshot_identity(self.source_revision)

    def _snapshot_identity(self, revision):
        return phase_inputs(
            self.source_root, self.source_root, revision=revision
        )

    def _legacy_identity(self, legacy, current):
        if (
            isinstance(legacy, list)
            and len(legacy) == 2
            and legacy[1] == list(test_environment())
            and legacy[0] == self.journal.data["source_binding"][1]
        ):
            return (
                current
                if legacy[0] == self.source_revision
                else self._snapshot_identity(legacy[0])
            )
        return None

    def _checkpoint_refreshed_inputs(self):
        return None

    def _test_gate_options(self):
        return {
            "source_root": self.source_root,
            "canary_root": self.root,
            "canary_settings_sha256": self.target_runtime_digest,
        }

    def _build_package(self):
        self.failed_step = "build_package"
        self.staging = _new_staging_directory(self.root, f"{self.run_id}-")
        self.journal.data["staging"] = self.staging.relative_to(
            self.root
        ).as_posix()
        self.journal.save()
        (
            self.prepared_product,
            self.product_identity,
            self.package,
            self.package_identity,
        ) = package_phases.build_package(
            self.source_root,
            self.source_selection,
            None,
            self.staging,
            active_sources=True,
            tracked=self.tracked,
        )

    def _declared_provenance(self):
        return {
            "project_id": self.selection.instance_id,
            "project_root": str(self.root),
            "control_root": self.selection.control_relative.as_posix(),
            "project_name": self.selection.project_name,
            "head_commit": self.source_revision,
        }

    def _check_image_provenance(self, provenance):
        expected = self._declared_provenance()
        expected["head_commit"] = self.journal.data["build_source_sha"]
        if provenance != expected:
            raise LocalReleaseError(
                "local-release-resume-image-provenance-changed"
            )

    def _receipt_evidence(self):
        return {
            **super()._receipt_evidence(),
            "source_root": str(self.source_root),
            "project_root": str(self.root),
            "project_instance": self.selection.instance_id,
            "control_root": self.selection.control_relative.as_posix(),
            "port": self.production_port,
            "target_manifest_sha256": self.selection.manifest_sha256,
            "target_runtime_settings_sha256": self.target_runtime_digest,
        }


def run_snapshot_release(source_root, *, target_root, source_revision, run_id, resume=False, runner=None,
                         test_modules=None, image_mode=None, functional_suite=None, started_at=None):
    """Verify the explicit source and release it into the selected target."""
    try:
        release = SnapshotReleaseRun(source_root, target_root, source_revision, run_id, runner, test_modules,
                                     image_mode, resume=resume, functional_suite=functional_suite, started_at=started_at)
    except LocalReleaseError as error:
        step = "validate_project_selection" if str(error).endswith("selection-invalid") else "validate_inputs"
        return {"outcome": "failed", "failed_step": step, "error_type": type(error).__name__,
                "error": str(error), "effects": []}
    return release.run()
