import tempfile
import unittest
from pathlib import Path

import duckdb

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.project_database__pub import (
    LEGACY_DATABASE, PROJECT_DATABASE, migrate_project_database,
)


class ProjectDatabaseTests(unittest.TestCase):
    def test_migration_preserves_rows_and_never_overwrites_target(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            legacy = root / LEGACY_DATABASE
            legacy.parent.mkdir(parents=True)
            with duckdb.connect(str(legacy)) as connection:
                connection.execute("CREATE TABLE work_journal (event VARCHAR)")
                connection.execute("INSERT INTO work_journal VALUES ('saved')")
                connection.execute("CREATE TABLE durable_projection (value INTEGER)")
                connection.execute("INSERT INTO durable_projection VALUES (42)")
            target = migrate_project_database(root)
            self.assertEqual(root / PROJECT_DATABASE, target)
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
