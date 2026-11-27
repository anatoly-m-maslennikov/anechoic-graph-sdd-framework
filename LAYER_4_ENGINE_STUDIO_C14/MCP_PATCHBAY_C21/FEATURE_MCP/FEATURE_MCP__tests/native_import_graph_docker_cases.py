"""Docker graph browser and MCP cases shared by the E2E test class."""

import asyncio
from contextlib import ExitStack, contextmanager
import json
import os
from pathlib import Path
import subprocess
import tempfile
from time import monotonic, sleep
from uuid import uuid4

from mcp.client.session import ClientSession

from .FEATURE_MCP__tests__shared import project as make_project, run_workbench_browser
from .workbench_docker_support import (
    defer_container_cleanup, docker_deadline_env, image_mcp_transport, image_timeout, observing, request,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.work_journal__pub import PROJECT_DATABASE, append_sealed_events
from MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__shared import HEALTH_PATH, MCP_PATH


_STARTUP_REUSE_RUNS = """
    SELECT t.run_id, bool_or(e.kind = 'effect' AND e.name = 'generation_reuse_check'
                            AND e.outcome = 'succeeded')
    FROM flow_events t JOIN flow_events e USING (run_id)
    WHERE t.kind = 'trigger' AND t.name = 'startup'
      AND t.component = 'C68' AND e.sequence > t.sequence
    GROUP BY t.run_id
    HAVING bool_or(e.kind = 'output' AND e.name = 'generation_result')
"""




@contextmanager
def archive_project(case, prepare=make_project):
    """Run lifecycle operations against a disposable Project."""
    with tempfile.TemporaryDirectory(prefix="ane-archive-image-") as directory, ExitStack() as cleanup:
        root = Path(directory).resolve()
        subprocess.run(["git", "init", "--quiet", str(root)], check=True)
        control = "_anechoic_anechoic"
        prepare(root)
        name = f"ane-archive-{uuid4().hex}"
        defer_container_cleanup(cleanup.callback, name)
        container = subprocess.check_output([
            "docker", "run", "--detach", "--pull=never", "--init", "--name", name,
            "--label", "anechoic.test=import-graph-canary", "--read-only", "--tmpfs", "/tmp:rw,nosuid,nodev,size=256m",
            "--pids-limit", "128", "--cpus", "1", "--publish", "127.0.0.1::8092", "--volume", f"{root}:/project:rw",
            "--env", "ANECHOIC_RUNTIME_NAMESPACE=docker", "--env", f"ANECHOIC_CONTROL_ROOT={control}",
            "--env", docker_deadline_env(), os.environ["ANECHOIC_IMAGE"], "mcp-http",
        ], text=True, timeout=image_timeout(60)).strip()
        binding = subprocess.check_output(
            ["docker", "port", container, "8092/tcp"], text=True, timeout=image_timeout(10),
        ).strip()
        project = case.__class__("runTest")
        project.root, project.url, project.container = root, f"http://{binding}", container
        project.api = f"{project.url}/anechoic/Anechoic/api"
        deadline = monotonic() + 90
        while observing(container, deadline):
            try:
                if request(project.url + HEALTH_PATH) == (200, {"state": "ready"}):
                    break
            except OSError:
                pass
            sleep(.2)
        else:
            logs = subprocess.run(["docker", "logs", "--tail", "12", container], capture_output=True, text=True)
            raise RuntimeError(f"Archive Project failed to start: {logs.stdout}{logs.stderr}")
        yield project


class WarmProjectionRestartCase:
    def _startup_reuse_runs(self):
        return dict(self._rows(_STARTUP_REUSE_RUNS))

    def _startup_reuse_before_restart(self):
        environment = subprocess.check_output([
            "docker", "image", "inspect", "--format", "{{json .Config.Env}}", os.environ["ANECHOIC_IMAGE"],
        ], text=True, timeout=image_timeout(10))
        if bool({"ANECHOIC_RUNTIME_STACK=beta", "ANECHOIC_RUNTIME_STACK=beta_next"} & set(json.loads(environment))):
            return self._startup_reuse_runs().keys()
        return None

    def _assert_warm_projection_reused(self, previous):
        if previous is None:
            logs = subprocess.run(["docker", "logs", self.container],
                                  check=True, capture_output=True, text=True, timeout=image_timeout(10))
            self.assertIn("database_edit operation=reuse table=projection", logs.stdout + logs.stderr)
            return
        deadline = monotonic() + 10
        observed = self._startup_reuse_runs()
        while not observed.keys() - previous and observing(self.container, deadline):
            sleep(.1)
            observed = self._startup_reuse_runs()
        self.assertTrue(any(observed[run] for run in observed.keys() - previous),
                        f"No new Beta startup reuse run. Before: {previous}. After: {observed}.")

    def test_disk_journal_and_projection_survive_warm_restart(self):
        receipt, = append_sealed_events(
            self.root, [{"event_id": "host-canary"}], author="release-canary",
            local_date="2026-11-21", timezone="UTC", storage="duckdb",
        )
        sql = "SELECT record_id FROM work_journal WHERE author = 'release-canary'"
        self._wait_rows(sql, [[receipt["record_id"]]])
        saved = self._post("/run", {"sql": "SELECT 1", "save": True, "result_delivery": "inline"})
        self.assertEqual("SELECT 1", self._post("/load", {"reference": saved["saved_query_id"]})["sql"])
        self.assertEqual("ready", self._post("/rebuild", {"target": "all"})["status"])
        self.assertEqual([[receipt["record_id"]]], self._rows(sql))
        database = self.root / PROJECT_DATABASE
        inode = database.stat().st_ino
        previous_reuse = self._startup_reuse_before_restart()
        subprocess.run(["docker", "container", "restart", self.container],
                       check=True, capture_output=True, timeout=image_timeout(30))
        self._wait_ready()
        self.assertEqual(inode, database.stat().st_ino)
        self.assertEqual([[receipt["record_id"]]], self._rows(sql))
        self.assertEqual("SELECT 1", self._post("/load", {"reference": saved["saved_query_id"]})["sql"])
        self._assert_warm_projection_reused(previous_reuse)


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
                        result = await client.call_tool("query_run", {
                            "sql": f"SELECT {value} AS ready",
                            "result_delivery": "inline",
                            "result_format": "json_matrix",
                        })
                        self.assertFalse(result.is_error, result.structured_content)
                        self.assertEqual([[value]], result.structured_content["rows"])

        asyncio.run(exercise())

    def test_archive_requires_replacement_and_immediately_refreshes(self):
        async def exercise():
            async with image_mcp_transport(project.url + MCP_PATH) as streams, ClientSession(*streams) as client:
                await client.initialize()

                async def call(name, arguments, status="completed"):
                    result = await client.call_tool(name, arguments)
                    value = result.structured_content
                    self.assertEqual(status, value["status"], value)
                    return value

                async def create(summary):
                    created = await call("atom_lifecycle_create_draft", {"newAtom": {"template": "task",
                        "container": {"component": "C00"}, "body": f"## Summary\n\n{summary}\n"}})
                    draft = created["savedDraft"]
                    promoted = await call("atom_lifecycle_promote_draft", {"target": {
                        "ref_id": draft["ref_id"], "version": draft["version"]}, "targetStatus": "backlog"})
                    return promoted["artifact"]

                original = await create("Archive original canary.")
                atom = original["atom_id"]
                arguments = {"target": {"ref_id": atom, "version": original["version"]}}
                sql = (f'SELECT reference, "header.state.status" FROM atoms '
                       f"WHERE reference IN ('{atom}', '{atom}@{original['version']}')")
                started = monotonic()
                refused = await call("atom_lifecycle_archive", arguments, status="failed")
                print(f"archive refusal: {monotonic() - started:.3f}s", flush=True)
                self.assertEqual("invalid_input", refused["errors"][0]["code"], refused)
                self.assertEqual([], refused["effects"])
                self.assertEqual([[atom, "backlog"]], project._rows(sql))
                replacement = await create("Archive replacement canary.")
                path = project.root / replacement["path"]
                data = path.read_text(encoding="utf-8")
                self.assertNotIn("\nrelations:", data)
                path.write_text(data.replace(
                    "\n---\n", f"\nrelations:\n  IS_REPLACEMENT_FOR: [{atom}]\n---\n", 1), encoding="utf-8")
                relation_sql = ("SELECT source_ref, target_ref FROM relations WHERE source_kind = 'Atom' "
                                f"AND source_ref = '{replacement['atom_id']}' AND target_kind = 'Atom' "
                                f"AND target_ref = '{atom}' AND relation_type = 'IS_REPLACEMENT_FOR' AND NOT derived")
                await asyncio.to_thread(project._wait_rows, relation_sql, [[replacement["atom_id"], atom]])
                archived = await call("atom_lifecycle_archive", arguments)
                self.assertEqual("archived", archived["artifact"]["status"])
                self.assertEqual([[f"{atom}@{original['version']}", "archived"]], project._rows(sql))

        with archive_project(self) as project:
            asyncio.run(exercise())


    def test_promotion_immediately_refreshes_workbench(self):
        environment = subprocess.check_output([
            "docker", "image", "inspect", "--format", "{{json .Config.Env}}", os.environ["ANECHOIC_IMAGE"],
        ], text=True, timeout=image_timeout(10))
        beta = bool({"ANECHOIC_RUNTIME_STACK=beta", "ANECHOIC_RUNTIME_STACK=beta_next"} & set(json.loads(environment)))
        witness = """SELECT count(*) FROM flow_events t JOIN flow_events e USING (run_id)
            WHERE t.component = 'C68' AND t.kind = 'trigger' AND t.name = 'lifecycle_refresh'
              AND e.kind = 'output' AND e.name = 'generation_result' AND e.outcome = 'succeeded'
              AND json_extract_string(e.detail, '$.kind') = 'native_delta'"""

        async def exercise():
            async with image_mcp_transport(self.url + MCP_PATH) as streams, ClientSession(*streams) as client:
                await client.initialize()

                async def call(name, arguments, status="completed"):
                    before = self._rows(witness)[0][0] if beta else 0
                    started = monotonic()
                    result = await client.call_tool(name, arguments)
                    elapsed = monotonic() - started
                    self.assertFalse(result.is_error, result.structured_content)
                    self.assertEqual(status, result.structured_content["status"], result.structured_content)
                    if beta:
                        self._wait_rows(witness, [[before + 1]])
                        print(f"{name}: {elapsed:.3f}s (native_delta)", flush=True)
                    return result.structured_content

                await self._assert_ticket_promotion(call, beta)

        asyncio.run(exercise())

    async def _assert_ticket_promotion(self, call, beta):
        created = await call("atom_lifecycle_create_draft", {"newAtom": {
            "template": "task", "container": {"component": "C00"},
            "body": "## Summary\n\nPromotion canary.\n",
        }})
        draft = created["savedDraft"]
        atom = draft["atom_id"]
        sql = ('SELECT reference, "header.state.version", "header.state.status" FROM atoms '
               f"WHERE reference = '{atom}' OR reference LIKE '{atom}@%' "
               'ORDER BY "header.state.version", reference')
        if beta:
            self.assertEqual([[draft["ref_id"], 1, "draft"]], self._rows(sql))
        await call("atom_lifecycle_promote_draft", {
            "target": {"ref_id": draft["ref_id"], "version": draft["version"]},
            "targetStatus": "backlog",
        })
        if beta:
            self.assertEqual([[atom, 1, "backlog"]], self._rows(sql))
        revised = await call("atom_lifecycle_update", {
            "sourceCurrent": {"ref_id": draft["atom_id"], "version": 1},
            "changes": {"body": "## Summary\n\nPromotion canary.\n\nRevised.\n"},
        }, status="draft_created")
        revision = revised["savedDraft"]
        if beta:
            self.assertEqual([[atom, 1, "backlog"], [revision["ref_id"], 2, "draft"]], self._rows(sql))
        promoted = await call("atom_lifecycle_promote_draft", {
            "target": {"ref_id": revision["ref_id"], "version": revision["version"]},
            "targetStatus": "backlog",
        })
        if beta:
            self.assertEqual(2, promoted["artifact"]["version"])
        self.assertEqual([[atom + "@1", 1, "archived"], [atom, 2, "backlog"]], self._rows(sql))
