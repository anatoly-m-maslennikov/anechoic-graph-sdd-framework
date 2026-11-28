"""Tool REST ingress checks without starting a server or Project owner."""

import asyncio
import json
import unittest
from unittest.mock import patch

import httpx2
from mcp import types

from MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__shared import ToolProtocolError
from MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__tests.integration.\
    tools.group_2.tool_rest_test_support import (
    BINDING,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__tests.integration.\
    tools.group_2.tool_rest_test_support import (
    FAULT,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__tests.integration.\
    tools.group_2.tool_rest_test_support import (
    INSTANCE,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__tests.integration.\
    tools.group_2.tool_rest_test_support import (
    JSON_HEADERS,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__tests.integration.\
    tools.group_2.tool_rest_test_support import (
    ORIGIN,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__tests.integration.\
    tools.group_2.tool_rest_test_support import (
    PROJECT,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__tests.integration.\
    tools.group_2.tool_rest_test_support import (
    RESULT,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__tests.integration.\
    tools.group_2.tool_rest_test_support import (
    TOOL,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__tests.integration.\
    tools.group_2.tool_rest_test_support import (
    ToolRestFixture,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__tests.integration.\
    tools.group_2.tool_rest_test_support import (
    invocation,
)


class ToolRestTests(ToolRestFixture, unittest.IsolatedAsyncioTestCase):
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
        await self._assert_shared_catalog(client)
        await self._assert_shared_invocation(client, sent, reply)

        reply = {"error": FAULT | {"scope": "tool"}, "project": PROJECT}
        status = 503
        response = await client.post("/", json=invocation(), headers=BINDING)
        self.assertEqual((503, reply), (response.status_code, response.json()))

        reply = {
            "result": RESULT,
            "project": PROJECT | {"instance_id": "b" * 64},
        }
        status = 200
        await self._assert_shared_receipt_mismatch(client, gateway, sent)

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
                    "/", json=invocation(), headers=headers
                )
                self.assertEqual(status, refused.status_code)
        encoded = json.dumps(invocation()).encode()

        async def oversized():
            yield encoded
            yield b" " * (65_537 - len(encoded))

        wrong_type = await client.post(
            "/",
            content=encoded,
            headers={"Content-Type": "text/plain"},
        )
        self.assertEqual(
            "invalid_tool_request", wrong_type.json()["error"]["code"]
        )
        for body in [b"{", b"{}", oversized()]:
            refused = await client.post(
                "/", content=body, headers=JSON_HEADERS
            )
            self.assertEqual(
                "invalid_tool_request", refused.json()["error"]["code"]
            )

    async def test_shared_catalog_rejects_invalid_descriptors(self):
        requests = []

        def backend(request):
            requests.append((request.method, request.url.path))
            return httpx2.Response(200, json={"result": {"tools": [None]}})

        client, gateway = await self.shared(backend)
        response = await client.get("/")
        self.assertEqual(503, response.status_code)
        self.assertEqual(
            "shared_gateway_failure", response.json()["error"]["code"]
        )
        self.assertEqual([("GET", "/")], requests)
        with self.assertRaises(ValueError):
            await gateway._load_catalog()

    async def test_shared_fault_receipts_match_in_rest_and_mcp(self):
        receipt = None

        def backend(_request):
            return httpx2.Response(
                200,
                json={"error": FAULT | {"scope": "tool"}, "project": receipt},
            )

        client, gateway = await self.shared(backend)
        for receipt, expected_status, expected_code in (
            (PROJECT, 200, FAULT["code"]),
            (None, 200, FAULT["code"]),
            (
                PROJECT | {"instance_id": "b" * 64},
                502,
                "project_receipt_mismatch",
            ),
            ({"instance_id": INSTANCE}, 502, "project_receipt_mismatch"),
        ):
            with self.subTest(receipt=receipt):
                response = await client.post(
                    "/", json=invocation(), headers=BINDING
                )
                self.assertEqual(expected_status, response.status_code)
                self.assertEqual(
                    expected_code, response.json()["error"]["code"]
                )
                with self.assertRaises(ToolProtocolError) as caught:
                    await gateway.call_tool(
                        TOOL["name"], {}, project_instance_id=INSTANCE
                    )
                self.assertEqual(expected_code, caught.exception.code)
                self.assertEqual(
                    response.json()["error"]["tool_result"],
                    caught.exception.tool_result,
                )

    async def test_shared_mcp_and_rest_validate_reply_envelopes(self):
        reply = {}
        requests = []

        def backend(request):
            requests.append((request.method, request.url.path))
            return httpx2.Response(200, json=reply)

        client, gateway = await self.shared(backend)
        params = types.CallToolRequestParams(
            name=TOOL["name"], arguments={"project_root": "/canonical/project"}
        )
        success = {"result": RESULT, "project": PROJECT}
        malformed = success | {"error": FAULT}
        with patch.object(
            gateway, "select_project", return_value={"instance_id": INSTANCE}
        ):
            for reply in (success, malformed):
                with self.subTest(reply=reply):
                    requests.clear()
                    rest = await client.post(
                        "/", json=invocation(), headers=BINDING
                    )
                    self.assertEqual([("POST", "/")], requests)
                    mcp = await gateway.call(None, params)
                    self.assertEqual([("POST", "/"), ("POST", "/")], requests)
                    if reply is malformed:
                        self.assertEqual(503, rest.status_code)
                        self.assertTrue(mcp.is_error)
                        self.assertEqual(
                            "failed", mcp.structured_content["outcome"]
                        )
                    else:
                        self.assertEqual(200, rest.status_code)
                        self.assertFalse(mcp.is_error)
                        self.assertEqual(
                            RESULT["value"], mcp.structured_content
                        )

    async def test_shared_limit_applies_after_inserting_trusted_origin(self):
        sizes = []

        def backend(request):
            sizes.append(len(request.content))
            return httpx2.Response(
                200, json={"result": RESULT, "project": PROJECT}
            )

        def encoded(size):
            def body(padding):
                return json.dumps(
                    invocation(
                        public_base_url=None, arguments={"data": padding}
                    ),
                    separators=(",", ":"),
                ).encode()

            return body("x" * (size - len(body(""))))

        client, _ = await self.shared(backend)
        inserted = len(json.dumps(ORIGIN + "/")) - len("null")
        good = await client.post(
            "/", content=encoded(65_536 - inserted), headers=JSON_HEADERS
        )
        bad = await client.post(
            "/", content=encoded(65_537 - inserted), headers=JSON_HEADERS
        )
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
                    "/",
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
        requests = []
        expected_fault = {
            "error": FAULT | {"scope": "tool"},
            "project": PROJECT,
        }

        def backend(request):
            requests.append((request.method, request.url.path))
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

        client = await self.direct(backend)
        page = await client.get("/anechoic/iwe-console/Project")
        self.assertEqual(200, page.status_code)
        self.assertIn(
            f'<meta name="anechoic-project-instance" content="{INSTANCE}">',
            page.text,
        )
        await self._assert_direct_rejections(client, sent)
        self.assertEqual([("GET", "/")], requests)
        await self._assert_direct_invocation(client, sent, expected_fault)
        self.assertEqual([("POST", "/")] * 3, requests[1:])
