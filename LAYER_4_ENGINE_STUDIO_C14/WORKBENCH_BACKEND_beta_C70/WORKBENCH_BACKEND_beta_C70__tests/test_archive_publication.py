"""Check that archive work is visible and does not delay live readiness."""

import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import httpx2

from .. import WORKBENCH_BACKEND_beta_C70__shared as api
from .. import projection_tools, runtime


class ArchivePublicationTests(unittest.IsolatedAsyncioTestCase):
    async def test_health_exposes_pending_and_legacy_default(self):
        app = api.create_app("instance", "digest", "/project", "db", "jobs")
        health = {"instance_id": "instance", "manifest_sha256": "digest", "pid": 42,
                  "generation": "live", "ready": True}
        async with httpx2.AsyncClient(transport=httpx2.ASGITransport(app=app),
                                      base_url="http://test") as client:
            with patch.object(api, "upstream", new_callable=AsyncMock) as upstream:
                for pending in (True, False, None):
                    result = dict(health)
                    if pending is not None:
                        result["archive_pending"] = pending
                    upstream.return_value = {"result": result}
                    response = await client.get("/health")
                    self.assertEqual(200, response.status_code)
                    self.assertTrue(response.json()["ready"])
                    self.assertEqual(pending is True, response.json()["archive_pending"])

    async def test_live_success_is_ready_while_archive_runs(self):
        peer = SimpleNamespace(poll=lambda: None)
        peers = runtime.ProjectPeers("db", "jobs", {}, peer, peer)
        replies = [{"result": {"ready": True, "archive_pending": True}},
                   {"result": {"latest": {"state": "succeeded"}, "active": None,
                               "archive": {"state": "running"}}}]
        with patch.object(runtime, "upstream", new_callable=AsyncMock, side_effect=replies):
            await peers.wait_ready("instance")

    async def test_status_exposes_archive_without_treating_it_as_live_sync(self):
        archive = {"state": "running", "started_at": 100, "worker_alive": True}
        replies = [{"result": {"active": None, "latest": {"state": "succeeded", "finished_at": 50},
                               "archive": archive}}, {"result": {"rows": []}}]
        with patch.object(projection_tools, "upstream", new_callable=AsyncMock, side_effect=replies) as upstream:
            response = await projection_tools.invoke("workbench_status", {}, "db", "jobs", None, "instance")
        status = response["result"]["value"]
        self.assertFalse(status["syncing"])
        self.assertEqual(archive, status["archive"])
        self.assertEqual(2, upstream.await_count)
