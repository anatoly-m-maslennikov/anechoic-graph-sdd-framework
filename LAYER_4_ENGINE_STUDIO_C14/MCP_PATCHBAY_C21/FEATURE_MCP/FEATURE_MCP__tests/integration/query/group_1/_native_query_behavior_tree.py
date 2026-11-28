import asyncio
import json
import sys
import tempfile
from pathlib import Path

from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

# fmt: off
from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.\
    FEATURE_PROJECT_TOOLS__tests.\
    FEATURE_PROJECT_TOOLS__tests__shared import extension_directory
# fmt: on
MCP = Path(__file__).resolve().parents[4]


class TreeCases:
    async def test_queries_the_native_tree_and_keeps_legacy_inputs_unchanged(
        self,
    ):
        self._write_tree_queries()
        before = self._carrier_digests()
        diagnostics = self.enterContext(tempfile.TemporaryFile(mode="w+t"))
        async with (
            asyncio.timeout(25),
            stdio_client(
                StdioServerParameters(
                    command=sys.executable,
                    args=self.args,
                    env={
                        "PYTHONPATH": str(MCP.parents[1]),
                        "ANECHOIC_DUCKPGQ_EXTENSION_DIRECTORY": str(
                            extension_directory(MCP.parents[2])
                        ),
                    },
                ),
                errlog=diagnostics,
            ) as streams,
            ClientSession(*streams) as client,
        ):
            await self._check_query_schema(client)
            await self._check_atom_templates(client)
            await self._check_inventory_templates(client)
            await self._check_query_pages(client)
            await self._check_query_diagnostics(client)
        self.assertEqual(before, self._carrier_digests())
        self._check_diagnostics_log(diagnostics)

    def _write_tree_queries(self):
        self._write(
            "001_TICKETS/TASKS/AN-T-010-TASK--child.md",
            "AN-T-010",
            "done",
            1,
            container={"atom": "AN-T-009"},
        )
        self._write(
            "002_PROJECT_CONFIG/CUSTOM_MODEL/AN-C-001--definition.md",
            "AN-C-001",
            "active",
            1,
            container={"atom": "AN-P-001"},
        )

    def _check_diagnostics_log(self, diagnostics):
        diagnostics.seek(0)
        output = diagnostics.read()
        self.assertNotIn("private_", output)
        records = [
            json.loads(line)
            for line in output.splitlines()
            if '"code":"query_error"' in line
        ]
        self.assertGreaterEqual(len(records), 6)
        self.assertTrue(
            all(
                row["severity"] == "WARNING" and row["outcome"] == "failed"
                for row in records
            )
        )
