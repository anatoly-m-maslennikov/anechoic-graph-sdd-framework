"""Basic worker job and private socket connection."""
import http.client
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import threading
import time

ENGINE = Path(__file__).resolve().parents[1]
FIELDS = {"instance_id", "root", "control_root", "manifest_path", "manifest_sha256", "project_prefix"}
DEADLINE_SECONDS = 120


def operation_timeout(seconds):
    return (None if os.getenv("ANECHOIC_TEST_IMAGE_DEADLINES") == "0"
            else seconds)


class Jobs:
    def __init__(self, instance_id):
        self.instance_id = instance_id
        self.lock = threading.Lock()
        self.active = None
        self.latest = None

    def status(self):
        with self.lock:
            return {"active": self.active, "latest": self.latest}

    def build(self, request):
        if not isinstance(request, dict) or set(request) != FIELDS:
            return 400, {"error": {"code": "invalid_request", "message": "Invalid build fields"}}
        if request["instance_id"] != self.instance_id:
            return 409, {"error": {"code": "instance_mismatch", "message": "Instance does not match"}}
        with self.lock:
            if self.active is not None:
                return 409, {"error": {"code": "build_active", "message": "A build is already active"}}
            self.active = {"state": "running", "started_at": time.time()}
        outcome = {"state": "failed", "code": "internal_error"}
        try:
            binding = {key: value for key, value in request.items() if key != "instance_id"}
            env = {key: value for key, value in os.environ.items() if key != "PYTHONHOME"}
            env["PYTHONPATH"] = str(ENGINE)
            process = subprocess.run(
                [sys.executable, "-B", "-P", "-m", "WORKERS_beta_C69.WORKERS_beta_C69__shared"],
                input=json.dumps(binding), text=True, capture_output=True,
                timeout=operation_timeout(DEADLINE_SECONDS), cwd=ENGINE,
                env=env, check=False)
            if process.returncode:
                raise RuntimeError("Worker failed: " + process.stderr[:2048])
            snapshot = json.loads(process.stdout)
            if not isinstance(snapshot, dict):
                raise ValueError("Worker returned an invalid snapshot")
            outcome = {"state": "succeeded"}
            return 200, {"result": snapshot}
        except subprocess.TimeoutExpired:
            outcome = {"state": "failed", "code": "worker_timeout"}
            return 504, {"error": {"code": "worker_timeout", "message": "Worker deadline exceeded"}}
        except (OSError, ValueError, RuntimeError) as error:
            outcome = {"state": "failed", "code": "worker_failed"}
            return 502, {"error": {"code": "worker_failed", "message": str(error)[:2048]}}
        finally:
            with self.lock:
                self.latest = {**self.active, **outcome, "finished_at": time.time()}
                self.active = None


class UnixConnection(http.client.HTTPConnection):
    def __init__(self, path):
        super().__init__("localhost", timeout=operation_timeout(30))
        self.path = path

    def connect(self):
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.settimeout(self.timeout)
        self.sock.connect(self.path)


