"""Run-scoped Worker liveness and cancellation."""
import os
import signal


class WorkerAborted(RuntimeError):
    pass


class AbortJobs:
    def _worker_alive(self):
        if self.warm_capture is not None:
            return self.warm_capture.alive()
        return self.process is not None and self.process.poll() is None

    def _stop_worker(self):
        if self.warm_capture is not None:
            self.warm_capture.cancel()
        elif self.process is not None:
            os.killpg(self.process.pid, signal.SIGKILL)

    def _register_warm_capture(self, capture):
        with self.lock:
            if self.stopping.is_set():
                return False
            self.warm_capture = capture
            return True

    def status(self):
        with self.lock:
            active = dict(self.active) if self.active is not None else None
            if active is not None:
                active["worker_alive"] = self._worker_alive()
            result = {"active": active, "latest": dict(self.latest) if self.latest is not None else None}
            if self.archive_run is not None:
                process = self.archive_process
                result["archive"] = {**self.archive_run, "worker_alive": process is not None and process.poll() is None}
            return result

    def abort(self, request):
        if (not isinstance(request, dict) or set(request) != {"instance_id", "run_id"}
                or not isinstance(request["run_id"], str) or not request["run_id"]):
            return 400, {"error": {"code": "invalid_request", "message": "Invalid abort fields"}}
        if request["instance_id"] != self.instance_id:
            return 409, {"error": {"code": "instance_mismatch", "message": "Instance does not match"}}
        with self.lock:
            archive = self.archive_run
            if archive is not None and archive["run_id"] == request["run_id"]:
                if archive["state"] != "running" or not self._stop_archive():
                    return 409, {"error": {"code": "run_not_abortable", "message": "Run has no active Worker"}}
                archive["state"] = "aborting"
                return 202, {"result": {"run_id": request["run_id"], "state": "aborting"}}
            if (self.lifecycle_job is not None or self.active is None
                    or self.active.get("run_id") != request["run_id"] or self.aborted_run is not None
                    or not self._worker_alive()):
                return 409, {"error": {"code": "run_not_abortable", "message": "Run has no active Worker"}}
            try:
                self._stop_worker()
            except OSError:
                return 409, {"error": {"code": "run_not_abortable", "message": "Worker has exited"}}
            self.aborted_run = request["run_id"]
        return 202, {"result": {"run_id": request["run_id"], "state": "aborting"}}

