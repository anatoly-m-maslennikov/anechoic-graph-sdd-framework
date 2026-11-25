"""Check bounded disk spill and retained query restrictions."""

import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

import duckdb

from ..DATABASE_SERVER_beta_C71__shared import open_database
from .DATABASE_SERVER_beta_C71__tests__shared import PIN, _launch_arguments


class QueryEngineSpillTest(unittest.TestCase):
    def test_disk_and_memory_settings_remain_locked(self):
        with TemporaryDirectory(dir="/tmp") as directory:
            root = Path(directory).resolve()
            _, environment = _launch_arguments(root / "db.sock")
            with patch.dict(os.environ, environment):
                for path in (root / "projection.duckdb", None):
                    with self.subTest(path=path):
                        connection = open_database(str(path) if path else None, PIN, "instance")
                        try:
                            values = dict(connection.execute("SELECT name, value FROM duckdb_settings() "
                                "WHERE name IN ('temp_directory', 'max_temp_directory_size', 'memory_limit')").fetchall())
                            self.assertEqual("244.1 MiB", values["memory_limit"])
                            self.assertEqual(str(path) + ".tmp" if path else "", values["temp_directory"])
                            if path:
                                self.assertEqual("488.2 MiB", values["max_temp_directory_size"])
                            with self.assertRaises(duckdb.Error):
                                connection.execute("SET enable_external_access = true")
                            with self.assertRaises(duckdb.Error):
                                connection.execute("SELECT * FROM read_text('/etc/passwd')")
                        finally:
                            connection.close()
