"""Capture and admit foreground generation evidence."""

import os
from pathlib import Path
from tempfile import TemporaryDirectory
import time

from ORCHESTRATOR_beta_C68.generation.generation import live_reuse
from ORCHESTRATOR_beta_C68.generation.generation_admission import DeltaRequiresReconciliation


_MODEL_TARGETS = frozenset(
    {
        "all",
        "model_entities",
        "model_properties",
        "model_tree",
        "model_primary_entities",
        "mrt_model_entities",
        "mrt_model_properties",
        "mrt_model_tree",
        "mrt_model_primary_entities",
    }
)


class GenerationLiveCapture:
    def _attempt_generation(
        self,
        target,
        reuse,
        paths=None,
        *,
        reconciliation=False,
        strict=False,
        recover_coverage=False,
    ):
        if target == "realization_graph":
            return self._attempt_explicit_graph(reuse)
        with TemporaryDirectory(prefix="anechoic-generation-") as temporary:
            directory = str(Path(temporary).resolve(strict=True))
            started = time.monotonic()
            result, reuse, deferred = self._capture_live(
                directory,
                target,
                reuse,
                paths,
                (reconciliation, strict, recover_coverage),
            )
            captured = time.monotonic()
            witness = result.get("reuse", reuse)
            if result.get("reuse", True) is None:
                del result["reuse"]
            admitted = self._admit_live_result(
                directory, result, target, witness
            )
            admitted.update(
                worker_seconds=captured - started,
                admission_seconds=time.monotonic() - captured,
            )
            if "paths" in result:
                admitted["delta_path_count"] = len(result["paths"])
        self._accept_capture(admitted, result, deferred, witness, reuse)
        return {"state": "succeeded", **admitted}

    def _accept_capture(self, admitted, result, deferred, witness, reuse):
        self._accept_live_generation(admitted["generation"], result, deferred)
        if witness is not None:
            self.generation_reuse = live_reuse(
                self.database_socket,
                self.instance_id,
                admitted["generation"],
                result,
                reuse,
                witness,
            )
            self._flow_effect(
                "generation_reuse_write",
                outcome="succeeded",
                detail={"state": "stored"},
            )

    def _capture_live(self, directory, target, reuse, paths, options):
        reconciliation, strict, recover_coverage = options
        explicit = target is not None or self.inflight is not None
        if explicit or (self.skip_archives and self.startup_capture):
            reuse = paths = None
        if (
            self.skip_archives
            and paths
            and any(
                self._is_archive_path(str(Path(self.binding["root"]) / path))
                for path in paths
            )
        ):
            paths = None
        result, reuse, options = self._capture_generation(
            directory,
            reuse,
            paths,
            explicit=explicit,
            reconciliation=reconciliation,
            strict=strict,
            recover_coverage=recover_coverage,
            force_model=target in _MODEL_TARGETS,
        )
        deferred = result.pop("deferred_archive", None)
        if self.skip_archives:
            deferred = None
        if (
            deferred is None
            and options.get("incremental")
            and not self.skip_archives
        ):
            deferred = self._restart_archive(reuse, result)
        self._include_archive_pending(result, deferred)
        self._check_foreground_capture(result, paths, deferred)
        return result, reuse, deferred

    def _check_foreground_capture(self, result, paths, deferred):
        if (
            self.skip_archives
            and "paths" in result
            and any(
                atom["status_group"] == "Archived"
                for atom in result["snapshot"]["atoms"]
            )
        ):
            raise DeltaRequiresReconciliation(
                "Archived Atom requires foreground capture"
            )
        if (
            self.deferred_archive
            and paths is not None
            and deferred is None
            and self._needs_foreground(result)
        ):
            raise DeltaRequiresReconciliation(
                "Archive paths require foreground capture"
            )

    def _admit_live_result(self, directory, result, target, witness):
        from ORCHESTRATOR_beta_C68.generation.generation import (
            admit_generation,
            confirm_reuse,
        )

        unchanged = "unchanged" in result
        effect = (
            "generation_reuse_check" if unchanged else "generation_admission"
        )
        timed = (
            self.startup_capture
            and os.environ.get("ANECHOIC_STARTUP_TIMING") == "1"
        )
        if timed:
            from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.sources.sources__shared import (
                mark_startup_timing,
            )
        try:
            admitted = (
                confirm_reuse(self.database_socket, self.instance_id, result)
                if unchanged
                else admit_generation(
                    self.database_socket,
                    self.instance_id,
                    directory,
                    result,
                    target,
                )
            )
        except Exception:
            self._flow_effect(effect, outcome="failed")
            raise
        if timed and "kind" in admitted:
            self._record_load_timing(result, admitted, mark_startup_timing)
        if unchanged:
            self._flow_effect(effect, outcome="succeeded")
            self._record_ingestion_issues("build", [])
        else:
            self._flow_effect(
                effect,
                outcome="succeeded",
                detail={"reuse_proof_present": witness is not None},
            )
        return admitted

    def _record_load_timing(self, result, admitted, mark_startup_timing):
        archive = (
            "disabled"
            if self.skip_archives
            else "deferred"
            if result.get("archive_pending") is True
            else "none"
        )
        mark_startup_timing(
            "non_archived_load_ended",
            mode=admitted["kind"],
            archive=archive,
        )
