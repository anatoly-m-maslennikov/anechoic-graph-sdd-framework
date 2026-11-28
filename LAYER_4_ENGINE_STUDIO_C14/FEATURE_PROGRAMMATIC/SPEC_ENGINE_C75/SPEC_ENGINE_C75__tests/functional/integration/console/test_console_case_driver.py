"""Check inputs and obligations emitted for pinned browser and HTTP cases."""

from copy import deepcopy
from pathlib import Path
import unittest

from ...console_case_driver import (
    observable_cases,
    pinned_console_claims,
    pinned_patchbay_claims,
    pinned_patchbay_rest_claims,
    pinned_rebuild_claims,
)

ROOT = Path(__file__).resolve().parents[7]


class ConsoleCaseDriverTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.claims = pinned_console_claims(ROOT)

    def test_render_outputs_share_the_requested_input(self):
        cases = {
            case["name"]: case
            for case in observable_cases(self.claims, "render_console_view")
        }
        self.assertEqual({"failed", "succeeded"}, cases.keys())
        failed, succeeded = cases["failed"], cases["succeeded"]
        self.assertEqual(failed["input"], succeeded["input"])
        self.assertEqual("in_process", failed["input"]["transport"])
        self.assertTrue(failed["input"]["entry"].endswith("/src/App.svelte"))
        self.assertEqual(["C46.console"], failed["forbid_effect"])
        self.assertIsNone(failed["effect"])
        self.assertEqual([], failed["must_effect"])
        self.assertEqual(
            [("C46.console", "view_displayed")], succeeded["must_effect"]
        )
        self.assertEqual(succeeded["must_effect"][-1], succeeded["effect"])
        for key in ("forbid_effect", "must_precede", "same_values"):
            self.assertEqual([], succeeded[key])

    def test_single_and_grouped_trace_profiles_emit_cases(self):
        graph = list(
            observable_cases(
                pinned_rebuild_claims(ROOT), "rebuild_only_realization_graph"
            )
        )
        self.assertEqual(
            {"ready": True, "disabled": False},
            {case["name"]: case["input"]["graph_enabled"] for case in graph},
        )
        views = list(observable_cases(self.claims, "select_console_view"))
        self.assertIn("table_default", {case["name"] for case in views})

    def test_builder_emits_each_declared_obligation(self):
        action = "run_console_builder"
        (scenario,) = observable_cases(self.claims, action)
        (contract,) = self.claims["contract"]["operations"][action]["cases"]
        for key, count in [
            ("must_effect", 7),
            ("must_precede", 6),
            ("same_values", 13),
        ]:
            self.assertEqual(count, len(scenario[key]))
            self.assertEqual(contract[key], scenario[key])
        self.assertEqual([], scenario["forbid_effect"])
        self.assertEqual(("workbench_display", "shown"), scenario["effect"])

    def test_staged_inputs_and_http_binding(self):
        guards = {
            case["name"]: case["input"]
            for case in observable_cases(self.claims, "guard_draft_editor")
        }
        self.assertEqual(
            {
                "saved": {"dirty": True},
                "discarded": {"dirty": True},
                "save_refused": {"dirty": True},
                "rename_inactive": {},
                "saved_after_pending": {"pending_save": True},
                "pending_save_refused": {"pending_save": True},
                "latest_save_refused": {"pending_save": True},
            },
            guards,
        )
        cases = observable_cases(
            pinned_patchbay_claims(ROOT),
            "forward_console_document",
            selecting=True,
        )
        inputs = {
            case["name"]: (case["input"], case["binding"]["tool"])
            for case in cases
        }
        for name, project, ref in [
            ("current", "Example", "EX-T-1"),
            ("exact", "Example", "EX-T-1@1"),
            ("wrong_project", "Other", "EX-T-1"),
        ]:
            self.assertEqual(
                (
                    {"project_name": project, "ref_id": ref},
                    "iwe_console_atom_document",
                ),
                inputs[name],
            )

    def test_missing_and_ambiguous_inputs_raise(self):
        action = "render_console_view"
        claims = deepcopy(self.claims)
        workflow = claims["solution"]["operations"][action]
        initial = next(
            state["transitions"]
            for state in workflow["states"]
            if state["name"] == workflow["initial"]
        )
        initial.append(dict(initial[0], event="another_request"))
        with self.assertRaisesRegex(ValueError, "ambiguous input"):
            list(observable_cases(claims, action))
        initial.clear()
        with self.assertRaisesRegex(ValueError, "no input reaches"):
            list(observable_cases(claims, action))

    def test_active_patchbay_workflow_includes_initial_refusals(self):
        cases = {
            case["name"]: case
            for case in observable_cases(
                pinned_patchbay_rest_claims(ROOT), "forward_tool_rest"
            )
        }
        self.assertEqual(10, len(cases))
        for name, forbidden in (
            (
                "transport_refused",
                {"C45.shared_tool_coordinator", "bound_backend_client"},
            ),
            ("legacy_refused", {"Backend.tool_dispatch"}),
        ):
            with self.subTest(name=name):
                self.assertEqual(forbidden, set(cases[name]["forbid_effect"]))
                self.assertEqual({}, cases[name]["input"])
                self.assertIsNone(cases[name]["effect"])
