"""Check the direct transport's degraded startup and binding recovery."""
import asyncio
import os
import socket
import subprocess
import sys
import time
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory, TemporaryFile
from unittest.mock import NonCallableMock
from unittest.mock import Mock, patch

import httpx2
from mcp.server.lowlevel import Server
from MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__shared import (
    HEALTH_PATH, MCP_PATH, BackendClient, create_http_app, http_main,
)
from .FEATURE_MCP__tests__shared import write_manifest
from .test_launcher_runtime_profiles import DirectSupervisorProbe


async def observe_diagnostics(app):
    async with httpx2.AsyncClient(transport=httpx2.ASGITransport(app=app), base_url="http://localhost") as client:
        health = await client.get(HEALTH_PATH)
        call = await client.post(MCP_PATH, json={})
    return (health.status_code, health.json()), (call.status_code, call.json())


class DirectRuntimeDiagnosticsTests(unittest.IsolatedAsyncioTestCase):
    async def _diagnostics(self, gate):
        with socket.socket() as probe:
            probe.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            probe.bind(("0.0.0.0", 8092))
        log = self.enterContext(TemporaryFile(mode="w+"))
        engine = Path(__file__).resolve().parents[3]
        environment = {**os.environ, "PYTHONPATH": str(engine), "ANECHOIC_RUNTIME_STACK": "beta_next",
                       "ANECHOIC_BETA_BACKEND_SOCKET": str(gate.parent / "backend.sock"),
                       "ANECHOIC_BETA_DIRECT_TRANSPORT_GATE": str(gate), "ANECHOIC_BETA_DIRECT_DIAGNOSTICS": "1"}
        process = subprocess.Popen([sys.executable, "-B", "-m", "MCP_PATCHBAY_C21.FEATURE_MCP.server",
                                    "--project-root", str(gate.parent), "--transport", "streamable-http"],
                                   env=environment, stdout=log, stderr=log)
        self.addCleanup(self._stop_diagnostics, process)
        client = await self.enterAsyncContext(httpx2.AsyncClient(base_url="http://127.0.0.1:8092", trust_env=False))
        deadline = time.monotonic() + 30
        while time.monotonic() < deadline and process.poll() is None:
            try:
                response = await client.get(HEALTH_PATH)
                if response.status_code == 200 and response.json().get("health_warning") == "project_manifest_invalid":
                    gate.write_text("project_manifest_reloading")
                    try:
                        identity = await client.get(HEALTH_PATH)
                        if identity.json() == {"state": "pending"} and process.poll() is None:
                            return client
                    finally:
                        gate.write_text("project_manifest_invalid")
            except (httpx2.TransportError, ValueError):
                pass
            await asyncio.sleep(.1)
        log.seek(0)
        self.fail("Diagnostics process did not start: " + log.read()[-4000:])

    @staticmethod
    def _stop_diagnostics(process):
        if process.poll() is None:
            process.terminate()
        try:
            process.wait(timeout=15)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
        with socket.socket() as probe:
            probe.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            probe.bind(("0.0.0.0", 8092))

    def test_missing_manifest_serves_diagnostics_until_initial_binding_is_available(self):
        directory = Path(self.enterContext(TemporaryDirectory())).resolve()
        manifest = write_manifest(self, directory / "_anechoic_anechoic")
        raw = manifest.read_bytes()
        manifest.unlink()
        observed = []
        app = None

        def restore(_gate):
            nonlocal app
            self.assertEqual(([], []), (probe.launched["owner"], probe.launched["api"]))
            _, environment = probe.launched["diagnostics"][-1]
            with patch.dict(os.environ, environment), patch("uvicorn.run") as run:
                self.assertIsNone(http_main(["--project-root", str(directory)]))
            run.assert_called_once()
            app = run.call_args.args[0]
            observed.append(asyncio.run(observe_diagnostics(app)))
            manifest.write_bytes(raw)

        def bound(gate):
            self.assertFalse(gate.exists())
            observed.append(asyncio.run(observe_diagnostics(app)))

        probe = DirectSupervisorProbe(manifest, diagnostics=restore, bound=bound)
        status, stderr = probe.run(directory, "beta_next")
        self.assertEqual(0, status)
        self.assertEqual(1, stderr.count("Project Manifest is missing or invalid"))
        self.assertEqual([1, 1, 1, 1], [len(probe.launched[role]) for role in ("diagnostics", "owner", "api", "mcp")])
        self.assertEqual([((200, {"state": "degraded", "health_warning": "project_manifest_invalid"}),
                           (409, {"error": "project_manifest_invalid"})),
                          ((200, {"state": "pending"}), (200, {"error": "project_build_pending"}))], observed)

    def test_managed_backend_attaches_before_advertising_projection_readiness(self):
        selection = NonCallableMock(
            spec_set=['instance_id', 'manifest_sha256'],
            instance_id="project", manifest_sha256="digest")
        binding = {"instance_id": "project", "manifest_sha256": "digest", "pid": 21}
        pending = httpx2.Response(200, json={**binding, "state": "pending"})
        degraded = httpx2.Response(200, json={
            **binding, "state": "degraded", "error": {"code": "project_build_unavailable"},
        })
        ready = httpx2.Response(200, json={
            **binding, "state": "ready", "kernel_pid": 22, "generation": "generation",
        })
        http = Mock()
        http.get.side_effect = [pending, pending, degraded, ready]
        client = BackendClient(selection, None, http)
        client.start()
        self.assertEqual(21, client.backend_pid)
        self.assertFalse(client.available)
        self.assertFalse(client.available)
        self.assertTrue(client.available)

    async def test_public_health_distinguishes_pending_startup_from_unavailability(self):
        directory = Path(self.enterContext(TemporaryDirectory())).resolve()
        gateway = NonCallableMock(
            spec_set=['health_state', 'build_server'],
            health_state=Mock(side_effect=["pending", "degraded", "unavailable"]),
                                  build_server=lambda: Server("health-test"))
        app = create_http_app(directory, runtime_gateway=gateway, direct_gate=directory / "api.draining")
        client = await self.enterAsyncContext(httpx2.AsyncClient(
            transport=httpx2.ASGITransport(app=app), base_url="http://localhost",
        ))
        for state, expected in (("pending", 200), ("degraded", 200), ("unavailable", 503)):
            with self.subTest(state=state):
                response = await client.get(HEALTH_PATH)
                payload = {"state": state}
                if state == "degraded":
                    payload["health_warning"] = "project_build_unavailable"
                self.assertEqual(expected, response.status_code)
                self.assertEqual(payload, response.json())

    async def test_reload_gate_and_faulty_gate_have_different_status(self):
        gate = Path(self.enterContext(TemporaryDirectory())).resolve() / "api.draining"
        gate.write_text("project_manifest_invalid")
        client = await self._diagnostics(gate)
        for content, state, health_code, tool_code, error in (
            (b"project_manifest_reloading", "pending", 200, 409, "project_manifest_reloading"),
            (b"\xff", "unavailable", 503, 503, "admission_gate_unavailable"),
        ):
            with self.subTest(state=state):
                gate.write_bytes(content)
                response = await client.get(HEALTH_PATH)
                expected = {"state": state}
                if state != "pending":
                    expected["health_warning"] = error
                self.assertEqual((health_code, expected), (response.status_code, response.json()))
                response = await client.post(MCP_PATH, json={})
                self.assertEqual((tool_code, {"error": error}), (response.status_code, response.json()))
