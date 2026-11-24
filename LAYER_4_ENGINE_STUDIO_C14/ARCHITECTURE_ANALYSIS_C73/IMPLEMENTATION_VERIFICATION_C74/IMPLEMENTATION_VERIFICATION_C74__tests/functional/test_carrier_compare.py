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
                target.write_bytes(data.replace(b'AN-S-3303@15', b'AN-S-3303@14') if name == 'solution' else data)
            with self.assertRaisesRegex(ValueError, 'binding'):
                formal_inputs(tmp)

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
