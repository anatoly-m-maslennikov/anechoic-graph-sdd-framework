"""Load deferred Archive carriers while live generation work continues."""
import http.client
from hashlib import sha256
import json
import os
from pathlib import Path
import signal
import threading
import time
from uuid import uuid4

from .abort import WorkerAborted
from .jobs import _Run
from .generation import DeltaRequiresReconciliation, WorkerIngestionFailure, admit_generation, read_reuse
from .startup_checkpoint import archive_checkpoint, compatible_checkpoint
from .watcher_diagnostics import emit_record

_ARCHIVE_ERRORS = (OSError, ValueError, TypeError, KeyError, RuntimeError, http.client.HTTPException)
_ARCHIVE_FENCE_MESSAGE = "Archive watcher coverage was lost during capture"
ARCHIVE_RECONCILIATION = "archive_reconciliation"


class ArchiveInputsChanged(RuntimeError):
    """The archive population changed during a capture."""


class ArchiveCoverageLost(RuntimeError):
    """The watcher cannot establish archive currentness."""


class ArchiveJobs:
    def _initialize_archive(self):
        self.deferred_archive = None
        self.archive_run = self.archive_process = None
        self.archive_thread = self.archive_result = None
        self.archive_dirty = False
        self.archive_reconciliation_pending = False
        self.archive_watching = False
        self.live_generation = None

    def _capture_options(self, reuse, paths, *, explicit=False):
        if self.skip_archives:
            epoch = self.watcher.capture_epoch(trace=True) if self.thread is not None and not explicit else None
            return {"foreground": True, "watcher_guarded": epoch is not None}, epoch
        if explicit:
            return {}, None
        managed = self.thread is not None
        if paths is not None:
            epoch = self.watcher.capture_epoch(trace=True) if managed else None
            return ({"foreground": True} if self.deferred_archive else {}), epoch
        if not (self.startup_capture or self.deferred_archive or managed):
            return {}, None
        has_archive = self.watcher.has_archive_roots()
        if has_archive and not (self.startup_capture or self.deferred_archive):
            return {}, None
        epoch = self.watcher.capture_epoch(trace=True)
        if self.startup_capture:
            options = {"watcher_guarded": epoch is not None, "foreground": True}
            if epoch is not None and compatible_checkpoint(reuse):
                options["incremental"] = True
            return options, epoch
        foreground = self.deferred_archive is not None or reuse is None or reuse.get("archive_pending") is True
        return {"watcher_guarded": epoch is not None, "foreground": foreground}, epoch

    def _restart_archive(self, reuse, result):
        if not {"unchanged", "paths", "compiler"} & result.keys():
            return None
        if reuse.get("checkpoint_scope") == "foreground":
            return {"roots": list(self.watcher.archive_roots()), "snapshot": {"atoms": [], "relations": []},
                    "carrier_hashes": {}, "endpoints": result.get("reuse", reuse)["endpoints"],
                    "checkpoint_source": result.get("reuse", reuse)}
        checkpoint = archive_checkpoint(reuse)
        if "compiler" in result:
            checkpoint["endpoints"] = result["reuse"]["endpoints"]
        roots = self.watcher.archive_roots()
        if not roots and not checkpoint["carrier_hashes"] and not reuse.get("archive_pending"):
            return None
        return {"roots": list(roots), "snapshot": {"atoms": [], "relations": []}, "carrier_hashes": {},
                "endpoints": checkpoint["endpoints"], "checkpoint": checkpoint}

    def _needs_foreground(self, result):
        if "paths" not in result:
            return True
        return any(
            atom["status_group"] == "Archived"
            for atom in result["snapshot"]["atoms"]
        ) or any(
            str(Path(parent) / name) in self.deferred_archive["carrier_hashes"]
            for parent, name in result["paths"]
        )

    @staticmethod
    def _include_archive_pending(result, deferred):
        if deferred and (deferred["roots"] or deferred["snapshot"]["atoms"]
                         or deferred["snapshot"].get("ingestion_issues") or "checkpoint" in deferred
                         or "checkpoint_source" in deferred):
            result["archive_pending"] = True
            if "archive_versions" in deferred:
                result["archive_versions"] = deferred.pop("archive_versions")

    def _is_archive_path(self, path):
        if not path:
            return False
        control = Path(self.binding["root"]) / self.binding["control_root"]
        location = Path(path)
        return (
            location.is_relative_to(control)
            and "09_archived" in location.relative_to(control).parts
        )

    def _partition_archive_changes(self, changes):
        if self.skip_archives:
            return [live for change in changes if (live := self._foreground_change(change)) is not None]
        if self.deferred_archive is None:
            return changes
        live = []
        for change in changes:
            paths = [change[key] for key in ("old_path", "new_path") if change and change[key]]
            deferred = [self._is_archive_path(path) for path in paths]
            if any(deferred):
                self.archive_dirty = True
            if not deferred or not all(deferred):
                live.append(change)
        return live

    def _foreground_change(self, change):
        paths = [change.get("old_path"), change.get("new_path")]
        archived = [self._is_archive_path(path) for path in paths]
        if not any(archived):
            return change
        if all(archived[index] or not path for index, path in enumerate(paths)):
            return None
        index = 1 if archived[0] else 0
        return {**change, "old_path": paths[index], "new_path": None,
                "event_type": "created" if index else "deleted"}

    def _accept_live_generation(self, generation, result, deferred):
        self.live_generation = generation
        self.startup_capture = False
        full = "batch_artifact" in result or (
            "snapshot" in result and "paths" not in result
        )
        if deferred is not None or full:
            self._accept_deferred_archive(
                deferred if "archive_pending" in result else None
            )
            self.unconfirmed_lifecycle_write = False

    def _accept_deferred_archive(self, deferred):
        previous = self.deferred_archive
        self.deferred_archive = deferred
        if previous is None:
            self.archive_dirty |= deferred is not None and self.archive_run is not None
        elif deferred is not None:
            keys = ("roots", "endpoints", "checkpoint", "checkpoint_source", "snapshot", "carrier_hashes")
            self.archive_dirty |= any(previous.get(key) != deferred.get(key) for key in keys)

    def _run_archive(self):
        if self.skip_archives or self.startup_capture or self.startup_replay or self.stopping.is_set():
            return
        if self.archive_thread is not None:
            if self.archive_thread.is_alive():
                return
            self.archive_thread = None
            self._finish_archive()
        if self.deferred_archive is None and self.archive_watching:
            return
        if self.archive_run is not None and not self.archive_dirty:
            return
        with self.lock:
            self.archive_dirty = False
            if self.deferred_archive is not None:
                self.archive_run = _Run(
                    state="running", started_at=time.time(), run_id=uuid4().hex
                )
            self.archive_thread = threading.Thread(
                target=self._capture_archive, args=(self.deferred_archive,), daemon=True)
            self.archive_thread.start()

    def _capture_archive(self, deferred):
        try:
            self.watcher.start_ticket_watch()
            if not self.watcher.watch_archives():
                raise ArchiveCoverageLost("Archive watcher coverage is unavailable")
            self.archive_watching = True
            if deferred is not None:
                checkpoint = deferred.get("checkpoint")
                source = deferred.get("checkpoint_source")
                if source is not None:
                    record = read_reuse(self.database_socket, self.instance_id, scope="archive")
                    candidate = record.model_dump(exclude_unset=True) if record is not None else None
                    if compatible_checkpoint(candidate) and candidate["inputs"] == source["inputs"]:
                        checkpoint = archive_checkpoint(candidate)
                        checkpoint["endpoints"] = deferred["endpoints"]
                endpoints, result = self._archive_snapshot(deferred["endpoints"], checkpoint, deferred)
                replace = deferred.get("replace") or (source is not None and checkpoint is None)
                if self.stopping.is_set():
                    if (temporary := result.pop("_archive_temp", None)) is not None:
                        temporary.cleanup()
                    return
                self.archive_result = endpoints, result | {"replace": True} if replace else result
        except _ARCHIVE_ERRORS as error:
            self.archive_result = error
        finally:
            self.watcher.queue.put({})

    def _finish_archive(self):
        result, self.archive_result = self.archive_result, None
        try:
            self._finish_archive_result(result)
        finally:
            if isinstance(result, tuple) and (temporary := result[1].pop("_archive_temp", None)) is not None:
                temporary.cleanup()

    def _finish_archive_result(self, result):
        if self.archive_run is None:
            if isinstance(result, Exception):
                emit_record("WARNING", "archive_watcher_unavailable", "archive", "degraded")
                self.archive_watching = True
            return
        state, message = "succeeded", None
        if self.deferred_archive is not None and isinstance(result, WorkerAborted):
            state, message = "aborted", str(result)
            self.archive_dirty = False
        elif self._archive_superseded(result):
            state, message = "superseded", "Archive scope changed during capture"
        else:
            try:
                if isinstance(result, Exception):
                    raise result
                self._admit_archive(result[1])
            except DeltaRequiresReconciliation:
                if "paths" in result[1] or result[1].get("unchanged") is True:
                    state, message = "superseded", "Archive requires full capture"
                    self.deferred_archive = {key: value for key, value in self.deferred_archive.items()
                                             if key != "checkpoint"} | {"replace": True}
                    self.archive_dirty = True
                else:
                    state, message = "superseded", "Archive requires full native reconciliation"
                    self.archive_reconciliation_pending = True
                    self.watcher.queue.put({"event_type": ARCHIVE_RECONCILIATION, "old_path": None,
                                            "new_path": None, "is_directory": True})
            except _ARCHIVE_ERRORS as error:
                state, message = "failed", str(error)[-2048:]
                self._record_archive_failure(error)
        with self.lock:
            self.archive_run.state = state
            self.archive_run.finished_at = time.time()
            if message is not None:
                self.archive_run.message = message

    def _record_archive_failure(self, error):
        if isinstance(error, WorkerIngestionFailure):
            issues = error.diagnostic["issues"]
            emit_record("WARNING", "archive_ingestion_invalid", "archive", "failed",
                        (self.archive_run.run_id if self.archive_run else None))
        else:
            message = str(error)[-8192:] or type(error).__name__
            if message != _ARCHIVE_FENCE_MESSAGE:
                severity = "WARNING" if isinstance(error, ValueError) else "ERROR"
                emit_record(severity, "archive_generation_failed", "archive", "failed",
                            (self.archive_run.run_id if self.archive_run else None))
            issues = [{"relative_path": None, "code": "archive_generation_failed", "message": message,
                       "atom_ref": None, "related_paths": []}]
        self._record_ingestion_issues("archive", issues)

    def _archive_superseded(self, result):
        if self.deferred_archive is None:
            return True
        if isinstance(result, ArchiveCoverageLost):
            return False
        if (isinstance(result, ArchiveInputsChanged)
                or isinstance(result, tuple) and result[0] != self.deferred_archive["endpoints"]):
            self.archive_dirty = True
        return self.archive_dirty

    def _admit_archive(self, result):
        temporary = result.get("_archive_temp")
        if "batch_artifact" in result:
            payload = {key: value for key, value in result.items() if key != "_archive_temp"}
            payload["base_generation"] = self.live_generation
        elif "paths" in result or result.get("unchanged") is True:
            payload = result | {"base_generation": self.live_generation}
        else:
            payload = self._archive_snapshot_payload(result)
        outcome = admit_generation(self.database_socket, self.instance_id,
                                   str(Path(temporary.name).resolve()) if temporary else None, payload, None, archive=True)
        if os.environ.get("ANECHOIC_STARTUP_TIMING") == "1":
            from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import mark_startup_timing
            mode = "reused" if result.get("unchanged") is True else "native_delta" if "paths" in result else "full"
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
        digest = sha256(json.dumps(
            snapshot, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        payload = {"base_generation": self.live_generation, "snapshot": snapshot, "snapshot_sha256": digest,
                   "carrier_hashes": hashes}
        return payload | {"replace": True} if result.get("replace") is True else payload

    def _close_archive(self):
        with self.lock:
            self._stop_archive()
        if self.archive_thread is not None:
            self.archive_thread.join(1)
            if not self.archive_thread.is_alive() and isinstance(self.archive_result, tuple):
                if (temporary := self.archive_result[1].pop("_archive_temp", None)) is not None:
                    temporary.cleanup()

    def _stop_archive(self):
        if self.archive_process is not None and self.archive_process.poll() is None:
            try:
                os.killpg(self.archive_process.pid, signal.SIGKILL)
            except ProcessLookupError:
                return False
            return True
        return False
