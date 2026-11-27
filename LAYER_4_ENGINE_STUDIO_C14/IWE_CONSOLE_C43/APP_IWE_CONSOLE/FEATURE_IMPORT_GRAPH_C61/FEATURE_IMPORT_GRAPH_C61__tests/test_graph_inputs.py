from importlib import metadata
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from IWE_CONSOLE_C43.APP_IWE_CONSOLE.FEATURE_IMPORT_GRAPH_C61.import_graph__shared import capture, graph_input_signature


class GraphInputsTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(self.enterContext(tempfile.TemporaryDirectory())).resolve()
        which = shutil.which
        self.enterContext(patch.object(shutil, "which", side_effect=lambda name: (
            None if name == "lean" else which(name))))

    def write(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def signature(self):
        value = graph_input_signature(self.root, {})
        self.assertRegex(value or "", r"^[0-9a-f]{64}$")
        return value

    def test_ticket_edits_preserve_graph_inputs(self):
        source = self.write("app/main.py", "VALUE = 1\n")
        ticket_dir = self.root / "_anechoic_anechoic/001_TICKETS/TASKS"
        ticket_dir.mkdir(parents=True)
        signature = self.signature()
        ticket = self.write("_anechoic_anechoic/001_TICKETS/TASKS/AN-T-9901--watcher.md", "Create")
        self.assertEqual(signature, self.signature())
        ticket.write_text("Edit", encoding="utf-8")
        self.assertEqual(signature, self.signature())
        ticket = ticket.rename(ticket.with_name("AN-T-9901--renamed.md"))
        self.assertEqual(signature, self.signature())
        ticket.unlink()
        self.assertEqual(signature, self.signature())
        source.write_text("VALUE = 2\n", encoding="utf-8")
        self.assertNotEqual(signature, self.signature())

    def test_identical_replacement_and_excluded_runtime_preserve_signature(self):
        source = self.write("app/main.py", "VALUE = 1\n")
        manifest = self.write("app/pyproject.toml", "[project]\nname = 'app'\n")
        first = self.signature()
        replacement = self.write("app/replacement.tmp", manifest.read_text())
        replacement.replace(manifest)
        self.assertEqual(first, self.signature())
        self.write(".anechoic_runtime/state", "one")
        self.write("app/.anechoic_runtime/state", "two")
        self.assertEqual(first, self.signature())
        self.write(".anechoic_runtime/state", "changed")
        self.assertEqual(first, self.signature())
        added = self.write("app/added.py", "VALUE = 2\n")
        self.assertNotEqual(first, self.signature())
        added.unlink()
        self.assertEqual(first, self.signature())
        source.write_text("VALUE = 2\n")
        self.assertNotEqual(first, self.signature())

    def test_dependency_roots_and_installed_module_names_change_signature(self):
        self.write("app/main.py", "import extra\n")
        initial = self.signature()
        self.write("app/pyproject.toml", "[project]\nname = 'app'\n")
        self.write("app/uv.lock", "version = 1\n")
        with_root = self.signature()
        self.assertNotEqual(initial, with_root)
        with patch.object(metadata, "packages_distributions", return_value={"extra": ["extra"]}):
            self.assertNotEqual(with_root, self.signature())

    @unittest.skipUnless(shutil.which("git"), "requires Git to stage a fixture file")
    def test_git_index_and_ignore_change_signature(self):
        subprocess.run(["git", "init", "--quiet", str(self.root)], check=True)
        self.write("app/main.py", "VALUE = 1\n")
        initial = self.signature()
        self.write(".git/info/exclude", "*.py\n")
        ignored = self.signature()
        self.assertNotEqual(initial, ignored)
        subprocess.run(["git", "-C", str(self.root), "add", "-f", "app/main.py"], check=True)
        staged = self.signature()
        self.assertNotEqual(ignored, staged)
        self.write(".gitignore", "# Changes the ignore rules carrier\n")
        self.assertNotEqual(staged, self.signature())

    def test_runtime_and_hidden_assets_are_witnessed(self):
        self.write("app/frontend.js", "import '../.assets/site.css';\nimport '../.assets/data.json';\n")
        if capture(self.root, None)["app/frontend.js"].status != "parsed":
            self.skipTest("requires the framework web parsers")
        missing = self.signature()
        self.write(".assets/site.css", "")
        css = self.signature()
        self.assertNotEqual(missing, css)
        self.write(".assets/data.json", "{}")
        both = self.signature()
        self.assertNotEqual(css, both)
        (self.root / ".assets/site.css").unlink()
        self.assertNotEqual(both, self.signature())
        with patch.object(shutil, "which", return_value=None):
            self.assertIsNone(graph_input_signature(self.root, {}))

    def _lean_fixture(self):
        package = "IWE_CONSOLE_C43.APP_IWE_CONSOLE.FEATURE_IMPORT_GRAPH_C61.graph_inputs"
        toolchain = Path(self.enterContext(tempfile.TemporaryDirectory())).resolve()
        binary = toolchain / "bin" / "lean"
        binary.parent.mkdir()
        binary.write_text("Lean launcher")
        library = toolchain / "lib" / "lean"
        library.mkdir(parents=True)
        dependency = library / "Lean.olean"
        dependency.write_text("importable dependency")
        checker = toolchain / "ActionEffects.lean"
        for file in (checker, *(toolchain / name for name in
                               ("state_effects.py", "python_state_cases.py", "web_state_cases.py"))):
            file.write_text("Checker input")
        self.enterContext(patch(package + "._CHECKER", checker))
        self.enterContext(patch.object(shutil, "which", return_value=str(binary)))
        self.enterContext(patch.dict(os.environ, LEAN_PATH="ignored", LEAN_SRC_PATH="ignored"))
        replies = {"--print-libdir": str(library), "--deps": str(dependency)}

        def probe(command, **options):
            self.assertEqual(toolchain, options["cwd"])
            self.assertNotIn("LEAN_PATH", options["env"])
            self.assertNotIn("LEAN_SRC_PATH", options["env"])
            self.assertEqual(None if os.getenv("ANECHOIC_TEST_IMAGE_DEADLINES") == "0" else 5, options["timeout"])
            return subprocess.CompletedProcess(command, 0, stdout=replies[command[1]] + "\n")

        self.enterContext(patch.object(subprocess, "run", side_effect=probe))
        return checker, dependency, replies

    def test_lean_checker_and_installed_library_are_witnessed(self):
        checker, dependency, _ = self._lean_fixture()
        self.write("app/main.py", "def report(): print('event')\n")
        first = self.signature()
        self.assertEqual(first, self.signature())
        with patch.dict(os.environ, ANECHOIC_TEST_IMAGE_DEADLINES="0"):
            self.assertEqual(first, self.signature())
        dependency.write_text("changed dependency")
        second = self.signature()
        self.assertNotEqual(first, second)
        checker.write_text("changed checker")
        self.assertNotEqual(second, self.signature())

    def test_lean_graph_witness_refuses_untracked_dependencies(self):
        checker, dependency, replies = self._lean_fixture()
        self.write("app/main.py", "VALUE = 1\n")
        self.signature()
        replies["--deps"] = str(checker)
        self.assertIsNone(graph_input_signature(self.root, {}))
        replies["--deps"] = str(dependency)
        with patch.dict(os.environ, DYLD_LIBRARY_PATH=str(checker.parent)):
            self.assertIsNone(graph_input_signature(self.root, {}))
        (dependency.parent / "outside.olean").symlink_to(checker)
        self.assertIsNone(graph_input_signature(self.root, {}))
