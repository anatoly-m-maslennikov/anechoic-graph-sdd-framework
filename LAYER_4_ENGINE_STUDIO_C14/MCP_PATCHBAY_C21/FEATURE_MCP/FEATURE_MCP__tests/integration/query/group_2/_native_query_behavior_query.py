import json

CONTROL = ".anechoic_anechoic"


class QueryCases:
    async def _tree_query(self, client, sql, **options):
        response = await client.call_tool(
            "query_run",
            {
                "sql": sql,
                "result_delivery": "inline",
                "project_root": str(self.root),
                **options,
            },
        )
        self.assertFalse(response.is_error, response.structured_content)
        return response.structured_content

    async def _tree_template(self, client, name, **arguments):
        response = await client.call_tool(
            "query_template",
            {
                "template": name,
                "result_format": "json_matrix",
                **arguments,
            },
        )
        self.assertFalse(response.is_error, response.structured_content)
        return response.structured_content

    async def _check_query_schema(self, client):
        initialized = await client.initialize()
        self.assertIsNone(initialized.capabilities.resources)
        tools = {tool.name: tool for tool in (await client.list_tools()).tools}
        self.assertTrue(
            {
                "query_run",
                "query_page",
                "query_check",
                "query_schema",
                "query_template",
                "workspace_open",
            }
            <= set(tools)
        )
        schema = await client.call_tool("query_schema", {})
        self.assertFalse(schema.is_error, schema.structured_content)
        tables = schema.structured_content["tables"]
        await self._check_schema_tables(tables)
        await self._check_query_results(client)

    async def _check_schema_tables(self, tables):
        self.assertEqual(
            {
                "atoms",
                "relations",
                "native_references",
                "components",
                "component_seeds",
                "import_nodes",
                "module_imports",
                "import_edges",
                "package_imports",
                "package_external_imports",
                "test_edges",
                "tested_by_edges",
                "import_read_issues",
                "implementation_rmedo",
                "component_metrics",
                "package_audit",
                "change_log",
                "query_log",
                "live_runs",
                "runtime_diagnostics",
                "atom_parse_issues",
                "atom_schema_issues",
                "atom_declared_carrier_issues",
                "atom_physical_carrier_issues",
                "atom_duplicate_revision_issues",
                "boundary_declarations",
                "code_access_findings",
                "state_effect_findings",
            },
            set(tables),
        )

    async def _check_query_results(self, client):
        small = await client.call_tool(
            "query_run", {"sql": "SELECT 0 AS n FROM range(120)"}
        )
        self.assertFalse(small.is_error, small.structured_content)
        self.assertEqual([[0]] * 120, small.structured_content["rows"])
        self.assertEqual(120, small.structured_content["row_count"])
        self.assertLessEqual(len(small.content[0].text.encode("utf-8")), 4096)
        large = await client.call_tool(
            "query_run", {"sql": "SELECT repeat('a', 4096) AS payload"}
        )
        self.assertFalse(large.is_error, large.structured_content)
        file = large.structured_content["result_file"]
        self.assertEqual("json_matrix", file["format"])
        self.assertEqual(
            [["a" * 4096]],
            json.loads((self.root / file["path"]).read_text())["rows"],
        )
        csv = await client.call_tool(
            "query_run", {"sql": "SELECT 1 AS n", "result_format": "csv"}
        )
        self.assertFalse(csv.is_error, csv.structured_content)
        self.assertEqual('"n"\r\n"1"\r\n', csv.content[0].text)

    async def _check_atom_templates(self, client):
        current = await self._tree_template(
            client, "get_atom", reference="AN-T-009"
        )
        self.assertEqual(
            ["exact_ref", "summary", "status", "path"],
            [column["name"] for column in current["columns"]],
        )
        self.assertEqual(
            [
                [
                    "AN-T-009@2",
                    "Verify the operator's runtime.",
                    "active",
                    f"{CONTROL}/001_TICKETS/TASKS/"
                    "AN-T-009-TASK--verify-runtime.md",
                ]
            ],
            current["rows"],
        )
        exact = await self._tree_template(
            client, "get_atom", reference="AN-T-009@1"
        )
        self.assertEqual("AN-T-009@1", exact["rows"][0][0])
        state = await self._tree_template(
            client, "get_atom_state", reference="AN-T-009"
        )
        self.assertEqual(
            ["status", "version"],
            [column["name"] for column in state["columns"]],
        )
        self.assertEqual([["active", 2]], state["rows"])
        await self._check_atom_csv_and_versions(client)
        await self._check_atom_search(client)

    async def _check_atom_csv_and_versions(self, client):
        state_csv = await client.call_tool(
            "query_template",
            {
                "template": "get_atom_state",
                "reference": "AN-T-009",
            },
        )
        self.assertFalse(state_csv.is_error, state_csv.structured_content)
        self.assertEqual(
            '"status","version"\r\n"active","2"\r\n', state_csv.content[0].text
        )
        self.assertEqual(
            state_csv.content[0].text, state_csv.structured_content["csv"]
        )
        self.assertNotIn("rows", state_csv.structured_content)
        self.assertNotIn("result_file", state_csv.structured_content)
        csv_file = await self._tree_template(
            client,
            "list_versions",
            reference="AN-T-009",
            result_format="csv",
            page_size=1,
        )
        self.assertEqual("csv", csv_file["result_file"]["format"])
        self.assertEqual(3, csv_file["result_file"]["row_count"])
        versions = await self._tree_template(
            client, "list_versions", reference="AN-T-009"
        )
        self.assertEqual(
            ["AN-T-009@3-draft", "AN-T-009@2", "AN-T-009@1"],
            [item[0] for item in versions["rows"]],
        )

    async def _check_atom_search(self, client):
        found = await self._tree_template(
            client, "find_atoms", text="OPERATOR'S"
        )
        self.assertEqual(
            [
                [
                    "AN-T-009",
                    "Verify the operator's runtime.",
                    f"{CONTROL}/001_TICKETS/TASKS/"
                    "AN-T-009-TASK--verify-runtime.md",
                ]
            ],
            found["rows"],
        )
        self.assertEqual(
            found["rows"],
            (
                await self._tree_template(
                    client, "find_atoms", text="TASK--verify-runtime"
                )
            )["rows"],
        )
