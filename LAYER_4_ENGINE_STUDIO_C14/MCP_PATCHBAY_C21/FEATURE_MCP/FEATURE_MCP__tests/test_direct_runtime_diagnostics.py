"""Check the direct transport's degraded startup and binding recovery."""
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import NonCallableMock
from unittest.mock import Mock

import httpx2
from mcp.server.lowlevel import Server
from MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__shared import (
    HEALTH_PATH, BackendClient, create_http_app,
)


class DirectRuntimeDiagnosticsTests(unittest.IsolatedAsyncioTestCase):
    def test_managed_backend_attaches_before_advertising_projection_readiness(
        self,
    ):
        selection = NonCallableMock(
            spec_set=["instance_id", "manifest_sha256"],
            instance_id="project",
            manifest_sha256="digest",
        )
        binding = {
            "instance_id": "project",
            "manifest_sha256": "digest",
            "pid": 21,
        }
        pending = httpx2.Response(200, json={**binding, "state": "pending"})
        degraded = httpx2.Response(
            200,
            json={
                **binding,
                "state": "degraded",
                "error": {"code": "project_build_unavailable"},
            },
        )
        ready = httpx2.Response(
            200,
            json={
                **binding,
                "state": "ready",
                "kernel_pid": 22,
                "generation": "generation",
            },
        )
        http = Mock()
        http.get.side_effect = [pending, pending, degraded, ready]
        client = BackendClient(selection, None, http)
        client.start()
        self.assertEqual(21, client.backend_pid)
        self.assertFalse(client.available)
        self.assertFalse(client.available)
        self.assertTrue(client.available)

    async def test_public_health_reports_current_gateway_readiness(
        self,
    ):
        directory = Path(self.enterContext(TemporaryDirectory())).resolve()
        gateway = NonCallableMock(
            spec_set=["ready", "build_server"],
            build_server=lambda: Server("health-test"),
        )
        app = create_http_app(
            directory,
            runtime_gateway=gateway,
        )
        client = await self.enterAsyncContext(
            httpx2.AsyncClient(
                transport=httpx2.ASGITransport(app=app),
                base_url="http://localhost",
            )
        )
        for ready, state, status in (
            (True, "ready", 200),
            (False, "unavailable", 503),
        ):
            with self.subTest(state=state):
                gateway.ready = ready
                response = await client.get(HEALTH_PATH)
                self.assertEqual(status, response.status_code)
                self.assertEqual({"state": state}, response.json())
