import json
import subprocess
from pathlib import Path
import shutil
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "web_code_units.mjs"


FRONTEND = SCRIPT.parents[1] / "IWE_CONSOLE_C43/APP_WORKBENCH/FEATURE_WORKBENCH_FRONTEND"


@unittest.skipUnless(shutil.which("node") and (FRONTEND / "node_modules/typescript").is_dir(),
                     "Framework web parser is unavailable")
class WebCodeUnitTests(unittest.TestCase):
    def test_imports_methods_shadowing_and_ambiguous_imports(self):
        data = {
            "sources": {
                "a.ts": "export const f = () => 1; export class C { static m() {} }",
                "b.ts": "import * as x from './a'; function g(f: () => void) { f(); x.f(); x.C.m(); new x.C(); } x.f();",
                "c.ts": "import { f } from './ambiguous'; f();",
                "other.ts": "export function f() {}",
            },
            "imports": {
                "b.ts": [[1, "./a", "a.ts"]],
                "c.ts": [[1, "./ambiguous", "a.ts"], [1, "./ambiguous", "other.ts"]],
            },
        }
        result = subprocess.run(["node", str(SCRIPT)], input=json.dumps(data), text=True, capture_output=True, check=True)
        units, calls = json.loads(result.stdout)
        by_name = {(unit[1], unit[3]): unit[0] for unit in units}
        assert {(source, target) for source, target, _, _ in calls} == {
            (by_name[("module:b.ts", "g")], by_name[("module:a.ts", "f")]),
            (by_name[("module:b.ts", "g")], by_name[("module:a.ts", "C.m")]),
        }
