"""In-memory Workbench service and call assertions."""


class FakeServiceBase:
    def __init__(self):
        self.calls = []
        self.closed = False

    def run(
        self,
        sql,
        page_size=100,
        cursor_position=None,
        *,
        save=False,
        preview=None,
        name=None,
        result_delivery="file",
        result_format="json_matrix",
    ):
        self.calls.append((
            self._fixture_globals["RUN"],
            sql,
            page_size,
            cursor_position,
            save,
            preview,
            name,
            result_delivery,
            result_format,
        ))
        result = {
            "query_id": "q-1",
            "columns": [{"name": "sql", "type": "VARCHAR"}],
            "rows": [[sql]],
            "row_count": 1,
            "column_count": 1,
            "offset": 0,
            "page_size": page_size,
            "has_more": False,
        }
        if save:
            result.update({
                "saved_query_id": "q_1",
                "kind": "query",
                "sql": sql,
                "name": name,
            })
        return result

    def check(self, sql, cursor_position=None):
        self.calls.append((
            self._fixture_globals["CHECK"],
            sql,
            cursor_position,
        ))
        return {"valid": True, "row_count": 1, "column_count": 1}

    def page(
        self,
        query_id,
        offset,
        page_size=100,
        *,
        grid=None,
        preview=None,
        result_delivery="file",
        result_format="json_matrix",
    ):
        self.calls.append((
            self._fixture_globals["PAGE"],
            query_id,
            offset,
            page_size,
            grid,
            result_delivery,
            result_format,
        ))
        return {
            "query_id": query_id,
            "columns": [{"name": "sql", "type": "VARCHAR"}],
            "rows": [[query_id]],
            "row_count": 1,
            "column_count": 1,
            "offset": offset,
            "page_size": page_size,
            "has_more": False,
        }

    def schema(self):
        self.calls.append((self._fixture_globals["SCHEMA"],))
        return {"atoms": []}

    def save_view(self, sql, name=None):
        self.calls.append((self._fixture_globals["SAVE_VIEW"], sql, name))
        return {
            "saved_query_id": "w_1",
            "kind": "view",
            "sql": sql,
            "name": name,
        }

    def load(self, reference):
        self.calls.append((self._fixture_globals["LOAD"], reference))
        return {
            "saved_query_id": reference,
            "kind": "query",
            "sql": "SELECT 1",
        }

    def saved_list(self, limit=20):
        self.calls.append((self._fixture_globals["SAVED_LIST"], limit))
        return {"items": []}

    def interface_call(self, name, arguments):
        self.calls.append((name, arguments))
        return {"operation": name, **arguments}

    def close(self):
        self.closed = True


async def exercise_initial(self, owner, g):
    run = await owner.call(g["RUN"], {"sql": "SELECT 1"})
    self.assertEqual("q-1", run["query_id"])
    self.assertEqual(1, run["row_count"])
    page = await owner.call(
        g["PAGE"], {"query_id": run["query_id"], "offset": 0, "page_size": 1}
    )
    self.assertEqual(0, page["offset"])
    self.assertTrue(
        (await owner.call(g["CHECK"], {"sql": "SELECT 1"}))["valid"]
    )


async def exercise_remaining(self, owner, g):
    saved = await owner.call(
        g["RUN"],
        {
            "sql": "SELECT 2",
            "cursor_position": 2,
            "save": True,
            "name": "saved",
        },
    )
    self.assertEqual("q_1", saved["saved_query_id"])
    self.assertEqual(
        "w_1",
        (
            await owner.call(
                g["SAVE_VIEW"], {"sql": "SELECT 3", "name": "view"}
            )
        )["saved_query_id"],
    )
    await owner.call(
        g["RUN"], {"sql": "SELECT 4", "save": True, "name": "   "}
    )
    self.assertEqual(
        "q_2",
        (await owner.call(g["LOAD"], {"reference": "q_2"}))["saved_query_id"],
    )
    self.assertEqual({"atoms": []}, await owner.call(g["SCHEMA"], {}))
    self.assertEqual(
        {"items": []}, await owner.call(g["SAVED_LIST"], {"limit": 3})
    )
    await exercise_workspace(self, owner, g)


async def exercise_workspace(self, owner, g):
    self.assertEqual(
        "session-1",
        (await owner.call(g["WORKSPACE_OPEN"], {"session_id": "session-1"}))[
            "session_id"
        ],
    )
    self.assertEqual(
        "view_create",
        (await owner.call(g["VIEW_CREATE"], {"workspace_id": "session-1"}))[
            "operation"
        ],
    )
    self.assertEqual(
        "view_duplicate",
        (
            await owner.call(
                g["VIEW_DUPLICATE"],
                {
                    "workspace_id": "session-1",
                    "view_id": "source-view",
                },
            )
        )["operation"],
    )
    self.assertEqual(
        "query_log_list",
        (await owner.call(g["QUERY_LOG_LIST"], {}))["operation"],
    )
    await owner.close()
