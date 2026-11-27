import hashlib
import json
import os
import shutil
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch

from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75 import formal_chain__pub as chain
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75._package__shared import (
    verify_formal_chain,
)
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_1_SOURCE_ADAPTERS_C95.\
    _package__shared import SourceError, read_source  # fmt: skip
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_3_LEAN_TRANSLATOR_C84._package__shared import (
    run_lean_json,
)
from .test_direct_manifest_chain import _manifest, _pins
from .test_trace_cases import FIRST, SECOND, SOLUTION


class LeanReplayEvidenceTests(unittest.TestCase):
    def test_stage_observations_detect_changed_renderer_input(self):
        lean = os.environ.get('ANECHOIC_TEST_LEAN') or shutil.which('lean')
        self.assertTrue(lean, 'Lean executable unavailable')
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            pins = _pins(root, _manifest('python trace', FIRST), SOLUTION)
            result = verify_formal_chain(root, 'C15', *pins, lean=lean)
            self.assertEqual('compared', result['outcome'], result)
            evidence = result['evidence']
            stages = evidence['stages']
            actual = json.loads(evidence['validation_programs'][0]['stdout'])
            claims = {role: row[0]['claim'] for role, row in zip(
                ('manifest', 'contract', 'solution'), actual[-1][0],
                strict=True)}
            def digest(value):
                encoded = json.dumps(value, sort_keys=True, allow_nan=False,
                                     separators=(',', ':')).encode('utf-8')
                return hashlib.sha256(encoded).hexdigest()
            self.assertEqual(digest(claims), evidence['model_pin'])
            self.assertEqual(evidence['model_pin'], stages['generated_claims'])
            self.assertEqual(evidence['model_pin'], stages['lean_claims'])
            self.assertEqual({'claims_pin': evidence['model_pin'],
                              'action': None, 'kind': 'trace'},
                             stages['comparison'])
            self.assertEqual(digest(claims['solution']),
                             stages['rendering']['solution_pin'])
            fake = {'status': 'matched', 'issues': [], 'unresolved': [],
                    'claims': claims}
            with patch.object(chain, 'validate_translation',
                              return_value=fake):
                missing = verify_formal_chain(root, 'C15', *pins, lean=lean)
            self.assertEqual('incomplete', missing['outcome'], missing)
            self.assertIn('Missing Lean validation observation',
                          missing['diagnostics'][0]['message'])
            original = chain._require_diagram
            def changed(model, claim, observations, *, action=None):
                claim = deepcopy(claim)
                claim['changed'] = True
                return original(model, claim, observations, action=action)
            with patch.object(chain, '_require_diagram', side_effect=changed):
                failed = verify_formal_chain(root, 'C15', *pins, lean=lean)
            self.assertEqual('incomplete', failed['outcome'], failed)
            self.assertIn('Rendering Solution identity',
                          failed['diagnostics'][0]['message'])
            self.assertNotIn('evidence', failed)

    def test_changed_action_or_comparison_model_is_incomplete(self):
        lean = os.environ.get('ANECHOIC_TEST_LEAN') or shutil.which('lean')
        self.assertTrue(lean, 'Lean executable unavailable')
        render = chain._require_diagram
        compare = chain.compare_trace_spec

        def other_action(model, claim, observations, *, action=None):
            return render(model, claim, observations, action='audit')

        def changed_claim(model, canonical, **options):
            canonical['claims']['solution']['changed'] = True
            return compare(model, canonical, **options)

        def changed_source(model, canonical, **options):
            result = compare(model, canonical, **options)
            result['sources']['solution'] = {
                **result['sources']['solution'], 'sha256': 'f' * 64}
            return result

        def changed_diagram(model, canonical, **options):
            return {**compare(model, canonical, **options),
                    'mermaid': 'flowchart TD\n  x --> y'}

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = _manifest('python trace', FIRST,
                                 FIRST.replace("'compile'", "'audit'"))
            solution = (SOLUTION + '\n```\n\n```python\n'
                        + SOLUTION.replace("'compile'", "'audit'"))
            pins = _pins(root, manifest, solution)
            for name, mutate, message in (
                ('_require_diagram', other_action, 'Rendering Action differs'),
                ('compare_trace_spec', changed_claim, 'Comparison Model'),
                ('compare_trace_spec', changed_source, 'Comparison source'),
                ('compare_trace_spec', changed_diagram, 'Comparison diagram'),
            ):
                with self.subTest(name=name), patch.object(
                        chain, name, side_effect=mutate):
                    result = verify_formal_chain(root, 'C15', *pins,
                                                 action='compile', lean=lean)
                    self.assertEqual('incomplete', result['outcome'], result)
                    self.assertIn(message, result['diagnostics'][0]['message'])

    def _default_failure_standard(self, root):
        pin = {
            'path': ('_anechoic_anechoic/LAYER_4_ENGINE_STUDIO_C14/'
                     'FEATURE_PROGRAMMATIC_C15/01_draft/'
                     'AN-S-5072@2-draft-SWCS-STANDARD--report-'
                     'programmatic-operation-failures-explicitly.md'),
            'atom_id': 'AN-S-5072', 'version': 2, 'status': 'draft',
            'container_component': 'C15',
            'sha256': ('90858185dfdf80f16af951c5dfc6e699'
                       'bb896deb46fc50a9ae49973bdf6f489b'),
        }
        standard, pinned = read_source(root, pin, 'standard')
        self.assertEqual(pin, pinned)
        specs = root / '_anechoic_anechoic'
        owners = {}
        for component, atom, version, parent in (
            ('C75', 'AN-S-3395', 6, 'C15'),
            ('C94', 'AN-S-5020', 4, 'C75'),
            ('C95', 'AN-S-5021', 3, 'C75'),
        ):
            path, = specs.rglob(f'{atom}-SPEC-COMPONENT_MANIFEST--*.md')
            owner_pin = {'path': path.relative_to(root).as_posix(),
                         'atom_id': atom, 'version': version,
                         'status': 'active', 'container_component': parent}
            carrier, _ = read_source(root, owner_pin, 'manifest')
            self.assertIn(f"component_id='{component}'", carrier.body)
            owners[component] = carrier.metadata['container']['component']
        self.assertEqual({'C75': pin['container_component'],
                          'C94': 'C75', 'C95': 'C75'}, owners)
        self.assertIn('Apply this Standard by default to Programmatic public '
                      'operations', standard.body)
        return standard

    def test_draft_failure_standard_on_public_incomplete_response(self):
        root = Path(__file__).resolve().parents[5]
        standard = self._default_failure_standard(root)
        claim = standard.body.split('```lean\n', 1)[1].split('```', 1)[0]
        lean = os.environ.get('ANECHOIC_TEST_LEAN') or shutil.which('lean')
        self.assertTrue(lean, 'Lean executable unavailable')
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory)
            manifest, solution = _pins(
                work, _manifest('python trace', FIRST), SOLUTION)
            bad = {**solution, 'sha256': '0' * 64}
            with self.assertRaises(SourceError) as caught:
                read_source(work, bad, 'solution')
            result = verify_formal_chain(work, 'C15', manifest, solution=bad)
        error = caught.exception
        diagnostic, = result['diagnostics']
        self.assertEqual('incomplete', result['outcome'])
        self.assertEqual((error.source, error.field),
                         (diagnostic['source'], diagnostic['field']))
        self.assertEqual((bad, 'sha256'), (error.source, error.field))
        self.assertNotEqual((error.source, error.field),
                            (manifest, diagnostic['field']))
        self.assertNotEqual((error.source, error.field),
                            (diagnostic['source'], 'source_pin'))
        self.assertEqual(error.role, diagnostic['role'])
        self.assertEqual(str(error), diagnostic['message'])
        reported = bool(result['diagnostics'])
        failure = result['outcome'] == 'incomplete'
        values = [(reported, failure), (False, failure), (reported, False)]
        checks = ', '.join(
            f'{{ProgrammaticFailures.conforms .response true {str(d).lower()} '
            f'{str(f).lower()} false}}' for d, f in values)
        program = claim + f'\n#eval IO.println s!"[{checks}]"\n'
        self.assertEqual([True, False, False], run_lean_json(program, lean))

    def test_single_outcome_receipt_names_its_implicit_action(self):
        lean = os.environ.get('ANECHOIC_TEST_LEAN') or shutil.which('lean')
        self.assertTrue(lean, 'Lean executable unavailable')
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            pins = _pins(root, _manifest("python trace", FIRST), SOLUTION)
            evidence = verify_formal_chain(root, "C15", *pins, lean=lean)[
                "evidence"
            ]
        self.assertEqual("compile", evidence["action"])
        facts = {
            fact["key"]: (fact.get("action"), fact.get("output"))
            for fact in evidence["coverage"]
            if fact["direction"] == "manifest_solution"
        }
        self.assertEqual(("compile", "python"), facts["must_effect"])
        self.assertEqual(("compile", "python"), facts["terminal_output"])

    def test_matching_and_conflicting_receipts_replay_and_failure_has_no_receipt(
        self,
    ):
        lean = os.environ.get("ANECHOIC_TEST_LEAN") or shutil.which("lean")
        self.assertTrue(lean, "Lean executable unavailable")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            pins = _pins(
                root, _manifest("python trace", FIRST, SECOND), SOLUTION
            )
            model_pins = set()
            for expected in ('matched', 'conflicting'):
                result = verify_formal_chain(root, 'C15', *pins, action='compile', lean=lean)
                self.assertEqual(expected, result['status'], result)
                evidence = result['evidence']
                self.assertRegex(evidence['model_pin'], r'^[0-9a-f]{64}$')
                model_pins.add(evidence['model_pin'])
                self.assertTrue(evidence['validation_programs'])
                self.assertTrue(evidence['comparison_programs'])
                for item in evidence['validation_programs'] + evidence['comparison_programs']:
                    self.assertEqual(json.loads(item['stdout']), run_lean_json(item['program'], lean))
                self.assertEqual(expected, next(f['status'] for f in evidence['coverage']
                                                if f.get('key') == 'must_effect'))
                self.assertEqual({'python', 'cfel'}, {f['output'] for f in evidence['coverage']
                                                     if 'output' in f})
                for role, source in evidence['sources'].items():
                    self.assertEqual(hashlib.sha256((root / source['path']).read_bytes()).hexdigest(),
                                     source['sha256'], role)
                path = root / pins[1]['path']
                path.write_text(path.read_text().replace("'target': 'parser'", "'target': 'wrong'"))
            self.assertEqual(2, len(model_pins))
            failed = verify_formal_chain(
                root, "C15", *pins, action="compile", lean="/missing/lean"
            )
            self.assertEqual("incomplete", failed["outcome"])
            self.assertNotIn("evidence", failed)
