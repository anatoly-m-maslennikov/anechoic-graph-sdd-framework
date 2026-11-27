import os
import shutil
import tempfile
import unittest
from pathlib import Path

from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75._package__shared import (
    verify_formal_chain,
)
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_2_SPEC_READING_C83._package__shared import (
    load_boundary_model,
)
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_2_SPEC_READING_C83.SPECIFICATION_MODEL_C85._package__shared import (
    parse_trace_contract,
    validate_declaration,
)
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_3_LEAN_TRANSLATOR_C84._package__shared import (
    compile_lean,
)

from .test_cli_spec import _SOLUTION, _carrier
from .test_trace_cases import FIRST, SECOND, SOLUTION


def _order_claim(effects, orders):
    return ("declare_trace_contract(action='compile', output='python', "
            f"must_effect={effects!r}, must_precede={orders!r})")


def _manifest(
    language, *claims, boundaries="{'state': {'reads': [], 'writes': []}}"
):
    body = (
        '## Summary\n\nSample Component\n\n## Purpose\n\nProvide a public Action.\n\n'
        '## Component Identity\n\n```python\nfrom anechoic.model import ComponentManifest\n'
        "ComponentManifest(component_id='C15', name='Sample')\n```\n\n"
        f'## Component Boundaries\n\n```python\n{boundaries}\n```\n\n## Component Contract\n'
    )
    return body + "".join(
        f"\n```{language}\n{claim}\n```\n" for claim in claims
    )


def _pins(root, manifest, solution, answer='AN-S-1@1'):
    pins = (
        _carrier(root, "AN-S-1", "component_manifest", "C1", "{}", manifest),
        _carrier(
            root,
            "AN-S-2",
            "solution",
            "C15",
            f"{{ANSWERS: [{answer}]}}",
            f"## Claim\n\n### Formal Claim\n\n```python\n{solution}\n```\n",
        ),
    )
    path = root / pins[0]['path']
    path.write_text(path.read_text().replace('tier: 4\n', 'tier: 1\n', 1))
    return pins


