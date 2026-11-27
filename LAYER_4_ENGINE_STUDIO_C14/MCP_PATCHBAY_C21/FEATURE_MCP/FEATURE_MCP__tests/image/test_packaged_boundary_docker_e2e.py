"""Fast packaged runtime boundary checks against an immutable image."""

import unittest

from .test_native_import_graph_docker_e2e import _CanaryProject
from ..FEATURE_MCP__tests__shared import run_workbench_browser


class PackagedBoundaryDockerE2E(_CanaryProject, unittest.TestCase):
    def test_host_write_and_delete_reach_packaged_runtime(self):
        path = self._write("fast_canary.py", "import dep.helper\n")
        sql = "SELECT resolution_status FROM module_imports WHERE source_key = 'module:fast_canary.py'"
        self._wait_rows(sql, [["internal"]])
        path.unlink()
        self._wait_rows(sql, [])

    def test_packaged_workbench_runs_sql_in_pinned_chromium(self):
        run_workbench_browser(self, (
            "inline-results.e2e.spec.ts", "--grep", "browser fetches inline rows while MCP defaults to files",
        ))
