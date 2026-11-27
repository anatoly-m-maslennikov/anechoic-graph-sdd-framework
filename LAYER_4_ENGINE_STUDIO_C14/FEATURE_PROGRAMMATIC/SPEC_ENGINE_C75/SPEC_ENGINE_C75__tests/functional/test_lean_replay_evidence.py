import hashlib
import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path

from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75._package__shared import verify_formal_chain
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_3_LEAN_TRANSLATOR_C84._package__shared import run_lean_json
from .test_direct_manifest_chain import _manifest, _pins
from .test_trace_cases import FIRST, SECOND, SOLUTION


class LeanReplayEvidenceTests(unittest.TestCase):
    def test_single_outcome_receipt_names_its_implicit_action(self):
        lean = os.environ.get('ANECHOIC_TEST_LEAN') or shutil.which('lean')
        self.assertTrue(lean, 'Lean executable unavailable')
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            pins = _pins(root, _manifest('python trace', FIRST), SOLUTION)
            evidence = verify_formal_chain(root, 'C15', *pins, lean=lean)['evidence']
        self.assertEqual('compile', evidence['action'])
        facts = {fact['key']: (fact.get('action'), fact.get('output')) for fact in evidence['coverage']
                 if fact['direction'] == 'manifest_solution'}
        self.assertEqual(('compile', 'python'), facts['must_effect'])
        self.assertEqual(('compile', 'python'), facts['terminal_output'])

    def test_matching_and_conflicting_receipts_replay_and_failure_has_no_receipt(self):
        lean = os.environ.get('ANECHOIC_TEST_LEAN') or shutil.which('lean')
        self.assertTrue(lean, 'Lean executable unavailable')
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            pins = _pins(root, _manifest('python trace', FIRST, SECOND), SOLUTION)
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
            failed = verify_formal_chain(root, 'C15', *pins, action='compile', lean='/missing/lean')
            self.assertEqual('incomplete', failed['outcome'])
            self.assertNotIn('evidence', failed)
