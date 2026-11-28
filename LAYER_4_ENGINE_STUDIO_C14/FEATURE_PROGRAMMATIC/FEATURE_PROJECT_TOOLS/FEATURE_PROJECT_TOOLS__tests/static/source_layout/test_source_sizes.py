"""Verify source-size measurement and the static entry point."""

from contextlib import redirect_stderr
from io import StringIO
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.\
    source_inventory.source_sizes import (
    check_functions,
    check_module,
    python_functions,
    web_functions,
)

from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.test_suite__shared import (
    run_full_suite,
)

ROOT = Path(__file__).resolve().parents[6]


class SourceSizeTests(unittest.TestCase):
    @patch(
        "FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.static_checks._run",
        return_value=0,
    )
    def test_static_phase_checks_programmatic_and_honors_optional_scope(
        self, _run
    ):
        root = self._project()
        studio = "LAYER_4_ENGINE_STUDIO_C14"
        test_dir = (
            root / studio / "FEATURE_PROGRAMMATIC/example/example__tests"
        )
        test_dir.mkdir(parents=True)
        programmatic = test_dir / "test_example.py"
        other = root / "LAYER_5_USER_SETUP_C65/example__shared.py"
        other.parent.mkdir()
        oversized = b"def run():\n" + b"    pass\n" * 45 + b"\n" * 6145
        programmatic.write_bytes(oversized)
        other.write_bytes(oversized)
        config = root / "pyproject.toml"
        self._assert_programmatic_scope(root, config, programmatic)
        self._assert_optional_scope(root, config, other)

    def _project(self):
        root = Path(self.enterContext(TemporaryDirectory())).resolve()
        subprocess.run(("git", "init", "--quiet", str(root)), check=True)
        (root / "LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27").mkdir(parents=True)
        return root

    def _assert_programmatic_scope(self, root, config, programmatic):
        setting = "[tool.anechoic.test_suite]\nenforce_source_size = false\n"
        for selected_setting in ("", setting):
            with self.subTest(setting=selected_setting):
                if selected_setting:
                    config.write_text(selected_setting)
                errors = self._static_failures(root, "test_example.py")
                self.assertNotIn("example__shared.py:", errors)
        programmatic.write_text("x = 1\n" * 301)
        self.assertEqual(run_full_suite(root, phase="static"), 0)

    def _assert_optional_scope(self, root, config, other):
        config.write_text(
            "[tool.anechoic.test_suite]\nenforce_source_size = true\n"
        )
        self._static_failures(root, "example__shared.py")
        other.write_text("value = 1\n")
        self.assertEqual(run_full_suite(root, phase="static"), 0)

    def _static_failures(self, root, name):
        errors = StringIO()
        with redirect_stderr(errors):
            self.assertEqual(run_full_suite(root, phase="static"), 1)
        output = errors.getvalue()
        self.assertIn(f"{name}: module has 6561 bytes (maximum 6144)", output)
        self.assertIn(f"{name}:1: run has 46 lines", output)
        return output

    def test_module_counts_source_bytes(self):
        source = ("é" * 3071).encode() + b"\r\n"
        self.assertEqual([], list(check_module("example.py", len(source))))
        self.assertEqual(
            ["example.py: module has 6145 bytes (maximum 6144)"],
            list(check_module("example.py", len(source + b"\n"))),
        )

    def test_python_function_limit_includes_decorators(self):
        path = "example.py"
        body = "    pass\n\n    \n" * 43
        source = "\n\n@decorator\nasync def run():\n" + body
        self.assertEqual(
            [],
            check_functions(path, python_functions(path, source)),
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
        from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.\
            source_inventory import source_sizes

        root = self._project()
        folder = root / "LAYER_5_USER_SETUP_C65"
        folder.mkdir()
        body = "const run = () => {\n" + "  void 0;\n" * 44 + "};\n"
        for suffix in ("jsx", "tsx", "mts"):
            (folder / f"example.{suffix}").write_text(body)
        with patch.object(
            source_sizes,
            "web_functions",
            side_effect=lambda root, files: web_functions(ROOT, files),
        ):
            findings = source_sizes.source_size_findings(root)
        self.assertEqual(3, len(findings))
        self.assertTrue(all("run has 46 lines" in item for item in findings))

    def test_javascript_and_typescript_function_limit(self):
        arrow = "const run = () => {\n" + "  void 0;\n\n  \n" * 43 + "};"
        longer = arrow.replace("};", "  void 0;\n};")
        component = (
            '<script lang="ts" module>\n' + arrow + "\n</script>\n"
            '<script lang="ts">\n'
            + longer.replace("run", "slow")
            + "\n</script>"
        )
        files = [
            {"path": "exact.ts", "source": arrow},
            {"path": "over.js", "source": longer},
            {"path": "Both.svelte", "source": component},
        ]
        exact, over, blocks = web_functions(ROOT, files)
        self.assertCountEqual(
            [("run", 45), ("slow", 46)],
            [(name, size) for _, name, size, _ in blocks],
        )
        self.assertEqual([[1, "run", 45, 0]], exact)
        self.assertEqual([], check_functions("exact.ts", exact))
        self.assertEqual(
            ["over.js:1: run has 46 lines (maximum 45)"],
            check_functions("over.js", over),
        )
