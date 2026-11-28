"""Private Workspace end-to-end test steps."""


class WorkspaceStepsB:
    async def _prepare_duplicate_workspace(self, session):
        opened = await self.tool(
            session, "workspace_open", {"session_id": "duplicate"}
        )
        workspace_id, source_id = (
            opened["workspace_id"],
            opened["active_view_id"],
        )
        await self.tool(
            session,
            "view_update",
            {
                "workspace_id": workspace_id,
                "view_id": source_id,
                "sql": "SELECT 42",
                "cursor_position": 7,
                "expected_revision": 0,
            },
        )
        await self.tool(
            session,
            "view_rename",
            {
                "workspace_id": workspace_id,
                "view_id": source_id,
                "name": "Report",
            },
        )
        return source_id, workspace_id

    async def _duplicate_view_and_read_log(
        self, session, source_id, workspace_id
    ):
        await self.tool(
            session,
            "view_create",
            {
                "workspace_id": workspace_id,
                "position": "last",
                "name": "Report(1)",
            },
        )
        await self.tool(
            session,
            "view_create",
            {
                "workspace_id": workspace_id,
                "position": "last",
                "name": "Report(3)",
            },
        )
        logs_before = await self.tool(
            session, "query_log_list", {"limit": 1000}
        )

        duplicate = await self.tool(
            session,
            "view_duplicate",
            {
                "workspace_id": workspace_id,
                "view_id": source_id,
            },
        )
        duplicate_id = duplicate["view_id"]
        self.assertEqual(duplicate_id, duplicate["active_view_id"])
        return duplicate, duplicate_id, logs_before

    async def _check_duplicate_and_http(
        self,
        client,
        duplicate,
        duplicate_id,
        logs_before,
        session,
        source_id,
        workspace_id,
    ):
        self.assertEqual(
            [source_id, duplicate_id],
            [item["id"] for item in duplicate["views"][:2]],
        )
        duplicate_view = await self.tool(
            session,
            "view_get",
            {
                "workspace_id": workspace_id,
                "view_id": duplicate_id,
            },
        )
        self.assertEqual("SELECT 42", duplicate_view["sql"])
        self.assertEqual(7, duplicate_view["cursor_position"])
        self.assertEqual(0, duplicate_view["revision"])
        self.assertNotIn("result", duplicate_view)
        self.assertEqual("Report(2)", duplicate_view["name"])
        self.assertEqual(
            logs_before,
            await self.tool(session, "query_log_list", {"limit": 1000}),
        )

        await self._check_duplicate_http_parity(
            session, client, workspace_id, source_id
        )

    async def _save_successful_query(self, session):
        opened = await self.tool(
            session, "workspace_open", {"session_id": "logs"}
        )
        view = opened["active_view_id"]
        await self.tool(
            session,
            "view_update",
            {
                "workspace_id": "logs",
                "view_id": view,
                "sql": "SELECT 1",
                "expected_revision": 0,
            },
        )
        succeeded = await self.tool(
            session, "view_run", {"workspace_id": "logs", "view_id": view}
        )
        self.assertEqual("success", succeeded["status"])
        saved = await self.tool(
            session, "view_save", {"workspace_id": "logs", "view_id": view}
        )
        self.assertEqual(
            "SELECT 1",
            (
                await self.tool(
                    session,
                    "query_load",
                    {"reference": saved["saved_query_id"]},
                )
            )["sql"],
        )
        return view

    async def _run_failure_and_read_logs(self, session, view):
        revision = (
            await self.tool(
                session,
                "view_get",
                {"workspace_id": "logs", "view_id": view},
            )
        )["revision"]
        await self.tool(
            session,
            "view_update",
            {
                "workspace_id": "logs",
                "view_id": view,
                "sql": 'SELECT * FROM "restart required"',
                "expected_revision": revision,
            },
        )
        failed = await self.tool(
            session, "view_run", {"workspace_id": "logs", "view_id": view}
        )
        self.assertEqual("failed", failed["status"])
        logs = await self.tool(session, "query_log_list", {})
        self.assertEqual(
            ["failed", "success"],
            [item["outcome"] for item in logs["items"][:2]],
        )
        return logs

    async def _check_logs_and_preview(self, logs, session):
        for item in logs["items"][:2]:
            self.assertEqual(
                {
                    "log_id",
                    "at",
                    "sql",
                    "outcome",
                    "error",
                    "row_count",
                    "column_count",
                },
                set(item),
            )
            self.assertNotIn("rows", item)
            self.assertEqual(
                item,
                await self.tool(
                    session, "query_log_get", {"log_id": item["log_id"]}
                ),
            )
        preview = await self.tool(
            session,
            "query_run",
            {
                "sql": "SELECT 1",
                "preview": 0,
                "save": False,
                "result_delivery": "inline",
            },
        )
        self.assertEqual([], preview["rows"])
        self.assertEqual(0, preview["row_count"])
        return preview

    async def _check_preview_not_saved(self, preview):
        self.assertEqual(1, preview["column_count"])
        self.assertNotIn("saved_query_id", preview)
