"""Exercise the required functional selection through the public suite CLI."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

TOOLS = Path(__file__).resolve().parents[2]
ENTRY = TOOLS / "test_suite__pub.py"
MODULE = "LAYER_4_ENGINE_STUDIO_C14/example/test_selected.py"


class FunctionalSuiteTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        for name in ("LAYER_4_ENGINE_STUDIO_C14", "LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27", "LAYER_5_USER_SETUP_C65"):
            (self.root / name).mkdir(parents=True, exist_ok=True)
        self.module = self.root / MODULE
        self.module.parent.mkdir(parents=True)
        self.module.write_text("import unittest\nclass Test(unittest.TestCase):\n def test_ok(self): self.assertTrue(True)\n")
        self.config([MODULE])

    def test_engine_config_takes_precedence(self):
        engine = self.root / "LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72/engine/pyproject.toml"
        engine.parent.mkdir(parents=True)
        engine.write_text("[tool.ruff]\n")
        self.assertEqual(0, self.run_cli().returncode)
        engine.write_text('[tool.anechoic.test_suite]\nfunctional_test_modules = []\n')
        self.assertNotEqual(0, self.run_cli().returncode)
        engine.write_text('[tool.anechoic.test_suite]\nfunctional_test_modules = ' + json.dumps([MODULE]))
        self.assertEqual(0, self.run_cli().returncode)

    def config(self, paths):
        (self.root / "pyproject.toml").write_text(
            "[tool.anechoic.test_suite]\nfunctional_test_modules = " + json.dumps(paths) + "\n"
        )

    def run_cli(self):
        return subprocess.run(
            (sys.executable, "-B", str(ENTRY), "--project-root", str(self.root), "--phase", "unit", "--required"),
            capture_output=True, text=True, timeout=30,
        )

    def test_selected_pass_missing_failure_and_skip(self):
        passing = self.run_cli()
        self.assertEqual(0, passing.returncode, passing.stdout + passing.stderr)
        self.assertIn("tests run: 1; skipped: 0; failed modules: 0", passing.stdout)
        self.config([MODULE, "LAYER_4_ENGINE_STUDIO_C14/example/test_missing.py"])
        missing = self.run_cli()
        self.assertNotEqual(0, missing.returncode)
        self.assertIn("not discovered", missing.stderr)
        self.config([MODULE])
        self.module.write_text("import unittest\nclass Test(unittest.TestCase):\n def test_bad(self): self.fail('required failure')\n")
        failing = self.run_cli()
        self.assertNotEqual(0, failing.returncode)
        self.assertIn("required failure", failing.stderr)
        self.module.write_text("import unittest\n@unittest.skip('required skip')\nclass Test(unittest.TestCase):\n def test_skip(self): pass\n")
        skipped = self.run_cli()
        self.assertNotEqual(0, skipped.returncode)
        self.assertIn("Required functional tests skipped", skipped.stderr)
        paths = (self.root / ".anechoic_tmp/test_reports").glob("*.json")
        passed, absent, failed, skip = sorted((json.loads(path.read_text()) for path in paths),
                                             key=lambda report: report["started_at"])
        self.assertEqual(("passed", 1, MODULE), (passed["status"], passed["tests_run"], passed["modules"][0]["path"]))
        self.assertEqual(("discovery", []), (absent["step"], absent["modules"]))
        self.assertIn("required failure", failed["modules"][0]["stderr"])
        self.assertEqual(("failed", 1), (skip["status"], skip["skipped"]))

    def test_invalid_config_and_docker_selection_fail(self):
        for paths in ([], [MODULE, MODULE], [42]):
            with self.subTest(paths=paths):
                self.config(paths)
                self.assertNotEqual(0, self.run_cli().returncode)
        self.config("not a list")
        self.assertNotEqual(0, self.run_cli().returncode)
        (self.root / "pyproject.toml").write_text("[invalid\n")
        self.assertNotEqual(0, self.run_cli().returncode)
        (self.root / "pyproject.toml").unlink()
        self.assertNotEqual(0, self.run_cli().returncode)
        docker = "LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests/test_one_docker_e2e.py"
        path = self.root / docker
        path.parent.mkdir(parents=True)
        path.write_text(self.module.read_text())
        self.config([docker])
        result = self.run_cli()
        self.assertNotEqual(0, result.returncode)
        self.assertIn("functional_test_modules must select host functional tests", result.stderr)


if __name__ == "__main__":
    unittest.main()
