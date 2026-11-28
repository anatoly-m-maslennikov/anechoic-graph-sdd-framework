"""Native projection test cases."""

from . import test_native_projection as fixtures


class NativeProjectionDeltaCases:
    def test_delta_move_relations_references_and_rollback(self):
        source, header, store, bindings = self._setup_delta_move()
        old_path = fixtures.PurePosixPath(
            source.relative_to(self.root).as_posix()
        )
        target = source.parent / "moved" / source.name
        target.parent.mkdir()
        header["relations"] = {"REFERENCES": ["AN-S-002"]}
        target.write_text(
            "---\n"
            + fixtures.yaml.safe_dump(header)
            + "---\n\n## Summary\n\nUpdated\n"
        )
        source.unlink()
        new_path = fixtures.PurePosixPath(
            target.relative_to(self.root).as_posix()
        )
        capture = fixtures.capture_native(self.selection)

        self._assert_move_rollback(
            store, capture, old_path, new_path, bindings
        )
        self._assert_moved_projection(
            store, capture, old_path, new_path, bindings
        )
        self._assert_retained_and_removed(
            store, capture, target, new_path, bindings
        )

    def _setup_delta_move(self):
        source = self.write("AN-T-09--task.md", "AN-T-09", "active", 2)
        header = fixtures.yaml.safe_load(source.read_text().split("---\n")[1])
        header["relations"] = {"REFERENCES": ["AN-S-001"]}
        source.write_text(
            "---\n"
            + fixtures.yaml.safe_dump(header)
            + "---\n\n## Summary\n\nTask\n"
        )
        store = fixtures.QueryStore(
            extension_directory=fixtures.EXTENSIONS, native=True
        )
        self.addCleanup(store.close)
        bindings = dict(
            relation_types={"CONTAINED_BY", "CONTAINS", "REFERENCES"},
            inverses={"CONTAINED_BY": "CONTAINS"},
        )
        fixtures.project_native(
            store,
            fixtures.capture_native(self.selection),
            component_ids=["C99"],
            **bindings,
        )
        return source, header, store, bindings

    def _assert_move_rollback(
        self, store, capture, old_path, new_path, bindings
    ):
        def fail(_graph):
            raise ValueError("injected failure")

        with self.assertRaisesRegex(ValueError, "injected failure"):
            fixtures.project_native_delta(
                store,
                capture,
                paths={old_path, new_path},
                before_commit=fail,
                **bindings,
            )
        self.assertEqual(
            [[old_path.as_posix()]],
            store.run(
                (
                    "SELECT relative_path || '/' || filename FROM atoms "
                    "WHERE reference = 'AN-T-09'"
                )
            )["rows"],
        )
        self.assertIn(
            ["AN-T-09", "AN-S-001"],
            store.run(
                (
                    "SELECT source_ref, target_ref FROM relations WHERE "
                    "relation_type = 'REFERENCES'"
                )
            )["rows"],
        )

    def _assert_moved_projection(
        self, store, capture, old_path, new_path, bindings
    ):
        with fixtures.patch.object(
            fixtures.native_projection,
            "_projected_rows",
            wraps=fixtures.native_projection._projected_rows,
        ) as project:
            self.assertTrue(
                fixtures.project_native_delta(
                    store, capture, paths={old_path, new_path}, **bindings
                )
            )
            self.assertEqual(
                ["AN-T-09"],
                [row["id"] for row in project.call_args.args[0].atoms],
            )
        self.assertEqual(
            [[new_path.as_posix(), "AN-T-09@2"]],
            store.run(
                "SELECT relative_path || '/' || filename, exact_ref FROM native_references "
                "WHERE reference = 'AN-T-09'"
            )["rows"],
        )
        self.assertIn(
            ["AN-T-09", "AN-S-002"],
            store.run(
                (
                    "SELECT source_ref, target_ref FROM relations WHERE "
                    "relation_type = 'REFERENCES'"
                )
            )["rows"],
        )
        self.assertIn(("Component", "C99"), store._projection.graph.references)
        self.assertEqual(
            1,
            len(
                store._connection.execute(
                    "SELECT * FROM internal.native_frontier"
                ).fetchall()
            ),
        )

    def _assert_retained_and_removed(
        self, store, capture, target, new_path, bindings
    ):
        with fixtures.patch.object(
            store, "replace", wraps=store.replace
        ) as replace:
            fixtures.project_native(
                store,
                capture,
                component_ids=["C99"],
                use_retained=True,
                **bindings,
            )
            self.assertTrue(replace.call_args.kwargs["reuse"])
        target.unlink()
        self.assertTrue(
            fixtures.project_native_delta(
                store,
                fixtures.capture_native(self.selection),
                paths={new_path},
                **bindings,
            )
        )
        self.assertEqual(
            [],
            store.run(
                (
                    "SELECT exact_ref FROM native_references WHERE reference "
                    "= 'AN-T-09'"
                )
            )["rows"],
        )

    def test_delta_falls_back_for_schema_change_and_skips_noop_callback(self):
        source = self.write("AN-T-09--task.md", "AN-T-09", "active", 2)
        store = fixtures.QueryStore(
            extension_directory=fixtures.EXTENSIONS, native=True
        )
        self.addCleanup(store.close)
        bindings = dict(
            relation_types={"CONTAINED_BY", "CONTAINS"},
            inverses={"CONTAINED_BY": "CONTAINS"},
        )
        fixtures.project_native(
            store, fixtures.capture_native(self.selection), **bindings
        )
        path = fixtures.PurePosixPath(source.relative_to(self.root).as_posix())
        callbacks = []
        self.assertTrue(
            fixtures.project_native_delta(
                store,
                fixtures.capture_native(self.selection),
                paths={path},
                before_commit=callbacks.append,
                **bindings,
            )
        )
        self.assertEqual([], callbacks)
        self._assert_schema_change_fallback(source, store, path, bindings)

    def _assert_schema_change_fallback(self, source, store, path, bindings):
        header = fixtures.yaml.safe_load(source.read_text().split("---\n")[1])
        header["new_field"] = "changes layout"
        source.write_text(
            "---\n"
            + fixtures.yaml.safe_dump(header)
            + "---\n\n## Summary\n\nChanged\n"
        )
        self.assertFalse(
            fixtures.project_native_delta(
                store,
                fixtures.capture_native(self.selection),
                paths={path},
                **bindings,
            )
        )
        self.assertEqual(
            [["Example"]],
            store.run(
                (
                    'SELECT "content.summary" FROM atoms WHERE reference = '
                    "'AN-T-09'"
                )
            )["rows"],
        )

    def test_delta_preserves_component_reference_owner_and_falls_back_when_removed(
        self,
    ):
        source = self.write("AN-T-09--task.md", "AN-T-09", "active", 2)
        capture = fixtures.capture_native(self.selection)
        capture.atoms.sort(key=lambda row: row["id"] != "AN-T-09")
        store = fixtures.QueryStore(
            extension_directory=fixtures.EXTENSIONS, native=True
        )
        self.addCleanup(store.close)
        bindings = dict(
            relation_types={"CONTAINED_BY", "CONTAINS"},
            inverses={"CONTAINED_BY": "CONTAINS"},
        )
        fixtures.project_native(
            store, capture, component_ids=["C99"], **bindings
        )
        path = fixtures.PurePosixPath(source.relative_to(self.root).as_posix())
        source.write_text(source.read_text().replace("Example", "Changed"))
        self.assertTrue(
            fixtures.project_native_delta(
                store,
                fixtures.capture_native(self.selection),
                paths={path},
                **bindings,
            )
        )
        self.assertIn(("Component", "C99"), store._projection.graph.references)
        source.unlink()
        self.assertFalse(
            fixtures.project_native_delta(
                store,
                fixtures.capture_native(self.selection),
                paths={path},
                **bindings,
            )
        )
        self.assertEqual(
            [["AN-T-09"]],
            store.run(
                "SELECT reference FROM atoms WHERE reference = 'AN-T-09'"
            )["rows"],
        )
