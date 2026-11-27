"""Exercise the pinned public C87 implementation comparison."""

import hashlib
import json
import os
import shutil
import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[5]
STUDIO = ROOT / 'LAYER_4_ENGINE_STUDIO_C14'
COMPONENT = Path(
    'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/'
    'LAYER_2_FORMAL_SPECIFICATION_C94/LAYER_3_MERMAID_RENDERER_C87'
)
SOURCE_NAMES = ('solution_diagram__pub.py', 'shape_diagram__pub.py')
SPECS = '_anechoic_anechoic/LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC_C15/SPEC_ENGINE_C75/'
COMPARATOR = 'ARCHITECTURE_ANALYSIS_C73.IMPLEMENTATION_VERIFICATION_C74.carrier_compare'
C87 = 'LAYER_2_FORMAL_SPECIFICATION_C94/'
C52 = 'LAYER_2_FORMAL_MODEL_C51/'
PAIRS = {
    'C87': (
        (C87 + '01_TIER_1_ARCHITECTURE/AN-S-4934-SPEC-COMPONENT_MANIFEST--declare-mermaid-renderer.md', 'AN-S-4934', 1, 'C94'),
        (C87 + 'LAYER_3_MERMAID_RENDERER_C87/AN-S-5028-DES-SOLUTION--render-a-mermaid-solution-diagram.md', 'AN-S-5028', 1, 'C87'),
    ),
    'C52': (
        (C52 + '01_TIER_1_ARCHITECTURE/AN-S-3066-SPEC-COMPONENT_MANIFEST--declare-generated-model.md', 'AN-S-3066', 10, 'C51'),
        (C52 + 'FEATURE_GENERATED_MODEL_C52/AN-S-5033-DES-SOLUTION--represent-bundled-model-classes.md', 'AN-S-5033', 2, 'C52'),
    ),
}


def _stage(root, relative):
    target = root / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(ROOT / relative, target)
    return hashlib.sha256(target.read_bytes()).hexdigest()


def _pins(root, component):
    pins = {}
    for role, (relative, atom, version, owner) in zip(('manifest', 'solution'), PAIRS[component], strict=True):
        path = SPECS + relative
        pins[role] = {'path': path, 'atom_id': atom, 'version': version, 'status': 'active',
                      'container_component': owner, 'sha256': _stage(root, path)}
    return pins


def _compare(root, request):
    path = root.parent / 'renderer-pins.json'
    path.write_text(json.dumps(request), encoding='utf-8')
    lean = os.environ.get('ANECHOIC_TEST_LEAN', 'lean')
    result = subprocess.run([sys.executable, '-B', '-m', COMPARATOR, '--root', str(root),
                             '--lean', lean, '--component', 'C87', '--pins', str(path)],
                            cwd=STUDIO, capture_output=True, text=True, timeout=2100, check=False)
    return result.returncode, json.loads(result.stdout)


@unittest.skipUnless(all(os.environ.get(name) for name in ('AUTOFORM_CHECKOUT', 'JOERN_HOME', 'LEAN_PATH')),
                     'Autoform and its Lean libraries are not configured')
