"""Check the native Import Graph through a disposable Docker Workbench."""

import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
from time import monotonic, sleep
import unittest
from uuid import uuid4


from .. import native_import_graph_docker_cases as docker_cases
from ..native_shared_candidate_cases import SharedCandidateCases
from MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__shared import HEALTH_PATH, WORKBENCH_PATH

from ..FEATURE_MCP__tests__shared import (
    defer_container_cleanup, docker_deadline_env, image_timeout, observing, request, write_manifest,
)


GRAPH_COUNTS = """
    SELECT count(*) FROM GRAPH_TABLE (anechoic
    MATCH (s:ImportNode)-[e:Imports]->(t:ImportNode)
    COLUMNS (s.node_key AS source_key, e.occurrence_key AS occurrence_key))
"""


def _watcher_contents(version, container):
    return ("---\nidentity: {atom_id: AN-T-9901}\n"
            f"context: {{container: {{{container}}}}}\n"
            f"state: {{status: active, version: {version}}}\n"
            "---\n\n## Summary\n\nWatcher canary.\n")




class _CanaryProject:
    @classmethod
    def setUpClass(cls):
        image = os.environ.get("ANECHOIC_IMAGE", "")
        if not re.fullmatch(r"sha256:[0-9a-f]{64}", image):
            raise RuntimeError("ANECHOIC_IMAGE must be the immutable test image ID")
        cls.root = Path(cls.enterClassContext(tempfile.TemporaryDirectory())).resolve()
        subprocess.run(["git", "init", "--quiet", str(cls.root)], check=True)
        control = "_anechoic_anechoic"
        write_manifest(cls, cls.root / control, component="C00", parameters={
            "project": {"root": {"prefix": "underscore"}},
            "runtime": {"journal": {"storage": "duckdb"}, "workbench": {"storage": "disk", "import_graph": {}}},
        })
        (cls.root / control / "001_TICKETS/TASKS").mkdir(parents=True)
        for name, contents in (("app/__init__.py", ""), ("app/main.py", "import dep.helper\nimport dep.helper\n"),
                               ("app/package.json", '{"name": "app"}\n'), ("app/frontend.js", ""),
                               ("dep/__init__.py", ""), ("dep/helper.py", "VALUE = 1\n")):
            cls._write(name, contents)
        (cls.root / "app/app__tests").mkdir()
        (cls.root / "app/app__tests/test_app.py").write_text("pass\n", encoding="utf-8")
        name = f"anechoic-import-graph-canary-{uuid4().hex}"
        defer_container_cleanup(cls.addClassCleanup, name)
        cls.container = subprocess.check_output([
            "docker", "run", "--detach", "--pull=never", "--init",
            "--name", name,
            "--label", "anechoic.test=import-graph-canary",
            "--read-only", "--tmpfs", "/tmp:rw,nosuid,nodev,size=256m",
            "--pids-limit", "128", "--cpus", "1",
            "--publish", "127.0.0.1::8092", "--volume", f"{cls.root}:/project:rw",
            "--env", "ANECHOIC_RUNTIME_NAMESPACE=docker", "--env", f"ANECHOIC_CONTROL_ROOT={control}",
            "--env", docker_deadline_env(), image, "mcp-http",
        ], text=True, timeout=image_timeout(60)).strip()
        cls._wait_ready()

    @classmethod
    def _wait_ready(cls):
        binding = subprocess.check_output(["docker", "port", cls.container, "8092/tcp"],
                                          text=True, timeout=image_timeout(10)).strip()
        if not re.fullmatch(r"127\.0\.0\.1:[0-9]+", binding):
            raise RuntimeError(f"Unexpected canary port binding: {binding!r}")
        cls.url = f"http://{binding}"
        cls.api = f"{cls.url}/anechoic/Anechoic/api"
        deadline = monotonic() + 60
        while observing(cls.container, deadline):
            try:
                if request(cls.url + HEALTH_PATH) == (200, {"state": "ready"}):
                    return
            except OSError:
                pass
            sleep(.2)
        logs = subprocess.run(["docker", "logs", "--tail", "12", cls.container],
                              capture_output=True, text=True, check=True, timeout=image_timeout(10))
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
        while actual != expected and observing(self.container, deadline):
            sleep(.1)
            actual = self._rows(sql)
        self.assertEqual(expected, actual, sql)


class WarmProjectionRestartDockerE2E(_CanaryProject, docker_cases.WarmProjectionRestartCase, unittest.TestCase):
    """Check warm restart on a fresh Project."""


