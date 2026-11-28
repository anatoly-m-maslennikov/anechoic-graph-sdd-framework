"""Private Docker image test steps."""


class ImportGraphSteps:
    def _check_import_relations(self):
        from .. import test_native_import_graph_docker_e2e as original

        status, page = original.request(
            f"{self.url}{original.WORKBENCH_PATH}/Anechoic"
        )
        self.assertEqual(200, status)
        self.assertIn("Workbench", page)
        tables = self._post("/schema", {})["tables"]
        self.assertTrue(
            {
                "import_nodes",
                "module_imports",
                "import_edges",
                "package_imports",
            }
            <= tables.keys()
        )
        self.assertEqual(
            [
                ["module", "module", 2],
                ["module", "package", 2],
                ["package", "module", 2],
                ["package", "package", 2],
            ],
            self._rows("""
            SELECT s.kind, t.kind, count(*) FROM import_edges e
            JOIN import_nodes s ON s.node_key = e.source_key
            JOIN import_nodes t ON t.node_key = e.target_key
            JOIN module_imports i USING (occurrence_key)
            WHERE i.source_key = 'module:app/main.py' GROUP BY ALL ORDER BY ALL
        """),
        )

    def _open_occurrence_view(self):
        from .. import test_native_import_graph_docker_e2e as original

        graph = original.GRAPH_COUNTS + (
            " JOIN module_imports i USING (occurrence_key) WHERE i."
            "source_key = 'module:app/main.py'"
        )
        self.assertEqual([[8]], self._rows(graph))
        query = (
            "SELECT occurrence_count FROM package_imports WHERE source_key = "
            "'package:local:app'"
        )
        workspace = self._post(
            "/interface",
            {
                "operation": "workspace_open",
                "arguments": {"session_id": "imports"},
            },
        )
        view = {
            "workspace_id": workspace["workspace_id"],
            "view_id": workspace["active_view_id"],
        }
        for operation, args in (
            ("view_update", {"sql": query, "expected_revision": 0}),
            ("view_run", {}),
        ):
            self._post(
                "/interface",
                {"operation": operation, "arguments": view | args},
            )
        return view

    def _check_occurrence_view(self, view):
        result = self._post(
            "/interface",
            {
                "operation": "view_fetch",
                "arguments": view | {"result_delivery": "inline"},
            },
        )
        self.assertEqual([[2]], result["rows"])

    def _check_test_package(self):
        query = """
            SELECT parent.node_key, parent.kind, test.node_key, test.kind, test.package_type
            FROM tested_by_edges e
            JOIN import_nodes parent ON parent.node_key = e.source_key
            JOIN import_nodes test ON test.node_key = e.target_key
            WHERE parent.relative_path = 'app'
        """
        expected = [
            [
                "package:local:app",
                "package",
                "package:local:app/app__tests",
                "package",
                "Test Package",
            ]
        ]
        self.assertEqual(expected, self._rows(query))
        self.assertEqual(
            [["package:local:app"], ["package:local:app"]],
            self._rows("""
            SELECT package_key FROM import_nodes
            WHERE relative_path IN ('app/main.py', 'app/frontend.js') ORDER BY relative_path
        """),
        )
        return expected, query

    def _open_realization_view(self, expected):
        for label, source, target in (
            ("TESTS", expected[0][2], expected[0][0]),
            ("IS_TESTED_BY", expected[0][0], expected[0][2]),
        ):
            self.assertEqual(
                [[source, target]],
                self._rows(f"""
                FROM GRAPH_TABLE (anechoic
                MATCH (s:ImportNode)-[e:{label}]->(t:ImportNode)
                COLUMNS (s.node_key AS source_key, t.node_key AS target_key))
                WHERE source_key = '{source}' AND target_key = '{target}'
            """),
            )
        workspace = self._post(
            "/interface",
            {
                "operation": "workspace_open",
                "arguments": {"session_id": "realization-canary"},
            },
        )
        view = {
            "workspace_id": workspace["workspace_id"],
            "view_id": workspace["active_view_id"],
        }
        return view

    def _check_rebuild_view(self, expected, query, view):
        self._post(
            "/interface",
            {
                "operation": "view_update",
                "arguments": view | {"sql": query, "expected_revision": 0},
            },
        )
        first = self._post(
            "/interface", {"operation": "view_run", "arguments": view}
        )["query_id"]
        rebuilt = self._post("/rebuild", {"target": "all"})
        second = rebuilt["result_ids"][first]
        self.assertNotEqual(first, second)
        fetched = self._post(
            "/interface",
            {
                "operation": "view_fetch",
                "arguments": view | {"result_delivery": "inline"},
            },
        )
        self.assertEqual(
            (second, expected), (fetched["query_id"], fetched["rows"])
        )

    def _check_native_atom_change(self, sql, graph, label, started, expected):
        from .. import test_native_import_graph_docker_e2e as original

        limit = 20.0
        actual = self._rows(sql)
        while actual != expected and original.observing(
            self.container, started + limit
        ):
            original.sleep(0.1)
            actual = self._rows(sql)
        elapsed = original.monotonic() - started
        print(f"native Atom watcher {label}: {elapsed:.3f}s", flush=True)
        self.assertEqual(expected, actual, label)
        if original.image_timeout(limit) is not None:
            self.assertLessEqual(elapsed, limit, label)
        self.assertEqual(
            [expected[0][-2:]] if expected else [],
            self._rows(graph),
            label,
        )

    def _create_edit_rename_atom(self, check):
        from .. import test_native_import_graph_docker_e2e as original

        started = original.monotonic()
        path = self._write(
            "_anechoic_anechoic/001_TICKETS/TASKS/AN-T-9901--watcher.md",
            original._watcher_contents(1, "component: C00"),
        )
        check(
            "create",
            started,
            [[path.name, "AN-T-9901", "AN-T-9901@1", "Component", "C00"]],
        )
        started = original.monotonic()
        path.write_text(
            original._watcher_contents(2, "atom: AN-S-001"), encoding="utf-8"
        )
        check(
            "edit",
            started,
            [[path.name, "AN-T-9901", "AN-T-9901@2", "Atom", "AN-S-001"]],
        )
        started = original.monotonic()
        path = path.rename(path.with_name("AN-T-9901--renamed.md"))
        check(
            "rename",
            started,
            [[path.name, "AN-T-9901", "AN-T-9901@2", "Atom", "AN-S-001"]],
        )
        return path
