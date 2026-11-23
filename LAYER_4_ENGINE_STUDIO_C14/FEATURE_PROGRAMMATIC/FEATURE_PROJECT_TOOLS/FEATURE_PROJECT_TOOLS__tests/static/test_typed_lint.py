"""Tests for the configured typed-lint static-phase hook."""

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
            (root / name).mkdir()
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
              patch.object(static_checks.python_boundaries, "check", return_value=0),
              patch.object(static_checks.subprocess, "run", side_effect=execute) as run):
            self.assertEqual(static_checks.check(root), 1)
            self.assertEqual(run.call_args.args[0], ("npm", "run", "lint"))
            self.assertEqual(run.call_args.kwargs["cwd"], package)
            data["scripts"]["check:types"] = "tsc --noEmit"
            manifest.write_text(json.dumps(data), encoding="utf-8")
            self.assertEqual(static_checks.check(root), 1)
            self.assertEqual(run.call_args.args[0], ("npm", "run", "check:types"))


if __name__ == "__main__":
    unittest.main()
