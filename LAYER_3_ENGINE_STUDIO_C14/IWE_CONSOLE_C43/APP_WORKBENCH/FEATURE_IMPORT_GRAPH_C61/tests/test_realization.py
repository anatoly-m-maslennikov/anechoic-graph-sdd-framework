from pathlib import Path
import os
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from APP_WORKBENCH.FEATURE_IMPORT_GRAPH_C61.resolution import resolve_realization
from APP_WORKBENCH.FEATURE_IMPORT_GRAPH_C61.source import capture, relevant_change


def test_direct_test_packages_follow_source_inventory(tmp_path):
    for name in ("pkg/pkg__tests/test_one.py", "pkg/other__tests/test_two.py",
                 "other/pkg__tests/test_three.py", "pkg/pkg__tests/nested/test_four.py"):
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("pass\n")
    sources = capture(tmp_path, None)
    nodes, occurrences, edges, tests = resolve_realization(tmp_path, sources)
    packages = {node[0]: node for node in nodes if node[1] == "package"}
    assert ("package:python:pkg/pkg__tests", "package:python:pkg") in tests
    assert tests == [("package:python:pkg/pkg__tests", "package:python:pkg")]
    assert packages["package:python:pkg/pkg__tests"][1] == "package"
    assert not occurrences and not edges
    assert relevant_change(tmp_path, [{"new_path": "pkg/pkg__tests", "old_path": None}], {})


def test_graph_relations_and_transaction_rollback():
    from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.graph_store import build_graph
    from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.import_tables import remove_imports, replace_imports
    from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.query_store import _connect

    extension = Path(os.environ.get("ANECHOIC_DUCKPGQ_EXTENSION_DIRECTORY",
                                    Path(__file__).resolve().parents[5] / ".anechoic_tmp/workbench/extensions"))
    connection = _connect(extension, None)
    graph = build_graph(connection, [], [])
    parent = "package:python:pkg"
    test = "package:python:pkg/pkg__tests"
    nodes = [(parent, "package", "python", "pkg", None, None),
             (test, "package", "python", "pkg/pkg__tests", None, parent)]
    connection.execute("BEGIN")
    replace_imports(connection, graph, nodes, [], [], [(test, parent)])
    connection.execute("COMMIT")
    for label, expected in (("TESTS", (test, parent)), ("IS_TESTED_BY", (parent, test))):
        rows = connection.execute(
            f"FROM GRAPH_TABLE (anechoic MATCH (s:ImportNode)-[e:{label}]->(d:ImportNode) "
            "COLUMNS (s.node_key, d.node_key))"
        ).fetchall()
        assert rows == [expected]
    connection.execute("BEGIN")
    remove_imports(connection, graph)
    connection.execute("ROLLBACK")
    assert connection.execute("SELECT count(*) FROM test_edges").fetchone()[0] == 1
    connection.close()
