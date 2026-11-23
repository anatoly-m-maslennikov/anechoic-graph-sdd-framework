from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from IWE_CONSOLE_C43.APP_WORKBENCH.FEATURE_IMPORT_GRAPH_C61 import graph_inputs
from IWE_CONSOLE_C43.APP_WORKBENCH.FEATURE_IMPORT_GRAPH_C61.import_graph__shared import graph_input_signature


class GraphInputsTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(self.enterContext(tempfile.TemporaryDirectory())).resolve()
        which = shutil.which
        self.enterContext(patch.object(graph_inputs.shutil, "which", side_effect=lambda name: (
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

    def test_dependency_roots_and_installed_module_names_change_signature(self):
        self.write("app/main.py", "import extra\n")
        initial = self.signature()
        self.write("app/pyproject.toml", "[project]\nname = 'app'\n")
        self.write("app/uv.lock", "version = 1\n")
        with_root = self.signature()
        self.assertNotEqual(initial, with_root)
        with patch.object(graph_inputs.metadata, "packages_distributions", return_value={"extra": ["extra"]}):
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
        if graph_inputs.scan_web([{"path": "setup.js", "language": "javascript", "text": ""}]) is None:
            self.skipTest("requires the framework web parsers")
        self.write("app/frontend.js", "import '../.assets/site.css';\nimport '../.assets/data.json';\n")
        missing = self.signature()
        self.write(".assets/site.css", "")
        css = self.signature()
        self.assertNotEqual(missing, css)
        self.write(".assets/data.json", "{}")
        both = self.signature()
        self.assertNotEqual(css, both)
        (self.root / ".assets/site.css").unlink()
        self.assertNotEqual(both, self.signature())
        with patch.object(graph_inputs.shutil, "which", return_value=None):
            self.assertIsNone(graph_input_signature(self.root, {}))
