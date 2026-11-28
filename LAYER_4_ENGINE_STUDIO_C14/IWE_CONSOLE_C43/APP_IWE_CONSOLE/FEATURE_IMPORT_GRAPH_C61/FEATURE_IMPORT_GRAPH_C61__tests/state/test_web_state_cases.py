import json
import subprocess
import unittest
from unittest.mock import patch

from IWE_CONSOLE_C43.APP_IWE_CONSOLE.FEATURE_IMPORT_GRAPH_C61.\
    STATE_ANALYSIS.WEB_STATE.WEB_STATE__shared import (
    web_state_cases,
)  # fmt: skip


class WebStateCasesTests(unittest.TestCase):
    def test_node_observes_external_environment_write_and_restore(self):
        source = """function action() {
  process.env.ANECHOIC_STATE_CANARY = 'changed';
  console.log(process.env.ANECHOIC_STATE_CANARY);
  process.env.ANECHOIC_STATE_CANARY = 'original';
}
"""
        row = next(
            row
            for row in web_state_cases({"action.js": source})["action.js"]
            if row["action"] == "action"
        )
        self.assertTrue(row["complete"])
        self.assertEqual(
            [
                ("write", "ENV"),
                ("read", "ENV"),
                ("output", ""),
                ("write", "ENV"),
            ],
            [(item["kind"], item["name"]) for item in row["events"]],
        )
        result = subprocess.check_output(
            [
                "node",
                "-e",
                "process.env.ANECHOIC_STATE_CANARY = 'original';\n"
                + source
                + "action(); console.log(process.env.ANECHOIC_STATE_CANARY);",
            ],
            text=True,
        )
        self.assertEqual(["changed", "original"], result.splitlines())

    def test_named_import_and_unresolved_short_circuit(self):
        source = """import {thing} from './other';
let state = false;
function action() { state && (state = true); }
"""
        row = next(
            row
            for row in web_state_cases({"main.js": source})["main.js"]
            if row["action"] == "action"
        )
        self.assertFalse(row["complete"])
        self.assertIsNone(row["input"])

    def test_paths_and_runtime_match_on_trusted_fixture(self):
        source = """let count = 0;
function action(go: boolean) {
  if (go) { count = 1; count = 0; return 3; }
}
"""
        cases = [
            c
            for c in web_state_cases({"fixture.ts": source})["fixture.ts"]
            if c["action"] == "action"
        ]
        self.assertEqual(
            [c["input"] for c in cases], [{"go": False}, {"go": True}]
        )
        self.assertTrue(all(c["complete"] for c in cases))
        self.assertEqual(cases[0]["events"], [])
        self.assertEqual(
            [e["kind"] for e in cases[1]["events"]],
            ["write", "write", "output"],
        )
        self.assertTrue(
            all(e["name"] == "$owner" for e in cases[1]["events"][:2])
        )
        js = (
            "let count=0; function action(go){if(go){count=1; count=0; return "
            "3;}}; console.log(JSON.stringify([action(false) ?? null, "
            "action(true), count]));"
        )
        actual = subprocess.check_output(["node", "-e", js], text=True)
        self.assertEqual(json.loads(actual), [None, 3, 0])

    def test_ambient_alias_and_unknown_are_conservative(self):
        source = """const store = {};
function go() { const alias = store; alias.value = 1; process.env.TEST = 'x'; }
function mystery() { external(); }
function bad(x) { if (x) return 1; }
"""
        rows = {
            c["action"]: c for c in web_state_cases({"a.js": source})["a.js"]
        }
        self.assertTrue(rows["go"]["complete"])
        self.assertEqual(
            [
                (e["kind"], e["target"], e["name"])
                for e in rows["go"]["events"]
            ],
            [
                ("read", "local", "$owner"),
                ("write", "local", "$owner"),
                ("write", "ambient", "ENV"),
            ],
        )
        for name in ["mystery", "bad"]:
            self.assertFalse(rows[name]["complete"])
            self.assertIsNone(rows[name]["input"])

    def test_shadowed_locals_and_parse_errors(self):
        source = "let value = 1; function a() { value; let value = 2; }"
        rows = web_state_cases({"a.js": source, "bad.js": "function {"})
        self.assertFalse(
            next(c for c in rows["a.js"] if c["action"] == "a")["complete"]
        )
        self.assertFalse(rows["bad.js"][0]["complete"])

    def test_module_initialization_and_shadowed_process(self):
        rows = web_state_cases(
            {
                "a.js": "let state = 0; function go() { state = 1; }",
                "b.js": (
                    "import process from 'node:process'; function go() { "
                    "process.env.X = 'x'; }"
                ),
            }
        )
        module = rows["a.js"][0]
        self.assertEqual(
            (module["action"], module["input"], module["complete"]),
            ("<module>", {}, True),
        )
        self.assertEqual(module["events"][0]["kind"], "write")
        self.assertFalse(
            next(c for c in rows["b.js"] if c["action"] == "go")["complete"]
        )

    def test_graph_calls_and_unknown_values(self):
        source = """function go() { helper(); return helper(); }
const arrow = () => helper();
function value() { if (helper()) return 1; }
function missing() { other(); }
async function asyncGo() { helper(); }
"""
        sites = {
            "a.js": [
                [1, 16, "unit"],
                [1, 33, "unit"],
                [2, 20, "unit"],
                [3, 23, "unit"],
                [5, 27, "unit"],
            ]
        }
        rows = {
            row["action"]: row
            for row in web_state_cases({"a.js": source}, sites)["a.js"]
        }
        self.assertEqual(
            [e["forward"] for e in rows["go"]["events"]], [False, True]
        )
        self.assertEqual(rows["go"]["events"][0]["name"], "unit")
        self.assertTrue(rows["go"]["inlineable"])
        self.assertTrue(rows["arrow"]["events"][0]["forward"])
        for name in ("value", "missing", "asyncGo"):
            self.assertFalse(rows[name]["complete"])
            self.assertFalse(rows[name]["inlineable"])
        self.assertNotIn(
            "column", web_state_cases({"a.js": source})["a.js"][1]
        )

    def test_scanner_failure_is_explicit(self):
        result = subprocess.CompletedProcess([], 1, "", "parser failure")
        with patch(
            (
                "IWE_CONSOLE_C43.APP_IWE_CONSOLE.FEATURE_IMPORT_GRAPH_C61.STATE_"
                "ANALYSIS.WEB_STATE.WEB_STATE__shared.subprocess.run"
            ),
            return_value=result,
        ):
            with self.assertRaisesRegex(RuntimeError, "parser failure"):
                web_state_cases({"a.js": ""})
