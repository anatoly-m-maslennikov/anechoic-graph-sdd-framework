"""Additional saved-query controls."""

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent


class ProductionControls:
    def test_production_helper_and_unsupported_variants(self):
        root = next(
            p for p in HERE.parents if (p / "_anechoic_anechoic").is_dir()
        )
        source = (
            root
            / "LAYER_4_ENGINE_STUDIO_C14/KERNEL_MIXER_C59/_result_lifecycle.py"
        ).read_text()
        good = self.run_case(source, ["A", "B"], [["A", "B"]])
        self.assertEqual(good, {"findings": [], "unresolved": []})
        self._production_discovery(source, good)
        self._production_variants(source)

    def _production_discovery(self, source, good):
        with tempfile.TemporaryDirectory() as tmp:
            checkout = Path(tmp)
            target = (
                checkout
                / "LAYER_4_ENGINE_STUDIO_C14/KERNEL_MIXER_C59/_result_lifecycle.py"
            )
            target.parent.mkdir(parents=True)
            target.write_text(source)
            self.assertEqual(self._run_discovery(checkout), good)
            historical = checkout / (
                "LAYER_3_ENGINE_STUDIO_C14/FEATURE_WORKBENCH_BACKEN"
                "D/query_store.py"
            )
            historical.parent.mkdir(parents=True)
            historical.write_text(source)
            self.assertTrue(self._run_discovery(checkout)["unresolved"])

    def _run_discovery(self, checkout):
        run = subprocess.run(
            [
                sys.executable,
                "-B",
                str(HERE / "analyze.py"),
                str(checkout),
                "--lean",
                os.environ.get("LEAN_BIN") or shutil.which("lean") or "lean",
            ],
            capture_output=True,
            text=True,
            timeout=45,
            check=True,
        )
        return json.loads(run.stdout)

    def _production_variants(self, source):
        bind = '"ALTER TABLE workbench_results."'
        self.assertIn(bind, source)
        changed_sql = source.replace(
            bind, bind.replace("ALTER TABLE", "DELETE FROM"), 1
        )
        self.assertTrue(
            self.run_case(changed_sql, ["A", "B"], [["A", "B"]])["unresolved"]
        )
        statement = (
            "        self._connection.execute(\n"
            '            "ALTER TABLE workbench_results."\n'
            '            f"{runtime.quote_identifier(result.table_name)} "\n'
            '            f"RENAME TO {runtime.quote_identifier(old.table_name)}"\n'
            "        )\n"
        )
        self.assertIn(statement, source)
        lost = self.run_case(
            source.replace(statement, "", 1), ["A", "B"], [["A", "B"]]
        )
        self.assertEqual(len(lost["findings"]), 1)
        self.assertEqual(lost["unresolved"], [])
        self._production_unsupported(source)

    def _production_unsupported(self, source):
        variants = [
            source.replace(
                "        return new_id, result\n",
                (
                    "        staged[old_id] = (new_id, result)\n       "
                    " return new_id, result\n"
                ),
                1,
            ),
            source.replace(
                "self._stage_result_replacement(old)",
                "self._stage_result_replacement(old, old)",
                1,
            ),
            source.replace(
                "return new_id, result\n", "return result, new_id\n", 1
            ),
            source.replace(
                "    def _stage_result_replacement(",
                "    @staticmethod\n    def _stage_result_replacement(",
                1,
            ),
            source.replace(
                "        new_id, result = self._materialize(",
                (
                    "        self._stage_result_replacement = other\n  "
                    "      new_id, result = self._materialize("
                ),
                1,
            ),
        ]
        for variant in variants:
            with self.subTest(variant=variants.index(variant)):
                self.assertTrue(
                    self.run_case(variant, ["A", "B"], [["A", "B"]])[
                        "unresolved"
                    ]
                )
