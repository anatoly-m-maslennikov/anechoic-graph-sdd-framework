"""Focused suite selection stays scoped, safe, and truthful."""

from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
import io
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS import test_suite__shared as full

TOOLS = Path(__file__).resolve().parents[1]


PASSING = (
    "import unittest\n"
    "class Test(unittest.TestCase):\n"
    " def test_one(self): self.assertTrue(True)\n"
)


class FocusedReleaseTests(unittest.TestCase):
    def setUp(self) -> None:
        parent = TOOLS.parent / ".anechoic_tmp/tests/focused-release"
        parent.mkdir(parents=True, exist_ok=True)
        directory = tempfile.TemporaryDirectory(dir=parent)
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        for name in full.CODE_ROOTS:
            (self.root / name).mkdir(parents=True, exist_ok=True)
        self.output, self.errors = io.StringIO(), io.StringIO()

    def file(self, relative: str, content: str = PASSING) -> Path:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def run_suite(self, modules: tuple[str, ...] | None = None) -> int:
        with redirect_stdout(self.output), redirect_stderr(self.errors):
            if modules is None:
                return full.run_full_suite(self.root, phase="unit")
            return full.run_full_suite(self.root, test_modules=modules, phase="unit")

    def test_default_selection_runs_the_discovered_unit_suite(self) -> None:
        markers = (self.root / "first.marker", self.root / "second.marker")
        paths = ("LAYER_4_ENGINE_STUDIO_C14/test_first.py", "LAYER_4_ENGINE_STUDIO_C14/test_second.py")
        for relative, marker in zip(paths, markers):
            self.file(relative, (
                "import unittest\nclass Test(unittest.TestCase):\n def test_one(self):\n"
                f"  with open({str(marker)!r}, 'a', encoding='utf-8') as output: output.write('ran\\n')\n"
            ))
        for name in ("test_suite__pub.py", "test_suite__shared.py"):
            self.file(f"LAYER_4_ENGINE_STUDIO_C14/{name}", "raise AssertionError('excluded')\n")
        result = subprocess.run(
            (sys.executable, "-B", str(TOOLS / "test_suite__pub.py"), "--project-root", str(self.root)),
            cwd=self.root, capture_output=True, text=True, check=False, timeout=30,
        )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("Test scope: unit; selected modules: unit modules\n", result.stdout)
        starts = [line.removeprefix("Test module START: ") for line in result.stdout.splitlines()
                  if line.startswith("Test module START: ")]
        self.assertCountEqual(paths, starts)
        self.assertIn("Modules: 2; tests run: 2; skipped: 0; failed modules: 0", result.stdout)
        for marker in markers:
            self.assertEqual("ran\n", marker.read_text(encoding="utf-8"))
        self.assertNotIn("focused", result.stdout.lower())
        self.assertNotIn("test_suite__pub.py", result.stdout)
        self.assertNotIn("test_suite__shared.py", result.stdout)

    def test_public_cli_preserves_selection_report_and_exit_status(self) -> None:
        passing_marker, failing_marker = self.root / "passing.marker", self.root / "failing.marker"
        def fixture(marker: Path, success: bool) -> str:
            return (
                "import unittest\n"
                "class Test(unittest.TestCase):\n"
                " def test_one(self):\n"
                f"  with open({str(marker)!r}, 'a', encoding='utf-8') as output: output.write('ran\\n')\n"
                f"  self.assertTrue({success!r})\n"
            )
        passing = self.file("LAYER_4_ENGINE_STUDIO_C14/test_passing.py", fixture(passing_marker, True))
        failing = self.file("LAYER_4_ENGINE_STUDIO_C14/test_failing.py", fixture(failing_marker, False))
        for selected, unselected, marker, other_marker, expected in (
            (passing, failing, passing_marker, failing_marker, 0),
            (failing, passing, failing_marker, passing_marker, 1),
        ):
            with self.subTest(selected=selected.name):
                passing_marker.unlink(missing_ok=True)
                failing_marker.unlink(missing_ok=True)
                relative = selected.relative_to(self.root).as_posix()
                result = subprocess.run(
                    (sys.executable, "-B", str(TOOLS / "test_suite__pub.py"),
                     "--project-root", str(self.root), "--test-module", relative),
                    cwd=self.root, capture_output=True, text=True, check=False, timeout=30,
                )
                self.assertEqual(expected, result.returncode, result.stderr)
                self.assertIn(f"Test scope: focused; selected modules: {relative}\n", result.stdout)
                self.assertEqual([f"Test module START: {relative}"],
                                 [line for line in result.stdout.splitlines() if line.startswith("Test module START:")])
                self.assertIn(f"Modules: 1; tests run: 1; skipped: 0; failed modules: {expected}", result.stdout)
                self.assertEqual("ran\n", marker.read_text(encoding="utf-8"))
                self.assertFalse(other_marker.exists())
                self.assertNotIn(unselected.name, result.stdout)

    def assert_rejected(self, modules: tuple[str, ...]) -> None:
        with patch.object(full, "run_module") as run:
            try:
                status = self.run_suite(modules)
            except (OSError, ValueError) as error:
                status = 1
                self.errors.write(str(error))
        self.assertEqual(1, status)
        run.assert_not_called()

    def test_empty_duplicate_malformed_foreign_and_symlink_selection_is_rejected(self) -> None:
        selected = self.file("LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_PROJECT_TOOLS/FEATURE_PROJECT_TOOLS__tests/test_selected.py")
        relative = selected.relative_to(self.root).as_posix()
        foreign = self.file("outside/test_foreign.py")

        cases = (
            ("empty", ()),
            ("duplicate", (relative, relative)),
            ("malformed", ("LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_PROJECT_TOOLS/FEATURE_PROJECT_TOOLS__tests/test_selected",)),
            ("absolute", (str(selected),)),
            ("traversal", ("../outside/test_foreign.py",)),
            ("foreign", (foreign.relative_to(self.root).as_posix(),)),
        )
        for name, modules in cases:
            with self.subTest(name=name):
                self.output, self.errors = io.StringIO(), io.StringIO()
                self.assert_rejected(modules)

        linked_target = self.file("outside/test_link_target.py")
        link = self.root / "LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_PROJECT_TOOLS/FEATURE_PROJECT_TOOLS__tests/test_link.py"
        link.symlink_to(linked_target)
        self.output, self.errors = io.StringIO(), io.StringIO()
        self.assert_rejected((link.relative_to(self.root).as_posix(),))

    def test_failing_focused_and_skipped_required_modules_fail_the_suite(self) -> None:
        failing = self.file(
            "LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_PROJECT_TOOLS/FEATURE_PROJECT_TOOLS__tests/test_failing.py",
            PASSING.replace("assertTrue(True)", "assertTrue(False)"),
        )
        later = self.file("LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_PROJECT_TOOLS/FEATURE_PROJECT_TOOLS__tests/test_later.py")
        self.assertEqual(
            1,
            self.run_suite((failing.relative_to(self.root).as_posix(), later.relative_to(self.root).as_posix())),
        )
        self.assertIn(later.name, self.output.getvalue())
        self.assertIn("failed modules: 1", self.output.getvalue())

        self.output, self.errors = io.StringIO(), io.StringIO()
        skipped = self.file(
            "LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_PROJECT_TOOLS/FEATURE_PROJECT_TOOLS__tests/test_required_e2e.py",
            "import unittest\n"
            "@unittest.skip('required fixture unavailable')\n"
            "class Test(unittest.TestCase):\n"
            " def test_required(self): pass\n",
        )
        relative = skipped.relative_to(self.root).as_posix()
        self.file("pyproject.toml", '[tool.anechoic.test_suite]\n'
                  f'functional_test_modules = ["{relative}"]\n')
        with redirect_stdout(self.output), redirect_stderr(self.errors):
            self.assertEqual(1, full.run_full_suite(self.root, phase="unit", required=True))
        self.assertIn("Required functional tests skipped", self.errors.getvalue())


if __name__ == "__main__":
    unittest.main()
