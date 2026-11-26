"""Check the Project manifest gate and peer readiness."""

import os
from pathlib import Path

import httpx2

from .models import JobsHealth, KernelHealth, ManifestBinding, ReadinessState, WorkerRuns


def failure(code, message):
    rejected = code in {"tool_input_invalid", "tool_unavailable"}
    diagnostic = "Unknown Tool" if code == "tool_unavailable" else code if rejected else f"{code}: {message}"
    return {"error": {"code": code, "message": message, "tool_result": {
        "outcome": "rejected" if rejected else "failed", "diagnostics": [diagnostic]}}}


def manifest_guard():
    binding = os.environ.get("ANECHOIC_BETA_DIRECT_MANIFEST")
    if binding is None:
        return lambda: None
    value = ManifestBinding.model_validate_json(binding)
    manifest, gate, expected = Path(value.path), Path(value.gate), value.version

    def check():
        try:
            state = gate.read_text(encoding="ascii")
        except FileNotFoundError:
            try:
                info = manifest.lstat()
                version = (info.st_dev, info.st_ino, info.st_mode, info.st_size, info.st_mtime_ns, info.st_ctime_ns)
                if version == expected:
                    return None
            except OSError:
                return failure("project_manifest_invalid", "The Project Manifest is missing or invalid")
        except (OSError, UnicodeError):
            return failure("admission_gate_unavailable", "The Project admission gate is unavailable")
        else:
            if state == "project_manifest_invalid":
                return failure("project_manifest_invalid", "The Project Manifest is missing or invalid")
            if state not in ("", "project_manifest_reloading"):
                return failure("admission_gate_unavailable", "The Project admission gate is unavailable")
        return failure("project_manifest_reloading", "The Project Manifest binding is being reloaded")
    return check


async def peer(socket_path, method, path, *, timeout=None, **kwargs):
    if timeout is None:
        timeout = httpx2.Timeout(None, connect=10) if os.getenv("ANECHOIC_TEST_IMAGE_DEADLINES") == "0" else 10
    async with httpx2.AsyncClient(transport=httpx2.AsyncHTTPTransport(uds=str(socket_path)),
                                  base_url="http://private", timeout=timeout, trust_env=False) as client:
        data = (await client.request(method, path, **kwargs)).json()
    if not isinstance(data, dict) or set(data) not in ({"result"}, {"error"}):
        raise ValueError("Invalid upstream response")
    return data


class Readiness:
    def __init__(self, instance, digest, database, jobs):
        self.instance, self.digest, self.database, self.jobs = instance, digest, database, jobs
        self.guard = manifest_guard()
        self.admitted = False

    async def status(self):
        return ReadinessState.validate_python(await self._status()).model_dump(exclude_unset=True)

    async def _status(self):
        if problem := self.guard():
            return manifest_state(problem)
        try:
            startup = await self.startup()
            health = KernelHealth.model_validate((await peer(self.database, "GET", "/health"))["result"])
            if health.instance_id != self.instance or health.manifest_sha256 != self.digest:
                raise ValueError("Invalid Kernel binding")
            if not health.ready:
                result = {"state": "degraded", **failure("project_build_unavailable", "The Project projection is unavailable")}
            elif not health.generation:
                raise ValueError("Invalid Kernel generation")
            else:
                result = {"state": "ready", "kernel_pid": health.pid, "generation": health.generation,
                          "archive_pending": health.archive_pending}
            result = startup or result
        except (httpx2.HTTPError, ValueError, TypeError, KeyError):
            return {"state": "unavailable"}
        if problem := self.guard():
            return manifest_state(problem)
        if result["state"] == "ready":
            self.admitted = True
        return result

    async def startup(self):
        health = JobsHealth.model_validate((await peer(self.jobs, "GET", "/health"))["result"])
        if health.instance_id != self.instance:
            raise ValueError("Invalid Orchestrator binding")
        if not health.watcher_active:
            return {"state": "degraded", **failure("project_build_unavailable", "The Project watcher is unavailable")}
        if not health.startup_replay_pending:
            return None
        runs = WorkerRuns.model_validate((await peer(self.jobs, "GET", "/jobs/worker-runs",
                                                     params={"instance_id": self.instance}))["result"])
        latest = runs.latest
        if runs.active is None and latest and latest.state in ("failed", "aborted") and not latest.retrying:
            return {"state": "degraded", **failure("project_build_unavailable", "The Project projection is unavailable")}
        return {"state": "pending"}


def manifest_state(problem):
    code = problem["error"]["code"]
    return {"state": {"project_manifest_invalid": "degraded", "project_manifest_reloading": "pending"}.get(code, "unavailable"), **problem}
