"""Admit archive results and record reconciliation outcomes."""

from ORCHESTRATOR_beta_C68.archive_operations import archive_jobs as jobs


class ArchivePublication:
    def _finish_archive_result(self, result):
        if self.archive_run is None:
            if isinstance(result, Exception):
                jobs.emit_record(
                    "WARNING",
                    "archive_watcher_unavailable",
                    "archive",
                    "degraded",
                )
                self.archive_watching = True
            return
        state, message = "succeeded", None
        if self.deferred_archive is not None and isinstance(
            result, jobs.WorkerAborted
        ):
            state, message = "aborted", str(result)
            self.archive_dirty = False
        elif self._archive_superseded(result):
            state, message = (
                "superseded",
                "Archive scope changed during capture",
            )
        else:
            try:
                if isinstance(result, Exception):
                    raise result
                self._admit_archive(result[1])
            except jobs.DeltaRequiresReconciliation:
                state, message = self._reconcile_archive_result(result)
            except jobs._ARCHIVE_ERRORS as error:
                state, message = "failed", str(error)[-2048:]
                self._record_archive_failure(error)
        with self.lock:
            self.archive_run.state = state
            self.archive_run.finished_at = jobs.time.time()
            if message is not None:
                self.archive_run.message = message

    def _reconcile_archive_result(self, result):
        if "paths" in result[1] or result[1].get("unchanged") is True:
            state, message = (
                "superseded",
                "Archive requires full capture",
            )
            self.deferred_archive = {
                key: value
                for key, value in self.deferred_archive.items()
                if key != "checkpoint"
            } | {"replace": True}
            self.archive_dirty = True
        else:
            state, message = (
                "superseded",
                "Archive requires full native reconciliation",
            )
            self.archive_reconciliation_pending = True
            self.watcher.queue.put(
                {
                    "event_type": jobs.ARCHIVE_RECONCILIATION,
                    "old_path": None,
                    "new_path": None,
                    "is_directory": True,
                }
            )
        return state, message

    def _record_archive_failure(self, error):
        if isinstance(error, jobs.WorkerIngestionFailure):
            issues = error.diagnostic["issues"]
            jobs.emit_record(
                "WARNING",
                "archive_ingestion_invalid",
                "archive",
                "failed",
                (self.archive_run.run_id if self.archive_run else None),
            )
        else:
            message = str(error)[-8192:] or type(error).__name__
            if message != jobs._ARCHIVE_FENCE_MESSAGE:
                severity = (
                    "WARNING" if isinstance(error, ValueError) else "ERROR"
                )
                jobs.emit_record(
                    severity,
                    "archive_generation_failed",
                    "archive",
                    "failed",
                    (self.archive_run.run_id if self.archive_run else None),
                )
            issues = [
                {
                    "relative_path": None,
                    "code": "archive_generation_failed",
                    "message": message,
                    "atom_ref": None,
                    "related_paths": [],
                }
            ]
        self._record_ingestion_issues("archive", issues)

    def _archive_superseded(self, result):
        if self.deferred_archive is None:
            return True
        if isinstance(result, jobs.ArchiveCoverageLost):
            return False
        if (
            isinstance(result, jobs.ArchiveInputsChanged)
            or isinstance(result, tuple)
            and result[0] != self.deferred_archive["endpoints"]
        ):
            self.archive_dirty = True
        return self.archive_dirty

    def _admit_archive(self, result):
        temporary = result.get("_archive_temp")
        if "batch_artifact" in result:
            payload = {
                key: value
                for key, value in result.items()
                if key != "_archive_temp"
            }
            payload["base_generation"] = self.live_generation
        elif "paths" in result or result.get("unchanged") is True:
            payload = result | {"base_generation": self.live_generation}
        else:
            payload = self._archive_snapshot_payload(result)
        outcome = jobs.admit_generation(
            self.database_socket,
            self.instance_id,
            str(jobs.Path(temporary.name).resolve()) if temporary else None,
            payload,
            None,
            archive=True,
        )
        if jobs.os.environ.get("ANECHOIC_STARTUP_TIMING") == "1":
            from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30 \
                .sources.sources__shared import mark_startup_timing  # fmt: skip

            mode = (
                "reused"
                if result.get("unchanged") is True
                else "native_delta"
                if "paths" in result
                else "full"
            )
            mark_startup_timing("archive_load_ended", mode=mode)
        self.live_generation = outcome["generation"]
        if self.generation_reuse is not None:
            self.generation_reuse.base_generation = self.live_generation
        self.deferred_archive = None

    def _archive_snapshot_payload(self, result):
        deferred = self.deferred_archive
        snapshot = result["snapshot"]
        for key in ("atoms", "relations"):
            snapshot[key].extend(deferred["snapshot"][key])
        if issues := deferred["snapshot"].get("ingestion_issues"):
            snapshot.setdefault("ingestion_issues", []).extend(issues)
        hashes = deferred["carrier_hashes"] | result["carrier_hashes"]
        digest = jobs.sha256(
            jobs.json.dumps(
                snapshot,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ).encode()
        ).hexdigest()
        payload = {
            "base_generation": self.live_generation,
            "snapshot": snapshot,
            "snapshot_sha256": digest,
            "carrier_hashes": hashes,
        }
        return (
            payload | {"replace": True}
            if result.get("replace") is True
            else payload
        )
