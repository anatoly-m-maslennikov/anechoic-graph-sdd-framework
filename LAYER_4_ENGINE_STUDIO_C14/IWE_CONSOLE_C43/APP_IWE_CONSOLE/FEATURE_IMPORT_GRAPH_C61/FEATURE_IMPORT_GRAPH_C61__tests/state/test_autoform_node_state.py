"""Bounded Node/Autoform interpreter comparison; no kernel proof is claimed."""

import json
import os
from pathlib import Path
import subprocess
import struct
import sys
from tempfile import TemporaryDirectory
import unittest


SOURCE = """function indexTrace(a, b) {
  let state = [];
  state.push(a);
  let alias = state;
  alias[0] = b;
  let mutation = state[0];
  let output = state[0] + 1;
  alias[0] = a;
  let restored = state[0];
  let silent = state[0];
  return mutation * 1000 + output * 100 + restored * 10 + silent;
}"""


def run(args, cwd):
    result = subprocess.run(
        args, cwd=cwd, text=True, capture_output=True, timeout=240
    )
    if result.returncode:
        raise AssertionError(result.stdout + result.stderr)
    return result.stdout


def _parse(folder, source, joern, checkout):
    run(
        [
            joern / "joern-parse",
            source,
            "--language",
            "JAVASCRIPT",
            "--output",
            "cpg.bin",
        ],
        folder,
    )
    run(
        [
            joern / "joern",
            "--script",
            checkout / "cartographer/export_ast.sc",
            "--param",
            "cpgPath=cpg.bin",
            "--param",
            "out=ast.json",
            "--param",
            "dataModel=lp64",
        ],
        folder,
    )


def _evaluate(folder, checkout, prefix):
    model = folder / "Model.lean"
    run(
        [
            sys.executable,
            "-B",
            checkout / "cartographer/render_lean.py",
            folder / "ast.json",
            model,
            "Numeric",
        ],
        folder,
    )
    code = (
        model.read_text()
        + """\nopen Autoform.Core Autoform.Generated.Numeric
def main : IO Unit := do
"""
    )
    for a, b in [(1, 2), (3, 4)]:
        code += (
            f'  match runFunc program 200 "numbers.js::program:'
            f'indexTrace" [{prefix}.int ({a}), .int ({b})] with\n'
            """  | .val (.int n) => IO.println n
  | .val (.float n) =>
    if n.fmt == .binary64 then IO.println ("float:" ++ toString n.bits)
    else throw (IO.userError "unexpected float format")
  | other => throw (IO.userError (reprStr other))
"""
        )
    driver = folder / "Check.lean"
    driver.write_text(code)
    actual = run(
        ["lake", "env", "lean", "--run", driver], checkout
    ).splitlines()
    values = [
        struct.unpack(">d", int(s[6:]).to_bytes(8, "big"))[0]
        if s.startswith("float:")
        else int(s)
        for s in actual
    ]
    return values


@unittest.skipUnless(
    os.environ.get("AUTOFORM_CHECKOUT"),
    "Set AUTOFORM_CHECKOUT for the Autoform canary",
)
class AutoformNodeStateTests(unittest.TestCase):
    def test_node_observations_match_autoform_interpreter(self):
        checkout = Path(os.environ["AUTOFORM_CHECKOUT"]).resolve(strict=True)
        joern = Path(os.environ["JOERN_HOME"]).resolve(strict=True)
        with TemporaryDirectory(prefix="anechoic-node-effects-") as tmp:
            folder = Path(tmp)
            source = folder / "src"
            source.mkdir()
            (source / "numbers.js").write_text(SOURCE)
            runner = folder / "runner.js"
            runner.write_text(
                SOURCE
                + "\nconsole.log(indexTrace(1,2));\n"
                + "console.log(indexTrace(3,4));\n"
            )
            native = run(["node", runner], folder).splitlines()
            self.assertEqual(native, ["2311", "4533"])
            _parse(folder, source, joern, checkout)
            functions = json.loads((folder / "ast.json").read_text())
            entries = [
                f
                for f in functions
                if f["name"] == "numbers.js::program:indexTrace"
            ]
            self.assertEqual(len(entries), 1)
            params = entries[0]["params"]
            prefix = ".unit, " if params and params[0] == "this" else ""
            self.assertEqual(
                params, ["this", "a", "b"] if prefix else ["a", "b"]
            )
            values = _evaluate(folder, checkout, prefix)
            self.assertEqual(values, [int(item) for item in native])
