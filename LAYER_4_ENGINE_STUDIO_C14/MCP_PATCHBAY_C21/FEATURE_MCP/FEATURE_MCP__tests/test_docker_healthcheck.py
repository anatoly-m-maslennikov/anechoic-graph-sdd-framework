"""Verify the image's opt-in MCP session health check."""

import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch
from types import SimpleNamespace

import httpx2
from mcp.client.session import ClientSession
from starlette.applications import Starlette
from starlette.responses import JSONResponse, Response
from starlette.routing import Route

from . import test_shared_http_server as shared

SCRIPT = Path(__file__).resolve().parents[1] / "docker" / "healthcheck.py"
spec = importlib.util.spec_from_file_location("docker_healthcheck", SCRIPT)
healthcheck = importlib.util.module_from_spec(spec)
spec.loader.exec_module(healthcheck)


class DockerHealthcheckTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.app = shared.create_app(
            SimpleNamespace(http_port=8092), gateway_factory=shared.FakeGateway
        )

    async def probe(self, app):
        client_class = httpx2.AsyncClient

        def client(**kwargs):
            self.assertEqual(
                {"trust_env": False, "follow_redirects": False, "timeout": 3},
                kwargs,
            )
            return client_class(
                transport=httpx2.ASGITransport(app=app), **kwargs
            )

        with patch.object(httpx2, "AsyncClient", side_effect=client):
            await healthcheck.check()

    async def test_initializes_and_pings_actual_mcp_session(self):
        ping = ClientSession.send_ping
        calls = []

        async def record_ping(session):
            calls.append(session)
            return await ping(session)

        async with self.app.starlette_app.router.lifespan_context(
            self.app.starlette_app
        ):
            with patch.object(ClientSession, "send_ping", record_ping):
                await self.probe(self.app)
        self.assertEqual(1, len(calls))

    async def test_rejects_failed_ping(self):
        async with self.app.starlette_app.router.lifespan_context(
            self.app.starlette_app
        ):
            with patch.object(
                ClientSession,
                "send_ping",
                side_effect=RuntimeError("ping failed"),
            ):
                with self.assertRaises(ExceptionGroup) as failure:
                    await self.probe(self.app)
        self.assertIsNotNone(failure.exception.subgroup(RuntimeError))

    async def test_rejects_a_pending_health_response_before_initializing(self):
        async with self.app.starlette_app.router.lifespan_context(
            self.app.starlette_app
        ):
            self.app.gateway.snapshot["initialized"] = False
            async with httpx2.AsyncClient(
                transport=httpx2.ASGITransport(app=self.app)
            ) as client:
                response = await client.get(
                    "http://127.0.0.1:8092/anechoic/health"
                )
            self.assertEqual(
                (200, {"state": "pending"}),
                (response.status_code, response.json()),
            )
            with (
                patch.object(ClientSession, "initialize") as initialize,
                self.assertRaisesRegex(
                    RuntimeError, "MCP service is not ready"
                ),
            ):
                await self.probe(self.app)
            initialize.assert_not_called()

    async def test_rejects_non_mcp_response(self):
        async def ready(request):
            return JSONResponse({"state": "ready"})

        async def unavailable(request):
            return Response(status_code=503)

        app = Starlette(
            routes=[
                Route("/anechoic/health", ready),
                Route("/anechoic/mcp", unavailable, methods=["POST"]),
            ]
        )
        with self.assertRaises(Exception):
            await self.probe(app)

    def test_other_modes_skip_mcp_dependencies(self):
        env = dict(os.environ, ANECHOIC_MCP_HTTP_HEALTHCHECK="0")
        result = subprocess.run(
            [sys.executable, "-B", "-S", str(SCRIPT)], env=env, timeout=4
        )
        self.assertEqual(0, result.returncode)
