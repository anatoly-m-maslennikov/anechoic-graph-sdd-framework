"""Check default startup and the injected Workbench fixture path."""
from .native_query_test_support import local_gateway


from contextlib import nullcontext
from pathlib import Path
import tempfile
import unittest
from unittest.mock import AsyncMock, patch

MCP = Path(__file__).resolve().parents[1]
from MCP_PATCHBAY_C21.FEATURE_MCP.native_startup import ProjectAdmissionError  # noqa: E402
from types import SimpleNamespace
from MCP_PATCHBAY_C21.FEATURE_MCP.http_server import create_app  # noqa: E402
import MCP_PATCHBAY_C21.FEATURE_MCP.server as mcp_server  # noqa: E402


class DefaultMCPRuntimeTests(unittest.IsolatedAsyncioTestCase):
    async def test_injected_gateway_owner_needs_no_child_process(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            owner = SimpleNamespace(selection=SimpleNamespace(root=root, parameters={}),
                                    start=lambda: None, close=lambda: None)
            gateway = local_gateway(root, native_query=owner)
            with patch("asyncio.create_subprocess_exec", side_effect=AssertionError("unexpected child")):
                self.assertFalse(gateway.ready)
                await gateway.initialize()
                self.assertTrue(gateway.ready)
                from IWE_CONSOLE_C43.APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.registry_lifecycle_provider import LIFECYCLE_TOOL_NAMES

                names = {tool.name for tool in gateway.tools}
                self.assertIn("query_run", names)
                self.assertTrue(LIFECYCLE_TOOL_NAMES <= names)
                await gateway.close()
                self.assertFalse(gateway.ready)

    def test_http_app_requires_native_manifest(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ProjectAdmissionError):
                create_app(Path(directory))

    def test_stdio_uses_native_gateway(self):
        gateway = SimpleNamespace(serve=AsyncMock())
        args = SimpleNamespace(project_root=Path("/project"), control_root=None,
                               instance_id=None, host_project_root=None)
        selection = object()
        with (patch.object(mcp_server, "startup_selection", return_value=selection),
              patch.object(mcp_server, "native_runtime_gateway", return_value=nullcontext(gateway)) as factory):
            mcp_server._serve_stdio(args)
        factory.assert_called_once_with(selection)
        gateway.serve.assert_awaited_once()


if __name__ == "__main__":
    unittest.main()
