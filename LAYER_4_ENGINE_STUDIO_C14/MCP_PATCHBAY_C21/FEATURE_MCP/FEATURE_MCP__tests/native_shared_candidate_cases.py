"""Shared MCP isolation against the exact disposable candidate image."""

import asyncio
from contextlib import suppress
import json
import os
import shlex
from pathlib import Path
import subprocess
import sys
import tempfile
import time
from urllib.error import HTTPError
from urllib.request import ProxyHandler, build_opener
from uuid import uuid4

import httpx2
from mcp.client.session import ClientSession
from mcp.client.streamable_http import streamable_http_client

from .FEATURE_MCP__tests__shared import write_manifest
from .native_shared_core_recovery import KILL_CHILD, assert_core_recovery
from .workbench_docker_support import defer_container_cleanup, docker_deadline_env, image_timeout, observing
from MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__shared import HEALTH_PATH, MCP_PATH


_MCP_MODULE = "MCP_PATCHBAY_C21.FEATURE_MCP.shared_http_server"
_BETA_BACKEND_MODULE = "API_MIXER_beta_C91.shared_runtime"


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
                    timeout=image_timeout(10), capture_output=True, text=True, check=True,
                )
                print(logs.stdout + logs.stderr, file=sys.stderr)
            raise

    def _shared_projects(self, host):
        projects = host / "projects"
        for name in ("alpha", "beta"):
            project = projects / name
            project.mkdir(parents=True)
            subprocess.run(["git", "init", "--quiet", str(project)], check=True)
            write_manifest(
                None, project / f"_anechoic_{name}", name=name,
                prefix=name.upper(), component="C00",
                parameters={"project": {"root": {"prefix": "underscore"}}},
            )
        return projects

    def _start_shared_candidate(self, host, projects):
        image = os.environ.get("ANECHOIC_IMAGE", "")
        self.assertRegex(image, r"\Asha256:[0-9a-f]{64}\Z")
        environment = subprocess.check_output(
            ["docker", "image", "inspect", "--format", "{{json .Config.Env}}", image],
            timeout=image_timeout(10), text=True,
        )
        env = set(json.loads(environment))
        self._shared_candidate_beta_next = "ANECHOIC_RUNTIME_STACK=beta_next" in env
        self._shared_candidate_beta = self._shared_candidate_beta_next
        self._backend_module = _BETA_BACKEND_MODULE
        defaults = '\n[project_defaults]\nworkbench_storage="memory"\n' if self._shared_candidate_beta else ""
        settings = host / "MCP_PATCHBAY_C21.FEATURE_MCP.docker.runtime.toml"
        settings.write_text(
            "schema_version = 1\n[shared_mcp]\n"
            f"projects_root={json.dumps(str(projects))}\nhttp_port=8092\n{defaults}",
            encoding="utf-8",
        )
        name = "anechoic-shared-candidate-" + uuid4().hex
        defer_container_cleanup(self.addCleanup, name)
        container = subprocess.check_output([
            "docker", "run", "--detach", "--pull=never", "--init", "--read-only",
            "--name", name, "--label", "anechoic.test=shared-candidate",
            "--cap-drop", "ALL", "--security-opt", "no-new-privileges:true",
            "--tmpfs", "/tmp:size=128m,mode=1777", "--memory", "1536m",
            "--publish", "127.0.0.1::8092", "--mount", f"type=bind,src={host},dst={host}",
            *(["-e", "ANECHOIC_RUNTIME_PROFILE=test"] if self._shared_candidate_beta_next else []),
            "-e", f"ANECHOIC_HOST_SETTINGS={settings}", "-e", docker_deadline_env(), image, "shared-mcp",
        ], timeout=image_timeout(40), text=True).strip()
        self.assertRegex(container, r"\A[a-f0-9]{64}\Z")
        self._shared_candidate_container = container
        binding = subprocess.check_output(
            ["docker", "port", container, "8092/tcp"], timeout=image_timeout(10), text=True,
        ).strip()
        self.assertRegex(binding, r"\A127\.0\.0\.1:[0-9]+\Z")
        base = f"http://{binding}"
        self._wait_shared_ready(base, container)
        return base + MCP_PATH

    def _wait_shared_ready(self, base, container):
        opener = build_opener(ProxyHandler({}))
        deadline = time.monotonic() + 55
        while observing(container, deadline):
            try:
                with opener.open(base + HEALTH_PATH, timeout=image_timeout(2)) as response:
                    if json.load(response)["state"] == "ready":
                        return
            except HTTPError as error:
                error.close()
            except (OSError, ValueError, KeyError):
                pass
            time.sleep(.3)
        logs = subprocess.run(["docker", "logs", "--tail", "20", container],
                              timeout=image_timeout(10), check=True, capture_output=True, text=True)
        self.fail(f"Disposable shared runtime did not become ready: {logs.stdout}{logs.stderr}")

    async def _check_shared_projects(self, endpoint, projects, host):
        timeout = httpx2.Timeout(image_timeout(5.0), read=image_timeout(60.0))
        async with asyncio.timeout(image_timeout(180)), httpx2.AsyncClient(trust_env=False, timeout=timeout) as http:
            async with streamable_http_client(endpoint, http_client=http) as streams, ClientSession(*streams) as session:
                await session.initialize()
                tool = next(tool for tool in (await session.list_tools()).tools if tool.name == "query_run")
                self.assertIn("project_root", tool.input_schema["required"])
                query_ids = await self._assert_project_queries(session, projects)
                beta = self._assert_project_processes(projects)
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
            if beta is not None:
                await self._assert_shared_restarts(endpoint, projects, http, query_ids, beta)
                await assert_core_recovery(self, endpoint, projects, http, query_ids)

    def _processes(self):
        listing = subprocess.check_output(
            ["docker", "top", self._shared_candidate_container, "-eo", "pid,ppid,args"],
            timeout=image_timeout(10), text=True,
        )
        return [line.split(None, 2) for line in listing.splitlines()[1:]], listing

    def _assert_project_processes(self, projects):
        processes, listing = self._processes()
        mcp = self._one(processes, _MCP_MODULE, listing)
        beta = [item for item in processes if self._backend_module in item[2]]
        current = [item for item in processes if "FEATURE_IWE_CONSOLE_BACKEND.shared_backend_process" in item[2]]
        self.assertEqual(1, len(beta) + len(current), listing)
        self.assertEqual(self._shared_candidate_beta, bool(beta), listing)
        if beta:
            backend = beta[0]
            owner_module = "ORCHESTRATOR_beta_C68.shared_peer_owner"
            owner = self._one(processes, owner_module, listing)
            self.assertEqual({mcp[1]}, {backend[1], owner[1]}, listing)
            self.assertTrue(any(pid == mcp[1] and "docker/entrypoint.py" in command
                                for pid, _, command in processes), listing)
            peer_processes = self._assert_beta_processes(processes, backend[0], owner[0], listing)
            return {_MCP_MODULE: mcp[0], self._backend_module: backend[0], "peer_processes": peer_processes}
        backend = current[0]
        self.assertEqual(mcp[0], backend[1], listing)
        self._assert_current_processes(processes, backend[0], projects, listing)

    def _restart_shared_child(self, endpoint, module, old_pid):
        container = self._shared_candidate_container
        subprocess.run(["docker", "exec", container, "python", "-B", "-c", KILL_CHILD, module],
                       timeout=image_timeout(10), check=True, capture_output=True, text=True)
        deadline = time.monotonic() + 15
        while observing(container, deadline):
            processes, listing = self._processes()
            if any(pid != old_pid and module in command for pid, _, command in processes):
                self._wait_shared_ready(endpoint.removesuffix(MCP_PATH), container)
                return
            time.sleep(.1)
        self.fail(f"Shared runtime did not replace {module}: {listing}")

    async def _assert_shared_restarts(self, endpoint, projects, http, query_ids, previous):
        for module in (self._backend_module, _MCP_MODULE):
            with self.subTest(restarted=module):
                await asyncio.to_thread(self._restart_shared_child, endpoint, module, previous[module])
                async with streamable_http_client(endpoint, http_client=http) as streams, ClientSession(*streams) as session:
                    await session.initialize()
                    for name, query_id in query_ids.items():
                        result = await session.call_tool("query_page", {
                            "project_root": str(projects / name),
                            "caller_context": {"session_id": "candidate-" + name},
                            "query_id": query_id, "offset": 0, "page_size": 1, "result_delivery": "inline",
                        })
                        self.assertFalse(result.is_error, result.structured_content)
                        self.assertEqual([[f"{name.upper()}-S-001"]], result.structured_content["rows"])
                current = self._assert_project_processes(projects)
                self.assertNotEqual(previous[module], current[module])
                self.assertEqual(previous | {module: current[module]}, current)
                previous = current

    def _one(self, processes, role, listing):
        matches = [item for item in processes if role in item[2]]
        self.assertEqual(1, len(matches), listing)
        return matches[0]

    def _assert_current_processes(self, processes, coordinator, projects, listing):
        self.assertFalse(any("FEATURE_IWE_CONSOLE_BACKEND.project_admission" in command
                             for _, _, command in processes), listing)
        backends = [item for item in processes if "FEATURE_IWE_CONSOLE_BACKEND.backend_process" in item[2]]
        kernels = [item for item in processes if "KERNEL_MIXER_C59.kernel_process" in item[2]]
        self.assertEqual(2, len(backends), listing)
        self.assertEqual(2, len(kernels), listing)
        self.assertEqual({coordinator}, {parent for _, parent, _ in backends}, listing)
        self.assertEqual({pid for pid, _, _ in backends}, {parent for _, parent, _ in kernels}, listing)
        kernel_pids = {pid for pid, _, _ in kernels}
        self.assertTrue(all("manifest_compiler_CS1." in command for _, parent, command in processes
                            if parent in kernel_pids), listing)
        for name in ("alpha", "beta"):
            backend = self._one(backends, str(projects / name), listing)
            self.assertTrue(any(parent == backend[0] and str(projects / name) in command
                                for _, parent, command in kernels), listing)

    def _assert_beta_processes(self, processes, backend, owner, listing):
        admissions = [item for item in processes if "FEATURE_MODEL_VALIDATION.project_admission__pub" in item[2]]
        admission_parents = {parent for _, parent, _ in admissions}
        self.assertEqual({owner}, admission_parents, listing)
        self.assertEqual(len(admissions), len(admission_parents), listing)
        worker = self._one([item for item in processes if item[1] == owner],
                           "WORKERS_beta_C69.warm_worker", listing)
        kernels = [item for item in processes if "DATABASE_SERVER_beta_C71.DATABASE_SERVER_beta_C71__shared" in item[2]]
        orchestrators = [item for item in processes if "ORCHESTRATOR_beta_C68.ORCHESTRATOR_beta_C68__shared" in item[2]]
        self.assertEqual(2, len(kernels), listing)
        self.assertEqual(2, len(orchestrators), listing)
        self.assertEqual({owner}, {parent for _, parent, _ in kernels + orchestrators}, listing)
        self.assertTrue(all("--database-path" not in command for _, _, command in kernels), listing)
        def option(command, name):
            words = shlex.split(command)
            return words[words.index(name) + 1]
        kernel_ids = {option(command, "--instance-id"): option(command, "--socket")
                      for _, _, command in kernels}
        orchestrator_ids = {option(command, "--instance-id"): option(command, "--database-socket")
                            for _, _, command in orchestrators}
        self.assertEqual(2, len(kernel_ids), listing)
        self.assertEqual(kernel_ids, orchestrator_ids, listing)
        self.assertEqual({option(worker[2], "--socket")},
                         {option(command, "--worker-socket") for _, _, command in orchestrators}, listing)
        self.assertTrue(all(float(option(command, "--worker-load-seconds")) > 0
                            for _, _, command in orchestrators), listing)
        return {owner, worker[0], *(pid for pid, _, _ in kernels + orchestrators)}

    async def _assert_project_queries(self, session, projects):
        async def query(name):
            return await session.call_tool("query_run", {
                "project_root": str(projects / name),
                "caller_context": {"session_id": "candidate-" + name},
                "sql": "SELECT reference FROM atoms ORDER BY reference LIMIT 1",
                "result_delivery": "inline", "result_format": "json_matrix",
            })
        names = ("alpha", "beta")
        results = dict(zip(names, await asyncio.gather(*(query(name) for name in names)), strict=True))
        for name, result in results.items():
            self.assertFalse(result.is_error, result.structured_content)
            self.assertEqual([[f"{name.upper()}-S-001"]], result.structured_content["rows"])
        return {name: result.structured_content["query_id"] for name, result in results.items()}
