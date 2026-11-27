"""Fast packaged runtime boundary checks against an immutable image."""

import json
import subprocess
import unittest

import tomllib

from ..FEATURE_MCP__tests__shared import run_workbench_browser
from ..workbench_docker_support import image_timeout
from .test_native_import_graph_docker_e2e import _CanaryProject


class PackagedBoundaryDockerE2E(_CanaryProject, unittest.TestCase):
    def test_openapi_uses_the_packaged_framework_version(self):
        def read(*command):
            return subprocess.check_output(
                ["docker", "exec", self.container, *command],
                text=True,
                timeout=image_timeout(10),
            )

        stack = read("printenv", "ANECHOIC_RUNTIME_STACK").strip()
        if stack == "current":
            self.skipTest("OpenAPI is packaged in beta_next")
        self.assertEqual("beta_next", stack)
        document = json.loads(
            read("cat", "/usr/local/share/anechoic/openapi.json")
        )
        version = tomllib.loads(read("cat", "/workspace/version.toml"))
        self.assertEqual(
            version["framework"]["version"], document["info"]["version"]
        )

    def test_host_write_and_delete_reach_packaged_runtime(self):
        path = self._write("fast_canary.py", "import dep.helper\n")
        sql = (
            "SELECT resolution_status FROM module_imports WHERE source_key = "
            "'module:fast_canary.py'"
        )
        self._wait_rows(sql, [["internal"]])
        path.unlink()
        self._wait_rows(sql, [])

    def test_packaged_workbench_runs_sql_in_pinned_chromium(self):
        run_workbench_browser(
            self,
            (
                "inline-results.e2e.spec.ts",
                "--grep",
                "browser fetches inline rows while MCP defaults to files",
            ),
        )
