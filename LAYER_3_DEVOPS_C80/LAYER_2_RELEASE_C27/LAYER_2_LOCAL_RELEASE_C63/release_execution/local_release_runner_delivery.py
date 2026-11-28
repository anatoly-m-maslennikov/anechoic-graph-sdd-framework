"""Start, verify and clean up the released Project runtime."""

from . import local_release_runner as r


class RunnerDelivery:
    def _start_mcp(self):
        self.failed_step = "start_mcp"
        existing = self._find_running() if self.resume else None
        if existing is not None:
            existing = r.reconcile_release_container(
                self.root,
                self.selection,
                self.candidate_image,
                self.candidate_fingerprint,
                self.production_port,
                existing,
                self.cleanup_runner,
                run_id=self.run_id,
            )
        self._prepare_cleanup()
        run_id = self.run_id
        if existing is None:
            existing, self.cleanup_note, self.cleanup_pending = (
                r.previous_container(
                    self.root,
                    self.selection,
                    self.prior_project,
                    self.candidate_image,
                    self.cleanup,
                    self.runner,
                    self.cleanup_runner,
                    r.image_labels,
                    self.cleanup_note,
                )
            )
            if existing is not None:
                run_id = None
                self.journal.data["adopted_container"] = existing
                self.journal.save()
        self.endpoint = r.start_container(
            self.root,
            self.selection,
            self.candidate_image,
            self.candidate_fingerprint,
            self.production_port,
            self.cleanup_runner,
            existing_container=existing,
            run_id=run_id,
            evidence=self.readiness,
        )

    def _prepare_cleanup(self):
        self.cleanup = r.cleanup_stopped_containers(
            self.root,
            self.selection.instance_id,
            self.selection.control_relative.as_posix(),
            self.candidate_image,
            self.candidate_fingerprint,
            self.cleanup_runner,
        )
        if self.prior_image is not None:
            self.cleanup.images.add(self.prior_image)

    def _find_running(self):
        return r.find_release_container(
            self.root, self.selection, self.run_id, self.runner
        )

    def _adopt_running(self):
        adopted = self.journal.data.get("adopted_container")
        existing = adopted or self._find_running()
        if existing is None:
            raise r.LocalReleaseError("local-release-resume-container-missing")
        endpoint = r.verify_release_container(
            self.root,
            self.selection,
            self.candidate_image,
            self.candidate_fingerprint,
            self.production_port,
            existing,
            self.cleanup_runner,
            run_id=None if adopted else self.run_id,
            evidence=self.readiness,
        )
        if endpoint != self.endpoint:
            raise r.LocalReleaseError("local-release-resume-endpoint-changed")

    def _receipt_evidence(self):
        elapsed = self._release_seconds()
        return r.release_evidence(self) | {
            "functional_suite": self.functional_suite,
            "ready_seconds": elapsed,
            "fast_target_met": elapsed <= r.FAST_TARGET_SECONDS
            if elapsed is not None and self.functional_suite == "fast"
            else None,
            "fast_limit_met": elapsed <= r.FAST_LIMIT_SECONDS
            if elapsed is not None and self.functional_suite == "fast"
            else None,
        }

    def _after_start(self):
        if not self.journal.data.get("production_tagged"):
            self.failed_step = "promote_candidate_image"
            try:
                self.manager.mark_production_image(self.candidate_image)
            except RuntimeError, OSError:
                self.cleanup_pending = True
                self.cleanup_note += (
                    "\nProduction image tag failed. Cleanup deferred."
                )
                return r.reports.record_receipt(self)
            self.journal.data["production_tagged"] = True
            self.journal.save()
        self.failed_step = "final"
        if self.cleanup is None:
            self._prepare_cleanup()
        r.cleanup_stopped_containers(
            self.root,
            self.selection.instance_id,
            self.selection.control_relative.as_posix(),
            self.candidate_image,
            self.candidate_fingerprint,
            self.cleanup_runner,
            cleanup=self.cleanup,
        )
        self._cleanup_image_history()
        try:
            self.manager.prune_build_cache()
        except OSError, RuntimeError:
            self.cleanup.pending = True
            self.cleanup.notes.append("Docker build cache cleanup failed.")
        if (
            self.prior_image is not None
            and self.previous_image is None
            and (self.prior_image != self.candidate_image)
        ):
            self.cleanup.pending = True
            self.cleanup.notes.append(
                "Prior image retained: readiness evidence unavailable."
            )
        self._cleanup_temporary()
        self.cleanup_pending |= self.cleanup.pending
        self.cleanup_note = "\n".join([self.cleanup_note, *self.cleanup.notes])
        r.reports.record_receipt(self)

    def _cleanup_image_history(self):
        try:
            history = r._project_path(
                self.root,
                r.Path(
                    ".anechoic_runtime/simple_local_release/ready-images.json"
                ),
                label="simple-image-history",
            )
            previous_images = r.record_ready_images(
                history,
                self.selection.instance_id,
                self.candidate_image,
                self.prior_image,
            )
        except OSError, ValueError, r.LocalReleaseError:
            self.cleanup.pending = True
            self.cleanup.notes.append(
                "Image history unavailable. Retained existing images."
            )
        else:
            r.cleanup_obsolete_images(
                self.root,
                self.candidate_image,
                self.candidate_fingerprint,
                self.cleanup,
                self.cleanup_runner,
                previous_images=previous_images,
            )

    def _cleanup_temporary(self):
        try:
            removed, blocked = r.prune_temporary_files(self.root)
            self.cleanup.notes.append(
                f"Removed {removed} temporary paths older than 48 hours."
            )
            if blocked:
                self.cleanup.pending = True
                self.cleanup.notes.append(
                    f"Temporary file cleanup blocked on {len(blocked)} paths. "
                    f"First error: {blocked[0]}"
                )
        except OSError, r.LocalReleaseError:
            self.cleanup.pending = True
            self.cleanup.notes.append("Temporary file cleanup failed.")
