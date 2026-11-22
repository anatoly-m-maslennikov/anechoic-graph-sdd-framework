"""Beta admission preserves the Project binding wire contract."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from .WORKBENCH_BACKEND_beta_C70__tests__shared import ENGINE, ROOT, write_project

MODULE = "FEATURE_PROGRAMMATIC.FEATURE_MODEL.FEATURE_MODEL_VALIDATION.project_admission__pub"


class ProjectAdmissionTests(unittest.TestCase):
    def test_native_manifest_and_binding_rejection(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            write_project(root)
            request = {"project_root": str(root), "control_root": None, "instance_id": None, "host_root": None}
            bad = {**request, "host_root": str(root)}
            result = subprocess.run(
                [sys.executable, "-B", "-P", "-m", MODULE], cwd=ROOT,
                env={**os.environ, "PYTHONPATH": str(ENGINE)},
                input=json.dumps(request) + "\n" + json.dumps(bad) + "\n{}\n",
                capture_output=True, text=True, timeout=30, check=True,
            )
            good, rejected, malformed = map(json.loads, result.stdout.splitlines())
            self.assertIn("result", good, good)
            self.assertEqual("AN", good["result"]["project_prefix"])
            self.assertEqual("AN-S-001@3", good["result"]["manifest_ref"])
            self.assertEqual("_anechoic_anechoic", good["result"]["control_relative"])
            self.assertEqual("project_selection_error", rejected["error"]["code"])
            self.assertEqual("project_selection_error", malformed["error"]["code"])


if __name__ == "__main__":
    unittest.main()
