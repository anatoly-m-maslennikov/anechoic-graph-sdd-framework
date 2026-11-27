"""Check the published Diagnostics contract against fresh Autoform Lean."""

import hashlib
import json
import os
import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[5]
STUDIO = ROOT / 'LAYER_4_ENGINE_STUDIO_C14'
FORMAL = Path('SPEC_ENGINE_C75/LAYER_2_FORMAL_SPECIFICATION_C94')
CARRIERS = Path('_anechoic_anechoic/LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC_C15') / FORMAL
SOURCE = STUDIO / 'FEATURE_PROGRAMMATIC' / FORMAL / 'LAYER_1_DIAGNOSTICS_C90/diagnostics__pub.py'
EXPORT = SOURCE.with_name('_package__shared.py')
CLI = 'ARCHITECTURE_ANALYSIS_C73.IMPLEMENTATION_VERIFICATION_C74.carrier_compare'
PINS = {
    'manifest': {
        'path': (CARRIERS / '01_TIER_1_ARCHITECTURE/AN-S-4937-SPEC-COMPONENT_MANIFEST--declare-diagnostics.md').as_posix(),
        'atom_id': 'AN-S-4937', 'version': 4, 'status': 'active',
        'container_component': 'C94',
    },
    'solution': {
        'path': (CARRIERS / 'LAYER_1_DIAGNOSTICS_C90/AN-S-5024-DES-SOLUTION--form-a-diagnostic-from-a-finding.md').as_posix(),
        'atom_id': 'AN-S-5024', 'version': 4, 'status': 'active',
        'container_component': 'C90',
    },
}


def _compare(pins, source, root, request_path, *, export_sha256=None):
    request = {**pins, 'implementation_sha256': hashlib.sha256(source).hexdigest()}
    if export_sha256 is not None:
        request['export_sha256'] = export_sha256
    request_path.write_text(json.dumps(request), encoding='utf-8')
    result = subprocess.run(
        [sys.executable, '-B', '-m', CLI, '--root', str(root), '--component', 'C90',
         '--pins', str(request_path), '--lean', os.environ.get('ANECHOIC_TEST_LEAN', 'lean')],
        cwd=STUDIO, capture_output=True, text=True, timeout=2000, check=False,
    )
    return result.returncode, json.loads(result.stdout)


def _pinned_specs():
    return {role: {**pin, 'sha256': hashlib.sha256((ROOT / pin['path']).read_bytes()).hexdigest()}
            for role, pin in PINS.items()}


def _stage(root, pins, source):
    for pin in pins.values():
        target = root / pin['path']
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((ROOT / pin['path']).read_bytes())
    target = root / SOURCE.relative_to(ROOT)
    target.parent.mkdir(parents=True)
    target.write_bytes(source)
    target.with_name(EXPORT.name).write_bytes(EXPORT.read_bytes())


@unittest.skipUnless(all(os.environ.get(name) for name in ('AUTOFORM_CHECKOUT', 'JOERN_HOME', 'LEAN_PATH')),
                     'Autoform and its Lean libraries are not configured')
