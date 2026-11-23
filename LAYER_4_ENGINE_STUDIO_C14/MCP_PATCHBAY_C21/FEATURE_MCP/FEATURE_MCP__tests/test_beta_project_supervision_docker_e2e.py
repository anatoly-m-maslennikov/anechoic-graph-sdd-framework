"""Check process recovery in the packaged single-Project HTTP runtime."""

import asyncio
from contextlib import suppress
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from time import monotonic
import unittest
from uuid import uuid4

import httpx2
from mcp.client.session import ClientSession
from mcp.client.streamable_http import streamable_http_client

from MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__shared import HEALTH_PATH, MCP_PATH
from .FEATURE_MCP__tests__shared import CONTROL, project
from .workbench_docker_support import defer_container_cleanup, docker_deadline_env, image_timeout, observing


_ROLES = {
    "mcp": ("MCP_PATCHBAY_C21.FEATURE_MCP.server", "--transport", "streamable-http"),
    "api": ("WORKBENCH_BACKEND_beta_C70.runtime", "--role", "api"),
    "peer-owner": ("WORKBENCH_BACKEND_beta_C70.runtime", "--role", "peer-owner"),
    "kernel": ("KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.DATABASE_SERVER_beta_C71__shared",),
    "orchestrator": ("ORCHESTRATOR_beta_C68.ORCHESTRATOR_beta_C68__shared",),
}
_PROCESS_PROBE = """
import json
import os
from pathlib import Path
import signal
import sys

roles = json.loads(sys.argv[1])
matches = {role: [] for role in roles}
for path in Path('/proc').glob('[0-9]*/cmdline'):
    try:
        args = [os.fsdecode(arg) for arg in path.read_bytes().split(b'\\0')]
    except (FileNotFoundError, ProcessLookupError):
        continue
    pairs = set(zip(args, args[1:]))
    for role, (module, *option) in roles.items():
        if ('-m', module) in pairs and (not option or tuple(option) in pairs):
            matches[role].append(int(path.parent.name))
if len(sys.argv) == 4:
    role, pid = sys.argv[2], int(sys.argv[3])
    if matches[role] != [pid]:
        raise RuntimeError(f'Expected one {role} process with PID {pid}, got {matches}')
    os.kill(pid, signal.SIGKILL)
print(json.dumps(matches, sort_keys=True))
"""


