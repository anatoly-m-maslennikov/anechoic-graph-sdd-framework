"""Exercise the Backend Tool catalog and dispatch over its private socket."""
import asyncio
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from mcp import types
from mcp.client._memory import InMemoryTransport
from mcp.client.session import ClientSession

from . import test_api_backend_process as fixture
from MCP_PATCHBAY_C21.FEATURE_MCP.direct_gateway import native_runtime_gateway
from MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__shared import select_runtime_project
from IWE_CONSOLE_C43.APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.FEATURE_WORKBENCH_BACKEND__shared import NATIVE_TOOLS


class BackendToolApiTests(unittest.IsolatedAsyncioTestCase):
    async def test_blacklist_hides_query_run_and_dependent_template_over_mcp(self):
        with (tempfile.TemporaryDirectory() as temporary,
              patch.dict(os.environ, fixture._test_environment())):
            root = Path(temporary).resolve()
            fixture._project(root)
            manifest = root / "AN-S-3037-SPEC-PROJECT_MANIFEST--declare-anechoic.md"
            original = manifest.read_text(encoding="utf-8")
            marker = "'tool_blacklist': ['release_version', 'public.release']"
            self.assertIn(marker, original)
            manifest.write_text(original.replace(marker, "'tool_blacklist': ['query_run']"), encoding="utf-8")
            selection = select_runtime_project(root, fixture.CONTROL)
            with native_runtime_gateway(selection) as gateway:
                try:
                    await gateway.initialize()
                    self.assertNotEqual(os.getpid(), gateway._native_query.backend_pid)
                    self.assertNotIn(fixture._kernel_pid(gateway._native_query),
                                     {os.getpid(), gateway._native_query.backend_pid})
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

    async def _post(self, owner, name, arguments, **changes):
        request = {"name": name, "arguments": arguments, "instance_id": owner.selection.instance_id,
                   "session_id": None, "public_base_url": None, "asserted_project_root": None}
        return (await asyncio.to_thread(owner._http.post, "/tools", json=request | changes)).json()

    async def _assert_catalog(self, owner, selection):
        response = await asyncio.to_thread(owner._http.get, "/tools", params={"instance_id": selection.instance_id})
        catalog = response.json()["result"]
        registry = fixture.ROOT / "LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_WORKBENCH/FEATURE_WORKBENCH_BACKEND/tool_registry.json"
        baseline = json.loads(registry.read_text(encoding="utf-8"))
        excluded = set(baseline["mcp_blacklist"]) | set(selection.tool_blacklist)
        expected = [types.Tool.model_validate(tool).model_dump(by_alias=True, mode="json")
                    for provider in baseline["providers"] for tool in provider["tools"]
                    if tool["name"] not in excluded]
        self.assertEqual(sorted(excluded), catalog["blacklist"])
        self.assertEqual(expected, catalog["tools"])
        invalid = await asyncio.to_thread(owner._http.get, "/tools", params={"instance_id": "wrong"})
        self.assertEqual("value_error", invalid.json()["error"]["code"])

    async def _assert_dispatch(self, owner, root):
        result = await self._post(owner, "query_run", {"sql": "SELECT 42 AS answer", "result_delivery": "inline"})
        self.assertEqual([[42]], result["result"]["value"]["rows"])
        self.assertIsNone(result["result"]["text"])
        for name, args, changes, code in (
            ("query_run", {"sql": 42}, {}, "tool_input_invalid"),
            ("unknown_tool", {}, {}, "tool_unavailable"),
            ("query_check", {"sql": "SELECT 1"}, {}, "tool_unavailable"),
            ("query_run", {"sql": "SELECT 1"}, {"instance_id": "wrong"}, "value_error"),
            ("query_run", {"sql": "SELECT 1"}, {"asserted_project_root": str(root / "wrong")}, "value_error"),
        ):
            with self.subTest(name=name, changes=changes):
                reply = await self._post(owner, name, args, **changes)
                self.assertEqual(code, reply["error"]["code"], reply)
                wire = reply["error"]["tool_result"]
                self.assertEqual("failed" if code == "value_error" else "rejected", wire["outcome"])
                self.assertTrue(wire["diagnostics"])

    async def _assert_worker_runs(self, owner, selection):
        path = "/jobs/worker-runs"
        response = await asyncio.to_thread(owner._http.get, path, params={"instance_id": selection.instance_id})
        records = response.json()["result"]
        self.assertEqual([], records["active"])
        startup = next(run for run in records["latest"] if run["kind"] == "model_build")
        self.assertEqual(("completed", 0), (startup["status"], startup["returncode"]))
        self.assertGreater(startup["pid"], 0)
        self.assertNotIn(startup["pid"], {owner.backend_pid, fixture._kernel_pid(owner)})
        invalid = await asyncio.to_thread(owner._http.get, path, params={"instance_id": "wrong"})
        self.assertEqual("value_error", invalid.json()["error"]["code"])

    async def test_catalog_and_dispatch_over_backend_process(self):
        with (tempfile.TemporaryDirectory() as temporary,
              patch.dict(os.environ, fixture._test_environment())):
            root = Path(temporary).resolve()
            fixture._project(root)
            manifest = root / "AN-S-3037-SPEC-PROJECT_MANIFEST--declare-anechoic.md"
            original = manifest.read_text(encoding="utf-8")
            marker = "'tool_blacklist': ['release_version', 'public.release']"
            self.assertIn(marker, original)
            manifest.write_text(original.replace(marker, "'tool_blacklist': ['query_check']"), encoding="utf-8")
            selection = select_runtime_project(root, fixture.CONTROL)
            self.assertIn("query_check", selection.tool_blacklist)
            with native_runtime_gateway(selection) as gateway:
                try:
                    await gateway.initialize()
                    owner = gateway._native_query
                    self.assertNotEqual(os.getpid(), owner.backend_pid)
                    await self._assert_catalog(owner, selection)
                    await self._assert_worker_runs(owner, selection)
                    await self._assert_dispatch(owner, root)
                finally:
                    await gateway.close()
