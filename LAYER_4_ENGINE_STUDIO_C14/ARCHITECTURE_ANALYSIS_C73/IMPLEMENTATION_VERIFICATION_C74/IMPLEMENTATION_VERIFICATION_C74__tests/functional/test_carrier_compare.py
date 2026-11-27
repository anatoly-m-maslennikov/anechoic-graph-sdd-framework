"""Check the admitted carrier models and the comparison failure boundary."""
import hashlib
import json
import shutil
import subprocess
import sys
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
_DIRECT_PATHS = {
    'manifest': (Path(_PATHS['manifest']).parent.parent
                 / '01_draft/AN-S-3069@63-draft-SPEC-COMPONENT_MANIFEST--declare-adapters.md'),
    'solution': (Path(_PATHS['solution']).parent
                 / 'AN-S-4742@2-draft-SWD-SOLUTION--extract-the-carrier-body.md'),
}
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


def _run_pinned_cli(request):
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / 'pins.json'
        path.write_text(json.dumps(request), encoding='utf-8')
        return subprocess.run(
            [sys.executable, '-B', '-m', 'ARCHITECTURE_ANALYSIS_C73.IMPLEMENTATION_VERIFICATION_C74.carrier_compare',
             '--root', str(ROOT), '--pins', str(path)],
            cwd=ROOT / 'LAYER_4_ENGINE_STUDIO_C14', capture_output=True, text=True, timeout=240, check=False,
        )


def _formal_witnesses():
    invalid = {'bounds': None, 'body': None}
    pins = {
        'manifest': {'path': _DIRECT_PATHS['manifest'].as_posix(), 'atom_id': 'AN-S-3069',
                     'version': 63, 'status': 'draft', 'container_component': 'C16'},
        'solution': {'path': _DIRECT_PATHS['solution'].as_posix(), 'atom_id': 'AN-S-4742',
                     'version': 2, 'status': 'draft', 'container_component': 'C30'},
    }
    return {
        'outcome': 'compared',
        'translation': {'status': 'bounded_match'},
        'lean': SPEC + SPEC.replace('CarrierBodyContract', 'CarrierBodySolution').removeprefix('import Lean\n'),
        'sources': {role: {**pin, 'sha256': hashlib.sha256((ROOT / pin['path']).read_bytes()).hexdigest()}
                    for role, pin in pins.items()},
        'cases': [
            {'input': list(b'---\n---\n\xff'), 'manifest': invalid, 'solution': invalid},
            {'input': list(b'---\n---'), 'manifest': invalid, 'solution': invalid},
        ],
    }


def _pins(formal):
    return {role: {key: value for key, value in source.items() if key != 'sha256'}
            for role, source in formal['sources'].items()}


