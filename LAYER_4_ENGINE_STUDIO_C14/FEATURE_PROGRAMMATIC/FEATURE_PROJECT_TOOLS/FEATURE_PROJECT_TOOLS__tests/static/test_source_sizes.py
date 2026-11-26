"""Verify source-size measurement and the static entry point."""

from contextlib import redirect_stderr
from io import StringIO
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
import unittest

from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.test_suite__shared import run_full_suite
from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.test_suite__shared import (
    check_functions,
    check_module,
    python_functions,
    web_functions,
)

ROOT = Path(__file__).resolve().parents[5]


class SourceSizeTests(unittest.TestCase):
    def test_static_phase_applies_only_the_configured_size_limits(self):
        with TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            subprocess.run(("git", "init", "--quiet", str(root)), check=True)
            for folder in ("LAYER_4_ENGINE_STUDIO_C14", "LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27", "LAYER_5_USER_SETUP_C65"):
                (root / folder).mkdir(parents=True, exist_ok=True)
            engine_config = root / "LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72/engine/pyproject.toml"
            engine_config.parent.mkdir(parents=True)
            engine_config.write_text("[tool.ruff]\n")
            path = root / "LAYER_5_USER_SETUP_C65/example__shared.py"
            path.write_text("def run():\n" + "    pass\n" * 45 + "value = 1\n" * 255)
            config = engine_config
            config.write_text("[tool.anechoic.test_suite]\nenforce_source_size = false\n")
            self.assertEqual(run_full_suite(root, phase="static"), 0)
            config.write_text("[tool.anechoic.test_suite]\nenforce_source_size = true\n")
            errors = StringIO()
            with redirect_stderr(errors):
                self.assertEqual(run_full_suite(root, phase="static"), 1)
            self.assertIn("module has 301 lines (maximum 300)", errors.getvalue())
            self.assertIn("run has 46 lines (maximum 45)", errors.getvalue())
            path.write_text(f"value = {'x' * 100!r}\n")
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

    def test_javascript_and_typescript_function_limit(self):
        arrow = "const run = () => {\n" + "  void 0;\n\n  \n" * 43 + "};"
        longer = arrow.replace("};", "  void 0;\n};")
        files = [
            {"path": "exact.ts", "source": arrow},
            {"path": "over.js", "source": longer},
        ]
        exact, over = web_functions(ROOT, files)
        self.assertEqual([], check_functions("exact.ts", exact))
        self.assertEqual(
            ["over.js:1: run has 46 lines (maximum 45)"],
            check_functions("over.js", over),
        )
