"""Tests for Python launcher bytecode containment checks."""

from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
import unittest

from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.run_full_test_suite import CODE_ROOTS, run_full_suite
from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.python_bytecode import (
    python_findings, shell_findings, unsafe, yaml_findings,
)


class PythonBytecodeTests(unittest.TestCase):
    def test_interpreter_options_stop_at_target(self):
        self.assertTrue(unsafe(["python", "app.py", "-B"]))
        self.assertTrue(unsafe(["python", "-m", "tool", "-B"]))
        self.assertFalse(unsafe(["python", "-B", "app.py"]))
        self.assertFalse(unsafe(["python", "-X", "pycache_prefix=.anechoic_tmp/cache", "-m", "tool"]))
        self.assertTrue(unsafe(["python", "-X", "pycache_prefix=/tmp/cache", "app.py"]))
        self.assertTrue(unsafe(["python", "-Wignore::Broken", "app.py"]))
        self.assertTrue(unsafe(["PYTHONDONTWRITEBYTECODE=1", "python", "-I", "app.py"]))
        self.assertTrue(unsafe(["python", "-B", "-m", "compileall", "."]))
        self.assertTrue(unsafe(["uv", "sync", "--compile-bytecode"]))
        self.assertFalse(unsafe(["uv", "python", "find", "3.14"]))

    def test_python_argv(self):
        source = ('command = [sys.executable, "app.py"]\n'
                  'subprocess.run(["uv", "run", "python", "-B", "-m", "tool"])\n'
                  'subprocess.run([sys.executable, "-X", f"pycache_prefix={root}/.anechoic_tmp/cache", "app.py"])\n'
                  'py_compile.compile("app.py", cfile="scope.bin")\n')
        self.assertEqual(python_findings(source), [1])

    def test_shell_and_docs(self):
        source = 'python app.py\nPYTHONDONTWRITEBYTECODE=1 python app.py\npython -B app.py\n'
        self.assertEqual(shell_findings(source), [1])
        docs = 'Use python app.py here.\n```sh\npython app.py\n```\n'
        self.assertEqual(shell_findings(docs, markdown=True), [3])
        joined = 'uv run \\\n  python app.py\npython -B app.py && python app.py\n'
        self.assertEqual(shell_findings(joined), [1, 3])

    def test_container_and_workflow_commands(self):
        docker = 'FROM python:3.14\nENTRYPOINT ["python", "app.py"]\nRUN python -B app.py\n'
        self.assertEqual(shell_findings(docker, docker=True), [2])
        yaml = 'jobs:\n  - run: |\n      python app.py\n  - test: [CMD, python, app.py]\n'
        self.assertEqual(sorted(yaml_findings(yaml)), [3, 4])

    def test_static_phase_reports_and_rejects_an_unguarded_launch(self):
        root = Path(self.enterContext(TemporaryDirectory())).resolve()
        subprocess.run(("git", "init", "--quiet", str(root)), check=True)
        for name in CODE_ROOTS:
            (root / name).mkdir()
        config = root / "LAYER_3_ENVIRONMENTS_C72/engine/pyproject.toml"
        config.parent.mkdir(parents=True)
        config.write_text("[tool.ruff]\n", encoding="utf-8")
        relative = "LAYER_5_FRAMEWORK_DELIVERY/launcher.py"
        launcher = root / relative
        unsafe_source = 'import subprocess\nsubprocess.run(["python", "worker.py"])\n'
        launcher.write_text(unsafe_source, encoding="utf-8")
        with redirect_stdout(StringIO()), redirect_stderr(StringIO()) as errors:
            self.assertEqual(1, run_full_suite(root, phase="static"))
        self.assertIn(f"{relative}:2: Python launch may write bytecode outside .anechoic_tmp", errors.getvalue())
        launcher.write_text(unsafe_source.replace('"python",', '"python", "-B",'), encoding="utf-8")
        outside = launcher.parent / "__pycache__"
        outside.mkdir()
        with redirect_stdout(StringIO()), redirect_stderr(StringIO()) as errors:
            self.assertEqual(1, run_full_suite(root, phase="static"))
        self.assertIn("LAYER_5_FRAMEWORK_DELIVERY/__pycache__: bytecode cache outside .anechoic_tmp", errors.getvalue())
        temporary = root / ".anechoic_tmp"
        temporary.mkdir()
        outside.rename(temporary / "__pycache__")
        with redirect_stdout(StringIO()), redirect_stderr(StringIO()):
            self.assertEqual(0, run_full_suite(root, phase="static"))


if __name__ == "__main__":
    unittest.main()
