"""Exercise the candidate Project MCP stdio transport and peer cleanup."""

import asyncio
import os
from pathlib import Path
import sys
import tempfile
import unittest

import httpx2
from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client
from mcp.shared.exceptions import MCPError

from MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__shared import (
    select_runtime_project,
)
from .test_beta_next_query_comparison import project

ENGINE = Path(__file__).resolve().parents[3]


def parameters(fixture, *, profile="dev-local"):
    env = {
        **os.environ,
        "PYTHONPATH": str(ENGINE),
        "ANECHOIC_RUNTIME_STACK": "beta_next",
        "ANECHOIC_RUNTIME_PROFILE": profile,
        "PYTHONDONTWRITEBYTECODE": "1",
        "ANECHOIC_DUCKPGQ_EXTENSION_DIRECTORY": os.environ.get(
            "ANECHOIC_DUCKPGQ_EXTENSION_DIRECTORY",
            str(ENGINE.parent / ".anechoic_tmp/workbench/extensions"),
        ),
    }
    return StdioServerParameters(
        command=sys.executable,
        args=[
            "-B",
            "-P",
            "-m",
            "MCP_PATCHBAY_C21.FEATURE_MCP.server",
            "--project-root",
            str(fixture),
        ],
        cwd=ENGINE.parent,
        env=env,
    )


def find_runtime(before, instance):
    for directory in (
        set(Path("/tmp").resolve().glob("anechoic-api-*")) - before
    ):
        socket = directory / "api.sock"
        if not socket.is_socket():
            continue
        try:
            with httpx2.Client(
                transport=httpx2.HTTPTransport(uds=str(socket)),
                base_url="http://private",
                timeout=1,
                trust_env=False,
            ) as http:
                if http.get("/health").json().get("instance_id") == instance:
                    return directory
        except httpx2.HTTPError, OSError, ValueError:
            pass
    raise AssertionError("The selected Project runtime was not found")


class BetaNextStdioTests(unittest.IsolatedAsyncioTestCase):
    async def test_real_mcp_query_and_eof_cleans_peers(self):
        with tempfile.TemporaryDirectory(dir="/tmp") as temporary:
            fixture = Path(temporary).resolve() / "project"
            project(fixture)
            instance = select_runtime_project(fixture).instance_id
            before = set(Path("/tmp").resolve().glob("anechoic-api-*"))
            async with (
                asyncio.timeout(120),
                stdio_client(parameters(fixture)) as streams,
                ClientSession(*streams) as client,
            ):
                await client.initialize()
                names = {
                    tool.name for tool in (await client.list_tools()).tools
                }
                self.assertTrue(
                    {
                        "query_run",
                        "query_schema",
                        "atom_lifecycle_create_draft",
                    }
                    <= names
                )
                reply = await client.call_tool(
                    "query_run",
                    {
                        "sql": 'SELECT reference, "content.summary" FROM atoms ORDER BY reference',
                        "result_delivery": "inline",
                    },
                )
                self.assertFalse(reply.is_error, reply.structured_content)
                self.assertEqual(
                    [
                        ["EX-S-1", "Declare Example"],
                        ["EX-T-1", "Example task"],
                    ],
                    reply.structured_content["rows"],
                )
                runtime = find_runtime(before, instance)
            self.assertFalse(
                runtime.exists(),
                "EOF must close both peers and remove the runtime directory",
            )

    async def test_invalid_runtime_profile_refuses_stdio_startup(self):
        with tempfile.TemporaryDirectory(dir="/tmp") as temporary:
            fixture = Path(temporary).resolve() / "project"
            project(fixture)
            async with (
                asyncio.timeout(90),
                stdio_client(
                    parameters(fixture, profile="invalid")
                ) as streams,
            ):
                async with ClientSession(*streams) as client:
                    with self.assertRaises(MCPError):
                        await client.initialize()


if __name__ == "__main__":
    unittest.main()
