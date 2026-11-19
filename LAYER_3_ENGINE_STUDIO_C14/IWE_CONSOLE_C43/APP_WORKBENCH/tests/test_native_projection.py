from pathlib import Path
import sys
import yaml

APP_ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(APP_ROOT), str(APP_ROOT.parent / "FEATURE_PROGRAMMATIC" / "FEATURE_TOOLS"), str(Path(__file__).parent)]

from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.native_projection import project_native  # noqa: E402
from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.native_source_rows import capture_native, NativeCapture  # noqa: E402
from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.query_store import QueryStore  # noqa: E402
from smalltest_support import extension_directory  # noqa: E402
from test_native_source_rows import NativeCaptureTests  # noqa: E402


class NativeProjectionTests(NativeCaptureTests):
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
                           migration_refs=[("CA-O-188@3", "bad.md", "AN-T-09@2")], **bindings)

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
