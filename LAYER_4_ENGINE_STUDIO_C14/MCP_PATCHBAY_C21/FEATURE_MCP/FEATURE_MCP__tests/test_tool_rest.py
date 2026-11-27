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
from MCP_PATCHBAY_C21.FEATURE_MCP.backend_client import ToolProtocolError
from MCP_PATCHBAY_C21.FEATURE_MCP.direct_gateway import DirectGateway
from MCP_PATCHBAY_C21.FEATURE_MCP.http_server import create_app as direct_app
from MCP_PATCHBAY_C21.FEATURE_MCP.shared_http_server import (
    create_app as shared_app,
)


ORIGIN = "http://localhost:8092"
ROOT = "/canonical/project"
INSTANCE = "a" * 64
BINDING = {"X-Anechoic-Project-Instance": INSTANCE}
JSON_HEADERS = {"Content-Type": "application/json"}
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
        return await self.enterAsyncContext(
            httpx2.AsyncClient(
                transport=httpx2.ASGITransport(app=app), base_url=ORIGIN
            )
        )

    def frontend(self):
        frontend = Path(self.enterContext(TemporaryDirectory()))
        (frontend / "index.html").write_text(
            "<!doctype html><html><head></head><body></body></html>",
            encoding="utf-8",
        )
        return patch(
            "MCP_PATCHBAY_C21.FEATURE_MCP.workbench_web._FRONTEND", frontend
        )

    async def shared(self, handler):
        with self.frontend():
            app = shared_app(None)
        app.gateway._http = await self.enterAsyncContext(
            httpx2.AsyncClient(
                transport=httpx2.MockTransport(handler),
                base_url="http://backend",
            )
        )
        return await self.public(app), app.gateway

    async def test_shared_catalog_and_invocation_keep_backend_contract(self):
        sent = []
        reply = {"result": RESULT, "project": PROJECT}
        status = 200

        def backend(request):
            sent.append(request)
            if request.url.path == "/selection":
                return httpx2.Response(
                    200,
                    json={
                        "result": {
                            "project_name": "Project",
                            "instance_id": INSTANCE,
                        }
                    },
                )
            if request.method == "GET":
                return httpx2.Response(200, json={"result": {"tools": [TOOL]}})
            return httpx2.Response(status, json=reply)

        client, gateway = await self.shared(backend)
        page = await client.get(
            "/anechoic/iwe-console/Project", params={"project_root": ROOT}
        )
        self.assertEqual(200, page.status_code)
        self.assertIn(
            f'<meta name="anechoic-project-instance" content="{INSTANCE}">',
            page.text,
        )
        self.assertEqual("no-store", page.headers["cache-control"])
        self.assertEqual(
            404, (await client.post("/selection", json={})).status_code
        )
        catalog = await client.get("/tools")
        self.assertEqual({"result": {"tools": [TOOL]}}, catalog.json())
        response = await client.post(
            "/tools",
            json=invocation(),
            headers=BINDING | {"Origin": ORIGIN},
        )
        self.assertEqual((200, reply), (response.status_code, response.json()))
        self.assertEqual(
            ["/selection", "/tools", "/tools"],
            [request.url.path for request in sent],
        )
        self.assertEqual(
            INSTANCE, sent[-1].headers["x-anechoic-project-instance"]
        )
        self.assertEqual(
            invocation(public_base_url=ORIGIN + "/"),
            json.loads(sent[-1].content),
        )

        reply = {"error": FAULT | {"scope": "tool"}, "project": PROJECT}
        status = 503
        response = await client.post(
            "/tools", json=invocation(), headers=BINDING
        )
        self.assertEqual((503, reply), (response.status_code, response.json()))

        reply = {
            "result": RESULT,
            "project": PROJECT | {"instance_id": "b" * 64},
        }
        status = 200
        response = await client.post(
            "/tools", json=invocation(), headers=BINDING
        )
        self.assertEqual(502, response.status_code)
        self.assertEqual(
            "project_receipt_mismatch", response.json()["error"]["code"]
        )
        self.assertNotIn("result", response.json())
        calls = gateway.health_observations.snapshot()["calls"]
        self.assertEqual(
            ["completed", "failed"], [call["outcome"] for call in calls]
        )
        self.assertEqual(
            [INSTANCE, INSTANCE],
            [call["project_instance_id"] for call in calls],
        )

    async def test_shared_rejects_unsafe_requests_before_any_backend_call(
        self,
    ):
        def backend(_request):
            self.fail("Unexpected private request")

        client, _ = await self.shared(backend)
        for headers, status in [
            ({"Origin": "http://localhost:8093"}, 403),
            ({"Origin": "https://example.test"}, 403),
            ({"Host": "example.test"}, 421),
            ({"Sec-Fetch-Site": "cross-site"}, 403),
            ({"X-Anechoic-Project-Instance": "invalid"}, 200),
        ]:
            with self.subTest(headers=headers):
                refused = await client.post(
                    "/tools", json=invocation(), headers=headers
                )
                self.assertEqual(status, refused.status_code)
        encoded = json.dumps(invocation()).encode()

        async def oversized():
            yield encoded
            yield b" " * (65_537 - len(encoded))

        wrong_type = await client.post(
            "/tools",
            content=encoded,
            headers={"Content-Type": "text/plain"},
        )
        self.assertEqual(
            "invalid_tool_request", wrong_type.json()["error"]["code"]
        )
        for body in [b"{", b"{}", oversized()]:
            refused = await client.post(
                "/tools", content=body, headers=JSON_HEADERS
            )
            self.assertEqual(
                "invalid_tool_request", refused.json()["error"]["code"]
            )

    async def test_shared_catalog_rejects_invalid_descriptors(self):
        def backend(_request):
            return httpx2.Response(200, json={"result": {"tools": [None]}})

        client, gateway = await self.shared(backend)
        response = await client.get("/tools")
        self.assertEqual(503, response.status_code)
        self.assertEqual("shared_gateway_failure", response.json()["error"]["code"])
        with self.assertRaises(ValueError):
            await gateway._load_catalog()

    async def test_shared_fault_receipts_match_in_rest_and_mcp(self):
        receipt = None

        def backend(_request):
            return httpx2.Response(
                200, json={"error": FAULT | {"scope": "tool"}, "project": receipt}
            )

        client, gateway = await self.shared(backend)
        for receipt, expected_status, expected_code in (
            (PROJECT, 200, FAULT["code"]),
            (None, 200, FAULT["code"]),
            (PROJECT | {"instance_id": "b" * 64}, 502, "project_receipt_mismatch"),
            ({"instance_id": INSTANCE}, 502, "project_receipt_mismatch"),
        ):
            with self.subTest(receipt=receipt):
                response = await client.post("/tools", json=invocation(), headers=BINDING)
                self.assertEqual(expected_status, response.status_code)
                self.assertEqual(expected_code, response.json()["error"]["code"])
                with self.assertRaises(ToolProtocolError) as caught:
                    await gateway.call_tool(TOOL["name"], {}, project_instance_id=INSTANCE)
                self.assertEqual(expected_code, caught.exception.code)
                self.assertEqual(response.json()["error"]["tool_result"], caught.exception.tool_result)

    async def test_shared_limit_applies_after_inserting_trusted_origin(self):
        sizes = []

        def backend(request):
            sizes.append(len(request.content))
            return httpx2.Response(200, json={"result": RESULT, "project": PROJECT})

        def encoded(size):
            def body(padding):
                return json.dumps(
                    invocation(public_base_url=None, arguments={"data": padding}),
                    separators=(",", ":"),
                ).encode()

            return body("x" * (size - len(body(""))))

        client, _ = await self.shared(backend)
        inserted = len(json.dumps(ORIGIN + "/")) - len("null")
        good = await client.post("/tools", content=encoded(65_536 - inserted), headers=JSON_HEADERS)
        bad = await client.post("/tools", content=encoded(65_537 - inserted), headers=JSON_HEADERS)
        self.assertEqual(RESULT, good.json()["result"])
        self.assertEqual("invalid_tool_request", bad.json()["error"]["code"])
        self.assertEqual([65_536], sizes)

    async def test_valid_request_at_the_body_limit_preserves_cancellation(
        self,
    ):
        started = asyncio.Event()

        async def backend(_request):
            started.set()
            await asyncio.Future()

        client, _ = await self.shared(backend)
        encoded = json.dumps(invocation()).encode()
        encoded = encoded.ljust(65_536, b" ")
        async with asyncio.timeout(3):
            call = asyncio.create_task(
                client.post(
                    "/tools",
                    content=encoded,
                    headers=BINDING | JSON_HEADERS,
                )
            )
            await started.wait()
            call.cancel()
            with self.assertRaises(asyncio.CancelledError):
                await call

    async def test_direct_catalog_binding_context_and_backend_status(self):
        sent = []
        expected_fault = {
            "error": FAULT | {"scope": "tool"},
            "project": PROJECT,
        }

        def backend(request):
            if request.method == "GET":
                self.assertEqual(INSTANCE, request.url.params["instance_id"])
                return httpx2.Response(
                    200, json={"result": {"tools": [TOOL], "blacklist": []}}
                )
            sent.append(json.loads(request.content))
            if sent[-1]["name"] != TOOL["name"]:
                return httpx2.Response(
                    200,
                    json={
                        "error": {
                            "code": "tool_unavailable",
                            "message": "Unknown Tool",
                            "tool_result": {
                                "outcome": "rejected",
                                "diagnostics": ["Unknown Tool"],
                            },
                        }
                    },
                )
            if sent[-1]["arguments"].get("fail"):
                return httpx2.Response(503, json={"error": FAULT})
            return httpx2.Response(200, json={"result": RESULT})

        root = Path.cwd()
        selection = SimpleNamespace(
            root=root,
            host_root=Path(ROOT),
            project_prefix="AN",
            project_name="Project",
            instance_id=INSTANCE,
        )
        owner = SimpleNamespace(start=lambda: None, selection=selection)
        private = self.enterContext(
            httpx2.Client(
                transport=httpx2.MockTransport(backend),
                base_url="http://backend",
            )
        )
        gateway = DirectGateway(
            root,
            native_query=owner,
            workbench=object(),
            tool_client=BackendClient(selection, None, private),
        )
        await gateway.initialize()
        with self.frontend():
            client = await self.public(
                direct_app(root, runtime_gateway=gateway)
            )
        page = await client.get("/anechoic/iwe-console/Project")
        self.assertEqual(200, page.status_code)
        self.assertIn(
            f'<meta name="anechoic-project-instance" content="{INSTANCE}">',
            page.text,
        )
        catalog = (await client.get("/tools")).json()["result"]["tools"]
        self.assertEqual([TOOL["name"]], [entry["name"] for entry in catalog])
        self.assertNotIn("project_root", catalog[0]["inputSchema"]["required"])
        for headers, updates, code in [
            (
                {"X-Anechoic-Project-Instance": "b" * 64},
                {},
                "project_declarations_stale",
            ),
            (
                BINDING,
                {"arguments": {"project_root": "/other"}},
                "invalid_project_root",
            ),
        ]:
            with self.subTest(code=code):
                response = await client.post(
                    "/tools", json=invocation(**updates), headers=headers
                )
                self.assertEqual(code, response.json()["error"]["code"])
        self.assertEqual([], sent)
        unknown = await client.post(
            "/tools", json=invocation(name="unknown"), headers=BINDING
        )
        self.assertEqual("tool_unavailable", unknown.json()["error"]["code"])
        self.assertEqual("unknown", sent[-1]["name"])
        response = await client.post(
            "/tools", json=invocation(), headers=BINDING
        )
        self.assertEqual(
            {"result": RESULT, "project": PROJECT}, response.json()
        )
        self.assertEqual(
            {
                "name": TOOL["name"],
                "arguments": {},
                "instance_id": INSTANCE,
                "session_id": "test-session",
                "asserted_project_root": ROOT,
                "public_base_url": ORIGIN + "/",
            },
            sent[-1],
        )
        response = await client.post(
            "/tools",
            json=invocation(arguments={"fail": True}),
            headers=BINDING,
        )
        self.assertEqual(
            (503, expected_fault), (response.status_code, response.json())
        )
        self.assertIsNone(sent[-1]["asserted_project_root"])
