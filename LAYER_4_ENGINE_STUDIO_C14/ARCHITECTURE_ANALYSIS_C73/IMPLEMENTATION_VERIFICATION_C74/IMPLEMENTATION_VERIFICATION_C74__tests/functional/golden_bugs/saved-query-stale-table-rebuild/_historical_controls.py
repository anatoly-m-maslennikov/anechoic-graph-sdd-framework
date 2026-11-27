"""Additional saved-query controls."""

import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent


class HistoricalControls:
    def test_historical_and_readable_effects(self):
        revision = "415fc9dcfb6dc8cc6a4e3b8e6ef7ecd60e4cabe7"
        paths = subprocess.check_output(
            ["git", "ls-tree", "-r", "--name-only", revision], text=True
        ).splitlines()
        source_path = next(
            p
            for p in paths
            if p.endswith("/query_store.py")
            and "FEATURE_WORKBENCH_BACKEND" in p
        )
        historical = subprocess.check_output(
            ["git", "show", f"{revision}:{source_path}"], text=True
        )
        good = self.run_case(historical, ["A", "B"], [["A", "B"]])
        self.assertEqual(good, {"findings": [], "unresolved": []})
        self._historical_guards(historical, good)
        bad = self.run_case(historical, ["B", "A"], [["A", "B"]])
        self.assertEqual(len(bad["findings"]), 1)
        self.assertEqual(bad["unresolved"], [])
        self._historical_variant(historical, good)

    def _historical_guards(self, historical, good):
        guard = (
            "            if (selected is not None or tables is "
            "not None) and old_id != selected:"
        )
        changed = historical.replace(
            guard,
            guard
            + (
                "\n                self._connection.execute('DELETE"
                " FROM workbench_results.x')"
            ),
        )
        self.assertEqual(
            self.run_case(changed, ["A", "B"], [["A", "B"]]), good
        )
        reversed_guard = changed.replace(
            "selected is not None or tables is not None",
            "selected is None or tables is not None",
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

    def _historical_variant(self, historical, good):
        variant = (
            "class Store:\n    def prepare_result_rebuild(self)"
            ":\n        staged = {}\n        for old_id, old in"
            " self._results.items():\n            new_id, resul"
            "t = self._materialize(old.sql, old.preview, admitt"
            "ed=True)\n            self._connection.execute(f'D"
            "ROP TABLE workbench_results.{quote_identifier(old."
            "table_name)}')\n            self._connection.execu"
            "te(f'ALTER TABLE workbench_results.{quote_identifi"
            "er(result.table_name)} RENAME TO {quote_identifier"
            "(old.table_name)}')\n            staged[old_id] = "
            "(new_id, result)\n            result.table_name = "
            "old.table_name\n        return staged\n"
        )
        self.assertEqual(
            self.run_case(variant, ["A", "B"], [["A", "B"]]), good
        )
        premature = variant.replace(
            (
                "            staged[old_id] = (new_id, result)\n   "
                "         result.table_name = old.table_name"
            ),
            "            staged[old_id] = (new_id, result)",
        ).replace(
            "            self._connection.execute(f'ALTER TABLE",
            (
                "            result.table_name = old.table_name\n  "
                "          self._connection.execute(f'ALTER TABLE"
            ),
        )
        self.assertTrue(
            self.run_case(premature, ["A", "B"], [["A", "B"]])["unresolved"]
        )
        self._historical_other_variants(historical, variant)

    def _historical_other_variants(self, historical, variant):
        no_guard = historical.replace(
            (
                "            if old.table_name.lower() not in retai"
                "ned:\n                continue\n"
            ),
            "",
        )
        self.assertTrue(
            self.run_case(no_guard, ["A", "B"], [["A", "B"]])["unresolved"]
        )
        stale = self.run_case(variant, ["B", "A"], [["A", "B"]])
        self.assertEqual(len(stale["findings"]), 1)
        self.assertEqual(stale["unresolved"], [])
        changed_sql = variant.replace(
            "DROP TABLE workbench_results.", "DELETE FROM workbench_results."
        )
        self.assertTrue(
            self.run_case(changed_sql, ["A", "B"], [["A", "B"]])["unresolved"]
        )
        unknown = variant.replace(
            "            staged[old_id] = (new_id, result)",
            (
                "            self.other_effect()\n            stage"
                "d[old_id] = (new_id, result)"
            ),
        )
        self.assertTrue(
            self.run_case(unknown, ["A", "B"], [["A", "B"]])["unresolved"]
        )
