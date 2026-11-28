"""Controls for the bounded saved-result graph model."""

import json
import os
import shutil
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from _historical_controls import HistoricalControls
from _production_controls import ProductionControls

HERE = Path(__file__).resolve().parent


class SavedQueryControls(
    HistoricalControls, ProductionControls, unittest.TestCase
):
    def run_case(self, source, order, edges, released=None):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            backend = root / "FEATURE_WORKBENCH_BACKEND"
            backend.mkdir()
            (backend / "moved.py").write_text(source)
            case = root / "graph.json"
            case.write_text(
                json.dumps(
                    {
                        "order": order,
                        "edges": edges,
                        "released": released if released is not None else [],
                    }
                )
            )
            run = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(HERE / "analyze.py"),
                    str(root),
                    "--lean",
                    os.environ.get("LEAN_BIN")
                    or shutil.which("lean")
                    or "lean",
                    "--file",
                    "FEATURE_WORKBENCH_BACKEND/moved.py",
                    "--case",
                    str(case),
                ],
                capture_output=True,
                text=True,
                timeout=45,
                check=True,
            )
            return json.loads(run.stdout)

    def test_graph_order_and_fan_in(self):
        fixed = (HERE / "fixed.py.txt").read_text()
        edges = [["A", "C"], ["B", "C"]]
        good = self.run_case(fixed, ["B", "A", "C"], edges)
        self.assertEqual(good, {"findings": [], "unresolved": []})
        bad = self.run_case(fixed, ["A", "C", "B"], edges)
        self.assertEqual(len(bad["findings"]), 1)
        self.assertIn("C reads B", bad["findings"][0]["detail"])
        self.assertEqual(bad["unresolved"], [])
        chain = self.run_case(fixed, ["A", "B", "C"], [["A", "B"], ["B", "C"]])
        self.assertEqual(chain, {"findings": [], "unresolved": []})
        cycle = self.run_case(fixed, ["A", "B"], [["A", "B"], ["B", "A"]])
        self.assertIn("cycle", cycle["unresolved"][0]["detail"])

    def test_production_released_guard(self):
        root = next(
            p for p in HERE.parents if (p / "_anechoic_anechoic").is_dir()
        )
        source = (
            root
            / "LAYER_4_ENGINE_STUDIO_C14/KERNEL_MIXER_C59/_result_lifecycle.py"
        ).read_text()
        guard = "            if old.table_name.lower() not in retained:\n"
        self.assertEqual(source.count(guard), 1)
        mutant = source.replace(
            guard,
            (
                "            if old.table_name.lower() not in retai"
                "ned or old.released:\n"
            ),
            1,
        )
        clean = {"findings": [], "unresolved": []}
        self.assertEqual(
            self.run_case(source, ["A", "B"], [["A", "B"]], ["A"]), clean
        )
        self.assertEqual(
            self.run_case(mutant, ["A", "B"], [["A", "B"]]), clean
        )
        bad = self.run_case(mutant, ["A", "B"], [["A", "B"]], ["A"])
        self.assertEqual(bad["unresolved"], [])
        self.assertEqual(len(bad["findings"]), 1)
        self.assertIn("B reads A before", bad["findings"][0]["detail"])
        for invalid in (["C"], ["A", "A"], "A"):
            self.assertTrue(
                self.run_case(mutant, ["A", "B"], [["A", "B"]], invalid)[
                    "unresolved"
                ]
            )

    def test_production_reverse_iteration(self):
        root = next(
            p for p in HERE.parents if (p / "_anechoic_anechoic").is_dir()
        )
        source = (
            root
            / "LAYER_4_ENGINE_STUDIO_C14/KERNEL_MIXER_C59/_result_lifecycle.py"
        ).read_text()
        loop = "for old_id, old in self._results.items():"
        self.assertEqual(source.count(loop), 1)
        reverse = source.replace(
            loop, "for old_id, old in reversed(self._results.items()):", 1
        )
        self.assertEqual(
            self.run_case(source, ["A", "B"], [["A", "B"]]),
            {"findings": [], "unresolved": []},
        )
        self.assertEqual(
            self.run_case(reverse, ["A", "B"], []),
            {"findings": [], "unresolved": []},
        )
        bad = self.run_case(reverse, ["A", "B"], [["A", "B"]])
        self.assertEqual(bad["unresolved"], [])
        self.assertEqual(len(bad["findings"]), 1)
        self.assertIn("B reads A before", bad["findings"][0]["detail"])
        for variant in (
            reverse + "\nreversed = list\n",
            reverse.replace(
                "reversed(self._results.items())",
                "reversed(list(self._results.items()))",
            ),
        ):
            self.assertTrue(
                self.run_case(variant, ["A", "B"], [["A", "B"]])["unresolved"]
            )

    def test_unreachable_partial_selection(self):
        fixed = (HERE / "fixed.py.txt").read_text()
        guard = (
            "            if selected is not None and old_id not in selected:"
        )
        changed = fixed.replace(
            guard,
            guard
            + (
                "\n                self._connection.execute('DELETE"
                " FROM workbench_results.x')\n                self."
                "other_effect()"
            ),
        )
        self.assertEqual(
            self.run_case(changed, ["A", "B"], [["A", "B"]]),
            {"findings": [], "unresolved": []},
        )
        reversed_guard = changed.replace(
            "if selected is not None and old_id not in selected:",
            "if selected is None and old_id not in selected:",
        )
        self.assertTrue(
            self.run_case(reversed_guard, ["A", "B"], [["A", "B"]])[
                "unresolved"
            ]
        )
        with_else = changed.replace(
            "            new_id, result = self._materialize",
            (
                "            else:\n                pass\n         "
                "   new_id, result = self._materialize"
            ),
        )
        self.assertTrue(
            self.run_case(with_else, ["A", "B"], [["A", "B"]])["unresolved"]
        )

    def test_before_and_fixed(self):
        before = self.run_case(
            (HERE / "before.py.txt").read_text(), ["A", "B"], [["A", "B"]]
        )
        fixed = self.run_case(
            (HERE / "fixed.py.txt").read_text(), ["A", "B"], [["A", "B"]]
        )
        self.assertEqual(len(before["findings"]), 1)
        self.assertEqual(before["unresolved"], [])
        self.assertEqual(fixed, {"findings": [], "unresolved": []})

    def test_unsupported_conditional_effect(self):
        fixed = (HERE / "fixed.py.txt").read_text()
        source = fixed.replace(
            (
                "            new_id, result = self._materialize(old"
                ".sql, old.preview, admitted=True)"
            ),
            (
                "            if old_id:\n                new_id, re"
                "sult = self._materialize(old.sql, old.preview, adm"
                "itted=True)"
            ),
        )
        result = self.run_case(source, ["A", "B"], [["A", "B"]])
        self.assertEqual(result["findings"], [])
        self.assertTrue(result["unresolved"])


if __name__ == "__main__":
    unittest.main()
