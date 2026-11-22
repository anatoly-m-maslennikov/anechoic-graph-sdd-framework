"""Run the ordinary MCP entry point with only the Beta runtime Components."""

import asyncio
from pathlib import Path
import shutil
import sys
from tempfile import TemporaryDirectory
import unittest

from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

ENGINE = Path(__file__).resolve().parents[3]
COMPONENTS = ("FEATURE_PROGRAMMATIC", "MCP_PATCHBAY_C21", "KERNEL_MIXER_beta_C67",
              "ORCHESTRATOR_beta_C68", "WORKERS_beta_C69", "WORKBENCH_BACKEND_beta_C70")


def _stage(root):
    engine = root / ENGINE.name
    for component in COMPONENTS:
        shutil.copytree(ENGINE / component, engine / component, ignore=shutil.ignore_patterns(
            "__pycache__", "*__tests", ".venv*", "node_modules", "fixtures", ".git",
        ))
    (root / "project.toml").write_text('stack = "beta"\n', encoding="utf-8")
    return engine


def _project(root):
    control = root / "_anechoic_example"
    control.mkdir(parents=True)
    (control / "EX-S-1-PROJECT_MANIFEST--declare-example.md").write_text(
        "---\natom_family: SPEC\natom_id: EX-S-1\ncontainer:\n  component: C00\ntier: -1\n"
        "context:\n  template: project_manifest\n  lens: SPEC\nstate:\n  status: active\n  version: 1\n"
        "  updated_at: '2026-11-19T00:00:00Z'\n---\n\n## Summary\n\nDeclare Example\n\n"
        "## Claim\n\n### Formal Claim\n\n```python\n"
        "from anechoic.formal_claims import declare_entity\n"
        "from anechoic.model import ProjectManifest\n"
        "declare_entity(entity_name='Project Manifest', instance=ProjectManifest(name='Example', prefix='EX'))\n```\n",
        encoding="utf-8",
    )
    task = control / "001_TICKETS/TASKS/EX-T-1-TASK--example.md"
    task.parent.mkdir(parents=True)
    task.write_text(
        "---\natom_family: TKT\natom_id: EX-T-1\ncontainer:\n  component: C00\npriority: 2\n"
        "context:\n  template: task\nstate:\n  status: active\n  version: 1\n"
        "  updated_at: '2026-11-19T00:00:00Z'\n---\n\n## Summary\n\nExample task\n",
        encoding="utf-8",
    )


class BetaMcpTest(unittest.IsolatedAsyncioTestCase):
    async def test_one_selected_project_query(self):
        with TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            engine = _stage(root / "framework")
            project = root / "project"
            _project(project)
            parameters = StdioServerParameters(
                command=sys.executable,
                args=["-B", "-P", "-m", "MCP_PATCHBAY_C21.FEATURE_MCP.server", "--project-root", str(project)],
                cwd=engine.parent, env={"PYTHONPATH": str(engine)},
            )
            async with asyncio.timeout(90), stdio_client(parameters) as streams, ClientSession(*streams) as client:
                await client.initialize()
                tools = (await client.list_tools()).tools
                self.assertEqual(["query_run"], [tool.name for tool in tools])
                query = {"sql": "SELECT reference, summary FROM atoms ORDER BY reference"}
                reply = await client.call_tool("query_run", query)
                self.assertFalse(reply.is_error, reply.structured_content)
                self.assertEqual([["EX-S-1", "Declare Example"], ["EX-T-1", "Example task"]],
                                 reply.structured_content["rows"])
                reply = await client.call_tool("query_run", {**query, "project_root": str(root)})
                self.assertTrue(reply.is_error)


if __name__ == "__main__":
    unittest.main()
