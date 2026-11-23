"""Functional HTTP checks for the same-listener MCP health view."""
from types import SimpleNamespace

from .health_fixture import HealthHTTPFixture
from MCP_PATCHBAY_C21.FEATURE_MCP.health_page import render_health_page
from MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__shared import HEALTH_PATH


class HTTPHealthPageTests(HealthHTTPFixture):
    def test_renderer_escapes_dynamic_snapshot_fields(self):
        gateway = SimpleNamespace(
            ready=True, tools=[]
        )
        html = render_health_page(
            {
                "started_at": "<script>bad</script>",
                "calls": [{"observed_at": "<b>", "name": "<script>", "outcome": "returned"}],
            },
            ready=True,
            gateway=gateway,
        )
        self.assertIn("&lt;script&gt;", html)
        self.assertNotIn("<script>bad</script>", html)

    async def test_native_readiness_returns_json_for_browser_and_machine(self):
        async with self.lifespan():
            async with self.raw_client() as client:
                for accept in ("application/json", "text/html"):
                    response = await client.get(HEALTH_PATH, headers=self.headers(accept=accept))
                    self.assertEqual(200, response.status_code)
                    self.assertEqual({"ready": True}, response.json())
                self.app.gateway.ready = False
                response = await client.get(HEALTH_PATH, headers=self.headers())
                self.assertEqual(503, response.status_code)
                self.assertEqual({"ready": False}, response.json())
