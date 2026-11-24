"""Focused MCP image/process/gateway failure-boundary checks."""
from .native_query_test_support import local_gateway


from contextlib import redirect_stderr
import io
import json
import os
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock, patch

from mcp import types

MCP = Path(__file__).resolve().parents[1]
TOOLS = MCP.parents[1] / "FEATURE_PROGRAMMATIC" / "FEATURE_TOOLS"

import MCP_PATCHBAY_C21.FEATURE_MCP.http_server as http_server  # noqa: E402
import MCP_PATCHBAY_C21.FEATURE_MCP.server as server  # noqa: E402



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
    async def _guard(self, host, origin=None):
        messages = []

        async def app(_scope, _receive, _send):
            self.fail("refused request reached the MCP app")

        guard = http_server.LoopbackGuard(app)
        guard.gateway = SimpleNamespace(root=Path(self.tempdir.name))
        headers = [(b"host", host.encode())]
        if origin is not None:
            headers.append((b"origin", origin.encode()))
        scope = {"type": "http", "method": "GET", "path": "/health",
                 "headers": headers, "query_string": b"", "http_version": "1.1"}
        async def send(message):
            messages.append(message)

        with patch.object(http_server, "warning") as reported:
            await guard(scope, lambda: None, send)
        return messages, reported

    async def test_host_and_origin_refusals_warn_without_crashing(self):
        host_messages, host_report = await self._guard("attacker.invalid")
        origin_messages, origin_report = await self._guard("127.0.0.1:8092", "https://attacker.invalid")
        self.assertEqual(421, host_messages[0]["status"])
        self.assertEqual(403, origin_messages[0]["status"])
        host_report.assert_called_once()
        origin_report.assert_called_once()

    async def test_health_observer_failure_is_visible_without_changing_readiness(self):
        class BrokenObserver:
            def snapshot(self):
                raise ValueError("secret=must-not-leak")

        gateway = SimpleNamespace(
            root=Path(self.tempdir.name),
            ready=True,
            health_observations=BrokenObserver(),
        )
        with patch.object(http_server, "warning") as reported:
            response = await http_server.health(gateway)
        payload = json.loads(response.body)
        self.assertEqual(200, response.status_code)
        self.assertTrue(payload["ready"])
        self.assertEqual("health observations unavailable", payload["health_warning"])
        self.assertNotIn("must-not-leak", response.body.decode())
        reported.assert_called_once()

    async def asyncSetUp(self):
        self.tempdir = __import__("tempfile").TemporaryDirectory()
        self.addAsyncCleanup(self.tempdir.cleanup)


class ProcessBoundaryTests(unittest.TestCase):
    def test_invalid_log_level_refuses_stdio_without_echoing_the_value(self):
        with (
            patch.dict(os.environ, ANECHOIC_LOG_LEVEL="private-invalid-level"),
            patch.object(server, "_serve_stdio") as serve,
            redirect_stderr(io.StringIO()) as stderr,
        ):
            self.assertEqual(2, server.main(["--project-root", self.tempdir.name]))
        serve.assert_not_called()
        self.assertNotIn("private-invalid-level", stderr.getvalue())
        self.assertEqual("invalid_log_level", json.loads(stderr.getvalue())["event"])

    def test_process_boundary_emits_one_sanitized_fallback(self):
        with (
            patch.object(server, "_serve_stdio", side_effect=ValueError("token=private")),
            redirect_stderr(io.StringIO()) as stderr,
        ):
            code = server.main(["--project-root", self.tempdir.name])
        self.assertEqual(2, code)
        self.assertNotIn("private", stderr.getvalue())
        self.assertEqual(1, stderr.getvalue().count("anechoic: operation failed\n"))
        self.assertIn("mcp_stdio_startup_failed", stderr.getvalue())

    def test_explicit_startup_failure_stays_distinct_and_sanitized(self):
        from MCP_PATCHBAY_C21.FEATURE_MCP.mcp_startup_boundary import ExplicitStartupFailure
        with (
            patch.object(server, "_serve_stdio", side_effect=ExplicitStartupFailure("blocked")),
            redirect_stderr(io.StringIO()) as stderr,
        ):
            code = server.main(["--project-root", self.tempdir.name])
        self.assertEqual(2, code)
        self.assertIn("mcp_stdio_startup_blocked", stderr.getvalue())
        self.assertIn("anechoic: runtime failure", stderr.getvalue())

    def test_startup_cancellation_is_not_converted(self):
        from concurrent.futures import CancelledError
        with patch.object(server, "_serve_stdio", side_effect=CancelledError()):
            with self.assertRaises(CancelledError):
                server.main(["--project-root", self.tempdir.name])

    def test_http_delegation_has_one_process_owner(self):
        with (
            patch.object(server, "run_startup", side_effect=AssertionError("duplicate boundary")),
            patch("MCP_PATCHBAY_C21.FEATURE_MCP.http_server.main", return_value=0) as delegated,
        ):
            result = server.main(["--project-root", self.tempdir.name, "--transport", "streamable-http"])
        self.assertEqual(0, result)
        delegated.assert_called_once_with(["--project-root", self.tempdir.name])

    def setUp(self):
        self.tempdir = __import__("tempfile").TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)


if __name__ == "__main__":
    unittest.main()
