"""Tool REST ingress checks without starting a server or Project owner."""

import asyncio
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import httpx2

from MCP_PATCHBAY_C21.FEATURE_MCP.backend_client import BackendClient
from MCP_PATCHBAY_C21.FEATURE_MCP.direct_gateway import DirectGateway
from MCP_PATCHBAY_C21.FEATURE_MCP.http_server import create_app as direct_app
from MCP_PATCHBAY_C21.FEATURE_MCP.shared_http_server import (
    create_app as shared_app,
)


ORIGIN = "http://localhost:8092"
ROOT = "/canonical/project"
INSTANCE = "a" * 64
BINDING = {"X-Anechoic-Project-Instance": INSTANCE}
PROJECT = {"prefix": "AN", "instance_id": INSTANCE}
TOOL = {
    "name": "custom_tool",
    "description": "Test Tool from the Backend catalog",
    "inputSchema": {"type": "object", "properties": {}},
}
RESULT = {"value": {"outcome": "completed", "made": [1]}, "text": "rendered"}
FAULT = {
    "code": "workbench_unavailable",
    "message": "The Project Workbench is unavailable",
    "tool_result": {"outcome": "failed", "diagnostics": ["unavailable"]},
}


def invocation(**changes):
    return {
        "name": TOOL["name"],
        "arguments": {"project_root": ROOT},
        "session_id": "test-session",
        "public_base_url": "https://untrusted.example/",
        **changes,
    }


