"Exercise initial Worker control through the real shared API and peer owner."

import asyncio
import os
import sys
import tempfile
import unittest
from pathlib import Path

import httpx2

from .test_archive_process import ENGINE, write_manifest


class SharedInitialControlTests(unittest.IsolatedAsyncioTestCase):
    async def test_initial_worker_abort_refuses_sql_and_recovers(self):
        temporary = self.enterContext(
            tempfile.TemporaryDirectory(
                prefix="ane-shared-control-", dir="/tmp"
            )
        )
        runtime = Path(temporary).resolve()
        project = runtime / "project"
        project.mkdir()
        write_manifest(project)
        settings = runtime / "host.toml"
        settings.write_text(
            f'schema_version=1\n[shared_mcp]\nproject_root="{project}"\n'
            "http_port=8092\nmax_loaded_projects=1\n"
        )
        env = {
            **os.environ,
            "PYTHONPATH": str(ENGINE),
            "ANECHOIC_RUNTIME_PROFILE": "test",
            "ANECHOIC_LOG_LEVEL": "ERROR",
            "ANECHOIC_DUCKPGQ_EXTENSION_DIRECTORY": os.environ.get(
                "ANECHOIC_DUCKPGQ_EXTENSION_DIRECTORY",
                str(ENGINE.parent / ".anechoic_tmp/workbench/extensions"),
            ),
        }
        owner_socket, api_socket = runtime / "owner.sock", runtime / "api.sock"
        owner = await self.start(
            "ORCHESTRATOR_beta_C68.shared_peer_owner",
            env,
            "--socket",
            str(owner_socket),
            "--host-settings",
            str(settings),
        )
        await self.wait_socket(owner_socket, owner)
        api = await self.start(
            "API_MIXER_beta_C91.shared_runtime",
            env,
            "--socket",
            str(api_socket),
            "--peer-owner-socket",
            str(owner_socket),
        )
        await self.wait_socket(api_socket, api)
        await self.exercise(api_socket, project)

    async def exercise(self, api_socket, project):
        async with httpx2.AsyncClient(
            transport=httpx2.AsyncHTTPTransport(uds=str(api_socket)),
            base_url="http://private",
            timeout=90,
            trust_env=False,
        ) as client:

            async def invoke(name, arguments):
                request = {
                    "name": name,
                    "arguments": {"project_root": str(project), **arguments},
                    "session_id": None,
                    "public_base_url": None,
                }
                return (await client.post("/tools", json=request)).json()

            cold = await invoke("workbench_abort", {"run_id": "unknown"})
            self.assertEqual("run_not_abortable", cold["error"]["code"])
            self.assertEqual(
                0,
                (await client.get("/health")).json()["result"][
                    "loaded_project_count"
                ],
            )
            query = asyncio.create_task(
                invoke(
                    "query_run",
                    {"sql": "SELECT 42", "result_delivery": "inline"},
                )
            )
            await self.control_initial_worker(query, invoke)
            recovered = await invoke(
                "query_run", {"sql": "SELECT 42", "result_delivery": "inline"}
            )
            self.assertEqual([[42]], recovered["result"]["value"]["rows"])

    async def control_initial_worker(self, query, invoke):
        try:
            async with asyncio.timeout(45):
                while not query.done():
                    status = (await invoke("workbench_status", {}))["result"][
                        "value"
                    ]
                    if status.get("worker_alive"):
                        break
                    await asyncio.sleep(0.02)
                else:
                    self.fail(
                        (
                            "Initial Worker finished before it could be "
                            "controlled: "
                            f"{query.result()}"
                        )
                    )
                self.assertFalse(
                    query.done(),
                    "SQL was admitted while the initial Worker was active",
                )
                run_id = status["run_id"]
                aborted = await invoke("workbench_abort", {"run_id": run_id})
                self.assertEqual(
                    {"run_id": run_id, "state": "aborting"},
                    aborted["result"]["value"],
                )
                self.assertEqual(
                    "shared_gateway_failure",
                    (await query)["error"]["code"],
                )
                status = await invoke("workbench_status", {})
                self.assertEqual(
                    "live_index", status["result"]["value"]["mode"]
                )
        finally:
            if not query.done():
                query.cancel()
                await asyncio.gather(query, return_exceptions=True)

    async def start(self, module, env, *arguments):
        process = await asyncio.create_subprocess_exec(
            sys.executable,
            "-B",
            "-P",
            "-m",
            module,
            *arguments,
            cwd=ENGINE,
            env=env,
            stdin=asyncio.subprocess.PIPE,
        )
        self.addAsyncCleanup(self.stop, process)
        return process

    async def stop(self, process):
        process.stdin.close()
        try:
            await asyncio.wait_for(process.wait(), 20)
        except TimeoutError:
            process.kill()
            await process.wait()
            self.fail("Shared process did not stop on EOF")
        self.assertEqual(0, process.returncode)

    async def wait_socket(self, path, process):
        async with asyncio.timeout(30):
            while not path.is_socket():
                self.assertIsNone(
                    process.returncode,
                    f"Process exited before creating {path}",
                )
                await asyncio.sleep(0.02)
