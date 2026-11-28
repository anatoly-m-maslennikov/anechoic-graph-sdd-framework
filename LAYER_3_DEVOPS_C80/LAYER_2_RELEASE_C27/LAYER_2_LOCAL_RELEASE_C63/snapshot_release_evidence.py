"""Bind snapshot image provenance and receipt evidence."""

from LAYER_1_RUNTIME_IMAGES_C81.LAYER_1_RUNTIME_IMAGES_C81__shared import (
    LocalReleaseError,
)


class SnapshotReleaseEvidence:
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
