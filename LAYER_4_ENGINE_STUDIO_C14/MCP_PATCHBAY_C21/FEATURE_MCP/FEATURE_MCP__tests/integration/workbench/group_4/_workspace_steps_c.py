"""Private Workspace end-to-end test steps."""

from MCP_PATCHBAY_C21.FEATURE_MCP.transport_support.paths.\
    paths__shared import (
    WORKBENCH_PATH,
)


class WorkspaceStepsC:
    async def _check_http_duplicate(
        self, client, session, source_id, workspace_id
    ):
        http_duplicate = await self.interface_call(
            client,
            "view_duplicate",
            {
                "workspace_id": workspace_id,
                "view_id": source_id,
            },
        )
        self.assertEqual(200, http_duplicate.status_code, http_duplicate.text)
        http_state_response = await self.interface_call(
            client,
            "workspace_get",
            {
                "workspace_id": workspace_id,
            },
        )
        self.assertEqual(
            200, http_state_response.status_code, http_state_response.text
        )
        http_state = http_state_response.json()
        self.assertEqual(
            http_duplicate.json()["view_id"], http_state["active_view_id"]
        )
        self.assertEqual(
            http_state,
            await self.tool(
                session, "workspace_get", {"workspace_id": workspace_id}
            ),
        )
        return http_state

    async def _check_invalid_duplicate(
        self, client, http_state, session, source_id, workspace_id
    ):
        invalid_mcp = await session.call_tool(
            "view_duplicate",
            {
                "workspace_id": workspace_id,
                "view_id": source_id,
                "unexpected": True,
            },
        )
        self.assertTrue(invalid_mcp.is_error)
        invalid_http = await self.interface_call(
            client,
            "view_duplicate",
            {
                "workspace_id": workspace_id,
                "view_id": source_id,
                "unexpected": True,
            },
        )
        self.assertEqual(400, invalid_http.status_code)
        self.assertEqual(
            http_state,
            await self.tool(
                session, "workspace_get", {"workspace_id": workspace_id}
            ),
        )

    async def _run_grid_query(self, session):
        opened = await self.tool(
            session, "workspace_open", {"session_id": "grid-session"}
        )
        identity = {
            "workspace_id": opened["workspace_id"],
            "view_id": opened["active_view_id"],
        }
        await self.tool(
            session,
            "view_update",
            identity
            | {
                "sql": (
                    "SELECT i % 3 AS bucket, i AS rowid, 'DRAFT%' AS label "
                    "FROM range(12) AS t(i)"
                ),
                "expected_revision": 0,
            },
        )
        run = await self.tool(session, "view_run", identity)
        grid = {
            "sort": [{"column": 1, "direction": "desc"}],
            "filters": [
                {"column": 2, "operator": "contains", "value": "draft%"}
            ],
            "group_by": {"column": 0, "direction": "asc"},
        }
        args = {
            "query_id": run["query_id"],
            "offset": 0,
            "page_size": 2,
            "grid": grid,
            "result_delivery": "inline",
        }
        native = await self.tool(session, "query_page", args)
        return args, grid, identity, native

    async def _check_grid_results(
        self, args, client, grid, identity, native, session
    ):
        response = await client.post(
            f"{WORKBENCH_PATH}/fixture/page", json=args
        )
        self.assertEqual(200, response.status_code, response.text)
        self.assertEqual(native, response.json())
        self.assertEqual([[0, 9, "DRAFT%"], [0, 6, "DRAFT%"]], native["rows"])
        self.assertEqual(12, native["source_row_count"])
        self.assertEqual(12, native["row_count"])
        self.assertEqual([{"value": 0, "count": 4}], native["groups"])
        fetched = await self.tool(
            session,
            "view_fetch",
            identity
            | {
                "offset": 0,
                "page_size": 2,
                "grid": grid,
                "result_delivery": "inline",
            },
        )
        self.assertEqual(native["rows"], fetched["rows"])
        self.assertEqual(native["groups"], fetched["groups"])
        return response

    async def _check_invalid_grid(
        self, args, client, identity, native, response, session
    ):
        for bad in (
            {"sort": [{"column": 99, "direction": "asc"}]},
            {"unknown": True},
            None,
            [],
        ):
            rejected = await session.call_tool(
                "query_page", args | {"grid": bad}
            )
            self.assertTrue(rejected.is_error)
            response = await client.post(
                f"{WORKBENCH_PATH}/fixture/page", json=args | {"grid": bad}
            )
            self.assertEqual(400, response.status_code)
        invalid_fetch = await self.interface_call(
            client, "view_fetch", identity | {"grid": None}
        )
        self.assertEqual(400, invalid_fetch.status_code)
        self.assertEqual(native, await self.tool(session, "query_page", args))
