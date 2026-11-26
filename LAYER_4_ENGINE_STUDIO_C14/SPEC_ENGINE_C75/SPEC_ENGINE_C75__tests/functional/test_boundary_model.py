import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from SPEC_ENGINE_C75.LAYER_1_SPEC_SOURCES_C83.boundary_model__pub import load_boundary_model, load_manifest


def _inputs(tmp_path):
    pins = []
    for role, template, relation in (
        ('manifest', 'component_manifest', ''),
        ('contract', 'component_contract', '  ANSWERS: [AN-S-1]\n'),
        ('solution', 'decision', '  IS_SOLUTION_FOR: [AN-S-2@1]\n'),
    ):
        index = len(pins) + 1
        pin = {'path': role + '.md', 'atom_id': f'AN-S-{index}', 'version': 1,
               'status': 'active', 'container_component': 'C7'}
        body = ("## Formal Manifest\n\n```python\nfrom anechoic.formal_claims import declare_entity\n"
                "from anechoic.model import ComponentManifest\n"
                "declare_entity(entity_name='Component Manifest', instance=ComponentManifest("
                "component_id='C7', name='Test', boundaries={'io': {'server': 'API'}}))\n```\n"
                if role == 'manifest' else
                ('## Claim\n\n### Formal Claim\n\n```python contract\ndeclare_contract()\n```\n'
                 if role == 'contract' else
                 '## Claim\n\n### Formal Claim\n\n```python\ncomponent_workflow()\n```\n'))
        (tmp_path / pin['path']).write_text(
            f"---\natom_family: SPEC\natom_id: AN-S-{index}\ncontainer: {{component: C7}}\n"
            f"tier: {dict(manifest=4, contract=0, solution=1)[role]}\n"
            f"context: {{template: {template}}}\nrelations:\n{relation or '  OTHER: []' + chr(10)}"
            f"state: {{status: active, version: 1}}\n---\n{body}")
        pins.append(pin)
    return pins


class BoundaryModelTests(unittest.TestCase):
    def setUp(self):
        self.directory = TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.pins = _inputs(self.root)

    def load(self):
        return load_boundary_model(self.root, 'C7', *self.pins)

    def test_contract_and_solution_require_their_tiers(self):
        for role, expected, invalid in (('contract', 0, 'false'), ('solution', 1, '2')):
            with self.subTest(role=role):
                path = self.root / (role + '.md')
                source = path.read_text()
                path.write_text(source.replace(f'tier: {expected}\n', f'tier: {invalid}\n'))
                with self.assertRaisesRegex(ValueError, f'{role} must have Tier {expected}'):
                    self.load()
                path.write_text(source)

    def test_manifest_loads_without_contract_or_solution(self):
        (self.root / 'contract.md').unlink()
        (self.root / 'solution.md').unlink()
        manifest = load_manifest(self.root, 'C7', self.pins[0])
        self.assertEqual('C7', manifest['fields']['component_id'])
        self.assertEqual(self.pins[0]['atom_id'], manifest['source']['atom_id'])

    def test_solution_pins_the_exact_contract_draft(self):
        contract = self.root / 'contract.md'
        contract.write_text(contract.read_text().replace('status: active', 'status: draft'))
        self.pins[1]['status'] = 'draft'
        with self.assertRaisesRegex(ValueError, 'AN-S-2@1-draft'):
            self.load()
        solution = self.root / 'solution.md'
        solution.write_text(solution.read_text().replace('AN-S-2@1', 'AN-S-2@1-draft'))
        self.assertEqual('draft', self.load()['contract']['source']['status'])

    def test_sources_and_claims(self):
        model = self.load()
        self.assertEqual(model['manifest']['boundaries'], {'io': {'server': 'API'}})
        self.assertEqual(model['solution']['claims'], [('python', 'component_workflow()\n')])
        self.assertEqual(model['issues'], [])
        old_hash = model['solution']['source']['sha256']
        path = self.root / 'solution.md'
        path.write_text(path.read_text().replace('component_workflow()', 'unknown()'))
        updated = self.load()
        self.assertNotEqual(old_hash, updated['solution']['source']['sha256'])
        self.assertTrue(any('unsupported' in issue for issue in updated['issues']))
        path.write_text(path.read_text().replace('AN-S-2@1', 'AN-S-20@1'))
        with self.assertRaisesRegex(ValueError, 'exact IS_SOLUTION_FOR'):
            self.load()

    def test_seed_and_wrong_version_are_rejected(self):
        path = self.root / 'manifest.md'
        text = path.read_text()
        path.write_text(text.replace('component_manifest', 'component_seed_manifest'))
        with self.assertRaisesRegex(ValueError, 'Seed'):
            self.load()
        path.write_text(text)
        for version in (0, 2, True):
            self.pins[0]['version'] = version
            with self.assertRaisesRegex(ValueError, 'source pin'):
                self.load()

    def test_solution_template_and_status(self):
        path = self.root / 'solution.md'
        text = path.read_text()
        path.write_text(text.replace('template: decision', 'template: SOLUTION'))
        self.load()
        path.write_text(text.replace('template: decision', 'template: requirement'))
        with self.assertRaisesRegex(ValueError, 'Solution or Decision'):
            self.load()
        path.write_text(text)
        self.pins[2]['status'] = 'archived'
        with self.assertRaisesRegex(ValueError, 'source pin'):
            self.load()

    def test_admitted_statuses_and_missing_claim(self):
        path = self.root / 'solution.md'
        original = path.read_text()
        for status in ('draft', 'ready'):
            path.write_text(original.replace('status: active', f'status: {status}'))
            self.pins[2]['status'] = status
            self.load()
        path.write_text(path.read_text().replace('### Formal Claim', '### Example'))
        self.assertIn('solution: missing formal claim', self.load()['issues'])