class CarrierModelTests(unittest.TestCase):
    def test_cli_requires_exact_source_digests(self):
        request = {**_formal_witnesses()['sources'], 'implementation_sha256': 'invalid'}
        result = _run_pinned_cli(request)
        self.assertEqual(result.returncode, 1, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report['status'], 'unresolved')
        self.assertIn('implementation_sha256', report['reason'])

    @unittest.skipUnless(shutil.which('lean'), 'Lean is unavailable')
    def test_cli_replays_the_actual_pinned_framing_comparison(self):
        source_digest = hashlib.sha256((ROOT / _SOURCE).read_bytes()).hexdigest()
        pins = _formal_witnesses()['sources']
        request = {**pins, 'implementation_sha256': source_digest}
        result = _run_pinned_cli(request)
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout[:1200])
        report = json.loads(result.stdout)
        self.assertEqual(report['formal']['sources'], pins)
        self.assertEqual(report['evidence']['source_sha256'], source_digest)
        self.assertEqual(report['status'], 'no_mismatch_in_cases')
        self.assertEqual(len(report['cases']), 133)
        self.assertTrue(report['evidence']['unresolved'])
        self.assertFalse(report['findings'])
        self.assertEqual(report['proof']['status'], 'proved')
        self.assertEqual(report['proof']['quantified_over'], ['input', 'path'])
        self.assertIn('CPython regex execution and path conversion require separate evidence.',
                      report['evidence']['unresolved'])
        formal = {**report['formal'], 'cases': [
            {'input': row['raw'], 'manifest': row['manifest'], 'solution': row['solution']}
            for row in report['cases']
        ]}
        self._assert_failed_proof_keeps_samples(formal, request)
        self._assert_missing_theorem_keeps_samples(formal, request)
        stale = _run_pinned_cli({**request, 'solution': {**pins['solution'], 'sha256': '0' * 64}})
        self.assertEqual(stale.returncode, 1, stale.stderr)
        failure = json.loads(stale.stdout)
        self.assertEqual(failure['status'], 'unresolved')
        self.assertEqual(failure['formal']['diagnostics'][0]['field'], 'sha256')
        self.assertFalse(failure['cases'])

    def _assert_failed_proof_keeps_samples(self, formal, request):
        model, evidence = generate(ROOT)
        declaration = 'def closingPatterns : List (List Nat) := '
        self.assertEqual(model.count(declaration), 1)
        mutated = model.replace(declaration, declaration + '[201, 202, 203] :: ')
        module = 'ARCHITECTURE_ANALYSIS_C73.IMPLEMENTATION_VERIFICATION_C74.carrier_direct'
        with patch(f'{module}.generate', return_value=(mutated, evidence)):
            report = compare(ROOT, **request, formal_verifier=lambda *args, **kwargs: formal)
        self._assert_unresolved_proof(report)

    def _assert_missing_theorem_keeps_samples(self, formal, request):
        read_bytes = Path.read_bytes

        def without_manifest_body(path):
            raw = read_bytes(path)
            if path.name != 'framing_equivalence_proof.lean':
                return raw
            head, removed = raw.split(b'theorem manifest_body', maxsplit=1)
            self.assertIn(b'end C30ImplementationEquivalence', removed)
            return head + b'end C30ImplementationEquivalence\n'

        with patch.object(Path, 'read_bytes', without_manifest_body):
            report = compare(ROOT, **request, formal_verifier=lambda *args, **kwargs: formal)
        self._assert_unresolved_proof(report)
        self.assertIn('C30ImplementationEquivalence.manifest_body', report['proof']['reason'])

    def _assert_unresolved_proof(self, report):
        self.assertEqual(len(report['cases']), 133)
        self.assertFalse(report['findings'])
        self.assertTrue(all(row['code_matches_python'] and row['manifest_matches_code']
                            and row['solution_matches_code'] for row in report['cases']))
        self.assertEqual(report['proof']['status'], 'unresolved')
        self.assertEqual(report['status'], 'unresolved')

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
        with patch('ARCHITECTURE_ANALYSIS_C73.IMPLEMENTATION_VERIFICATION_C74.carrier_compare.formal_inputs',
                   return_value=([SPEC, SPEC], {})):
            report = compare(ROOT, '/missing/lean')
        self.assertEqual(report['status'], 'unresolved')

    def test_unbound_solution_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            for name, rel in _PATHS.items():
                target = Path(tmp) / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                data = (ROOT / _DIRECT_PATHS[name]).read_bytes()
                target.write_bytes(data.replace(b'status: draft', b'status: active') if name == 'manifest' else data)
            with self.assertRaisesRegex(ValueError, 'binding'):
                formal_inputs(tmp)

    def test_embedded_contract_uses_manifest_hash(self):
        with tempfile.TemporaryDirectory() as tmp:
            for name, rel in _PATHS.items():
                target = Path(tmp) / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                data = (ROOT / _DIRECT_PATHS[name]).read_bytes()
                data = (data.replace(b'status: draft', b'status: active') if name == 'manifest'
                        else data.replace(b'AN-S-3069@63-draft', b'AN-S-3069@63'))
                lean = b'\n```lean\n' + SPEC.encode() + b'```\n'
                data = (data + lean if name == 'manifest'
                        else data.replace(b'### Formal Claim\n', b'### Formal Claim\n' + lean))
                target.write_bytes(data)
            blocks, evidence = formal_inputs(tmp)
            self.assertEqual(evidence['manifest']['sha256'], evidence['contract']['sha256'])
            self.assertEqual(evidence['manifest']['atom_id'], evidence['contract']['atom_id'])
            self.assertEqual(len(blocks), 2)

    def test_duplicate_function_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / _SOURCE
            target.parent.mkdir(parents=True)
            target.write_bytes((ROOT / _SOURCE).read_bytes() + b'\ndef source_body(): pass\n')
            with self.assertRaisesRegex(ValueError, 'unsupported carrier functions'):
                generate(tmp)

    def test_extra_lean_output_is_unresolved(self):
        result = SimpleNamespace(returncode=0, stdout='notice true\n[true]', stderr='')
        with (patch('shutil.which', return_value='lean'), patch('subprocess.run', return_value=result),
              patch('ARCHITECTURE_ANALYSIS_C73.IMPLEMENTATION_VERIFICATION_C74.carrier_compare.formal_inputs',
                    return_value=([SPEC, SPEC], {}))):
            report = compare(ROOT)
        self.assertEqual(report['status'], 'unresolved')

    @unittest.skipUnless(shutil.which('lean'), 'Lean is unavailable')
    def test_direct_comparison_checks_the_python_oracle(self):
        formal = _formal_witnesses()
        pins = _pins(formal)

        def verify(root, component, manifest, *, solution, lean):
            self.assertEqual((root, component, manifest, solution), (ROOT, 'C30', pins['manifest'], pins['solution']))
            return formal

        report = compare(ROOT, **pins, formal_verifier=verify)
        self.assertEqual(report['status'], 'mismatch', report['evidence'])
        self.assertEqual(report['findings'], [
            {'model': role, 'case': 1, 'raw': list(b'---\n---\n\xff'), 'differences': ['bounds', 'body']}
            for role in ('manifest', 'solution')
        ])
        self.assertEqual(report['cases'][1]['error'], f"{Path('case-2/carrier-2.md')}: unsupported frontmatter delimiter")
        self.assertTrue(all(row['code_matches_python'] for row in report['cases']))

    def test_direct_comparison_rejects_different_solution_pin(self):
        formal = _formal_witnesses()
        pins = _pins(formal)
        pins['solution'].update(path=_PATHS['solution'], version=1)
        report = compare(ROOT, **pins, formal_verifier=lambda *a, **kw: formal)
        self.assertEqual(report['status'], 'unresolved')
        self.assertEqual(report['evidence']['unresolved'], ['Solution receipt does not match the requested pin'])

    def test_direct_comparison_replays_digest_pins(self):
        formal = _formal_witnesses()
        pins = formal['sources']
        source_digest = hashlib.sha256((ROOT / _SOURCE).read_bytes()).hexdigest()

        def verify(*args, **kwargs):
            return formal

        report = compare(ROOT, '/missing/lean', **pins, formal_verifier=verify,
                         implementation_sha256=source_digest)
        self.assertEqual(report['evidence']['source_sha256'], source_digest)
        self.assertIn('Lean executable unavailable', report['evidence']['unresolved'])
        stale = compare(ROOT, '/missing/lean', **pins, formal_verifier=verify,
                        implementation_sha256='0' * 64)
        self.assertEqual(stale['evidence']['unresolved'], ['Implementation source digest changed'])
        self.assertEqual(stale['cases'], [])
        changed = {**pins, 'solution': {**pins['solution'], 'sha256': '0' * 64}}
        stale = compare(ROOT, '/missing/lean', **changed, formal_verifier=verify)
        self.assertEqual(stale['evidence']['unresolved'], ['Solution receipt does not match the requested pin'])

    def test_direct_comparison_checks_both_formal_hashes(self):
        for role in ('manifest', 'solution'):
            with self.subTest(role=role):
                formal = _formal_witnesses()
                formal['sources'][role]['sha256'] = 'changed'
                report = compare(ROOT, **_pins(formal),
                                 formal_verifier=lambda *a, value=formal, **kw: value)
                self.assertEqual(report['status'], 'unresolved')
                self.assertEqual(report['evidence']['unresolved'], [f'{role.title()} bytes changed after formal comparison'])

    def test_direct_comparison_reads_the_manifest_operations(self):
        formal = _formal_witnesses()
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            for role, source in formal['sources'].items():
                relative = source['path']
                raw = (ROOT / relative).read_bytes()
                if role == 'manifest':
                    old = b"'operations': ['frontmatter_bounds', 'source_body']"
                    self.assertIn(old, raw)
                    raw = raw.replace(old, b"'operations': ['parse_settings_bytes']")
                target = root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(raw)
                source['sha256'] = hashlib.sha256(raw).hexdigest()
            report = compare(root, **_pins(formal), formal_verifier=lambda *a, **kw: formal)
        self.assertEqual(report['status'], 'unresolved')
        self.assertIn('Manifest does not declare the two checked framing operations', report['evidence']['unresolved'])

    @unittest.skipUnless(shutil.which('lean'), 'Lean is unavailable')
    def test_direct_comparison_rejects_constant_path_in_lowered_errors(self):
        formal = _formal_witnesses()
        model, evidence = generate(ROOT)
        self.assertIn('path ++', model)
        mutated = model.replace('path ++', '(if path.isEmpty then "carrier.md" else "carrier.md") ++')
        module = 'ARCHITECTURE_ANALYSIS_C73.IMPLEMENTATION_VERIFICATION_C74.carrier_direct'
        with patch(f'{module}.generate', return_value=(mutated, evidence)):
            report = compare(ROOT, **_pins(formal), formal_verifier=lambda *a, **kw: formal)
        self.assertEqual(report['status'], 'unresolved')
        self.assertFalse(report['cases'][1]['code_matches_python'])

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
