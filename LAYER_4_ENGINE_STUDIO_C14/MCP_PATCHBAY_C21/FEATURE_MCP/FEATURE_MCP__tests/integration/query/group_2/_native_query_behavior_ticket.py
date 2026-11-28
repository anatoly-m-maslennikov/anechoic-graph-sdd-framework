import asyncio
import sys
from pathlib import Path

from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

# fmt: off
from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.\
    FEATURE_PROJECT_TOOLS__tests.\
    FEATURE_PROJECT_TOOLS__tests__shared import extension_directory
# fmt: on
MCP = Path(__file__).resolve().parents[4]


class TicketCases:
    async def _create_ticket(self, client, label, container, summary):
        response = await client.call_tool(
            "atom_lifecycle_create_draft",
            {
                "newAtom": {
                    "template": "task",
                    "label": label,
                    "container": container,
                    "body": f"## Summary\n\n{summary}\n",
                }
            },
        )
        result = response.structured_content
        self.assertEqual("completed", result["status"], result)
        return result["savedDraft"]

    def _write_ticket_queries(self):
        self._write(
            "001_TICKETS/TASKS/AN-T-011-EPIC--canonical.md",
            "AN-T-011",
            "active",
            1,
            label="Epic",
        )
        self._write(
            "001_TICKETS/TASKS/AN-T-012-SUB_EPIC--canonical.md",
            "AN-T-012",
            "active",
            1,
            label="Sub-epic",
        )
        self._write(
            "001_TICKETS/TASKS/AN-T-013-EPIC--legacy.md",
            "AN-T-013",
            "active",
            1,
            template="epic",
        )
        self._write(
            "001_TICKETS/TASKS/AN-T-014-TASK--custom.md",
            "AN-T-014",
            "active",
            1,
            label="Custom Group",
        )

    async def test_ticket_label_queries_and_legacy_epic_kind(self):
        self._write_ticket_queries()
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
                )
            ) as streams,
            ClientSession(*streams) as client,
        ):
            await client.initialize()
            await self._check_ticket_queries(client)

    async def _check_ticket_queries(self, client):
        async def query(**arguments):
            response = await client.call_tool(
                "query_template",
                {
                    "template": "list_tickets",
                    "result_format": "json_matrix",
                    **arguments,
                },
            )
            self.assertFalse(response.is_error, response.structured_content)
            return response.structured_content

        epics = await query(kind="epic")
        self.assertEqual(
            ["ref", "summary", "kind", "status", "path", "label"],
            [column["name"] for column in epics["columns"]],
        )
        self.assertEqual(
            {
                ("AN-T-011", "task", "Epic"),
                ("AN-T-012", "task", "Sub-epic"),
                ("AN-T-013", "epic", None),
            },
            {(row[0], row[2], row[5]) for row in epics["rows"]},
        )
        self.assertEqual(
            ["AN-T-012"],
            [row[0] for row in (await query(label="sub epic"))["rows"]],
        )
        self.assertEqual(
            ["AN-T-014"],
            [row[0] for row in (await query(label="CUSTOM-GROUP"))["rows"]],
        )
        await self._check_ticket_parent(client, query)

    async def _check_ticket_parent(self, client, query):
        parent = await self._create_ticket(
            client, "Version", {"component": "C00"}, "Parent version"
        )
        child = await self._create_ticket(
            client, "Epic", {"atom": parent["atom_id"]}, "Child epic"
        )
        promoted = await client.call_tool(
            "atom_lifecycle_promote_draft",
            {
                "target": {
                    "ref_id": parent["ref_id"],
                    "version": parent["version"],
                },
                "targetStatus": "backlog",
            },
        )
        self.assertEqual(
            "completed",
            promoted.structured_content["status"],
            promoted.structured_content,
        )
        children = (
            await query(parent=parent["atom_id"], statuses=["backlog"])
        )["rows"]
        self.assertEqual(
            [(child["atom_id"], "task", "Epic")],
            [(row[0], row[2], row[5]) for row in children],
        )
