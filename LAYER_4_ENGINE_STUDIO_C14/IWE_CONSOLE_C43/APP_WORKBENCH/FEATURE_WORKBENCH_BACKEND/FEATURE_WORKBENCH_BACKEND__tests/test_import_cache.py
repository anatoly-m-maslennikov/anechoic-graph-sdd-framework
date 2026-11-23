"""The private import cache survives reopening and rejects old versions."""
from pathlib import Path
import tempfile
import unittest

import duckdb

from KERNEL_MIXER_C59.KERNEL_MIXER_C59__shared import (
    clear_import_sources, read_import_sources, replace_import_sources,
)
from KERNEL_MIXER_C59.KERNEL_MIXER_C59__shared import _create_external_imports_view
from IWE_CONSOLE_C43.APP_WORKBENCH.FEATURE_IMPORT_GRAPH_C61.import_graph__shared import ImportSite, Source


class ImportCacheTests(unittest.TestCase):
    def test_external_imports_view_counts_occurrences_and_excludes_stdlib(self):
        connection = duckdb.connect()
        self.addCleanup(connection.close)
        connection.execute("CREATE TABLE import_nodes (node_key VARCHAR, kind VARCHAR, language VARCHAR, "
                           "relative_path VARCHAR, package_key VARCHAR)")
        connection.execute("CREATE TABLE module_imports (source_key VARCHAR, target_key VARCHAR, "
                           "resolution_status VARCHAR, type_only BOOLEAN)")
        connection.executemany("INSERT INTO import_nodes VALUES (?, ?, ?, ?, ?)", [
            ("package:local:app", "package", "python", "app", None),
            ("module:app/a.py", "module", "python", "app/a.py", "package:local:app"),
            ("package:external:requests", "package", "python", None, None),
            ("package:external:json", "package", "python", None, None),
        ])
        connection.executemany("INSERT INTO module_imports VALUES (?, ?, ?, ?)", [
            ("module:app/a.py", "package:external:requests", "external", False),
            ("module:app/a.py", "package:external:requests", "external", True),
            ("module:app/a.py", "package:external:json", "external", False),
        ])
        _create_external_imports_view(connection)
        self.assertEqual([("app", "python", "requests", 2, 1)], connection.execute(
            "SELECT * FROM package_external_imports").fetchall())
        connection.execute("DELETE FROM module_imports WHERE type_only")
        _create_external_imports_view(connection)
        self.assertEqual([("app", "python", "requests", 1, 0)], connection.execute(
            "SELECT * FROM package_external_imports").fetchall())

    def test_reopen_replace_and_invalidate(self):
        with tempfile.TemporaryDirectory() as directory:
            path = str(Path(directory) / "cache.duckdb")
            sources = {
                "a.py": Source("python", "parsed", "stat:one", (
                    ImportSite("pkg", "item", 2, 4, 3), ImportSite("os", None, 0, 5, 0),
                )),
                "a.js": Source("javascript", "parsed", "stat:two", (
                    ImportSite("@playwright/test", "../package.json", 0, 1, 0, True),
                )),
                "bad.py": Source("python", "parse_error", "stat:bad"),
                "denied.py": Source("python", "read_error", "stat:denied", error_message="denied"),
            }
            connection = duckdb.connect(path)
            self.assertEqual({}, read_import_sources(connection))
            connection.execute("BEGIN")
            replace_import_sources(connection, sources)
            connection.execute("COMMIT")
            connection.close()
            connection = duckdb.connect(path)
            self.assertEqual(sources, read_import_sources(connection))
            updated = {"bad.py": sources["bad.py"], "a.js": Source("javascript", "unsupported", "stat:new")}
            replace_import_sources(connection, updated, sources)
            self.assertEqual(updated, read_import_sources(connection))
            connection.execute("UPDATE _anechoic_import_cache.version SET version = -1")
            self.assertEqual({}, read_import_sources(connection))
            replace_import_sources(connection, {"a.js": sources["a.js"]})
            self.assertEqual({"a.js": sources["a.js"]}, read_import_sources(connection))
            clear_import_sources(connection)
            self.assertEqual({}, read_import_sources(connection))
            connection.close()


if __name__ == "__main__":
    unittest.main()