class RendererDispatchLeanTests(unittest.TestCase):
    def test_pinned_shape_runs_through_translated_dispatcher(self):
        with TemporaryDirectory() as directory:
            root = Path(directory) / 'project'
            digests = {name: _stage(root, COMPONENT / name) for name in SOURCE_NAMES}
            export_path = COMPONENT / '_package__shared.py'
            export_digest = _stage(root, export_path)
            pins = _pins(root, 'C87')
            request = {**pins, 'witness': _pins(root, 'C52'), 'implementation_sha256': digests,
                       'export_sha256': export_digest}
            status, report = _compare(root, request)
            self.assertEqual(0, status, report)
            self.assertEqual('no_mismatch_in_cases', report['status'], report)
            self.assertEqual(pins, report['sources'])
            self.assertEqual(request['witness'], report['witness'])
            self.assertEqual({(COMPONENT / name).as_posix(): digest for name, digest in digests.items()},
                             report['implementation'])
            export = report['public_export']
            self.assertEqual((export_path.as_posix(), export_digest, 'matched'),
                             (export['path'], export['sha256'], export['status']))
            self.assertTrue(export['unresolved'] and report['unresolved'])
            self.assertEqual(['matched', 'matched'], [case['status'] for case in report['cases']])

            dispatcher = root / COMPONENT / SOURCE_NAMES[0]
            original = dispatcher.read_bytes()
            returned = b'return shape_to_mermaid(claim)'
            self.assertEqual(original.count(returned), 1)
            changed = original.replace(returned, b'return None')
            dispatcher.write_bytes(changed)
            status, report = _compare(root, request)
            self.assertEqual((1, 'unresolved'), (status, report['status']), report)
            self.assertIn('implementation source digest changed', json.dumps(report))
            self.assertFalse(report['cases'])

            digests[SOURCE_NAMES[0]] = hashlib.sha256(changed).hexdigest()
            status, report = _compare(root, request)
            self.assertEqual((1, 'mismatch'), (status, report['status']), report)
            self.assertEqual(['conflicting', 'conflicting'], [case['status'] for case in report['cases']])

            dispatcher.write_bytes(original)
            digests[SOURCE_NAMES[0]] = hashlib.sha256(original).hexdigest()
            leaf = root / COMPONENT / SOURCE_NAMES[1]
            renamed = leaf.read_bytes().replace(b'ShapeRecord', b'OtherRecord')
            leaf.write_bytes(renamed)
            digests[SOURCE_NAMES[1]] = hashlib.sha256(renamed).hexdigest()
            status, report = _compare(root, request)
            self.assertEqual((1, 'unresolved'), (status, report['status']), report)
            self.assertEqual(['unresolved: different diagram text'] * 2,
                             [case['status'] for case in report['cases']])

    def test_blank_diagram_is_a_mismatch(self):
        with TemporaryDirectory() as directory:
            root = Path(directory) / 'project'
            digests = {name: _stage(root, COMPONENT / name) for name in SOURCE_NAMES}
            export = _stage(root, COMPONENT / '_package__shared.py')
            dispatcher = root / COMPONENT / SOURCE_NAMES[0]
            original = dispatcher.read_bytes()
            returned = b'return shape_to_mermaid(claim)'
            self.assertEqual(original.count(returned), 1)
            changed = original.replace(returned, "return ' \u00a0 '".encode())
            dispatcher.write_bytes(changed)
            digests[SOURCE_NAMES[0]] = hashlib.sha256(changed).hexdigest()
            request = {**_pins(root, 'C87'), 'witness': _pins(root, 'C52'),
                       'implementation_sha256': digests, 'export_sha256': export}
            status, report = _compare(root, request)
        self.assertEqual((1, 'mismatch'), (status, report['status']), report)
        self.assertEqual(['conflicting', 'conflicting'], [case['status'] for case in report['cases']])

    def test_missing_facade_leaves_the_renderer_unresolved(self):
        with TemporaryDirectory() as directory:
            root = Path(directory) / 'project'
            digests = {name: _stage(root, COMPONENT / name) for name in SOURCE_NAMES}
            request = {**_pins(root, 'C87'), 'witness': _pins(root, 'C52'), 'implementation_sha256': digests}
            status, report = _compare(root, request)
        self.assertEqual((1, 'unresolved'), (status, report['status']), report)
        self.assertIn('_package__shared.py', json.dumps(report['unresolved']))
        self.assertFalse(report['cases'])

    def test_renderer_must_accept_the_callers_action_keyword(self):
        with TemporaryDirectory() as directory:
            root = Path(directory) / 'project'
            digests = {name: _stage(root, COMPONENT / name) for name in SOURCE_NAMES}
            export = _stage(root, COMPONENT / '_package__shared.py')
            dispatcher = root / COMPONENT / SOURCE_NAMES[0]
            original = dispatcher.read_bytes()
            signature = b'*, action=None):'
            self.assertEqual(original.count(signature), 1)
            changed = original.replace(signature, b'*, selection=None):\n    action = selection')
            dispatcher.write_bytes(changed)
            digests[SOURCE_NAMES[0]] = hashlib.sha256(changed).hexdigest()
            request = {**_pins(root, 'C87'), 'witness': _pins(root, 'C52'),
                       'implementation_sha256': digests, 'export_sha256': export}
            status, report = _compare(root, request)
        self.assertEqual((1, 'mismatch'), (status, report['status']), report)
        self.assertEqual(['conflicting', 'conflicting'], [case['status'] for case in report['cases']])
        self.assertEqual([{'positional': 'matched', 'action_none': 'conflicting'}] * 2,
                         [case['calls'] for case in report['cases']])

    def test_replay_rejects_a_changed_export_digest(self):
        with TemporaryDirectory() as directory:
            root = Path(directory) / 'project'
            digests = {name: _stage(root, COMPONENT / name) for name in SOURCE_NAMES}
            export = COMPONENT / '_package__shared.py'
            expected = _stage(root, export)
            with (root / export).open('ab') as file:
                file.write(b'\n')
            request = {**_pins(root, 'C87'), 'witness': _pins(root, 'C52'), 'implementation_sha256': digests,
                       'export_sha256': expected}
            status, report = _compare(root, request)
        self.assertEqual((1, 'unresolved'), (status, report['status']), report)
        self.assertIn('Public export source digest changed', json.dumps(report['unresolved']))
        self.assertFalse(report['cases'])
