"""Cover import-table publication, graph edges, and transaction rollback."""
from unittest.mock import NonCallableMock

import os
from pathlib import Path
import unittest

from KERNEL_MIXER_C59.graph_store import build_graph  # noqa: E402
from KERNEL_MIXER_C59.KERNEL_MIXER_C59__shared import remove_imports, replace_imports  # noqa: E402
from KERNEL_MIXER_C59.KERNEL_MIXER_C59__shared import _connect  # noqa: E402


class ImportTableTests(unittest.TestCase):
    def setUp(self):
        extension = Path(os.environ.get(
            "ANECHOIC_DUCKPGQ_EXTENSION_DIRECTORY",
            Path(__file__).resolve().parents[5] / ".anechoic_tmp/workbench/extensions",
        ))
        self.connection = _connect(extension, None)
        self.addCleanup(self.connection.close)

    def test_graph_relations_and_transaction_rollback(self):
        connection = self.connection
        graph = build_graph(connection, [], [])
        parent = "package:local:pkg"
        test = "package:local:pkg/pkg__tests"
        nodes = [(parent, "package", "python", "pkg", None, None),
                 (test, "package", "python", "pkg/pkg__tests", None, parent)]
        connection.execute("BEGIN")
        replace_imports(connection, graph, nodes, [], [], [(test, parent)],
                        {"pkg/a.py": NonCallableMock(
                            spec_set=[
                                'status', 'error_message'
                            ],
                            status="read_error", error_message="denied")})
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

    def test_realization_replaces_empty_native_import_label(self):
        connection = self.connection
        graph = build_graph(connection, [], [], {"IMPORTS"})
        labels = ("SELECT schema, label FROM describe_property_graph('anechoic') "
                  "WHERE lower(label) = 'imports'")
        self.assertEqual([("internal", "IMPORTS")], connection.execute(labels).fetchall())
        nodes = [(key, "module", "python", f"{key}.py", None, None) for key in ("a", "b")]
        connection.execute("BEGIN")
        replace_imports(connection, graph, nodes, [], [("a", "b", "o", False)], [])
        connection.execute("COMMIT")
        self.assertEqual([("main", "Imports")], connection.execute(labels).fetchall())
        self.assertEqual([("a", "b")], connection.execute(
            "FROM GRAPH_TABLE (anechoic MATCH (s:ImportNode)-[e:Imports]->(d:ImportNode) "
            "COLUMNS (s.node_key, d.node_key))"
        ).fetchall())
        connection.execute("BEGIN")
        remove_imports(connection, graph)
        connection.execute("COMMIT")
        self.assertEqual([("internal", "IMPORTS")], connection.execute(labels).fetchall())

    def test_realization_rejects_populated_native_import_label(self):
        connection = self.connection
        fact = dict(source_kind="Atom", source_ref="a", target_kind="Atom", target_ref="b",
                    relation_type="Imports", derived=False)
        graph = build_graph(connection, [{"relation_edges_json": [fact]}], [])
        self.assertEqual([("a", "b")], connection.execute(
            'FROM GRAPH_TABLE (anechoic MATCH (s:Reference)-[e:"Imports"]->(d:Reference) '
            "COLUMNS (s.ref, d.ref))"
        ).fetchall())
        connection.execute("BEGIN")
        with self.assertRaisesRegex(ValueError, "Native IMPORTS relations conflict"):
            replace_imports(connection, graph, [], [], [], [])
        connection.execute("ROLLBACK")
        self.assertEqual([("a", "b", "Imports")], connection.execute(
            "SELECT source_ref, target_ref, relation_type FROM relations"
        ).fetchall())


if __name__ == "__main__":
    unittest.main()
