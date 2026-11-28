"""Query, lifecycle and HTTP checks shared by the native MCP stdio suite."""

from contextlib import asynccontextmanager


class NativeQueryProtocolCases:
    @asynccontextmanager
    async def _stdio_session(self):
        from . import test_native_query_stdio as host

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
            yield client

    async def test_discovered_query_templates_and_statuses_are_callable(self):
        samples = {
            "get_atom": {"reference": "AN-T-009"},
            "get_atom_state": {"reference": "AN-T-009"},
            "find_atoms": {"text": "fixture"},
            "list_versions": {"reference": "AN-T-009"},
            "list_tickets": {"label": "Task"},
            "list_atoms": {"family": "spec"},
            "count_atoms": {"group_by": "status"},
            "list_relations": {"reference": "AN-T-009"},
            "count_relations_by_type": {},
            "fetch_contracts": {"component": "C00"},
            "fetch_solutions": {"component": "C00"},
            "get_component_manifest": {"component": "C00"},
            "get_component_purpose": {"component": "C00"},
        }
        async with self._stdio_session() as client:
            await client.initialize()
            tools = (await client.list_tools()).tools
            descriptor = next(
                tool for tool in tools if tool.name == "query_template"
            )
            properties = descriptor.input_schema["properties"]
            self.assertEqual(set(samples), set(properties["template"]["enum"]))
            statuses = properties["statuses"]["items"]["enum"]
            self.assertTrue(
                {"ready", "in_queue", "complete"}.issubset(statuses)
            )
            await self._check_query_templates(client, samples)
            await self._check_lifecycle_statuses(client, statuses)

    async def _check_query_templates(self, client, samples):
        for template, arguments in samples.items():
            with self.subTest(template=template):
                response = await client.call_tool(
                    "query_template",
                    {
                        "template": template,
                        "result_format": "json_matrix",
                        **arguments,
                    },
                )
                self.assertFalse(
                    response.is_error, response.structured_content
                )

    async def _check_lifecycle_statuses(self, client, statuses):
        for status in statuses:
            with self.subTest(status=status):
                response = await client.call_tool(
                    "query_template",
                    {
                        "template": "list_tickets",
                        "statuses": [status],
                        "result_format": "json_matrix",
                    },
                )
                self.assertFalse(
                    response.is_error, response.structured_content
                )

    async def test_ticket_asset_and_spec_draft_archive_tools(self):
        for number in (11, 12):
            self._write(
                (
                    "01_draft/AN-S-"
                    f"{number:03d}"
                    "@1-draft-SPEC-COMPONENT_CONTRACT--fixture.md"
                ),
                f"AN-S-{number:03d}",
                "draft",
                1,
                template="component_contract",
                lens="SPEC",
                container={"component": "C0"},
                structure_tier=1,
            )
        async with self._stdio_session() as client:
            await client.initialize()
            asset = await client.call_tool(
                "atom_lifecycle_create_asset",
                {
                    "newAtom": {
                        "template": "spec_proposal",
                        "body": "## Summary\n\nExample proposal\n",
                    }
                },
            )
            self.assertEqual(
                "completed",
                asset.structured_content["status"],
                asset.structured_content,
            )
            saved = asset.structured_content["artifact"]
            self.assertEqual("in_queue", saved["status"])
            self.assertIn("/__TICKETS/ASSETS/", saved["path"])
            await self._check_spec_archive_tools(client)

    async def _check_spec_archive_tools(self, client):
        selection = await client.call_tool(
            "query_run",
            {
                "sql": 'SELECT reference, "header.state.version" FROM atoms '
                "WHERE reference IN ('AN-S-011@1-draft', 'AN-S-012@1-draft') ORDER BY 1",
                "result_delivery": "inline",
            },
        )
        targets = selection.structured_content["rows"]
        self.assertEqual(
            [["AN-S-011@1-draft", 1], ["AN-S-012@1-draft", 1]], targets
        )
        archived = await client.call_tool(
            "atom_lifecycle_archive", {"targets": targets}
        )
        self.assertEqual(
            "completed",
            archived.structured_content["status"],
            archived.structured_content,
        )
        self.assertEqual(
            ["AN-S-011@1", "AN-S-012@1"],
            [
                row["artifact"]["ref_id"]
                for row in archived.structured_content["results"]
            ],
        )

    async def test_http_queries_native_projection_without_legacy_routes(self):
        from MCP_PATCHBAY_C21.FEATURE_MCP.transport_support.\
            paths.paths__shared import (
            HEALTH_PATH,
            MCP_PATH,
            WORKBENCH_PATH,
        )
        from MCP_PATCHBAY_C21.FEATURE_MCP.gateway.gateway__shared import (
            create_http_app as create_app,
        )

        from . import test_native_query_stdio as host

        before = self._carrier_digests()
        app = create_app(
            self.root,
            gateway_factory=lambda root, control: host.create_native_gateway(
                root, control, host._native_inputs()
            ),
            control_root=host.CONTROL,
        )
        async with app.starlette_app.router.lifespan_context(
            app.starlette_app
        ):
            async with host.httpx2.AsyncClient(
                transport=host.httpx2.ASGITransport(app=app),
                base_url="http://127.0.0.1:18093",
            ) as http:
                await self._check_native_http_status(
                    http, HEALTH_PATH, WORKBENCH_PATH
                )
                await self._check_native_http_mcp(http, MCP_PATH)
        self.assertEqual(before, self._carrier_digests())

    async def _check_native_http_status(
        self, http, health_path, workbench_path
    ):
        health = await http.get(health_path, headers={"Accept": "text/html"})
        self.assertEqual({"state": "ready"}, health.json())
        for path in (
            f"{health_path}/workbench-restart",
            f"{health_path}/workbench-reread",
        ):
            self.assertEqual(404, (await http.post(path)).status_code)
        self.assertEqual(
            404,
            (await http.get(f"{workbench_path}/fixture")).status_code,
        )
        self.assertEqual(
            421,
            (
                await http.get(health_path, headers={"Host": "example.com"})
            ).status_code,
        )

    async def _check_native_http_mcp(self, http, mcp_path):
        from . import test_native_query_stdio as host

        async with (
            host.streamable_http_client(
                "http://127.0.0.1:18093" + mcp_path,
                http_client=http,
            ) as streams,
            host.ClientSession(*streams) as client,
        ):
            await self._check_native_http_schema(client)
            await self._check_native_http_query(client)

    async def _check_native_http_schema(self, client):
        await client.initialize()
        self.assertTrue(
            {
                "query_run",
                "query_page",
                "query_check",
                "query_schema",
                "workspace_open",
            }
            <= {tool.name for tool in (await client.list_tools()).tools}
        )
        schema = await client.call_tool("query_schema", {})
        self.assertIn(
            "native_references",
            schema.structured_content["tables"],
        )

    async def _check_native_http_query(self, client):
        sql = (
            "SELECT exact_ref FROM native_references WHERE exact_ref LIKE "
            "'AN-T-%' ORDER BY exact_ref"
        )
        checked = await client.call_tool("query_check", {"sql": sql})
        self.assertTrue(checked.structured_content["valid"])
        first = await client.call_tool(
            "query_run",
            {
                "sql": sql,
                "page_size": 1,
                "result_delivery": "inline",
            },
        )
        self.assertFalse(first.is_error, first.structured_content)
        self.assertEqual([["AN-T-009@1"]], first.structured_content["rows"])
        page = await client.call_tool(
            "query_page",
            {
                "query_id": first.structured_content["query_id"],
                "offset": 1,
                "result_delivery": "inline",
            },
        )
        self.assertFalse(page.is_error, page.structured_content)
        self.assertEqual(
            [["AN-T-009@2"], ["AN-T-009@3-draft"]],
            page.structured_content["rows"],
        )
        refused = await client.call_tool(
            "workspace_get", {"workspace_id": "unavailable"}
        )
        self.assertTrue(refused.is_error)
