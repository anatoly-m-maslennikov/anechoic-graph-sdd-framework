from pathlib import Path
import os
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from APP_WORKBENCH.FEATURE_IMPORT_GRAPH_C61.resolution import resolve_realization
from APP_WORKBENCH.FEATURE_IMPORT_GRAPH_C61.source import Source, capture, relevant_change


class RealizationTests(unittest.TestCase):
    def test_direct_test_packages_follow_source_inventory(self):
        tmp_path = Path(self.enterContext(TemporaryDirectory())).resolve()
        subprocess.run(["git", "init", "--quiet", str(tmp_path)], check=True)
        for name in ("pkg/pkg__tests/test_one.py", "pkg/other__tests/test_two.py",
                     "other/pkg__tests/test_three.py", "pkg/pkg__tests/nested/test_four.py"):
            path = tmp_path / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("pass\n")
        sources = capture(tmp_path, None)
        nodes, occurrences, edges, tests = resolve_realization(tmp_path, sources)
        packages = {node[0]: node for node in nodes if node[1] == "package"}
        assert ("package:local:pkg/pkg__tests", "package:local:pkg") in tests
        assert tests == [("package:local:pkg/pkg__tests", "package:local:pkg")]
        assert packages["package:local:pkg/pkg__tests"][1] == "package"
        assert not occurrences and not edges
        assert relevant_change(tmp_path, [{"new_path": "pkg/pkg__tests", "old_path": None}], {})

    def test_graph_relations_and_transaction_rollback(self):
        from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.graph_store import build_graph
        from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.import_tables import remove_imports, replace_imports
        from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.query_store import _connect

        extension = Path(os.environ.get("ANECHOIC_DUCKPGQ_EXTENSION_DIRECTORY",
                                        Path(__file__).resolve().parents[5] / ".anechoic_tmp/workbench/extensions"))
        connection = _connect(extension, None)
        graph = build_graph(connection, [], [])
        parent = "package:local:pkg"
        test = "package:local:pkg/pkg__tests"
        nodes = [(parent, "package", "python", "pkg", None, None),
                 (test, "package", "python", "pkg/pkg__tests", None, parent)]
        connection.execute("BEGIN")
        replace_imports(connection, graph, nodes, [], [], [(test, parent)],
                        {"pkg/a.py": Source("python", "read_error", "stat:a", error_message="denied")})
        connection.execute("COMMIT")
        assert connection.execute("SELECT * FROM import_read_issues").fetchall() == [("pkg/a.py", "denied")]
        connection.execute("BEGIN")
        replace_imports(connection, graph, nodes, [], [], [(test, parent)], {})
        assert connection.execute("SELECT * FROM import_read_issues").fetchall() == []
        connection.execute("ROLLBACK")
        assert connection.execute("SELECT * FROM import_read_issues").fetchall() == [("pkg/a.py", "denied")]
        replace_imports(connection, graph, nodes, [], [], [(test, parent)], {})
        assert connection.execute("SELECT * FROM import_read_issues").fetchall() == []
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

    def test_mixed_package_and_import_pairs(self):
        root = Path(self.enterContext(TemporaryDirectory())).resolve()
        for name, content in {"pkg/package.json": '{"name":"pkg"}',
                              "pkg/a.py": "import other.b\n", "pkg/app.js": "",
                              "pkg/pkg__tests/test.py": "", "pkg/pkg__tests/test.js": "",
                              "pkg/pkg__tests/package.json": '{"name":"tests"}',
                              "other/b.py": ""}.items():
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
        nodes, _, edges, tests = resolve_realization(root, capture(root, None))
        packages = [node for node in nodes if node[1] == "package" and node[3] == "pkg"]
        assert len(packages) == 1
        node_by_key = {node[0]: node for node in nodes}
        assert node_by_key["module:pkg/app.js"][5] == packages[0][0] == node_by_key["module:pkg/a.py"][5]
        assert tests == [("package:local:pkg/pkg__tests", "package:local:pkg")]
        assert {(source, target) for source, target, _, _ in edges} == {
            ("module:pkg/a.py", "module:other/b.py"), ("module:pkg/a.py", "package:local:other"),
            ("package:local:pkg", "module:other/b.py"), ("package:local:pkg", "package:local:other"),
        }
        (root / "pkg/a.py").unlink()
        (root / "pkg/pkg__tests/test.py").unlink()
        nodes, _, _, tests = resolve_realization(root, capture(root, None))
        assert [node[0] for node in nodes if node[1] == "package" and node[3] == "pkg"] == ["package:local:pkg"]
        assert tests == [("package:local:pkg/pkg__tests", "package:local:pkg")]

    def test_read_error_is_retried_on_next_capture_without_stat_change(self):
        root = Path(self.enterContext(TemporaryDirectory())).resolve()
        path = root / "a.py"
        path.write_text("import os\n")
        with patch.object(Path, "read_bytes", side_effect=PermissionError("denied")) as read:
            failed = capture(root, None)
        assert read.call_count == 1
        assert failed["a.py"].status == "read_error"
        assert failed["a.py"].error_message == "denied"
        recovered = capture(root, failed, changes=[{"new_path": "other.py", "old_path": None}])
        assert recovered["a.py"].status == "parsed"
        assert recovered["a.py"].signature == failed["a.py"].signature
        assert recovered["a.py"].error_message is None
        path.unlink()
        assert capture(root, failed, changes=[{"new_path": None, "old_path": "a.py"}]) == {}
