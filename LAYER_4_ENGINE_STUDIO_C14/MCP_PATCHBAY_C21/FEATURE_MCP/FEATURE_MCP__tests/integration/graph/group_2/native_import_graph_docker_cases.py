"""Docker graph browser and MCP cases shared by the E2E test class."""

import asyncio
from contextlib import ExitStack, contextmanager
import os as os
from pathlib import Path
import subprocess
import tempfile
from time import monotonic, sleep as sleep
from uuid import uuid4

from mcp.client.session import ClientSession

from ..group_3 import _native_import_graph_docker_helpers as helpers
from ....FEATURE_MCP__tests__shared import project as make_project
from ....FEATURE_MCP__tests__shared import run_workbench_browser
from ...workbench.group_4.workbench_docker_support import (
    defer_container_cleanup,
)
from ...workbench.group_4.workbench_docker_support import (
    docker_deadline_env as docker_deadline_env,
)
from ...workbench.group_4.workbench_docker_support import image_mcp_transport
from ...workbench.group_4.workbench_docker_support import image_timeout
from ...workbench.group_4.workbench_docker_support import (
    observing as observing,
)
from ...workbench.group_4.workbench_docker_support import request as request
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.settings.\
    project.project_database__pub import (
    PROJECT_DATABASE,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.settings.\
    journal.work_journal__pub import (
    append_sealed_events,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.transport_support.paths.\
    paths__shared import (
    HEALTH_PATH as HEALTH_PATH,
    MCP_PATH,
)


@contextmanager
def archive_project(case, prepare=make_project):
    """Run lifecycle operations against a disposable Project."""
    with (
        tempfile.TemporaryDirectory(prefix="ane-archive-image-") as directory,
        ExitStack() as cleanup,
    ):
        root = Path(directory).resolve()
        subprocess.run(["git", "init", "--quiet", str(root)], check=True)
        control = "_anechoic_anechoic"
        prepare(root)
        name = f"ane-archive-{uuid4().hex}"
        defer_container_cleanup(cleanup.callback, name)
        container = helpers.launch_archive(root, name, control, globals())
        binding = subprocess.check_output(
            ["docker", "port", container, "8092/tcp"],
            text=True,
            timeout=image_timeout(10),
        ).strip()
        project = case.__class__("runTest")
        project.root, project.url, project.container = (
            root,
            f"http://{binding}",
            container,
        )
        project.api = f"{project.url}/anechoic/Anechoic/api"
        helpers.wait_archive(project, container, globals())
        yield project


class WarmProjectionRestartCase:
    def _assert_warm_projection_reused(self):
        logs = subprocess.run(
            ["docker", "logs", self.container],
            check=True,
            capture_output=True,
            text=True,
            timeout=image_timeout(10),
        )
        self.assertIn(
            "database_edit operation=reuse table=projection",
            logs.stdout + logs.stderr,
        )

    def test_disk_journal_and_projection_survive_warm_restart(self):
        (receipt,) = append_sealed_events(
            self.root,
            [{"event_id": "host-canary"}],
            author="release-canary",
            local_date="2026-11-21",
            timezone="UTC",
            storage="duckdb",
        )
        sql = (
            "SELECT record_id FROM work_journal WHERE author = "
            "'release-canary'"
        )
        self._wait_rows(sql, [[receipt["record_id"]]])
        saved = self._post(
            "/run",
            {"sql": "SELECT 1", "save": True, "result_delivery": "inline"},
        )
        self.assertEqual(
            "SELECT 1",
            self._post("/load", {"reference": saved["saved_query_id"]})["sql"],
        )
        self.assertEqual(
            "ready", self._post("/rebuild", {"target": "all"})["status"]
        )
        self.assertEqual([[receipt["record_id"]]], self._rows(sql))
        database = self.root / PROJECT_DATABASE
        inode = database.stat().st_ino
        subprocess.run(
            ["docker", "container", "restart", self.container],
            check=True,
            capture_output=True,
            timeout=image_timeout(30),
        )
        self._wait_ready()
        self.assertEqual(inode, database.stat().st_ino)
        self.assertEqual([[receipt["record_id"]]], self._rows(sql))
        self.assertEqual(
            "SELECT 1",
            self._post("/load", {"reference": saved["saved_query_id"]})["sql"],
        )
        self._assert_warm_projection_reused()


class DockerBrowserAndMcpCases:
    def test_workbench_browser_flows(self):
        run_workbench_browser(self)

    def test_mcp_queries_work_after_a_previous_session_closes(self):
        async def exercise():
            async with asyncio.timeout(image_timeout(15)):
                for value in (1, 2):
                    async with (
                        image_mcp_transport(self.url + MCP_PATH) as streams,
                        ClientSession(*streams) as client,
                    ):
                        await client.initialize()
                        result = await client.call_tool(
                            "query_run",
                            {
                                "sql": f"SELECT {value} AS ready",
                                "result_delivery": "inline",
                                "result_format": "json_matrix",
                            },
                        )
                        self.assertFalse(
                            result.is_error, result.structured_content
                        )
                        self.assertEqual(
                            [[value]], result.structured_content["rows"]
                        )

        asyncio.run(exercise())

    def test_archive_requires_replacement_and_immediately_refreshes(self):
        async def exercise():
            async with (
                image_mcp_transport(project.url + MCP_PATH) as streams,
                ClientSession(*streams) as client,
            ):
                await client.initialize()

                async def call(name, arguments, status="completed"):
                    result = await client.call_tool(name, arguments)
                    value = result.structured_content
                    self.assertEqual(status, value["status"], value)
                    return value

                (
                    original,
                    atom,
                    arguments,
                    sql,
                ) = await helpers.assert_archive_refused(
                    self, project, call, monotonic
                )
                await helpers.assert_archive_replacement(
                    self,
                    project,
                    call,
                    original,
                    atom,
                    arguments,
                    sql,
                    asyncio,
                )

        with archive_project(self) as project:
            asyncio.run(exercise())

    def test_promotion_immediately_refreshes_workbench(self):
        async def exercise():
            async with (
                image_mcp_transport(self.url + MCP_PATH) as streams,
                ClientSession(*streams) as client,
            ):
                await client.initialize()

                async def call(name, arguments, status="completed"):
                    result = await client.call_tool(name, arguments)
                    self.assertFalse(
                        result.is_error, result.structured_content
                    )
                    self.assertEqual(
                        status,
                        result.structured_content["status"],
                        result.structured_content,
                    )
                    return result.structured_content

                await self._assert_ticket_promotion(call)

        asyncio.run(exercise())

    async def _assert_ticket_promotion(self, call):
        await helpers.assert_ticket_promotion(self, call)
