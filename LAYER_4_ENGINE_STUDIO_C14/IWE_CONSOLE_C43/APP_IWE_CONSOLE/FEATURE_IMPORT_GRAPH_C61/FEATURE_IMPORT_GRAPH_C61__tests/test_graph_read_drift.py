"""Exercise source drift through the actual Worker graph command."""
import json
from pathlib import Path
from runpy import run_module
import subprocess
import sys
from tempfile import TemporaryDirectory
import tokenize
import unittest
from unittest.mock import patch


def run_graph_with_read_fixture():
    source, mutation, *flags = sys.argv[1:]
    target = Path(source)
    original = tokenize.open

    def read(file):
        if Path(file) == target:
            if mutation == "remove":
                target.unlink()
            elif mutation == "change":
                target.write_text("VALUE = 2\n")
            elif mutation == "unreadable":
                raise PermissionError("fixture read failure")
        return original(file)

    module = "WORKERS_beta_C69.realization_graph"
    with patch.object(sys, "argv", [module, *flags]), patch.object(tokenize, "open", side_effect=read):
        run_module(module, run_name="__main__")


class GraphReadDriftTests(unittest.TestCase):
    def run_graph(self, name, mutation, *, replay=False):
        with TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            source = root / name
            source.write_text("VALUE = 1\n")
            command = [sys.executable, "-B", str(Path(__file__).resolve()), str(source), mutation]
            if replay:
                command.append("--watcher-replay")
            request = {"root": str(root), "config": {"python_roots": ["."]}}
            return subprocess.run(command, input=json.dumps(request), text=True, capture_output=True, timeout=30)

    def test_read_drift_emits_only_structured_graph_change(self):
        cases = (("main.py", "change", False), ("main.py", "remove", True), ("private_token.py", "change", True))
        for name, mutation, replay in cases:
            with self.subTest(name=name, mutation=mutation, replay=replay):
                result = self.run_graph(name, mutation, replay=replay)
                self.assertEqual(1, result.returncode, result.stderr)
                self.assertEqual("", result.stdout)
                record = json.loads(result.stderr)
                self.assertEqual(("C61", "ERROR", "realization_graph_inputs_changed"),
                                 (record["component"], record["severity"], record["code"]))
                change = {"change": "changed", "fields": ["signature"]}
                if name == "main.py":
                    change["path"] = name
                self.assertEqual({"sources": change}, record["details"])

    def test_ordinary_read_error_does_not_emit_a_consistency_change(self):
        result = self.run_graph("main.py", "unreadable", replay=True)
        self.assertEqual(1, result.returncode, result.stderr)
        self.assertEqual("", result.stdout)
        self.assertEqual("realization graph: fixture read failure\n", result.stderr)


if __name__ == "__main__":
    run_graph_with_read_fixture()