class NativeImportGraphDockerE2E(
    _CanaryProject, SharedCandidateCases, docker_cases.DockerBrowserAndMcpCases, unittest.TestCase,
):
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

    def test_package_external_import_inventory(self):
        source = self._write(
            "external_fixture/imports.py",
            "import json\nimport sys\nimport dep.helper\nimport yaml\n"
            "from yaml import safe_load\nimport unavailable_fixture_module\n",
        )
        sql = (
            "SELECT language, import_name, occurrence_count FROM package_external_imports "
            "WHERE package_path = 'external_fixture'"
        )
        try:
            self._wait_rows(sql, [["python", "yaml", 2]])
            self.assertEqual([["unavailable_fixture_module"]], self._rows("""
                SELECT written_specifier FROM module_imports
                WHERE source_key = 'module:external_fixture/imports.py'
                AND resolution_status = 'unresolved'
            """))
        finally:
            source.unlink()
            source.parent.rmdir()
        self._wait_rows(sql, [])

    def test_watcher_updates_native_atom_and_relations(self):
        relative = "_anechoic_anechoic/001_TICKETS/TASKS/AN-T-9901--watcher.md"
        graph = """
            FROM GRAPH_TABLE (anechoic
            MATCH (s:Reference)-[e:CONTAINED_BY]->(t:Reference)
            COLUMNS (s.ref AS source_ref, t.kind AS target_kind, t.ref AS target_ref))
            SELECT target_kind, target_ref WHERE source_ref = 'AN-T-9901'
        """
        sql = """
            SELECT a.filename, a.reference, n.exact_ref, r.target_kind, r.target_ref
            FROM atoms a JOIN native_references n USING (relative_path, filename, reference)
            JOIN relations r ON r.source_kind = 'Atom' AND r.source_ref = a.reference
                AND r.relation_type = 'CONTAINED_BY' AND NOT r.derived
            WHERE a.reference = 'AN-T-9901'
        """

        def check(label, started, expected):
            limit = 20.0
            deadline = started + limit
            actual = self._rows(sql)
            while actual != expected and observing(self.container, deadline):
                sleep(.1)
                actual = self._rows(sql)
            elapsed = monotonic() - started
            print(f"native Atom watcher {label}: {elapsed:.3f}s", flush=True)
            self.assertEqual(expected, actual, label)
            if image_timeout(limit) is not None:
                self.assertLessEqual(elapsed, limit, label)
            self.assertEqual([expected[0][-2:]] if expected else [], self._rows(graph), label)

        started = monotonic()
        path = self._write(relative, _watcher_contents(1, "component: C00"))
        check("create", started, [[path.name, "AN-T-9901", "AN-T-9901@1", "Component", "C00"]])
        started = monotonic()
        path.write_text(_watcher_contents(2, "atom: AN-S-001"), encoding="utf-8")
        check("edit", started, [[path.name, "AN-T-9901", "AN-T-9901@2", "Atom", "AN-S-001"]])
        started = monotonic()
        path = path.rename(path.with_name("AN-T-9901--renamed.md"))
        check("rename", started, [[path.name, "AN-T-9901", "AN-T-9901@2", "Atom", "AN-S-001"]])
        started = monotonic()
        path.unlink()
        sql = """
            SELECT reference FROM atoms WHERE reference = 'AN-T-9901'
            UNION ALL SELECT reference FROM native_references WHERE reference = 'AN-T-9901'
            UNION ALL SELECT source_ref FROM relations WHERE source_ref = 'AN-T-9901'
        """
        check("delete", started, [])

    def test_watcher_stays_live_when_many_host_directories_appear(self):
        for index in range(80):
            (self.root / f"app/churn/branch_{index}").mkdir(parents=True)
        relative = "app/churn/branch_79/main.py"
        target = self._write(relative, "import dep.helper\n")
        sql = f"SELECT resolution_status FROM module_imports WHERE source_key = 'module:{relative}'"
        self._wait_rows(sql, [["internal"]])
        target.write_text("import missing_canary_resource\n", encoding="utf-8")
        self._wait_rows(sql, [["unresolved"]])
        self.assertEqual((200, {"state": "ready"}), request(self.url + HEALTH_PATH))

    def test_ignored_files_and_parse_errors_appear_as_expected(self):
        def foreground_warnings():
            logs = subprocess.run(["docker", "logs", self.container],
                                  capture_output=True, text=True, check=True, timeout=image_timeout(10))
            self.assertNotIn("import graph: policy.py: parse error:", logs.stderr)
            records = (json.loads(line) for line in logs.stderr.splitlines()
                       if line.startswith("{") and '"worker_stderr_present"' in line)
            return {record.get("correlation_id"): record for record in records
                    if record.get("code") == "worker_stderr_present"
                    and record.get("details", {}).get("phase") == "foreground"}

        before = foreground_warnings()
        self._write("generated/ignored.py", "import dep\n")
        self._write("policy.py", "import\n")
        sql = "SELECT relative_path, scan_status FROM import_nodes WHERE relative_path IN ('policy.py', 'generated/ignored.py')"
        self._wait_rows(sql, [["policy.py", "parse_error"]])
        after = foreground_warnings()
        new_runs = after.keys() - before.keys()
        self.assertTrue(new_runs, after)
        for run_id in new_runs:
            warning = after[run_id]
            self.assertRegex(run_id or "", r"^[0-9a-f]{32}$")
            self.assertRegex(warning["timestamp"], r"Z$")
            self.assertEqual(("WARNING", "C68", "worker_stderr_present", "capture", "degraded", {"phase": "foreground"}),
                             tuple(warning[key] for key in ("severity", "component", "event", "operation", "outcome", "details")))
        self._write("policy.py", "import dep\n")
        self._wait_rows(sql, [["policy.py", "parsed"]])
        ignore = self._write(".gitignore", "policy.py\n")
        self._wait_rows(sql, [])
        ignore.unlink()
        self._wait_rows(sql, [["policy.py", "parsed"]])
