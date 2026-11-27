"""Check the packaged single-Project HTTP runtime."""

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

from MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__shared import (
    HEALTH_PATH,
    MCP_PATH,
)
from .FEATURE_MCP__tests__shared import CONTROL, project
from .workbench_docker_support import (
    defer_container_cleanup,
    docker_deadline_env,
    image_timeout,
    observing,
)


class PackagedProjectHttpTests(unittest.IsolatedAsyncioTestCase):
    async def test_current_mcp_serves_pages_across_sessions(self):
        image = os.environ.get("ANECHOIC_IMAGE", "")
        self.assertRegex(
            image,
            r"\Asha256:[0-9a-f]{64}\Z",
            "Require the immutable candidate image ID",
        )
        image_environment = self._docker(
            "image", "inspect", "--format", "{{json .Config.Env}}", image
        )
        self.assertIn("ANECHOIC_RUNTIME_STACK=current", json.loads(image_environment))
        root = Path(
            self.enterContext(
                tempfile.TemporaryDirectory(prefix="anechoic-project-http-")
            )
        ).resolve()
        subprocess.run(
            ["git", "init", "--quiet", str(root)],
            check=True,
            timeout=image_timeout(10),
        )
        project(root)
        url = self._start(image, root)
        try:
            timeout = httpx2.Timeout(image_timeout(5), read=image_timeout(30))
            async with httpx2.AsyncClient(trust_env=False, timeout=timeout) as http:
                await self._ready(http, url)
                query_id = await self._first_page(http, url)
                processes = await asyncio.to_thread(
                    self._docker, "top", self.container, "-eo", "pid,args"
                )
                mcp_processes = [
                    line for line in processes.splitlines()
                    if "-m MCP_PATCHBAY_C21.FEATURE_MCP.server" in line
                    and "--transport streamable-http" in line
                ]
                self.assertEqual(1, len(mcp_processes), processes)
                await self._assert_page(http, url, query_id)
        except Exception:
            with suppress(OSError, subprocess.SubprocessError, AssertionError):
                print(self._docker("logs", "--tail", "45", self.container), file=sys.stderr)
            raise

    def _docker(self, *arguments, timeout=10):
        result = subprocess.run(
            ["docker", *arguments],
            capture_output=True,
            text=True,
            timeout=image_timeout(timeout),
        )
        if result.returncode:
            self.fail(
                f"docker {arguments[0]} failed ({result.returncode}): {result.stdout}{result.stderr}"
            )
        return (
            result.stdout.strip()
            if arguments[0] != "logs"
            else result.stdout + result.stderr
        )

    def _start(self, image, root):
        name = f"anechoic-project-http-{uuid4().hex}"
        defer_container_cleanup(self.addCleanup, name)
        self.container = self._docker(
            "run",
            "--detach",
            "--pull=never",
            "--init",
            "--read-only",
            "--name",
            name,
            "--label",
            "anechoic.test=project-http",
            "--cap-drop",
            "ALL",
            "--security-opt",
            "no-new-privileges:true",
            "--tmpfs",
            "/tmp:rw,nosuid,nodev,size=256m",
            "--pids-limit",
            "128",
            "--cpus",
            "1",
            "--publish",
            "127.0.0.1::8092",
            "--mount",
            f"type=bind,src={root},dst=/project",
            "--env",
            "ANECHOIC_RUNTIME_NAMESPACE=docker",
            "--env",
            f"ANECHOIC_CONTROL_ROOT={CONTROL}",
            "--env",
            docker_deadline_env(),
            image,
            "mcp-http",
            timeout=45,
        )
        self.assertRegex(self.container, r"\A[0-9a-f]{64}\Z")
        binding = self._docker("port", self.container, "8092/tcp")
        self.assertRegex(binding, r"\A127\.0\.0\.1:[0-9]+\Z")
        return f"http://{binding}"

    async def _ready(self, http, url, *, deadline_seconds=90):
        deadline = monotonic() + deadline_seconds
        while await asyncio.to_thread(observing, self.container, deadline):
            try:
                response = await http.get(
                    url + HEALTH_PATH, timeout=image_timeout(2)
                )
                if (
                    response.status_code == 200
                    and response.json()["state"] == "ready"
                ):
                    return
            except httpx2.TransportError, ValueError, KeyError:
                pass
            await asyncio.sleep(0.2)
        self.fail(f"Candidate did not become ready at {url + HEALTH_PATH}")

    async def _mcp_call(self, http, url, operation, arguments):
        async with asyncio.timeout(image_timeout(60)):
            async with (
                streamable_http_client(
                    url + MCP_PATH, http_client=http
                ) as streams,
                ClientSession(*streams) as session,
            ):
                await session.initialize()
                reply = await session.call_tool(operation, arguments)
        self.assertFalse(
            reply.is_error, reply.structured_content or reply.content
        )
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
        page = await self._mcp_call(
            http,
            url,
            "query_page",
            {
                "query_id": query_id,
                "offset": 1,
                "page_size": 1,
                "result_delivery": "inline",
            },
        )
        self.assertEqual((query_id, [[200]]), (page["query_id"], page["rows"]))
