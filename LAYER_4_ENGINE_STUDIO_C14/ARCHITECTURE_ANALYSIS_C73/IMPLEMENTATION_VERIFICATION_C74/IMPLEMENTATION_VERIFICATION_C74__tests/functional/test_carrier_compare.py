"""Check the admitted carrier models and the comparison failure boundary."""
import shutil
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from ARCHITECTURE_ANALYSIS_C73.IMPLEMENTATION_VERIFICATION_C74.carrier_compare import (
    compare,
)
from ARCHITECTURE_ANALYSIS_C73.IMPLEMENTATION_VERIFICATION_C74.carrier_formal import (
    _PATHS,
    formal_inputs,
)
from ARCHITECTURE_ANALYSIS_C73.IMPLEMENTATION_VERIFICATION_C74.carrier_model import (
    _SOURCE,
    generate,
)

ROOT = Path(__file__).resolve().parents[5]
SPEC = '''import Lean
namespace CarrierBodyContract
inductive Outcome where
  | missingDelimiter
  | body (bytes : List Nat)
  deriving BEq
def bounds (_ : List Nat) : Option (Nat × Nat × Nat) := none
def body (_ : List Nat) : Outcome := .missingDelimiter
end CarrierBodyContract
'''


class CarrierModelTests(unittest.TestCase):
    def test_live_source_and_analysis(self):
        model, evidence = generate(ROOT)
        self.assertIn('findClosing', model)
        self.assertEqual(set(evidence['symbols']), {'frontmatter_bounds', 'source_body'})
        self.assertTrue(evidence['calls'])

    def test_unknown_source_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / _SOURCE
            target.parent.mkdir(parents=True)
            target.write_bytes((ROOT / _SOURCE).read_bytes().replace(b'opening_end - 1', b'opening_end - 2'))
            with self.assertRaisesRegex(ValueError, 'unsupported carrier operation'):
                generate(tmp)

    def test_missing_lean_is_unresolved(self):
        report = compare(ROOT, '/missing/lean')
        self.assertEqual(report['status'], 'unresolved')

    def test_unbound_solution_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            for name, rel in _PATHS.items():
                target = Path(tmp) / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                data = (ROOT / rel).read_bytes()
                target.write_bytes(data.replace(b'AN-S-3303@16-draft', b'AN-S-3303@15') if name == 'solution' else data)
            with self.assertRaisesRegex(ValueError, 'binding'):
                formal_inputs(tmp)

    def _spec_fixture(self, root, mutate=None):
        for name, rel in _PATHS.items():
            target = Path(root) / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            data = (ROOT / rel).read_bytes()
            target.write_bytes(mutate(name, data) if mutate else data)

    @unittest.skipUnless(shutil.which('lean'), 'Lean is unavailable')
    def test_formal_only_without_implementation(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._spec_fixture(tmp)
            with patch('ARCHITECTURE_ANALYSIS_C73.IMPLEMENTATION_VERIFICATION_C74.carrier_compare.generate',
                       side_effect=AssertionError('implementation source used')), patch(
                    'ARCHITECTURE_ANALYSIS_C73.IMPLEMENTATION_VERIFICATION_C74.carrier_compare._observations',
                    side_effect=AssertionError('implementation executed')):
                report = compare(tmp, formal_only=True)
        self.assertEqual(report['status'], 'no_mismatch_in_cases')
        self.assertEqual(len(report['cases']), 8)
        self.assertIn('no inference', report['evidence']['scope'])
        self.assertTrue(report['evidence']['coverage_unresolved'])
        for direction in ('manifest_to_contract', 'manifest_to_solution'):
            self.assertEqual(report['directions'][direction]['verdict'], 'unresolved')
        self.assertEqual(report['directions']['contract_to_solution']['case_count'], 8)
        self.assertTrue(all(v['verdict'] == 'no_mismatch_in_cases' for v in
                            report['directions']['contract_to_solution']['behavioral_witnesses']))

    @unittest.skipUnless(shutil.which('lean'), 'Lean is unavailable')
    def test_manifest_with_imports_only(self):
        def mutate(name, data):
            if name != 'manifest':
                return data
            start = data.find(b"                'exports': {")
            if start < 0:
                return data
            end = data.index(b'                },\n', start) + len(b'                },\n')
            return data[:start] + data[end:]
        with tempfile.TemporaryDirectory() as tmp:
            self._spec_fixture(tmp, mutate)
            blocks, evidence = formal_inputs(tmp)
            with patch('ARCHITECTURE_ANALYSIS_C73.IMPLEMENTATION_VERIFICATION_C74.carrier_compare.formal_inputs',
                       return_value=(blocks, evidence)):
                report = compare(ROOT, '/missing/lean')
            formal = compare(tmp, formal_only=True)
        self.assertEqual(report['status'], 'unresolved')
        self.assertIn('Lean executable unavailable', report['evidence']['unresolved'])
        self.assertEqual(formal['status'], 'no_mismatch_in_cases')
        self.assertEqual(len(formal['cases']), 8)
        for direction in ('manifest_to_contract', 'manifest_to_solution'):
            self.assertEqual(formal['directions'][direction]['verdict'], 'unresolved')
        self.assertEqual(formal['findings'], [])

    @unittest.skipUnless(shutil.which('lean'), 'Lean is unavailable')
    def test_formal_only_solution_disagreement(self):
        def mutate(name, data):
            if name != 'solution':
                return data
            for prefix in (b'13, 10, 45, 45, 45', b'10, 45, 45, 45'):
                original = b'[' + prefix + b', 13, 10]'
                self.assertIn(original, data)
                data = data.replace(original, b'[' + prefix + b', 13, 11]')
            return data
        with tempfile.TemporaryDirectory() as tmp:
            self._spec_fixture(tmp, mutate)
            report = compare(tmp, formal_only=True)
        self.assertEqual(report['status'], 'mismatch')
        body = report['directions']['contract_to_solution']['behavioral_witnesses'][1]
        self.assertEqual(body['verdict'], 'mismatch')
        self.assertTrue(body['differing_cases'])
        self.assertTrue(any(f['kind'] == 'formal_disagreement' and f['body'] and f['raw']
                            for f in report['findings']))

    def test_formal_only_rejects_malformed_output(self):
        result = SimpleNamespace(returncode=0, stdout='[true]', stderr='')
        with patch('shutil.which', return_value='lean'), patch('subprocess.run', return_value=result):
            report = compare(ROOT, formal_only=True)
        self.assertEqual(report['status'], 'unresolved')

    def test_duplicate_function_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / _SOURCE
            target.parent.mkdir(parents=True)
            target.write_bytes((ROOT / _SOURCE).read_bytes() + b'\ndef source_body(): pass\n')
            with self.assertRaisesRegex(ValueError, 'unsupported carrier functions'):
                generate(tmp)

    def test_extra_lean_output_is_unresolved(self):
        result = SimpleNamespace(returncode=0, stdout='notice true\n[true]', stderr='')
        with patch('shutil.which', return_value='lean'), patch('subprocess.run', return_value=result):
            report = compare(ROOT)
        self.assertEqual(report['status'], 'unresolved')

    @unittest.skipUnless(shutil.which('lean'), 'Lean is unavailable')
    def test_confirmed_spec_mismatch_has_python_witness(self):
        blocks = [SPEC, SPEC.replace('CarrierBodyContract', 'CarrierBodySolution')]
        with patch('ARCHITECTURE_ANALYSIS_C73.IMPLEMENTATION_VERIFICATION_C74.carrier_compare.formal_inputs',
                   return_value=(blocks, {})):
            report = compare(ROOT)
        self.assertEqual(report['status'], 'mismatch')
        self.assertTrue(all(case['code_matches_python'] for case in report['cases']))
        self.assertTrue(any(row['case'] == 'empty_crlf' and row['bounds']
                            for row in report['findings']))


if __name__ == '__main__':
    unittest.main()
