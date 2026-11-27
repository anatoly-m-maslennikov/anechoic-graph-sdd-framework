
"""Focused checks for the shared host HTTP boundary."""

from __future__ import annotations

import json
from concurrent.futures import CancelledError as FutureCancelledError
import os
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import httpx2
from mcp import types
from mcp.client.session import ClientSession
from mcp.client.streamable_http import streamable_http_client
from mcp.server.lowlevel import Server

MCP_ROOT = Path(__file__).resolve().parents[1]
TOOLS_ROOT = MCP_ROOT.parents[1] / "FEATURE_PROGRAMMATIC" / "FEATURE_TOOLS"

from MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__shared import create_shared_http_app as create_app  # noqa: E402
from MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__shared import HEALTH_PATH, MCP_PATH  # noqa: E402


def _query_tool():
    return types.Tool(name="query_run", inputSchema={
        "type": "object", "properties": {"sql": {"type": "string"}, "project_root": {"type": "string"}},
        "required": ["sql", "project_root"],
    })


class FakeGateway:
    instances: list["FakeGateway"] = []

    def __init__(self, config):
        self.config = config
        self.initialized = False
        self.initialize_calls = 0
        self.close_calls = 0
        self.status_calls = 0
        self.status_error = None
        self.fail_initialize = False
        self.snapshot = {"initialized": False, "advertised_tools": [],
                         "calls": []}
        self.__class__.instances.append(self)

    def build_server(self):
        async def list_tools(_context, _params):
            return types.ListToolsResult(tools=[types.Tool(
                name="echo_project", description="test", inputSchema={
                    "type": "object", "properties": {"project_root": {"type": "string"}},
                    "required": ["project_root"], "additionalProperties": False,
                })])

        async def call_tool(_context, params):
            root = params.arguments.get("project_root")
            value = {"project_root": root, "instance": str(id(self))}
            return types.CallToolResult(
                content=[types.TextContent(type="text", text=json.dumps(value))],
                structuredContent=value,
            )

        return Server("shared-test", on_list_tools=list_tools, on_call_tool=call_tool)

    async def initialize(self):
        self.initialize_calls += 1
        if self.fail_initialize:
            raise RuntimeError("private initialization detail")
        self.initialized = True
        self.snapshot.update(initialized=True, advertised_tools=["echo_project"])

    async def close(self):
        self.close_calls += 1
        self.initialized = False
        self.snapshot.update(initialized=False, advertised_tools=[])

    async def status(self):
        self.status_calls += 1
        if self.status_error is not None:
            raise self.status_error
        return dict(self.snapshot)


class SharedHTTPTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        FakeGateway.instances.clear()
        self.config = SimpleNamespace(http_port=8092)
        self.app = create_app(self.config, gateway_factory=FakeGateway)
        self.gateway = FakeGateway.instances[-1]

    async def test_beta_next_gateway_reuses_socket_and_preserves_selection_and_tool_replies(self):
        messages = []
        root = "/canonical/main"
        project = {"project_name": "Main", "project_prefix": "MA", "instance_id": "a" * 64}
        tool = _query_tool()

        def backend(request):
            key = (request.method, request.url.path)
            data = json.loads(request.content) if request.content else None
            messages.append((key, data))
            if key == ("POST", "/tools") and "project_root" not in data["arguments"]:
                fault = {"scope": "project", "code": "missing_project_root", "message": "missing_project_root"}
                return httpx2.Response(200, json={"error": fault, "project": None})
            result = {
                ("GET", "/health"): {"pid": 101, "initialized": True},
                ("GET", "/tools"): {"tools": [tool.model_dump(mode="json", by_alias=True)]},
                ("POST", "/selection"): project,
                ("POST", "/tools"): {"value": {"rows": [[1]]}, "text": None},
            }[key]
            envelope = {"result": result}
            if key == ("POST", "/tools"):
                envelope["project"] = {"prefix": "MA", "instance_id": project["instance_id"]}
            return httpx2.Response(200, json=envelope)

        gateway = create_app(self.config).gateway
        self.addAsyncCleanup(gateway.close)
        socket = "/private/api.sock"
        with (
            patch("MCP_PATCHBAY_C21.FEATURE_MCP.shared_backend.runtime_stack", return_value="beta_next"),
            patch.dict(os.environ, {"ANECHOIC_BETA_BACKEND_SOCKET": socket}),
            patch.object(httpx2, "AsyncHTTPTransport", return_value=httpx2.MockTransport(backend)) as transport,
        ):
            await gateway.initialize()
            self.assertEqual([tool], gateway.tools)
            self.assertEqual(project, await gateway.select_project(root))
            params = types.CallToolRequestParams(name="query_run", arguments={"sql": "SELECT 1", "project_root": root})
            response = await gateway.call(None, params)
            self.assertEqual({"rows": [[1]]}, response.structured_content)
            refused = await gateway.call(None, types.CallToolRequestParams(name="query_run", arguments={"sql": "SELECT 1"}))
            self.assertTrue(refused.is_error)
            self.assertEqual(["missing_project_root"], refused.structured_content["diagnostics"])
        transport.assert_called_once_with(uds=socket)
        self.assertEqual([(("POST", "/selection"), {"project_root": root}), (("POST", "/tools"), {
            "name": "query_run", "arguments": {"sql": "SELECT 1", "project_root": root}, "session_id": None, "public_base_url": None,
        }), (("POST", "/tools"), {
            "name": "query_run", "arguments": {"sql": "SELECT 1"}, "session_id": None, "public_base_url": None,
        })], messages[-3:])

    async def test_web_and_mcp_refuse_foreign_and_missing_project_receipts(self):
        app = create_app(self.config)
        selected = {"project_name": "Main", "project_prefix": "MA", "instance_id": "a" * 64}
        arguments = {"project_root": "/canonical/main", "sql": "SELECT 1"}
        calls = []

        def backend(request):
            data = json.loads(request.content)
            calls.append(request.url.path)
            if request.url.path == "/selection":
                self.assertEqual(arguments["project_root"], data["project_root"])
                return httpx2.Response(200, json={"result": selected})
            self.assertEqual(arguments["project_root"], data["arguments"]["project_root"])
            self.assertEqual(selected["instance_id"], request.headers["X-Anechoic-Project-Instance"])
            return httpx2.Response(200, json={"project": receipt, "result": {"value": {"rows": [["private"]]}, "text": None}})

        private = httpx2.AsyncClient(transport=httpx2.MockTransport(backend), base_url="http://coordinator")
        app.gateway._http = await self.enterAsyncContext(private)
        url = "http://127.0.0.1:8092"
        public = httpx2.AsyncClient(transport=httpx2.ASGITransport(app=app), base_url=url)
        client = await self.enterAsyncContext(public)
        app.gateway.tools = [_query_tool()]
        app.gateway.ready = True
        async with (app.starlette_app.router.lifespan_context(app.starlette_app),
                    streamable_http_client(url + MCP_PATH, http_client=client) as streams,
                    ClientSession(*streams) as session):
            await session.initialize()
            for receipt in ({"prefix": "MA", "instance_id": "b" * 64}, {"prefix": "MA"}, None):
                with self.subTest(receipt=receipt):
                    calls.clear()
                    web = await client.post("/anechoic/Main/api/run", json=arguments)
                    self.assertEqual(502, web.status_code)
                    failure = web.json()
                    self.assertEqual("project_receipt_mismatch", failure["code"])
                    self.assertEqual("failed", failure["tool_result"]["outcome"])
                    self.assertNotIn("private", web.text)
                    mcp = await session.call_tool("query_run", arguments)
                    self.assertTrue(mcp.is_error)
                    self.assertEqual(failure["tool_result"], mcp.structured_content)
                    self.assertEqual(["/selection", "/tools", "/selection", "/tools"], calls)
            receipt = {"prefix": "MA", "instance_id": selected["instance_id"]}
            web = await client.post("/anechoic/Main/api/run", json=arguments)
            mcp = await session.call_tool("query_run", arguments)
            self.assertEqual(200, web.status_code)
            self.assertFalse(mcp.is_error)
            self.assertEqual({"rows": [["private"]]}, web.json())
            self.assertEqual(web.json(), mcp.structured_content)

    async def test_beta_next_gateway_refuses_unsupervised_start(self):
        gateway = create_app(self.config).gateway
        with (
            patch("MCP_PATCHBAY_C21.FEATURE_MCP.shared_backend.runtime_stack", return_value="beta_next"),
            patch.dict(os.environ, {}, clear=True),
            patch.object(gateway, "_start_backend") as start,
            self.assertRaisesRegex(Exception, "^beta_next_requires_supervised_shared_http$"),
        ):
            await gateway.initialize()
        start.assert_not_called()
    async def request(self, method="GET", path=HEALTH_PATH, **kwargs):
        async with httpx2.AsyncClient(
            transport=httpx2.ASGITransport(app=self.app),
            base_url="http://127.0.0.1:8092",
        ) as client:
            return await client.request(method, path, **kwargs)

    async def test_health_is_preinit_snapshot_and_accept_negotiation_is_explicit(self):
        response = await self.request()
        self.assertEqual(200, response.status_code)
        self.assertEqual({"state": "pending"}, response.json())
        self.assertEqual(0, self.gateway.initialize_calls)
        self.assertGreaterEqual(self.gateway.status_calls, 1)

        response = await self.request(headers={"accept": "text/html;q=1,application/json;q=.5"})
        self.assertEqual(200, response.status_code)
        self.assertTrue(response.headers["content-type"].startswith("text/html"))
        self.assertIn("<dt>Gateway readiness</dt><dd>pending</dd>", response.text)

        response = await self.request(headers={"accept": "text/html;q=0,application/json;q=1"})
        self.assertEqual({"state": "pending"}, response.json())

    async def test_loopback_host_and_origin_guard_are_shared(self):
        self.assertEqual(421, (await self.request(headers={"host": "attacker.invalid"})).status_code)
        self.assertEqual(403, (await self.request(
            headers={"origin": "https://attacker.invalid"})).status_code)
        self.assertEqual(0, self.gateway.initialize_calls)

    async def test_health_snapshot_failure_is_safe_and_reported_unbound(self):
        self.gateway.status_error = RuntimeError("secret status detail")
        with patch("MCP_PATCHBAY_C21.FEATURE_MCP.shared_http_server.warning") as report:
            response = await self.request()
        self.assertEqual(503, response.status_code)
        self.assertEqual({"state": "unavailable"}, response.json())
        report.assert_called_once()
        report.assert_called_once_with("shared_health_snapshot_unavailable")
        self.assertNotIn("secret status detail", response.text)

    async def test_health_snapshot_cancellation_is_not_converted_to_503(self):
        self.gateway.status_error = FutureCancelledError()
        with self.assertRaises(FutureCancelledError):
            await self.request()

    async def test_lifespan_closes_after_partial_initialize_failure(self):
        self.gateway.fail_initialize = True
        with self.assertRaises(BaseException):
            async with self.app.starlette_app.router.lifespan_context(self.app.starlette_app):
                pass
        self.assertEqual(1, self.gateway.close_calls)

    async def test_lifespan_initializes_host_and_routes_two_project_calls(self):
        async with self.app.starlette_app.router.lifespan_context(self.app.starlette_app):
            async with httpx2.AsyncClient(
                transport=httpx2.ASGITransport(app=self.app),
                base_url="http://127.0.0.1:8092",
            ) as client:
                transport = streamable_http_client("http://127.0.0.1:8092" + MCP_PATH, http_client=client)
                streams = await transport.__aenter__()
                session = ClientSession(*streams)
                await session.__aenter__()
                try:
                    await session.initialize()
                    first = await session.call_tool("echo_project", {"project_root": "/repos/alpha"})
                    second = await session.call_tool("echo_project", {"project_root": "/repos/beta"})
                    self.assertEqual("/repos/alpha", first.structured_content["project_root"])
                    self.assertEqual("/repos/beta", second.structured_content["project_root"])
                    health = await client.get(HEALTH_PATH)
                    self.assertEqual({"state": "ready"}, health.json())
                finally:
                    await session.__aexit__(None, None, None)
                    await transport.__aexit__(None, None, None)
        self.assertEqual(1, self.gateway.initialize_calls)
        self.assertEqual(1, self.gateway.close_calls)

if __name__ == "__main__":
    unittest.main()
