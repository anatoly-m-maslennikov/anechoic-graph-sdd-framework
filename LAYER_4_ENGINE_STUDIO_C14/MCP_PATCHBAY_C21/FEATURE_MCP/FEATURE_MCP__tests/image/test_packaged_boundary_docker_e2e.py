"""Fast packaged runtime boundary checks against an immutable image."""

import subprocess
import unittest

from ..FEATURE_MCP__tests__shared import run_workbench_browser
from ..workbench_docker_support import image_timeout
from .test_native_import_graph_docker_e2e import _CanaryProject


class PackagedBoundaryDockerE2E(_CanaryProject, unittest.TestCase):
    def test_image_contains_the_current_runtime(self):
        check = (
            "import os; from pathlib import Path; "
            "engine = Path('/workspace/LAYER_4_ENGINE_STUDIO_C14'); "
            "assert os.environ['ANECHOIC_RUNTIME_STACK'] == 'current'; "
            "assert (engine / 'KERNEL_MIXER_C59').is_dir(); "
            "assert not list(engine.glob('*_beta_C*')); "
            "import json; "
            "doc = json.loads(Path('/usr/local/share/anechoic/openapi.json')"
            ".read_text()); "
            "assert doc['openapi'] == '3.1.0'; "
            "assert set(doc['paths']) == {'/'}"
        )
        subprocess.run(
            ["docker", "exec", self.container, "python", "-B", "-c", check],
            check=True,
            timeout=image_timeout(10),
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
