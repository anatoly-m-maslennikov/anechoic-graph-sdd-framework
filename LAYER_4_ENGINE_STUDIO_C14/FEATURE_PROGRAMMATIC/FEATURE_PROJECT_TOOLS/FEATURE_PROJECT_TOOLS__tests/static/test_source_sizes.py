"""Verify source-size measurement and the static entry point."""

from contextlib import redirect_stderr
from io import StringIO
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.test_suite__shared import run_full_suite
from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.test_suite__shared import (
    check_functions,
    check_module,
    python_functions,
    web_functions,
)

ROOT = Path(__file__).resolve().parents[5]


class SourceSizeTests(unittest.TestCase):
    @patch("FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.static_checks._run", return_value=0)
    def test_static_phase_checks_programmatic_and_honors_optional_scope(self, _run):
        with TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            subprocess.run(("git", "init", "--quiet", str(root)), check=True)
            studio = "LAYER_4_ENGINE_STUDIO_C14"
            release = "LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27"
            setup = "LAYER_5_USER_SETUP_C65"
            for folder in (studio, release, setup):
                (root / folder).mkdir(parents=True, exist_ok=True)
            test_dir = root / studio / "FEATURE_PROGRAMMATIC/example/example__tests"
            test_dir.mkdir(parents=True)
            programmatic = test_dir / "test_example.py"
            other = root / setup / "example__shared.py"
            oversized = "def run():\n" + "    pass\n" * 45 + "value = 1\n" * 255
            programmatic.write_text(oversized)
            other.write_text(oversized)
            config = root / "pyproject.toml"
            for setting in ("", "[tool.anechoic.test_suite]\nenforce_source_size = false\n"):
                with self.subTest(setting=setting):
                    if setting:
                        config.write_text(setting)
                    errors = StringIO()
                    with redirect_stderr(errors):
                        self.assertEqual(run_full_suite(root, phase="static"), 1)
                    self.assertIn("test_example.py: module has 301 lines", errors.getvalue())
                    self.assertIn("test_example.py:1: run has 46 lines", errors.getvalue())
                    self.assertNotIn("example__shared.py:", errors.getvalue())
            programmatic.write_text("value = 1\n")
            self.assertEqual(run_full_suite(root, phase="static"), 0)
            config.write_text("[tool.anechoic.test_suite]\nenforce_source_size = true\n")
            errors = StringIO()
            with redirect_stderr(errors):
                self.assertEqual(run_full_suite(root, phase="static"), 1)
            self.assertIn("example__shared.py: module has 301 lines", errors.getvalue())
            self.assertIn("example__shared.py:1: run has 46 lines", errors.getvalue())
            other.write_text("value = 1\n")
            self.assertEqual(run_full_suite(root, phase="static"), 0)

    def test_module_ignores_blank_lines(self):
        source = 'value = "a\fb"\n\n \t\n' * 300
        self.assertEqual([], list(check_module("example.py", source)))
        self.assertEqual(
            ["example.py: module has 301 lines (maximum 300)"],
            list(check_module("example.py", source + "x")),
        )

    def test_python_function_limit_includes_decorators(self):
        path = "example.py"
        body = "    pass\n\n    \n" * 43
        source = "\n\n@decorator\nasync def run():\n" + body
        self.assertEqual(
            [], check_functions(path, python_functions(path, source)),
        )
        longer = source + "    pass\n"
        self.assertEqual(
            ["example.py:3: run has 46 lines (maximum 45)"],
            check_functions(path, python_functions(path, longer)),
        )

    def test_class_can_contain_many_short_methods(self):
        source = "class Example:\n" + "".join(
            f"    def method_{index}(self):\n        pass\n"
            for index in range(25)
        )
        functions = list(python_functions("example.py", source))
        self.assertEqual(25, len(functions))
        self.assertEqual([], check_functions("example.py", functions))

    def test_added_web_suffixes_are_measured(self):
        from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS import source_sizes
        with TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            subprocess.run(("git", "init", "--quiet", str(root)), check=True)
            folder = root / "LAYER_5_USER_SETUP_C65"
            folder.mkdir()
            body = "const run = () => {\n" + "  void 0;\n" * 44 + "};\n"
            for suffix in ("jsx", "tsx", "mts"):
                (folder / f"example.{suffix}").write_text(body)
            with unittest.mock.patch.object(source_sizes, "web_functions") as parse:
                parse.side_effect = lambda root, files: web_functions(ROOT, files)
                findings = source_sizes.source_size_findings(root)
            self.assertEqual(3, len(findings))
            self.assertTrue(all("run has 46 lines" in item for item in findings))

    def test_javascript_and_typescript_function_limit(self):
        arrow = "const run = () => {\n" + "  void 0;\n\n  \n" * 43 + "};"
        longer = arrow.replace("};", "  void 0;\n};")
        component = (
            '<script lang="ts" module>\n' + arrow + '\n</script>\n'
            '<script lang="ts">\n' + longer.replace('run', 'slow') + '\n</script>'
        )
        files = [
            {"path": "exact.ts", "source": arrow},
            {"path": "over.js", "source": longer},
            {"path": "Both.svelte", "source": component},
        ]
        exact, over, blocks = web_functions(ROOT, files)
        self.assertCountEqual([("run", 45), ("slow", 46)], [
            (name, size) for _, name, size in blocks
        ])
        self.assertEqual([[1, "run", 45]], exact)
        self.assertEqual([], check_functions("exact.ts", exact))
        self.assertEqual(
            ["over.js:1: run has 46 lines (maximum 45)"],
            check_functions("over.js", over),
        )
