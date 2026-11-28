"""Fixtures and assertions for Tool REST ingress tests."""

import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import httpx2
from pydantic import BaseModel, ConfigDict

from MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__shared import (
    BackendClient,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.gateway.gateway__shared import (
    DirectGateway,
    create_http_app as direct_app,
    create_shared_http_app as shared_app,
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


class _TestProjectSelection(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    root: Path
    host_root: Path
    project_prefix: str
    project_name: str
    instance_id: str


class _TestProjectOwner(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    selection: _TestProjectSelection
    started: bool = False

    def start(self) -> None:
        self.started = True


class ToolRestFixture:
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
            "MCP_PATCHBAY_C21.FEATURE_MCP.gateway.workbench_web._FRONTEND",
            frontend,
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

    async def direct(self, backend):
        root = Path.cwd()
        selection = _TestProjectSelection(
            root=root,
            host_root=Path(ROOT),
            project_prefix="AN",
            project_name="Project",
            instance_id=INSTANCE,
        )
        owner = _TestProjectOwner(selection=selection)
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
        self.assertTrue(owner.started)
        with self.frontend():
            client = await self.public(
                direct_app(root, runtime_gateway=gateway)
            )
        return client

    async def _assert_shared_catalog(self, client):
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
        for method in ("GET", "POST"):
            self.assertEqual(
                404, (await client.request(method, "/tools")).status_code
            )
        catalog = await client.get("/")
        self.assertEqual({"result": {"tools": [TOOL]}}, catalog.json())

    async def _assert_shared_invocation(self, client, sent, reply):
        response = await client.post(
            "/",
            json=invocation(),
            headers=BINDING | {"Origin": ORIGIN},
        )
        self.assertEqual((200, reply), (response.status_code, response.json()))
        self.assertEqual(
            [("POST", "/selection"), ("GET", "/"), ("POST", "/")],
            [(request.method, request.url.path) for request in sent],
        )
        self.assertEqual(
            INSTANCE, sent[-1].headers["x-anechoic-project-instance"]
        )
        self.assertEqual(
            invocation(public_base_url=ORIGIN + "/"),
            json.loads(sent[-1].content),
        )

    async def _assert_shared_receipt_mismatch(self, client, gateway, sent):
        previous = len(sent)
        response = await client.post("/", json=invocation(), headers=BINDING)
        self.assertEqual(
            [("POST", "/")],
            [
                (request.method, request.url.path)
                for request in sent[previous:]
            ],
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

    async def _assert_direct_rejections(self, client, sent):
        catalog = (await client.get("/")).json()["result"]["tools"]
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
                    "/", json=invocation(**updates), headers=headers
                )
                self.assertEqual(code, response.json()["error"]["code"])
        self.assertEqual([], sent)

    async def _assert_direct_invocation(self, client, sent, expected_fault):
        unknown = await client.post(
            "/", json=invocation(name="unknown"), headers=BINDING
        )
        self.assertEqual("tool_unavailable", unknown.json()["error"]["code"])
        self.assertEqual("unknown", sent[-1]["name"])
        response = await client.post("/", json=invocation(), headers=BINDING)
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
            "/",
            json=invocation(arguments={"fail": True}),
            headers=BINDING,
        )
        self.assertEqual(
            (503, expected_fault), (response.status_code, response.json())
        )
        self.assertIsNone(sent[-1]["asserted_project_root"])
