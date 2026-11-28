import json

CONTROL = ".anechoic_anechoic"


class InventoryCases:
    async def _check_inventory_templates(self, client):
        tickets = await self._tree_template(
            client, "list_tickets", kind="task"
        )
        self.assertEqual(
            {"AN-T-009", "AN-T-009@3-draft", "AN-T-010"},
            {item[0] for item in tickets["rows"]},
        )
        children = await self._tree_template(
            client, "list_tickets", parent="AN-T-009", statuses=["done"]
        )
        self.assertEqual(
            [
                [
                    "AN-T-010",
                    "Fixture.",
                    "task",
                    "done",
                    f"{CONTROL}/001_TICKETS/TASKS/AN-T-010-TASK--child.md",
                    None,
                ]
            ],
            children["rows"],
        )
        await self._check_inventory_atoms(client)
        await self._check_inventory_counts(client)

    async def _check_inventory_atoms(self, client):
        listed = await self._tree_template(
            client, "list_atoms", family="project_config", statuses=["active"]
        )
        self.assertEqual(
            {"AN-P-001", "AN-C-001"}, {row[0] for row in listed["rows"]}
        )
        self.assertEqual(
            {"AN-P-001"},
            {
                row[0]
                for row in (
                    await self._tree_template(
                        client,
                        "list_atoms",
                        family="pmeta",
                        statuses=["active"],
                    )
                )["rows"]
            },
        )
        self.assertEqual(
            [["active", 1]],
            (
                await self._tree_template(
                    client, "get_atom_state", reference="AN-C-001@1"
                )
            )["rows"],
        )
        self.assertEqual(
            [["CONTAINED_BY", "AN-P-001", False]],
            (
                await self._tree_template(
                    client, "list_relations", reference="AN-C-001@1"
                )
            )["rows"],
        )

    async def _check_inventory_counts(self, client):
        counted = await self._tree_template(
            client,
            "count_atoms",
            family="tkt",
            kind="task",
            statuses=["archived"],
        )
        self.assertEqual(
            ["count"], [column["name"] for column in counted["columns"]]
        )
        self.assertEqual([[1]], counted["rows"])
        grouped = await self._tree_template(
            client, "count_atoms", family="tkt", group_by="status"
        )
        self.assertEqual(
            [["active", 1], ["archived", 1], ["done", 1], ["draft", 1]],
            grouped["rows"],
        )
        edges = await self._tree_template(
            client, "list_relations", reference="AN-T-010@1"
        )
        self.assertEqual([["CONTAINED_BY", "AN-T-009", False]], edges["rows"])
        incoming = await self._tree_template(
            client,
            "list_relations",
            reference="AN-T-010",
            direction="incoming",
        )
        self.assertEqual([["CONTAINS", "AN-T-009", True]], incoming["rows"])
        edge_counts = await self._tree_template(
            client, "count_relations_by_type"
        )
        self.assertEqual(
            [["CONTAINED_BY", False, 7], ["CONTAINS", True, 7]],
            edge_counts["rows"],
        )

    async def _check_query_pages(self, client):
        sql = (
            "SELECT stable_ref, exact_ref FROM native_references "
            "WHERE exact_ref LIKE 'AN-T-009@%' ORDER BY exact_ref"
        )
        checked = await client.call_tool("query_check", {"sql": sql})
        self.assertTrue(checked.structured_content["valid"])
        first = await self._tree_query(client, sql, page_size=1)
        self.assertEqual([[None, "AN-T-009@1"]], first["rows"])
        page = await client.call_tool(
            "query_page",
            {
                "query_id": first["query_id"],
                "offset": 1,
                "result_delivery": "inline",
            },
        )
        self.assertEqual(
            [["AN-T-009", "AN-T-009@2"], [None, "AN-T-009@3-draft"]],
            page.structured_content["rows"],
        )
        inverse = await self._tree_query(
            client,
            "SELECT relation_type, derived FROM relations "
            "WHERE (source_ref = 'C0' AND target_ref = 'AN-T-009') "
            "OR (source_ref = 'AN-T-009' AND target_ref = 'C0') "
            "ORDER BY derived",
        )
        self.assertEqual(
            [["CONTAINED_BY", False], ["CONTAINS", True]], inverse["rows"]
        )
        await self._check_refused_queries(client)

    async def _check_refused_queries(self, client):
        for name, arguments in (
            (
                "query_run",
                {"sql": "SELECT 1", "project_root": str(self.root.parent)},
            ),
            ("query_run", {"sql": "SELECT 1", "save": "yes"}),
            ("query_run", {"sql": "DELETE FROM atoms"}),
            (
                "query_template",
                {"template": "list_versions", "reference": "AN-T-009@2"},
            ),
            (
                "query_template",
                {
                    "template": "get_atom",
                    "reference": "AN-T-009",
                    "text": "wrong input",
                },
            ),
            ("workspace_get", {"workspace_id": "unavailable"}),
        ):
            with self.subTest(name=name, arguments=arguments):
                refused = await client.call_tool(name, arguments)
                self.assertTrue(refused.is_error)
        self.assertEqual(
            7,
            (
                await self._tree_query(
                    client, "SELECT count(*) AS atoms FROM atoms"
                )
            )["rows"][0][0],
        )

    async def _check_query_diagnostics(self, client):
        cases = (
            (
                "SELECT missing FROM atoms WHERE 'private_binder_value' = 'x'",
                "binding",
            ),
            ("SELECT 'private_parser_value' FROM", "syntax"),
            ("SELECT CAST('private_conversion_value' AS INTEGER)", "convert"),
        )
        for sql, reason in cases:
            for operation in ("query_run", "query_check"):
                with self.subTest(operation=operation, reason=reason):
                    response = await client.call_tool(operation, {"sql": sql})
                    self.assertTrue(response.is_error)
                    self.assertEqual(
                        "failed", response.structured_content["outcome"]
                    )
                    detail = json.dumps(response.structured_content).lower()
                    self.assertNotIn("private_", detail)
                    self.assertNotIn(sql.lower(), detail)
                    self.assertIn("query_error", detail)
                    self.assertIn(reason, detail)
                    recovered = await self._tree_query(client, "SELECT 1")
                    self.assertEqual([[1]], recovered["rows"])
