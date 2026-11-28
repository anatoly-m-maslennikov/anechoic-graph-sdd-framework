"""Check the native Import Graph through a disposable Docker Workbench."""

import os as os
from pathlib import Path as Path
import re
import subprocess
import tempfile as tempfile
from time import monotonic, sleep
import unittest
from uuid import uuid4 as uuid4


from ..integration.graph.\
    group_2 import native_import_graph_docker_cases as docker_cases
from ..integration.shared.group_1.\
    native_shared_candidate_cases import SharedCandidateCases
from MCP_PATCHBAY_C21.FEATURE_MCP.transport_support.paths.\
    paths__shared import (
    HEALTH_PATH,
    WORKBENCH_PATH as WORKBENCH_PATH,
)

from MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__tests.integration.\
    workbench.group_4.workbench_docker_support import (
    defer_container_cleanup as defer_container_cleanup,
    docker_deadline_env as docker_deadline_env,
    image_timeout,
    observing,
    request,
)
from ..FEATURE_MCP__tests__shared import (
    write_manifest as write_manifest,
)

from .canary._canary_setup_steps import CanarySetupSteps
from .canary._import_graph_steps import ImportGraphSteps


GRAPH_COUNTS = """
    SELECT count(*) FROM GRAPH_TABLE (anechoic
    MATCH (s:ImportNode)-[e:Imports]->(t:ImportNode)
    COLUMNS (s.node_key AS source_key, e.occurrence_key AS occurrence_key))
"""


def _watcher_contents(version, container):
    return (
        "---\nidentity: {atom_id: AN-T-9901}\n"
        f"context: {{container: {{{container}}}}}\n"
        f"state: {{status: active, version: {version}}}\n"
        "---\n\n## Summary\n\nWatcher canary.\n"
    )


class _CanaryProject(CanarySetupSteps):
    @classmethod
    def setUpClass(cls):
        control, image = cls._prepare_canary_project()
        name = cls._write_canary_files()
        cls._start_canary_container(control, image, name)
        cls._wait_canary_schema()

    @classmethod
    def _wait_ready(cls):
        binding = subprocess.check_output(
            ["docker", "port", cls.container, "8092/tcp"],
            text=True,
            timeout=image_timeout(10),
        ).strip()
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
            sleep(0.2)
        logs = subprocess.run(
            ["docker", "logs", "--tail", "12", cls.container],
            capture_output=True,
            text=True,
            check=True,
            timeout=image_timeout(10),
        )
        raise RuntimeError(
            (
                "Canary Workbench failed to become ready\n"
                f"{logs.stdout}"
                f"{logs.stderr}"
            )
        )

    @classmethod
    def _write(cls, relative, contents):
        path = cls.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(contents, encoding="utf-8")
        return path

    def _post(self, route, body):
        status, payload = request(
            self.api + route, method="POST", payload=body
        )
        self.assertEqual(200, status, payload)
        return payload

    def _rows(self, sql):
        return self._post("/run", {"sql": sql, "result_delivery": "inline"})[
            "rows"
        ]

    def _wait_rows(self, sql, expected):
        deadline = monotonic() + 10
        actual = self._rows(sql)
        while actual != expected and observing(self.container, deadline):
            sleep(0.1)
            actual = self._rows(sql)
        self.assertEqual(expected, actual, sql)


class WarmProjectionRestartDockerE2E(
    _CanaryProject, docker_cases.WarmProjectionRestartCase, unittest.TestCase
):
    """Check warm restart on a fresh Project."""


