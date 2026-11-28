"""Restore and verify reusable Local Release artifacts."""

from LAYER_1_RUNTIME_IMAGES_C81.LAYER_1_RUNTIME_IMAGES_C81__shared import (
    LocalReleaseError,
)

from .. import local_release_package_phases as package_phases
from ..local_release_progress import BUILD, IMAGE
from ..local_release_state import PHASES


class RecoveryArtifacts:
    def _declared_provenance(self):
        return package_phases.release_image_provenance(
            self.root, self.selection, self.cleanup_runner
        )

    def _image_provenance(self):
        data = self.journal.data
        if data.get("provenance") is None:
            provenance = self._declared_provenance()
            data["provenance"] = {
                **provenance,
                "head_commit": data["build_source_sha"],
            }
            self.journal.save()
        self._check_image_provenance(data["provenance"])
        return data["provenance"]

    def _check_image_provenance(self, provenance):
        data = self.journal.data
        if not isinstance(provenance, dict) or provenance.get(
            "head_commit"
        ) != data.get("build_source_sha"):
            raise LocalReleaseError(
                "local-release-resume-image-provenance-changed"
            )

    def _load_reusable_artifacts(self):
        data = self.journal.data
        try:
            self._restore_artifacts()
        except LocalReleaseError, OSError, RuntimeError:
            if data.get("delivery") is not None:
                raise
            first = IMAGE if self._package_matches() else BUILD
            self._invalidate(set(PHASES[PHASES.index(first) :]))
            self.journal.save()

    def _package_matches(self):
        from . import local_release_recovery as recovery

        if self.package is None or any(
            path.is_symlink() for path in (self.package, self.prepared_product)
        ):
            return False
        try:
            recovery._verify_package(self.package, self.package_identity)
            recovery._verify_package(
                self.prepared_product, self.product_identity
            )
            return True
        except LocalReleaseError, OSError:
            return False

    def _restore_artifacts(self, *, completed=False):
        from . import local_release_recovery as recovery

        data = self.journal.data
        if BUILD not in data["done"]:
            return
        self.staging = self.journal.staging()
        if completed:
            self.package, self.prepared_product = self.runtime, self.installed
        else:
            if self.staging is None or not self.staging.is_dir():
                raise LocalReleaseError("local-release-resume-staging-missing")
            self.package, self.prepared_product = (
                self.staging / "package",
                self.staging / "framework",
            )
        for path in (self.package, self.prepared_product):
            if not path.is_dir() or path.is_symlink():
                raise LocalReleaseError("local-release-resume-staging-invalid")
        self.package_identity = {
            name: tuple(value)
            for name, value in data["package_identity"].items()
        }
        self.product_identity = {
            name: tuple(value)
            for name, value in data["product_identity"].items()
        }
        recovery._verify_package(self.package, self.package_identity)
        if not completed:
            recovery._verify_package(
                self.prepared_product, self.product_identity
            )
        if IMAGE in data["done"]:
            self._restore_image(
                data, self.runtime.parent if completed else self.staging
            )

    def _restore_image(self, data, build_root):
        self._check_image_provenance(data["provenance"])
        self.candidate_image, self.candidate_fingerprint = (
            data["image_id"],
            data["fingerprint"],
        )
        self.manager = package_phases.restore_image(
            self.root,
            build_root,
            self.package,
            data["provenance"],
            self.candidate_image,
            self.candidate_fingerprint,
        )

    def _verify_installed(self):
        from . import local_release_recovery as recovery

        for phase in recovery.INSTALL_PHASES:
            if phase in self.journal.data["done"]:
                recovery.check_targets(self, phase)

    def _resume_cleanup(self):
        data = self.journal.data
        self._verify_installed()
        self._adopt_running()
        data["evidence"] = self._receipt_evidence()
        if "final" in data["done"]:
            data["done"].remove("final")
            self.journal.save()
