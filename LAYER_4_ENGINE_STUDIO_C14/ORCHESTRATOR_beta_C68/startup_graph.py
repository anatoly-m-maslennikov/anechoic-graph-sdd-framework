"""Build and admit the startup Realization Graph after core readiness."""

import os
import signal
import tempfile
import threading

from .generation import admit_generation, worker_request
from .generation_worker import GENERATION_ERRORS, ForegroundCoverageLost
from .jobs import operation_timeout
from .startup_checkpoint import ReuseRecord
from .watcher_diagnostics import FOREGROUND_FENCE_MESSAGE, emit_record
from .worker_reply import parse_graph_result


class StartupGraphJobs:
    def _attempt_explicit_graph(self, reuse):
        if reuse is None or reuse.get("graph_config") is None:
            raise ValueError(
                "Realization Graph requires an admitted core generation"
            )
        epoch = self.watcher.capture_epoch()
        if epoch is None:
            raise ForegroundCoverageLost(FOREGROUND_FENCE_MESSAGE)
        request = worker_request(
            self.binding, self.database_socket, self.instance_id, reuse, None
        )
        if "structure" not in request:
            raise ValueError(
                "Realization Graph requires an admitted Structure"
            )
        request.update(graph_only=True, force_graph=True, watcher_guarded=True)
        with tempfile.TemporaryDirectory(
            prefix="anechoic-graph-"
        ) as directory:
            payload = parse_graph_result(
                self._communicate_worker(directory, request),
                reuse["base_generation"],
            )
            self._check_explicit_graph_fence(epoch)
            admitted = admit_generation(
                self.database_socket,
                self.instance_id,
                None,
                payload,
                None,
                force_graph=True,
            )
        self.live_generation = admitted["generation"]
        self.generation_reuse = ReuseRecord.model_validate(
            {
                **reuse,
                **payload["reuse"],
                "base_generation": self.live_generation,
            }
        )
        return {"state": "succeeded", **admitted, "result_ids": {}}

    def _check_explicit_graph_fence(self, epoch):
        if (
            self.watcher.capture_fence(
                epoch,
                timeout=operation_timeout(45),
                run_id=self.active.run_id if self.active else None,
            )
            is not True
        ):
            raise ForegroundCoverageLost(FOREGROUND_FENCE_MESSAGE)

    def _initialize_startup_graph(self):
        self.graph_queued = False
        self.graph_thread = None
        self.graph_process = None
        self.graph_result = None

    def _run_startup_graph(self):
        if (
            self.startup_capture
            or self.startup_replay
            or self.stopping.is_set()
        ):
            return
        if self.graph_thread is not None:
            if self.graph_thread.is_alive():
                return
            self.graph_thread = None
            self._finish_startup_graph()
        if not self.graph_queued:
            return
        if (
            self.archive_reconciliation_pending
            or self.archive_thread is not None
            and self.archive_run is not None
            or self.deferred_archive is not None
            and (self.archive_run is None or self.archive_dirty)
        ):
            return
        witness = self.generation_reuse
        if witness is None or witness.graph_config is None:
            self.graph_queued = False
            return
        epoch = self.watcher.capture_epoch()
        if epoch is None:
            return
        self.graph_queued = False
        reuse = witness.model_dump(exclude_unset=True)
        self.graph_thread = threading.Thread(
            target=self._capture_startup_graph,
            args=(reuse, epoch, self.watcher.foreground_events()),
            daemon=True,
        )
        self.graph_thread.start()

    def _capture_startup_graph(self, reuse, epoch, events):
        base = reuse["base_generation"]
        try:
            request = worker_request(
                self.binding,
                self.database_socket,
                self.instance_id,
                reuse,
                None,
            )
            if "structure" not in request:
                raise ValueError("The startup graph has no admitted Structure")
            request.update(graph_only=True, watcher_guarded=True)
            with tempfile.TemporaryDirectory(
                prefix="anechoic-graph-"
            ) as directory:
                payload = parse_graph_result(
                    self._communicate_worker(directory, request, graph=True),
                    base,
                )
            if (
                self.watcher.replay_fence(epoch, timeout=operation_timeout(45))
                is not True
            ):
                raise ValueError("The startup graph lost watcher coverage")
        except GENERATION_ERRORS as error:
            payload = error
        self.graph_result = (base, events, payload)
        self.watcher.queue.put({})

    def _finish_startup_graph(self):
        (base, events, payload), self.graph_result = self.graph_result, None
        witness = self.generation_reuse
        if (
            witness is None
            or base != witness.base_generation
            or events != self.watcher.foreground_events()
        ):
            self.graph_queued = True
            return
        try:
            if isinstance(payload, Exception):
                raise payload
            if payload.get("unchanged") is True:
                return
            admitted = admit_generation(
                self.database_socket, self.instance_id, None, payload, None
            )
            self.live_generation = admitted["generation"]
            self.generation_reuse = witness.model_copy(
                update={
                    **payload["reuse"],
                    "base_generation": self.live_generation,
                }
            )
        except GENERATION_ERRORS as error:
            emit_record(
                "ERROR",
                "realization_graph_failed",
                "graph",
                "failed",
                details={"message": str(error)[-2048:]},
            )

    def _close_startup_graph(self):
        with self.lock:
            if (
                self.graph_process is not None
                and self.graph_process.poll() is None
            ):
                try:
                    os.killpg(self.graph_process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
        if self.graph_thread is not None:
            self.graph_thread.join(1)
