"""Check control-flow depth in Python and web functions."""

from pathlib import Path
import unittest

from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.\
    source_inventory.source_sizes import (
    check_functions,
    python_functions,
    web_functions,
)

ROOT = Path(__file__).resolve().parents[6]

PYTHON = """def outer():
    if enabled:
        pass
    elif ready:
        for row in rows:
            try:
                match row:
                    case 1:
                        def inner():
                            if ok:
                                pass
                    case 2:
                        pass
            except LookupError:
                pass
"""

TYPESCRIPT = """function outer() {
  const object = { first: { second: { third: { fourth: { fifth: 0 } } } } };
  if (enabled)
    stop();
  else if (ready)
    for (const row of rows)
      try {
        switch (row) {
          case 1:
            function inner() {
              if (ok) stop();
            }
            break;
          case 2:
            break;
        }
      } catch { stop(); }
}"""


class SourceNestingTests(unittest.TestCase):
    def test_python_branches_and_nested_function_scopes(self):
        path = "example.py"
        deeper = PYTHON.replace(
            "case 2:\n                        pass",
            "case 2:\n                        while ready:\n"
            "                            pass",
        )
        accepted = list(python_functions(path, PYTHON))
        self.assertEqual({"outer": 4, "inner": 1}, self._depths(accepted))
        self.assertEqual([], check_functions(path, accepted))
        self.assertEqual(
            [f"{path}:1: outer has nesting depth 5 (maximum 4)"],
            check_functions(path, python_functions(path, deeper)),
        )

    def test_web_control_flow_without_braces_and_svelte_offsets(self):
        deeper = TYPESCRIPT.replace(
            "case 2:\n            break;",
            "case 2:\n            while (ready) stop();",
        )
        accepted, rejected = web_functions(
            ROOT,
            [
                {"path": "example.ts", "source": TYPESCRIPT},
                {
                    "path": "Example.svelte",
                    "source": '<script lang="ts">\n' + deeper + "\n</script>",
                },
            ],
        )
        self.assertEqual({"outer": 4, "inner": 1}, self._depths(accepted))
        self.assertEqual([], check_functions("example.ts", accepted))
        self.assertEqual(
            ["Example.svelte:2: outer has nesting depth 5 (maximum 4)"],
            check_functions("Example.svelte", rejected),
        )

    @staticmethod
    def _depths(functions):
        return {name: depth for _, name, _, depth in functions}
