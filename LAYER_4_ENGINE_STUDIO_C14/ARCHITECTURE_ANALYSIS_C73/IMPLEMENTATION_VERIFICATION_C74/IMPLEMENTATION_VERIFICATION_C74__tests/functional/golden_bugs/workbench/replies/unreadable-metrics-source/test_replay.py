"""Replay complete historical metrics modules with a missing source size."""

import json
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
CASE = json.loads((HERE / "case.json").read_text())


def load(version):
    namespace = {}
    source = (HERE / CASE[version]["fixture"]).read_text()
    exec(compile(source, CASE[version]["fixture"], "exec"), namespace)
    return namespace["code_rows"]


class Replay(unittest.TestCase):
    def test_unreadable_and_controls(self):
        nodes = [
            ["p", "package", "python", "a", None, None, None],
            ["m", "module", "python", "a/x.py", "read_error", "p", None],
        ]
        before, fixed = load("before"), load("fixed")
        self.assertEqual(before(nodes, [], {"a": "C1"}, {}, {}), [])
        with self.assertRaisesRegex(
            ValueError, "^Cannot measure unreadable source: a/x[.]py$"
        ):
            fixed(nodes, [], {"a": "C1"}, {}, {})
        for function in (before, fixed):
            self.assertEqual(
                function(nodes, [], {"a": "C1"}, {"a/x.py": (10, 1)}, {}),
                [
                    ["Component", "C1", "a/x.py", "unclassified", 10, 1],
                    ["Package", "p", "a/x.py", "unclassified", 10, 1],
                ],
            )
            nodes[1][4] = None
            self.assertEqual(function(nodes, [], {"a": "C1"}, {}, {}), [])
            nodes[1][4] = "read_error"


if __name__ == "__main__":
    unittest.main()
