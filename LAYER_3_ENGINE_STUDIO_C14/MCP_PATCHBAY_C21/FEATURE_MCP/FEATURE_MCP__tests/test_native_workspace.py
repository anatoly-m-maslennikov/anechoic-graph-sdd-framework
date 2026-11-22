"""Native Workspace operations share the native query projection."""
import unittest
from dataclasses import replace
from types import SimpleNamespace

from . import test_native_query_stdio as fixture
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.FEATURE_TOOLS__pub import resolve_native_project
from .native_query_test_support import NativeQueryOwner


class NativeWorkspaceTests(unittest.TestCase):
    setUp = fixture.NativeQueryStdioTests.setUp
    _write = fixture.NativeQueryStdioTests._write

    def test_native_workspace_views_use_one_store_and_save_in_native_journal(self):
        legacy = self.root / ".anechoic_legacy"
        legacy_saved = self.root / ".anechoic_runtime/workbench/saved_queries"
        legacy_saved.mkdir(parents=True)
        legacy_id = "q_" + "a" * 32
        (legacy_saved / f"{legacy_id}.sql").write_text("SELECT 'legacy'", encoding="utf-8")
        before = {path.relative_to(legacy): path.read_bytes() for path in legacy.rglob("*") if path.is_file()}
        inputs = fixture._native_inputs()
        selection = resolve_native_project(self.root, fixture.CONTROL, validate_manifest=inputs.validate_manifest)
        owner = NativeQueryOwner(selection, inputs)
        self.addCleanup(owner.close)
        owner.start()
        call = owner.interface_call
        opened = call("workspace_open", {"session_id": "one"})
        self.assertEqual(str(self.root), opened["project_root"])
        self.assertEqual(opened, call("workspace_get", {"workspace_id": "one"}))
        created = call("view_create", {"workspace_id": "one", "name": "Native"})
        identity = {"workspace_id": "one", "view_id": created["view_id"]}
        sql = "SELECT exact_ref FROM native_references WHERE exact_ref = 'AN-T-009@2'"
        call("view_update", identity | {"sql": sql, "expected_revision": 0})
        self.assertTrue(call("view_check", identity)["valid"])
        result = call("view_run", identity)
        self.assertEqual("success", result["status"])
        self.assertTrue(owner._store._results[result["query_id"]].pinned)
        fetched = call("view_fetch", identity | {"result_delivery": "inline"})
        self.assertEqual([["AN-T-009@2"]], fetched["rows"])
        self.assertEqual([["AN-T-009@2"]], owner.page(result["query_id"], 0, result_delivery="inline")["rows"])
        call("workspace_open", {"session_id": "other"})
        with self.assertRaisesRegex(ValueError, "unknown view_id"):
            call("view_fetch", identity | {"workspace_id": "other"})
        self._check_saved_and_reopened(owner, call, identity, sql, result, opened, selection, inputs, legacy, legacy_saved, legacy_id, before)

    def _check_saved_and_reopened(self, owner, call, identity, sql, result, opened, selection, inputs, legacy, legacy_saved, legacy_id, before):
        saved_view = call("view_save", identity)
        self.assertEqual("view", saved_view["kind"])
        self.assertEqual(sql, owner.load(saved_view["saved_query_id"])["sql"])
        saved_query = owner.run(sql, save=True, name="Bookmark", result_delivery="inline")
        self.assertEqual("query", saved_query["kind"])
        self.assertEqual(sql, owner.load(saved_query["saved_query_id"])["sql"])
        self.assertEqual({saved_view["saved_query_id"], saved_query["saved_query_id"]},
                         {item["saved_query_id"] for item in owner.saved_list()["items"]})
        with self.assertRaisesRegex(ValueError, "unavailable"):
            owner.load(legacy_id)
        self.assertEqual("SELECT 'legacy'", (legacy_saved / f"{legacy_id}.sql").read_text(encoding="utf-8"))
        self.assertTrue(list((self.root / fixture.CONTROL / "_journal").glob("workbench-saved-items-*.ndjson")))
        self.assertEqual(result["query_id"], call("view_get", identity)["result"]["query_id"])
        owner._query_log._writer.submit(lambda: None).result(timeout=10)
        logs = call("query_log_list", {})["items"]
        self.assertEqual([sql, sql], [item["sql"] for item in logs])
        self.assertEqual(logs[0], call("query_log_get", {"log_id": logs[0]["log_id"]}))
        rerun = call("view_run", identity | {"save": True, "name": "View Bookmark"})
        self.assertEqual(sql, owner.load(rerun["saved_query_id"])["sql"])
        self.assertNotIn(result["query_id"], owner._store._results)
        self.assertTrue(owner._store._results[rerun["query_id"]].pinned)
        call("view_remove", identity)
        self.assertFalse(owner._store._results[rerun["query_id"]].pinned)
        initial = {"workspace_id": "one", "view_id": opened["active_view_id"]}
        call("view_update", initial | {"sql": sql, "expected_revision": 0})
        call("view_run", initial)
        owner.close()
        reopened = NativeQueryOwner(selection, inputs)
        self.addCleanup(reopened.close)
        reopened.start()
        self.assertNotIn("result", reopened.interface_call("view_get", initial))
        self.assertEqual(before, {path.relative_to(legacy): path.read_bytes()
                                  for path in legacy.rglob("*") if path.is_file()})

    def test_manifest_journal_path_and_unsafe_paths(self):
        inputs = fixture._native_inputs()
        manifest = self.root / fixture.CONTROL / fixture.MANIFEST
        manifest.write_text(manifest.read_text(encoding="utf-8").replace(
            'prefix="AN")', 'prefix="AN", parameters={"paths": {"journal_root": "custom/journal"}})'),
            encoding="utf-8")

        def validate_manifest(fields, component):
            self.assertEqual("C0", component)
            self.assertEqual({"paths": {"journal_root": "custom/journal"}}, fields["parameters"])
            return SimpleNamespace(**fields)

        selection = resolve_native_project(self.root, fixture.CONTROL, validate_manifest=validate_manifest)
        owner = NativeQueryOwner(selection, inputs)
        self.addCleanup(owner.close)
        saved = owner.save_view("SELECT 1")
        self.assertEqual("SELECT 1", owner.load(saved["saved_query_id"])["sql"])
        self.assertTrue(list((self.root / "custom/journal").glob("*.ndjson")))
        for path in ("../escape", "/tmp/escape", ".env/journal", "custom/../escape"):
            with self.subTest(path=path), self.assertRaisesRegex(RuntimeError, "safe"):
                NativeQueryOwner(replace(selection, parameters={"paths": {"journal_root": path}}), inputs)
        for paths in (None, {"journal_root": None}):
            with self.subTest(paths=paths), self.assertRaises((ValueError, RuntimeError)):
                NativeQueryOwner(replace(selection, parameters={"paths": paths}), inputs)
        (self.root / "linked").symlink_to(self.root / "custom", target_is_directory=True)
        with self.assertRaisesRegex(RuntimeError, "symlink"):
            NativeQueryOwner(replace(selection, parameters={"paths": {"journal_root": "linked/journal"}}), inputs)

    def test_manifest_workbench_options_configure_native_store(self):
        inputs = fixture._native_inputs()
        selection = resolve_native_project(self.root, fixture.CONTROL, validate_manifest=inputs.validate_manifest)
        workbench = {"schema_mode": 1, "result_ttl_seconds": 180, "inline_result_limit_kib": 1}
        native = replace(selection, parameters={"runtime": {"workbench": workbench}})
        owner = NativeQueryOwner(native, inputs)
        self.addCleanup(owner.close)
        owner.start()
        self.assertEqual(1, owner._store._schema_mode)
        self.assertEqual(180, owner._store._result_ttl_seconds)
        small = owner.run("SELECT 'small' AS value", result_delivery="auto", result_format="csv")
        self.assertEqual('"value"\r\n"small"\r\n', small["csv"])
        large = owner.run("SELECT repeat('a', 1100) AS value", result_delivery="auto", result_format="csv")
        self.assertEqual("csv", large["result_file"]["format"])
        self.assertNotIn("csv", large)
        self.assertEqual([["AN-T-009@2"]], owner.run(
            "SELECT exact_ref FROM native_references WHERE stable_ref = 'AN-T-009'", result_delivery="inline",
        )["rows"])

    def test_native_database_does_not_follow_a_symlink(self):
        inputs = fixture._native_inputs()
        selection = resolve_native_project(self.root, fixture.CONTROL, validate_manifest=inputs.validate_manifest)
        owner = NativeQueryOwner(selection, inputs)
        self.addCleanup(owner.close)
        target = self.root / "other.duckdb"
        target.write_bytes(b"keep this file")
        database = self.root / ".anechoic_runtime/workbench/projection.duckdb"
        database.parent.mkdir(parents=True)
        database.symlink_to(target)
        with self.assertRaisesRegex(ValueError, "Project runtime directory directly"):
            owner.start()
        self.assertEqual(b"keep this file", target.read_bytes())


if __name__ == "__main__":
    unittest.main()
