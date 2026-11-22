"""Shared MCP isolation against the exact disposable candidate image."""

import asyncio
from contextlib import suppress
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
from urllib.request import ProxyHandler, build_opener
from uuid import uuid4

import httpx2
from mcp.client.session import ClientSession
from mcp.client.streamable_http import streamable_http_client

from . import test_native_startup as fixture
from MCP_PATCHBAY_C21.FEATURE_MCP.http_paths import HEALTH_PATH, MCP_PATH


class SharedCandidateCases:
    def test_shared_candidate_isolates_projects_and_recovers_after_refusal(self):
        directory = self.enterContext(tempfile.TemporaryDirectory(prefix="shared-candidate-"))
        host = Path(directory).resolve()
        projects = self._shared_projects(host)
        endpoint = self._start_shared_candidate(host, projects)
        try:
            asyncio.run(self._check_shared_projects(endpoint, projects, host))
        except Exception:
            with suppress(OSError, subprocess.SubprocessError):
                logs = subprocess.run(
                    ["docker", "logs", "--tail", "60", self._shared_candidate_container],
                    timeout=10, capture_output=True, text=True, check=True,
                )
                print(logs.stdout + logs.stderr, file=sys.stderr)
            raise

    def _shared_projects(self, host):
        projects = host / "projects"
        for name in ("alpha", "beta"):
            project = projects / name
            project.mkdir(parents=True)
            subprocess.run(["git", "init", "--quiet", str(project)], check=True)
            fixture.RuntimeSelectionTests.manifest(
                None, project / f"_anechoic_{name}", name=name,
                prefix=name.upper(), component="C00",
                parameters={"project": {"root": {"prefix": "underscore"}}},
            )
        return projects

    def _start_shared_candidate(self, host, projects):
        image = os.environ.get("ANECHOIC_IMAGE", "")
        self.assertRegex(image, r"\Asha256:[0-9a-f]{64}\Z")
        settings = host / "MCP_PATCHBAY_C21.FEATURE_MCP.docker.runtime.toml"
        settings.write_text(
            "schema_version = 1\n[shared_mcp]\n"
            f"projects_root={json.dumps(str(projects))}\nhttp_port=8092\n",
            encoding="utf-8",
        )
        name = "anechoic-shared-candidate-" + uuid4().hex
        self.addCleanup(subprocess.run, ["docker", "rm", "-f", name],
                        timeout=30, check=True, capture_output=True)
        container = subprocess.check_output([
            "docker", "run", "--detach", "--pull=never", "--init", "--read-only",
            "--name", name, "--label", "anechoic.test=shared-candidate",
            "--cap-drop", "ALL", "--security-opt", "no-new-privileges:true",
            "--tmpfs", "/tmp:size=128m,mode=1777", "--memory", "1536m",
            "--publish", "127.0.0.1::8092", "--mount", f"type=bind,src={host},dst={host}",
            "-e", f"ANECHOIC_HOST_SETTINGS={settings}", image, "shared-mcp",
        ], timeout=40, text=True).strip()
        self.assertRegex(container, r"\A[a-f0-9]{64}\Z")
        self._shared_candidate_container = container
        binding = subprocess.check_output(
            ["docker", "port", container, "8092/tcp"], timeout=10, text=True,
        ).strip()
        self.assertRegex(binding, r"\A127\.0\.0\.1:[0-9]+\Z")
        base = f"http://{binding}"
        self._wait_shared_ready(base, container)
        return base + MCP_PATH

    def _wait_shared_ready(self, base, container):
        opener = build_opener(ProxyHandler({}))
        deadline = time.monotonic() + 55
        while time.monotonic() < deadline:
            try:
                with opener.open(base + HEALTH_PATH, timeout=2) as response:
                    if json.load(response)["ready"] is True:
                        return
            except (OSError, ValueError, KeyError):
                pass
            time.sleep(.3)
        logs = subprocess.run(["docker", "logs", "--tail", "20", container],
                              timeout=10, check=True, capture_output=True, text=True)
        self.fail(f"Disposable shared runtime did not become ready: {logs.stdout}{logs.stderr}")

    async def _check_shared_projects(self, endpoint, projects, host):
        timeout = httpx2.Timeout(5.0, read=60.0)
        async with asyncio.timeout(60), httpx2.AsyncClient(trust_env=False, timeout=timeout) as http:
            async with streamable_http_client(endpoint, http_client=http) as streams, ClientSession(*streams) as session:
                await session.initialize()
                tool = next(tool for tool in (await session.list_tools()).tools if tool.name == "query_run")
                self.assertIn("project_root", tool.input_schema["required"])
                await self._assert_project_queries(session, projects)
                self._assert_project_processes(projects)
                for arguments in (
                    {},
                    {"project_root": str(host)},
                    {"project_root": "relative/path"},
                    {"project_root": str(projects / "alpha"), "caller_context": {"session_id": ""}},
                ):
                    with self.subTest(arguments=arguments):
                        result = await session.call_tool("query_run", {
                            "sql": "SELECT 1", "result_delivery": "inline", **arguments,
                        })
                        self.assertTrue(result.is_error, result.structured_content)
                await self._assert_project_queries(session, projects)

    def _assert_project_processes(self, projects):
        listing = subprocess.check_output(
            ["docker", "top", self._shared_candidate_container, "-eo", "pid,ppid,args"],
            timeout=10, text=True,
        )
        processes = [line.split(None, 2) for line in listing.splitlines()[1:]]
        mcp, = [pid for pid, _, command in processes if "/shared_http_server.py" in command]
        coordinator, = [(pid, parent) for pid, parent, command in processes
                        if "FEATURE_WORKBENCH_BACKEND.shared_backend_process" in command]
        self.assertEqual(mcp, coordinator[1], listing)
        self.assertFalse(any("FEATURE_WORKBENCH_BACKEND.project_admission" in command
                             for _, _, command in processes), listing)
        backends = [(pid, parent, command) for pid, parent, command in processes
                    if "FEATURE_WORKBENCH_BACKEND.backend_process" in command]
        kernels = [(pid, parent, command) for pid, parent, command in processes
                   if "KERNEL_MIXER_C59.kernel_process" in command]
        self.assertEqual(2, len(backends), listing)
        self.assertEqual(2, len(kernels), listing)
        self.assertEqual({coordinator[0]}, {parent for _, parent, _ in backends}, listing)
        self.assertEqual({pid for pid, _, _ in backends}, {parent for _, parent, _ in kernels}, listing)
        kernel_pids = {pid for pid, _, _ in kernels}
        self.assertTrue(all("manifest_compiler_CS1." in command for _, parent, command in processes
                            if parent in kernel_pids), listing)
        for name in ("alpha", "beta"):
            pid, = (pid for pid, _, command in backends if str(projects / name) in command)
            self.assertTrue(any(parent == pid and str(projects / name) in command for _, parent, command in kernels), listing)

    async def _assert_project_queries(self, session, projects):
        async def query(name):
            return await session.call_tool("query_run", {
                "project_root": str(projects / name),
                "caller_context": {"session_id": "candidate-" + name},
                "sql": "SELECT reference FROM atoms ORDER BY reference LIMIT 1",
                "result_delivery": "inline", "result_format": "json_matrix",
            })
        results = await asyncio.gather(*(query(name) for name in ("alpha", "beta")))
        for name, result in zip(("alpha", "beta"), results, strict=True):
            self.assertFalse(result.is_error, result.structured_content)
            self.assertEqual([[f"{name.upper()}-S-001"]], result.structured_content["rows"])
