"""The coordinator retains its Project lease while a child can finish a write."""

import asyncio
from types import SimpleNamespace
import unittest

import httpx2

from IWE_CONSOLE_C43.APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.project_tool_session import (
    ProjectToolSession,
)


class ProjectToolSessionTests(unittest.IsolatedAsyncioTestCase):
    async def test_cancellation_waits_for_dispatched_tool_without_replay(self):
        posted = []
        started = asyncio.Event()
        finish = asyncio.Event()

        class HTTP:
            async def post(self, path, *, json):
                posted.append((path, json))
                started.set()
                await finish.wait()
                return httpx2.Response(200, json={"result": {"value": {}, "text": None}})

        selection = SimpleNamespace(instance_id="alpha")
        gateway = ProjectToolSession("/project", selection=selection)
        gateway._http = HTTP()
        gateway._process = SimpleNamespace(poll=lambda: None)
        gateway._catalog_digest = "loaded"
        call = asyncio.create_task(gateway.call_tool(
            "atom_lifecycle_update", {}, session_id="operator", asserted_project_root="/project",
        ))
        try:
            await asyncio.wait_for(started.wait(), 1)
            call.cancel()
            await asyncio.sleep(0)
            self.assertFalse(call.done())
        finally:
            finish.set()
        with self.assertRaises(asyncio.CancelledError):
            await asyncio.wait_for(call, 1)
        self.assertEqual([("/tools", {
            "name": "atom_lifecycle_update", "arguments": {}, "instance_id": "alpha",
            "session_id": "operator", "public_base_url": None, "asserted_project_root": "/project",
        })], posted)
