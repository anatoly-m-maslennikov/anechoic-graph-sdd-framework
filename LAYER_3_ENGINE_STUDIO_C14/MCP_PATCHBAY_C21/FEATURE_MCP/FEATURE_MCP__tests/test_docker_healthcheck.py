"""Verify the image's opt-in MCP initialization health check."""
import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch
from types import SimpleNamespace

import httpx2
from starlette.applications import Starlette
from starlette.responses import Response
from starlette.routing import Route

import test_shared_http_server as shared

SCRIPT = Path(__file__).resolve().parents[1] / "docker" / "healthcheck.py"
spec = importlib.util.spec_from_file_location("docker_healthcheck", SCRIPT)
healthcheck = importlib.util.module_from_spec(spec)
spec.loader.exec_module(healthcheck)


class DockerHealthcheckTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.app = shared.create_app(SimpleNamespace(http_port=8092), gateway_factory=shared.FakeGateway)

    async def probe(self, app):
        client_class = httpx2.AsyncClient

        def client(**kwargs):
            self.assertEqual({"trust_env": False, "follow_redirects": False, "timeout": 3}, kwargs)
            return client_class(transport=httpx2.ASGITransport(app=app), **kwargs)

        with patch.object(httpx2, "AsyncClient", side_effect=client):
            await healthcheck.check()

    async def test_initializes_actual_mcp_session(self):
        async with self.app.starlette_app.router.lifespan_context(self.app.starlette_app):
            await self.probe(self.app)

    async def test_rejects_non_mcp_response(self):
        async def unavailable(request):
            return Response(status_code=503)

        app = Starlette(routes=[Route("/anechoic/mcp", unavailable, methods=["POST"])])
        with self.assertRaises(Exception):
            await self.probe(app)

    def test_other_modes_skip_mcp_dependencies(self):
        env = dict(os.environ, ANECHOIC_MCP_HTTP_HEALTHCHECK="0")
        result = subprocess.run([sys.executable, "-S", str(SCRIPT)], env=env, timeout=4)
        self.assertEqual(0, result.returncode)