class NativeImportGraphDockerE2E(
    _CanaryProject,
    ImportGraphSteps,
    SharedCandidateCases,
    docker_cases.DockerBrowserAndMcpCases,
    unittest.TestCase,
):
    def test_workbench_shows_all_four_relations_and_counts_each_occurrence(
        self,
    ):
        self._check_import_relations()
        view = self._open_occurrence_view()
        self._check_occurrence_view(view)

    def test_realization_test_package_and_rebuild_follows_open_view(self):
        expected, query = self._check_test_package()
        view = self._open_realization_view(expected)
        self._check_rebuild_view(expected, query, view)

    def test_watcher_adds_renames_and_removes_targets(self):
        self._write("consumer.py", "import moving.target\n")
        sql = (
            "SELECT resolution_status FROM module_imports WHERE source_key = "
            "'module:consumer.py'"
        )
        graph = GRAPH_COUNTS + " WHERE source_key = 'module:consumer.py'"
        self._wait_rows(sql, [["unresolved"]])
        self._write("moving/__init__.py", "")
        target = self._write("moving/target.py", "VALUE = 1\n")
        self._wait_rows(sql, [["internal"]])
        self.assertEqual([[2]], self._rows(graph))
        moved = target.rename(target.with_name("moved.py"))
        self._wait_rows(sql, [["unresolved"]])
        self.assertEqual([[0]], self._rows(graph))
        self.assertEqual(
            [],
            self._rows(
                (
                    "SELECT node_key FROM import_nodes WHERE relative_path = "
                    "'moving/target.py'"
                )
            ),
        )
        moved.rename(target)
        self._wait_rows(sql, [["internal"]])
        target.unlink()
        self._wait_rows(sql, [["unresolved"]])
        self.assertEqual([[0]], self._rows(graph))

    def test_dependency_manifest_changes_resolution(self):
        self._write("declared.py", "import canary_dependency\n")
        sql = (
            "SELECT resolution_status FROM module_imports WHERE source_key = "
            "'module:declared.py'"
        )
        self._wait_rows(sql, [["unresolved"]])
        manifest = self._write(
            "pyproject.toml",
            '[project]\ndependencies = ["canary-dependency>=1"]\n',
        )
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
            self.assertEqual(
                [["unavailable_fixture_module"]],
                self._rows("""
                SELECT written_specifier FROM module_imports
                WHERE source_key = 'module:external_fixture/imports.py'
                AND resolution_status = 'unresolved'
            """),
            )
        finally:
            source.unlink()
            source.parent.rmdir()
        self._wait_rows(sql, [])

    def test_watcher_updates_native_atom_and_relations(self):
        ([relation],) = self._rows(
            "SELECT DISTINCT relation_type FROM relations "
            "WHERE relation_type IN ('CONTAINED_BY', 'IS_CONTAINED_BY') AND NOT derived"
        )
        graph = f"""
            FROM GRAPH_TABLE (anechoic
            MATCH (s:Reference)-[e:{relation}]->(t:Reference)
            COLUMNS (s.ref AS source_ref, t.kind AS target_kind, t.ref AS target_ref))
            SELECT target_kind, target_ref WHERE source_ref = 'AN-T-9901'
        """
        sql = f"""
            SELECT a.filename, a.reference, n.exact_ref, r.target_kind, r.target_ref
            FROM atoms a JOIN native_references n USING (relative_path, filename, reference)
            JOIN relations r ON r.source_kind = 'Atom' AND r.source_ref = a.reference
                AND r.relation_type = '{relation}' AND NOT r.derived
            WHERE a.reference = 'AN-T-9901'
        """

        def check(label, started, expected):
            self._check_native_atom_change(
                sql, graph, label, started, expected
            )

        path = self._create_edit_rename_atom(check)
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
        sql = (
            "SELECT resolution_status FROM module_imports WHERE source_key = "
            "'module:"
            f"{relative}"
            "'"
        )
        self._wait_rows(sql, [["internal"]])
        target.write_text("import missing_canary_resource\n", encoding="utf-8")
        self._wait_rows(sql, [["unresolved"]])
        self.assertEqual(
            (200, {"state": "ready"}), request(self.url + HEALTH_PATH)
        )

    def test_ignored_files_and_parse_errors_appear_as_expected(self):
        self._write("generated/ignored.py", "import dep\n")
        self._write("policy.py", "import\n")
        sql = (
            "SELECT relative_path, scan_status FROM import_nodes WHERE "
            "relative_path IN ('policy.py', 'generated/ignored.py')"
        )
        self._wait_rows(sql, [["policy.py", "parse_error"]])
        self._write("policy.py", "import dep\n")
        self._wait_rows(sql, [["policy.py", "parsed"]])
        ignore = self._write(".gitignore", "policy.py\n")
        self._wait_rows(sql, [])
        ignore.unlink()
        self._wait_rows(sql, [["policy.py", "parsed"]])
