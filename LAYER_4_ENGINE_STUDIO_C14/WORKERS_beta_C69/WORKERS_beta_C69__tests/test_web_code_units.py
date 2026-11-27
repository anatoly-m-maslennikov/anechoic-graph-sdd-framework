import json
import os
import subprocess
from pathlib import Path
import shutil
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from .WORKERS_beta_C69__tests__shared import command_with_fixture


SCRIPT = Path(__file__).resolve().parents[1] / "web_code_units.ts"


FRONTEND = (
    SCRIPT.parents[1]
    / "IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IWE_CONSOLE_FRONTEND"
)


class ScannerDeadlineTests(unittest.TestCase):
    def test_image_deadline_switch_controls_subprocess_wait(self):
        switch = "ANECHOIC_TEST_IMAGE_DEADLINES"
        module = "WORKERS_beta_C69.realization_graph"
        root = Path(self.enterContext(TemporaryDirectory())).resolve()
        (root / "source.ts").write_text("export const value = 1;")
        request = {"root": str(root), "config": {"python_roots": ["."]}}
        result = subprocess.CompletedProcess([], 0, stdout="[[], []]")
        original_run = subprocess.run
        timeouts = []

        def launch(command, *args, **options):
            if command[:2] == ["node", str(SCRIPT)]:
                timeouts.append(options["timeout"])
                return result
            return original_run(command, *args, **options)

        with (
            patch.dict(os.environ),
            patch("subprocess.run", side_effect=launch),
        ):
            os.environ.pop(switch, None)
            for setting, expected in ((None, 60), ("1", 60), ("0", None)):
                if setting is not None:
                    os.environ[switch] = setting
                with self.subTest(setting=setting):
                    response = command_with_fixture(module, request)
                    self.assertEqual(0, response.returncode, response.stderr)
                    graph = json.loads(response.stdout)
                    self.assertEqual(
                        ([], []),
                        (graph["code_units"], graph["code_unit_calls"]),
                    )
                    self.assertEqual(expected, timeouts[-1])
            result = subprocess.CompletedProcess([], 2, stderr="bad graph")
            response = command_with_fixture(module, request)
            self.assertEqual(1, response.returncode)
            self.assertIn(
                "Code Unit scanner failed: bad graph", response.stderr
            )
        self.assertEqual([60, 60, None, None], timeouts)


@unittest.skipUnless(
    shutil.which("node") and (FRONTEND / "node_modules/typescript").is_dir(),
    "Framework web parser is unavailable",
)
class WebCodeUnitTests(unittest.TestCase):
    def test_imports_methods_shadowing_and_ambiguous_imports(self):
        data = {
            "sources": {
                "a.ts": "export const f = () => 1; export class C { static m() {} }",
                "b.ts": (
                    "import * as x from './a'; function g(f: () => void) { "
                    "f(); x.f(); x.C.m(); new x.C(); } x.f();"
                ),
                "c.ts": "import { f } from './ambiguous'; f();",
                "other.ts": "export function f() {}",
            },
            "imports": {
                "b.ts": [[1, "./a", "a.ts"]],
                "c.ts": [
                    [1, "./ambiguous", "a.ts"],
                    [1, "./ambiguous", "other.ts"],
                ],
            },
        }
        result = subprocess.run(
            ["node", str(SCRIPT)],
            input=json.dumps(data),
            text=True,
            capture_output=True,
            check=True,
        )
        units, calls = json.loads(result.stdout)
        by_name = {(unit[1], unit[3]): unit[0] for unit in units}
        assert {(source, target) for source, target, _, _ in calls} == {
            (by_name[("module:b.ts", "g")], by_name[("module:a.ts", "f")]),
            (by_name[("module:b.ts", "g")], by_name[("module:a.ts", "C.m")]),
        }
