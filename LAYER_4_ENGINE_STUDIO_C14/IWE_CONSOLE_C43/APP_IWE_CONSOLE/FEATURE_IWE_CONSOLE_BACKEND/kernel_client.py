"""Call the Kernel that owns the selected Project's database."""

from contextlib import contextmanager
from functools import partial
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import threading
from time import monotonic, sleep

import httpx2

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.FEATURE_TOOLS__shared import (
    ExplicitBlockingRuntimeFailure,
)
from KERNEL_MIXER_C59.KERNEL_MIXER_C59__shared import (
    QueryExecutionError,
    WorkbenchUnavailableError,
)


_MODULE = "KERNEL_MIXER_C59.kernel_process"
_STARTUP_SECONDS = 150
_OPERATIONS = frozenset(
    {
        "status",
        "interface_call",
        "run",
        "check",
        "page",
        "schema",
        "save_view",
        "load",
        "saved_list",
        "rebuild",
        "lifecycle",
        "atom_document",
    }
)


class KernelClient:
    def __init__(self, selection, process, http):
        self.selection = selection
        self._process = process
        self._http = http
        self._interface_lock = threading.RLock()

    @property
    def available(self):
        return self._process.poll() is None

    @property
    def pid(self):
        return self._process.pid

    def start(self):
        expected = {
            "ready": True,
            "instance_id": self.selection.instance_id,
            "manifest_sha256": self.selection.manifest_sha256,
            "pid": self._process.pid,
        }
        deadline = monotonic() + _STARTUP_SECONDS
        bounded = os.getenv("ANECHOIC_TEST_IMAGE_DEADLINES") != "0"
        while self.available and (not bounded or monotonic() < deadline):
            try:
                response = self._http.get("/health", timeout=0.5)
            except httpx2.TransportError:
                sleep(0.05)
                continue
            if response.status_code != 200 or response.json() != expected:
                raise RuntimeError(
                    "Kernel reported a different Project binding"
                )
            return
        raise WorkbenchUnavailableError(
            "Kernel did not start; see process diagnostics"
        )

    def __getattr__(self, name):
        if name not in _OPERATIONS:
            raise AttributeError(name)
        return partial(self._request, name)

    def _request(self, operation, *args, **kwargs):
        return self._call(
            "POST",
            "/database",
            json={
                "operation": operation,
                "args": args,
                "kwargs": kwargs,
                "instance_id": self.selection.instance_id,
            },
        )

    def worker_runs(self):
        return self._call(
            "GET",
            "/jobs/worker-runs",
            params={"instance_id": self.selection.instance_id},
        )

    def _call(self, method, path, **kwargs):
        try:
            response = self._http.request(method, path, **kwargs)
            envelope = response.json()
        except (httpx2.HTTPError, ValueError, RuntimeError) as error:
            raise WorkbenchUnavailableError(
                "Kernel unavailable; restart required"
            ) from error
        if isinstance(envelope, dict):
            if (
                response.is_success
                and set(envelope) == {"result"}
                and isinstance(envelope["result"], dict)
            ):
                return envelope["result"]
            fault = envelope.get("error")
            if isinstance(fault, dict) and isinstance(
                fault.get("message"), str
            ):
                errors = {
                    "value_error": ValueError,
                    "query_error": QueryExecutionError,
                    "workbench_unavailable": WorkbenchUnavailableError,
                }
                code = fault.get("code")
                if code in errors:
                    raise errors[code](fault["message"])
                if code in {"atom_not_found", "tool_input_invalid"}:
                    raise ExplicitBlockingRuntimeFailure(code, fault["message"])
        raise RuntimeError("Kernel operation failed; see process diagnostics")

    def wait(self):
        return self._process.wait()

    def close(self):
        try:
            self._http.close()
        finally:
            self._process.stdin.close()
            try:
                self._process.wait(timeout=15)
            except subprocess.TimeoutExpired:
                self._process.terminate()
                try:
                    self._process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self._process.kill()
                    self._process.wait()


def _start(selection, socket):
    engine = Path(__file__).resolve().parents[3]
    root = engine.parent
    paths = (engine,)
    environment = {
        **os.environ,
        "PYTHONPATH": os.pathsep.join(map(str, paths)),
    }
    command = [
        sys.executable,
        "-B",
        "-P",
        "-m",
        _MODULE,
        "--socket",
        str(socket),
    ]
    for name in (
        "project_root",
        "control_root",
        "instance_id",
        "manifest_sha256",
        "host_project_root",
        "default_workbench_storage",
        "default_journal_storage",
    ):
        value = getattr(selection, name)
        if value is not None:
            command.extend(["--" + name.replace("_", "-"), value])
    return subprocess.Popen(
        command, cwd=root, env=environment, stdin=subprocess.PIPE, stdout=2
    )


@contextmanager
def kernel_client(selection):
    with TemporaryDirectory(prefix="anechoic-db-", dir="/tmp") as directory:
        socket = Path(directory).resolve() / "db.sock"
        with httpx2.Client(
            transport=httpx2.HTTPTransport(uds=str(socket)),
            base_url="http://anechoic-kernel",
            trust_env=False,
            timeout=None,
        ) as http:
            client = KernelClient(selection, _start(selection, socket), http)
            try:
                client.start()
                yield client
            finally:
                client.close()
