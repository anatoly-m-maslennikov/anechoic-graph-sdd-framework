"""Check the bounded full-generation admission route."""

import asyncio
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock, patch

import httpx2

from ..DATABASE_SERVER_beta_C71__shared import create_app, FULL_GENERATION_BODY_LIMIT
from ..query_engine import connect
from ..native_delta import native_generation_route
from .DATABASE_SERVER_beta_C71__tests__shared import BINDING, PIN, _generation, _launch_arguments, _server


class FullGenerationLimitTest(unittest.TestCase):
    def test_native_full_and_delta_use_distinct_limits(self):
        read = AsyncMock(return_value={"instance_id": "foreign"})
        route = native_generation_route(None, "instance", PIN, None, read, lambda *args: None)

        async def exercise():
            for path in ("/generation/native", "/generation/native-delta"):
                await route(SimpleNamespace(url=SimpleNamespace(path=path)))

        asyncio.run(exercise())
        self.assertEqual([128 * 1024 * 1024, 64 * 1024 * 1024],
                         [call.args[1] for call in read.await_args_list])

    def test_bounded_admission_preserves_previous_generation(self):
        self.assertEqual(128 * 1024 * 1024, FULL_GENERATION_BODY_LIMIT)
        with TemporaryDirectory(dir="/tmp") as directory:
            path = Path(directory).resolve() / "db.duckdb"
            with _server(path) as client:
                response = client.put("/generation", json=_generation())
                self.assertEqual(200, response.status_code, response.text)
            _, environment = _launch_arguments(Path(directory) / "db.sock", path)
            with patch.dict(os.environ, environment), connect(str(path)) as connection:
                app = create_app(connection, BINDING["instance_id"], PIN)
                route = next(r for r in app.routes if r.path == "/generation")

                async def exercise():
                    async with httpx2.AsyncClient(transport=httpx2.ASGITransport(app=app), base_url="http://test") as client:
                        payload = _generation()
                        payload["snapshot"]["atoms"][0]["summary"] = "changed"
                        body = json.dumps(payload).encode()
                        with patch.dict(route.endpoint.__globals__, {"FULL_GENERATION_BODY_LIMIT": len(body)}):
                            accepted = await client.put("/generation", content=body)
                            self.assertEqual(200, accepted.status_code, accepted.text)
                            generation = connection.execute("SELECT id FROM ops_generation").fetchone()[0]
                            rejected = await client.put("/generation", content=body + b" ")
                            self.assertEqual(400, rejected.status_code, rejected.text)
                            self.assertEqual(generation, connection.execute("SELECT id FROM ops_generation").fetchone()[0])
                            self.assertEqual("changed", connection.execute('SELECT "content.summary" FROM mrt_atoms').fetchone()[0])

                asyncio.run(exercise())
