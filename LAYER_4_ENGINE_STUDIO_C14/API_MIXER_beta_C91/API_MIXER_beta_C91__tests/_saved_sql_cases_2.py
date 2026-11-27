"""Saved SQL process test cases."""

INSTANCE = "b" * 64


class SavedSqlCases2:
    def test_query_log_list_and_get(self):
        self.value(
            False,
            "query_run",
            {"sql": "SELECT 27", "result_delivery": "inline"},
        )
        for shared in (False, True):
            items = self.value(shared, "query_log_list", {"limit": 1})["items"]
            self.assertEqual(1, len(items))
            record = self.value(
                shared, "query_log_get", {"log_id": items[0]["log_id"]}
            )
            self.assertEqual(items[0], record)
            self.assertEqual(
                ("SELECT 27", "success"), (record["sql"], record["outcome"])
            )
            for name, args in (
                ("query_log_list", {"limit": True}),
                ("query_log_list", {"limit": 1001}),
                ("query_log_get", {"log_id": " "}),
            ):
                self.assertEqual(
                    "tool_input_invalid",
                    self.call(shared, name, args)["error"]["code"],
                )

    def test_rebuild_qualified_query_and_flow_targets(self):
        for shared in (False, True):
            with self.subTest(shared=shared):
                run = self.value(
                    shared,
                    "query_run",
                    {"sql": "SELECT 27", "result_delivery": "inline"},
                )
                target = "workbench_results.query_" + run["query_id"]
                rebuilt = self.value(
                    shared, "query_rebuild", {"target": target}
                )
                self.assertEqual(target, rebuilt["target"])
                args = {
                    "query_id": rebuilt["result_ids"][run["query_id"]],
                    "result_delivery": "inline",
                }
                self.assertEqual(
                    [[27]], self.value(shared, "query_page", args)["rows"]
                )
                for rejected in (
                    "ops_ingestion_issues",
                    "mrt_flow_events",
                    "mrt_package_coupling",
                    "biz_atoms",
                ):
                    reply = self.call(
                        shared, "query_rebuild", {"target": rejected}
                    )
                    self.assertEqual(
                        "tool_input_invalid", reply["error"]["code"], rejected
                    )
        flow = self.value(
            False,
            "query_run",
            {
                "sql": "SELECT count(*) FROM main.src_flow_events",
                "result_delivery": "inline",
            },
        )
        target = "main.src_flow_events"
        rebuilt = self.value(False, "query_rebuild", {"target": target})
        self.assertEqual(target, rebuilt["target"])
        self.assertIn(flow["query_id"], rebuilt["result_ids"])

    def test_view_family_direct_and_shared(self):
        for shared in (False, True):
            self.exercise_views(shared)

    def test_lifecycle_direct_and_shared_binding(self):
        for shared in (False, True):
            args = {"target": {"ref": "AN-S-1"}}
            result = self.value(shared, "atom_lifecycle_archive", args)
            self.assertEqual("completed", result["status"])
            request = {
                **self.servers[1].lease["worker_binding"],
                "instance_id": INSTANCE,
                "name": "atom_lifecycle_archive",
                "arguments": args,
            }
            self.assertEqual(
                ("/jobs/lifecycle", request), self.servers[0].requests[-1]
            )

    def test_atom_document_direct_and_shared_binding(self):
        for shared in (False, True):
            args = {"ref_id": "AN-S-1@2-draft"}
            self.assertEqual(
                {"ref_id": "AN-S-1", "body": "text"},
                self.value(shared, "iwe_console_atom_document", args),
            )
            request = {
                **self.servers[1].lease["worker_binding"],
                "instance_id": INSTANCE,
                **args,
            }
            self.assertEqual(
                ("/jobs/atom-document", request), self.servers[0].requests[-1]
            )

    def exercise_views(self, shared):
        session = "views-shared" if shared else "views-direct"
        workspace = self.value(
            shared, "workspace_open", {"session_id": session}
        )
        view = {
            "workspace_id": session,
            "view_id": workspace["active_view_id"],
        }
        update = {**view, "sql": "SELECT 42 AS answer", "expected_revision": 0}
        self.assertEqual(
            1, self.value(shared, "view_update", update)["revision"]
        )
        self.assertTrue(self.value(shared, "view_check", view)["valid"])
        run = self.value(
            shared,
            "view_run",
            {**view, "save": True, "name": "Saved View Run"},
        )
        self.assertEqual("success", run["status"])
        self.assertIn("saved_query_url", run)
        self.assertEqual(
            "SELECT 42 AS answer",
            self.value(
                shared, "query_load", {"reference": run["saved_query_id"]}
            )["sql"],
        )
        grid = {"sort": [{"column": 0, "direction": "desc"}]}
        page = self.value(
            shared,
            "view_fetch",
            {**view, "result_delivery": "inline", "grid": grid},
        )
        self.assertEqual([[42]], page["rows"])
        exported = self.value(shared, "view_fetch", view)["result_file"]
        self.assertTrue((self.root / exported["path"]).is_file())
        self.assertEqual(
            run["query_id"],
            self.value(shared, "view_get", view)["result"]["query_id"],
        )
        self.exercise_view_changes(shared, session, view, update)

    def exercise_view_changes(self, shared, session, view, update):
        created = self.value(
            shared,
            "view_create",
            {"workspace_id": session, "name": "Second", "position": "first"},
        )
        second = {"workspace_id": session, "view_id": created["view_id"]}
        duplicate = self.value(shared, "view_duplicate", second)
        third = {"workspace_id": session, "view_id": duplicate["view_id"]}
        self.assertEqual(
            "Renamed",
            self.value(shared, "view_rename", {**third, "name": "Renamed"})[
                "name"
            ],
        )
        self.assertEqual(
            third["view_id"],
            self.value(shared, "view_focus", third)["active_view_id"],
        )
        self.assertEqual(
            3,
            len(
                self.value(shared, "view_list", {"workspace_id": session})[
                    "views"
                ]
            ),
        )
        self.value(shared, "view_remove", third)
        self.value(shared, "view_remove", second)
        self.assertEqual(
            "workspace_error",
            self.call(shared, "view_remove", view)["error"]["code"],
        )
        self.assertEqual(
            "workspace_error",
            self.call(shared, "view_update", update)["error"]["code"],
        )
        self.check_invalid_views(shared, view, update)

    def check_invalid_views(self, shared, view, update):
        for name, args in (
            ("view_run", {**view, "name": "without save"}),
            ("view_update", {**update, "expected_revision": True}),
            ("view_fetch", {**view, "page_size": 0}),
            ("view_get", {**view, "extra": 1}),
        ):
            self.assertEqual(
                "tool_input_invalid",
                self.call(shared, name, args)["error"]["code"],
            )
