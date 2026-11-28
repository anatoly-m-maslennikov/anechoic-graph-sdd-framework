"""Additional native Import Graph cases."""

from ..group_1 import native_import_graph_cases_4 as origin


class ImportGraphCases4Extra:
    def _component_fixture(self):
        self._source("src/UNIT_C1/UNIT_C1__tests/test_e2e.py", "pass\n")
        implementation = self._source(
            "src/UNIT_C1/service_pkg1/main.py", "pass\n"
        )
        self._source(
            "src/UNIT_C1/service_pkg1/service_pkg1__tests/test_main.py",
            "pass\n",
        )
        self._source("src/group/group__tests/test_e2e.py", "pass\n")
        structure = self._source(
            ".anechoic_tmp/structure.json",
            origin.json.dumps({
                "model_sha256": "fixture",
                "project": {"ref": "AN-S-001@1", "sha256": "fixture"},
                "components": {
                    "C1": {
                        "parent": "C00",
                        "ref": "AN-S-006@1",
                        "sha256": "fixture",
                        "source_path": (
                            'AN-S-006-SPEC-COMPONENT_MANI'
                            'FEST--unit.md'
                        ),
                        "fields": {"name": "Unit"},
                    }
                },
            }),
        )
        return implementation, structure

    async def test_component_test_package_and_unmarked_package(self):
        implementation, structure = self._component_fixture()
        gateway = await self._gateway(structure_snapshot=structure)

        async def rows(sql):
            response = await gateway.call(
                None,
                origin.types.CallToolRequestParams(
                    name="query_run",
                    arguments={
                        "sql": sql,
                        "result_delivery": "inline",
                    },
                ),
            )
            self.assertFalse(response.is_error, response.structured_content)
            return response.structured_content["rows"]

        await self._assert_component_rows(rows)
        inverse = origin._INVERSE_TEST_COMPONENT
        expected = [["C1", "src/UNIT_C1/UNIT_C1__tests"]]
        self.assertEqual(expected, await rows(inverse))
        issues = (
            "SELECT relative_path, test_issue FROM package_audit WHERE "
            "test_issue IS NOT NULL ORDER BY relative_path"
        )
        orphan = ["src/group/group__tests", "missing_test_target"]
        self.assertEqual(
            [
                ["src/UNIT_C1/service_pkg1", "missing_visibility_marker"],
                orphan,
            ],
            await rows(issues),
        )
        implementation.rename(implementation.with_name("main__shared.py"))
        async with origin.asyncio.timeout(6):
            while await rows(issues) != [orphan]:
                await origin.asyncio.sleep(0.03)
        await gateway.close()
        gateway = await self._gateway(structure_snapshot=structure)
        self.assertEqual(expected, await rows(inverse))
        self.assertEqual([orphan], await rows(issues))

    async def _assert_component_rows(self, rows):
        self.assertEqual(
            [
                ["src/UNIT_C1/UNIT_C1__tests"],
                ["src/UNIT_C1/service_pkg1"],
                ["src/UNIT_C1/service_pkg1/service_pkg1__tests"],
            ],
            await rows(
                "SELECT relative_path FROM import_nodes WHERE kind = 'package' "
                "AND relative_path LIKE 'src/UNIT_C1%' ORDER BY relative_path"
            ),
        )
        self.assertEqual(
            [
                ["package:local:src/UNIT_C1/UNIT_C1__tests", "C1"],
                [
                    (
                        "package:local:src/UNIT_C1/service_pkg1/"
                        "service_pkg1__tests"
                    ),
                    "package:local:src/UNIT_C1/service_pkg1",
                ],
            ],
            await rows(
                (
                    "SELECT source_key, target_key FROM test_edges ORDER BY "
                    "source_key"
                )
            ),
        )
        self.assertEqual(
            [["Component", "C1"]], await rows(origin._TESTS_COMPONENT)
        )

    async def test_read_issue_is_queryable_and_clears_on_the_next_scan(self):
        source = self._source("src/app/main.py", "import os\n")
        read_bytes = origin.Path.read_bytes

        def read(path):
            if path == source:
                raise PermissionError("fixture read denied")
            return read_bytes(path)

        with (
            origin.patch.object(origin.Path, "read_bytes", read),
            origin.redirect_stderr(origin.StringIO()) as errors,
        ):
            gateway = await self._gateway()
        self.assertIn("fixture read denied", errors.getvalue())
        sql = "SELECT relative_path, error_message FROM import_read_issues"
        owner = gateway._native_query
        self.assertIn("import_read_issues", owner.schema()["tables"])
        self.assertEqual(
            [["src/app/main.py", "fixture read denied"]],
            owner.run(sql, result_delivery="inline")["rows"],
        )
        owner.rebuild("import_read_issues")
        self.assertEqual([], owner.run(sql, result_delivery="inline")["rows"])

    async def test_graph_rebuild_failure_disables_queries_at_the_public_boundary(
        self,
    ):
        self._source("src/main.py", "")
        gateway = await self._gateway()
        owner = gateway._native_query
        store = owner._owner()
        async with origin.httpx2.AsyncClient(
            transport=origin.httpx2.ASGITransport(
                app=origin.Starlette(routes=origin.routes(gateway))
            ),
            base_url="http://127.0.0.1:18093",
        ) as client:
            stderr = origin.StringIO()
            with (
                origin.redirect_stderr(stderr),
                origin.patch(
                    "KERNEL_MIXER_C59.query_store.insert_rows",
                    side_effect=OSError("fixture atom insert blocked"),
                ),
            ):
                failure = await client.post(
                    "/anechoic/Anechoic/api/rebuild", json={"target": "atoms"}
                )
            self.assertEqual(400, failure.status_code)
            self.assertIn("restart required", failure.json()["error"])
            self.assertIn("fixture atom insert blocked", stderr.getvalue())
            response = await gateway.call(
                None,
                origin.types.CallToolRequestParams(
                    name="query_run",
                    arguments={"sql": "SELECT count(*) FROM atoms"},
                ),
            )
            self.assertTrue(response.is_error)
            self.assertIn("restart required", str(response.structured_content))
        with store._lock:
            self.assertGreater(
                store._connection.execute(
                    "SELECT count(*) FROM atoms"
                ).fetchone()[0],
                0,
            )
