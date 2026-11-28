"""Private Workspace end-to-end test steps."""


class WorkspaceStepsA:
    async def _open_workspace_and_create_view(self, client, session):
        opened = await self.tool(
            session, "workspace_open", {"session_id": "native-session"}
        )
        self.assertEqual("native-session", opened["workspace_id"])
        self.assertEqual("fixture", opened["project_name"])
        self.assertNotEqual(self.root.name, opened["project_name"])
        self.assertIn("?workspace=native-session", opened["workspace_url"])
        native_state = await self.tool(
            session,
            "workspace_get",
            {"workspace_id": opened["workspace_id"]},
        )
        self.assertEqual("fixture", native_state["project_name"])
        http_open = await self.interface_call(
            client, "workspace_open", {"session_id": "native-session"}
        )
        self.assertEqual(200, http_open.status_code, http_open.text)
        self.assertEqual("fixture", http_open.json()["project_name"])
        first = opened["active_view_id"]
        created = await self.tool(
            session,
            "view_create",
            {
                "workspace_id": opened["workspace_id"],
                "position": "last",
            },
        )
        view = created["view_id"]
        return created, first, opened, view

    async def _run_and_fetch_view(self, opened, session, view):
        updated = await self.tool(
            session,
            "view_update",
            {
                "workspace_id": opened["workspace_id"],
                "view_id": view,
                "sql": (
                    'SELECT reference FROM atoms '
                    "WHERE reference = 'AN-S-684'"
                ),
                "expected_revision": 0,
            },
        )
        self.assertEqual(1, updated["revision"])
        run = await self.tool(
            session,
            "view_run",
            {
                "workspace_id": opened["workspace_id"],
                "view_id": view,
            },
        )
        self.assertNotIn("rows", run)
        self.assertEqual("success", run["status"])
        fetched = await self.tool(
            session,
            "view_fetch",
            {
                "workspace_id": opened["workspace_id"],
                "view_id": view,
                "offset": 0,
                "page_size": 1,
                "result_delivery": "inline",
            },
        )
        return fetched

    async def _check_workspace_state(
        self, client, created, fetched, first, opened, session
    ):
        self.assertEqual([["AN-S-684"]], fetched["rows"])
        focused = await self.tool(
            session,
            "view_focus",
            {
                "workspace_id": opened["workspace_id"],
                "view_id": first,
            },
        )
        self.assertEqual(first, focused["active_view_id"])
        http = await self.interface_call(
            client,
            "workspace_get",
            {"workspace_id": opened["workspace_id"]},
        )
        self.assertEqual(200, http.status_code, http.text)
        state = http.json()
        self.assertEqual("fixture", state["project_name"])
        self.assertNotEqual(self.root.name, state["project_name"])
        self.assertEqual(first, state["active_view_id"])
        self.assertEqual(
            {item["id"] for item in created["views"]},
            {item["id"] for item in state["views"]},
        )
        self._check_workspace_persistence()

    async def _prepare_isolated_workspaces(self, session):
        one = await self.tool(session, "workspace_open", {"session_id": "one"})
        two = await self.tool(session, "workspace_open", {"session_id": "two"})
        one_view, two_view = one["active_view_id"], two["active_view_id"]
        await self.tool(
            session,
            "view_update",
            {
                "workspace_id": "one",
                "view_id": one_view,
                "sql": "SELECT 1",
                "expected_revision": 0,
            },
        )
        return one_view, two_view

    async def _check_workspace_guards(self, one_view, session, two_view):
        for name, arguments, message in (
            (
                "workspace_get",
                {"workspace_id": "missing"},
                "unknown workspace_id",
            ),
            (
                "view_get",
                {"workspace_id": "one", "view_id": two_view},
                "unknown view_id",
            ),
            (
                "view_update",
                {
                    "workspace_id": "one",
                    "view_id": one_view,
                    "sql": "SELECT 2",
                    "expected_revision": 0,
                },
                "expected_revision does not match",
            ),
            (
                "view_remove",
                {"workspace_id": "two", "view_id": two_view},
                "cannot remove the last view",
            ),
        ):
            with self.subTest(name=name):
                response = await session.call_tool(name, arguments)
                self.assertTrue(response.is_error)
                self.assertIn(message, str(response.structured_content))

    async def _check_workspace_http_error(self, client, session, two_view):
        unknown = await self.interface_call(
            client, "workspace_get", {"workspace_id": "missing"}
        )
        self.assertEqual(400, unknown.status_code)
        self.assertEqual(
            {
                "error": "unknown workspace_id",
                "code": "query_error",
                "tool_result": {
                    "outcome": "failed",
                    "diagnostics": ["query_error: unknown workspace_id"],
                },
            },
            unknown.json(),
        )
        untouched = await self.tool(
            session,
            "view_get",
            {"workspace_id": "two", "view_id": two_view},
        )
        self.assertEqual("", untouched["sql"])
