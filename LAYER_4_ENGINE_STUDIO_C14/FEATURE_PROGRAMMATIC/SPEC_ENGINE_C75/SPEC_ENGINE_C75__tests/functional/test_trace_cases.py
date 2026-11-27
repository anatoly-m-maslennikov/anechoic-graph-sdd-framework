import os
import shutil
import unittest
from unittest.mock import patch

from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75._package__shared import (
    verify_formal_chain,
)
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_3_LEAN_TRANSLATOR_C84._package__shared import (
    compile_lean,
)
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_4_SPEC_COMPARISON_C88._package__shared import (
    check_trace_spec,
)

FIRST = "declare_trace_contract(action='compile', output='python', must_effect=(('parser', 'called'),))"
SECOND = "declare_trace_contract(action='compile', output='cfel', must_effect=(('parser', 'called'),))"
SOLUTION = """component_workflow(component='C15', action='compile', machine={
    'id': 'compile', 'initial': 'start', 'states': {
        'start': {'on': {'parse': {'target': 'parsed', 'guard': {'type': 'matchesTrace',
            'params': {'kind': 'effect', 'target': 'parser', 'outcome': 'called'}}}}},
        'parsed': {'on': {
            'python': {'target': 'done', 'guard': {'type': 'matchesTrace',
                'params': {'kind': 'output', 'outcome': 'python'}}},
            'cfel': {'target': 'done', 'guard': {'type': 'matchesTrace',
                'params': {'kind': 'output', 'outcome': 'cfel'}}}}},
        'done': {'type': 'final'}}})"""


def model():
    return {
        "component_id": "C15",
        "manifest": {
            "fields": {"component_id": "C15", "name": "Parser"},
            "boundaries": None,
            "source": {"atom_id": "AN-S-1"},
        },
        "contract": {
            "source": {"atom_id": "AN-S-2"},
            "claims": [("python trace", FIRST), ("python trace", SECOND)],
        },
        "solution": {
            "source": {"atom_id": "AN-S-3"},
            "claims": [("python", SOLUTION)],
        },
    }


class TraceCasesTests(unittest.TestCase):
    def test_action_selector_preserves_repeated_unbound_contract_cases(self):
        lean = os.environ.get('ANECHOIC_TEST_LEAN') or shutil.which('lean')
        if lean is None:
            self.skipTest('Lean unavailable')
        sample = model()
        boundaries = {"state": {"reads": [], "writes": []}}
        sample["manifest"]["fields"]["boundaries"] = sample["manifest"][
            "boundaries"
        ] = boundaries
        with patch(
            "FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.formal_chain__pub.load_boundary_model",
            return_value=sample,
        ):
            result = verify_formal_chain(
                ".", "C15", {}, {}, {}, action="compile", lean=lean
            )
        self.assertEqual("compared", result["outcome"])
        facts = result["directions"]["contract_solution"]["facts"]
        self.assertEqual(
            {"python": "matched", "cfel": "matched"},
            {
                fact["output"]: fact["status"]
                for fact in facts
                if fact["key"] == "must_effect"
            },
        )

    def test_cli_outcome_names_count_as_declarations(self):
        from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_4_SPEC_COMPARISON_C88._package__shared import (
            _uncovered_outcomes,
        )

        workflow = compile_lean(model())["claims"]["solution"]
        contract = {
            "action": "compile",
            "transport": "cli",
            "trace": {"output": "python"},
            "exit_codes": {"cfel": 0},
        }
        self.assertEqual(
            _uncovered_outcomes(None, contract, workflow, "compile"), []
        )
        del contract["exit_codes"]
        self.assertEqual(
            _uncovered_outcomes(None, contract, workflow, "compile"),
            [{"action": "compile", "output": "cfel"}],
        )
        contract["stdout.cfel"] = "compiled CFEL"
        self.assertEqual(
            _uncovered_outcomes(None, contract, workflow, "compile"), []
        )

    def test_rejects_invalid_case_sets(self):
        for second in (
            FIRST,
            SECOND[:-1]
            + ", interface='i', route='r', transport='http', operation='POST /x')",
        ):
            sample = model()
            sample['contract']['claims'][1] = ('python trace', second)
            result = compile_lean(sample)
            self.assertNotIn('contract', result['claims'])
            self.assertTrue(result['unresolved'])
        sample = model()
        sample['contract']['claims'][1] = ('python cli', SECOND)
        self.assertNotIn('contract', compile_lean(sample)['claims'])

    def test_cases_compare_independently(self):
        lean = os.environ.get('ANECHOIC_TEST_LEAN') or shutil.which('lean')
        if lean is None:
            self.skipTest('Lean unavailable')
        sample = model()
        compiled = compile_lean(sample)
        self.assertEqual(2, len(compiled['claims']['contract']['cases']))
        self.assertIn('AN-S-2', compiled['lean'])
        with patch('FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_2_SPEC_READING_C83._package__shared.load_boundary_model', return_value=sample):
            def statuses(*uncovered):
                result = check_trace_spec(
                    None, "C15", None, None, None, lean=lean
                )
                self.assertEqual(
                    [
                        {"action": "compile", "output": name}
                        for name in uncovered
                    ],
                    result["uncovered_outcomes"],
                )
                facts = result["directions"]["contract_solution"]["facts"]
                return {
                    fact["output"]: fact["status"]
                    for fact in facts
                    if fact["key"] == "must_effect"
                }

            self.assertEqual(
                {"python": "matched", "cfel": "matched"}, statuses()
            )
            sample["solution"]["claims"][0] = (
                "python",
                SOLUTION.replace("'outcome': 'cfel'", "'outcome': 'other'"),
            )
            self.assertEqual(
                {"python": "matched", "cfel": "unresolved"}, statuses("other")
            )
            sample["contract"]["claims"][1] = (
                "python trace",
                SECOND.replace("('parser', 'called')", "('other', 'called')"),
            )
            sample["solution"]["claims"][0] = ("python", SOLUTION)
            self.assertEqual(
                {"python": "matched", "cfel": "conflicting"}, statuses()
            )


