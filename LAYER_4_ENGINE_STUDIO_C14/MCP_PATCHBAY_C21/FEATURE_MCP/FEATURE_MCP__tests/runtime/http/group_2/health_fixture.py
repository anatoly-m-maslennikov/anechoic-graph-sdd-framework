"""Native Workbench ASGI fixture with controlled backend outcomes."""

from ....native_query_test_support import local_gateway

import asyncio
from pathlib import Path
import tempfile
from unittest.mock import NonCallableMock
import unittest

import httpx2
from mcp.client.session import ClientSession
from mcp.client.streamable_http import streamable_http_client


APP = Path(__file__).resolve().parents[4]
from MCP_PATCHBAY_C21.FEATURE_MCP.gateway.gateway__shared import (  # noqa: E402
    create_http_app as create_app,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.transport_support.paths.paths__shared import (  # noqa: E402
    MCP_PATH,
)  # noqa: E402


SECRET = "HEALTH_FIXTURE_SECRET"
PROVIDER_DIAGNOSTIC = "provider diagnostic /fixture/absolute/path"


class HealthHTTPFixture(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        directory = APP.parents[2] / ".anechoic_tmp/tests/mcp-health"
        directory.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(
            dir=directory, ignore_cleanup_errors=True
        )
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.marker = self.root / "backend.calls"
        self.app = self.new_app()

    async def backend_call(self, name, arguments):
        if name == "query_schema":
            return {
                "outcome": "completed",
                "secret": SECRET,
                "result": "fixture-result",
            }
        if name == "query_page":
            return {"outcome": "partial", "result": "partial-result"}
        if name == "query_load":
            return {
                "outcome": SECRET,
                "disposition": PROVIDER_DIAGNOSTIC,
                "error": SECRET,
            }
        if name == "query_check":
            raise RuntimeError(PROVIDER_DIAGNOSTIC)
        if name == "query_run":
            self.marker.write_text("slow-started")
            await asyncio.sleep(30)
        if name in {"workspace_list", "query_saved_list"}:
            await asyncio.sleep(0.02)
        return {"outcome": "completed", "worker": name}

    def headers(self, **extra):
        return {"host": "127.0.0.1:18092", **extra}

    def lifespan(self):
        return self.app.starlette_app.router.lifespan_context(
            self.app.starlette_app
        )

    def new_app(self):
        owner = NonCallableMock(
            spec_set=["selection", "start", "close"],
            selection=NonCallableMock(
                spec_set=["root", "parameters"], root=self.root, parameters={}
            ),
            start=lambda: None,
            close=lambda: None,
        )
        app = create_app(
            self.root,
            runtime_gateway=local_gateway(self.root, native_query=owner),
        )
        app.gateway.workbench.call = self.backend_call
        return app

    def raw_client(self):
        return httpx2.AsyncClient(
            transport=httpx2.ASGITransport(app=self.app),
            base_url="http://127.0.0.1:18092",
        )

    async def session(self):
        client = httpx2.AsyncClient(
            transport=httpx2.ASGITransport(app=self.app),
            base_url="http://127.0.0.1:18092",
        )
        transport = streamable_http_client(
            "http://127.0.0.1:18092" + MCP_PATH, http_client=client
        )
        streams = await transport.__aenter__()
        session = ClientSession(*streams)
        await session.__aenter__()
        await session.initialize()
        return client, transport, session

    async def close_session(self, client, transport, session):
        await session.__aexit__(None, None, None)
        await transport.__aexit__(None, None, None)
        await client.aclose()

    @staticmethod
    def outcome(row):
        return row.get("outcome", row.get("actual_outcome"))


if __name__ == "__main__":
    unittest.main()
