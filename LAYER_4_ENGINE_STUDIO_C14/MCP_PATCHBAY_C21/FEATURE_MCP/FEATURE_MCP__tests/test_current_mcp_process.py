"""Exercise stdio using a source closure that contains only Current."""

import asyncio
import os
from pathlib import Path
import shutil
import sys
from tempfile import TemporaryDirectory
import unittest

from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

from .example_project import project


ENGINE = Path(__file__).resolve().parents[3]
COMPONENTS = (
    "FEATURE_PROGRAMMATIC",
    "ARCHITECTURE_ANALYSIS_C73",
    "MCP_PATCHBAY_C21",
    "KERNEL_MIXER_C59",
    "IWE_CONSOLE_C43",
)


def stage_current(root):
    engine = root / ENGINE.name
    for component in COMPONENTS:
        shutil.copytree(
            ENGINE / component,
            engine / component,
            ignore=shutil.ignore_patterns(
                "__pycache__", "*__tests", ".venv*", "node_modules",
                "fixtures", ".git",
            ),
        )
    return engine


class CurrentMcpTest(unittest.IsolatedAsyncioTestCase):
    async def test_one_selected_project_query(self):
        with TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            engine = stage_current(root / "framework")
            selected = root / "project"
            project(selected)
            extension = ENGINE.parent / ".anechoic_tmp/workbench/extensions"
            parameters = StdioServerParameters(
                command=sys.executable,
                args=[
                    "-B", "-P", "-m", "MCP_PATCHBAY_C21.FEATURE_MCP.server",
                    "--project-root", str(selected),
                ],
                cwd=engine.parent,
                env={
                    "PYTHONPATH": str(engine),
                    "ANECHOIC_RUNTIME_STACK": "current",
                    "ANECHOIC_DUCKPGQ_EXTENSION_DIRECTORY": os.environ.get(
                        "ANECHOIC_DUCKPGQ_EXTENSION_DIRECTORY", str(extension)
                    ),
                },
            )
            async with (
                asyncio.timeout(90),
                stdio_client(parameters) as streams,
                ClientSession(*streams) as client,
            ):
                await client.initialize()
                tools = {tool.name for tool in (await client.list_tools()).tools}
                self.assertLessEqual(
                    {"query_run", "query_page", "workspace_open", "view_run"},
                    tools,
                )
                arguments = {
                    "sql": 'SELECT reference FROM atoms ORDER BY reference',
                    "page_size": 1,
                    "result_delivery": "inline",
                }
                result = await client.call_tool("query_run", arguments)
                self.assertFalse(result.is_error, result.structured_content)
                first = result.structured_content
                self.assertEqual([["EX-S-1"]], first["rows"])
                page = await client.call_tool(
                    "query_page",
                    {
                        "query_id": first["query_id"],
                        "offset": 1,
                        "page_size": 1,
                        "result_delivery": "inline",
                    },
                )
                self.assertFalse(page.is_error, page.structured_content)
                self.assertEqual([["EX-T-1"]], page.structured_content["rows"])
                foreign = await client.call_tool(
                    "query_run", arguments | {"project_root": str(root)}
                )
                self.assertTrue(foreign.is_error, foreign.structured_content)
