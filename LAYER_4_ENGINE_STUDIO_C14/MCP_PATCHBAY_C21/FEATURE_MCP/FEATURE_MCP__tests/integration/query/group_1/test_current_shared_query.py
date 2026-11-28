"""Exercise shared Current Web and MCP queries for independent Projects."""

import asyncio
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import unittest

import httpx2
from mcp import ClientSession, types
from mcp.client.streamable_http import streamable_http_client

from ....runtime.core.group_2.example_project import project
from ...shared.group_2.shared_query_lifecycle import SharedQueryLifecycle

ENGINE = Path(__file__).resolve().parents[6]
SQL = 'SELECT reference, "content.summary" FROM atoms ORDER BY reference'


def launch(settings, port):
    child = (
        "import sys,uvicorn; from MCP_PATCHBAY_C21.FEATURE_MCP.gateway import shared_http_server as h; "
        "original=uvicorn.run; uvicorn.run=lambda app,**kw: original(app,**(kw | {'host':'127.0.0.1'})); "
        f"h.PORT={port}; sys.exit(h.main(['--host-settings',sys.argv[1]]))"
    )
    env = {
        **os.environ,
        "PYTHONPATH": str(ENGINE),
        "ANECHOIC_RUNTIME_STACK": "current",
        "PYTHONDONTWRITEBYTECODE": "1",
        "ANECHOIC_DUCKPGQ_EXTENSION_DIRECTORY": os.environ.get(
            "ANECHOIC_DUCKPGQ_EXTENSION_DIRECTORY",
            str(ENGINE.parent / ".anechoic_tmp/workbench/extensions"),
        ),
    }
    log = tempfile.TemporaryFile(mode="w+")
    proc = subprocess.Popen(
        [sys.executable, "-B", "-c", child, str(settings)],
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=log,
    )
    return proc, log


