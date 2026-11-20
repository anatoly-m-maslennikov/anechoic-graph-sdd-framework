"""Check the native Import Graph through a disposable Docker Workbench."""

import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from time import monotonic, sleep
import unittest
from uuid import uuid4

import test_native_startup as fixture
from http_paths import HEALTH_PATH, WORKBENCH_PATH

sys.path.insert(0, str(fixture.MCP.parents[1] / "IWE_CONSOLE_C43/APP_WORKBENCH/APP_WORKBENCH__tests"))
from workbench_docker_support import request


GRAPH_COUNTS = """
    SELECT count(*) FROM GRAPH_TABLE (anechoic
    MATCH (s:ImportNode)-[e:Imports]->(t:ImportNode)
    COLUMNS (s.node_key AS source_key, e.occurrence_key AS occurrence_key))
"""


class NativeImportGraphDockerE2E(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        image = os.environ.get("ANECHOIC_IMAGE", "")
        if not re.fullmatch(r"sha256:[0-9a-f]{64}", image):
            raise RuntimeError("ANECHOIC_IMAGE must be the immutable test image ID")
        cls.root = Path(cls.enterClassContext(tempfile.TemporaryDirectory())).resolve()
        subprocess.run(["git", "init", "--quiet", str(cls.root)], check=True)
        control = ".anechoic_anechoic"
        fixture.RuntimeSelectionTests.manifest(cls, cls.root / control, component="C00", parameters={
            "runtime": {"workbench": {"import_graph": {}}},
        })
        cls._write("app/__init__.py", "")
        cls._write("app/main.py", "import dep.helper\nimport dep.helper\n")
        cls._write("app/package.json", '{"name": "app"}\n')
        cls._write("app/frontend.js", "")
        cls._write("dep/__init__.py", "")
        cls._write("dep/helper.py", "VALUE = 1\n")
        (cls.root / "app/app__tests").mkdir()
        cls.container = subprocess.check_output([
            "docker", "run", "--detach", "--pull=never", "--init",
            "--name", f"anechoic-import-graph-canary-{uuid4().hex}",
            "--label", "anechoic.test=import-graph-canary",
            "--read-only", "--tmpfs", "/tmp:rw,nosuid,nodev,size=256m",
            "--publish", "127.0.0.1::8092", "--volume", f"{cls.root}:/project:rw",
            "--env", "ANECHOIC_RUNTIME_NAMESPACE=docker", "--env", f"ANECHOIC_CONTROL_ROOT={control}",
            image, "mcp-http",
        ], text=True, timeout=60).strip()
        cls.addClassCleanup(subprocess.run, ["docker", "container", "rm", "-f", cls.container],
                            check=True, capture_output=True, timeout=30)
        binding = subprocess.check_output(["docker", "port", cls.container, "8092/tcp"],
                                          text=True, timeout=10).strip()
        if not re.fullmatch(r"127\.0\.0\.1:[0-9]+", binding):
            raise RuntimeError(f"Unexpected canary port binding: {binding!r}")
        cls.url = f"http://{binding}"
        cls.api = f"{cls.url}/anechoic/Anechoic/api"
        deadline = monotonic() + 60
        while monotonic() < deadline:
            try:
                if request(cls.url + HEALTH_PATH) == (200, {"ready": True}):
                    return
            except OSError:
                pass
            sleep(.2)
        logs = subprocess.run(["docker", "logs", "--tail", "12", cls.container],
                              capture_output=True, text=True, check=True, timeout=10)
        raise RuntimeError(f"Canary Workbench failed to become ready\n{logs.stdout}{logs.stderr}")

    @classmethod
    def _write(cls, relative, contents):
        path = cls.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(contents, encoding="utf-8")
        return path

    def _post(self, route, body):
        status, payload = request(self.api + route, method="POST", payload=body)
        self.assertEqual(200, status, payload)
        return payload

    def _rows(self, sql):
        return self._post("/run", {"sql": sql, "result_delivery": "inline"})["rows"]

    def _wait_rows(self, sql, expected):
        deadline = monotonic() + 10
        actual = self._rows(sql)
        while actual != expected and monotonic() < deadline:
            sleep(.1)
            actual = self._rows(sql)
        self.assertEqual(expected, actual, sql)

    def test_workbench_shows_all_four_relations_and_counts_each_occurrence(self):
        status, page = request(f"{self.url}{WORKBENCH_PATH}/Anechoic")
        self.assertEqual(200, status)
        self.assertIn("Workbench", page)
        tables = self._post("/schema", {})["tables"]
        self.assertTrue({"import_nodes", "module_imports", "import_edges", "package_imports"} <= tables.keys())
        self.assertEqual([["module", "module", 2], ["module", "package", 2],
                          ["package", "module", 2], ["package", "package", 2]], self._rows("""
            SELECT s.kind, t.kind, count(*) FROM import_edges e
            JOIN import_nodes s ON s.node_key = e.source_key
            JOIN import_nodes t ON t.node_key = e.target_key
            JOIN module_imports i USING (occurrence_key)
            WHERE i.source_key = 'module:app/main.py' GROUP BY ALL ORDER BY ALL
        """))
        graph = GRAPH_COUNTS + " JOIN module_imports i USING (occurrence_key) WHERE i.source_key = 'module:app/main.py'"
        self.assertEqual([[8]], self._rows(graph))
        query = "SELECT occurrence_count FROM package_imports WHERE source_key = 'package:local:app'"
        workspace = self._post("/interface", {"operation": "workspace_open", "arguments": {"session_id": "imports"}})
        view = {"workspace_id": workspace["workspace_id"], "view_id": workspace["active_view_id"]}
        for operation, args in (("view_update", {"sql": query, "expected_revision": 0}), ("view_run", {})):
            self._post("/interface", {"operation": operation, "arguments": view | args})
        result = self._post("/interface", {"operation": "view_fetch", "arguments": view | {"result_delivery": "inline"}})
        self.assertEqual([[2]], result["rows"])

    def test_realization_test_package_and_rebuild_follows_open_view(self):
        query = """
            SELECT parent.node_key, parent.kind, test.node_key, test.kind, test.package_type
            FROM tested_by_edges e
            JOIN import_nodes parent ON parent.node_key = e.source_key
            JOIN import_nodes test ON test.node_key = e.target_key
            WHERE parent.relative_path = 'app'
        """
        expected = [["package:local:app", "package", "package:local:app/app__tests",
                     "package", "Test Package"]]
        self.assertEqual(expected, self._rows(query))
        self.assertEqual([["package:local:app"], ["package:local:app"]], self._rows("""
            SELECT package_key FROM import_nodes
            WHERE relative_path IN ('app/main.py', 'app/frontend.js') ORDER BY relative_path
        """))
        for label, source, target in (("TESTS", expected[0][2], expected[0][0]),
                                      ("IS_TESTED_BY", expected[0][0], expected[0][2])):
            self.assertEqual([[source, target]], self._rows(f"""
                FROM GRAPH_TABLE (anechoic
                MATCH (s:ImportNode)-[e:{label}]->(t:ImportNode)
                COLUMNS (s.node_key AS source_key, t.node_key AS target_key))
                WHERE source_key = '{source}' AND target_key = '{target}'
            """))
        workspace = self._post("/interface", {"operation": "workspace_open",
                                               "arguments": {"session_id": "realization-canary"}})
        view = {"workspace_id": workspace["workspace_id"], "view_id": workspace["active_view_id"]}
        self._post("/interface", {"operation": "view_update",
                                  "arguments": view | {"sql": query, "expected_revision": 0}})
        first = self._post("/interface", {"operation": "view_run", "arguments": view})["query_id"]
        rebuilt = self._post("/rebuild", {"target": "all"})
        second = rebuilt["result_ids"][first]
        self.assertNotEqual(first, second)
        fetched = self._post("/interface", {"operation": "view_fetch",
                                           "arguments": view | {"result_delivery": "inline"}})
        self.assertEqual((second, expected), (fetched["query_id"], fetched["rows"]))

    def test_watcher_adds_renames_and_removes_targets(self):
        self._write("consumer.py", "import moving.target\n")
        sql = "SELECT resolution_status FROM module_imports WHERE source_key = 'module:consumer.py'"
        graph = GRAPH_COUNTS + " WHERE source_key = 'module:consumer.py'"
        self._wait_rows(sql, [["unresolved"]])
        self._write("moving/__init__.py", "")
        target = self._write("moving/target.py", "VALUE = 1\n")
        self._wait_rows(sql, [["internal"]])
        self.assertEqual([[2]], self._rows(graph))
        moved = target.rename(target.with_name("moved.py"))
        self._wait_rows(sql, [["unresolved"]])
        self.assertEqual([[0]], self._rows(graph))
        self.assertEqual([], self._rows("SELECT node_key FROM import_nodes WHERE relative_path = 'moving/target.py'"))
        moved.rename(target)
        self._wait_rows(sql, [["internal"]])
        target.unlink()
        self._wait_rows(sql, [["unresolved"]])
        self.assertEqual([[0]], self._rows(graph))

    def test_dependency_manifest_changes_resolution(self):
        self._write("declared.py", "import canary_dependency\n")
        sql = "SELECT resolution_status FROM module_imports WHERE source_key = 'module:declared.py'"
        self._wait_rows(sql, [["unresolved"]])
        manifest = self._write("pyproject.toml", '[project]\ndependencies = ["canary-dependency>=1"]\n')
        self._wait_rows(sql, [["external"]])
        manifest.unlink()
        self._wait_rows(sql, [["unresolved"]])

    def test_ignored_files_and_parse_errors_appear_as_expected(self):
        self._write("generated/ignored.py", "import dep\n")
        self._write("policy.py", "import\n")
        sql = "SELECT relative_path, scan_status FROM import_nodes WHERE relative_path IN ('policy.py', 'generated/ignored.py')"
        self._wait_rows(sql, [["policy.py", "parse_error"]])
        logs = subprocess.run(["docker", "logs", self.container], capture_output=True, text=True, check=True, timeout=10)
        self.assertIn("import graph: policy.py: parse error:", logs.stderr)
        self._write("policy.py", "import dep\n")
        self._wait_rows(sql, [["policy.py", "parsed"]])
        ignore = self._write(".gitignore", "policy.py\n")
        self._wait_rows(sql, [])
        ignore.unlink()
        self._wait_rows(sql, [["policy.py", "parsed"]])
