"""Native projection query cases."""


class NativeQueryProjectionCases:
    async def test_project_queries_include_only_solutions_at_tier_zero(self):
        from ..group_1 import test_native_query_stdio as host

        self._write_projection_fixtures()
        async with (
            host.asyncio.timeout(25),
            host.stdio_client(
                host.StdioServerParameters(
                    command=host.sys.executable,
                    args=self.args,
                    env={"PYTHONPATH": str(host.MCP.parents[1])},
                )
            ) as streams,
            host.ClientSession(*streams) as client,
        ):
            await client.initialize()
            for template, expected in (
                ("fetch_contracts", []),
                ("fetch_solutions", ["AN-S-1429@1"]),
            ):
                result = await client.call_tool(
                    "query_template",
                    {
                        "template": template,
                        "component": "C0",
                        "result_format": "json_matrix",
                    },
                )
                self.assertFalse(result.is_error, result.structured_content)
                self.assertEqual(
                    expected,
                    [row[0] for row in result.structured_content["rows"]],
                )

    def _write_projection_fixtures(self):
        self._write(
            "AN-S-1428-axiom.md",
            "AN-S-1428",
            "active",
            1,
            template="axiom",
            tier=-1,
        )
        self._write(
            "AN-S-1429-contract.md",
            "AN-S-1429",
            "active",
            1,
            template="solution",
            tier=0,
        )
        self._write(
            "AN-S-3190-principle.md",
            "AN-S-3190",
            "active",
            1,
            template="applicable_principle",
            tier=2,
        )
        self._write(
            "AN-S-3038-manifest.md",
            "AN-S-3038",
            "active",
            1,
            template="component_manifest",
            tier=0,
        )
        self._write(
            "AN-S-021-tier-one.md",
            "AN-S-021",
            "active",
            1,
            template=None,
            tier=1,
        )
