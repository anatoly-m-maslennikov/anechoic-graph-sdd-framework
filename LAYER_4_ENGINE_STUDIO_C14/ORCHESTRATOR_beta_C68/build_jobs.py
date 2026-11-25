"""Build request admission."""
import threading
import time

from .flow import safe_target
from .jobs import FIELDS


class BuildJobs:
    def build(self, request):
        if not isinstance(request, dict) or set(request) not in (FIELDS, FIELDS | {"refresh_target"}):
            return 400, {"error": {"code": "invalid_request", "message": "Invalid build fields"}}
        target = request.get("refresh_target")
        if "refresh_target" in request and (not isinstance(target, str) or not target):
            return 400, {"error": {"code": "invalid_request", "message": "Invalid refresh target"}}
        if request["instance_id"] != self.instance_id:
            return 409, {"error": {"code": "instance_mismatch", "message": "Instance does not match"}}
        if {key: request[key] for key in FIELDS - {"instance_id"}} != self.binding:
            return 409, {"error": {"code": "binding_mismatch", "message": "Binding does not match"}}
        with self.lock:
            if self.stopping.is_set():
                return 503, {"error": {"code": "orchestrator_stopping", "message": "Orchestrator is stopping"}}
            job = self.inflight or self.pending
            if job is not None and job["target"] != target:
                return 409, {"error": {"code": "build_active", "message": "Another refresh is active"}}
            if job is None:
                job = self.pending = {"event": threading.Event(), "outcome": None, "target": target, "requests": [], "omitted_requests": 0}
                self.watcher.queue.put({})
            request_time = time.time()
            if job is self.inflight and self.flow is not None:
                self.flow.input("rebuild_request", target=safe_target(target), detail={"coalesced": True}, at=request_time, trigger=False)
            elif len(job["requests"]) < 200:
                job["requests"].append(request_time)
            else:
                job["omitted_requests"] += 1
        return self._wait_build(job)
