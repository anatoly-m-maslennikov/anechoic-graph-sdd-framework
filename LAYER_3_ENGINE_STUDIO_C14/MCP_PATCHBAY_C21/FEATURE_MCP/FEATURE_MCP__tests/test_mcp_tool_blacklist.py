"""Native Project exclusions apply to discovery and calls."""

from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest

from mcp.client._memory import InMemoryTransport
from mcp.client.session import ClientSession

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from direct_gateway import DirectGateway  # noqa: E402
from workbench_tools import NATIVE_TOOLS  # noqa: E402


class MCPToolBlacklistTests(unittest.IsolatedAsyncioTestCase):
    async def test_gateway_lists_and_refuses_excluded_workbench_names(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            owner = SimpleNamespace(
                selection=SimpleNamespace(root=root, parameters={"project_mcp": {"tool_blacklist": ["query_run"]}}),
                start=lambda: None, close=lambda: None,
            )
            gateway = DirectGateway(root, native_query=owner)
            await gateway.initialize()
            try:
                async with InMemoryTransport(gateway.build_server(), raise_exceptions=True) as streams:
                    async with ClientSession(*streams) as client:
                        await client.initialize()
                        names = {tool.name for tool in (await client.list_tools()).tools}
                        self.assertEqual(set(NATIVE_TOOLS) - {"query_run"}, names & set(NATIVE_TOOLS))
                        self.assertNotIn("query_template", names)
                        for name in ("query_run", "query_template"):
                            response = await client.call_tool(name, {})
                            self.assertTrue(response.is_error)
                            self.assertEqual(["Unknown Tool"], response.structured_content["diagnostics"])
            finally:
                await gateway.close()


if __name__ == "__main__":
    unittest.main()
