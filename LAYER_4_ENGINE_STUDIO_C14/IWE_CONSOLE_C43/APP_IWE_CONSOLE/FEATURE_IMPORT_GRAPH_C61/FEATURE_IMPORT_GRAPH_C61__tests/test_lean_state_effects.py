"""Verify Lean effect rules and an instrumented Autoform fixture."""

import ast
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from _lean_state_effects_support import (
    FixtureTrace, LOWERED_CONTEXT, SOURCE, _context_observations, _event,
    _prove, _translate,
)


KERNEL = Path(__file__).resolve().parents[1] / "ActionEffects.lean"




def _case(events, **changes):
    return {
        "sourcePath": "action.py",
        "line": 2,
        "input": None,
        "reachable": True,
        "complete": True,
        "declaredNoOp": False,
        "policy": {"kind": "local", "owner": "caller", "grants": []},
        "events": events,
    } | changes


def _kernel(cases):
    result = subprocess.run(
        ["lean", "--run", KERNEL],
        input=json.dumps(cases),
        text=True,
        stdout=subprocess.PIPE,
        check=True,
        timeout=60,
    )
    return json.loads(result.stdout)


















@unittest.skipUnless(
    shutil.which("lean"), "Lean 4 is required for the effect checks"
)
class LeanStateEffectsTests(unittest.TestCase):
    def test_calls_keep_the_callee_policy_and_check_pure_callers(self):
        target = _case(
            [_event("write", "local", "provider", 8)],
            unit="provider:write",
            sourcePath="provider.py",
            policy={"kind": "local", "owner": "provider", "grants": []},
        )
        caller = _case([_event("call", name="provider:write")])
        pure = caller | {
            "policy": {"kind": "pure", "owner": "caller", "grants": []}
        }
        local, pure, target = _kernel([caller, pure, target])
        event = _event("write", "local", "provider", 8) | {
            "sourcePath": "provider.py"
        }
        self.assertEqual([event], local["events"])
        self.assertEqual([], local["violations"])
        self.assertEqual([], target["violations"])
        self.assertEqual([event | {"index": 0}], pure["violations"])

    def test_dead_end_and_grants(self):
        read = _event("read", "ambient", "REQUEST_CTX")
        write = _event("write", "ambient", "REQUEST_CTX")
        policy = {
            "kind": "local",
            "owner": "caller",
            "grants": [{"channel": "REQUEST_CTX", "mode": "r"}],
        }
        cases = [
            _case([]),
            _case([], declaredNoOp=True),
            _case([], complete=False),
            _case([_event("output")]),
            _case([read, write, write], policy=policy),
            _case([_event("write", "local", "other")]),
            _case([write], policy={"kind": "pure", "owner": "", "grants": []}),
        ]
        results = _kernel(cases)
        self.assertEqual(
            [result["status"] for result in results],
            [
                "deadEnd",
                "declaredNoOp",
                "unresolved",
                "hasEffects",
                "hasEffects",
                "hasEffects",
                "hasEffects",
            ],
        )
        self.assertEqual(
            [i for i, row in enumerate(results) if row["deadEnd"]], [0]
        )
        self.assertEqual(
            [[v["index"] for v in result["violations"]] for result in results],
            [[], [], [], [], [1, 2], [0], [0]],
        )

    def test_invalid_trace_fails_on_stderr(self):
        result = subprocess.run(
            ["lean", "--run", KERNEL],
            input="{}",
            text=True,
            capture_output=True,
            timeout=60,
            check=False,
        )
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "")
        self.assertTrue(result.stderr)

    @unittest.skipUnless(
        os.environ.get("AUTOFORM_CHECKOUT"),
        "Set AUTOFORM_CHECKOUT for the Autoform canary",
    )
    def test_autoform_agrees_with_python_on_ordered_effects(self):
        checkout = Path(os.environ["AUTOFORM_CHECKOUT"]).resolve(strict=True)
        joern = Path(os.environ["JOERN_HOME"]).resolve(strict=True)
        with (
            TemporaryDirectory(prefix="anechoic-state-effects-") as tmp,
            patch.dict(os.environ, {"AUTOFORM_NO_REEXEC": "1"}),
            patch.object(sys, "path", [str(checkout / "scripts"), *sys.path]),
        ):
            folder = Path(tmp)
            source = folder / "source" / "instrumented.py"
            source.parent.mkdir()
            tree = FixtureTrace().visit(ast.parse(SOURCE))
            source.write_text(
                ast.unparse(ast.fix_missing_locations(tree)) + "\n"
            )
            _translate(folder, checkout, joern, source)
            events = _prove(folder, checkout, source)
        self.assertEqual(
            [[event["kind"] for event in path] for path in events],
            [["write"], ["output"], ["read", "write", "write"], []],
        )
        policy = {
            "kind": "local",
            "owner": "caller",
            "grants": [{"channel": "REQUEST_CTX", "mode": "r"}],
        }
        results = _kernel([
            _case(path, policy=policy, input=index)
            for index, path in enumerate(events)
        ])
        self.assertEqual(
            [row["status"] for row in results],
            ["hasEffects"] * 3 + ["deadEnd"],
        )
        self.assertEqual(
            [[v["index"] for v in row["violations"]] for row in results],
            [[0], [], [1, 2], []],
        )
        self.assertEqual(
            [v["line"] for v in results[2]["violations"]], [10, 11]
        )
        self.assertEqual(
            (results[3]["sourcePath"], results[3]["input"]), ("action.py", 3)
        )

    @unittest.skipUnless(
        os.environ.get("AUTOFORM_CHECKOUT"),
        "Set AUTOFORM_CHECKOUT for the Autoform canary",
    )
    def test_contextvar_single_set_reset_matches_lowered_cell(self):
        checkout = Path(os.environ["AUTOFORM_CHECKOUT"]).resolve(strict=True)
        joern = Path(os.environ["JOERN_HOME"]).resolve(strict=True)
        with (
            TemporaryDirectory(prefix="anechoic-context-effects-") as tmp,
            patch.dict(os.environ, {"AUTOFORM_NO_REEXEC": "1"}),
            patch.object(sys, "path", [str(checkout / "scripts"), *sys.path]),
        ):
            folder = Path(tmp)
            source = folder / "source" / "instrumented.py"
            source.parent.mkdir()
            source.write_text(LOWERED_CONTEXT)
            _translate(folder, checkout, joern, source)
            _prove(folder, checkout, source, _context_observations)


if __name__ == "__main__":
    unittest.main()
