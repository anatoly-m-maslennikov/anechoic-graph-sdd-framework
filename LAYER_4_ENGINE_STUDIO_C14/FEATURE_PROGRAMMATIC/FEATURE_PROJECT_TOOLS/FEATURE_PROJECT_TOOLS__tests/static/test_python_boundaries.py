import contextlib
import importlib.util
import io
from pathlib import Path
import tempfile
import unittest


MODULE = Path(__file__).parents[2] / "python_boundaries.py"
spec = importlib.util.spec_from_file_location("python_boundaries", MODULE)
boundaries = importlib.util.module_from_spec(spec)
spec.loader.exec_module(boundaries)


class PythonBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.engine, self.release, self.setup = boundaries.PYTHON_CHILD_ROOTS
        self.release_module = self.release.replace("/", ".")

    def write(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)

    def run_check(self):
        output = io.StringIO()
        with contextlib.redirect_stderr(output):
            count = boundaries.check(self.root)
        return count, output.getvalue()

    def test_qualified_and_sibling_local_imports_are_reported(self):
        self.write(f"{self.release}/ship.py", "VALUE = 1\n")
        self.write(
            f"{self.engine}/app.py",
            f"import {self.release_module}.ship\nfrom ship import VALUE\n",
        )
        count, output = self.run_check()
        self.assertEqual(count, 2)
        self.assertIn(f"{self.engine}/app.py:1", output)
        self.assertIn("app.py:2: cross-child import ship.VALUE", output)

    def test_own_module_wins_and_cli_text_is_not_an_import(self):
        self.write(f"{self.release}/ship.py", "")
        self.write(f"{self.engine}/ship.py", "")
        self.write(
            f"{self.engine}/app.py",
            "import ship\ncommand = ['python', 'ship.py']\n",
        )
        self.assertEqual(self.run_check()[0], 0)

    def test_dynamic_literals_and_relative_cross_child(self):
        self.write(
            f"{self.engine}/app.py",
            (
                "import importlib\nimportlib.import_module('"
                f"{self.setup}"
                ".run')\nfrom .."
                f"{self.release_module}"
                " import ship\n"
            ),
        )
        count, output = self.run_check()
        self.assertEqual(count, 2)
        self.assertIn("app.py:2", output)
        self.assertIn("app.py:3", output)

    def test_build_and_hidden_trees_are_excluded(self):
        self.write(f"{self.engine}/build/a.py", f"import {self.setup}.run\n")
        self.write(f"{self.engine}/.cache/a.py", f"import {self.setup}.run\n")
        self.assertEqual(self.run_check()[0], 0)

    def test_parse_errors_fail_the_check(self):
        self.write(f"{self.engine}/bad.py", "def broken(:\n")
        self.assertEqual(self.run_check()[0], 1)


if __name__ == "__main__":
    unittest.main()