class ManifestOutcomeTests(unittest.TestCase):
    def test_logical_outcomes_in_three_directions(self):
        lean = os.environ.get('ANECHOIC_TEST_LEAN') or shutil.which('lean')
        if lean is None:
            self.skipTest('Lean unavailable')
        sample = model()
        boundaries = {'io': {'server': {'compile': {'outcomes': {
            'python': {'must_effect': [('parser', 'called')], 'forbid_effect': ['state']},
            'cfel': {'must_effect': [('parser', 'called')]}}}}}}
        sample['manifest']['fields']['boundaries'] = boundaries
        sample['manifest']['boundaries'] = boundaries
        sample['contract']['claims'][0] = ('python trace', FIRST[:-1] + ", forbid_effect=('state',))")
        with patch('FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_2_SPEC_READING_C83._package__shared.load_boundary_model', return_value=sample):
            def check():
                return check_trace_spec(
                    None, "C15", None, None, None, lean=lean
                )

            self.assertEqual("matched", check()["status"])
            sample["contract"]["claims"][0] = (
                "python trace",
                FIRST.replace("parser", "other"),
            )
            self.assertEqual(
                "conflicting",
                check()["directions"]["manifest_contract"]["status"],
            )
            sample["contract"]["claims"][0] = (
                "python trace",
                FIRST[:-1] + ", forbid_effect=('state',))",
            )
            sample["solution"]["claims"][0] = (
                "python",
                SOLUTION.replace("'target': 'parser'", "'target': 'other'"),
            )
            self.assertEqual(
                "conflicting",
                check()["directions"]["manifest_solution"]["status"],
            )
            sample["contract"]["claims"].pop()
            self.assertEqual(
                "unresolved",
                check()["directions"]["manifest_contract"]["status"],
            )

    def test_manifest_rejects_bad_effects_and_keeps_other_io_unresolved(self):
        from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_2_SPEC_READING_C83.SPECIFICATION_MODEL_C85._package__shared import (
            validate_manifest,
        )

        sample = model()["manifest"]
        for constraints in (
            {"must_effect": [("x", "ok"), ("x", "ok")]},
            {"must_effect": [("x", "ok")], "forbid_effect": ["x"]},
            {"must_effect": [("x",)]},
            {"forbid_effect": []},
        ):
            boundaries = {
                "io": {"server": {"a": {"outcomes": {"b": constraints}}}}
            }
            sample["fields"]["boundaries"] = sample["boundaries"] = boundaries
            self.assertTrue(validate_manifest(sample)["issues"])
        boundaries = {
            "io": {"server": {"some_interface": {"transport": "http"}}}
        }
        sample["fields"]["boundaries"] = sample["boundaries"] = boundaries
        self.assertTrue(validate_manifest(sample)["unresolved"])
