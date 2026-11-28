"""Saved SQL process test cases."""

from urllib.parse import parse_qs, urlsplit
from uuid import UUID

INSTANCE = "b" * 64


class SavedSqlCases1:
    def test_direct_save_load_list_and_view(self):
        sql = " SELECT 43 AS answer\n"
        saved = self.value(
            False,
            "query_run",
            {
                "sql": sql,
                "save": True,
                "name": "Bookmark",
                "result_delivery": "inline",
            },
        )
        self.assertEqual([[43]], saved["rows"])
        self.assertEqual(7, UUID(saved["saved_query_id"]).version)
        url = urlsplit(saved["saved_query_url"])
        self.assertEqual(
            ("example.test", "/anechoic/iwe-console/Project%20A"),
            (url.netloc, url.path),
        )
        self.assertEqual([str(self.root)], parse_qs(url.query)["project_root"])
        loaded = self.value(
            False, "query_load", {"reference": saved["saved_query_url"]}
        )
        self.assertEqual((sql, "Bookmark"), (loaded["sql"], loaded["name"]))
        view = self.value(
            False,
            "view_save",
            {"sql": "SELECT missing_column", "name": "Snapshot"},
        )
        self.assertEqual("view", view["kind"])
        self.assertEqual(
            "SELECT missing_column",
            self.value(
                False, "query_load", {"reference": view["saved_query_id"]}
            )["sql"],
        )
        items = self.value(False, "query_saved_list", {"limit": 10})["items"]
        self.assertEqual(
            {saved["saved_query_id"], view["saved_query_id"]},
            {item["saved_query_id"] for item in items},
        )

    def test_shared_links_and_input_refusals(self):
        saved = self.value(
            True,
            "query_run",
            {"sql": "SELECT 7", "save": True, "result_delivery": "inline"},
        )
        url = saved["saved_query_url"]
        for reference in (url, url.replace("/iwe-console/", "/workbench/")):
            loaded = self.value(True, "query_load", {"reference": reference})
            self.assertEqual("SELECT 7", loaded["sql"])
            bad_link = reference.replace("example.test", "foreign.test")
            self.assertEqual(
                "tool_input_invalid",
                self.call(True, "query_load", {"reference": bad_link})[
                    "error"
                ]["code"],
            )
        for name, args in (
            ("query_run", {"sql": "SELECT 1", "name": "bad"}),
            ("query_run", {"sql": "SELECT 1", "save": 1}),
            ("view_save", {"sql": "SELECT 1", "workspace_id": "x"}),
            ("query_saved_list", {"limit": True}),
        ):
            self.assertEqual(
                "tool_input_invalid",
                self.call(True, name, args)["error"]["code"],
            )
        configured = self.value(
            False,
            "query_load",
            {"reference": saved["saved_query_id"]},
            base=None,
            asserted=False,
        )
        self.assertTrue(
            configured["saved_query_url"].startswith(
                "https://configured.test/workbench?"
            )
        )

    def test_missing_or_invalid_public_url_preserves_saved_sql(self):
        sql = "SELECT 31"
        for index, public_url in enumerate(
            (None, "https://user@configured.test/custom")
        ):
            self.direct = self.start_direct(
                f"fallback-{index}.sock", public_url
            )
            workbench = (
                {} if public_url is None else {"public_url": public_url}
            )
            self.servers[1].binding["parameters"] = {
                "runtime": {"workbench": workbench}
            }
            for shared in (False, True):
                for operation, args in (
                    ("query_run", {"save": True, "result_delivery": "inline"}),
                    ("view_save", {}),
                ):
                    with self.subTest(
                        public_url=public_url,
                        shared=shared,
                        operation=operation,
                    ):
                        self.check_missing_url(
                            public_url, shared, operation, sql, args
                        )

    def check_missing_url(self, public_url, shared, operation, sql, args):
        saved = self.value(
            shared,
            operation,
            {"sql": sql, **args},
            base=None,
            asserted=False,
        )
        saved_id = saved["saved_query_id"]
        self.assertEqual(7, UUID(saved_id).version)
        self.assertIsNone(saved["saved_query_url"])
        self.assertEqual(
            "workbench_url_unknown",
            saved["saved_query_url_reason"],
        )
        loaded = self.value(
            shared,
            "query_load",
            {"reference": saved_id},
            base=None,
            asserted=False,
        )
        self.assertEqual(
            (saved_id, sql),
            (loaded["saved_query_id"], loaded["sql"]),
        )

    def test_save_existing_view_uses_its_workspace_identity(self):
        def kernel(operation, arguments):
            response = self.kernel.post(
                "/workspace",
                json={
                    "instance_id": INSTANCE,
                    "operation": operation,
                    "arguments": arguments,
                },
            )
            self.assertEqual(200, response.status_code, response.text)
            return response.json()["result"]

        workspace = kernel("workspace_open", {"session_id": "session-a"})
        view = {
            "workspace_id": workspace["workspace_id"],
            "view_id": workspace["active_view_id"],
        }
        kernel(
            "view_update", {**view, "sql": "SELECT 12", "expected_revision": 0}
        )
        saved = self.value(True, "view_save", view)
        self.assertEqual(view, {key: saved[key] for key in view})
        self.assertEqual(
            "SELECT 12",
            self.value(
                True, "query_load", {"reference": saved["saved_query_id"]}
            )["sql"],
        )

    def test_workspace_session_binding_links_and_refusals(self):
        for shared, session in (
            (False, "direct-session"),
            (True, "shared-session"),
        ):
            opened = self.value(shared, "workspace_open", {}, session=session)
            self.assertEqual(session, opened["workspace_id"])
            self.assertEqual("Project A", opened["project_name"])
            url = urlsplit(opened["workspace_url"])
            self.assertEqual("/anechoic/iwe-console/Project%20A", url.path)
            self.assertEqual(
                {"workspace": [session], "project_root": [str(self.root)]},
                parse_qs(url.query),
            )
            loaded = self.value(
                shared, "workspace_get", {"workspace_id": session}
            )
            self.assertEqual(opened, loaded)
            explicit = self.value(
                shared,
                "workspace_open",
                {"session_id": session + "-explicit"},
                session=session,
            )
            self.assertEqual(session + "-explicit", explicit["workspace_id"])
            items = self.value(shared, "workspace_list", {})["items"]
            self.assertIn({"workspace_id": session}, items)
            for name, args in (
                ("workspace_open", {}),
                ("workspace_open", {"session_id": " "}),
                ("workspace_get", {"workspace_id": ""}),
                ("workspace_list", {"extra": True}),
            ):
                self.assertEqual(
                    "tool_input_invalid",
                    self.call(shared, name, args)["error"]["code"],
                )
