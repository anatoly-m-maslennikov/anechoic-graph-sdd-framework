"""The private import cache survives reopening and rejects old versions."""
from pathlib import Path
import sys
import tempfile
import unittest

import duckdb

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from APP_WORKBENCH.FEATURE_IMPORT_GRAPH_C61.source import ImportSite, Source
from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.import_cache import clear_import_sources, read_import_sources, replace_import_sources


class ImportCacheTests(unittest.TestCase):
    def test_reopen_replace_and_invalidate(self):
        with tempfile.TemporaryDirectory() as directory:
            path = str(Path(directory) / "cache.duckdb")
            sources = {
                "a.py": Source("python", "parsed", "stat:one", (
                    ImportSite("pkg", "item", 2, 4, 3), ImportSite("os", None, 0, 5, 0),
                )),
                "a.js": Source("javascript", "unsupported", "stat:two"),
                "bad.py": Source("python", "parse_error", "stat:bad"),
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
