import hashlib
import json
from pathlib import Path
import shutil
import tempfile
from unittest.mock import NonCallableMock
import unittest
from unittest.mock import patch

import yaml

from ..LAYER_2_PROJECT_STRUCTURE_C93__shared import _validation_fields, compile_structure
from ..LAYER_2_PROJECT_STRUCTURE_C93__rows import StructureAdmissionError, compile_structure_rows
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import CarrierError, LimitReached, ReadContext, canonical_native_header, native_header_view, read_structure
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carrier_read__pub import parse_carrier
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.project_manifest__pub import manifest_summary_fields
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import capture_native
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.model_capture import model_inputs
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.FEATURE_TOOLS__shared import resolve_native_project

ROOT = Path(__file__).resolve().parents[5]
CONTROL = ROOT / '_anechoic_anechoic'
if (ROOT.parent / 'native-control').is_dir():
    CONTROL = ROOT.parent / 'native-control'
PROJECT = ROOT / 'AN-S-3037-SPEC-PROJECT_MANIFEST--declare-anechoic.md'
COMPONENT = CONTROL / '01_TIER_1_ARCHITECTURE/AN-S-3039-SPEC-COMPONENT_MANIFEST--declare-engine-studio.md'

LEGACY_COMPONENT = '''---
atom_family: SPEC
atom_id: AN-S-3039
container:
  component: C00
tier: 4
context:
  template: component_manifest
  lens: SPEC
state:
  status: active
  version: 4
  updated_at: '2026-11-23T13:46:18.273025+00:00'
---

## Summary

Declare Engine Studio

## Purpose

Consume Environments. DevOps builds Engine Studio.

This Component delegates implementation to its child Components.

## Formal manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(
        component_id='C14',
        name='Engine Studio',
        layer=4,
        lens_whitelist=['DES', 'DevOps', 'QA', 'SPEC', 'SWD'],
        boundaries={'code': {'imports': [], 'exports': {}}},
    ),
)
```
'''


def selection(control, project=None):
    if project is None:
        project = PROJECT if control == CONTROL else control / PROJECT.name
    raw = project.read_bytes()
    meta = native_header_view(parse_carrier(raw, project).metadata)
    ref = f"{meta['identity']['atom_id']}@{meta['state']['version']}"
    return NonCallableMock(
        spec_set=[
            'control_root',
            'manifest_path',
            'manifest_ref',
            'manifest_sha256',
        ],
        control_root=control,
        manifest_path=project,
        manifest_ref=ref,
        manifest_sha256=hashlib.sha256(raw).hexdigest())


class Model:
    fingerprint = 'model-fingerprint'
    requires_atom_state = False

    def validate_manifest(self, fields, parent_id):
        assert fields['name'] and fields['prefix'] and parent_id == 'C00'

    def validate_component_manifest(self, fields, parent_id):
        assert fields['component_id'] and parent_id

    def validate_component_seed_manifest(self, fields, parent_id):
        assert fields['component_seed_id'] and parent_id