class DiagnosticLeanComparisonTests(unittest.TestCase):
    def test_shared_verdict_matches_policy_for_any_status_list(self):
        pins, source = _pinned_specs(), SOURCE.read_bytes()
        original = b"return ('conflicting' if 'conflicting' in statuses else"
        mutated = (b"return ('unresolved' if 'unresolved' in statuses else\n"
                   b"            " + original.removeprefix(b'return ('))
        self.assertEqual(1, source.count(original))
        changed = source.replace(original, mutated)
        with TemporaryDirectory() as directory:
            folder = Path(directory)
            path = folder / 'pins.json'
            code, control = _compare(pins, source, ROOT, path)
            root = folder / 'mutation'
            _stage(root, pins, changed)
            result, report = _compare(pins, changed, root, path)
        self.assertEqual((0, 'no_mismatch_in_cases'),
                         (code, control['status']), control)
        self.assertEqual('proved', control['verdict_proof']['status'], control)
        self.assertEqual('publicVerdictMatchesContract',
                         control['verdict_proof']['theorem'])
        self.assertRegex(control['verdict_proof']['sha256'], r'^[0-9a-f]{64}$')
        self.assertRegex(control['verdict_proof']['authored_lean_sha256'],
                         r'^[0-9a-f]{64}$')
        self.assertEqual((1, 'unresolved'), (result, report['status']), report)
        self.assertEqual('unresolved', report['verdict_proof']['status'])
        self.assertEqual('proved', report['effect']['status'])
        self.assertEqual(['matched'] * 3,
                         [row['implementation'] for row in report['facts']])

    def test_agreeing_changed_verdict_specs_cannot_prove_original_code(self):
        pins, source = _pinned_specs(), SOURCE.read_bytes()
        pending = b"'unresolved_or_empty': True"
        clear = b"'unresolved_or_empty': False"
        with TemporaryDirectory() as directory:
            root = Path(directory)
            _stage(root, pins, source)
            for pin in pins.values():
                path = root / pin['path']
                original = path.read_bytes()
                self.assertEqual((1, 1), (original.count(pending),
                                          original.count(clear)))
                changed = original.replace(pending, b'PLACEHOLDER', 1)
                changed = changed.replace(clear, pending, 1)
                changed = changed.replace(b'PLACEHOLDER', clear, 1)
                path.write_bytes(changed)
                pin['sha256'] = hashlib.sha256(changed).hexdigest()
            code, report = _compare(pins, source, root, root / 'pins.json')
        self.assertEqual((1, 'unresolved'), (code, report['status']), report)
        self.assertEqual('proved', report['effect']['status'])
        verdict = report['verdict_proof']
        self.assertEqual('unresolved', verdict['status'])
        self.assertRegex(verdict['authored_lean_sha256'], r'^[0-9a-f]{64}$')

    def test_extra_verdict_solution_guard_leaves_proof_unresolved(self):
        pins, source = _pinned_specs(), SOURCE.read_bytes()
        with TemporaryDirectory() as directory:
            root = Path(directory)
            _stage(root, pins, source)
            path = root / pins['solution']['path']
            original = path.read_bytes()
            guard = b"{'has_conflict': True}"
            self.assertEqual(1, original.count(guard))
            changed = original.replace(
                guard, b"{'has_conflict': True, 'unresolved_or_empty': True}")
            path.write_bytes(changed)
            pins['solution']['sha256'] = hashlib.sha256(changed).hexdigest()
            code, report = _compare(pins, source, root, root / 'pins.json')
        self.assertEqual((1, 'unresolved'), (code, report['status']), report)
        self.assertEqual('proved', report['effect']['status'])
        verdict = report['verdict_proof']
        self.assertEqual('unresolved', verdict['status'])
        self.assertRegex(verdict['authored_lean_sha256'], r'^[0-9a-f]{64}$')

    def test_cli_checks_declared_values_and_detects_wrong_field(self):
        pins = _pinned_specs()
        source = SOURCE.read_bytes()
        self.assertEqual(source.count(b"'message': message"), 1)
        mutant = source.replace(b"'message': message", b"'message': field")
        with TemporaryDirectory() as directory:
            folder = Path(directory)
            request_path = folder / 'pins.json'
            digest = hashlib.sha256(EXPORT.read_bytes()).hexdigest()
            status, control = _compare(pins, source, ROOT, request_path, export_sha256=digest)
            self.assertEqual(status, 0, control)
            self.assertEqual(control['formal']['sources'], pins)
            self.assertEqual(control['formal']['translation']['status'], 'matched')
            self.assertEqual(control['status'], 'no_mismatch_in_cases')
            self.assertEqual('proved', control['proof']['status'], control)
            self.assertEqual({'target': 'C90.source_diagnostic', 'outcome': 'formed', 'status': 'proved'},
                             control['effect'])
            self.assertEqual('matched', control['public_export']['status'], control)
            self.assertTrue(control['unresolved'])
            checked = {tuple(row['right']): row for row in control['facts']}
            fields = {('result_returned', name) for name in ('source', 'field', 'message')}
            self.assertEqual(set(checked), fields)
            for row in checked.values():
                self.assertEqual(row['solution'], 'matched')
                self.assertEqual(row['implementation'], 'matched')
            root = folder / 'mutation'
            _stage(root, pins, mutant)
            status, mutated = _compare(pins, mutant, root, request_path)
            self.assertEqual(status, 1, mutated)
            self.assertEqual(mutated['status'], 'mismatch')
            self.assertEqual([(row['right'], row['solution']) for row in mutated['facts']
                              if row['implementation'] == 'conflicting'],
                             [(['result_returned', 'message'], 'matched')])

            fields = b"'source': source, 'field': field"
            self.assertEqual(source.count(fields), 1)
            reordered = source.replace(fields, b"'field': field, 'source': source")
            root = folder / 'reordered'
            _stage(root, pins, reordered)
            status, report = _compare(pins, reordered, root, request_path)
            self.assertEqual((0, 'proved'), (status, report['proof']['status']), report)

    def test_cli_leaves_a_solution_with_an_unguarded_alternative_unresolved(self):
        pins = _pinned_specs()
        source = SOURCE.read_bytes()
        with TemporaryDirectory() as directory:
            root = Path(directory)
            _stage(root, pins, source)
            path = root / pins['solution']['path']
            text = path.read_text(encoding='utf-8')
            state = "            'returning': {'on': {"
            self.assertEqual(text.count(state), 1)
            alternative = """            'returning': {'on': {
                'return_unchecked': {'target': 'done', 'guard': {'type': 'matchesTrace',
                    'params': {'kind': 'output', 'outcome': 'reported'}}},
"""
            data = text.replace(state, alternative).encode()
            path.write_bytes(data)
            pins['solution']['sha256'] = hashlib.sha256(data).hexdigest()
            status, report = _compare(pins, source, root, root / 'pins.json')
            self.assertEqual(status, 1, report)
            self.assertEqual(report['status'], 'unresolved')
            self.assertEqual(len(report['facts']), 3)
            self.assertTrue(all(row['solution'] == 'unresolved' and row['implementation'] == 'matched'
                                for row in report['facts']), report)

    def test_finding_proof_checks_inputs_outside_the_string_witness(self):
        pins = _pinned_specs()
        source = SOURCE.read_bytes()
        self.assertEqual(source.count(b"'message': message"), 1)
        mutant = source.replace(b"'message': message", b"'message': field if message == 'other' else message")
        with TemporaryDirectory() as directory:
            root = Path(directory)
            _stage(root, pins, mutant)
            status, report = _compare(pins, mutant, root, root / 'pins.json')
            self.assertEqual((1, 'unresolved'), (status, report['status']), report)
            self.assertEqual('unresolved', report['proof']['status'], report)
            self.assertEqual('unresolved', report['effect']['status'])
            self.assertEqual(len(report['facts']), 3)
            self.assertTrue(all(row['implementation'] == 'matched' for row in report['facts']), report)

    def test_rebound_facade_leaves_finding_unresolved(self):
        pins, source = _pinned_specs(), SOURCE.read_bytes()
        with TemporaryDirectory() as directory:
            root = Path(directory)
            _stage(root, pins, source)
            facade = root / EXPORT.relative_to(ROOT)
            original = facade.read_bytes()
            changed = original.replace(b'finding as finding', b'verdict as finding')
            self.assertNotEqual(original, changed)
            facade.write_bytes(changed)
            digest = hashlib.sha256(original).hexdigest()
            exit_code, stale = _compare(pins, source, root, root / 'pins.json', export_sha256=digest)
            self.assertEqual((1, 'unresolved'), (exit_code, stale['status']), stale)
            self.assertIn('Public export source digest changed', json.dumps(stale['unresolved']))
            self.assertFalse(stale['facts'])
            status, report = _compare(pins, source, root, root / 'pins.json')
        self.assertEqual((1, 'unresolved'), (status, report['status']), report)
        self.assertEqual(hashlib.sha256(changed).hexdigest(), report['public_export']['sha256'])
        self.assertIn('Declared public export does not bind', json.dumps(report['unresolved']))
        self.assertIn('diagnostics__pub.py:<module>.verdict', json.dumps(report['unresolved']))
        self.assertFalse(report['facts'])

    def test_formation_conflict_is_visible_when_values_match(self):
        pins, source = _pinned_specs(), SOURCE.read_bytes()
        with TemporaryDirectory() as directory:
            root = Path(directory)
            _stage(root, pins, source)
            path = root / pins['solution']['path']
            original = path.read_bytes()
            changed = original.replace(b"'outcome': 'formed'", b"'outcome': 'emitted'")
            self.assertNotEqual(original, changed)
            path.write_bytes(changed)
            pins['solution']['sha256'] = hashlib.sha256(changed).hexdigest()
            status, report = _compare(pins, source, root, root / 'pins.json')
            manifest = root / pins['manifest']['path']
            raw = manifest.read_bytes()
            changed = raw.replace(b"'formed'", b"'emitted'")
            self.assertNotEqual(raw, changed)
            manifest.write_bytes(changed)
            pins['manifest']['sha256'] = hashlib.sha256(changed).hexdigest()
            code, unmeasured = _compare(pins, source, root, root / 'pins.json')
        self.assertEqual((1, 'mismatch'), (status, report['status']), report)
        self.assertEqual('conflicting', report['effect']['status'])
        self.assertTrue(report['facts'])
        self.assertTrue(all(row['implementation'] == 'matched' for row in report['facts']))
        self.assertEqual((1, 'unresolved'), (code, unmeasured['status']), unmeasured)
        self.assertEqual('proved', unmeasured['proof']['status'])
        self.assertEqual('unresolved', unmeasured['effect']['status'])

    def test_unmeasured_output_guard_leaves_formation_unresolved(self):
        pins, source = _pinned_specs(), SOURCE.read_bytes()
        with TemporaryDirectory() as directory:
            root = Path(directory)
            _stage(root, pins, source)
            path = root / pins['solution']['path']
            original = path.read_bytes()
            changed = original.replace(b"'same_as': {", b"'same_as': {'unreturned_field': 'source', ")
            self.assertNotEqual(original, changed)
            path.write_bytes(changed)
            pins['solution']['sha256'] = hashlib.sha256(changed).hexdigest()
            status, report = _compare(pins, source, root, root / 'pins.json')
        self.assertEqual((1, 'unresolved'), (status, report['status']), report)
        self.assertEqual('proved', report['proof']['status'])
        self.assertEqual('unresolved', report['effect']['status'])

    def test_unmeasured_contract_type_prevents_a_pass(self):
        pins, source = _pinned_specs(), SOURCE.read_bytes()
        with TemporaryDirectory() as directory:
            root = Path(directory)
            _stage(root, pins, source)
            path = root / pins['manifest']['path']
            original = path.read_bytes()
            prefix = b'    same_values=('
            self.assertEqual(original.count(prefix), 1)
            changed = original.replace(
                prefix, b"    value_types={('result_returned', 'message'): 'integer'},\n" + prefix)
            path.write_bytes(changed)
            pins['manifest']['sha256'] = hashlib.sha256(changed).hexdigest()
            status, report = _compare(pins, source, root, root / 'pins.json')
        self.assertEqual((1, 'unresolved'), (status, report['status']), report)
        self.assertEqual('proved', report['effect']['status'])
        self.assertEqual([{'direction': 'manifest_solution', 'action': 'finding',
                           'key': 'value_types', 'field': ['result_returned', 'message'],
                           'expected': 'integer', 'status': 'unresolved', 'output': 'reported'}],
                         report['unresolved_obligations'])