class DirectManifestChainTests(unittest.TestCase):
    def test_cyclic_contract_stops_before_comparison(self):
        lean = os.environ.get('ANECHOIC_TEST_LEAN') or shutil.which('lean')
        self.assertTrue(lean, 'Lean executable unavailable')
        parse, emit = ('parser', 'called'), ('emitter', 'called')
        claim = _order_claim((parse, emit), ((parse, emit), (emit, parse)))
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            pins = _pins(root, _manifest("python trace", claim), SOLUTION)
            report = validate_declaration(root, "C15", "manifest", pins[0])
            self.assertIn(
                ("contract", "cyclic must_precede constraints"),
                [
                    (gap["field"], gap["message"])
                    for gap in report["unresolved"]
                ],
            )
            model = load_boundary_model(root, "C15", pins[0], None, pins[1])
            self.assertNotIn("def contract", compile_lean(model)["lean"])
            result = verify_formal_chain(
                root, "C15", *pins, action="compile", lean=lean
            )
            self.assertEqual("incomplete", result["outcome"], result)
            self.assertEqual("unresolved", result["translation"]["status"])
            (diagnostic,) = result["diagnostics"]
            self.assertEqual("contract", diagnostic["field"])
            self.assertEqual(pins[0]["path"], diagnostic["source"]["path"])
            self.assertNotIn("evidence", result)

    def test_order_uses_exact_effect_predicates(self):
        old = ('parser', 'called', {'stage': 'old', 'count': {'at_most': 2}})
        new = ('parser', 'called', {'stage': 'new'})
        emit = ('emitter', 'called')
        effects = (old, new, emit)
        chain = ((old, new), (new, emit))
        self.assertEqual(
            list(chain),
            parse_trace_contract(_order_claim(effects, chain))["must_precede"],
        )
        same_old = (
            "parser",
            "called",
            {"count": {"at_most": 2}, "stage": "old"},
        )
        with self.assertRaisesRegex(ValueError, "cyclic must_precede"):
            parse_trace_contract(
                _order_claim(effects, (*chain, (emit, same_old)))
            )
        with self.assertRaises(ValueError):
            parse_trace_contract(_order_claim(effects, ((old, same_old),)))

    def test_opposite_orders_in_different_outcomes(self):
        parse, emit = ('parser', 'called'), ('emitter', 'called')
        cases = {
            "python": {
                "must_effect": (emit,),
                "must_precede": ((parse, emit),),
            },
            "cfel": {
                "must_effect": (parse,),
                "must_precede": ((emit, parse),),
            },
        }
        claim = parse_trace_contract(
            f"declare_trace_contract(action='compile', cases={cases!r})"
        )
        self.assertEqual(
            ["python", "cfel"], [case["output"] for case in claim["cases"]]
        )

    def test_two_pins_compare_each_embedded_trace_outcome(self):
        lean = os.environ.get('ANECHOIC_TEST_LEAN') or shutil.which('lean')
        self.assertTrue(lean, 'Lean executable unavailable')
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            pins = _pins(
                root, _manifest("python trace", FIRST, SECOND), SOLUTION
            )
            result = verify_formal_chain(
                root, "C15", *pins, action="compile", lean=lean
            )
            self.assertEqual("compared", result["outcome"], result)
            self.assertEqual("matched", result["translation"]["status"])
            self.assertEqual("matched", result["status"])
            self.assertEqual({"manifest", "solution"}, set(result["sources"]))
            self.assertEqual({"manifest_solution"}, set(result["directions"]))
            path = root / pins[1]["path"]
            path.write_text(
                path.read_text().replace(
                    "'target': 'parser'", "'target': 'wrong'"
                )
            )
            changed = verify_formal_chain(
                root,
                "C15",
                pins[0],
                solution=pins[1],
                action="compile",
                lean=lean,
            )
            self.assertEqual(
                "conflicting",
                changed["directions"]["manifest_solution"]["status"],
            )

    def test_missing_workflow_retains_the_declared_outcome_obligations(self):
        lean = os.environ.get('ANECHOIC_TEST_LEAN') or shutil.which('lean')
        self.assertTrue(lean, 'Lean executable unavailable')
        audit = (
            "declare_trace_contract(action='audit', output='recorded', "
            "must_effect=(('audit_log', 'written'),), "
            "same_values=((('audit_log', 'id'), ('reply', 'id')),), "
            "value_types={('audit_log', 'id'): 'integer'})"
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            pins = _pins(root, _manifest('python trace', FIRST, SECOND, audit), SOLUTION)
            report = verify_formal_chain(root, 'C15', *pins, lean=lean)
        self.assertEqual('compared', report['outcome'], report)
        self.assertEqual('unresolved', report['status'])
        facts = report['operations']['audit']['manifest_solution']['facts']
        self.assertEqual({'action', 'must_effect', 'terminal_output', 'same_values', 'value_types'},
                         {fact['key'] for fact in facts})
        self.assertTrue(all(fact['status'] == 'unresolved' and fact['output'] == 'recorded' for fact in facts))
        coverage = [fact for fact in report['evidence']['coverage'] if fact['action'] == 'audit']
        self.assertEqual([{'direction': 'manifest_solution', **fact} for fact in facts], coverage)
        by_key = {fact['key']: fact for fact in facts}
        self.assertEqual(('audit_log', 'id'), by_key['same_values']['left'])
        self.assertEqual(('reply', 'id'), by_key['same_values']['right'])
        self.assertEqual(('audit_log', 'id'), by_key['value_types']['field'])
        self.assertEqual('integer', by_key['value_types']['expected'])

    def test_cli_runner_is_checked_from_boundaries(self):
        lean = os.environ.get("ANECHOIC_TEST_LEAN") or shutil.which("lean")
        self.assertTrue(lean, "Lean executable unavailable")
        source = (
            _SOLUTION.split("```")[1]
            .removeprefix("python\n")
            .replace("component='C2'", "component='C15'")
        )
        boundaries = "{'io': {'server': {'suite': {'transport': 'cli', 'runner': 'uv', 'path': 'suite.py'}}}}"
        contract = ("declare_cli_contract(interface='suite', action='run', "
                    "outcomes={'succeeded': 'zero', 'failed': 'nonzero'})")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            pins = _pins(root, _manifest('python cli', contract, boundaries=boundaries), source)
            result = verify_formal_chain(root, 'C15', *pins, action='run', lean=lean)
            self.assertEqual('compared', result['outcome'], result)
            self.assertEqual('matched', result['directions']['manifest_solution']['status'])
            self.assertEqual('matched', result['manifest_consistency']['status'])
            path = root / pins[1]['path']
            original = path.read_text()
            path.write_text(
                original.replace("'runner': 'uv'", "'runner': 'python'")
            )
            changed = verify_formal_chain(
                root, "C15", *pins, action="run", lean=lean
            )
            self.assertEqual(
                "conflicting",
                changed["directions"]["manifest_solution"]["status"],
            )
            path.write_text(
                original.replace("action='run'", "action='renamed'")
            )
            whole = verify_formal_chain(root, "C15", *pins, lean=lean)
            self.assertEqual(
                ("compared", "conflicting"),
                (whole["outcome"], whole["status"]),
                whole,
            )
            self.assertTrue(whole["mermaid"])
            selected = verify_formal_chain(
                root, "C15", *pins, action="run", lean=lean
            )
            self.assertEqual("incomplete", selected["outcome"], selected)
            self.assertEqual("mermaid", selected["diagnostics"][0]["field"])

    def test_exact_answers_and_embedded_contract_are_checked(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            pins = _pins(
                root,
                _manifest(
                    "python trace", "declare_trace_contract(action='compile')"
                ),
                SOLUTION,
                answer="AN-S-1@2",
            )
            report = validate_declaration(root, "C15", "manifest", pins[0])
            self.assertEqual(
                ["contract"],
                [issue["field"] for issue in report["unresolved"]],
            )
            failure = verify_formal_chain(root, "C15", *pins)
            self.assertEqual(
                "relations.ANSWERS", failure["diagnostics"][0]["field"]
            )
