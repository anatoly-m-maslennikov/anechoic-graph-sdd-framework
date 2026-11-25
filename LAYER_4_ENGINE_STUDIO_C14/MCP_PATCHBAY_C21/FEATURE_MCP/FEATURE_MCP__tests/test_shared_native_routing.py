"""Functional shared-host proof with per-Project Backend processes."""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from types import SimpleNamespace
from pathlib import Path
import os
import tempfile
import unittest
from unittest.mock import patch

import httpx2
from mcp.client.session import ClientSession
from mcp.client.streamable_http import streamable_http_client

APP = Path(__file__).resolve().parents[1]
ROOT = APP.parents[2]
TOOLS = APP.parents[1] / "FEATURE_PROGRAMMATIC" / "FEATURE_TOOLS"

from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared import extension_directory  # noqa: E402
from MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__shared import MCP_PATH  # noqa: E402
from MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__shared import create_shared_http_app as create_app  # noqa: E402
from . import test_native_startup as fixtures  # noqa: E402


class SharedNativeRoutingTests(unittest.IsolatedAsyncioTestCase):
    """Exercise isolated native Workbench owners through one HTTP facade."""

    def setUp(self) -> None:
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
            "max_loaded_projects=2\n"
            "[project_defaults]\nworkbench_storage=\"memory\"\njournal_storage=\"files\"\n",
            encoding="utf-8",
        )

    def _project(self, name: str) -> Path:
        root = self.projects / name
        control = root / f".anechoic_{name}"
        parameters = {"runtime": {"workbench": {"storage": "disk"}}} if name == "beta" else None
        fixtures.RuntimeSelectionTests.manifest(self, control, name=name, prefix=name.upper(),
                                                component="C00", parameters=parameters)
        return root.resolve()

    @asynccontextmanager
    async def _session(self):
        environment = {"ANECHOIC_DUCKPGQ_EXTENSION_DIRECTORY": str(extension_directory(ROOT)),
                       "ANECHOIC_RUNTIME_NAMESPACE": "docker"}
        self.enterContext(patch.dict(os.environ, environment))
        app = create_app(self.config_path)
        self.app = app
        async with app.starlette_app.router.lifespan_context(app.starlette_app):
            async with httpx2.AsyncClient(
                transport=httpx2.ASGITransport(app=app),
                base_url="http://127.0.0.1:18092",
            ) as client:
                self.client = client
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
            coordinator, owners = await self._assert_distinct_backends()
            self.assertFalse((self.projects_by_name["alpha"] / ".anechoic_runtime/db/project.duckdb").exists())
            self.assertTrue((self.projects_by_name["beta"] / ".anechoic_runtime/db/project.duckdb").is_file())
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
        for pid in [coordinator, *owners.values()]:
            await self._assert_exited(pid)

    async def _backend_children(self, coordinator):
        status = await self.app.gateway.status()
        self.assertEqual(coordinator, status["pid"])
        by_instance = {item["instance_id"]: item["pid"]
                       for item in status["loaded_project_processes"]}
        children = {}
        for root in self._expected_roots:
            selection = await self.app.gateway.select_project(str(root))
            pid = by_instance.get(selection["instance_id"])
            if pid is not None:
                children[str(root)] = pid
        return children

    async def _assert_distinct_backends(self):
        coordinator = (await self.app.gateway.status())["pid"]
        self.assertNotEqual(os.getpid(), coordinator)
        self._expected_roots = tuple(self.projects_by_name.values())
        children = await self._backend_children(coordinator)
        self.assertEqual({str(root) for root in self._expected_roots}, set(children))
        self.assertEqual(2, len(set(children.values())))
        return coordinator, children

    async def _assert_exited(self, pid):
        for _ in range(100):
            try:
                os.kill(pid, 0)
            except ProcessLookupError:
                return
            await asyncio.sleep(0.05)
        self.fail(f"process {pid} did not exit")

    async def test_idle_eviction_closes_only_the_evicted_backend(self):
        self.config_path.write_text(
            self.config_path.read_text(encoding="utf-8").replace(
                "max_loaded_projects=2", "max_loaded_projects=1"), encoding="utf-8")
        async with self._session() as session:
            alpha, beta = (self.projects_by_name[name] for name in ("alpha", "beta"))
            first = await session.call_tool("query_schema", {"project_root": str(alpha)})
            self.assertFalse(first.is_error, first.structured_content)
            coordinator = (await self.app.gateway.status())["pid"]
            self._expected_roots = (alpha, beta)
            old = (await self._backend_children(coordinator))[str(alpha)]
            second = await session.call_tool("query_schema", {"project_root": str(beta)})
            self.assertFalse(second.is_error, second.structured_content)
            await self._assert_exited(old)
            children = await self._backend_children(coordinator)
            self.assertEqual({str(beta)}, set(children))
            current = children[str(beta)]
            self.assertNotEqual(old, current)
        await self._assert_exited(current)
        await self._assert_exited(coordinator)

    async def test_cached_backend_refuses_lifecycle_after_manifest_drift(self):
        root = self.projects_by_name["alpha"]
        async with self._session() as session:
            ready = await session.call_tool("query_schema", {"project_root": str(root)})
            self.assertFalse(ready.is_error, ready.structured_content)
            coordinator = (await self.app.gateway.status())["pid"]
            self._expected_roots = (root,)
            owner = (await self._backend_children(coordinator))[str(root)]
            manifest = root / ".anechoic_alpha/ALPHA-S-001-PROJECT_MANIFEST--declare.md"
            manifest.write_text(manifest.read_text(encoding="utf-8") + "\n", encoding="utf-8")
            before = {path: path.read_bytes() for path in manifest.parent.rglob("*") if path.is_file()}
            reply = await session.call_tool("atom_lifecycle_create_draft", {
                "project_root": str(root), "newAtom": {
                    "template": "task", "label": "Task", "container": {"component": "C00"},
                    "body": "## Summary\n\nMust not be written.\n",
                },
            })
            self.assertEqual("project_manifest_reload_required", reply.structured_content["errors"][0]["code"])
            self.assertEqual(before, {path: path.read_bytes() for path in manifest.parent.rglob("*") if path.is_file()})
            self.assertEqual(owner, (await self._backend_children(coordinator))[str(root)])

    async def test_single_project_mcp_and_workbench_schema(self):
        root = self.projects_by_name["alpha"]
        self.config_path.write_text(
            f'schema_version=1\n[shared_mcp]\nproject_root={str(root)!r}\nhttp_port=18092\n'
            '[project_defaults]\nworkbench_storage="memory"\njournal_storage="files"\n'
        )
        async with self._session() as session:
            tools = {tool.name for tool in (await session.list_tools()).tools}
            self.assertIn("query_schema", tools)
            response = await session.call_tool("query_schema", {"project_root": str(root)})
            self.assertFalse(response.is_error, response.structured_content)
            self.assertFalse((root / ".anechoic_runtime/db/project.duckdb").exists())
            web = await self.client.post(
                "/anechoic/alpha/api/schema", json={"project_root": str(root)}
            )
            self.assertEqual(200, web.status_code, web.text)
            wrong = await self.client.post(
                "/anechoic/beta/api/schema", json={"project_root": str(root)}
            )
            self.assertEqual(404, wrong.status_code)
            outside = await session.call_tool(
                "query_schema", {"project_root": str(self.projects_by_name["beta"])}
            )
            self.assertTrue(outside.is_error)
            self.assertEqual(["outside_project_root"], outside.structured_content["diagnostics"])

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
