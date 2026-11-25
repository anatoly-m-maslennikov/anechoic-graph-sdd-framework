from hashlib import sha256
import os
from pathlib import Path, PurePosixPath
from types import SimpleNamespace
from unittest.mock import patch
import tempfile
import unittest
import yaml

APP_ROOT = Path(__file__).resolve().parents[3]

from KERNEL_MIXER_C59 import native_projection  # noqa: E402
from KERNEL_MIXER_C59.native_projection import project_native, project_native_delta  # noqa: E402
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import capture_native, NativeCapture  # noqa: E402
from KERNEL_MIXER_C59.KERNEL_MIXER_C59__shared import QueryStore  # noqa: E402


EXTENSIONS = Path(os.environ.get("ANECHOIC_DUCKPGQ_EXTENSION_DIRECTORY",
                                APP_ROOT.parents[1] / ".anechoic_tmp/workbench/extensions"))


class NativeProjectionTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(self.enterContext(tempfile.TemporaryDirectory())).resolve()
        self.control = self.root / ".anechoic_test"
        self.control.mkdir()
        self.manifest = self.write("AN-S-001-PROJECT_MANIFEST--manifest.md", "AN-S-001", "active", 1)
        self.selection = SimpleNamespace(root=self.root, control_root=self.control,
                                         manifest_path=self.manifest, project_prefix="AN",
                                         manifest_sha256=sha256(self.manifest.read_bytes()).hexdigest())

    def write(self, relative, atom_id, status, version, container=None):
        if "-T-" in atom_id and not relative.startswith("__TKT/"):
            relative = "__TKT/TASKS/" + relative
        path = self.control / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        header = {"identity": {"atom_id": atom_id}, "context": {"container": container or {"component": "C0"}},
                  "state": {"status": status, "version": version, "updated_at": "2026-11-19T00:00:00Z"}}
        path.write_text("---\n" + yaml.safe_dump(header) + "---\n\n## Summary\n\nExample\n", encoding="utf-8")
        return path

    def test_authored_relation_to_config_exact_reference(self):
        row = {"ref": "AN-P-1", "header_json": {"relations": {"REFERENCES": ["AN-C-2@3-draft"]}}}
        edges = list(native_projection._authored_edges(row, {"IS_REFERENCE"}))
        self.assertEqual(("Atom", "AN-C-2@3-draft"), (edges[0]["target_kind"], edges[0]["target_ref"]))

    def test_archived_citations_are_omitted_when_the_relation_is_retired(self):
        row = {"ref": "AN-S-1@1", "status_group": "Archived", "header_json": {"relations": {
            "IS_REFERENCE": ["AN-S-2"], "SERVES": ["AN-S-3"],
        }}}
        edges = list(native_projection._authored_edges(row, {"SERVES"}))
        self.assertEqual([("SERVES", "AN-S-3")], [(edge["relation_type"], edge["target_ref"]) for edge in edges])

    def test_historical_relations_project_to_declared_successors(self):
        relations = {
            "ADVANCES": ["AN-S-2@3-draft"], "SERVES": ["AN-S-2@3-draft"],
            "IS_ADVANCED_BY": ["AN-S-3"], "REFINES": ["AN-S-4"],
            "IS_REFINED_BY": ["AN-S-5"],
        }
        row = {"ref": "AN-S-1", "header_json": {"relations": relations},
               "content_markdown": "Archived text"}
        inverse = {"SERVES": "IS_SERVED_BY", "IS_SERVED_BY": "SERVES",
                   "CONTRIBUTES_TO": "RECEIVES_CONTRIBUTION_FROM",
                   "RECEIVES_CONTRIBUTION_FROM": "CONTRIBUTES_TO"}
        capture = NativeCapture([row], [], {})
        projected = native_projection._projected_rows(capture, set(inverse), inverse)[0]
        edges = projected["relation_edges_json"]
        self.assertEqual(8, len(edges))
        self.assertEqual({("SERVES", "AN-S-2@3-draft"), ("IS_SERVED_BY", "AN-S-3"),
                          ("CONTRIBUTES_TO", "AN-S-4"),
                          ("RECEIVES_CONTRIBUTION_FROM", "AN-S-5")},
                         {(e["relation_type"], e["target_ref"]) for e in edges if not e["derived"]})
        self.assertIn(("IS_SERVED_BY", "AN-S-2@3-draft", "AN-S-1"),
                      {(e["relation_type"], e["source_ref"], e["target_ref"]) for e in edges if e["derived"]})
        self.assertIs(relations, row["header_json"]["relations"])
        self.assertEqual("Archived text", projected["content_markdown"])

    def test_declared_historical_relation_is_not_rewritten(self):
        row = {"ref": "AN-S-1", "header_json": {"relations": {"ADVANCES": ["AN-S-2"]}}}
        capture = NativeCapture([row], [], {})
        projected = native_projection._projected_rows(capture, {"ADVANCES", "SERVES"}, {})[0]
        self.assertEqual("ADVANCES", projected["relation_edges_json"][0]["relation_type"])
        with self.assertRaisesRegex(ValueError, "Undeclared native relation: ADVANCES"):
            native_projection._projected_rows(capture, set(), {})

    def test_old_contribution_inverses_project_to_has_contribution(self):
        row = {"ref": "AN-S-1", "header_json": {"relations": {
            "IS_REFINED_BY": ["AN-S-2"], "RECEIVES_CONTRIBUTION_FROM": ["AN-S-2"],
        }}}
        inverse = {"CONTRIBUTES_TO": "HAS_CONTRIBUTION", "HAS_CONTRIBUTION": "CONTRIBUTES_TO"}
        projected, = native_projection._projected_rows(NativeCapture([row], [], {}), set(inverse), inverse)
        self.assertEqual(
            [("HAS_CONTRIBUTION", "AN-S-1", "AN-S-2", False),
             ("CONTRIBUTES_TO", "AN-S-2", "AN-S-1", True)],
            [(edge["relation_type"], edge["source_ref"], edge["target_ref"], edge["derived"])
             for edge in projected["relation_edges_json"]],
        )

    def test_delta_move_relations_references_and_rollback(self):
        source = self.write("AN-T-09--task.md", "AN-T-09", "active", 2)
        header = yaml.safe_load(source.read_text().split("---\n")[1])
        header["relations"] = {"REFERENCES": ["AN-S-001"]}
        source.write_text("---\n" + yaml.safe_dump(header) + "---\n\n## Summary\n\nTask\n")
        store = QueryStore(extension_directory=EXTENSIONS, native=True)
        self.addCleanup(store.close)
        bindings = dict(relation_types={"IS_CONTAINED_BY", "CONTAINS", "REFERENCES"},
                        inverses={"IS_CONTAINED_BY": "CONTAINS"})
        project_native(store, capture_native(self.selection), component_ids=["C99"], **bindings)
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
            project_native_delta(store, capture, paths={old_path, new_path},
                                 before_commit=fail, **bindings)
        self.assertEqual([[old_path.as_posix()]], store.run(
            "SELECT relative_path || '/' || filename FROM atoms WHERE reference = 'AN-T-09'")["rows"])
        self.assertIn(["AN-T-09", "AN-S-001"], store.run(
            "SELECT source_ref, target_ref FROM relations WHERE relation_type = 'REFERENCES'")["rows"])
        with patch.object(native_projection, "_projected_rows", wraps=native_projection._projected_rows) as project:
            self.assertTrue(project_native_delta(store, capture, paths={old_path, new_path},
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
            project_native(store, capture, component_ids=["C99"], use_retained=True, **bindings)
            self.assertTrue(replace.call_args.kwargs["reuse"])
        target.unlink()
        self.assertTrue(project_native_delta(store, capture_native(self.selection), paths={new_path},
                                             **bindings))
        self.assertEqual([], store.run("SELECT exact_ref FROM native_references WHERE reference = 'AN-T-09'")["rows"])

    def test_delta_falls_back_for_schema_change_and_skips_noop_callback(self):
        source = self.write("AN-T-09--task.md", "AN-T-09", "active", 2)
        store = QueryStore(extension_directory=EXTENSIONS, native=True)
        self.addCleanup(store.close)
        bindings = dict(relation_types={"IS_CONTAINED_BY", "CONTAINS"}, inverses={"IS_CONTAINED_BY": "CONTAINS"})
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
        store = QueryStore(extension_directory=EXTENSIONS, native=True)
        self.addCleanup(store.close)
        bindings = dict(relation_types={"IS_CONTAINED_BY", "CONTAINS"}, inverses={"IS_CONTAINED_BY": "CONTAINS"})
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
        seed = self.write("AN-S-002-SPEC-COMPONENT_SEED_MANIFEST--model-host.md", "AN-S-002", "active", 1)
        header = yaml.safe_load(seed.read_text().split("---\n")[1])
        header["context"]["template"] = "component_seed_manifest"
        seed.write_text("---\n" + yaml.safe_dump(header) + "---\n\n"
                        "# Model Host\n\n## Formal Manifest\n\n\n"
                        "## Purpose\n\nProvide the Model.\n\n## Solution\n\nLoad admitted types.\n")
        store = QueryStore(extension_directory=EXTENSIONS)
        self.addCleanup(store.close)
        capture = capture_native(self.selection)
        bindings = dict(relation_types={"IS_CONTAINED_BY", "CONTAINS"}, inverses={"IS_CONTAINED_BY": "CONTAINS"})
        project_native(store, capture, **bindings)
        query = 'SELECT reference, "content.summary" FROM atoms ORDER BY reference'
        expected = [["AN-S-001", "Example"], ["AN-S-002", "Model Host"],
                    ["AN-T-09", "Example"], ["AN-T-10", None]]
        self.assertEqual(expected, store.run(query)["rows"])
        retired = ("native_legacy_references", "native_migration_paths")
        for table in retired:
            store._connection.execute(f"CREATE TABLE main.{table} (exact_ref VARCHAR)")
        store._connection.execute("UPDATE internal.native_frontier SET frontier = 'v4'")
        project_native(store, capture, use_retained=True, **bindings)
        self.assertEqual(expected, store.run(query)["rows"])
        self.assertTrue(all(table not in store.schema()["tables"] for table in retired))
        self.assertEqual([], store._connection.execute(
            "SELECT table_name FROM information_schema.tables WHERE table_name IN (?, ?)", retired,
        ).fetchall())
        project_native(store, capture, use_retained=True, **bindings)
        self.assertEqual(expected, store.run(query)["rows"])

    def test_rejects_incomplete_capture_without_changing_store(self):
        store = QueryStore(extension_directory=EXTENSIONS)
        self.addCleanup(store.close)
        with self.assertRaisesRegex(ValueError, "invalid carriers"):
            project_native(store, NativeCapture([], [], {"bad.md": "invalid"}),
                           relation_types={"IS_CONTAINED_BY", "CONTAINS"},
                           inverses={"IS_CONTAINED_BY": "CONTAINS"})
        self.assertEqual([], store.run("SELECT * FROM atoms")["rows"])

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
        store = QueryStore(extension_directory=EXTENSIONS)
        self.addCleanup(store.close)
        bindings = {"IS_CONTAINED_BY": "CONTAINS"}
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

    def test_new_reference_model_and_flat_header(self):
        source = self.control / "001_TICKETS" / "TASKS" / "task.md"
        source.parent.mkdir(parents=True)
        header = {"atom_family": "TKT", "atom_id": "AN-T-09",
                  "container": {"component": "C0"}, "priority": 2,
                  "context": {"template": "task"},
                  "relations": {"REFERENCES": ["AN-S-001"], "IS_REFERENCE": ["AN-S-001", "AN-S-001@1"]},
                  "state": {"status": "active", "version": 1, "updated_at": "2026-11-19T00:00:00Z"}}
        source.write_text("---\n" + yaml.safe_dump(header) + "---\n\n## Summary\n\nTask\n")
        capture = capture_native(self.selection)
        self.assertEqual({}, capture.errors)
        self.assertEqual(header, next(row for row in capture.atoms if row["id"] == "AN-T-09")["header_json"])
        store = QueryStore(extension_directory=EXTENSIONS)
        self.addCleanup(store.close)
        inverse = {"IS_CONTAINED_BY": "CONTAINS", "IS_REFERENCE": "HAS_REFERENCE"}
        types = set(inverse) | set(inverse.values())
        project_native(store, capture, relation_types=types, inverses=inverse)
        facts = store.run("SELECT source_ref, target_ref, relation_type, derived FROM relations "
                          "WHERE relation_type IN ('IS_REFERENCE', 'HAS_REFERENCE')")["rows"]
        self.assertCountEqual(facts, [
            ["AN-T-09", "AN-S-001", "IS_REFERENCE", False],
            ["AN-S-001", "AN-T-09", "HAS_REFERENCE", True],
            ["AN-T-09", "AN-S-001@1", "IS_REFERENCE", False],
            ["AN-S-001@1", "AN-T-09", "HAS_REFERENCE", True],
        ])
        self.assertEqual([[2, 'C0']], store.run(
            'SELECT "header.priority", "header.container.component" FROM atoms WHERE reference = \'AN-T-09\''
        )["rows"])
        header["relations"] = {"HAS_REFERENCE": ["AN-S-001"]}
        source.write_text("---\n" + yaml.safe_dump(header) + "---\n\n## Summary\n\nTask\n")
        with self.assertRaisesRegex(ValueError, "HAS_REFERENCE is derived"):
            project_native(store, capture_native(self.selection), relation_types=types, inverses=inverse)

    def test_authored_cross_revision_relation_and_reprojection(self):
        source = self.write("AN-T-09--task.md", "AN-T-09", "active", 2)
        header = yaml.safe_load(source.read_text().split("---\n")[1])
        header["relations"] = {"DEPENDS_ON": ["AN-S-001@1"]}
        source.write_text("---\n" + yaml.safe_dump(header) + "---\n\n## Summary\n\nTask\n")
        store = QueryStore(extension_directory=EXTENSIONS)
        self.addCleanup(store.close)
        for _ in range(2):
            project_native(store, capture_native(self.selection),
                           relation_types={"IS_CONTAINED_BY", "CONTAINS", "DEPENDS_ON", "SUPPORTS"},
                           inverses={"IS_CONTAINED_BY": "CONTAINS", "DEPENDS_ON": "SUPPORTS"})
        facts = store.run("SELECT source_ref, target_ref, relation_type, derived FROM relations")["rows"]
        self.assertIn(["AN-T-09", "AN-S-001@1", "DEPENDS_ON", False], facts)
        self.assertIn(["AN-S-001@1", "AN-T-09", "SUPPORTS", True], facts)
