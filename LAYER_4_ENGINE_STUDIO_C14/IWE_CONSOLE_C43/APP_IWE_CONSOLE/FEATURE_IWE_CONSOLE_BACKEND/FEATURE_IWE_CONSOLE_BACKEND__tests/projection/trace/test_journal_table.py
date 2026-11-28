from __future__ import annotations
from unittest.mock import NonCallableMock

import json
from hashlib import sha256
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


from KERNEL_MIXER_C59.KERNEL_MIXER_C59__shared import QueryStore  # noqa: E402
from KERNEL_MIXER_C59.KERNEL_MIXER_C59__shared import QueryExecutionError
from KERNEL_MIXER_C59.native_projection import project_native  # noqa: E402

# fmt: off
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.sources.inventory.inventory__shared import (
    capture_native,
)
from IWE_CONSOLE_C43.APP_IWE_CONSOLE.FEATURE_IMPORT_GRAPH_C61 \
    .SOURCE_CAPTURE.SOURCE_CAPTURE__shared import Source
from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.FEATURE_PROJECT_TOOLS__tests \
    .FEATURE_PROJECT_TOOLS__tests__shared import extension_directory
# fmt: on
from KERNEL_MIXER_C59.KERNEL_MIXER_C59__shared import publish_imports
from KERNEL_MIXER_C59.KERNEL_MIXER_C59__shared import (  # noqa: E402
    read_import_sources,
    replace_import_sources,
)


APP_ROOT = Path(__file__).resolve().parents[5]


