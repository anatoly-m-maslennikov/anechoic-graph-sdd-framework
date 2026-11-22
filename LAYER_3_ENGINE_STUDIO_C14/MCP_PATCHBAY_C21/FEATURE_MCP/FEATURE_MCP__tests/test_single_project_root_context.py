
"""Real MCP proof for the optional single-Project root envelope."""

from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import httpx2
from mcp.client.session import ClientSession
from mcp.client.streamable_http import streamable_http_client


REPOSITORY = Path(__file__).resolve().parents[4]
PROGRAMMATIC = REPOSITORY / "LAYER_3_ENGINE_STUDIO_C14" / "FEATURE_PROGRAMMATIC"
MCP = REPOSITORY / "LAYER_3_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP"
TOOLS = PROGRAMMATIC / "FEATURE_TOOLS"
APP = REPOSITORY / "LAYER_3_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_WORKBENCH"

from MCP_PATCHBAY_C21.FEATURE_MCP.http_paths import MCP_PATH  # noqa: E402
from MCP_PATCHBAY_C21.FEATURE_MCP.http_server import create_app  # noqa: E402
from MCP_PATCHBAY_C21.FEATURE_MCP.direct_gateway import startup_selection  # noqa: E402
from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.FEATURE_PROJECT_TOOLS__tests.smalltest_support__pub import extension_directory, polling_source_watcher  # noqa: E402


from .test_native_startup import RuntimeSelectionTests, native_fixture_gateway  # noqa: E402


class SingleProjectRootContextTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.enterContext(polling_source_watcher())
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        base = Path(self.temporary.name).resolve()
        self.host = self._project(base / "host")
        self.container = self._project(base / "container")
        self.foreign = self._project(base / "foreign")
        self.alias = base / "container-alias"
        self.alias.symlink_to(self.container, target_is_directory=True)
        selection = startup_selection(
            self.container,
            instance_id=startup_selection(self.host).instance_id,
            host_root=self.host,
        )
        gateway = native_fixture_gateway(self.container, extension_directory(REPOSITORY), selection=selection)
        self.app = create_app(self.container, runtime_gateway=gateway)

    @staticmethod
    def _project(root: Path) -> Path:
        RuntimeSelectionTests.manifest(None, root / ".anechoic_fixture", name="fixture", component="C00")
        return root

    @asynccontextmanager
    async def session(self):
        async with self.app.starlette_app.router.lifespan_context(self.app.starlette_app):
            async with httpx2.AsyncClient(
                transport=httpx2.ASGITransport(app=self.app),
                base_url="http://127.0.0.1:18093",
            ) as client:
                transport = streamable_http_client(
                    "http://127.0.0.1:18093" + MCP_PATH, http_client=client,
                )
                streams = await transport.__aenter__()
                session = ClientSession(*streams)
                await session.__aenter__()
                try:
                    await session.initialize()
                    yield session
                finally:
                    await session.__aexit__(None, None, None)
                    await transport.__aexit__(None, None, None)

    async def test_single_project_envelope_is_advertised_validated_and_not_forwarded(self) -> None:
        async with self.session() as session:
            listed = {tool.name: tool for tool in (await session.list_tools()).tools}
            self.assertIn("query_schema", listed)
            for name, tool in listed.items():
                with self.subTest(name=name):
                    schema = tool.input_schema
                    self.assertEqual("string", schema["properties"]["project_root"]["type"])
                    self.assertNotIn("project_root", schema.get("required", []))

            native = {tool.name: tool for tool in self.app.gateway.tools}
            self.assertNotIn("project_root", native["query_schema"].input_schema["properties"])

            for root in (None, str(self.container), str(self.host)):
                arguments = {} if root is None else {"project_root": root}
                response = await session.call_tool("query_schema", arguments)
                self.assertFalse(response.is_error, response.structured_content)
                self.assertIn("atoms", response.structured_content["tables"])

            checked = await session.call_tool("query_check", {
                "sql": "SELECT 1", "project_root": str(self.host),
            })
            self.assertFalse(checked.is_error, checked.structured_content)
            self.assertTrue(checked.structured_content["valid"])

            workspace = await session.call_tool("workspace_open", {
                "session_id": "root-envelope", "project_root": str(self.host),
            })
            self.assertFalse(workspace.is_error, workspace.structured_content)
            self.assertEqual("root-envelope", workspace.structured_content["workspace_id"])

            backend_call = self.app.gateway.workbench.call
            with patch.object(self.app.gateway.workbench, "call", wraps=backend_call) as backend:
                for root in (str(self.foreign), ".", "../container", str(self.alias), "\0", 1):
                    with self.subTest(root=repr(root)):
                        response = await session.call_tool("query_schema", {"project_root": root})
                        self.assertTrue(response.is_error)
                backend.assert_not_awaited()


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
