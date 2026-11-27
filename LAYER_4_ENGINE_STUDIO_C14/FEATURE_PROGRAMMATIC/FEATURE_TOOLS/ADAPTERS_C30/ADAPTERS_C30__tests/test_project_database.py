import tempfile
import unittest
from pathlib import Path

import duckdb

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
    console_state_path,
    migrate_project_database,
)


class ProjectDatabaseTests(unittest.TestCase):
    def test_state_selection_and_database_copy_after_an_offline_rename(self):
        root = Path(self.enterContext(tempfile.TemporaryDirectory())).resolve()
        runtime = root / ".anechoic_runtime"
        old, new = runtime / "workbench", runtime / "iwe_console"
        self.assertEqual(new, console_state_path(root))
        self.assertFalse(runtime.exists())
        old.mkdir(parents=True)
        self.assertEqual(old, console_state_path(root))
        with duckdb.connect(str(old / "projection.duckdb")) as connection:
            connection.execute("CREATE TABLE work_journal AS SELECT 'saved' AS event")
        old.rename(new)
        self.assertEqual(new, console_state_path(root))
        with duckdb.connect(str(migrate_project_database(root))) as connection:
            self.assertEqual([("saved",)], connection.execute(
                "SELECT event FROM work_journal",
            ).fetchall())
        self.assertFalse(old.exists())

    def test_state_selection_rejects_conflicting_directories(self):
        root = Path(self.enterContext(tempfile.TemporaryDirectory())).resolve()
        runtime = root / ".anechoic_runtime"
        for name in ("workbench", "iwe_console"):
            (runtime / name).mkdir(parents=True)
        with self.assertRaisesRegex(ValueError, "Both IWE Console and Workbench"):
            console_state_path(root)

    def test_state_selection_rejects_symlinks_and_files(self):
        for relative in (".anechoic_runtime", ".anechoic_runtime/workbench",
                         ".anechoic_runtime/iwe_console"):
            with self.subTest(relative=relative), tempfile.TemporaryDirectory() as directory:
                root = Path(directory).resolve()
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.symlink_to(root / "missing", target_is_directory=True)
                with self.assertRaisesRegex(ValueError, "runtime directories directly"):
                    console_state_path(root)
                path.unlink()
                path.touch()
                with self.assertRaisesRegex(ValueError, "runtime directories directly"):
                    console_state_path(root)

    def test_migration_preserves_rows_and_never_overwrites_target(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            legacy = root / ".anechoic_runtime/workbench/projection.duckdb"
            legacy.parent.mkdir(parents=True)
            with duckdb.connect(str(legacy)) as connection:
                connection.execute("CREATE TABLE work_journal (event VARCHAR)")
                connection.execute("INSERT INTO work_journal VALUES ('saved')")
                connection.execute("CREATE TABLE durable_projection (value INTEGER)")
                connection.execute("INSERT INTO durable_projection VALUES (42)")
            target = migrate_project_database(root)
            self.assertEqual(root / ".anechoic_runtime/db/project.duckdb", target)
            with duckdb.connect(str(target)) as connection:
                self.assertEqual([('saved',)], connection.execute('SELECT * FROM work_journal').fetchall())
                self.assertEqual([(42,)], connection.execute('SELECT * FROM durable_projection').fetchall())
                connection.execute("INSERT INTO work_journal VALUES ('new')")
            self.assertEqual(target, migrate_project_database(root))
            with duckdb.connect(str(target)) as connection:
                self.assertEqual(2, connection.execute('SELECT count(*) FROM work_journal').fetchone()[0])
            self.assertTrue(legacy.is_file())

    def test_missing_database_does_not_create_one(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            self.assertFalse(migrate_project_database(root).exists())