class ToolRestTests(unittest.IsolatedAsyncioTestCase):
    async def public(self, app):
        return await self.enterAsyncContext(httpx2.AsyncClient(
            transport=httpx2.ASGITransport(app=app), base_url=ORIGIN
        ))

    async def shared(self, handler):
        with TemporaryDirectory() as directory:
            frontend = Path(directory)
            (frontend / "index.html").write_text(
                "<!doctype html><html><head></head><body></body></html>",
                encoding="utf-8",
            )
            with patch("MCP_PATCHBAY_C21.FEATURE_MCP.workbench_web._FRONTEND", frontend):
                app = shared_app(None)
            app.gateway._http = await self.enterAsyncContext(httpx2.AsyncClient(
                transport=httpx2.MockTransport(handler), base_url="http://backend"
            ))
            yield await self.public(app)

    async def test_shared_catalog_and_invocation_keep_backend_contract(self):
        sent = []
        reply = {"result": RESULT, "project": PROJECT}
        status = 200

        def backend(request):
            sent.append(request)
            if request.url.path == "/selection":
                return httpx2.Response(200, json={"result": {
                    "project_name": "Project", "instance_id": INSTANCE,
                }})
            if request.method == "GET":
                return httpx2.Response(200, json={"result": {"tools": [TOOL]}})
            return httpx2.Response(status, json=reply)

        async for client in self.shared(backend):
            page = await client.get("/anechoic/iwe-console/Project", params={"project_root": ROOT})
            self.assertEqual(200, page.status_code)
            self.assertIn(f'<meta name="anechoic-project-instance" content="{INSTANCE}">', page.text)
            self.assertEqual("no-store", page.headers["cache-control"])
            self.assertEqual(404, (await client.post("/selection", json={})).status_code)
            catalog = await client.get("/tools")
            self.assertEqual({"result": {"tools": [TOOL]}}, catalog.json())
            response = await client.post("/tools", json=invocation(), headers=BINDING | {"Origin": ORIGIN})
            self.assertEqual((200, reply), (response.status_code, response.json()))
            self.assertEqual(["/selection", "/tools", "/tools"], [request.url.path for request in sent])
            self.assertEqual(INSTANCE, sent[-1].headers["x-anechoic-project-instance"])
            self.assertEqual(invocation(public_base_url=ORIGIN + "/"), json.loads(sent[-1].content))

            reply = {"error": FAULT | {"scope": "tool"}, "project": PROJECT}
            status = 503
            response = await client.post("/tools", json=invocation(), headers=BINDING)
            self.assertEqual((503, reply), (response.status_code, response.json()))

            reply = {"result": RESULT, "project": PROJECT | {"instance_id": "b" * 64}}
            status = 200
            response = await client.post("/tools", json=invocation(), headers=BINDING)
            self.assertEqual(502, response.status_code)
            self.assertEqual("project_receipt_mismatch", response.json()["error"]["code"])
            self.assertNotIn("result", response.json())

    async def test_shared_rejects_unsafe_requests_before_any_backend_call(self):
        def backend(_request):
            self.fail("Unexpected private request")

        async for client in self.shared(backend):
            for headers, status in [
                ({"Origin": "http://localhost:8093"}, 403),
                ({"Origin": "https://example.test"}, 403),
                ({"Host": "example.test"}, 421),
                ({"Sec-Fetch-Site": "cross-site"}, 403),
                ({"X-Anechoic-Project-Instance": "invalid"}, 200),
            ]:
                with self.subTest(headers=headers):
                    refused = await client.post("/tools", json=invocation(), headers=headers)
                    self.assertEqual(status, refused.status_code)
            encoded = json.dumps(invocation()).encode()

            async def oversized():
                yield encoded
                yield b" " * (65_537 - len(encoded))

            for body in [b"{", b"{}", oversized()]:
                refused = await client.post("/tools", content=body)
                self.assertEqual("invalid_tool_request", refused.json()["error"]["code"])

    async def test_valid_request_at_the_body_limit_preserves_cancellation(self):
        started = asyncio.Event()

        async def backend(_request):
            started.set()
            await asyncio.Future()

        async for client in self.shared(backend):
            encoded = json.dumps(invocation()).encode()
            encoded = encoded.ljust(65_536, b" ")
            async with asyncio.timeout(3):
                call = asyncio.create_task(client.post("/tools", content=encoded, headers=BINDING))
                await started.wait()
                call.cancel()
                with self.assertRaises(asyncio.CancelledError):
                    await call

    async def test_direct_catalog_binding_context_and_backend_status(self):
        sent = []
        expected_fault = {"error": FAULT | {"scope": "tool"}, "project": PROJECT}

        def backend(request):
            if request.method == "GET":
                self.assertEqual(INSTANCE, request.url.params["instance_id"])
                return httpx2.Response(200, json={"result": {"tools": [TOOL], "blacklist": []}})
            sent.append(json.loads(request.content))
            if sent[-1]["arguments"].get("fail"):
                return httpx2.Response(503, json={"error": FAULT})
            return httpx2.Response(200, json={"result": RESULT})

        root = Path.cwd()
        selection = SimpleNamespace(root=root, host_root=Path(ROOT),
                                    project_prefix="AN", instance_id=INSTANCE)
        owner = SimpleNamespace(start=lambda: None, selection=selection)
        private = self.enterContext(httpx2.Client(
            transport=httpx2.MockTransport(backend), base_url="http://backend"
        ))
        gateway = DirectGateway(root, native_query=owner, workbench=object(),
                                tool_client=BackendClient(selection, None, private))
        await gateway.initialize()
        client = await self.public(direct_app(root, runtime_gateway=gateway))
        catalog = (await client.get("/tools")).json()["result"]["tools"]
        self.assertEqual([TOOL["name"]], [entry["name"] for entry in catalog])
        self.assertNotIn("project_root", catalog[0]["inputSchema"]["required"])
        for headers, updates, code in [
            ({"X-Anechoic-Project-Instance": "b" * 64}, {}, "project_declarations_stale"),
            (BINDING, {"arguments": {"project_root": "/other"}}, "invalid_project_root"),
            (BINDING, {"name": "unknown"}, "tool_unavailable"),
        ]:
            with self.subTest(code=code):
                response = await client.post("/tools", json=invocation(**updates), headers=headers)
                self.assertEqual(code, response.json()["error"]["code"])
        self.assertEqual([], sent)
        response = await client.post("/tools", json=invocation(), headers=BINDING)
        self.assertEqual({"result": RESULT, "project": PROJECT}, response.json())
        self.assertEqual({
            "name": TOOL["name"], "arguments": {}, "instance_id": INSTANCE,
            "session_id": "test-session", "asserted_project_root": ROOT,
            "public_base_url": ORIGIN + "/",
        }, sent[-1])
        response = await client.post("/tools", json=invocation(arguments={"fail": True}), headers=BINDING)
        self.assertEqual((503, expected_fault), (response.status_code, response.json()))
        self.assertIsNone(sent[-1]["asserted_project_root"])
