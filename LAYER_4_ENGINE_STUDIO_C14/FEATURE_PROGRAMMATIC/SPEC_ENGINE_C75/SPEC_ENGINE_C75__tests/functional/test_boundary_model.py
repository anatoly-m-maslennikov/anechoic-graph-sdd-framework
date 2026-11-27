import hashlib
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carrier_read__pub import (
    parse_carrier,
)
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_1_SOURCE_ADAPTERS_C95._package__shared import (
    SourceError,
    SpecSnapshot,
    read_source,
)
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_2_SPEC_READING_C83._package__shared import (
    load_boundary_model,
    load_manifest,
)


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
            f"tier: { {'manifest': 4, 'contract': 0, 'solution': 1}[role]}\n"
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

    def test_formal_path_is_pinned_and_does_not_read_files(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            pins = _inputs(root)
            rows = []
            for pin in pins:
                path = root / pin['path']
                raw = path.read_bytes()
                carrier = parse_carrier(raw, path)
                rows.append({'source_path': pin['path'], 'exact_ref': pin['atom_id'] + '@1',
                             'metadata': carrier.metadata, 'body': carrier.body,
                             'sha256': hashlib.sha256(raw).hexdigest()})
            snapshot = SpecSnapshot(rows)
            rows[0]['metadata']['atom_id'] = 'changed'
            snapshot.rows[0]['metadata']['atom_id'] = 'changed again'
            with patch.object(Path, 'read_bytes', side_effect=AssertionError('file read')):
                result = load_boundary_model(snapshot, 'C7', *pins)
            self.assertEqual(result['manifest']['source']['sha256'], rows[0]['sha256'])
            self.assertEqual(result['issues'], [])
            pins[0]['version'] = 2
            with self.assertRaises(SourceError) as error:
                load_boundary_model(snapshot, 'C7', *pins)
            self.assertEqual(error.exception.field, 'exact_ref')

    def load(self):
        return load_boundary_model(self.root, 'C7', *self.pins)

    def test_rejects_noncanonical_pins_before_source_lookup(self):
        manifest, contract, solution = self.pins
        nested = self.root / 'sub' / 'manifest.md'
        nested.parent.mkdir()
        nested.write_bytes((self.root / manifest['path']).read_bytes())
        for path in (str(self.root / manifest['path']), './manifest.md',
                     'child/../manifest.md', 'sub//manifest.md',
                     'sub/\x00manifest.md'):
            pin = {**manifest, 'path': path}
            for source in (self.root, SpecSnapshot([])):
                with self.subTest(path=path, source=type(source).__name__):
                    with self.assertRaisesRegex(SourceError, 'invalid source path') as error:
                        load_boundary_model(source, 'C7', pin, contract, solution)
                    self.assertEqual('path', error.exception.field)
                    self.assertEqual(pin, error.exception.source)

    def test_rejects_symlink_aliases_for_exact_source_path(self):
        manifest = self.pins[0]
        target = self.root / manifest['path']
        (self.root / 'alias.md').symlink_to(target)
        (self.root / 'real').mkdir()
        (self.root / 'real' / 'manifest.md').write_bytes(target.read_bytes())
        (self.root / 'alias').symlink_to('real', target_is_directory=True)
        c, source = read_source(self.root, manifest, 'manifest')
        digest = hashlib.sha256(target.read_bytes()).hexdigest()
        self.assertEqual(source['sha256'], digest)
        row = {'source_path': manifest['path'], 'exact_ref': 'AN-S-1@1',
               'metadata': c.metadata, 'body': c.body, 'sha256': digest}
        for path in ('alias.md', 'alias/manifest.md'):
            pin = {**manifest, 'path': path}
            for root in (self.root, SpecSnapshot([row])):
                with self.subTest(path=path, source=type(root).__name__):
                    with self.assertRaises(SourceError) as error:
                        read_source(root, pin, 'manifest')
                    self.assertEqual(error.exception.field, 'path')

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


class EmbeddedContractTests(unittest.TestCase):
    def setUp(self):
        directory = TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.manifest, self.contract, self.solution = _inputs(self.root)
        self.manifest.update(status='draft', container_component='C10')
        self.manifest_path = self.root / self.manifest['path']
        self.solution_path = self.root / self.solution['path']
        self.legacy_manifest_source = (
            self.manifest_path.read_text().replace('tier: 4', 'tier: 1')
            .replace('status: active', 'status: draft').replace('component: C7', 'component: C10')
        )
        self.manifest_path.write_text(
            self.legacy_manifest_source.partition('## Formal Manifest')[0] + """
## Summary

Declare the Test Component.

## Purpose

Test the boundary model.

## Component Identity

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest
declare_entity(entity_name='Component Manifest', instance=ComponentManifest(component_id='C7', name='Test'))
```

## Component Boundaries

```python
{'io': {'server': 'API'}}
```

## Component Contract

```python contract
declare_contract()
```
""")
        self.solution_path.write_text(
            self.solution_path.read_text().replace('tier: 1', 'tier: 0')
            .replace('template: decision', 'template: solution')
            .replace('IS_SOLUTION_FOR: [AN-S-2@1]', 'ANSWERS: [AN-S-1@1-draft]'))

    def load(self):
        return load_boundary_model(self.root, 'C7', self.manifest, solution=self.solution)

    def test_model_uses_one_manifest_pin_for_both_declarations(self):
        (self.root / self.contract['path']).unlink()
        model = self.load()
        self.assertTrue(model['embedded_contract'])
        self.assertEqual([], model['issues'])
        self.assertEqual(model['manifest']['source'], model['contract']['source'])
        self.assertEqual('C10', model['contract']['source']['container_component'])
        self.assertEqual([('python contract', 'declare_contract()\n')], model['contract']['claims'])
        self.assertEqual(model, load_boundary_model(self.root, 'C7', self.manifest, self.solution))
        with self.assertRaisesRegex(ValueError, 'Contract source is the pinned Manifest'):
            load_boundary_model(self.root, 'C7', self.manifest, self.contract, self.solution)
        self.solution_path.unlink()
        self.assertEqual(model['contract'], load_manifest(self.root, 'C7', self.manifest)['contract'])

    def test_solution_must_answer_the_exact_manifest_revision(self):
        source = self.solution_path.read_text()
        for relation in ('ANSWERS: [AN-S-1]', 'ANSWERS: [AN-S-1@1]', 'ANSWERS: [AN-S-1@2-draft]',
                         'IS_SOLUTION_FOR: [AN-S-1@1-draft]'):
            with self.subTest(relation=relation):
                self.solution_path.write_text(source.replace('ANSWERS: [AN-S-1@1-draft]', relation))
                with self.assertRaisesRegex(ValueError, 'missing exact ANSWERS link to AN-S-1@1-draft'):
                    self.load()

    def test_solution_must_have_tier_zero_and_belong_to_the_component(self):
        source = self.solution_path.read_text()
        self.solution_path.write_text(source.replace('tier: 0', 'tier: 1'))
        with self.assertRaisesRegex(ValueError, 'solution must have Tier 0'):
            self.load()
        self.solution_path.write_text(source.replace('component: C7', 'component: C10'))
        self.solution['container_component'] = 'C10'
        with self.assertRaisesRegex(ValueError, 'solution component does not match'):
            self.load()

    def test_only_tier_one_admits_the_embedded_contract(self):
        source = self.manifest_path.read_text()
        self.manifest_path.write_text(source.replace('tier: 1', 'tier: 4'))
        with self.assertRaises(ValueError):
            load_manifest(self.root, 'C7', self.manifest)

    def test_identity_only_manifest_loads_and_verification_reports_missing_contract(self):
        source = self.manifest_path.read_text()
        header = source.partition('## Summary')[0]
        identity = source[source.index('## Component Identity'):source.index('## Component Boundaries')]
        self.manifest_path.write_text(header + identity)
        manifest = load_manifest(self.root, 'C7', self.manifest)
        self.assertEqual(manifest['fields']['component_id'], 'C7')
        self.assertNotIn('contract', manifest)
        self.assertIsNone(manifest['boundaries'])
        with self.assertRaisesRegex(ValueError, 'missing Contract claim'):
            self.load()

    def test_verification_reports_missing_solution_source(self):
        with self.assertRaisesRegex(ValueError, 'missing Solution source'):
            load_boundary_model(self.root, 'C7', self.manifest)
