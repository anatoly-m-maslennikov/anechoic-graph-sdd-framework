"""Workspace isolation assertions for shared native routing tests."""


async def assert_workspace_opened(self, session, asyncio):
    responses = await asyncio.gather(
        *(
            session.call_tool(
                "workspace_open",
                {
                    "session_id": "same-id",
                    "project_root": str(self.projects_by_name[name]),
                },
            )
            for name in ("alpha", "beta")
        )
    )
    self.assertTrue(
        all(not response.is_error for response in responses), responses
    )
    self.assertEqual(
        ["alpha", "beta"],
        [r.structured_content["project_name"] for r in responses],
    )
    for root in self.projects_by_name.values():
        workspaces = root / ".anechoic_runtime/iwe_console/workspaces"
        self.assertEqual(1, len(list(workspaces.glob("*.json"))))


async def assert_workspace_views(self, session, asyncio):
    created = await session.call_tool(
        "view_create",
        {
            "project_root": str(self.projects_by_name["alpha"]),
            "workspace_id": "same-id",
        },
    )
    self.assertFalse(created.is_error, created.structured_content)
    states = await asyncio.gather(
        *(
            session.call_tool(
                "workspace_get",
                {
                    "workspace_id": "same-id",
                    "project_root": str(self.projects_by_name[name]),
                },
            )
            for name in ("alpha", "beta")
        )
    )
    self.assertEqual(
        [2, 1], [len(r.structured_content["views"]) for r in states]
    )


async def assert_schema_routes(self, session, asyncio):
    tools = {tool.name: tool for tool in (await session.list_tools()).tools}
    self.assertIn(
        "project_root", tools["query_schema"].input_schema["required"]
    )
    self.assertIn("atom_lifecycle_update", tools)
    self.assertNotIn("workbench_archive_load", tools)
    await self._assert_missing_and_outside_roots(session)
    retired = await session.call_tool(
        "query_schema", {"project_root": str(self.legacy)}
    )
    self.assertTrue(retired.is_error)
    self.assertEqual(
        ["invalid_project_root"],
        retired.structured_content["diagnostics"],
    )
    schemas = await asyncio.gather(
        *(
            session.call_tool("query_schema", {"project_root": str(root)})
            for root in self.projects_by_name.values()
        )
    )
    self.assertTrue(
        all(not response.is_error for response in schemas), schemas
    )