class PackagedProjectSupervisionTests(unittest.IsolatedAsyncioTestCase):
    async def test_candidate_http_runtime_recovers_after_process_exit(self):
        image = os.environ.get("ANECHOIC_IMAGE", "")
        self.assertRegex(image, r"\Asha256:[0-9a-f]{64}\Z", "Require the immutable candidate image ID")
        environment = self._docker("image", "inspect", "--format", "{{json .Config.Env}}", image)
        beta = "ANECHOIC_RUNTIME_STACK=beta" in json.loads(environment)
        root = Path(self.enterContext(tempfile.TemporaryDirectory(prefix="anechoic-supervision-"))).resolve()
        subprocess.run(["git", "init", "--quiet", str(root)], check=True, timeout=image_timeout(10))
        project(root)
        url = self._start(image, root)
        try:
            timeout = httpx2.Timeout(image_timeout(5), read=image_timeout(30))
            async with httpx2.AsyncClient(trust_env=False, timeout=timeout) as http:
                await self._ready(http, url)
                query_id = await self._first_page(http, url)
                previous = await asyncio.to_thread(self._processes)
                if beta:
                    for role in ("api", "mcp", "kernel", "orchestrator"):
                        previous, query_id = await self._restart(http, url, role, previous, query_id)
                else:
                    self.assertEqual({"mcp": previous["mcp"]}, {role: pids for role, pids in previous.items() if pids})
                    self.assertEqual(1, len(previous["mcp"]))
                    await self._assert_page(http, url, query_id)
                    print("Current candidate verified. Beta restart checks do not apply.", flush=True)
        except Exception:
            with suppress(OSError, subprocess.SubprocessError, AssertionError):
                print(self._docker("logs", "--tail", "45", self.container), file=sys.stderr)
            raise

    def _docker(self, *arguments, timeout=10):
        result = subprocess.run(["docker", *arguments], capture_output=True, text=True, timeout=image_timeout(timeout))
        if result.returncode:
            self.fail(f"docker {arguments[0]} failed ({result.returncode}): {result.stdout}{result.stderr}")
        return result.stdout.strip() if arguments[0] != "logs" else result.stdout + result.stderr

    def _start(self, image, root):
        name = f"anechoic-supervision-{uuid4().hex}"
        defer_container_cleanup(self.addCleanup, name)
        self.container = self._docker(
            "run", "--detach", "--pull=never", "--init", "--read-only",
            "--name", name, "--label", "anechoic.test=project-supervision",
            "--cap-drop", "ALL", "--security-opt", "no-new-privileges:true",
            "--tmpfs", "/tmp:rw,nosuid,nodev,size=256m", "--pids-limit", "128", "--cpus", "1",
            "--publish", "127.0.0.1::8092", "--mount", f"type=bind,src={root},dst=/project",
            "--env", "ANECHOIC_RUNTIME_NAMESPACE=docker", "--env", f"ANECHOIC_CONTROL_ROOT={CONTROL}",
            "--env", docker_deadline_env(), image, "mcp-http", timeout=45,
        )
        self.assertRegex(self.container, r"\A[0-9a-f]{64}\Z")
        binding = self._docker("port", self.container, "8092/tcp")
        self.assertRegex(binding, r"\A127\.0\.0\.1:[0-9]+\Z")
        return f"http://{binding}"

    def _processes(self, *signal_target):
        return json.loads(self._docker("exec", self.container, "python", "-B", "-c", _PROCESS_PROBE,
                                       json.dumps(_ROLES), *signal_target))

    async def _ready(self, http, url, *, deadline_seconds=90):
        deadline = monotonic() + deadline_seconds
        while await asyncio.to_thread(observing, self.container, deadline):
            try:
                response = await http.get(url + HEALTH_PATH, timeout=image_timeout(2))
                if response.status_code == 200 and response.json()["ready"] is True:
                    return
            except (httpx2.TransportError, ValueError, KeyError):
                pass
            await asyncio.sleep(.2)
        self.fail(f"Candidate did not become ready at {url + HEALTH_PATH}")

    async def _mcp_call(self, http, url, operation, arguments):
        async with asyncio.timeout(image_timeout(60)):
            async with streamable_http_client(url + MCP_PATH, http_client=http) as streams, ClientSession(*streams) as session:
                await session.initialize()
                reply = await session.call_tool(operation, arguments)
        self.assertFalse(reply.is_error, reply.structured_content or reply.content)
        self.assertIsInstance(reply.structured_content, dict)
        return reply.structured_content

    async def _first_page(self, http, url):
        result = await self._mcp_call(http, url, "query_run", {
            "sql": "SELECT marker FROM (VALUES (100), (200)) AS fixture(marker) ORDER BY marker",
            "result_delivery": "inline", "page_size": 1,
        })
        self.assertEqual([[100]], result["rows"])
        self.assertTrue(result["has_more"])
        return result["query_id"]

    async def _assert_page(self, http, url, query_id):
        page = await self._mcp_call(http, url, "query_page", {
            "query_id": query_id, "offset": 1, "page_size": 1, "result_delivery": "inline",
        })
        self.assertEqual((query_id, [[200]]), (page["query_id"], page["rows"]))

    def _assert_beta_processes(self, processes):
        self.assertEqual({role: 1 for role in _ROLES}, {role: len(pids) for role, pids in processes.items()}, processes)

    async def _replacement(self, role, original_pid):
        await asyncio.to_thread(self._processes, role, str(original_pid))
        deadline = monotonic() + 30
        while await asyncio.to_thread(observing, self.container, deadline):
            current = await asyncio.to_thread(self._processes)
            if len(current[role]) == 1 and current[role] != [original_pid]:
                return current[role]
            await asyncio.sleep(.2)
        self.fail(f"Candidate did not replace {role} PID {original_pid}")

    async def _restart(self, http, url, role, previous, query_id):
        self._assert_beta_processes(previous)
        original_pid, = previous[role]
        replacement = await self._replacement(role, original_pid)
        peer_restart = role in ("kernel", "orchestrator")
        await self._ready(http, url, deadline_seconds=90 if peer_restart else 30)
        current = await asyncio.to_thread(self._processes)
        self._assert_beta_processes(current)
        self.assertEqual(replacement, current[role])
        if peer_restart:
            for peer in ("kernel", "orchestrator"):
                self.assertNotEqual(previous[peer], current[peer], f"{peer} survived restart of {role}")
            fresh_id = await self._first_page(http, url)
            self.assertNotEqual(query_id, fresh_id)
            query_id = fresh_id
        else:
            self.assertEqual(previous | {role: replacement}, current)
        await self._assert_page(http, url, query_id)
        self.assertEqual(current, await asyncio.to_thread(self._processes))
        print(f"Restarted {role} PID {original_pid} as {replacement[0]}; ready processes {current}", flush=True)
        return current, query_id
