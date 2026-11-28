"""Native projection test cases."""

from . import test_native_projection as fixtures


class NativeProjectionStoreCases:
    def test_summary_projection_and_retained_upgrade(self):
        duplicate = self.write("AN-T-09--task.md", "AN-T-09", "active", 1)
        duplicate.write_text(
            duplicate.read_text() + "\n## Summary\n\nSecond\n"
        )
        missing = self.write("AN-T-10--task.md", "AN-T-10", "active", 1)
        missing.write_text(
            missing.read_text().replace("## Summary", "## Details")
        )
        seed = self.write(
            "AN-S-002-SPEC-COMPONENT_SEED_MANIFEST--model-host.md",
            "AN-S-002",
            "active",
            1,
        )
        header = fixtures.yaml.safe_load(seed.read_text().split("---\n")[1])
        header["context"]["template"] = "component_seed_manifest"
        seed.write_text(
            "---\n" + fixtures.yaml.safe_dump(header) + "---\n\n"
            "# Model Host\n\n## Formal Manifest\n\n\n"
            "## Purpose\n\nProvide the Model.\n\n## Solution\n\nLoad admitted types.\n"
        )
        store = fixtures.QueryStore(extension_directory=fixtures.EXTENSIONS)
        self.addCleanup(store.close)
        capture = fixtures.capture_native(self.selection)
        bindings = dict(
            relation_types={"CONTAINED_BY", "CONTAINS"},
            inverses={"CONTAINED_BY": "CONTAINS"},
        )
        fixtures.project_native(store, capture, **bindings)
        query = (
            'SELECT reference, "content.summary" FROM atoms ORDER BY reference'
        )
        expected = [
            ["AN-S-001", "Example"],
            ["AN-S-002", "Model Host"],
            ["AN-T-09", "Example"],
            ["AN-T-10", None],
        ]
        self.assertEqual(expected, store.run(query)["rows"])
        self._assert_retained_upgrade(
            store, capture, bindings, query, expected
        )

    def _assert_retained_upgrade(
        self, store, capture, bindings, query, expected
    ):
        retired = ("native_legacy_references", "native_migration_paths")
        for table in retired:
            store._connection.execute(
                f"CREATE TABLE main.{table} (exact_ref VARCHAR)"
            )
        store._connection.execute(
            "UPDATE internal.native_frontier SET frontier = 'v4'"
        )
        fixtures.project_native(store, capture, use_retained=True, **bindings)
        self.assertEqual(expected, store.run(query)["rows"])
        self.assertTrue(
            all(table not in store.schema()["tables"] for table in retired)
        )
        self.assertEqual(
            [],
            store._connection.execute(
                (
                    "SELECT table_name FROM information_schema.tables WHERE "
                    "table_name IN (?, ?)"
                ),
                retired,
            ).fetchall(),
        )
        fixtures.project_native(store, capture, use_retained=True, **bindings)
        self.assertEqual(expected, store.run(query)["rows"])

    def test_rejects_incomplete_capture_without_changing_store(self):
        store = fixtures.QueryStore(extension_directory=fixtures.EXTENSIONS)
        self.addCleanup(store.close)
        with self.assertRaisesRegex(ValueError, "no admitted carriers"):
            fixtures.project_native(
                store,
                fixtures.NativeCapture([], [], {"bad.md": "invalid"}),
                relation_types={"CONTAINED_BY", "CONTAINS"},
                inverses={"CONTAINED_BY": "CONTAINS"},
            )
        self.assertEqual([], store.run("SELECT * FROM atoms")["rows"])

    def test_canonical_authored_relations_use_admitted_types(self):
        source = self.control / "task.md"
        header = {
            "atom_family": "TKT",
            "atom_id": "AN-T-09",
            "structure": {"container": {"component": "C0"}, "priority": 2},
            "context": {"template": "task", "label": "Subtask"},
            "relations": {"REFERENCES": ["AN-S-001"]},
            "state": {
                "status": "active",
                "version": 1,
                "updated_at": "2026-11-19T00:00:00Z",
            },
        }
        source.write_text(
            "---\n"
            + fixtures.yaml.safe_dump(header)
            + "---\n\n## Summary\n\nTask\n"
        )
        capture = fixtures.capture_native(self.selection)
        store = fixtures.QueryStore(extension_directory=fixtures.EXTENSIONS)
        self.addCleanup(store.close)
        bindings = {"CONTAINED_BY": "CONTAINS"}
        self._assert_admitted_references(store, capture, bindings)
        self._assert_reference_inverses(store, source, header, bindings)

    def _assert_admitted_references(self, store, capture, bindings):
        with self.assertRaisesRegex(
            ValueError, "Undeclared native relation: REFERENCES"
        ):
            fixtures.project_native(
                store,
                capture,
                relation_types=set(bindings) | set(bindings.values()),
                inverses=bindings,
            )
        fixtures.project_native(
            store,
            capture,
            relation_types=set(bindings)
            | set(bindings.values())
            | {"REFERENCES"},
            inverses=bindings,
        )
        self.assertIn(
            ["AN-T-09", "AN-S-001", "REFERENCES", False],
            store.run(
                (
                    "SELECT source_ref, target_ref, relation_type, derived "
                    "FROM relations"
                )
            )["rows"],
        )
        self.assertEqual(
            [["task", "Subtask"]],
            store.run(
                (
                    'SELECT "header.context.template", "header.context.'
                    "label\" FROM atoms WHERE reference = 'AN-T-09'"
                )
            )["rows"],
        )

    def _assert_reference_inverses(self, store, source, header, bindings):
        header["relations"] = {
            "REFERENCES": ["AN-S-001"],
            "HAS_REFERENCE": ["AN-S-001", "AN-S-002@1"],
        }
        source.write_text(
            "---\n"
            + fixtures.yaml.safe_dump(header)
            + "---\n\n## Summary\n\nTask\n"
        )
        bindings["HAS_REFERENCE"] = "IS_REFERENCE_FOR"
        types = set(bindings) | set(bindings.values()) | {"REFERENCES"}
        fixtures.project_native(
            store,
            fixtures.capture_native(self.selection),
            relation_types=types,
            inverses=bindings,
        )
        facts = store.run(
            "SELECT source_ref, target_ref, relation_type, derived FROM relations "
            "WHERE relation_type IN ('REFERENCES', 'HAS_REFERENCE', 'IS_REFERENCE_FOR')"
        )["rows"]
        self.assertCountEqual(
            facts,
            [
                ["AN-T-09", "AN-S-001", "HAS_REFERENCE", False],
                ["AN-S-001", "AN-T-09", "IS_REFERENCE_FOR", True],
                ["AN-T-09", "AN-S-002@1", "HAS_REFERENCE", False],
                ["AN-S-002@1", "AN-T-09", "IS_REFERENCE_FOR", True],
            ],
        )
        header["relations"] = {"IS_REFERENCE_FOR": ["AN-S-001"]}
        source.write_text(
            "---\n"
            + fixtures.yaml.safe_dump(header)
            + "---\n\n## Summary\n\nTask\n"
        )
        with self.assertRaisesRegex(ValueError, "IS_REFERENCE_FOR is derived"):
            fixtures.project_native(
                store,
                fixtures.capture_native(self.selection),
                relation_types=types,
                inverses=bindings,
            )

    def test_new_reference_model_and_flat_header(self):
        source = self.control / "001_TICKETS" / "TASKS" / "task.md"
        source.parent.mkdir(parents=True)
        header = {
            "atom_family": "TKT",
            "atom_id": "AN-T-09",
            "container": {"component": "C0"},
            "priority": 2,
            "context": {"template": "task"},
            "relations": {
                "REFERENCES": ["AN-S-001"],
                "IS_REFERENCE": ["AN-S-001", "AN-S-001@1"],
            },
            "state": {
                "status": "active",
                "version": 1,
                "updated_at": "2026-11-19T00:00:00Z",
            },
        }
        source.write_text(
            "---\n"
            + fixtures.yaml.safe_dump(header)
            + "---\n\n## Summary\n\nTask\n"
        )
        capture = fixtures.capture_native(self.selection)
        self.assertEqual({}, capture.errors)
        self.assertEqual(
            header,
            next(row for row in capture.atoms if row["id"] == "AN-T-09")[
                "header_json"
            ],
        )
        self._assert_flat_reference_projection(source, header, capture)

    def _assert_flat_reference_projection(self, source, header, capture):
        store = fixtures.QueryStore(extension_directory=fixtures.EXTENSIONS)
        self.addCleanup(store.close)
        inverse = {"CONTAINED_BY": "CONTAINS", "IS_REFERENCE": "HAS_REFERENCE"}
        types = set(inverse) | set(inverse.values())
        fixtures.project_native(
            store, capture, relation_types=types, inverses=inverse
        )
        facts = store.run(
            "SELECT source_ref, target_ref, relation_type, derived FROM relations "
            "WHERE relation_type IN ('IS_REFERENCE', 'HAS_REFERENCE')"
        )["rows"]
        self.assertCountEqual(
            facts,
            [
                ["AN-T-09", "AN-S-001", "IS_REFERENCE", False],
                ["AN-S-001", "AN-T-09", "HAS_REFERENCE", True],
                ["AN-T-09", "AN-S-001@1", "IS_REFERENCE", False],
                ["AN-S-001@1", "AN-T-09", "HAS_REFERENCE", True],
            ],
        )
        self.assertEqual(
            [[2, "C0"]],
            store.run(
                (
                    'SELECT "header.priority", "header.container.component" '
                    "FROM atoms WHERE reference = 'AN-T-09'"
                )
            )["rows"],
        )
        header["relations"] = {"HAS_REFERENCE": ["AN-S-001"]}
        source.write_text(
            "---\n"
            + fixtures.yaml.safe_dump(header)
            + "---\n\n## Summary\n\nTask\n"
        )
        with self.assertRaisesRegex(ValueError, "HAS_REFERENCE is derived"):
            fixtures.project_native(
                store,
                fixtures.capture_native(self.selection),
                relation_types=types,
                inverses=inverse,
            )

    def test_authored_cross_revision_relation_and_reprojection(self):
        source = self.write("AN-T-09--task.md", "AN-T-09", "active", 2)
        header = fixtures.yaml.safe_load(source.read_text().split("---\n")[1])
        header["relations"] = {"DEPENDS_ON": ["AN-S-001@1"]}
        source.write_text(
            "---\n"
            + fixtures.yaml.safe_dump(header)
            + "---\n\n## Summary\n\nTask\n"
        )
        store = fixtures.QueryStore(extension_directory=fixtures.EXTENSIONS)
        self.addCleanup(store.close)
        for _ in range(2):
            fixtures.project_native(
                store,
                fixtures.capture_native(self.selection),
                relation_types={
                    "CONTAINED_BY",
                    "CONTAINS",
                    "DEPENDS_ON",
                    "SUPPORTS",
                },
                inverses={
                    "CONTAINED_BY": "CONTAINS",
                    "DEPENDS_ON": "SUPPORTS",
                },
            )
        facts = store.run(
            (
                "SELECT source_ref, target_ref, relation_type, derived FROM "
                "relations"
            )
        )["rows"]
        self.assertIn(["AN-T-09", "AN-S-001@1", "DEPENDS_ON", False], facts)
        self.assertIn(["AN-S-001@1", "AN-T-09", "SUPPORTS", True], facts)
