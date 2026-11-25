"""HTTP MCP compose/lifecycle boundary tests; no Docker daemon is invoked."""
import os
from pathlib import Path
from types import SimpleNamespace
import re
import tempfile
import unittest
from unittest.mock import patch

from MCP_PATCHBAY_C21.FEATURE_MCP.backend_client import BackendClient

APP = Path(__file__).resolve().parents[1]
from MCP_PATCHBAY_C21.FEATURE_MCP.docker.runtime import Runtime  # noqa: E402
from MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__shared import HEALTH_PATH, MCP_PATH  # noqa: E402

IMAGE = "sha256:" + "a" * 64


class BackendStartupBudgetTests(unittest.TestCase):
    def test_dev_local_startup_budget_is_bounded_and_private_to_managed_processes(self):
        cases = (
            ("dev-local", True, 180, True),
            ("dev-local", True, 420, False),
            ("dev-local", False, 180, False),
            ("dev-preprod", True, 180, False),
            ("prod", True, 180, False),
        )
        for profile, managed, elapsed, ready in cases:
            with self.subTest(profile=profile, managed=managed, elapsed=elapsed):
                process = SimpleNamespace(pid=42, poll=lambda: None) if managed else None
                client = BackendClient(None, process, None)
                with (patch.dict(os.environ, {"ANECHOIC_RUNTIME_PROFILE": profile}, clear=True),
                      patch("MCP_PATCHBAY_C21.FEATURE_MCP.backend_client.monotonic",
                            side_effect=[0, elapsed]),
                      patch.object(client, "_probe_ready", return_value=True) as probe):
                    if ready:
                        client.start()
                        probe.assert_called_once_with()
                    else:
                        with self.assertRaisesRegex(RuntimeError, "Backend did not start"):
                            client.start()
                        probe.assert_not_called()


class MCPHTTPRuntimeTests(unittest.TestCase):
    def setUp(self):
        self.temporary = APP.parents[2] / ".anechoic_tmp/tests/mcp-http-runtime"
        self.temporary.mkdir(parents=True, exist_ok=True)

    def root(self):
        directory = tempfile.TemporaryDirectory(dir=self.temporary, ignore_cleanup_errors=True)
        self.addCleanup(directory.cleanup)
        root = Path(directory.name)
        (root / ".anechoic_anechoic").mkdir()
        (root / ".git").mkdir()
        return root

    @staticmethod
    def _published_status(port=8099, *, state="running", health="healthy", publishers=None):
        if publishers is None:
            publishers = [{
                "Protocol": "tcp", "TargetPort": 8092,
                "PublishedPort": port, "URL": "127.0.0.1",
            }]
        return {"services": [{
            "Service": "mcp-http", "State": state, "Health": health,
            "Publishers": publishers,
        }]}

    def test_explicit_port_is_required_without_a_token_or_agent_auth(self):
        runtime = Runtime(self.root(), image=IMAGE)
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(ValueError, "ANECHOIC_MCP_HTTP_PORT"):
                runtime.mcp_http_start()
        with patch.dict(os.environ, {"ANECHOIC_MCP_HTTP_PORT": "8099"}, clear=True):
            with patch.object(runtime, "call", return_value="") as call, \
                    patch.object(runtime, "mcp_http_status", return_value=self._published_status()):
                result = runtime.mcp_http_start()
        self.assertEqual(f"http://127.0.0.1:8099{MCP_PATH}", result["url"])
        self.assertIn("mcp-http", call.call_args.args)
        self.assertTrue(call.call_args.kwargs["http"])

    def test_startup_deadlines_cover_generation_readiness_budget(self):
        runtime = Runtime(self.root(), image=IMAGE)
        with patch.dict(os.environ, {"ANECHOIC_MCP_HTTP_PORT": "8099"}, clear=True), \
                patch.object(runtime, "call", return_value="") as call, \
                patch.object(runtime, "mcp_http_status", return_value=self._published_status()):
            runtime.mcp_http_start()

        args = call.call_args.args
        compose_wait = int(args[args.index("--wait-timeout") + 1])
        outer_timeout = call.call_args.kwargs["timeout"]
        health_start_period = int(re.search(
            r"start_period:\s*(\d+)s", (APP / "docker/mcp-http.compose.yaml").read_text()
        ).group(1))
        self.assertEqual(compose_wait, 420)
        self.assertGreater(outer_timeout, compose_wait)
        self.assertEqual(health_start_period, 420)

    def test_start_requires_exact_loopback_publisher_admission(self):
        cases = {
            "missing": self._published_status(publishers=[]),
            "wrong-port": self._published_status(port=8100),
            "wildcard": self._published_status(publishers=[{
                "Protocol": "tcp", "TargetPort": 8092,
                "PublishedPort": 8099, "URL": "0.0.0.0",
            }]),
            "nonhealthy": self._published_status(health="starting"),
            "multiple-publishers": self._published_status(publishers=[
                {"Protocol": "tcp", "TargetPort": 8092, "PublishedPort": 8099, "URL": "127.0.0.1"},
                {"Protocol": "tcp", "TargetPort": 8092, "PublishedPort": 8100, "URL": "127.0.0.1"},
            ]),
            "multiple-services": {"services": self._published_status()["services"] * 2},
        }
        for name, status in cases.items():
            with self.subTest(name=name), \
                    patch.dict(os.environ, {"ANECHOIC_MCP_HTTP_PORT": "8099"}, clear=True):
                runtime = Runtime(self.root(), image=IMAGE)
                with patch.object(runtime, "call", return_value=""), \
                        patch.object(runtime, "mcp_http_status", return_value=status):
                    with self.assertRaisesRegex(RuntimeError, "HTTP MCP published listener admission failed"):
                        runtime.mcp_http_start()

    def test_overlay_is_loopback_only_and_has_no_agent_or_socket(self):
        text = (APP / "docker/mcp-http.compose.yaml").read_text()
        self.assertIn("127.0.0.1:${ANECHOIC_MCP_HTTP_PORT", text)
        self.assertNotIn("ANECHOIC_MCP_HTTP_SECRET_TOKEN", text)
        self.assertNotIn("/var/run/docker.sock", text)
        self.assertNotIn("agent_auth", text)
        self.assertIn("no-new-privileges:true", text)
        self.assertIn(f"http://127.0.0.1:8092{HEALTH_PATH}", text)


if __name__ == "__main__":
    unittest.main()
