"""Verify the static phase uses Ruff's mutable-default rule."""

from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.test_suite__shared import static_checks


class MutableDefaultTests(unittest.TestCase):
    def test_static_phase_rejects_mutable_default_and_accepts_fresh_value(self):
        root = Path(self.enterContext(TemporaryDirectory()))
        for name in static_checks.CODE_ROOTS:
            (root / name).mkdir(parents=True, exist_ok=True)
        config = root / "LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72/engine/pyproject.toml"
        config.parent.mkdir(parents=True)
        config.write_text("[tool.ruff]\n", encoding="utf-8")
        source = root / static_checks.CODE_ROOTS[0] / "fixture.py"
        run = subprocess.run
        output = []

        def execute(command, **kwargs):
            if "ruff" in command:
                result = run(command, capture_output=True, text=True, **kwargs)
                output.append(result.stdout)
                return result
            return SimpleNamespace(returncode=0)

        with (patch.object(static_checks.python_bytecode, "check", return_value=0),
              patch.object(static_checks.source_sizes, "check", return_value=0),
              patch.object(static_checks.python_boundaries, "check", return_value=0),
              patch.object(static_checks.subprocess, "run", side_effect=execute)):
            source.write_text("def collect(items=[]):\n    return items\n", encoding="utf-8")
            self.assertEqual(static_checks.check(root), 1)
            self.assertIn("B006", output[-1])
            source.write_text("def collect(items=None):\n    return [] if items is None else items\n", encoding="utf-8")
            self.assertEqual(static_checks.check(root), 0)
            source.write_text("def collect(items=[]):  # noqa: B006\n    return items\n", encoding="utf-8")
            self.assertEqual(static_checks.check(root), 0)


if __name__ == "__main__":
    unittest.main()
