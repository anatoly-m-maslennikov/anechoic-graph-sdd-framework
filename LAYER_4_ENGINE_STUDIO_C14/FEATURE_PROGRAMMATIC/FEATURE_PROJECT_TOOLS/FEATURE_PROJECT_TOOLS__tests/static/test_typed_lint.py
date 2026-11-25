"""Tests for the configured typed-lint static-phase hook."""

from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.test_suite__shared import static_checks


class TypedLintTests(unittest.TestCase):
    def test_only_configured_typed_lint_packages_gate_the_static_phase(self):
        root = Path(self.enterContext(TemporaryDirectory()))
        for name in static_checks.CODE_ROOTS:
            (root / name).mkdir(parents=True, exist_ok=True)
        package = root / static_checks.CODE_ROOTS[0] / "frontend"
        package.mkdir()
        manifest = package / "package.json"
        data = {"scripts": {"lint": "eslint ."}, "devDependencies": {
            "eslint": "*", "typescript-eslint": "*"}}
        manifest.write_text(json.dumps(data), encoding="utf-8")
        self.assertEqual(list(static_checks.npm_static_commands(root)), [])
        (package / "eslint.config.js").write_text("export default []\n", encoding="utf-8")
        self.assertEqual(list(static_checks.npm_static_commands(root)), [(package, "lint")])

        def execute(command, **kwargs):
            return SimpleNamespace(returncode=int(command[0] == "npm"))

        with (patch.object(static_checks.python_bytecode, "check", return_value=0),
              patch.object(static_checks.source_sizes, "check", return_value=0),
              patch.object(static_checks.source_languages, "check", return_value=0),
              patch.object(static_checks.python_boundaries, "check", return_value=0),
              patch.object(static_checks.subprocess, "run", side_effect=execute) as run):
            self.assertEqual(static_checks.check(root), 1)
            self.assertEqual(run.call_args.args[0], ("npm", "run", "lint"))
            self.assertEqual(run.call_args.kwargs["cwd"], package)
            data["scripts"]["check:types"] = "tsc --noEmit"
            manifest.write_text(json.dumps(data), encoding="utf-8")
            self.assertEqual(static_checks.check(root), 1)
            self.assertEqual(run.call_args.args[0], ("npm", "run", "check:types"))

    def test_language_gate_reports_baseline_and_enforces_only_when_enabled(self):
        gate = static_checks.source_languages
        root = Path(self.enterContext(TemporaryDirectory())).resolve()
        config = root / "LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72/engine/pyproject.toml"
        config.parent.mkdir(parents=True)
        config.write_text("[tool.anechoic.test_suite]\n", encoding="utf-8")
        python = Path("model.py")
        web = Path("app.jsx")
        (root / python).write_text("from dataclasses import dataclass\n@dataclass\nclass M: pass\n")
        (root / web).write_text("const x = 1;\n")
        with (patch.object(gate.source_comments, "source_paths", return_value=[python, web]) as paths,
              redirect_stdout(StringIO()) as output, redirect_stderr(StringIO()) as errors):
            self.assertEqual(gate.check(root), 0)
            self.assertIn("2 findings", output.getvalue())
            self.assertEqual(errors.getvalue(), "")
            paths.assert_called_with(root, gate.SUFFIXES, (".",))
            config.write_text("[tool.anechoic.test_suite]\nenforce_source_languages = true\n")
            self.assertEqual(gate.check(root), 1)
            self.assertIn("model.py:2:", errors.getvalue())
            self.assertIn("app.jsx", errors.getvalue())
            config.write_text('[tool.anechoic.test_suite]\nenforce_source_languages = "yes"\n')
            self.assertEqual(gate.check(root), 1)
            self.assertIn("must be a boolean", errors.getvalue())


if __name__ == "__main__":
    unittest.main()
