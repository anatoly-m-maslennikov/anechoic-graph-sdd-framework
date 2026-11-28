"""Exercise graph-only rebuilds through the native query owner."""

import asyncio
import json
import os
import subprocess
import sys
from contextlib import redirect_stderr
from io import StringIO
from pathlib import Path
from unittest.mock import patch

TARGET = "realization_graph"
IMPORTS = "SELECT written_specifier FROM module_imports"
ATOMS = "SELECT exact_ref FROM native_references WHERE stable_ref = 'AN-T-010'"
SEEDS = "SELECT purpose FROM component_seeds WHERE seed_id = 'C2'"


def _rebuild_case(name):
    engine = Path(__file__).resolve().parents[6]
    driver = engine.joinpath(
        "FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75",
        "SPEC_ENGINE_C75__tests/functional/console_case_driver.py",
    )
    action = "rebuild_only_realization_graph"
    result = subprocess.check_output(
        [sys.executable, "-B", str(driver), action],
        cwd=engine.parent,
        env={**os.environ, "PYTHONPATH": str(engine)},
        text=True,
    )
    cases = json.loads(result)[action]
    return next(case for case in cases if case["name"] == name)


class ImportGraphRebuildCases:
    async def test_graph_only_rebuild_keeps_atom_and_structure_facts(self):
        case = await asyncio.to_thread(_rebuild_case, "ready")
        source = self._source("src/UNIT_C1/main.py", "import os\n")
        structure = self._graph_rebuild_structure()
        gateway = await self._gateway(
            enabled=case["input"]["graph_enabled"],
            structure_snapshot=structure,
        )
        owner = gateway._native_query
        with owner._interface_lock:
            independent = owner.run("SELECT 7", result_delivery="inline")
            view, (previous_id, rows) = self._graph_rebuild_view(owner)
            self.assertEqual([["os"]], rows)
            self._write(
                "001_TICKETS/TASKS/AN-T-010-TASK--added.md",
                "AN-T-010",
                "active",
                1,
            )
            source.write_text("import sys\n", encoding="utf-8")
            structure.write_text(
                structure.read_text().replace("Initial purpose", "New purpose")
            )
            with patch.object(
                owner,
                "_prepare_realization",
                wraps=owner._prepare_realization,
            ) as prepare:
                result = owner.rebuild(case["input"]["target"])
            self.assertIs(True, prepare.call_args.kwargs["force_parse"])
            self._assert_graph_rebuild(
                case, result, owner, view, previous_id, independent
            )
            self.assertEqual("ready", owner.rebuild("all")["status"])
            self._assert_atom_and_seed(owner, [["AN-T-010@1"]], "New purpose")

    def _assert_graph_rebuild(
        self, case, result, owner, view, previous_id, independent
    ):
        self.assertEqual(case["name"], result["status"])
        self.assertEqual(case["input"]["target"], result["target"])
        replaced = result["result_ids"]
        current_id, rows = self._graph_view_result(owner, view)
        independent_id = independent["query_id"]
        independent_page = owner.page(
            independent_id, 0, result_delivery="inline"
        )
        observed = {
            "graph_replaced": rows == [["sys"]],
            "dependent_results_replaced": (
                current_id != previous_id
                and replaced.get(previous_id) == current_id
            ),
            "independent_results_preserved": (
                independent_id not in replaced
                and independent_page["rows"] == independent["rows"]
            ),
            "atoms_preserved": (
                owner.run(ATOMS, result_delivery="inline")["rows"] == []
            ),
            "structure_preserved": (
                owner.run(SEEDS, result_delivery="inline")["rows"]
                == [["Initial purpose"]]
            ),
        }
        self.assertEqual(
            ["C59.graph_rebuild", "published", observed], case["effect"]
        )

    def _assert_atom_and_seed(self, owner, atoms, purpose):
        self.assertEqual(
            atoms, owner.run(ATOMS, result_delivery="inline")["rows"]
        )
        self.assertEqual(
            [[purpose]], owner.run(SEEDS, result_delivery="inline")["rows"]
        )

    async def test_graph_only_rebuild_rolls_back_graph_and_results(self):
        source = self._source("src/main.py", "import os\n")
        gateway = await self._gateway()
        owner = gateway._native_query
        store = owner._owner()
        stage = store.prepare_result_rebuild

        def fail_after_stage(*args, **kwargs):
            self.assertTrue(stage(*args, **kwargs))
            raise ValueError("fixture result rebuild failed")

        with owner._interface_lock:
            view, before = self._graph_rebuild_view(owner)
            source.write_text("import sys\n", encoding="utf-8")
            with (
                patch.object(
                    store, "prepare_result_rebuild", fail_after_stage
                ),
                redirect_stderr(StringIO()) as errors,
                self.assertRaisesRegex(
                    ValueError, "^fixture result rebuild failed$"
                ),
            ):
                owner.rebuild(TARGET)
            self.assertIn(
                "Workbench rebuild failed for 'realization_graph': "
                "fixture result rebuild failed",
                errors.getvalue(),
            )
            self.assertEqual(before, self._graph_view_result(owner, view))
            self.assertEqual(
                [["os"]],
                owner.run(IMPORTS, result_delivery="inline")["rows"],
            )
            retry = owner.rebuild(TARGET)
            self.assertEqual(
                (retry["result_ids"][before[0]], [["sys"]]),
                self._graph_view_result(owner, view),
            )

    async def test_graph_only_rebuild_reports_disabled_graph(self):
        case = await asyncio.to_thread(_rebuild_case, "disabled")
        gateway = await self._gateway(enabled=case["input"]["graph_enabled"])
        owner = gateway._native_query
        with (
            redirect_stderr(StringIO()) as errors,
            patch.object(
                owner, "_rebuild_projection", wraps=owner._rebuild_projection
            ) as publish,
            self.assertRaises(ValueError) as refusal,
        ):
            owner.rebuild(case["input"]["target"])
        self.assertEqual(
            [
                "C59.graph_rebuild_reply",
                "refused",
                {
                    "message": str(refusal.exception),
                },
            ],
            case["effect"],
        )
        self.assertEqual(["C59.graph_rebuild"], case["forbid_effect"])
        publish.assert_not_called()
        self.assertIn(
            "Workbench rebuild failed for 'realization_graph': "
            "Realization Graph is disabled",
            errors.getvalue(),
        )
        self.assertEqual({"mode": "live_index"}, owner.status())

    def _graph_rebuild_structure(self):
        return self._source(
            ".anechoic_tmp/structure.json",
            json.dumps({
                "model_sha256": "fixture",
                "project": {"ref": "AN-S-001@1", "sha256": "fixture"},
                "components": {
                    "C1": {
                        "parent": "C00",
                        "ref": "AN-S-006@1",
                        "sha256": "fixture",
                        "source_path": (
                            "AN-S-006-SPEC-COMPONENT_MANIFEST--unit.md"
                        ),
                        "fields": {"name": "Unit"},
                    },
                },
                "packages": {
                    "C2": {
                        "component": "C1",
                        "ref": "AN-S-007@1",
                        "sha256": "fixture",
                        "source_path": "AN-S-007-SPEC--seed.md",
                        "fields": {"purpose": "Initial purpose"},
                    }
                },
            }),
        )

    def _graph_rebuild_view(self, owner):
        workspace = owner.interface_call(
            "workspace_open", {"session_id": "rebuild-graph"}
        )
        view = {
            "workspace_id": workspace["workspace_id"],
            "view_id": workspace["active_view_id"],
        }
        owner.interface_call(
            "view_update", view | {"sql": IMPORTS, "expected_revision": 0}
        )
        owner.interface_call("view_run", view)
        return view, self._graph_view_result(owner, view)

    def _graph_view_result(self, owner, view):
        result = owner.interface_call(
            "view_fetch", view | {"result_delivery": "inline"}
        )
        return result["query_id"], result["rows"]
