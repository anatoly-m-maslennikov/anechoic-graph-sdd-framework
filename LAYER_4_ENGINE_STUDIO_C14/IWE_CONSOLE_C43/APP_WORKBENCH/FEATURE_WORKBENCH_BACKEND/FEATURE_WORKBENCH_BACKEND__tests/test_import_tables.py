"""Cover import-table publication, graph edges, and transaction rollback."""

import os
from pathlib import Path
import unittest
from types import SimpleNamespace

from KERNEL_MIXER_C59.graph_store import build_graph  # noqa: E402
from KERNEL_MIXER_C59.import_tables import remove_imports, replace_imports  # noqa: E402
from KERNEL_MIXER_C59.query_store import _connect  # noqa: E402


class ImportTableTests(unittest.TestCase):
    def test_graph_relations_and_transaction_rollback(self):
        extension = Path(os.environ.get(
            "ANECHOIC_DUCKPGQ_EXTENSION_DIRECTORY",
            Path(__file__).resolve().parents[5] / ".anechoic_tmp/workbench/extensions",
        ))
        connection = _connect(extension, None)
        self.addCleanup(connection.close)
        graph = build_graph(connection, [], [])
        parent = "package:local:pkg"
        test = "package:local:pkg/pkg__tests"
        nodes = [(parent, "package", "python", "pkg", None, None),
                 (test, "package", "python", "pkg/pkg__tests", None, parent)]
        connection.execute("BEGIN")
        replace_imports(connection, graph, nodes, [], [], [(test, parent)],
                        {"pkg/a.py": SimpleNamespace(status="read_error", error_message="denied")})
        connection.execute("COMMIT")
        self.assertEqual([("pkg/a.py", "denied")],
                         connection.execute("SELECT * FROM import_read_issues").fetchall())
        connection.execute("BEGIN")
        replace_imports(connection, graph, nodes, [], [], [(test, parent)], {})
        self.assertEqual([], connection.execute("SELECT * FROM import_read_issues").fetchall())
        connection.execute("ROLLBACK")
        self.assertEqual([("pkg/a.py", "denied")],
                         connection.execute("SELECT * FROM import_read_issues").fetchall())
        replace_imports(connection, graph, nodes, [], [], [(test, parent)], {})
        self.assertEqual([], connection.execute("SELECT * FROM import_read_issues").fetchall())
        for label, expected in (("TESTS", (test, parent)), ("IS_TESTED_BY", (parent, test))):
            rows = connection.execute(
                f"FROM GRAPH_TABLE (anechoic MATCH (s:ImportNode)-[e:{label}]->(d:ImportNode) "
                "COLUMNS (s.node_key, d.node_key))"
            ).fetchall()
            self.assertEqual([expected], rows)
        connection.execute("BEGIN")
        remove_imports(connection, graph)
        connection.execute("ROLLBACK")
        self.assertEqual(1, connection.execute("SELECT count(*) FROM test_edges").fetchone()[0])


if __name__ == "__main__":
    unittest.main()
