"""Docker graph browser and MCP cases shared by the E2E test class."""

import asyncio
import os
import subprocess
import tempfile

from mcp.client.session import ClientSession
from mcp.client.streamable_http import streamable_http_client

from . import test_native_startup as fixture
from MCP_PATCHBAY_C21.FEATURE_MCP.http_paths import MCP_PATH, WORKBENCH_PATH


class DockerBrowserAndMcpCases:
    def test_workbench_browser_flows(self):
        repository = fixture.MCP.parents[2]
        frontend = fixture.MCP.parents[1] / "IWE_CONSOLE_C43/APP_WORKBENCH/FEATURE_WORKBENCH_FRONTEND"
        environment = os.environ | {
            "WORKBENCH_E2E_URL": f"{self.url}{WORKBENCH_PATH}/Anechoic",
            "PLAYWRIGHT_BROWSERS_PATH": str(repository / ".anechoic_tmp/workbench/playwright-browsers"),
        }
        with tempfile.TemporaryDirectory(prefix="workbench-browser-") as output:
            result = subprocess.run(
                ["npm", "run", "test:e2e", "--", "--output", output, "--global-timeout", "115000", "--retries", "1"],
                cwd=frontend, env=environment,
                capture_output=True, text=True, timeout=120,
            )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)


    def test_mcp_queries_work_after_a_previous_session_closes(self):
        async def exercise():
            async with asyncio.timeout(15):
                for value in (1, 2):
                    async with (
                        streamable_http_client(self.url + MCP_PATH) as streams,
                        ClientSession(*streams) as client,
                    ):
                        await client.initialize()
                        result = await client.call_tool("query_run", {
                            "sql": f"SELECT {value} AS ready",
                            "result_delivery": "inline",
                            "result_format": "json_matrix",
                        })
                        self.assertFalse(result.is_error, result.structured_content)
                        self.assertEqual([[value]], result.structured_content["rows"])

        asyncio.run(exercise())


    def test_promotion_immediately_refreshes_workbench(self):
        async def exercise():
            async with streamable_http_client(self.url + MCP_PATH) as streams, ClientSession(*streams) as client:
                await client.initialize()

                async def call(name, arguments, status="completed"):
                    result = await client.call_tool(name, arguments)
                    self.assertFalse(result.is_error, result.structured_content)
                    self.assertEqual(status, result.structured_content["status"], result.structured_content)
                    return result.structured_content

                created = await call("atom_lifecycle_create_draft", {"newAtom": {
                    "template": "task", "container": {"component": "C00"},
                    "body": "## Summary\n\nPromotion canary.\n",
                }})
                draft = created["savedDraft"]
                await call("atom_lifecycle_promote_draft", {
                    "target": {"ref_id": draft["ref_id"], "version": draft["version"]},
                    "targetStatus": "backlog",
                })
                revised = await call("atom_lifecycle_update", {
                    "sourceCurrent": {"ref_id": draft["atom_id"], "version": 1},
                    "changes": {"body": "## Summary\n\nPromotion canary.\n\nRevised.\n"},
                }, status="draft_created")
                revision = revised["savedDraft"]
                await call("atom_lifecycle_promote_draft", {
                    "target": {"ref_id": revision["ref_id"], "version": revision["version"]},
                    "targetStatus": "backlog",
                })
                atom = draft["atom_id"]
                self.assertEqual([[atom + "@1", 1, "archived"], [atom, 2, "backlog"]], self._rows(
                    'SELECT reference, "header.state.version", "header.state.status" FROM atoms '
                    f"WHERE reference IN ('{atom}', '{atom}@1', '{revision['ref_id']}') "
                    'ORDER BY "header.state.version"'
                ))

        asyncio.run(exercise())