class StructureTests(unittest.TestCase):
    def test_project_summary_follows_model_declaration(self):
        model = Model()
        summaries = []

        def validate(fields, parent):
            summaries.append(fields.get('summary'))
            model.validate_manifest(fields, parent)
            manifest = NonCallableMock(
                spec_set=['name', 'prefix'], prefix=fields['prefix'],
            )
            manifest.name = fields['name']
            return manifest

        resolve_native_project(
            ROOT, CONTROL.name, validate_manifest=validate,
            require_manifest_summary=True,
        )
        resolve_native_project(ROOT, CONTROL.name, validate_manifest=validate)
        self.assertEqual(['Declare Anechoic', None], summaries)
        self.assertEqual({}, manifest_summary_fields(NonCallableMock(
            spec_set=['body'],
            body='## Claim\n\nText\n')))
        with self.assertRaisesRegex(ValueError, 'duplicate Summary'):
            manifest_summary_fields(NonCallableMock(
                spec_set=['body'],
                body='## Summary\n\nOne\n\n## Summary\n\nTwo\n'))

    def test_component_and_seed_summary_follows_model_declaration(self):
        carrier = NonCallableMock(
            spec_set=['body', 'metadata'],
            body='## Summary\n\nAuthored summary.\n',
            metadata={})
        model = NonCallableMock(
            spec_set=['requires_atom_state', 'declares_summary'],
            requires_atom_state=False,
            declares_summary=lambda name: name == 'Component Manifest')
        self.assertEqual({'summary': 'Authored summary.'}, _validation_fields({}, carrier, model, 'Component Manifest'))
        self.assertEqual({}, _validation_fields({}, carrier, model, 'Component Seed Manifest'))
        self.assertEqual({}, _validation_fields({}, carrier, Model(), 'Component Manifest'))
        model.declares_summary = lambda _: True
        seed = NonCallableMock(
            spec_set=['body', 'metadata'],
            body='# Manifest Build\n\n## Purpose\n\nBuild.\n',
            metadata={})
        self.assertEqual({'summary': 'Manifest Build'}, _validation_fields({}, seed, model, 'Component Seed Manifest'))
        for body in ('## Purpose\n\nBuild.\n', '# One\n\n# Two\n'):
            with self.assertRaisesRegex(ValueError, 'requires one title'):
                _validation_fields({}, NonCallableMock(
                    spec_set=['body', 'metadata'],
                    body=body,
                    metadata={}), model, 'Component Seed Manifest')

    def test_component_template_comes_from_header_when_model_declares_it(self):
        carrier = parse_carrier(LEGACY_COMPONENT.encode(), COMPONENT)
        model = NonCallableMock(
            spec_set=['requires_atom_state', 'declares_property'],
            requires_atom_state=False,
            declares_property=lambda name, prop: name == 'Component Manifest' and prop == 'template')
        self.assertEqual({'template': 'component_manifest'},
                         _validation_fields({}, carrier, model, 'Component Manifest'))
        changed = NonCallableMock(
            spec_set=['body', 'metadata'],
            body=carrier.body,
            metadata={**carrier.metadata,
            'context': {**carrier.metadata['context'], 'template': 'other'}})
        self.assertEqual({'template': 'other'}, _validation_fields({}, changed, model, 'Component Manifest'))
        self.assertEqual({}, _validation_fields({}, changed, Model(), 'Component Manifest'))
        self.assertEqual({}, _validation_fields({}, changed, model, 'Component Seed Manifest'))

    def _standalone_project(self):
        root = Path(self.enterContext(tempfile.TemporaryDirectory())).resolve()
        control, project = root / "control", root / PROJECT.name
        (control / "_SPEC").mkdir(parents=True)
        shutil.copyfile(PROJECT, project)
        return control, selection(control, project)

    def test_offline_compile_validates_project_manifest_with_supplied_model(self):
        _, selected = self._standalone_project()
        model = Model()
        with patch.object(model, 'validate_manifest', side_effect=ValueError('Project refused')):
            with self.assertRaisesRegex(ValueError, 'Project refused'):
                compile_structure(selected, model)

    def test_component_scanner_uses_model_template(self):
        control, selected = self._standalone_project()
        component = control / '_SPEC' / COMPONENT.name
        component.write_text(LEGACY_COMPONENT.replace('template: component_manifest', 'template: new_component'))

        class ConfiguredModel(Model):
            def fixed_property_value(self, name, property_name):
                assert (name, property_name) == ('Component Manifest', 'template')
                return 'new_component'

            def declares_property(self, name, property_name):
                return (name, property_name) == ('Component Manifest', 'template')

            def validate_component_manifest(self, fields, parent_id):
                super().validate_component_manifest(fields, parent_id)
                assert fields['template'] == 'new_component'

        self.assertIn('C14', compile_structure(selected, ConfiguredModel())['components'])
        component.write_text(LEGACY_COMPONENT)
        self.assertNotIn('C14', compile_structure(selected, ConfiguredModel())['components'])
        self.assertIn('C14', compile_structure(selected, Model())['components'])

    def test_seed_optional_sections_survive_structure_compilation(self):
        control, selected = self._standalone_project()
        path = control / '_SPEC' / 'AN-S-4000-SPEC-COMPONENT_SEED_MANIFEST--test.md'
        path.write_text('''---
atom_family: SPEC
atom_id: AN-S-4000
container: {component: C00}
tier: 2
context: {template: component_seed_manifest, lens: SPEC}
state: {status: active, version: 1, updated_at: '2026-11-20T00:00:00Z'}
---
# Seed

## Formal Manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentSeedManifest
declare_entity(entity_name="Component Seed Manifest", instance=ComponentSeedManifest(component_seed_id="CS4000", boundaries={"process": {"launch": "worker"}}))
```

## Contract

Contract text.
''')
        snapshot = compile_structure(selected, Model())
        snapshot_path = control.parent / 'structure.json'
        snapshot_path.write_text(json.dumps(snapshot))
        fields = read_structure(snapshot_path).packages['CS4000'].fields
        self.assertEqual(fields['contract'], 'Contract text.')
        self.assertNotIn('purpose', fields)
        self.assertNotIn('solution', fields)
        self.assertEqual(dict(fields['boundaries']['process']), {'launch': 'worker'})

    def test_ordinary_specs_may_be_malformed_unreadable_or_oversized(self):
        control, selected = self._standalone_project()
        spec = control / "_SPEC"
        child = spec / COMPONENT.name
        child.write_text(LEGACY_COMPONENT)
        (control / "AN-S-4000-SPEC-REQUIREMENT--bad.md").write_text("---\ninvalid: [\n---\n")
        (spec / "AN-S-4001-SPEC-REQUIREMENT--unreadable.md").symlink_to(spec / "missing.md")
        oversized = spec / "AN-S-4002-SPEC-REQUIREMENT--oversized.md"
        oversized.touch()
        read = ReadContext.read

        def limited(reader, path, **options):
            if path == oversized:
                raise LimitReached("max_file_bytes")
            return read(reader, path, **options)

        with patch.object(ReadContext, "read", limited):
            result = compile_structure(selected, Model())
        self.assertEqual(f"_SPEC/{COMPONENT.name}", result["components"]["C14"]["source_path"])

    def test_conventional_structure_manifests_still_require_readable_valid_headers(self):
        control, selected = self._standalone_project()
        for filename in (COMPONENT.name, "AN-S-4000-SPEC-COMPONENT_SEED_MANIFEST--required.md"):
            with self.subTest(filename=filename):
                path = control / "_SPEC" / filename
                path.write_text("---\ninvalid: [\n---\n")
                with self.assertRaises(CarrierError):
                    compile_structure(selected, Model())
                path.unlink()

    def test_live_sources(self):
        result = compile_structure(selection(CONTROL), Model())
        self.assertTrue({'C14', 'C59', 'C62'} <= result['components'].keys())
        runtime = result['components']['C62']
        self.assertEqual(runtime['parent'], 'C59')
        runtime_header = native_header_view(parse_carrier((CONTROL / runtime['source_path']).read_bytes(), CONTROL / runtime['source_path']).metadata)
        self.assertEqual(runtime['ref'], f"AN-S-3088@{runtime_header['state']['version']}")
        self.assertEqual(runtime['source_path'], 'LAYER_4_ENGINE_STUDIO_C14/KERNEL_MIXER_C59/01_TIER_1_ARCHITECTURE/AN-S-3088-SPEC-COMPONENT_MANIFEST--declare-manifest-runtime.md')
        self.assertEqual(runtime['sha256'], hashlib.sha256((CONTROL / runtime['source_path']).read_bytes()).hexdigest())
        self.assertEqual(result['project']['ref'], selection(CONTROL).manifest_ref)
        self.assertEqual(result['project']['sha256'], selection(CONTROL).manifest_sha256)
        self.assertEqual(result['components']['C14']['parent'], 'C00')
        self.assertEqual(result['components']['C14']['source_path'], f'01_TIER_1_ARCHITECTURE/{COMPONENT.name}')
        self.assertEqual(json.loads(json.dumps(result)), result)
        self.assertEqual(result['packages']['CS1']['component'], 'C50')
        seed = CONTROL / result['packages']['CS1']['source_path']
        seed_header = native_header_view(parse_carrier(seed.read_bytes(), seed).metadata)
        self.assertEqual(result['packages']['CS1']['ref'], f"AN-S-3089@{seed_header['state']['version']}")

    def test_ingested_rows_match_offline_and_enforce_pin(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            control = root / 'control'
            control.mkdir()
            project = root / PROJECT.name
            shutil.copyfile(PROJECT, project)
            child = control / COMPONENT.name
            child.write_text(LEGACY_COMPONENT)
            rows = []
            for path in (project, child):
                raw = path.read_bytes()
                carrier = parse_carrier(raw, path)
                header = native_header_view(carrier.metadata)
                rows.append({'source_path': path.relative_to(root).as_posix(),
                             'exact_ref': f"{header['identity']['atom_id']}@{header['state']['version']}",
                             'metadata': carrier.metadata, 'body': carrier.body,
                             'sha256': hashlib.sha256(raw).hexdigest()})
            selected = selection(control, project)
            expected = compile_structure(selected, Model())
            project.unlink()
            child.unlink()
            self.assertEqual(expected, compile_structure_rows(root, 'control', selected.manifest_sha256, Model(), rows, manifest_path=project.name))
            for pin in ('', '0' * 64):
                with self.assertRaises(ValueError):
                    compile_structure_rows(root, 'control', pin, Model(), rows)
            with self.assertRaises(ValueError):
                compile_structure_rows(root, 'control', selected.manifest_sha256, Model(), rows[1:])
            with self.assertRaises(ValueError):
                compile_structure_rows(root, 'control', selected.manifest_sha256, Model(), rows, manifest_path='foreign.md')
            rows[0]['exact_ref'] = 'AN-S-0@1'
            with self.assertRaises(ValueError):
                compile_structure_rows(root, 'control', selected.manifest_sha256, Model(), rows)

    def test_pin_duplicates_parent_and_changes(self):
        with tempfile.TemporaryDirectory() as tmp:
            control = Path(tmp).resolve()
            project = control / PROJECT.name
            child = control / COMPONENT.name
            shutil.copyfile(PROJECT, project)
            child.write_text(LEGACY_COMPONENT)
            (control / '__EXAMPLE_C14').mkdir()
            selected = selection(control)
            result = compile_structure(selected, Model())
            self.assertEqual(result['project']['sha256'], selected.manifest_sha256)
            selected.manifest_ref = 'AN-S-3037@99'
            with self.assertRaisesRegex(ValueError, 'pin changed'):
                compile_structure(selected, Model())
            selected.manifest_ref = selection(control).manifest_ref
            duplicate = control / 'AN-S-4000-SPEC-PROJECT_MANIFEST--duplicate.md'
            duplicate.write_text(project.read_text().replace('AN-S-3037', 'AN-S-4000'))
            with self.assertRaisesRegex(ValueError, 'exactly one'):
                compile_structure(selected, Model())
            duplicate.unlink()
            child.write_text(child.read_text().replace('component: C00', 'component: C14'))
            with self.assertRaisesRegex(ValueError, 'identity or parent'):
                compile_structure(selected, Model())
            child.write_text(LEGACY_COMPONENT)
            (control / 'FIRST_C14').mkdir()
            (control / 'SECOND_C14').mkdir()
            with self.assertRaisesRegex(ValueError, 'Duplicate Component directory'):
                compile_structure(selected, Model())
            (control / 'FIRST_C14').rmdir()
            (control / 'SECOND_C14').rmdir()
            class MutatingModel(Model):
                def validate_component_manifest(self, fields, parent_id):
                    child.write_text(child.read_text() + '\n')
            with self.assertRaisesRegex(ValueError, 'changed'):
                compile_structure(selected, MutatingModel())

    def test_component_manifest_in_spec_and_duplicate_across_layouts(self):
        with tempfile.TemporaryDirectory() as tmp:
            control = Path(tmp).resolve()
            shutil.copyfile(PROJECT, control / PROJECT.name)
            spec = control / '_SPEC'
            spec.mkdir()
            content = LEGACY_COMPONENT
            (spec / COMPONENT.name).write_text(content)
            result = compile_structure(selection(control), Model())
            self.assertEqual(result['components']['C14']['source_path'], f'_SPEC/{COMPONENT.name}')
            (control / COMPONENT.name).write_text(content)
            with self.assertRaisesRegex(ValueError, 'Duplicate'):
                compile_structure(selection(control), Model())

    def test_optional_carrier_directory_appearing_during_compilation(self):
        for name in ('_SPEC', '01_CUSTOM_ARCHITECTURE'):
            for symlink in (False, True):
                with self.subTest(name=name, symlink=symlink), tempfile.TemporaryDirectory() as tmp:
                    control = Path(tmp).resolve() / 'control'
                    control.mkdir()
                    project = control.parent / PROJECT.name
                    project.write_text(PROJECT.read_text().replace('01_TIER_1_ARCHITECTURE', '01_CUSTOM_ARCHITECTURE', 1))
                    selected = selection(control, project)
                    currentness = ReadContext.currentness

                    def mutate(reader):
                        result = currentness(reader)
                        directory = control / name
                        if symlink:
                            directory.symlink_to(control / 'missing')
                        else:
                            directory.mkdir()
                            (directory / COMPONENT.name).write_text(LEGACY_COMPONENT)
                        return result

                    with patch.object(ReadContext, 'currentness', mutate):
                        with self.assertRaisesRegex(ValueError, 'Structure sources changed'):
                            compile_structure(selected, Model())

    def test_canonical_component_classified_by_header(self):
        with tempfile.TemporaryDirectory() as tmp:
            control = Path(tmp).resolve()
            shutil.copyfile(PROJECT, control / PROJECT.name)
            raw = COMPONENT.read_text()
            _, frontmatter, body = raw.split('---', 2)
            header = canonical_native_header(yaml.safe_load(frontmatter))
            header['tier'] = 1
            path = control / 'AN-S-3039-SPEC-OTHER--engine.md'
            path.write_text(f'---\n{yaml.safe_dump(header)}---{body}')
            result = compile_structure(selection(control), Model())
            self.assertEqual(path.name, result['components']['C14']['source_path'])

    def test_failed_alias_and_off_path_issue_match_offline_admission(self):
        control, selected = self._standalone_project()
        native = NonCallableMock(
            spec_set=[
                'root',
                'control_root',
                'manifest_path',
                'manifest_sha256',
                'project_prefix',
            ],
            root=control.parent,
            control_root=control,
            manifest_path=selected.manifest_path,
            manifest_sha256=selected.manifest_sha256,
            project_prefix='AN')
        alias = control / '_SPEC/AN-S-3039-SPEC-OTHER--engine.md'
        alias.write_text(LEGACY_COMPONENT)
        off_path = control / '_QA/AN-S-3333-SPEC-COMPONENT_MANIFEST--invalid.md'
        off_path.parent.mkdir()
        off_path.write_text('---\ninvalid: [\n---\n')
        self.assertIn('C14', compile_structure(selected, Model())['components'])
        capture = capture_native(native)
        self.assertEqual((), model_inputs(native, capture, include_spec_rows=True)['structure_issues'])
        alias.write_text(LEGACY_COMPONENT.replace('version: 4', 'version: 0'))
        with self.assertRaisesRegex(ValueError, 'Native State'):
            compile_structure(selected, Model())
        capture = capture_native(native)
        inputs = model_inputs(native, capture, include_spec_rows=True)
        issues = inputs['structure_alias_issues']
        self.assertEqual([alias.relative_to(native.root).as_posix()], [issue['relative_path'] for issue in issues])
        with self.assertRaises(StructureAdmissionError):
            compile_structure_rows(native.root, 'control', native.manifest_sha256, Model(), inputs['spec_rows'],
                                   manifest_path=selected.manifest_path.name, alias_issues=issues)

    def test_failed_custom_alias_is_classified_by_admitted_model(self):
        control, selected = self._standalone_project()
        native = NonCallableMock(
            spec_set=[
                'root',
                'control_root',
                'manifest_path',
                'manifest_sha256',
                'project_prefix',
            ],
            root=control.parent,
            control_root=control,
            manifest_path=selected.manifest_path,
            manifest_sha256=selected.manifest_sha256,
            project_prefix='AN')
        alias = control / '_SPEC/AN-S-3039-SPEC-OTHER--engine.md'
        alias.write_text(LEGACY_COMPONENT.replace('template: component_manifest', 'template: new_component')
                         .replace('version: 4', 'version: 0'))
        class ConfiguredModel(Model):
            def fixed_property_value(self, name, property_name):
                return 'new_component'
        self.assertEqual({}, compile_structure(selected, Model())['components'])
        with self.assertRaisesRegex(ValueError, 'Native State'):
            compile_structure(selected, ConfiguredModel())
        inputs = model_inputs(native, capture_native(native), include_spec_rows=True)
        args = (native.root, 'control', native.manifest_sha256)
        kwargs = {'manifest_path': selected.manifest_path.name, 'alias_issues': inputs['structure_alias_issues']}
        self.assertEqual({}, compile_structure_rows(*args, Model(), inputs['spec_rows'], **kwargs)['components'])
        with self.assertRaises(StructureAdmissionError):
            compile_structure_rows(*args, ConfiguredModel(), inputs['spec_rows'], **kwargs)

    def test_component_carrier_symlink_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            control = Path(tmp).resolve()
            shutil.copyfile(PROJECT, control / PROJECT.name)
            (control / COMPONENT.name).symlink_to(COMPONENT)
            with self.assertRaises(OSError):
                compile_structure(selection(control), Model())

    def test_legacy_component_manifest_requires_tier_four(self):
        control, selected = self._standalone_project()
        path = control / '_SPEC' / COMPONENT.name
        raw = LEGACY_COMPONENT
        _, frontmatter, body = raw.split('---', 2)
        header = yaml.safe_load(frontmatter)
        header['tier'] = 4
        path.write_text(f'---\n{yaml.safe_dump(header)}---{body}')
        fields = compile_structure(selected, Model())['components']['C14']['fields']
        self.assertEqual(fields['tier'], 4)
        header['tier'] = 1
        path.write_text(f'---\n{yaml.safe_dump(header)}---{body}')
        with self.assertRaisesRegex(ValueError, 'Tier 1 Component Manifest'):
            compile_structure(selected, Model())
        header['tier'] = 0
        path.write_text(f'---\n{yaml.safe_dump(header)}---{body}')
        with self.assertRaisesRegex(ValueError, 'identity or parent'):
            compile_structure(selected, Model())

    def test_canonical_tier_one_component_is_discovered_in_project_layout(self):
        control, selected = self._standalone_project()
        project = selected.manifest_path
        project.write_text(project.read_text().replace('01_TIER_1_ARCHITECTURE', '01_CUSTOM_ARCHITECTURE', 1))
        directory = control / '01_CUSTOM_ARCHITECTURE'
        directory.mkdir()
        path = directory / COMPONENT.name
        _, frontmatter, _ = COMPONENT.read_text().split('---', 2)
        header = yaml.safe_load(frontmatter)
        header['tier'] = 1
        path.write_text(f'---\n{yaml.safe_dump(header)}---\n' + '''## Summary

Declare Engine Studio

## Purpose

Provide the engine.

## Component Identity

```python
from anechoic.model import ComponentManifest
ComponentManifest(component_id='C14', name='Engine Studio', lens_whitelist=['SPEC'])
```

## Component Boundaries

```python
{'code': {'imports': ['C30']}}
```

## Component Contract

```python contract
declare_contract()
```
''')
        result = compile_structure(selection(control, project), Model())
        self.assertEqual(result['components']['C14']['fields']['tier'], 1)
        self.assertEqual(result['components']['C14']['source_path'], f'01_CUSTOM_ARCHITECTURE/{COMPONENT.name}')

    def test_component_lens_groups(self):
        with tempfile.TemporaryDirectory() as tmp:
            control = Path(tmp).resolve()
            project = control / PROJECT.name
            child = control / COMPONENT.name
            second = control / 'AN-S-4000-SPEC-COMPONENT_MANIFEST--second.md'
            groups = {'SWE': ['SWD', 'QA', 'DevOps'], 'SYS': ['SWE', 'DOM'],
                      'BACKEND': ['API', 'SWE'], 'OTHER': ['SWD2', 'API']}
            project.write_text(PROJECT.read_text().replace(
                "'project': {", f"'project': {{\n                'lens_groups': {groups!r},", 1))
            original = LEGACY_COMPONENT
            old_lenses = "lens_whitelist=['DES', 'DevOps', 'QA', 'SPEC', 'SWD']"

            def write_component(path, lenses, content=original):
                path.write_text(content.replace(old_lenses, f'lens_whitelist={lenses!r}'))

            write_component(child, ['SWE', 'SWD', 'SWD/DBT'])
            compile_structure(selection(control), Model())
            write_component(child, ['SYS', 'BACKEND'])
            with self.assertRaises(ValueError) as raised:
                compile_structure(selection(control), Model())
            for value in (child.name, 'SYS', 'BACKEND'):
                self.assertIn(value, str(raised.exception))

            write_component(child, ['SYS'])
            write_component(second, ['BACKEND'], original.replace('AN-S-3039', 'AN-S-4000').replace('C14', 'C15'))
            compile_structure(selection(control), Model())
            second.unlink()
            write_component(child, ['SWE', 'OTHER'])
            compile_structure(selection(control), Model())

            project.write_text(project.read_text().replace(
                repr(groups), repr({'SYS': ['BACKEND'], 'BACKEND': ['SYS']})))
            with self.assertRaisesRegex(ValueError, '(?i)cycle'):
                compile_structure(selection(control), Model())

    def test_formal_fields(self):
        claim = '''## Claim\n\n### Formal Claim\n\n```python\nfrom anechoic.formal_claims import declare_entity\nfrom anechoic.model import ComponentManifest\ndeclare_entity(entity_name="Component Manifest", instance=ComponentManifest(component_id="C1", name="One", lens_whitelist=["SPEC"]))\n```\n'''
        control, selected = self._standalone_project()
        _, frontmatter, _ = COMPONENT.read_text().split('---', 2)
        header = yaml.safe_load(frontmatter)
        header['tier'] = 4
        path = control / '_SPEC' / COMPONENT.name
        path.write_text(f'---\n{yaml.safe_dump(header)}---\n{claim}')
        fields = compile_structure(selected, Model())['components']['C1']['fields']
        self.assertEqual({key: fields[key] for key in ('component_id', 'name', 'lens_whitelist')},
                         {'component_id': 'C1', 'name': 'One', 'lens_whitelist': ['SPEC']})


if __name__ == '__main__':
    unittest.main()
