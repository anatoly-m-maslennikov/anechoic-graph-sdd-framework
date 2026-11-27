"""Check default startup and the injected Workbench fixture path."""
from .native_query_test_support import local_gateway


from pathlib import Path
import asyncio
import os
import sys
import tempfile
import unittest
from unittest.mock import patch

from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

MCP = Path(__file__).resolve().parents[1]
from MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__shared import ProjectAdmissionError  # noqa: E402
from types import SimpleNamespace
from MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__shared import create_http_app as create_app  # noqa: E402
from .test_beta_next_query_comparison import project


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
                from IWE_CONSOLE_C43.APP_IWE_CONSOLE.FEATURE_IWE_CONSOLE_BACKEND.registry_lifecycle_provider import LIFECYCLE_TOOL_NAMES

                names = {tool.name for tool in gateway.tools}
                self.assertIn("query_run", names)
                self.assertTrue(LIFECYCLE_TOOL_NAMES <= names)
                await gateway.close()
                self.assertFalse(gateway.ready)

    def test_http_app_requires_native_manifest(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ProjectAdmissionError):
                create_app(Path(directory))

    async def test_stdio_uses_native_gateway(self):
        engine = MCP.parents[1]
        with tempfile.TemporaryDirectory(dir="/tmp") as directory:
            root = Path(directory).resolve() / "project"
            project(root)
            env = {**os.environ, "PYTHONPATH": str(engine),
                   "ANECHOIC_RUNTIME_PROFILE": "dev-local", "PYTHONDONTWRITEBYTECODE": "1",
                   "ANECHOIC_DUCKPGQ_EXTENSION_DIRECTORY": os.environ.get(
                       "ANECHOIC_DUCKPGQ_EXTENSION_DIRECTORY", str(engine.parent / ".anechoic_tmp/workbench/extensions"))}
            env.pop("ANECHOIC_RUNTIME_STACK", None)
            params = StdioServerParameters(command=sys.executable, cwd=engine.parent, env=env,
                args=["-B", "-P", "-m", "MCP_PATCHBAY_C21.FEATURE_MCP.server", "--project-root", str(root)])
            async with asyncio.timeout(120), stdio_client(params) as streams, ClientSession(*streams) as client:
                await client.initialize()
                self.assertIn("query_run", {tool.name for tool in (await client.list_tools()).tools})
                reply = await client.call_tool("query_run", {
                    "sql": 'SELECT reference, "content.summary" FROM atoms ORDER BY reference',
                    "result_delivery": "inline"})
                self.assertFalse(reply.is_error, reply.structured_content)
                self.assertEqual([["EX-S-1", "Declare Example"], ["EX-T-1", "Example task"]],
                                 reply.structured_content["rows"])


if __name__ == "__main__":
    unittest.main()
