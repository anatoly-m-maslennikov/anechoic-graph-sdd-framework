"Verify the required host functional gate is separate from source analysis."

from contextlib import redirect_stderr, redirect_stdout
import io
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from .. import test_suite__shared as suite
from ..test_suite__shared import _test_phase


class FunctionalPhaseTest(unittest.TestCase):
    def setUp(self):
        self.directory = TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name).resolve()
        for name in suite.CODE_ROOTS:
            (self.root / name).mkdir(parents=True)
        self.base = "LAYER_4_ENGINE_STUDIO_C14/EXAMPLE/EXAMPLE__tests"

    def file(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        return path

    def config(self, names):
        self.file(
            "pyproject.toml",
            "[tool.anechoic.test_suite]\nfunctional_test_modules = "
            + repr(names)
            + "\n",
        )

    def test_cli_runs_configured_flat_and_functional_once_without_static(self):
        paths = [
            f"{self.base}/test_flat.py",
            f"{self.base}/functional/test_api.py",
        ]
        marker = self.root / "runs"
        for path in paths:
            self.file(
                path,
                "import unittest\nclass Test(unittest.TestCase):\n def test_one(self):\n"
                f'  with open({str(marker)!r}, "a") as f: f.write("{path}\\n")\n',
            )
        self.file("LAYER_4_ENGINE_STUDIO_C14/unused.py", "import os\n")
        self.config(paths)
        command = [
            sys.executable,
            "-B",
            str(Path(suite.__file__).with_name("test_suite__pub.py")),
            "--project-root",
            str(self.root),
            "--phase",
            "functional",
        ]
        result = subprocess.run(
            command, capture_output=True, text=True, timeout=30
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertCountEqual(paths, marker.read_text().splitlines())
        for path in paths:
            self.assertEqual(
                1, result.stdout.count("Test module START: " + path)
            )
        self.assertNotIn("Static check:", result.stdout)

    def test_invalid_configurations_and_static_selection_fail_closed(self):
        flat = f"{self.base}/test_flat.py"
        static = f"{self.base}/static/test_analyzer.py"
        image = f"{self.base}/image/test_docker.py"
        for name in (flat, static, image):
            self.file(
                name,
                (
                    "import unittest\nclass Test(unittest.TestCase):\n def "
                    "test_one(self): pass\n"
                ),
            )
        cases = (
            ([], "selection is empty"),
            ([flat, flat], "selection contains duplicates"),
            (["missing.py"], "selection is not discovered: missing.py"),
            ([flat, static], "must select host functional tests"),
            ([image], "must select host functional tests"),
        )
        for selection, reason in cases:
            with self.subTest(selection=selection):
                self.config(selection)
                with (
                    patch.object(suite, "_run_static_checks") as static_check,
                    patch.object(suite, "run_module") as run,
                    redirect_stderr(io.StringIO()) as errors,
                ):
                    self.assertEqual(
                        1, suite.run_full_suite(self.root, phase="functional")
                    )
                self.assertIn(reason, errors.getvalue())
                static_check.assert_not_called()
                run.assert_not_called()
        self.assertEqual("static", _test_phase(self.root, self.root / static))
        self.assertEqual("image", _test_phase(self.root, self.root / image))

    def test_required_skip_fails_functional_phase(self):
        name = f"{self.base}/functional/test_skip.py"
        self.file(
            name,
            (
                'import unittest\n@unittest.skip("unavailable")\nclass '
                "Test(unittest.TestCase):\n def test_one(self): pass\n"
            ),
        )
        self.config([name])
        report = {}
        with (
            redirect_stdout(io.StringIO()),
            redirect_stderr(io.StringIO()) as errors,
        ):
            self.assertEqual(
                1,
                suite.run_full_suite(
                    self.root, phase="functional", report=report
                ),
            )
        self.assertIn("Required functional tests skipped", errors.getvalue())
        (module,) = report["modules"]
        self.assertEqual(
            (name, "failed", 1, 1),
            (
                module["path"],
                module["status"],
                module["tests_run"],
                module["skipped"],
            ),
        )