class SharedProjectQueries(
    SharedQueryLifecycle, unittest.IsolatedAsyncioTestCase
):
    async def test_independent_projects_and_refresh(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            projects = root / "projects"
            first, second = projects / "alpha", projects / "beta"
            first_task = project(first)
            first_task.rename(
                first_task.with_name("EX-T-1-TASK--example-task.md")
            )
            task = project(second)
            task.write_text(
                task.read_text().replace("Example task", "Second task")
            )
            settings = root / "host.toml"
            settings.write_text(
                "schema_version=1\n[shared_mcp]\nprojects_root="
                + json.dumps(str(projects))
                + (
                    "\nhttp_port=8092\n[project_defaults]\n"
                    'workbench_storage="memory"\n'
                )
            )
            with socket.socket() as sock:
                sock.bind(("127.0.0.1", 0))
                port = sock.getsockname()[1]
            proc, log = launch(settings, port)
            try:
                await self.exercise(port, proc, first, second, task)
            except BaseException:
                log.seek(0)
                print(log.read(), file=sys.stderr)
                raise
            finally:
                proc.terminate()
                try:
                    proc.wait(timeout=15)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    proc.wait()
                log.close()

    async def exercise(self, port, proc, first, second, task):
        url = f"http://127.0.0.1:{port}"
        async with httpx2.AsyncClient(
            base_url=url, timeout=30, trust_env=False
        ) as http:
            async with asyncio.timeout(90):
                while True:
                    self.assertIsNone(
                        proc.poll(), "shared Current host exited"
                    )
                    try:
                        response = await http.get("/anechoic/health")
                        if (
                            response.status_code == 200
                            and response.json().get("state") == "ready"
                        ):
                            break
                    except httpx2.TransportError:
                        pass
                    await asyncio.sleep(0.2)
            async with streamable_http_client(
                url + "/anechoic/mcp", http_client=http
            ) as streams:
                async with ClientSession(*streams) as client:
                    await client.initialize()
                    self.instances = {}
                    catalog = await http.get("/")
                    catalog.raise_for_status()
                    self.assertEqual(
                        (await client.list_tools()).tools,
                        types.ListToolsResult.model_validate(
                            catalog.json()["result"]
                        ).tools,
                    )
                    await self.check_queries(http, client, first, second, task)
                    await self.check_diagnostics(http, first)
                    await self.check_console_lifecycle(http, first, second)
                    await self.check_console_document_cases(http, first)

    async def query(self, http, client, root):
        arguments = {
            "sql": SQL,
            "result_delivery": "inline",
            "project_root": str(root),
        }
        web = await self.console(http, root, "query_run", arguments)
        mcp = await client.call_tool("query_run", arguments)
        self.assertFalse(mcp.is_error, mcp.structured_content)
        return web, mcp.structured_content

    async def check_diagnostics(self, http, root):
        status = await self.console(
            http, root, "iwe_console_status", {"include_health": True}
        )
        self.assertEqual("live_index", status["mode"])
        self.assertEqual("ready", status["health"]["state"])
        self.assertGreaterEqual(status["indexed_atom_count"], 2)
        self.assertEqual(0, status["ingestion_issue_count"])
        self.assertEqual({"active", "latest"}, set(status["worker_runs"]))

    async def check_queries(self, http, client, first, second, task):
        first_results = await self.query(http, client, first)
        second_results = await self.query(http, client, second)
        first_rows = [
            ["EX-S-1", "Declare Example"],
            ["EX-T-1", "Example task"],
        ]
        second_rows = [
            ["EX-S-1", "Declare Example"],
            ["EX-T-1", "Second task"],
        ]
        for result in first_results:
            self.assertEqual(first_rows, result["rows"])
        for result in second_results:
            self.assertEqual(second_rows, result["rows"])
        self.assertNotEqual(
            first_results[1]["query_id"], second_results[1]["query_id"]
        )
        self.assertNotEqual(self.instances[first], self.instances[second])
        stale = await self.tool_rest(
            http, second, "query_run", {"sql": SQL}, self.instances[first]
        )
        self.assertEqual("project_declarations_stale", stale["error"]["code"])
        task.write_text(
            task.read_text().replace("Second task", "Changed second task")
        )
        second_rows[1][1] = "Changed second task"
        async with asyncio.timeout(30):
            while True:
                results = await self.query(http, client, second)
                if all(result["rows"] == second_rows for result in results):
                    break
                await asyncio.sleep(0.2)
        for result in await self.query(http, client, first):
            self.assertEqual(first_rows, result["rows"])

    async def check_console_document_cases(self, http, first):
        driver = ENGINE / (
            "FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/SPEC_ENGINE_C75__tests/"
            "functional/console_case_driver.py"
        )
        env = {**os.environ, "PYTHONPATH": str(ENGINE)}
        output = subprocess.check_output(
            [sys.executable, "-B", str(driver), "forward_console_document"],
            env=env,
            text=True,
            timeout=45,
        )
        cases = json.loads(output)["forward_console_document"]
        self.assertEqual(
            {"current", "exact", "wrong_project"},
            {case["name"] for case in cases},
        )
        await self.check_document_case_results(http, first, cases)

    async def check_document_case_results(self, http, first, cases):
        for case in cases:
            with self.subTest(case=case["name"]):
                binding, inputs = case["binding"], case["input"]
                method, route = binding["endpoint"].split(" ", 1)
                self.assertEqual(
                    ("POST", "http", "interface"),
                    (method, binding["transport"], binding["route_name"]),
                )
                target, outcome, expected = case["effect"]
                self.assertEqual("C21.console_document", target)
                response = await http.request(
                    method,
                    route.format(project_name=inputs["project_name"]),
                    json={
                        "project_root": str(first),
                        "operation": binding["tool"],
                        "arguments": {"ref_id": inputs["ref_id"]},
                    },
                )
                self.assertEqual(
                    expected["status"], response.status_code, response.text
                )
                self.assertEqual(
                    "returned" if response.is_success else "refused", outcome
                )
                if "exact_ref" in expected:
                    self.assertEqual(
                        expected["exact_ref"], response.json()["exact_ref"]
                    )

    async def tool_rest(self, http, root, name, arguments, instance):
        response = await http.post(
            "/",
            json={
                "name": name,
                "arguments": {**arguments, "project_root": str(root)},
                "session_id": None,
                "public_base_url": None,
            },
            headers={"X-Anechoic-Project-Instance": instance}
            if instance
            else {},
        )
        self.assertEqual(200, response.status_code, response.text)
        return response.json()

    async def console(self, http, root, operation, arguments):
        instance = self.instances.get(root)
        response = await self.tool_rest(
            http, root, operation, arguments, instance
        )
        self.assertIn("result", response, response)
        receipt = response["project"]["instance_id"]
        self.assertRegex(receipt, r"^[a-f0-9]{64}$")
        if instance is None:
            self.instances[root] = receipt
        else:
            self.assertEqual(instance, receipt)
        return response["result"]["value"]


if __name__ == "__main__":
    unittest.main()
