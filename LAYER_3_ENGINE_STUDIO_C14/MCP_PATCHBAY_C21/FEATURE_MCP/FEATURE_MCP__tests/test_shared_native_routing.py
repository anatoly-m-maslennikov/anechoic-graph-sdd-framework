"""Functional shared-host proof with real in-process Workbench gateways."""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from dataclasses import replace
from types import SimpleNamespace
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import httpx2
from mcp.client.session import ClientSession
from mcp.client.streamable_http import streamable_http_client
from watchdog.observers.polling import PollingObserver

APP = Path(__file__).resolve().parents[1]
ROOT = APP.parents[2]
TOOLS = APP.parents[1] / "FEATURE_PROGRAMMATIC" / "FEATURE_TOOLS"
sys.path[:0] = [str(APP), str(TOOLS), str(TOOLS / "VALIDATE_ATOMS")]

from host_runtime_config import load_host_runtime_config  # noqa: E402
from APP_WORKBENCH.APP_WORKBENCH__tests.smalltest_support import extension_directory  # noqa: E402
from http_paths import MCP_PATH  # noqa: E402
from shared_http_server import create_app  # noqa: E402
from native_startup import load_native_inputs  # noqa: E402
import test_native_startup as fixtures  # noqa: E402


class SharedNativeRoutingTests(unittest.IsolatedAsyncioTestCase):
    """Exercise isolated native Workbench owners through one HTTP facade."""

    def setUp(self) -> None:
        observer = patch("APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.source_watcher.NativeObserver", PollingObserver)
        observer.start()
        self.addCleanup(observer.stop)
        test_dir = ROOT / ".anechoic_tmp/tests/shared-native-routing"
        test_dir.mkdir(parents=True, exist_ok=True)
        self.temporary = tempfile.TemporaryDirectory(dir=test_dir)
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.projects = self.root / "My_Repos"
        self.projects.mkdir()
        self.projects_by_name = {name: self._project(name) for name in ("alpha", "beta")}
        self.legacy = self.projects / "legacy"
        self.legacy.mkdir()
        fixtures.RuntimeSelectionTests.legacy(SimpleNamespace(root=self.legacy))
        self.config_path = self.root / "host_runtime.toml"
        self.config_path.write_text(
            "schema_version=1\n"
            "[shared_mcp]\n"
            f"projects_root={str(self.projects)!r}\n"
            "http_port=18092\n"
            "max_loaded_projects=2\n",
            encoding="utf-8",
        )
        self.config = load_host_runtime_config(self.config_path)

    def _project(self, name: str) -> Path:
        root = self.projects / name
        control = root / f".anechoic_{name}"
        fixtures.RuntimeSelectionTests.manifest(self, control, name=name, prefix=name.upper(), component="C00")
        return root.resolve()

    @asynccontextmanager
    async def _session(self):
        cache = extension_directory(ROOT)
        def inputs(selection):
            return replace(load_native_inputs(selection), extension_directory=cache)

        app = create_app(self.config)
        self.enterContext(patch("native_startup.load_native_inputs", side_effect=inputs))
        async with app.starlette_app.router.lifespan_context(app.starlette_app):
            async with httpx2.AsyncClient(
                transport=httpx2.ASGITransport(app=app),
                base_url="http://127.0.0.1:18092",
            ) as client:
                transport = streamable_http_client(
                    "http://127.0.0.1:18092" + MCP_PATH,
                    http_client=client,
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

    async def test_frontdoor_routes_same_workspace_id_to_isolated_native_owners(self):
        async with self._session() as session:
            tools = {tool.name: tool for tool in (await session.list_tools()).tools}
            self.assertIn("project_root", tools["query_schema"].input_schema["required"])
            self.assertIn("atom_lifecycle_update", tools)
            self.assertNotIn("workbench_archive_load", tools)
            retired = await session.call_tool("query_schema", {"project_root": str(self.legacy)})
            self.assertTrue(retired.is_error)
            self.assertEqual(["invalid_project_root"], retired.structured_content["diagnostics"])
            schemas = await asyncio.gather(*(
                session.call_tool("query_schema", {"project_root": str(root)})
                for root in self.projects_by_name.values()
            ))
            self.assertTrue(all(not response.is_error for response in schemas), schemas)
            responses = await asyncio.gather(*(
                session.call_tool("workspace_open", {
                    "session_id": "same-id", "project_root": str(self.projects_by_name[name]),
                }) for name in ("alpha", "beta")
            ))
            self.assertTrue(all(not response.is_error for response in responses), responses)
            self.assertEqual(["alpha", "beta"], [r.structured_content["project_name"] for r in responses])
            for root in self.projects_by_name.values():
                self.assertEqual(1, len(list((root / ".anechoic_runtime/workbench/workspaces").glob("*.json"))))
            created = await session.call_tool("view_create", {
                "project_root": str(self.projects_by_name["alpha"]), "workspace_id": "same-id",
            })
            self.assertFalse(created.is_error, created.structured_content)
            states = await asyncio.gather(*(
                session.call_tool("workspace_get", {
                    "workspace_id": "same-id", "project_root": str(self.projects_by_name[name]),
                }) for name in ("alpha", "beta")
            ))
            self.assertEqual([2, 1], [len(r.structured_content["views"]) for r in states])

    async def test_frontdoor_refuses_missing_and_outside_project_root(self):
        async with self._session() as session:
            common = {}
            missing = await session.call_tool("query_schema", common)
            outside = await session.call_tool(
                "query_schema",
                {**common, "project_root": str(self.root)},
            )
            self.assertTrue(missing.is_error)
            self.assertTrue(outside.is_error)
            self.assertIn("project_root", str(missing.structured_content).lower())
            self.assertIn("outside", str(outside.structured_content).lower())


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
