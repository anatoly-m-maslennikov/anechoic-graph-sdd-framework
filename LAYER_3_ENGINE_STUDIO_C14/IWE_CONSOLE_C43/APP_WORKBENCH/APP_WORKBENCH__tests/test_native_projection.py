from pathlib import Path, PurePosixPath
from unittest.mock import patch
import sys
import yaml

APP_ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(APP_ROOT), str(APP_ROOT.parent / "FEATURE_PROGRAMMATIC" / "FEATURE_TOOLS"), str(Path(__file__).parent)]

from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND import native_projection  # noqa: E402
from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.native_projection import project_native, project_native_delta  # noqa: E402
from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.native_source_rows import capture_native, NativeCapture  # noqa: E402
from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.query_store import QueryStore  # noqa: E402
from smalltest_support import extension_directory  # noqa: E402
from test_native_source_rows import NativeCaptureTests  # noqa: E402


class NativeProjectionTests(NativeCaptureTests):
    def test_delta_move_relations_references_and_rollback(self):
        source = self.write("AN-T-09--task.md", "AN-T-09", "active", 2)
        header = yaml.safe_load(source.read_text().split("---\n")[1])
        header["relations"] = {"REFERENCES": ["AN-S-001"]}
        source.write_text("---\n" + yaml.safe_dump(header) + "---\n\n## Summary\n\nTask\n")
        store = QueryStore(extension_directory=extension_directory(APP_ROOT.parents[1]), native=True)
        self.addCleanup(store.close)
        bindings = dict(relation_types={"CONTAINED_BY", "CONTAINS", "REFERENCES"},
                        inverses={"CONTAINED_BY": "CONTAINS"})
        aliases = [("CA-P-2@1", "old/task.md", "AN-T-09@2")]
        project_native(store, capture_native(self.selection), migration_refs=aliases, component_ids=["C99"], **bindings)
        old_path = PurePosixPath(source.relative_to(self.root).as_posix())
        target = source.parent / "moved" / source.name
        target.parent.mkdir()
        header["relations"] = {"REFERENCES": ["AN-S-002"]}
        target.write_text("---\n" + yaml.safe_dump(header) + "---\n\n## Summary\n\nUpdated\n")
        source.unlink()
        new_path = PurePosixPath(target.relative_to(self.root).as_posix())
        capture = capture_native(self.selection)
        def fail(_graph):
            raise ValueError("injected failure")
        with self.assertRaisesRegex(ValueError, "injected failure"):
            project_native_delta(store, capture, paths={old_path, new_path}, migration_refs=aliases,
                                 before_commit=fail, **bindings)
        self.assertEqual([[old_path.as_posix()]], store.run(
            "SELECT relative_path || '/' || filename FROM atoms WHERE reference = 'AN-T-09'")["rows"])
        self.assertIn(["AN-T-09", "AN-S-001"], store.run(
            "SELECT source_ref, target_ref FROM relations WHERE relation_type = 'REFERENCES'")["rows"])
        with patch.object(native_projection, "_projected_rows", wraps=native_projection._projected_rows) as project:
            self.assertTrue(project_native_delta(store, capture, paths={old_path, new_path}, migration_refs=aliases,
                                                 **bindings))
            self.assertEqual(["AN-T-09"], [row["id"] for row in project.call_args.args[0].atoms])
        self.assertEqual([[new_path.as_posix(), "AN-T-09@2"]], store.run(
            "SELECT relative_path || '/' || filename, exact_ref FROM native_references "
            "WHERE reference = 'AN-T-09'")["rows"])
        self.assertIn(["AN-T-09", "AN-S-002"], store.run(
            "SELECT source_ref, target_ref FROM relations WHERE relation_type = 'REFERENCES'")["rows"])
        self.assertIn(("Component", "C99"), store._projection.graph.references)
        self.assertEqual(1, len(store._connection.execute("SELECT * FROM internal.native_frontier").fetchall()))
        with patch.object(store, "replace", wraps=store.replace) as replace:
            project_native(store, capture, migration_refs=aliases, component_ids=["C99"], use_retained=True, **bindings)
            self.assertTrue(replace.call_args.kwargs["reuse"])
        target.unlink()
        with self.assertRaisesRegex(ValueError, "Invalid native migration"):
            project_native_delta(store, capture_native(self.selection), paths={new_path}, migration_refs=aliases,
                                 **bindings)
        self.assertEqual([["AN-T-09@2"]], store.run(
            "SELECT exact_ref FROM native_legacy_references")["rows"])

    def test_delta_falls_back_for_schema_change_and_skips_noop_callback(self):
        source = self.write("AN-T-09--task.md", "AN-T-09", "active", 2)
        store = QueryStore(extension_directory=extension_directory(APP_ROOT.parents[1]), native=True)
        self.addCleanup(store.close)
        bindings = dict(relation_types={"CONTAINED_BY", "CONTAINS"}, inverses={"CONTAINED_BY": "CONTAINS"})
        project_native(store, capture_native(self.selection), **bindings)
        path = PurePosixPath(source.relative_to(self.root).as_posix())
        callbacks = []
        self.assertTrue(project_native_delta(store, capture_native(self.selection), paths={path},
                                             before_commit=callbacks.append, **bindings))
        self.assertEqual([], callbacks)
        header = yaml.safe_load(source.read_text().split("---\n")[1])
        header["new_field"] = "changes layout"
        source.write_text("---\n" + yaml.safe_dump(header) + "---\n\n## Summary\n\nChanged\n")
        self.assertFalse(project_native_delta(store, capture_native(self.selection), paths={path}, **bindings))
        self.assertEqual([["Example"]], store.run(
            "SELECT \"content.summary\" FROM atoms WHERE reference = 'AN-T-09'")["rows"])

    def test_delta_preserves_component_reference_owner_and_falls_back_when_removed(self):
        source = self.write("AN-T-09--task.md", "AN-T-09", "active", 2)
        capture = capture_native(self.selection)
        capture.atoms.sort(key=lambda row: row["id"] != "AN-T-09")
        store = QueryStore(extension_directory=extension_directory(APP_ROOT.parents[1]), native=True)
        self.addCleanup(store.close)
        bindings = dict(relation_types={"CONTAINED_BY", "CONTAINS"}, inverses={"CONTAINED_BY": "CONTAINS"})
        project_native(store, capture, component_ids=["C99"], **bindings)
        path = PurePosixPath(source.relative_to(self.root).as_posix())
        source.write_text(source.read_text().replace("Example", "Changed"))
        self.assertTrue(project_native_delta(store, capture_native(self.selection), paths={path}, **bindings))
        self.assertIn(("Component", "C99"), store._projection.graph.references)
        source.unlink()
        self.assertFalse(project_native_delta(store, capture_native(self.selection), paths={path}, **bindings))
        self.assertEqual([["AN-T-09"]], store.run(
            "SELECT reference FROM atoms WHERE reference = 'AN-T-09'")["rows"])

    def test_summary_projection_and_retained_upgrade(self):
        duplicate = self.write("AN-T-09--task.md", "AN-T-09", "active", 1)
        duplicate.write_text(duplicate.read_text() + "\n## Summary\n\nSecond\n")
        missing = self.write("AN-T-10--task.md", "AN-T-10", "active", 1)
        missing.write_text(missing.read_text().replace("## Summary", "## Details"))
        store = QueryStore(extension_directory=extension_directory(APP_ROOT.parents[1]))
        self.addCleanup(store.close)
        capture = capture_native(self.selection)
        bindings = dict(relation_types={"CONTAINED_BY", "CONTAINS"}, inverses={"CONTAINED_BY": "CONTAINS"})
        project_native(store, capture, **bindings)
        query = 'SELECT reference, "content.summary" FROM atoms ORDER BY reference'
        expected = [["AN-S-001", "Example"], ["AN-T-09", "Example"], ["AN-T-10", None]]
        self.assertEqual(expected, store.run(query)["rows"])
        store._connection.execute("UPDATE internal.native_frontier SET frontier = 'v1'")
        project_native(store, capture, use_retained=True, **bindings)
        self.assertEqual(expected, store.run(query)["rows"])
        project_native(store, capture, use_retained=True, **bindings)
        self.assertEqual(expected, store.run(query)["rows"])

    def test_query_real_duckdb_native_refs_and_relations(self):
        self.write("AN-T-09--task.md", "AN-T-09", "active", 2)
        self.write("AN-T-09@3-draft--task.md", "AN-T-09", "draft", 3)
        self.write("archived/AN-T-09@1--task.md", "AN-T-09", "archived", 1)
        self.write("__TKT/ASSETS/AN-T-10--asset.md", "AN-T-10", "active", 1, {"atom": "AN-T-09"})
        store = QueryStore(extension_directory=extension_directory(APP_ROOT.parents[1]))
        self.addCleanup(store.close)
        project_native(store, capture_native(self.selection), relation_types={"CONTAINED_BY", "CONTAINS"},
                       inverses={"CONTAINED_BY": "CONTAINS"})
        refs = store.run("SELECT stable_ref, exact_ref FROM native_references ORDER BY exact_ref")["rows"]
        self.assertIn(["AN-T-09", "AN-T-09@2"], refs)
        self.assertIn([None, "AN-T-09@3-draft"], refs)
        self.assertIn([None, "AN-T-09@1"], refs)
        facts = store.run("SELECT source_kind, source_ref, target_kind, target_ref, relation_type, derived FROM relations")["rows"]
        self.assertIn(["Atom", "AN-T-10", "Atom", "AN-T-09", "CONTAINED_BY", False], facts)
        self.assertIn(["Atom", "AN-T-09", "Atom", "AN-T-10", "CONTAINS", True], facts)
        self.assertIn(["Component", "C0", "Atom", "AN-T-09", "CONTAINS", True], facts)
        self.assertEqual([], store.run("SELECT * FROM scope_units")["rows"])

    def test_rejects_incomplete_capture_without_changing_store(self):
        store = QueryStore(extension_directory=extension_directory(APP_ROOT.parents[1]))
        self.addCleanup(store.close)
        with self.assertRaisesRegex(ValueError, "invalid carriers"):
            project_native(store, NativeCapture([], [], {"bad.md": "invalid"}),
                           relation_types={"CONTAINED_BY", "CONTAINS"},
                           inverses={"CONTAINED_BY": "CONTAINS"})
        self.assertEqual([], store.run("SELECT * FROM atoms")["rows"])

    def test_legacy_exact_collisions_keep_both_original_paths(self):
        self.write("archived/AN-T-09@2--first.md", "AN-T-09", "archived", 2)
        self.write("archived/AN-T-10@2--second.md", "AN-T-10", "archived", 2)
        store = QueryStore(extension_directory=extension_directory(APP_ROOT.parents[1]))
        self.addCleanup(store.close)
        capture = capture_native(self.selection)
        bindings = dict(relation_types={"CONTAINED_BY", "CONTAINS"},
                        inverses={"CONTAINED_BY": "CONTAINS"})
        refs = [
            ("CA-O-188@2", ".anechoic_c/09_operations/archive/first.md", "AN-T-09@2"),
            ("CA-O-188@2", ".anechoic_c/09_operations/archive/second.md", "AN-T-10@2"),
            ("CA-I-9@2-draft", ".anechoic_c/archive/withdrawn.md", "AN-T-09@2"),
        ]
        project_native(store, capture, migration_refs=refs, **bindings)
        query = (
            "SELECT original_path, exact_ref FROM native_legacy_references "
            "WHERE legacy_ref = 'CA-O-188@2' ORDER BY original_path"
        )
        self.assertEqual([[path, ref] for _, path, ref in refs[:2]], store.run(query)["rows"])
        self.assertEqual([["AN-T-09@2"]], store.run(
            "SELECT exact_ref FROM native_legacy_references WHERE legacy_ref = 'CA-I-9@2-draft'"
        )["rows"])
        with self.assertRaisesRegex(ValueError, "Invalid legacy migration reference"):
            project_native(store, capture,
                           migration_refs=[("CA-O-188@0", "bad.md", "AN-T-09@2")], **bindings)

    def test_legacy_revision_alias_can_target_a_renumbered_version(self):
        self.write("archived/AN-T-09@1--earlier.md", "AN-T-09", "archived", 1)
        self.write("archived/AN-T-09@2--resolved.md", "AN-T-09", "archived", 2)
        store = QueryStore(extension_directory=extension_directory(APP_ROOT.parents[1]))
        self.addCleanup(store.close)
        refs = [
            ("CA-C-453@1", ".anechoic_legacy/archive/earlier.md", "AN-T-09@1"),
            ("CA-C-453@1", ".anechoic_legacy/archive/resolved.md", "AN-T-09@2"),
        ]
        project_native(store, capture_native(self.selection), relation_types={"CONTAINED_BY", "CONTAINS"},
                       inverses={"CONTAINED_BY": "CONTAINS"}, migration_refs=refs)
        self.assertEqual([list(row) for row in refs], store.run(
            "SELECT legacy_ref, original_path, exact_ref FROM native_legacy_references ORDER BY original_path"
        )["rows"])

    def test_conflicting_migration_path_preserves_existing_projection(self):
        self.write("archived/AN-T-09@2--first.md", "AN-T-09", "archived", 2)
        self.write("archived/AN-T-10@2--second.md", "AN-T-10", "archived", 2)
        store = QueryStore(extension_directory=extension_directory(APP_ROOT.parents[1]))
        self.addCleanup(store.close)
        capture = capture_native(self.selection)
        bindings = dict(relation_types={"CONTAINED_BY", "CONTAINS"},
                        inverses={"CONTAINED_BY": "CONTAINS"})
        path = ".anechoic_c/archive/first.md"
        refs = [("CA-P-2@2", path, "AN-T-09@2"), (None, path, "AN-T-09@2")]
        project_native(store, capture, migration_refs=refs, **bindings)
        with self.assertRaisesRegex(ValueError, "Conflicting exact references"):
            project_native(store, capture, migration_refs=refs + [(None, path, "AN-T-10@2")], **bindings)
        self.assertEqual([[path, "AN-T-09@2"]], store.run(
            "SELECT original_path, exact_ref FROM native_migration_paths"
        )["rows"])

    def test_canonical_authored_relations_use_admitted_types(self):
        source = self.control / "task.md"
        header = {"atom_family": "TKT", "atom_id": "AN-T-09",
                  "structure": {"container": {"component": "C0"}, "priority": 2},
                  "context": {"template": "task", "label": "Subtask"},
                  "relations": {"REFERENCES": ["AN-S-001"]},
                  "state": {"status": "active", "version": 1,
                            "updated_at": "2026-11-19T00:00:00Z"}}
        source.write_text("---\n" + yaml.safe_dump(header) + "---\n\n## Summary\n\nTask\n")
        capture = capture_native(self.selection)
        store = QueryStore(extension_directory=extension_directory(APP_ROOT.parents[1]))
        self.addCleanup(store.close)
        bindings = {"CONTAINED_BY": "CONTAINS"}
        with self.assertRaisesRegex(ValueError, "Undeclared native relation: REFERENCES"):
            project_native(store, capture, relation_types=set(bindings) | set(bindings.values()), inverses=bindings)
        project_native(store, capture, relation_types=set(bindings) | set(bindings.values()) | {"REFERENCES"},
                       inverses=bindings)
        self.assertIn(["AN-T-09", "AN-S-001", "REFERENCES", False], store.run(
            "SELECT source_ref, target_ref, relation_type, derived FROM relations")["rows"])
        self.assertEqual([["task", "Subtask"]], store.run(
            'SELECT "header.context.template", "header.context.label" FROM atoms WHERE reference = \'AN-T-09\''
        )["rows"])

        header["relations"] = {"REFERENCES": ["AN-S-001"], "HAS_REFERENCE": ["AN-S-001", "AN-S-002@1"]}
        source.write_text("---\n" + yaml.safe_dump(header) + "---\n\n## Summary\n\nTask\n")
        bindings["HAS_REFERENCE"] = "IS_REFERENCE_FOR"
        types = set(bindings) | set(bindings.values()) | {"REFERENCES"}
        project_native(store, capture_native(self.selection), relation_types=types, inverses=bindings)
        facts = store.run("SELECT source_ref, target_ref, relation_type, derived FROM relations "
                          "WHERE relation_type IN ('REFERENCES', 'HAS_REFERENCE', 'IS_REFERENCE_FOR')")['rows']
        self.assertCountEqual(facts, [
            ["AN-T-09", "AN-S-001", "HAS_REFERENCE", False],
            ["AN-S-001", "AN-T-09", "IS_REFERENCE_FOR", True],
            ["AN-T-09", "AN-S-002@1", "HAS_REFERENCE", False],
            ["AN-S-002@1", "AN-T-09", "IS_REFERENCE_FOR", True],
        ])
        header["relations"] = {"IS_REFERENCE_FOR": ["AN-S-001"]}
        source.write_text("---\n" + yaml.safe_dump(header) + "---\n\n## Summary\n\nTask\n")
        with self.assertRaisesRegex(ValueError, "IS_REFERENCE_FOR is derived"):
            project_native(store, capture_native(self.selection), relation_types=types, inverses=bindings)

    def test_authored_cross_revision_relation_and_reprojection(self):
        source = self.write("AN-T-09--task.md", "AN-T-09", "active", 2)
        header = yaml.safe_load(source.read_text().split("---\n")[1])
        header["relations"] = {"DEPENDS_ON": ["AN-S-001@1"]}
        source.write_text("---\n" + yaml.safe_dump(header) + "---\n\n## Summary\n\nTask\n")
        store = QueryStore(extension_directory=extension_directory(APP_ROOT.parents[1]))
        self.addCleanup(store.close)
        for _ in range(2):
            project_native(store, capture_native(self.selection),
                           relation_types={"CONTAINED_BY", "CONTAINS", "DEPENDS_ON", "SUPPORTS"},
                           inverses={"CONTAINED_BY": "CONTAINS", "DEPENDS_ON": "SUPPORTS"})
        facts = store.run("SELECT source_ref, target_ref, relation_type, derived FROM relations")["rows"]
        self.assertIn(["AN-T-09", "AN-S-001@1", "DEPENDS_ON", False], facts)
        self.assertIn(["AN-S-001@1", "AN-T-09", "SUPPORTS", True], facts)