class JournalTableTest(unittest.TestCase):
    def store(
        self,
        database: Path | None,
        journal: Path | None,
        *,
        disk: bool = False,
    ) -> QueryStore:
        return QueryStore(
            extension_directory=extension_directory(APP_ROOT.parents[1]),
            database_path=database,
            journal_path=journal,
            journal_disk=disk,
        )

    def _assert_sync(self, store, root, inbox, name, record):
        with patch(
            "KERNEL_MIXER_C59.journal_table.os.unlink",
            side_effect=OSError("interrupted"),
        ):
            with self.assertRaisesRegex(OSError, "interrupted"):
                store.sync_work_journal(root)
        self.assertTrue((inbox / name).exists())
        store.sync_work_journal(root)
        store.sync_work_journal(root)
        self.assertFalse((inbox / name).exists())
        self.assertEqual([record["event"]], store.work_journal_events("a"))
        self.assertEqual([], store.work_journal_events("other"))
        self.assertEqual(
            [[1]],
            store.run("SELECT count(*) FROM main.work_journal")["rows"],
        )
        self.assertIn("work_journal", store.schema()["tables"])
        with self.assertRaises(ValueError):
            store.run("DELETE FROM main.work_journal")
        store.replace([], [])
        self.assertEqual(
            [[1]],
            store.run("SELECT count(*) FROM main.work_journal")["rows"],
        )

    def test_disk_and_memory_import_restart_and_read_only_history(
        self,
    ) -> None:
        for memory in (False, True):
            with (
                self.subTest(memory=memory),
                tempfile.TemporaryDirectory() as temporary,
            ):
                root = Path(temporary).resolve()
                database = root / "projection.duckdb"
                if memory:
                    prior = self.store(database, database, disk=True)
                    prior.close()
                inbox = root / ".anechoic_runtime/workbench/journal-inbox"
                inbox.mkdir(parents=True)
                name = "019c6e27-e55b-73d1-87d8-4e01f1f75043.json"
                record = {
                    "author": "a",
                    "local_date": "2026-11-21",
                    "event": {"sql": "SELECT 1"},
                }
                (inbox / name).write_text(
                    json.dumps(record, sort_keys=True, separators=(",", ":"))
                )
                (inbox / "invalid.json").write_text("ignored")
                (
                    inbox / "019c6e27-e55c-73d1-87d8-4e01f1f75043.json"
                ).symlink_to(inbox / name)
                store = self.store(
                    None if memory else database, database, disk=True
                )
                try:
                    self._assert_sync(store, root, inbox, name, record)
                finally:
                    store.close()
                self._assert_journal_history(root, database, record)

    def _assert_journal_history(self, root, database, record):
        history = self.store(None, database)
        try:
            history.sync_work_journal(root)
            self.assertEqual(
                [record["event"]], history.work_journal_events("a")
            )
            self.assertEqual(
                [[1]],
                history.run("SELECT count(*) FROM main.work_journal")["rows"],
            )
        finally:
            history.close()
        restarted = self.store(database, database)
        try:
            self.assertEqual(
                [record["event"]], restarted.work_journal_events("a")
            )
        finally:
            restarted.close()

    def test_unselected_journal_does_not_create_database_or_consume_inbox(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            database = root / "missing.duckdb"
            inbox = root / ".anechoic_runtime/workbench/journal-inbox"
            inbox.mkdir(parents=True)
            record = inbox / "019c6e27-e55b-73d1-87d8-4e01f1f75043.json"
            record.write_text("pending")
            store = self.store(None, database)
            try:
                store.sync_work_journal(root)
                self.assertEqual([], store.work_journal_events("a"))
                self.assertFalse(database.exists())
                self.assertTrue(record.exists())
                self.assertNotIn("work_journal", store.schema()["tables"])
            finally:
                store.close()

    def test_invalid_record_is_preserved(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            inbox = root / ".anechoic_runtime/workbench/journal-inbox"
            inbox.mkdir(parents=True)
            record = inbox / "019c6e27-e55b-73d1-87d8-4e01f1f75043.json"
            record.write_text("not json")
            store = self.store(None, root / "journal.duckdb", disk=True)
            try:
                with self.assertRaisesRegex(
                    RuntimeError, "invalid Work Journal inbox record"
                ):
                    store.sync_work_journal(root)
                self.assertTrue(record.exists())
                self.assertEqual([], store.work_journal_events("a"))
            finally:
                store.close()

    def _write_disk_projection(self, database, capture, bindings, options):
        disk = QueryStore(database_path=database, **options)
        try:
            project_native(disk, capture, **bindings)
            publish_imports(
                disk,
                [("disk", "package", "python", "disk", "ok", None)],
                [],
                [],
            )
            replace_import_sources(
                disk._connection,
                {"disk.py": Source("python", "ok", "disk")},
            )
        finally:
            disk.close()

    def test_memory_projection_ignores_attached_disk_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            control = root / ".anechoic_test"
            control.mkdir()
            manifest = control / "AN-S-001-PROJECT_MANIFEST--manifest.md"
            manifest.write_text(
                "---\nidentity:\n  atom_id: AN-S-001\ncontext:\n"
                "  container:\n    component: C0\n"
                "state:\n  status: active\n  version: 1\n"
                "  updated_at: '2026-11-19T00:00:00Z'\n"
                "---\n\n## Summary\n\nExample\n"
            )
            selection = NonCallableMock(
                spec_set=[
                    "root",
                    "control_root",
                    "manifest_path",
                    "project_prefix",
                    "manifest_sha256",
                ],
                root=root,
                control_root=control,
                manifest_path=manifest,
                project_prefix="AN",
                manifest_sha256=sha256(manifest.read_bytes()).hexdigest(),
            )
            capture = capture_native(selection)
            bindings = dict(
                relation_types={"CONTAINED_BY", "CONTAINS"},
                inverses={"CONTAINED_BY": "CONTAINS"},
            )
            database = root / "projection.duckdb"
            options = dict(
                extension_directory=extension_directory(APP_ROOT.parents[1]),
                native=True,
                journal_path=database,
                journal_disk=True,
            )
            self._write_disk_projection(database, capture, bindings, options)
            memory = QueryStore(**options)
            try:
                self._assert_memory_projection(memory, capture, bindings)
            finally:
                memory.close()

    def _assert_memory_projection(self, memory, capture, bindings):
        self.assertFalse(memory._initialized)
        self.assertEqual({}, read_import_sources(memory._connection))
        project_native(memory, capture, use_retained=True, **bindings)
        columns = memory.schema()["tables"]["atoms"]
        self.assertEqual(
            len(columns), len({column["name"] for column in columns})
        )
        self.assertNotIn("import_nodes", memory.schema()["tables"])
        with self.assertRaises(QueryExecutionError):
            memory.run("SELECT * FROM main.import_nodes")
        publish_imports(
            memory,
            [("memory", "package", "python", "memory", "ok", None)],
            [],
            [],
        )
        replace_import_sources(
            memory._connection, {"memory.py": Source("python", "ok", "memory")}
        )
        self.assertEqual(
            [["memory"]],
            memory.run("SELECT node_key FROM main.import_nodes")["rows"],
        )
        self.assertEqual(
            [("disk",)],
            memory._connection.execute(
                "SELECT node_key FROM journal_store.main.import_nodes"
            ).fetchall(),
        )
        self.assertEqual(
            [("disk.py",)],
            memory._connection.execute(
                "SELECT path FROM journal_store._anechoic_import_cache.sources"
            ).fetchall(),
        )


if __name__ == "__main__":
    unittest.main()
