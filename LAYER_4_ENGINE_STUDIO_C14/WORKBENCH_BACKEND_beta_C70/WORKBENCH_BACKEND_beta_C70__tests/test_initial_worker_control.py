"""Observe and abort the first shared Project build over the Backend socket."""

import asyncio
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from .test_shared_beta import _backend, _invoke, _project, _settings, _status


class InitialWorkerTests(unittest.IsolatedAsyncioTestCase):
    async def test_control_reaches_initial_worker_without_admitting_sql(self):
        with TemporaryDirectory(prefix="ane-beta-init-", dir="/tmp") as temporary:
            directory = Path(temporary).resolve()
            projects = directory / "projects"
            projects.mkdir()
            project, _ = _project(projects, "initial")
            async with _backend(directory, _settings(directory, projects)) as (http, _):
                no_run = await _invoke(http, project, "workbench_abort", {"run_id": "unknown"})
                self.assertEqual("run_not_abortable", no_run["error"]["code"])
                self.assertEqual(0, (await _status(http))["loaded_project_count"])
                async with asyncio.TaskGroup() as group:
                    query = group.create_task(_invoke(http, project))
                    await self.abort_initial(http, project, query)
                refused = query.result()
                self.assertEqual("shared_gateway_failure", refused["error"]["code"])
                recovered = await _invoke(http, project)
                self.assertEqual([["initial"]], recovered["result"]["value"]["rows"])

    async def abort_initial(self, http, project, query):
        async with asyncio.timeout(20):
            while not query.done():
                status = await _invoke(http, project, "workbench_status", {})
                value = status["result"]["value"]
                if value.get("worker_alive"):
                    run = value["run_id"]
                    aborted = await _invoke(http, project, "workbench_abort", {"run_id": run})
                    self.assertEqual({"run_id": run, "state": "aborting"}, aborted["result"]["value"])
                    return
                await asyncio.sleep(0.02)
        self.fail("Initial Worker completed before the control request")
