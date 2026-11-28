"""Test the full-suite entry point with fixtures."""

from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor
from contextlib import redirect_stderr, redirect_stdout
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch
from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS import (
    test_suite__shared as full,
)


# fmt: off
from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.FEATURE_PROJECT_TOOLS__tests \
    import full_suite_cases as cases
# fmt: on
APP = full.APP
FullSuiteCases = cases.FullSuiteCases
TOOLS = Path(__file__).resolve().parents[2]
PASSING = (
    "import unittest\nclass Test(unittest.TestCase"
    "):\n def test_one(self): self.assertTrue(True"
    ")\n"
)
PASSED_COUNT = full.RESULT_MARKER + '{"tests":1,"skipped":0}\n'


class FullTestSuiteTests(FullSuiteCases, unittest.TestCase):
    def setUp(self) -> None:
        temporary = TOOLS.parent / ".anechoic_tmp/tests/full-test-suite"
        temporary.mkdir(parents=True, exist_ok=True)
        directory = tempfile.TemporaryDirectory(dir=temporary)
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        for name in full.CODE_ROOTS:
            (self.root / name).mkdir(parents=True, exist_ok=True)
        self.file(
            "LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72/engine/pyproject.toml",
            '[tool.ruff.lint]\nselect = ["F"]\n'
            '[tool.ruff.format]\nexclude = ["*.py"]\n',
        )
        self.output = io.StringIO()
        self.errors = io.StringIO()

    def file(self, relative: str, content: str = PASSING) -> Path:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def run_suite(self) -> int:
        with redirect_stdout(self.output), redirect_stderr(self.errors):
            return full.run_full_suite(self.root)

    def test_duplicate_names_and_sibling_imports_use_fresh_interpreters(
        self,
    ) -> None:
        for component, value in (("first", "alpha"), ("second", "beta")):
            folder = (
                f"LAYER_4_ENGINE_STUDIO_C14/{component}/{component}__tests"
            )
            self.file(f"{folder}/helper.py", f"VALUE = {value!r}\n")
            self.file(
                f"{folder}/test_same.py",
                "import unittest\nfrom helper import VALUE\n"
                "class Test(unittest.TestCase):\n"
                f" def test_value(self): self.assertEqual({value!r}, VALUE)\n",
            )
        self.assertEqual(0, self.run_suite(), self.errors.getvalue())
        self.assertIn(
            "tests run: 2; skipped: 0; failed modules: 0",
            self.output.getvalue(),
        )

    def test_backend_provider_is_importable_by_its_registry_name(self) -> None:
        self.file(
            str(
                full.WORKBENCH
                / "FEATURE_IWE_CONSOLE_BACKEND/fixture_provider.py"
            ),
            "VALUE = 42\n",
        )
        self.file(
            (
                "LAYER_4_ENGINE_STUDIO_C14/component/component"
                "__tests/test_provider.py"
            ),
            "import unittest\nfrom fixture_provider import VALUE\n"
            "class Test(unittest.TestCase):\n def test_pro"
            "vider(self): self.assertEqual(42, VALUE)\n",
        )
        self.assertEqual(0, self.run_suite(), self.errors.getvalue())

    def test_test_and_import_errors_fail_but_later_modules_still_run(
        self,
    ) -> None:
        self.file(
            (
                "LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATI"
                "C/FEATURE_PROJECT_TOOLS/FEATURE_PROJECT_TOOLS"
                "__tests/test_a_failure.py"
            ),
            PASSING.replace("assertTrue(True)", "assertTrue(False)"),
        )
        self.file(
            (
                "LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATI"
                "C/FEATURE_PROJECT_TOOLS/FEATURE_PROJECT_TOOLS"
                "__tests/test_b_import.py"
            ),
            "from missing_fixture_dependency import VALUE\nprint(VALUE)\n",
        )
        self.file(
            (
                "LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATI"
                "C/FEATURE_PROJECT_TOOLS/FEATURE_PROJECT_TOOLS"
                "__tests/test_c_good.py"
            )
        )
        self.assertEqual(1, self.run_suite())
        self.assertIn("test_c_good.py", self.output.getvalue())
        self.assertIn("failed modules: 2", self.output.getvalue())
        self.assertIn("missing_fixture_dependency", self.errors.getvalue())

    def test_unused_import_fails_static_before_execution(self) -> None:
        dirty = self.file(
            "LAYER_4_ENGINE_STUDIO_C14/test_unused.py", "import os\n" + PASSING
        )
        self.file(".anechoic_legacy/old.py", "import sys\n")
        original = dirty.read_bytes()
        command = (
            sys.executable,
            "-B",
            str(TOOLS / "test_suite__pub.py"),
            "--project-root",
            str(self.root),
            "--phase",
        )
        for phase in ("static",):
            with self.subTest(phase=phase):
                result = subprocess.run(
                    (*command, phase),
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                self.assertEqual(1, result.returncode, result.stderr)
                self.assertIn("F401", result.stdout)
                self.assertNotIn("Test module START:", result.stdout)
                self.assertEqual(original, dirty.read_bytes())
        (report,) = (self.root / ".anechoic_tmp/test_reports").glob("*.json")
        failure = json.loads(report.read_text())
        self.assertEqual(
            ("static", "static_checks", "failed"),
            (failure["phase"], failure["step"], failure["status"]),
        )
        dirty.write_text(PASSING, encoding="utf-8")
        result = subprocess.run(
            (*command, "static"), capture_output=True, text=True, timeout=30
        )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertNotIn("Test module START:", result.stdout)

    def check_timeout_output(self, error):
        if (
            isinstance(error, subprocess.TimeoutExpired)
            and error.stdout is not None
        ):
            self.assertIn("partial output", self.output.getvalue())
            self.assertIn("partial errors", self.errors.getvalue())
            if isinstance(error.stdout, bytes):
                self.assertIn("partial output �", self.output.getvalue())
                self.assertIn("partial errors �", self.errors.getvalue())

    def waiting_module(self, ready, release):
        return self.file(
            (
                "LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATI"
                "C/FEATURE_PROJECT_TOOLS/FEATURE_PROJECT_TOOLS"
                "__tests/test_waiting.py"
            ),
            "import time, unittest\nfrom pathlib import Path\n"
            "class Test(unittest.TestCase):\n def test_wait(self):\n"
            f"  Path({str(ready)!r}).touch()\n"
            "  deadline = time.monotonic() + 5\n"
            f"  while not Path({str(release)!r}).exists() "
            "and time.monotonic() < deadline:\n"
            "   time.sleep(0.01)\n"
            f"  self.assertTrue(Path({str(release)!r}).exists())\n",
        )

    def test_module_start_is_visible_before_the_real_module_finishes(
        self,
    ) -> None:
        ready, release = self.root / "child-ready", self.root / "release-child"
        module = self.waiting_module(ready, release)
        with (
            patch.object(full, "_run_static_checks", return_value=0),
            ThreadPoolExecutor(max_workers=1) as driver,
        ):
            future = driver.submit(self.run_suite)
            try:
                deadline = time.monotonic() + 5
                while (
                    not ready.exists()
                    and not future.done()
                    and time.monotonic() < deadline
                ):
                    time.sleep(0.01)
                self.assertTrue(ready.exists(), self.errors.getvalue())
                self.assertFalse(future.done())
                self.assertIn(
                    f"Test module START: {module.relative_to(self.root)}",
                    self.output.getvalue(),
                )
                self.assertNotIn("Test module FINISH:", self.output.getvalue())
            finally:
                release.touch()
            self.assertEqual(
                0, future.result(timeout=5), self.errors.getvalue()
            )
        self.assertIn(
            f"Test module FINISH: {module.relative_to(self.root)}",
            self.output.getvalue(),
        )

    def test_platform_skip_is_reported_without_claiming_every_test_passed(
        self,
    ) -> None:
        self.file(
            (
                "LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATI"
                "C/FEATURE_PROJECT_TOOLS/FEATURE_PROJECT_TOOLS"
                "__tests/test_skip.py"
            ),
            "import unittest\n@unittest.skip('platform fix"
            "ture: symlinks unavailable')\n"
            "class Test(unittest.TestCase):\n def test_optional(self): pass\n",
        )
        self.assertEqual(0, self.run_suite())
        self.assertIn("skipped: 1", self.output.getvalue())
        self.assertIn(
            "platform fixture: symlinks unavailable", self.errors.getvalue()
        )

    def test_required_integration_skip_is_a_failure(self) -> None:
        self.file(
            (
                "LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATI"
                "C/FEATURE_PROJECT_TOOLS/FEATURE_PROJECT_TOOLS"
                "__tests/test_fixture_e2e.py"
            ),
            "import unittest\n@unittest.skip('missing test environment')\n"
            "class Test(unittest.TestCase):\n def test_required(self): pass\n",
        )
        self.assertEqual(1, self.run_suite())
        self.assertIn(
            "Required integration tests skipped", self.errors.getvalue()
        )
        self.assertIn("skipped: 1; failed modules: 1", self.output.getvalue())

    def test_empty_suite_and_module_with_no_cases_are_failures(self) -> None:
        self.assertEqual(1, self.run_suite())
        self.file(
            (
                "LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATI"
                "C/FEATURE_PROJECT_TOOLS/FEATURE_PROJECT_TOOLS"
                "__tests/test_empty.py"
            ),
            "VALUE = 1\n",
        )
        self.assertEqual(1, self.run_suite())
        self.assertIn("No test cases loaded", self.errors.getvalue())

    def test_symlink_test_module_is_not_executed_outside_source_root(
        self,
    ) -> None:
        original = self.file("outside.py")
        link = self.root / (
            "LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATI"
            "C/FEATURE_PROJECT_TOOLS/FEATURE_PROJECT_TOOLS"
            "__tests/test_link.py"
        )
        link.parent.mkdir(parents=True)
        link.symlink_to(original)
        self.assertEqual(1, self.run_suite())
        self.assertIn("Test discovery failed", self.errors.getvalue())

    def test_missing_source_root_fails_discovery(self) -> None:
        (self.root / full.CODE_ROOTS[0]).rmdir()
        self.assertEqual(1, self.run_suite())
        with self.assertRaisesRegex(
            OSError, "source test root is unavailable"
        ):
            full.discover_test_modules(self.root)

    def test_symlink_test_directory_cannot_silently_shrink_the_full_suite(
        self,
    ) -> None:
        outside = self.root / "outside"
        outside.mkdir()
        link = self.root / (
            "LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATI"
            "C/FEATURE_PROJECT_TOOLS/FEATURE_PROJECT_TOOLS"
            "__tests"
        )
        link.parent.mkdir(parents=True)
        link.symlink_to(outside, target_is_directory=True)
        self.assertEqual(1, self.run_suite())
        self.assertIn("Test discovery failed", self.errors.getvalue())


if __name__ == "__main__":
    unittest.main()
