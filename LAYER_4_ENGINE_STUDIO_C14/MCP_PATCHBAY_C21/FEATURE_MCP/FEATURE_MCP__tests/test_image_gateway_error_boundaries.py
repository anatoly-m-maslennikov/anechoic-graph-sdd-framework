"""Focused MCP image/process/gateway failure-boundary checks."""
from .native_query_test_support import local_gateway


from contextlib import redirect_stderr
import io
import json
import os
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock, Mock, patch

import httpx2
from mcp import types
from mcp.server.lowlevel import Server

MCP = Path(__file__).resolve().parents[1]
TOOLS = MCP.parents[1] / "FEATURE_PROGRAMMATIC" / "FEATURE_TOOLS"

from MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__shared import create_http_app, server_main  # noqa: E402



class GatewayErrorBoundaryTests(unittest.IsolatedAsyncioTestCase):
    def _gateway(self):
        root = Path(self.tempdir.name).resolve()
        owner = SimpleNamespace(selection=SimpleNamespace(root=root, parameters={}))
        gateway = local_gateway(root, native_query=owner)
        gateway.registry = SimpleNamespace(permits=lambda name: name == 'query_check')
        return gateway

    async def test_public_call_boundary_returns_safe_failure(self):
        gateway = self._gateway()
        params = types.CallToolRequestParams(name="query_check", arguments={})
        with (
            patch.object(gateway, "call_tool", new=AsyncMock(side_effect=ValueError("secret=private"))),
            patch("MCP_PATCHBAY_C21.FEATURE_MCP.shared_gateway_support.warning", return_value=None) as reported,
        ):
            response = await gateway.call(None, params)
        self.assertTrue(response.is_error)
        self.assertEqual("failed", response.structured_content["outcome"])
        self.assertNotIn("private", json.dumps(response.structured_content))
        reported.assert_called_once()

    async def test_health_observer_record_failure_warns_without_replacing_result(self):
        gateway = self._gateway()
        response = {"value": {"outcome": "success"}, "text": "success"}
        with patch.object(gateway, "call_tool", new=AsyncMock(return_value=response)), patch.object(
            gateway.health_observations, "record", side_effect=ValueError("private")), patch(
            "MCP_PATCHBAY_C21.FEATURE_MCP.shared_gateway_support.warning", return_value=None) as reported:
            actual = await gateway.call(None, types.CallToolRequestParams(name="query_check", arguments={}))
        self.assertEqual(response["value"], actual.structured_content)
        self.assertEqual(response["text"], actual.content[0].text)
        reported.assert_called_once_with("health_observation_failed")

    async def asyncSetUp(self):
        self.tempdir = __import__("tempfile").TemporaryDirectory()
        self.addAsyncCleanup(self.tempdir.cleanup)


class HTTPBoundaryTests(unittest.IsolatedAsyncioTestCase):
    def _app(self, **properties):
        gateway = SimpleNamespace(build_server=lambda: Server("edge-test"), **properties)
        return create_http_app(Path(self.tempdir.name), runtime_gateway=gateway)

    async def test_host_and_origin_refusals_warn_without_crashing(self):
        client = await self.enterAsyncContext(httpx2.AsyncClient(
            transport=httpx2.ASGITransport(app=self._app()), base_url="http://localhost",
        ))
        with patch("MCP_PATCHBAY_C21.FEATURE_MCP.http_server.warning") as reported:
            host = await client.get("/health", headers={"host": "attacker.invalid"})
            origin = await client.get("/health", headers={"origin": "https://attacker.invalid"})
        self.assertEqual(421, host.status_code)
        self.assertEqual(403, origin.status_code)
        self.assertEqual(2, reported.call_count)

    async def test_health_observer_failure_is_visible_without_changing_readiness(self):
        class BrokenObserver:
            def snapshot(self):
                raise ValueError("secret=must-not-leak")

        client = await self.enterAsyncContext(httpx2.AsyncClient(
            transport=httpx2.ASGITransport(app=self._app(ready=True, health_observations=BrokenObserver())),
            base_url="http://localhost",
        ))
        with patch("MCP_PATCHBAY_C21.FEATURE_MCP.http_server.warning") as reported:
            response = await client.get("/anechoic/health")
        payload = response.json()
        self.assertEqual(200, response.status_code)
        self.assertEqual("ready", payload["state"])
        self.assertEqual("health observations unavailable", payload["health_warning"])
        self.assertNotIn("must-not-leak", response.text)
        reported.assert_called_once()

    async def asyncSetUp(self):
        self.tempdir = __import__("tempfile").TemporaryDirectory()
        self.addAsyncCleanup(self.tempdir.cleanup)


class ProcessBoundaryTests(unittest.TestCase):
    def test_invalid_log_level_refuses_stdio_without_echoing_the_value(self):
        factory = Mock()
        with (patch.dict(os.environ, ANECHOIC_LOG_LEVEL="private-invalid-level"),
              redirect_stderr(io.StringIO()) as stderr):
            self.assertEqual(2, server_main(self.args, gateway_factory=factory))
        factory.assert_not_called()
        self.assertNotIn("private-invalid-level", stderr.getvalue())
        self.assertEqual("invalid_log_level", json.loads(stderr.getvalue())["event"])

    def test_process_boundary_emits_one_sanitized_fallback(self):
        factory = Mock(side_effect=ValueError("token=private"))
        with redirect_stderr(io.StringIO()) as stderr:
            code = server_main(self.args, gateway_factory=factory)
        self.assertEqual(2, code)
        self.assertNotIn("private", stderr.getvalue())
        self.assertEqual(1, stderr.getvalue().count("anechoic: operation failed\n"))
        self.assertIn("mcp_stdio_startup_failed", stderr.getvalue())

    def test_explicit_startup_failure_stays_distinct_and_sanitized(self):
        from MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__shared import ExplicitStartupFailure
        factory = Mock(side_effect=ExplicitStartupFailure("blocked"))
        with redirect_stderr(io.StringIO()) as stderr:
            code = server_main(self.args, gateway_factory=factory)
        self.assertEqual(2, code)
        self.assertIn("mcp_stdio_startup_blocked", stderr.getvalue())
        self.assertIn("anechoic: runtime failure", stderr.getvalue())

    def test_startup_cancellation_is_not_converted(self):
        from concurrent.futures import CancelledError
        with self.assertRaises(CancelledError):
            server_main(self.args, gateway_factory=Mock(side_effect=CancelledError()))

    def test_http_delegation_has_one_process_owner(self):
        gateway = SimpleNamespace(build_server=lambda: Server("edge-test"))
        factory = Mock(return_value=gateway)
        with patch("uvicorn.run") as run, redirect_stderr(io.StringIO()) as stderr:
            result = server_main(self.args + ["--transport", "streamable-http"], gateway_factory=factory)
        self.assertIsNone(result)
        factory.assert_called_once_with(Path(self.tempdir.name), "control")
        run.assert_called_once()
        self.assertEqual(1, stderr.getvalue().count('"event":"mcp_http_startup_started"'))
        self.assertNotIn("mcp_stdio_startup_started", stderr.getvalue())

    def setUp(self):
        self.tempdir = __import__("tempfile").TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        self.args = ["--project-root", self.tempdir.name, "--control-root", "control"]


if __name__ == "__main__":
    unittest.main()
